import pytest
from backend.domain import *

@pytest.mark.parametrize('raw,expected,yahoo',[
 ('POLYCAB','POLYCAB','POLYCAB.NS'),('M&M','M&M','M&M.NS'),('zomato','ETERNAL','ETERNAL.NS'),
 ('NARAYANA','NH','NH.NS'),('500325.BO','500325','500325.BO'),('NSE:TCS','TCS','TCS.NS')])
def test_resolver_generalises(raw,expected,yahoo):
 r=resolve_symbol(raw);assert r['symbol']==expected and r['yahoo']==yahoo
 if raw=='M&M':assert '%26' in r['screener']

@pytest.mark.parametrize('raw',['../etc/passwd','https://localhost','TCS?x=1','RELIANCE.BO','<script>',''])
def test_invalid_symbols(raw):
 with pytest.raises(ValueError):resolve_symbol(raw)

def test_change_bases_and_margin_units():
 assert pct(110,100)==pytest.approx(10)
 assert pct(5,0) is None and pct(5,-10) is None and pct(None,10) is None
 assert bps(20,19)==100
 assert cagr(100,121,2)==pytest.approx(10)
 assert cagr(0,100,5) is None

def test_rvol_excludes_current_bar_and_needs_twenty_sessions():
 bars=[{'date':f'2026-10-{i+1:02d}','close':100,'volume':10} for i in range(20)]
 bars.append({'date':'2026-10-21','close':103,'volume':40})
 m=eod_metrics(bars);assert m['adv20']==10 and m['rvol']==4 and m['triggered']
 assert eod_metrics(bars[-20:])['rvol'] is None
 assert eod_metrics([{'date':str(i),'close':100,'volume':0} for i in range(21)])['rvol'] is None

def test_price_or_volume_trigger():
 bars=[{'date':str(i),'close':100,'volume':10} for i in range(21)]
 bars[-1]['close']=96;assert eod_metrics(bars)['triggered']
 bars[-1]['close']=100;assert not eod_metrics(bars)['triggered']

@pytest.mark.parametrize('text,category,tier',[
 ('Change in Managing Director and Chief Executive Officer','management_change','CRITICAL'),
 ('allotment of securities pursuant to ESOP','unclassified','LOW_NOISE'),
 ('Bagging/Receiving of orders/contracts','press_release','MEDIUM'),
 ('Newspaper advertisement on financial results','unclassified','LOW_NOISE'),
 ('Board meeting intimation for financial results','results','LOW_NOISE'),
 ('Auditor resignation and disclaimer of opinion','litigation','HIGH'),
 ('Quarterly financial results','results','CRITICAL'),
 ('Transcript of post earnings call','earnings_call','MEDIUM'),
 ('Trading window closure','unclassified','LOW_NOISE'),
 ('Something entirely unfamiliar','unclassified','MEDIUM')])
def test_noise_rules_preserve_uncertainty(text,category,tier):
 r=classify(text);assert (r['category'],r['tier'])==(category,tier)

def test_filing_window_uses_event_time_not_future_information():
 rows=[{'symbol':'TCS','published_at':'2026-10-26T16:00:00+05:30','score':100,'tier':'CRITICAL'},
       {'symbol':'TCS','published_at':'2026-10-26T12:00:00+05:30','score':80,'tier':'HIGH'},
       {'symbol':'TCS','published_at':'2026-10-20T12:00:00+05:30','score':99,'tier':'CRITICAL'}]
 assert match_filing('TCS','2026-10-26T15:30:00+05:30',rows)['score']==80
 assert match_filing('LT','2026-10-26T15:30:00+05:30',rows) is None

def test_audit_requires_comparable_basis_and_horizon():
 r={'actual':20.8,'low':21,'high':21,'period_match':False,'basis_match':True}
 assert audit_guidance(r)['status']=='NOT_COMPARABLE'
 r['period_match']=True
 assert audit_guidance(r)=={'status':'MISSED','delta':pytest.approx(-.2)}
 r.update(actual=60,low=65,high=65,direction='lower')
 assert audit_guidance(r)['status']=='BEAT'
 assert credibility([{'status':'NOT_COMPARABLE'}])['score'] is None
 assert credibility([{'status':'BEAT'},{'status':'MISSED'},{'status':'NOT_EVALUABLE'}])['sample_size']==2

def test_cash_quality_unknown_is_not_green():
 assert cash_quality(100,0)['badge']=='UNKNOWN'
 assert cash_quality(65,100)=={'ratio':.65,'badge':'AMBER','review_flag':True}
 assert cash_quality(85,100)['badge']=='GREEN'
