import json
import pytest
from fastapi.testclient import TestClient
from backend import store
from backend.app import app

@pytest.fixture
def client(tmp_path,monkeypatch):
 monkeypatch.setattr(store,'DB_PATH',tmp_path/'test.db')
 monkeypatch.delenv('FINN_API_TOKEN',raising=False)
 with TestClient(app) as c:yield c

def test_settings_round_trip_and_validation(client):
 assert client.get('/api/health').json()['status']=='ok'
 v={'price_threshold_pct':4.5,'volume_multiplier_threshold':3.,'categories':['results']}
 assert client.put('/api/settings',json=v).status_code==200
 assert client.get('/api/settings').json()==v
 assert client.put('/api/settings',json={**v,'price_threshold_pct':99}).status_code==422
 assert client.put('/api/settings',json={**v,'categories':['fake']}).status_code==422

def test_digest_window_and_source_ids(client):
 assert client.get('/api/digest?start=2026-10-28T00:00:00%2B05:30&end=2026-10-27T00:00:00%2B05:30').status_code==422
 assert client.get('/api/digest?start=2026-10-26').status_code==422
 r=client.get('/api/digest?start=2026-10-26T00:00:00%2B05:30&end=2026-10-27T23:59:59%2B05:30').json()
 assert r['raw_count']==len(r['items']) and r['raw_count']>0

def test_pins_and_export(client):
 pin={'id':'test','symbol':'TCS','title':'Test evidence','note':'Review working capital','source_url':'https://example.com/report.pdf','source_label':'Test report'}
 assert client.put('/api/pins/test',json=pin).status_code==200
 assert client.get('/api/pins').json()[0]['note']=='Review working capital'
 assert 'Review working capital' in client.get('/api/memo').text
 assert client.delete('/api/pins/test').status_code==200
 assert client.get('/api/pins').json()==[]

def test_missing_model_key_is_not_fake_success(client,monkeypatch):
 import asyncio
 from backend.llm_router import run
 from backend.schemas import FilingAnalysisSchema
 monkeypatch.delenv('FINN_LLM_API_KEY',raising=False)
 assert asyncio.run(run('test',[],FilingAnalysisSchema))['status']=='unavailable'

def test_bad_upload_and_api_auth(client,monkeypatch):
 assert client.post('/api/documents?symbol=TCS',files={'file':('fake.pdf',b'<html>oops</html>','application/pdf')}).status_code==422
 monkeypatch.setenv('FINN_API_TOKEN','local-test-token')
 assert client.get('/api/health').status_code==401
 assert client.get('/api/health',headers={'Authorization':'Bearer local-test-token'}).status_code==200

def test_hosting_readiness_public_but_api_still_protected(client,monkeypatch):
 monkeypatch.setenv('FINN_API_TOKEN','reviewer-secret')
 assert client.get('/healthz').json()=={'status':'ok'}
 assert client.get('/api/health').status_code==401
 html=client.get('/').text
 assert '<meta name="finn-backend" content="same-origin">' in html
 assert 'reviewer-secret' not in html
 assert 'finn-backend' not in ( __import__('pathlib').Path(__file__).parents[1]/'dist/index.html').read_text()
