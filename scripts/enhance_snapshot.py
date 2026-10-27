"""Apply reviewed primary-source additions after the baseline snapshot build."""
import json
from pathlib import Path
from backend.domain import pct,bps,cagr
R=Path(__file__).resolve().parents[1];p=R/'dist/data/snapshot.json';s=json.loads(p.read_text());e=s['evidence'];d=s['dossiers']['KPITTECH']
kdocs=json.loads((R/'data/kpit_documents.json').read_text());ar=next(x for x in kdocs if x['kind']=='annual_report' and len(x['pages'])>100)
def ev(key,doc,page,label,note,symbol='KPITTECH'):
 e[key]={'symbol':symbol,'label':label,'url':doc['url'],'page':page,'hash':doc['id'],'quote':'','note':note}
ev('kpit-annual-cash',ar,150,'FY26 audited consolidated cash flow','CFO is after income tax: ₹1,194.774 Cr in FY26 and ₹1,389.527 Cr in FY25. Gross purchases of property, plant, equipment and intangible assets: ₹142.572 Cr and ₹129.529 Cr respectively. Acquisition payments are disclosed separately, not relabelled as capex.')
ev('kpit-five-year',ar,12,'FY22–FY26 five-year highlights','Revenue in US$ million: 328.4, 418.3, 587.3, 691.4, 724.8. This is a dollar-revenue series, not a rupee series. Five annual observations span four compounding intervals.')
ev('kpit-contingencies',ar,185,'FY26 consolidated note 54','Note 54.2 separates bank guarantees, customs bonds and appealed tax matters. Corporate guarantees of ₹828.99 million were also disclosed; the subsidiaries had not drawn borrowings at the reporting date. They should not be added to current debt.')
fy25=json.loads((R/'data/kpit_fy25_document.json').read_text())
ev('kpit-previous-cash',fy25,153,'FY25 & FY24 audited consolidated cash flow','PDF spread p.153 (printed pp.304–305): FY24 CFO ₹1,001.767 Cr and gross PPE/intangible purchases ₹155.337 Cr; FY25 comparatives reconcile to the FY26 report.')
periods=['FY24','FY25','FY26'];cfos=[1001.767,1389.527,1194.774];ebitdas=[991.32,1229.78,1345.66];capex=[155.337,129.529,142.572]
d['cash']={'period':'FY24–FY26 cumulative','cfo':sum(cfos),'ebitda':sum(ebitdas),'fcf':sum(cfos)-sum(capex),'ratio':sum(cfos)/sum(ebitdas),'evidence':'kpit-annual-cash','previous_evidence':'kpit-previous-cash','years':[{'label':q,'cfo':c,'ebitda':v,'capex':a,'fcf':c-a} for q,c,v,a in zip(periods,cfos,ebitdas,capex)],'note':'Three-year CFO / reported EBITDA is 100.5%: above the 80% green threshold and no <70% forensic flag. CFO is after cash tax; EBITDA is pre-tax, so this is a cash-quality indicator, not like-for-like profit. FCF = CFO minus gross PPE/intangible purchases, before acquisitions. EBITDA uses rounded annual-report highlights; acquisitions and working-capital timing can affect comparability.'}
d['trajectory']['annual_metrics']=[{'year':q,'margin':m,'roe':r} for q,m,r in zip(['FY22','FY23','FY24','FY25','FY26'],[18,18.9,20.3,21,20.8],[20.9,23.1,27.7,28.8,18])]
d['trajectory']['annual']=[{'label':q,'value':v} for q,v in zip(['FY22','FY23','FY24','FY25','FY26'],[328.4,418.3,587.3,691.4,724.8])]
d['trajectory']['annual_note']=f'Five-year USD revenue trajectory: {cagr(328.4,724.8,4):.1f}% CAGR over four annual intervals. Latest FY26 USD growth is 4.8%. Currency basis is explicitly USD; quarterly charts use INR.'
d['governance'][1]={'text':'Consolidated note 54 discloses guarantees, customs bonds and tax matters separately. Undrawn guarantees are not current debt; related-party flows and auditor commentary still require a full review.','evidence':'kpit-contingencies'}
# Current leadership change: primary filing plus official career profile enrichment.
h=json.loads((R/'data/hdfc_document.json').read_text());ev('hdfc-ceo',h,1,'27 Oct 2026 leadership filing','Sashidhar Jagdishan completed his term on 26 October. Anup Bagchi assumed charge as MD & CEO on 27 October 2026. The official board profile supplies career background; the exchange filing controls the current appointment date.','HDFCBANK')
f=next(f for f in s['filings'] if f['symbol']=='HDFCBANK' and f['source_url']==h['url'])
s['rich_filings'][f['id']]={'headline':'Anup Bagchi takes charge as HDFC Bank’s MD & CEO.','takeaway':'Sashidhar Jagdishan → Anup Bagchi · effective 27 October 2026. Jagdishan’s term ended at the previous day’s close.','bio_items':[{'label':'Prior leadership','value':'Former MD & CEO, ICICI Life; previously Executive Director, ICICI Bank (2017–2023).'}, {'label':'Experience','value':'Banking, securities and insurance; retail, wholesale and digital financial services.'},{'label':'Education','value':'Engineering, IIT Kanpur; management, IIM Bangalore.'}],'bio_source':'https://www.hdfc.bank.in/about-us/board-of-directors/mr-anup-bagchi','evidence':'hdfc-ceo'}
# Scanned financial grid manually checked against a rendered page after OCR.
sona=json.loads((R/'data/sona_documents.json').read_text());doc=sona[1]
ev('sona-statutory',doc,12,'Q2 FY27 consolidated results · reviewed scan','PDF p.12 was rendered and visually reviewed after OCR. Revenue is from operations. Reconciled EBITDA = profit before exceptional items and tax + finance costs + depreciation/amortisation − other income. The presentation uses revenue including FX and quotes a different margin denominator. PAT below includes NCI; owner PAT is separate.','SONACOMS')
rows=[]
for key,label,v in [('revenue','Revenue (operations)',[1535.840,1301.201,1138.293]),('ebitda','EBITDA*',[356.240,302.604,289.057]),('pbt','PBT',[295.964,240.942,227.559]),('pat','PAT incl. NCI',[222.987,178.513,170.466])]:rows.append({'key':key,'label':label,'values':v,'qoq':pct(v[0],v[1]),'yoy':pct(v[0],v[2]),'unit':'₹ Cr'})
m=[a/b*100 for a,b in zip(rows[1]['values'],rows[0]['values'])];rows.insert(2,{'key':'margin','label':'EBITDA / ops sales','values':m,'qoq':bps(m[0],m[1]),'yoy':bps(m[0],m[2]),'unit':'%'})
f=next(f for f in s['filings'] if f['symbol']=='SONACOMS' and f['published_at'][:10]=='2026-10-26' and f['headline']=='Outcome of Board Meeting');f['score']=96
s['rich_filings'][f['id']]={'headline':'Record revenue. A narrower operating margin.','takeaway':f'Revenue from operations +{rows[0]["yoy"]:.1f}% YoY; reconciled EBITDA +{rows[1]["yoy"]:.1f}%. Margin on operating sales falls {abs(rows[2]["yoy"]):.0f} bps.','financials':{'periods':['Q2FY27','Q1FY27','Q2FY26'],'rows':rows,'basis':'consolidated; statutory results','note':'*EBITDA before exceptional items, excluding other income; reconciled from statutory components. Margin uses operating revenue. The company presentation includes FX in revenue (23.0% margin). Source scan visually checked.','source':{'url':doc['url'],'page':12}},'evidence':'sona-statutory'}
# Separate source for the press-release assertions, not an unrelated financial page.
ev('sona-orders',sona[0],2,'Q2 FY27 result release','Issuer reports 129% BEV revenue growth, new orders of ₹3,600 Cr, and a ₹25,100 Cr net order book. Order book is not recognized revenue.','SONACOMS')
f=next(f for f in s['filings'] if f['symbol']=='SONACOMS' and f['published_at'][:10]=='2026-10-26' and f['headline']=='Press Release');s['rich_filings'][f['id']]['evidence']='sona-orders'
e.pop('sona-results',None)
p.write_text(json.dumps(s,ensure_ascii=False,allow_nan=False,separators=(',',':')))
print('Enhanced snapshot:',len(e),'evidence references; Sona margin',rows[2]['yoy'])
