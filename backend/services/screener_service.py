"""Screener discovers primary documents; its aggregates remain explicitly secondary."""
import re
from datetime import datetime, timezone
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup
from backend import store
from backend.domain import resolve_symbol
from backend.services.network import fetch

def number(text):
    text=text.replace(',','').replace('%','').strip()
    if text.startswith('(') and text.endswith(')'): text='-'+text[1:-1]
    try: return float(text)
    except ValueError: return None

def parse_html(raw, url):
    soup=BeautifulSoup(raw,'html.parser')
    title=soup.select_one('h1')
    if not title or not soup.select_one('#quarters table'): raise ValueError('No company financial table found; symbol may be invalid or data restricted.')
    tables={}
    for name in ['quarters','profit-loss','balance-sheet','cash-flow','ratios','shareholding']:
        section=soup.find(id=name)
        table=section.select_one('table') if section else None
        if not table: continue
        headers=[x.get_text(' ',strip=True) for x in table.select('thead th')][1:]
        rows={}
        for row in table.select('tbody tr'):
            cells=row.find_all('td',recursive=False)
            if not cells: continue
            label=re.sub(r'\s*\+\s*$', '',cells[0].get_text(' ',strip=True))
            if label in {'Raw PDF'}: continue
            values=[number(c.get_text(' ',strip=True)) for c in cells[1:]]
            if len(values)==len(headers): rows[label]=values
        tables[name]={'periods': headers,'rows': rows,'provenance':'screener_normalized_secondary','url':url}
    documents=[]
    section=soup.find(id='documents')
    if section:
        counts={}
        for a in section.select('a[href]'):
            text=a.get_text(' ',strip=True)
            if text.startswith('Annual Report'): kind='annual_report'; limit=3
            elif text=='Transcript': kind='transcript'; limit=4
            elif text=='PPT': kind='presentation'; limit=4
            else: continue
            if counts.get(kind,0)>=limit: continue
            href=urljoin(url,a['href'])
            if 'screener.in' in urlsplit(href).netloc: continue # Never ingest AI summaries.
            if 'bseindia.com/stockinfo/AnnPdfOpen.aspx?Pname=' in href:
                href=href.replace('stockinfo/AnnPdfOpen.aspx?Pname=','xml-data/corpfiling/AttachHis/')
            container=a.find_parent('li') or a.parent
            label=container.get_text(' ',strip=True).replace('AI Summary','').replace('Add Missing','')[:160]
            counts[kind]=counts.get(kind,0)+1
            documents.append({'kind':kind,'name':label if kind!='annual_report' else text,'url':href})
    # Link-only recent filing fallback; summaries from Screener are not primary evidence.
    announcements=[]
    if section:
        for a in section.select('a[href]'):
            href=a['href']; text=a.get_text(' ',strip=True)
            if ('AnnPdfOpen' in href or '/corpfiling/' in href) and len(text)>35 and not text.startswith('Annual Report'):
                announcements.append({'headline':text, 'url':href})
                if len(announcements)==5:break
    about=soup.select_one('.company-profile .sub') or soup.select_one('.about')
    return {'name':title.get_text(' ',strip=True),'tables':tables,'documents':documents,
            'discovered_announcements':announcements,'source_url':url,
            'fetched_at':datetime.now(timezone.utc).isoformat(),'content_hash':store.digest(raw),
            'basis':'consolidated' if '/consolidated/' in url else 'standalone'}

async def fetch_company(symbol, refresh=False):
    identity=resolve_symbol(symbol)
    key='screener-v2:'+identity['symbol']
    if not refresh and (cached:=store.get(key,3600)):
        store.log('screener',cache_hit=True); return {**cached,'cache_status':'hit'}
    error=None
    for url in [identity['screener'],identity['screener'].replace('/consolidated/','/')]:
        try:
            raw,final=await fetch(url)
            parsed={**parse_html(raw,final),**identity,'cache_status':'fresh'}
            store.put(key,parsed);store.log('screener');return parsed
        except Exception as e:error=e
    if cached:=store.get(key):return {**cached,'cache_status':'stale','warning':str(error)}
    raise ValueError(f'Fundamentals unavailable for {identity["symbol"]}: {type(error).__name__}') from error
