import json
from pathlib import Path
import pytest
from backend.services.screener_service import parse_html
from backend.services.documents import validate_citation,parse_pdf
from backend.services.network import validate_public_url
from backend.services.financials import extract_presentation

R=Path(__file__).resolve().parents[1]

def test_blank_cells_preserve_period_alignment():
 raw=b'<h1>Example</h1><section id="quarters"><table><thead><tr><th></th><th>Jun 2026</th><th>Mar 2026</th></tr></thead><tbody><tr><td>Sales +</td><td></td><td>1,234</td></tr></tbody></table></section>'
 p=parse_html(raw,'https://www.screener.in/company/EXAMPLE/')
 assert p['tables']['quarters']['rows']['Sales']==[None,1234]
 assert p['tables']['quarters']['provenance']=='screener_normalized_secondary'

def test_blocked_page_is_not_a_company():
 with pytest.raises(ValueError):parse_html(b'<h1>Access denied</h1>','https://example.com')
 with pytest.raises(ValueError):parse_pdf(b'<html>not a PDF</html>','https://example.com')

def test_citations_must_point_to_an_exact_quote_on_the_page():
 doc={'id':'abc','pages':[{'page':1,'text':'Revenue was 120 crore this quarter.'}]}
 assert validate_citation({'document_id':'abc','page':1,'quote':'Revenue was 120 crore'},[doc])
 assert not validate_citation({'document_id':'abc','page':2,'quote':'Revenue was 120 crore'},[doc])
 assert not validate_citation({'document_id':'abc','page':1,'quote':'Revenue was 200 crore'},[doc])
 assert not validate_citation({'document_id':'invented','page':1,'quote':'Revenue was 120 crore'},[doc])

@pytest.mark.parametrize('url',['http://example.com','https://localhost/a','https://user:pw@example.com','https://example.com:8443'])
def test_reject_unsafe_document_urls(url):
 with pytest.raises(ValueError):validate_public_url(url)

def test_reported_ebitda_not_screener_operating_profit():
 doc={'id':'x','url':'https://example.com/a.pdf','name':'test','pages':[{'page':2,'text':'DETAILS Q1FY27 Q4FY26 Q1FY26\nRevenue from Operations 1000 900 800\nEBITDA 200 180 160\nPBT 130 110 100\nPAT 100 90 80\nINR MN'}]}
 f=extract_presentation(doc);assert f['rows'][0]['values']==[100,90,80]
 assert f['rows'][2]['qoq']==pytest.approx(0)
 doc['pages'][0]['text']=doc['pages'][0]['text'].replace('EBITDA','Operating Profit')
 assert extract_presentation(doc) is None

def test_snapshot_has_real_provenance_and_unique_disclosures():
 s=json.loads((R/'dist/data/snapshot.json').read_text())
 assert s['mode']=='captured_real_data'
 assert len(s['universe'])==22 and sum(x['group']=='portfolio' for x in s['universe'])==18
 assert len({f['id'] for f in s['filings']})==len(s['filings'])
 assert len(s['prices'])==22
 for e in s['evidence'].values():assert e['url'].startswith('https://') and e['page']>=1 and len(e['hash'])==64
 for d in s['dossiers'].values():
  for row in d['audit']:
   assert row['promise_evidence'] in s['evidence'] and row['outcome_evidence'] in s['evidence']
 assert s['dossiers']['KPITTECH']['financials']['rows'][0]['values'][0]==pytest.approx(1674.994)

def test_sona_statutory_profit_reconciles():
 s=json.loads((R/'dist/data/snapshot.json').read_text())
 f=next(v['financials'] for v in s['rich_filings'].values() if v.get('evidence')=='sona-statutory')
 vals={r['key']:r['values'] for r in f['rows']}
 assert vals['pbt'][0]-72.977==pytest.approx(vals['pat'][0])
 assert vals['ebitda'][0]==pytest.approx(295.964+12.317+78.910-30.951)
 assert vals['revenue'][0]==1535.840

def test_multiline_table_skips_percentage_columns_and_rejects_wrong_quarter_order():
    from backend.services.financials import extract_presentation
    text='Consolidated P&L\nQ2FY27 % Q1FY27 % Q2FY26 %\nRevenue from Operations\n 1000\n 100%\n 800\n 100%\n 600\n 100%\nEBITDA (A)-(B)\n 200\n 20%\n 120\n 15%\n 60\n 10%\nPBT\n 150\n 15%\n 80\n 10%\n 30\n 5%\nPAT\n 120\n 12%\n 60\n 7.5%\n 24\n 4%\nParticulars (₹\n Mn)'
    doc={'url':'https://example.com/results.pdf','name':'Presentation','id':'a'*64,'pages':[{'page':1,'text':text}]}
    result=extract_presentation(doc)
    assert result['rows'][0]['values']==[100,80,60]
    assert result['rows'][1]['values']==[20,12,6]
    assert result['rows'][2]['values']==[20,15,10]
    doc['pages'][0]['text']=text.replace('Q1FY27 % Q2FY26','Q2FY26 % Q1FY27')
    assert extract_presentation(doc) is None
