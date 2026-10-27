import io
import json
import time
from pypdf import PdfReader
from backend import store
from backend.services.network import fetch

def parse_pdf(raw, source_url, name='', kind='filing'):
    if not raw.startswith(b'%PDF'):raise ValueError('Source is not a PDF; HTML challenge/login page rejected.')
    sha=store.digest(raw)
    with store.connect() as db:
        old=db.execute('SELECT pages FROM documents WHERE hash=?',(sha,)).fetchone()
    if old:
        pages=json.loads(old['pages']);store.log('pdf_parse',cache_hit=True)
    else:
        reader=PdfReader(io.BytesIO(raw))
        if len(reader.pages)>500:raise ValueError('Document exceeds the 500-page processing limit.')
        pages=[{'page':i+1,'text':p.extract_text() or ''} for i,p in enumerate(reader.pages)]
        with store.connect() as db:db.execute('INSERT OR IGNORE INTO documents VALUES (?,?,?,?)',(sha,source_url,json.dumps(pages),time.time()))
        store.log('pdf_parse')
    return {'id':sha,'url':source_url,'name':name,'kind':kind,'pages':pages,
            'ocr_pages':[p['page'] for p in pages if len(p['text'].strip())<80],
            'status':'ocr_required' if sum(len(p['text'].strip()) for p in pages)<=100 else 'partial_text' if any(len(p['text'].strip())<80 for p in pages) else 'text_ready'}

async def ingest(doc):
    key='doc-url-v1:'+doc['url']
    if value:=store.get(key,86400):return value
    raw,final=await fetch(doc['url'])
    value=parse_pdf(raw,final,doc['name'],doc['kind']);store.put(key,value);return value

def validate_citation(citation, docs):
    doc=next((d for d in docs if d['id']==citation.get('document_id')),None)
    if not doc:return False
    page=next((p for p in doc['pages'] if p['page']==citation.get('page')),None)
    quote=' '.join(citation.get('quote','').split())
    return bool(page and len(quote)>=8 and quote in ' '.join(page['text'].split()))
