import hashlib
import json
from datetime import datetime,timezone
from zoneinfo import ZoneInfo
from urllib.parse import urlencode
import httpx
from backend import store
from backend.domain import classify,resolve_symbol,CATEGORIES
from backend.services.network import fetch,USER_AGENT
from backend.llm_router import run
from backend.schemas import FilingAnalysisSchema

def timestamp(value):
    for fmt in ['%d-%b-%Y %H:%M:%S','%Y-%m-%d %H:%M:%S','%d-%m-%Y %H:%M:%S']:
        try:return datetime.strptime(value,fmt).replace(tzinfo=ZoneInfo('Asia/Kolkata')).isoformat()
        except (ValueError,TypeError):pass
    try:
        parsed=datetime.fromisoformat(value)
        return (parsed if parsed.tzinfo else parsed.replace(tzinfo=ZoneInfo('Asia/Kolkata'))).isoformat()
    except (ValueError,TypeError):return None

async def filings(symbol,refresh=False):
    ident=resolve_symbol(symbol);key='filings-v1:'+ident['yahoo']
    if not refresh and (old:=store.get(key,900)):return {**old,'cache_status':'hit'}
    if ident['exchange']=='BSE':return {'items':[],'cache_status':'unavailable','warning':'Direct BSE feed adapter is not implemented; primary documents are discovered through Screener.'}
    try:
        async with httpx.AsyncClient(timeout=20,headers={'User-Agent':USER_AGENT,'Accept':'application/json','Referer':'https://www.nseindia.com/'}) as client:
            await fetch('https://www.nseindia.com/',client)
            raw,_=await fetch('https://www.nseindia.com/api/corporate-announcements?'+urlencode({'index':'equities','symbol':ident['symbol']}),client)
        data=json.loads(raw)
        if not isinstance(data,list):raise ValueError('Unexpected exchange response.')
        items=[]
        for row in data:
            at=timestamp(row.get('an_dt') or row.get('sort_date'))
            if not at:continue
            headline=row.get('desc','');description=row.get('attchmntText','')
            text=headline+' '+description
            source=row.get('attchmntFile','')
            classified=classify(text)
            if classified['category']=='unclassified' and classified['reason'] and not any(t in text.lower() for t in ['trading window','74 (5)','certificate','esop']):
                from backend.prompts import FILING_PROMPT
                model=await run('ambiguous_filing',[{'role':'system','content':FILING_PROMPT},{'role':'user','content':text}],FilingAnalysisSchema,1)
                if model['status']=='ok':
                    v=model['data'];tier,_=CATEGORIES[v['category']]
                    classified={**classified,'category':v['category'],'tier':tier,'score':v['materiality_score'],'route':'T1','reason':'Model classification; inspect source'}
            item={'id':hashlib.sha256((ident['symbol']+source+at+headline).encode()).hexdigest()[:24],
                  'symbol':ident['symbol'],'headline':headline,'detail':description[:600],'published_at':at,
                  'source_url':source,'source_kind':'exchange','status':'live',**classified}
            items.append(item)
        result={'items':items,'cache_status':'fresh','fetched_at':datetime.now(timezone.utc).isoformat()}
        store.put(key,result)
        with store.connect() as db:
            db.executemany('INSERT OR REPLACE INTO filings VALUES (?,?,?,?)',[(i['id'],i['symbol'],i['published_at'],json.dumps(i)) for i in items])
        return result
    except Exception as e:
        if old:=store.get(key):return {**old,'cache_status':'stale','warning':type(e).__name__}
        return {'items':[],'cache_status':'unavailable','warning':f'Exchange feed unavailable: {type(e).__name__}. No inference from missing coverage.'}
