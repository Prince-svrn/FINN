"""Build the distributable snapshot from captured provider responses.

Raw captures are local intermediates. Curated claims below are explicitly reviewed
fixtures. The reusable live ingestion pipeline does not use ticker-specific logic.
"""
import json,re,sqlite3,shutil
from pathlib import Path
from datetime import datetime,timezone,timedelta
from backend.domain import classify,eod_metrics,pct,bps
from backend.services.financials import extract_presentation
ROOT=Path(__file__).resolve().parents[1]
market=json.loads((ROOT/'data/market.json').read_text())
companies=json.loads((ROOT/'data/companies.json').read_text())
universe=json.loads((ROOT/'config/universe.json').read_text())
kdocs=json.loads((ROOT/'data/kpit_documents.json').read_text())
sdocs=json.loads((ROOT/'data/sona_documents.json').read_text())
# Anchor the briefing to source capture time, not the packaging clock.
captures=[x.get('fetched_at') for v in market.values() for x in [v['filings'],v['prices']] if x.get('fetched_at')]
now=max(datetime.fromisoformat(x) for x in captures)
evidence={}
def ev(key,index,page,label,note='',quote='',symbol='KPITTECH',docs=kdocs):
 d=docs[index];page_text=next(x['text'] for x in d['pages'] if x['page']==page)
 if quote and ' '.join(quote.split()) not in ' '.join(page_text.split()):raise ValueError(f'Unsupported quote {key}')
 evidence[key]={'symbol':symbol,'label':label,'url':d['url'],'page':page,'hash':d['id'],'quote':quote,'note':note}
 return key
fin=extract_presentation(kdocs[9]);annual=extract_presentation(kdocs[10])
ev('kpit-financial',9,24,'Q1 FY27 investor update','Company-reported EBITDA excludes the separately disclosed forex loss. Figures in the source are INR million, converted to ₹ crore by dividing by ten.')
ev('kpit-balance',9,25,'Q1 FY27 balance sheet','Current plus non-current borrowings: ₹412.427 Cr. Equity including NCI: ₹3,686.275 Cr. Borrowings/equity excludes lease liabilities. Cash and bank: ₹1,314.079 Cr.')
ev('kpit-cash',9,9,'Q1 FY27 cash & DSO','Net cash is ₹901.7 Cr. DSO is 51 days. Reported quarterly capex is ₹28.8 Cr; the slide does not supply a complete comparable cash-conversion cycle.')
ev('kpit-business',9,31,'Q1 FY27 company overview','The company describes its focus on embedded software, AI and digital solutions for mobility. This is a company description, not an independent market-share assessment.')
ev('kpit-mix',9,26,'Q1 FY27 operating segments','Primary revenue segment and geography tables support the company’s automotive and mobility focus.')
ev('kpit-annual-metrics',10,25,'FY26 & FY25 financial grid','FY26 revenue: ₹6,454.931 Cr; FY25: ₹5,842.345 Cr. Reported FY26 EBITDA: ₹1,345.660 Cr. Two comparable annual observations are available in this extracted primary grid.')
ev('kpit-audit-q2',8,4,'Q1 FY26 concall → H2 outlook','A half-year directional statement is not a numeric Q2 promise. It is excluded from the numeric commitment score.',quote='H2 will be higher than H1')
ev('kpit-audit-q3',7,7,'Q2 FY26 concall → Q3 outlook','The comparison uses organic constant-currency growth, not reported rupee revenue.',quote='flattish to positive organic constant currency growth')
ev('kpit-audit-q3-actual',6,4,'Q3 FY26 concall → delivered','Management reported negative organic growth of less than 1% despite positive reported constant-currency growth.',quote='Organic growth is negative under 1%')
ev('kpit-audit-q4',6,11,'Q3 FY26 concall → Q4 outlook','The claim is directional. The observed acceleration does not justify a numeric beat magnitude.',quote='it will be the highest quarterly growth in FY26')
ev('kpit-audit-q4-actual',10,5,'Q4 FY26 operating performance','Q4 constant-currency sequential growth was 1.8%; Q3 was 1.5%. This supports acceleration, without claiming a specific numeric guidance beat.')
ev('kpit-annual-promise',7,5,'Q2 FY26 concall → FY26 margin','Annual guidance is compared against FY26, not a single quarter.',quote='maintain 21% EBITDA for the full year')
ev('kpit-annual-outcome',10,5,'FY26 delivered margin','The company reports FY26 EBITDA margin of 20.8%, versus 21% guidance: approximately 20 basis points lower on the rounded disclosed percentages.')
ev('kpit-fy27-promise',5,17,'May 2026 investor meet → FY27','The stated 20.5–21.2% EBITDA range refers to full FY27. Later updates must be checked before treating it as active guidance.',quote='EBITDA 20.5 to 21.2')
latest=next(i for i,d in enumerate(kdocs) if d['name']=='Q1 FY27 transcript')
ev('kpit-guidance',latest,4,'Q1 FY27 concall → recovery outlook','Management discusses returning to growth in H2, led by Q4. The horizon has not matured in the saved results. This is qualitative, not a guaranteed growth rate.')
ev('kpit-margin-guidance',latest,9,'Q1 FY27 concall → margin outlook','Management expects an incremental margin recovery; no numeric quarterly band is supplied in this excerpt.',quote='the margins will improve')
ev('kpit-wins',9,10,'Q1 FY27 new engagements','New engagements total US$257 million. Contract wins are not recognized revenue and may convert over multiple periods.')
ev('kpit-risk',9,7,'Q1 FY27 profitability context','Forex loss and Qorix losses affect profit; reported EBITDA excludes the disclosed forex item. Margin and PAT should not be treated as interchangeable measures.')
ev('kpit-director',0,6,'Board appointment & biography','The board filing describes Nirmala Pandit’s institution-building, education and legal background. This is an issuer-disclosed biography; external career verification has not been run.')
# The quoted biography summary is checked against the full annexure during build review.
filings=[]
for symbol,v in market.items():
 for f in v['filings']['items']:
  at=datetime.fromisoformat(f['published_at'])
  if now-timedelta(days=125)<=at<=now:
   f={**f,**classify(f['headline']+' '+f['detail'])};f['status']='captured';filings.append(f)
# Preserve distinct documents; deduplicate only identical identities.
filings=list({f['id']:f for f in filings}.values())
prices={s:{**v['prices'],'metrics':eod_metrics(v['prices']['bars'])} for s,v in market.items() if v['prices']['bars']}
for c in companies.values():
 # Discovery packs keep links and provenance, not secondary claims in Pull UI.
 c.pop('discovered_announcements',None)
rich={}
kf=next(f for f in filings if f['symbol']=='KPITTECH' and f['source_url']==kdocs[0]['url'])
rich[kf['id']]={'headline':'Rupee revenue grows. Profitability moves the other way.','takeaway':'Q1 FY27 revenue rose 8.9% YoY; company-reported EBITDA margin fell 387 bps. Currency and accounting basis matter.','financials':fin,'evidence':'kpit-financial'}
# Multiple material events may live inside one filing. An explicit event ID avoids
# hiding a board appointment behind a results headline without double counting PDFs.
director={**kf,'id':kf['id']+'-director','parent_filing_id':kf['id'],'category':'management_change','tier':'CRITICAL','score':90,'headline':'Nirmala Pandit appointed to KPIT’s board','detail':'Additional non-independent, non-executive director; effective 29 July 2026. No one-to-one predecessor was stated for this appointment.'}
# Kept as a replay card separate from raw digest accounting.
replay=[kf,director]
rich[director['id']]={'headline':'Nirmala Pandit joins the board. Here is the background.','takeaway':'Non-independent, non-executive director · effective 29 July 2026. A new appointment; no direct outgoing counterpart disclosed.','bio':'Issuer-disclosed background: legal academic and institution builder; former University of Pune law faculty; PhD in Law. External profile verification remains outstanding.','evidence':'kpit-director'}
# Avoid two bulky first-cut cards for the same result; the press release remains
# separately auditable in the priority stream, as a distinct exchange document.
press=next(f for f in filings if f['symbol']=='SONACOMS' and f['published_at'][:10]=='2026-10-26' and f['headline']=='Press Release')
rich[press['id']]={'headline':'BEV revenue more than doubles; orders add ₹3,600 Cr.','takeaway':'The result release reports 129% YoY BEV revenue growth and a ₹25,100 Cr net order book. Orders are not booked revenue.','evidence':'sona-orders'}
quarter_values={}
for d in kdocs:
 if d['kind']=='presentation' and (f:=extract_presentation(d)):
  for q,value in zip(f['periods'],f['rows'][0]['values']):quarter_values[q]=value
order=['Q2FY25','Q3FY25','Q4FY25','Q1FY26','Q2FY26','Q3FY26','Q4FY26','Q1FY27']
dossier={'financials':fin,'business':[{'text':'A mobility software specialist focused on embedded software, AI and digital solutions for vehicle manufacturers.','evidence':'kpit-business'},{'text':'The client and practice mix spans passenger vehicles, commercial vehicles and connected, autonomous and powertrain software.','evidence':'kpit-mix'}],
 'balance':{'period':'Q1 FY27','debt':412.427,'cash':1314.079,'net_cash':901.7,'de':412.427/3686.275,'dso':51,'note':'Borrowings exclude leases. Adding ₹365.557 Cr of lease liabilities takes debt including leases/equity to approximately 0.21×. Net cash here uses the company’s definition.'},
 'cash':{'ratio':None,'note':'Quarterly capex is ₹28.8 Cr and net cash is ₹901.7 Cr. A verified, like-for-like three-year CFO and reported EBITDA series has not been assembled; the conversion traffic light stays unknown.'},
 'trajectory':{'quarters':[{'label':q,'value':quarter_values[q]} for q in order if q in quarter_values],'annual':[{'label':'FY25','value':5842.345},{'label':'FY26','value':6454.931}],'quarter_note':'Q1 FY27 rupee revenue is 8.9% above the year-ago quarter, while reported EBITDA margin is 387 bps lower. Rupee growth is not constant-currency growth.','annual_note':'FY26 revenue grew 10.5% in rupees. Only two annual primary observations are extracted here; a five-year CAGR is deliberately withheld.'},
 'audit':[
 {'quarter':'Q2 FY26','promise':'H2 will be higher than H1','promise_evidence':'kpit-audit-q2','delivered':'Q2 rupee revenue: ₹1,587.7 Cr; reported EBITDA margin: 21.11%.','outcome_evidence':'kpit-q2-financial','verdict':'NOT COMPARABLE','note':'The promise applies to H2, not Q2. Quarterly growth cannot establish whether it was met.'},
 {'quarter':'Q3 FY26','promise':'flattish to positive organic constant currency growth','promise_evidence':'kpit-audit-q3','delivered':'Management reported organic growth below zero (decline of less than 1%).','outcome_evidence':'kpit-audit-q3-actual','verdict':'MISSED','note':'A directional miss on the same organic-growth basis. Positive reported growth does not erase it; no invented numeric miss magnitude.'},
 {'quarter':'Q4 FY26','promise':'it will be the highest quarterly growth in FY26','promise_evidence':'kpit-audit-q4','delivered':'Sequential constant-currency growth reached 1.8%, compared with 1.5% in Q3.','outcome_evidence':'kpit-audit-q4-actual','verdict':'DIRECTION SUPPORTED','note':'Acceleration is supported. The stronger “highest all year” claim requires every prior quarter on the same currency basis; no numeric beat is assigned.'},
 {'quarter':'Q1 FY27','promise':'EBITDA 20.5 to 21.2','promise_evidence':'kpit-fy27-promise','delivered':'Q1 reported EBITDA margin: 17.18%; June/July updates flagged program-related weakness.','outcome_evidence':'kpit-financial','verdict':'ANNUAL HORIZON OPEN','note':'This May range was for full FY27. Q1 alone cannot be judged against it. Later outlook updates must be reconciled before a full-year verdict.'}],
 'commitment':{'text':'FY26 EBITDA margin was reported at 20.8%, approximately 20 bps below the 21% full-year commitment. One observation is not a general credibility assessment.','promise':'kpit-annual-promise','outcome':'kpit-annual-outcome'},
 'guidance':[{'title':'Growth recovery','status':'OPEN · H2 FY27','text':'Management expects a return to growth in H2, led by Q4. No precise quarterly revenue target is supplied in the cited passage.','evidence':'kpit-guidance'},{'title':'Margin recovery','status':'QUALITATIVE','text':'Margins are expected to improve incrementally. The original May annual range should be read alongside the later outlook.','evidence':'kpit-margin-guidance'},{'title':'Capex & capacity','status':'NOT EXTRACTED','text':'No verified forward numeric capex or capacity target is included in this reviewed snapshot. Missing is not zero.','evidence':'kpit-cash'}],
 'bull':[{'text':'US$257m of quarterly engagement wins provides evidence of demand; conversion to revenue remains to be tracked.','evidence':'kpit-wins'},{'text':'The company retains ₹901.7 Cr of net cash under its disclosed definition.','evidence':'kpit-cash'},{'text':'FY26 rupee revenue grew to ₹6,454.9 Cr, up from ₹5,842.3 Cr.','evidence':'kpit-annual-metrics'}],
 'bear':[{'text':'Q1 FY27 EBITDA margin fell 387 bps YoY despite 8.9% rupee revenue growth.','evidence':'kpit-financial'},{'text':'Reported profitability is sensitive to forex and equity-accounted investee losses.','evidence':'kpit-risk'},{'text':'The promised Q3 organic recovery did not materialise; reported and organic growth need separate monitoring.','evidence':'kpit-audit-q3-actual'}],
 'governance':[{'text':'A promoter-linked board appointment is disclosed with the candidate’s background. It merits review, not an automatic wrongdoing flag.','evidence':'kpit-director'},{'text':'Contingent liabilities, related-party flows and annual audit qualifications have not been fully reviewed. No “all clear” conclusion is drawn.','evidence':'kpit-annual-metrics'}]}
ev('kpit-q2-financial',12,22,'Q2 FY26 financial grid','₹1,587.711 Cr revenue; ₹335.095 Cr company-reported EBITDA. Derived margin: 21.1055%.')
snapshot={'as_of':now.isoformat(),'price_as_of':max(p['metrics']['date'] for p in prices.values()),'mode':'captured_real_data','universe':universe,'filings':filings,'prices':prices,'companies':companies,'rich_filings':rich,'evidence':evidence,'dossiers':{'KPITTECH':dossier},'replay':replay,'limitations':['Snapshot is not a streaming feed','One reviewed deep dossier','Scanned results require OCR','Optional models not exercised without credentials']}
(ROOT/'dist/data').mkdir(parents=True,exist_ok=True)
(ROOT/'dist/data/snapshot.json').write_text(json.dumps(snapshot,ensure_ascii=False,allow_nan=False,separators=(',',':')))
# Portable deterministic caches omit copyrighted full document text and credentials.
seed=ROOT/'data/seed_cache.db'
if seed.exists():seed.unlink()
db=sqlite3.connect(seed)
db.executescript('CREATE TABLE cache(key TEXT PRIMARY KEY,value TEXT NOT NULL,created REAL NOT NULL);CREATE TABLE filings(id TEXT PRIMARY KEY,symbol TEXT,published_at TEXT,value TEXT);')
for s,c in companies.items():db.execute('INSERT INTO cache VALUES (?,?,?)',('screener-v2:'+s,json.dumps(c),now.timestamp()))
for s,p in prices.items():db.execute('INSERT INTO cache VALUES (?,?,?)',('eod-v2:'+s+'.NS',json.dumps(p),now.timestamp()))
for s in market:
 fs=[f for f in filings if f['symbol']==s]
 db.execute('INSERT INTO cache VALUES (?,?,?)',('filings-v1:'+s+'.NS',json.dumps({'items':fs,'cache_status':'captured','fetched_at':now.isoformat()}),now.timestamp()))
for f in filings:db.execute('INSERT INTO filings VALUES (?,?,?,?)',(f['id'],f['symbol'],f['published_at'],json.dumps(f)))
db.commit();db.close()
print('Built',len(filings),'filings,',len(prices),'price series,',len(companies),'source packs,',len(evidence),'page references')

# Reviewed additions are mandatory, never an optional second build step.
import runpy
runpy.run_path(str(ROOT/"scripts/enhance_snapshot.py"))
