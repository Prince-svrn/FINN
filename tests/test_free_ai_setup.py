import asyncio
from dotenv import dotenv_values
from scripts.setup_free_ai import update_env,DEFAULTS
from backend import store
from backend.services import research_service as service

def test_setup_replaces_old_key_and_duplicates_preserving_other_settings(tmp_path):
    path=tmp_path/'.env'
    path.write_text('# Keep this comment\nFINN_LLM_API_KEY=old-key\nexport FINN_LLM_API_KEY=duplicate\nFINN_MODEL_T2=old-model\nFINN_API_TOKEN=keep-local-token\n')
    update_env(path,{**DEFAULTS,'FINN_LLM_API_KEY':'test-gemini-key'})
    values=dotenv_values(path)
    assert values['FINN_LLM_API_KEY']=='test-gemini-key'
    assert values['FINN_API_TOKEN']=='keep-local-token'
    assert values['FINN_MODEL_T1']=='' and values['FINN_POLL_INTERVAL_SECONDS']=='0'
    assert values['FINN_MODEL_T2']=='gemini-3.5-flash-lite'
    assert values['FINN_T2_INPUT_USD_PER_MILLION']==''
    text=path.read_text()
    assert text.count('FINN_LLM_API_KEY=')==1 and 'old-key' not in text
    assert '# Keep this comment' in text
    assert len(list(tmp_path.iterdir()))==1

def test_research_returns_model_error_to_frontend(tmp_path,monkeypatch):
    monkeypatch.setattr(store,'DB_PATH',tmp_path/'research.db')
    async def company(*args):return {'symbol':'TEST','name':'Test company','documents':[]}
    async def price(*args):return {}
    async def discover(*args):return [{'kind':'transcript','url':'https://example.com/a.pdf','name':'Call'}]
    async def ingest(doc):return {**doc,'id':'doc1','pages':[{'page':1,'text':'Revenue rose this quarter.'}]}
    async def model(*args):return {'status':'error','error_code':'rate_limited','reason':'Free quota reached. Try again after reset.'}
    monkeypatch.setattr(service,'fetch_company',company)
    monkeypatch.setattr(service,'prices',price)
    monkeypatch.setattr(service,'discover_documents',discover)
    monkeypatch.setattr(service,'ingest',ingest)
    monkeypatch.setattr(service,'run',model)
    result=asyncio.run(service.research('TEST',use_models=True))
    assert result['analysis'] is None and result['coverage']['downloaded']==1
    assert result['analysis_error_code']=='rate_limited'
    assert 'Free quota' in result['analysis_reason']
    assert store.get('research-v1:TEST')['analysis_reason']==result['analysis_reason']
