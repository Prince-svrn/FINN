"""Validate the model adapter contract with a local mock, not paid inference."""
import asyncio
import json
import httpx
import pytest
from pydantic import BaseModel
from backend import store, llm_router

class Answer(BaseModel):
    claim: str

@pytest.fixture
def provider(tmp_path, monkeypatch):
    monkeypatch.setattr(store, 'DB_PATH', tmp_path/'router.db')
    monkeypatch.setenv('FINN_LLM_API_KEY', 'local-test-key')
    monkeypatch.setenv('FINN_MODEL_T2', 'local-test-model')
    monkeypatch.setenv('FINN_LLM_BASE_URL', 'https://example.com/v1')
    monkeypatch.delenv('FINN_T2_INPUT_USD_PER_MILLION', raising=False)
    monkeypatch.delenv('FINN_T2_OUTPUT_USD_PER_MILLION', raising=False)
    replies=[]
    calls=[]
    def respond(request):
        calls.append(json.loads(request.content))
        return httpx.Response(200,json={'choices':[{'message':{'content':replies.pop(0)}}],
                                      'usage':{'prompt_tokens':20,'completion_tokens':10}})
    client=httpx.AsyncClient
    monkeypatch.setattr(llm_router.httpx, 'AsyncClient',
                        lambda **kwargs:client(transport=httpx.MockTransport(respond),**kwargs))
    return replies,calls

def test_valid_output_cache_and_changed_evidence(provider):
    replies,calls=provider
    replies.extend(['{"claim":"Source A"}', '{"claim":"Source B"}'])
    async def check():
        a=[{'role':'user','content':'Source A'}]
        assert (await llm_router.run('test',a,Answer,2))['data']['claim']=='Source A'
        assert (await llm_router.run('test',a,Answer,2))['cache_hit']
        assert (await llm_router.run('test',[{'role':'user','content':'Source B'}],Answer,2))['data']['claim']=='Source B'
    asyncio.run(check())
    assert len(calls)==2
    assert store.telemetry()['unpriced_calls']==2

def test_invalid_model_response_is_not_cached(provider):
    replies,calls=provider
    replies.extend(['{"wrong_field":"unsupported"}', '{"claim":"Validated"}'])
    async def check():
        assert (await llm_router.run('test',[],Answer,2))['status']=='error'
        assert (await llm_router.run('test',[],Answer,2))['status']=='ok'
    asyncio.run(check())
    assert len(calls)==2

def test_actual_usage_drives_cost(provider,monkeypatch):
    replies,_=provider
    replies.append('{"claim":"Validated"}')
    monkeypatch.setenv('FINN_T2_INPUT_USD_PER_MILLION','1')
    monkeypatch.setenv('FINN_T2_OUTPUT_USD_PER_MILLION','2')
    asyncio.run(llm_router.run('test',[],Answer,2))
    assert store.telemetry()['cost']==pytest.approx(0.00004)

def test_provider_change_invalidates_cache(provider,monkeypatch):
    replies,calls=provider
    replies.extend(['{"claim":"First provider"}','{"claim":"Second provider"}'])
    asyncio.run(llm_router.run('test',[],Answer,2))
    monkeypatch.setenv('FINN_LLM_BASE_URL','https://other.example/v1')
    result=asyncio.run(llm_router.run('test',[],Answer,2))
    assert result['data']['claim']=='Second provider'
    assert len(calls)==2

def test_gemini_contract_and_uncached_connection_check(provider,monkeypatch):
    replies,calls=provider
    replies.extend(['{"claim":"OK"}']*2)
    monkeypatch.setenv('FINN_LLM_BASE_URL','https://generativelanguage.googleapis.com/v1beta/openai/')
    monkeypatch.setenv('FINN_MODEL_T2','gemini-3.8-flash')
    for _ in range(2):
        assert asyncio.run(llm_router.run('connection_check',[],Answer,2,use_cache=False))['status']=='ok'
    assert len(calls)==2
    assert calls[0]['response_format']=={'type':'json_object'}
    assert json.dumps(Answer.model_json_schema()) in calls[0]['messages'][0]['content']
    assert calls[0]['reasoning_effort']=='low'
    assert 'temperature' not in calls[0]
    assert store.telemetry()['cache_hits']==0

def test_gemini_research_json_mode_keeps_local_validation(provider,monkeypatch):
    from backend.schemas import Synthesis
    replies,calls=provider
    monkeypatch.setenv('FINN_LLM_BASE_URL','https://generativelanguage.googleapis.com/v1beta/openai')
    valid={'business':[{'claim':'Example company builds motors.',
                       'citation':{'document_id':'doc1','page':1,'quote':'Example company builds motors.'}}]}
    replies.extend([json.dumps({'business':'not a list'}),json.dumps(valid)])
    messages=[{'role':'user','content':'Primary evidence: Example company builds motors.'}]
    first=asyncio.run(llm_router.run('primary_research',messages,Synthesis,2))
    second=asyncio.run(llm_router.run('primary_research',messages,Synthesis,2))
    assert first['error_code']=='invalid_response'
    assert second['status']=='ok'
    assert second['data']['business'][0]['citation']['page']==1
    assert len(calls)==2 and calls[0]['response_format']=={'type':'json_object'}
    assert 'json_schema' not in calls[0]['response_format']
    assert json.dumps(Synthesis.model_json_schema()) in calls[0]['messages'][0]['content']
    assert messages==[{'role':'user','content':'Primary evidence: Example company builds motors.'}]

def test_google_list_error_preserves_quota_classification():
    response=httpx.Response(429,json=[{'error':{'code':429,'type':'insufficient_quota','message':'Do not expose this'}}])
    code,reason=llm_router.provider_error(response)
    assert code=='quota_exhausted' and 'Do not expose this' not in reason

@pytest.mark.parametrize('page,exit_code',[(1,0),(2,1)])
def test_full_research_setup_check_validates_citation(provider,monkeypatch,capsys,page,exit_code):
    from scripts.setup_free_ai import check_connection
    replies,_=provider
    monkeypatch.setenv('FINN_LLM_BASE_URL','https://generativelanguage.googleapis.com/v1beta/openai')
    replies.append(json.dumps({'business':[{'claim':'Example company manufactures electric motors.',
        'citation':{'document_id':'setup-fixture','page':page,'quote':'Example company manufactures electric motors.'}}]}))
    assert asyncio.run(check_connection(research=True))==exit_code
    output=capsys.readouterr().out
    assert ('PASS: Research-format' in output)==(exit_code==0)

@pytest.mark.parametrize('status,code,expected',[
    (429,'credit_balance_exhausted','quota_exhausted'),
    (429,'insufficient_quota','quota_exhausted'),
    (429,'RESOURCE_EXHAUSTED','rate_limited'),
    (401,'invalid_api_key','access_denied'),
    (403,'PERMISSION_DENIED','access_denied'),
    (404,'NOT_FOUND','model_unavailable'),
    (400,'INVALID_ARGUMENT','invalid_request'),
    (503,'UNAVAILABLE','provider_unavailable'),
])
def test_errors_are_actionable_secret_free_and_not_retried(tmp_path,monkeypatch,status,code,expected):
    monkeypatch.setattr(store,'DB_PATH',tmp_path/'errors.db')
    monkeypatch.setenv('FINN_LLM_API_KEY','private-test-secret')
    monkeypatch.setenv('FINN_MODEL_T2','test')
    calls=[]
    def respond(request):
        calls.append(request)
        return httpx.Response(status,json={'error':{'code':code,'message':'private-test-secret'}})
    client=httpx.AsyncClient
    monkeypatch.setattr(llm_router.httpx,'AsyncClient',lambda **kw:client(transport=httpx.MockTransport(respond),**kw))
    result=asyncio.run(llm_router.run('test',[],Answer,2))
    assert result['status']=='error' and result['error_code']==expected
    assert len(result['reason'])>40
    assert 'private-test-secret' not in json.dumps(result)+json.dumps(store.telemetry())
    assert len(calls)==1
    with store.connect() as db:assert db.execute('SELECT COUNT(*) FROM cache').fetchone()[0]==0

def test_truncated_json_is_rejected_even_when_parseable(tmp_path,monkeypatch):
    monkeypatch.setattr(store,'DB_PATH',tmp_path/'truncated.db')
    monkeypatch.setenv('FINN_LLM_API_KEY','test')
    monkeypatch.setenv('FINN_MODEL_T2','test')
    client=httpx.AsyncClient
    def respond(request):
        return httpx.Response(200,json={'choices':[{'finish_reason':'length','message':{'content':'{"claim":"partial"}'}}]})
    monkeypatch.setattr(llm_router.httpx,'AsyncClient',lambda **kw:client(transport=httpx.MockTransport(respond),**kw))
    assert asyncio.run(llm_router.run('test',[],Answer,2))['error_code']=='output_truncated'
    with store.connect() as db:assert db.execute('SELECT COUNT(*) FROM cache').fetchone()[0]==0
