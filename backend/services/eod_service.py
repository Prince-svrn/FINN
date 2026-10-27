import asyncio
import math
from datetime import datetime, timezone, time
from zoneinfo import ZoneInfo
from backend import store
from backend.domain import resolve_symbol, eod_metrics

IST=ZoneInfo('Asia/Kolkata')

def fetch_sync(symbol):
    import yfinance as yf
    identity=resolve_symbol(symbol)
    frame=yf.Ticker(identity['yahoo']).history(period='3mo',interval='1d',auto_adjust=False,actions=True,timeout=15)
    if frame.empty: raise ValueError('Price provider returned no bars (invalid ticker, no coverage, or rate limit).')
    now=datetime.now(IST)
    bars=[]
    for index,row in frame.iterrows():
        date=index.date()
        # Current-day quote is not a completed EOD bar until 16:00 IST.
        if date==now.date() and now.time()<time(16):continue
        close=float(row['Close']);volume=float(row['Volume'])
        if not math.isfinite(close) or not math.isfinite(volume) or close<=0 or volume<0:continue
        bars.append({'date':date.isoformat(),'close':close,'volume':volume,
                     'split':float(row.get('Stock Splits',0)),'dividend':float(row.get('Dividends',0))})
    return {'symbol':identity['symbol'],'bars':bars,'provider':'Yahoo Finance / yfinance',
            'fetched_at':datetime.now(timezone.utc).isoformat(),'source_url':f'https://finance.yahoo.com/quote/{identity["yahoo"]}/history/'}

async def prices(symbol, refresh=False):
    identity=resolve_symbol(symbol);key='eod-v2:'+identity['yahoo']
    if not refresh and (cached:=store.get(key,3600)):return {**cached,'cache_status':'hit'}
    try:
        value=await asyncio.wait_for(asyncio.to_thread(fetch_sync,symbol),timeout=30)
        store.put(key,value);return {**value,'cache_status':'fresh'}
    except Exception as e:
        if cached:=store.get(key):return {**cached,'cache_status':'stale','warning':str(e)}
        return {'symbol':identity['symbol'],'bars':[],'cache_status':'unavailable','warning':str(e)}
