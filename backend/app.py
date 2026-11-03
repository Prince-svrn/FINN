"""Single-process prototype API. `./start.sh` serves both API and UI."""
import asyncio
import json
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime,timedelta,timezone
from pathlib import Path
from fastapi import FastAPI,HTTPException,UploadFile,File,Query,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from backend import store
from backend.domain import resolve_symbol,eod_metrics,match_filing,CATEGORIES
from backend.schemas import Settings,ResearchRequest,Pin
from backend.services.research_service import research
from backend.services.screener_service import fetch_company
from backend.services.eod_service import prices
from backend.services.filings_service import filings
from backend.services.documents import parse_pdf
from backend.services.enrichment import executive_background

ROOT=Path(__file__).resolve().parents[1]
UNIVERSE=json.loads((ROOT/'config/universe.json').read_text())
refresh_lock=asyncio.Lock()

def settings():
    with store.connect() as db:r=db.execute('SELECT value FROM settings WHERE key=?',('default',)).fetchone()
    return Settings.model_validate_json(r[0]) if r else Settings()

async def refresh_portfolio():
    if refresh_lock.locked():return {'status':'already_running'}
    async with refresh_lock:
        semaphore=asyncio.Semaphore(3)
        async def one(row):
            async with semaphore:
                f,p=await asyncio.gather(filings(row['symbol'],True),prices(row['symbol'],True))
                return {'symbol':row['symbol'],'filings':f['cache_status'],'prices':p['cache_status']}
        return {'status':'complete','sources':await asyncio.gather(*(one(r) for r in UNIVERSE if r['group']=='portfolio'))}

@asynccontextmanager
async def lifespan(app):
    if not store.DB_PATH.exists() and (ROOT/'data/seed_cache.db').exists():
        import shutil
        store.DB_PATH.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/'data/seed_cache.db',store.DB_PATH)
    store.connect().close()
    interval=int(os.getenv('FINN_POLL_INTERVAL_SECONDS','0'))
    async def poll():
        while True:
            try:await refresh_portfolio()
            except Exception:store.log('portfolio_poll',status='error')
            await asyncio.sleep(max(interval,300))
    task=asyncio.create_task(poll()) if interval else None
    yield
    if task:
        task.cancel()
        try:await task
        except asyncio.CancelledError:pass

app=FastAPI(title='FINN — Evidence-first investment intelligence',version='1.0.0',lifespan=lifespan)
origins=[x for x in os.getenv('FINN_CORS_ORIGINS','').split(',') if x]
if origins:app.add_middleware(CORSMiddleware,allow_origins=origins,allow_methods=['GET','POST','PUT','DELETE'],allow_headers=['Authorization','Content-Type'])

@app.middleware('http')
async def protect_api(request:Request,call_next):
    token=os.getenv('FINN_API_TOKEN')
    if token and request.url.path.startswith('/api/') and request.headers.get('authorization')!='Bearer '+token:
        from fastapi.responses import JSONResponse
        return JSONResponse({'detail':'API token required'},status_code=401)
    response=await call_next(request)
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Referrer-Policy']='strict-origin-when-cross-origin'
    return response

@app.get('/api/health')
def health():return {'status':'ok','mode':'live_backend','models_configured':bool(os.getenv('FINN_LLM_API_KEY')),'polling_seconds':int(os.getenv('FINN_POLL_INTERVAL_SECONDS','0'))}

@app.get('/api/bootstrap')
def bootstrap():
    file=ROOT/'dist/data/snapshot.json'
    data=json.loads(file.read_text()) if file.exists() else {'universe':UNIVERSE,'filings':[],'prices':{},'companies':{}}
    data['backend']=True;data['settings']=settings().model_dump()
    return data

@app.get('/api/universe')
def universe():return UNIVERSE

@app.get('/api/settings')
def get_settings():return settings()

@app.put('/api/settings')
def set_settings(value:Settings):
    with store.connect() as db:db.execute('INSERT OR REPLACE INTO settings VALUES (?,?)',('default',value.model_dump_json()))
    return value

@app.get('/api/company/{symbol}')
async def company(symbol:str,refresh:bool=False):
    try:return await fetch_company(symbol,refresh)
    except ValueError as e:raise HTTPException(422,str(e)) from e

@app.get('/api/prices/{symbol}')
async def get_prices(symbol:str):
    try:
        value=await prices(symbol);s=settings()
        return {**value,'metrics':eod_metrics(value['bars'],s.price_threshold_pct,s.volume_multiplier_threshold)}
    except ValueError as e:raise HTTPException(422,str(e)) from e

@app.get('/api/digest')
def digest(start:str|None=None,end:str|None=None):
    try:
        end_at=datetime.fromisoformat(end) if end else datetime.now(timezone.utc)
        start_at=datetime.fromisoformat(start) if start else end_at-timedelta(hours=24)
        if not end_at.tzinfo or not start_at.tzinfo or start_at>end_at:raise ValueError()
    except ValueError:raise HTTPException(422,'Use ISO dates with timezone; start must precede end.')
    symbols={r['symbol'] for r in UNIVERSE if r['group']=='portfolio'}
    with store.connect() as db:items=[json.loads(r['value']) for r in db.execute('SELECT value FROM filings')]
    selected=[f for f in items if f['symbol'] in symbols and start_at<=datetime.fromisoformat(f['published_at'])<=end_at]
    selected.sort(key=lambda f:(f['score'],f['published_at']),reverse=True)
    return {'items':selected,'raw_count':len(selected),'noise_count':sum(f['tier']=='LOW_NOISE' for f in selected),'window':{'start':start_at.isoformat(),'end':end_at.isoformat()}}

@app.get('/api/alerts')
def alerts():
    s=settings();out=[]
    with store.connect() as db:all_filings=[json.loads(r['value']) for r in db.execute('SELECT value FROM filings')]
    for row in UNIVERSE:
        if row['group']!='portfolio':continue
        p=store.get('eod-v2:'+row['yahoo'])
        if not p:continue
        metric=eod_metrics(p['bars'],s.price_threshold_pct,s.volume_multiplier_threshold)
        if metric.get('triggered'):
            close_at=metric['date']+'T15:30:00+05:30'
            out.append({'symbol':row['symbol'],**metric,'related_filing':match_filing(row['symbol'],close_at,all_filings),
                        'attribution':'Contemporaneous disclosure; causality not established.'})
    return out

@app.post('/api/refresh')
async def refresh():return await refresh_portfolio()

@app.post('/api/research')
async def get_research(value:ResearchRequest):
    try:return await research(value.symbol,value.use_models,value.refresh)
    except ValueError as e:raise HTTPException(422,str(e)) from e

@app.post('/api/documents')
async def upload_document(symbol:str=Query(min_length=1,max_length=40),file:UploadFile=File(...)):
    try:
        ident=resolve_symbol(symbol);raw=await file.read(20*1024*1024+1)
        if len(raw)>20*1024*1024:raise HTTPException(413,'20 MB document limit')
        doc=parse_pdf(raw,'uploaded:'+ident['symbol'],Path(file.filename or 'document.pdf').name,'user_upload')
        # User uploads are unverified provenance, not automatically promoted to primary.
        return {**doc,'provenance':'user_uploaded_unverified'}
    except ValueError as e:raise HTTPException(422,str(e)) from e

@app.get('/api/executive')
async def executive(name:str=Query(min_length=2,max_length=100),company:str=Query(min_length=2,max_length=100)):
    return await executive_background(name,company)

@app.get('/api/telemetry')
def telemetry():return store.telemetry()

@app.get('/api/pins')
def pins():
    with store.connect() as db:return [json.loads(r['value']) for r in db.execute('SELECT value FROM pins ORDER BY created DESC')]

@app.put('/api/pins/{pin_id}')
def pin(pin_id:str,value:Pin):
    if pin_id!=value.id:raise HTTPException(422,'Pin ID mismatch')
    with store.connect() as db:db.execute('INSERT OR REPLACE INTO pins VALUES (?,?,?)',(pin_id,value.model_dump_json(),time.time()))
    return value

@app.delete('/api/pins/{pin_id}')
def unpin(pin_id:str):
    with store.connect() as db:db.execute('DELETE FROM pins WHERE id=?',(pin_id,))
    return {'deleted':pin_id}

@app.get('/api/memo',response_class=PlainTextResponse)
def memo():
    lines=['# FINN — Investment Committee working note','',f'Created: {datetime.now(timezone.utc).isoformat()}','', 'Pinned evidence, not an investment recommendation.','']
    for p in pins():lines.extend([f'## {p["symbol"]}: {p["title"]}',p['note'],p['source_url'],''])
    return '\n'.join(lines)

@app.get('/healthz')
def hosting_health():
    # Hosting readiness only: no credentials, model configuration or database contents.
    return {'status':'ok'}

@app.get('/',response_class=HTMLResponse)
def frontend_home():
    # Lets the same UI discover its backend on any domain without probing static hosts.
    html=(ROOT/'dist/index.html').read_text()
    return html.replace('<head>', '<head><meta name="finn-backend" content="same-origin">', 1)

app.mount('/',StaticFiles(directory=ROOT/'dist',html=True),name='frontend')
