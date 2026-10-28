"""Opt-in OpenAI-compatible model calls with schema validation and auditable spend.

No API key = unavailable, never synthetic model output. Cache includes model,
schema, prompt and all source text, so a changed disclosure invalidates inference.
"""
import json
import os
import time
import httpx
from urllib.parse import urlsplit
from pydantic import ValidationError
from backend import store

PROMPT_VERSION='finn-2026-10-28-v2'

def provider_error(response):
    """Return fixed, safe explanations; never expose response bodies or credentials."""
    try:
        error=response.json().get('error',{})
        if not isinstance(error,dict):error={}
    except (ValueError,AttributeError):error={}
    codes={str(error.get(k,'')).lower() for k in ('code','type','status')}
    status=response.status_code
    if codes & {'insufficient_quota','credit_balance_exhausted','billing_hard_limit_reached'}:
        return 'quota_exhausted','The provider has no available API credits or quota. For the zero-cost setup, use setup-free-ai.cmd with a Gemini Free Tier project; do not buy credits.'
    if status==429:
        return 'rate_limited','The provider limit was reached. Check your project quota in AI Studio and retry after it resets. Do not enable billing for the zero-cost setup.'
    if status in (401,403):
        return 'access_denied','The API key or project does not have access. Check the key, model access and Free Tier eligibility in AI Studio. Do not upgrade to a paid plan for this setup.'
    if status==404:
        return 'model_unavailable','The model or API address is unavailable. Check FINN_MODEL_T2 and FINN_LLM_BASE_URL against the provider model list.'
    if status==400:
        return 'invalid_request','The provider rejected the request. Check the model settings and supported request format; the source documents are still available.'
    if status>=500:
        return 'provider_unavailable','The AI provider is temporarily unavailable. Try again later.'
    return 'provider_error','The provider rejected the AI request. Check the model and project settings.'

async def run(task, messages, schema, tier=1, *, use_cache=True):
    model=os.getenv('FINN_MODEL_T1' if tier==1 else 'FINN_MODEL_T2','')
    key=os.getenv('FINN_LLM_API_KEY','')
    if not key or not model:return {'status':'unavailable','reason':'Model credentials are not configured.'}
    base_url=os.getenv('FINN_LLM_BASE_URL','https://api.openai.com/v1').rstrip('/')
    body={'model':model,'messages':messages,'temperature':0,
          'response_format':{'type':'json_object'},'max_tokens':5000}
    if urlsplit(base_url).hostname=='generativelanguage.googleapis.com':
        # Gemini's compatible endpoint supports JSON schemas and thinking controls.
        # Leave sampling at its provider default; reserve room for thinking + JSON.
        body.pop('temperature')
        body.update(max_tokens=8192,reasoning_effort='low',response_format={
            'type':'json_schema','json_schema':{'name':schema.__name__,'schema':schema.model_json_schema()}})
    cache_key='llm:'+store.digest(json.dumps([PROMPT_VERSION,base_url,body,schema.model_json_schema()],sort_keys=True).encode())
    if use_cache and (cached:=store.get(cache_key)) is not None:
        store.log(task,tier,model,cache_hit=True);return {'status':'ok','data':cached,'cache_hit':True}
    start=time.perf_counter();usage={};parsed=None;reason=''
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            r=await client.post(base_url+'/chat/completions',
                                headers={'Authorization':'Bearer '+key},json=body)
            r.raise_for_status();response=r.json();usage=response.get('usage',{})
        choice=response['choices'][0]
        if choice.get('finish_reason')=='length':
            status='output_truncated';reason='The model reached its output limit. No incomplete analysis was accepted. Try a smaller research request.'
        elif choice.get('finish_reason')=='content_filter' or choice['message'].get('refusal'):
            status='model_refused';reason='The model declined this request. No model analysis was generated.'
        else:
            parsed=schema.model_validate_json(choice['message']['content']).model_dump()
            if use_cache:store.put(cache_key,parsed)
            status='ok'
    except httpx.HTTPStatusError as e:
        status,reason=provider_error(e.response)
    except httpx.TimeoutException:
        status='timeout';reason='The AI request timed out. The downloaded evidence is still available; try again later.'
    except httpx.RequestError:
        status='connection_error';reason='FINN could not reach the AI provider. Check your internet connection and API address.'
    except (ValidationError,ValueError,KeyError,IndexError,TypeError):
        status='invalid_response';reason='The model returned an incomplete or invalid research structure. FINN rejected it instead of displaying unsupported output.'
    except Exception:
        status='internal_error';reason='FINN could not complete the model request. No model analysis was accepted.'
    # Prices are supplied by operator for the selected model, never a fake cost.
    inp=usage.get('prompt_tokens',0);out=usage.get('completion_tokens',0)
    in_price=os.getenv(f'FINN_T{tier}_INPUT_USD_PER_MILLION');out_price=os.getenv(f'FINN_T{tier}_OUTPUT_USD_PER_MILLION')
    try:cost=(inp*float(in_price)+out*float(out_price))/1e6 if in_price and out_price else None
    except ValueError:cost=None
    store.log(task,tier,model,inp,out,cost,(time.perf_counter()-start)*1000,False,status)
    return {'status':'ok','data':parsed,'cache_hit':False} if status=='ok' else {'status':'error','error_code':status,'reason':reason}
