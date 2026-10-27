"""Opt-in OpenAI-compatible model calls with schema validation and auditable spend.

No API key = unavailable, never synthetic model output. Cache includes model,
schema, prompt and all source text, so a changed disclosure invalidates inference.
"""
import json
import os
import time
import httpx
from backend import store

PROMPT_VERSION='finn-2026-10-27-v1'

async def run(task, messages, schema, tier=1):
    model=os.getenv('FINN_MODEL_T1' if tier==1 else 'FINN_MODEL_T2','')
    key=os.getenv('FINN_LLM_API_KEY','')
    if not key or not model:return {'status':'unavailable','reason':'Model credentials are not configured.'}
    body={'model':model,'messages':messages,'temperature':0,
          'response_format':{'type':'json_object'},'max_tokens':5000}
    cache_key='llm:'+store.digest(json.dumps([PROMPT_VERSION,body,schema.model_json_schema()],sort_keys=True).encode())
    if cached:=store.get(cache_key):
        store.log(task,tier,model,cache_hit=True);return {'status':'ok','data':cached,'cache_hit':True}
    start=time.perf_counter();response=None;usage={}
    try:
        async with httpx.AsyncClient(timeout=90) as client:
            r=await client.post(os.getenv('FINN_LLM_BASE_URL','https://api.openai.com/v1').rstrip('/')+'/chat/completions',
                                headers={'Authorization':'Bearer '+key},json=body)
            r.raise_for_status();response=r.json();usage=response.get('usage',{})
        parsed=schema.model_validate_json(response['choices'][0]['message']['content']).model_dump()
        store.put(cache_key,parsed);status='ok'
    except Exception as e:
        parsed=None;status=type(e).__name__
    # Prices are supplied by operator for the selected model, never a fake cost.
    inp=usage.get('prompt_tokens',0);out=usage.get('completion_tokens',0)
    in_price=os.getenv(f'FINN_T{tier}_INPUT_USD_PER_MILLION');out_price=os.getenv(f'FINN_T{tier}_OUTPUT_USD_PER_MILLION')
    try:cost=(inp*float(in_price)+out*float(out_price))/1e6 if in_price and out_price else None
    except ValueError:cost=None
    store.log(task,tier,model,inp,out,cost,(time.perf_counter()-start)*1000,False,status)
    return {'status':'ok','data':parsed,'cache_hit':False} if parsed is not None else {'status':'error','reason':status}
