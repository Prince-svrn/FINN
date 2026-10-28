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
