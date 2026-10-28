"""Configure a Gemini Free Tier key locally, then make one uncached JSON check.

No key is printed, sent to FINN hosting, or put in shell arguments. Billing tier
must be checked by the owner in AI Studio; an API key cannot prove it is free.
"""
import argparse
import asyncio
import getpass
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import warnings

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

DEFAULTS={
    'FINN_LLM_BASE_URL':'https://generativelanguage.googleapis.com/v1beta/openai',
    'FINN_MODEL_T1':'',
    'FINN_MODEL_T2':'gemini-3.5-flash-lite',
    'FINN_POLL_INTERVAL_SECONDS':'0',
    # Leave pricing unknown: FINN cannot inspect the owner's billing tier.
    'FINN_T1_INPUT_USD_PER_MILLION':'',
    'FINN_T1_OUTPUT_USD_PER_MILLION':'',
    'FINN_T2_INPUT_USD_PER_MILLION':'',
    'FINN_T2_OUTPUT_USD_PER_MILLION':'',
}

def update_env(path,settings):
    """Replace managed settings once; retain unrelated configuration and comments."""
    text=path.read_text(encoding='utf-8-sig') if path.exists() else ''
    lines=[];written=set()
    for line in text.splitlines():
        match=re.match(r'^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=',line)
        key=match.group(1) if match else None
        if key in settings:
            if key not in written:lines.append(key+'='+json.dumps(settings[key]))
            written.add(key)
        else:lines.append(line)
    lines.extend(key+'='+json.dumps(value) for key,value in settings.items() if key not in written)
    temp_name=None
    try:
        with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=path.parent,delete=False) as temp:
            temp_name=temp.name
            temp.write('\n'.join(lines)+'\n')
        os.replace(temp_name,path)
    finally:
        if temp_name and os.path.exists(temp_name):os.unlink(temp_name)

async def check_connection(research=False):
    from typing import Literal
    from pydantic import BaseModel
    from backend.llm_router import run
    class ConnectionCheck(BaseModel):
        answer:Literal['OK']
    if research:
        from backend.schemas import Synthesis
        from backend.services.documents import validate_citation
        text='Example company manufactures electric motors.'
        citation={'document_id':'setup-fixture','page':1,'quote':text}
        expected={'business':[{'claim':text,'citation':citation}],
                  'audit':[],'guidance':[],'bull':[],'bear':[],'governance':[]}
        schema=Synthesis
        prompt='This is a synthetic connection-test fixture, not investment research. Return exactly this JSON: '+json.dumps(expected)
    else:
        schema=ConnectionCheck
        prompt='Return exactly this JSON object: {"answer":"OK"}'
    print('Checking the configured Gemini model with one '+('research-format' if research else 'small')+' JSON request...',flush=True)
    result=await run('research_format_check' if research else 'connection_check',[{'role':'user','content':prompt}],schema,2,use_cache=False)
    if result['status']=='ok':
        if research:
            findings=result['data']['business']
            docs=[{'id':'setup-fixture','pages':[{'page':1,'text':text}]}]
            if not findings or not all(validate_citation(f['citation'],docs) for f in findings):
                print('CHECK FAILED: The research test did not return a valid source citation.')
                return 1
            print('PASS: Research-format JSON and the test citation validated.')
        else:print('PASS: Gemini returned valid JSON. The API connection works.')
        print('Next: restart FINN, select a company, and run Include model synthesis.')
        print('This checks the API connection; full primary-document research still needs testing.')
        return 0
    print('CHECK FAILED:',result.get('error_code',result['status']))
    print(result.get('reason','No usable response was received.'))
    return 1

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true',help='Check the existing Gemini configuration without changing it')
    parser.add_argument('--research-check',action='store_true',help='Check the full research format and a synthetic citation without changing settings')
    args=parser.parse_args()
    path=ROOT/'.env'
    print('FINN - Gemini Free Tier setup')
    print('Get a key at https://aistudio.google.com/apikey')
    print('Use a project marked Free Tier with no linked billing account.')
    print('Do not add a payment method or upgrade. Free access has quotas and eligibility limits.')
    print('FINN cannot verify your billing tier. Keep the key private.')
    if not (args.check or args.research_check):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('error',getpass.GetPassWarning)
                key=getpass.getpass('Paste your Gemini key here, then press Enter (characters are hidden): ').strip()
        except getpass.GetPassWarning:
            print('Hidden input is unavailable. Run setup-free-ai.cmd in a normal terminal.')
            return 1
        if not key or any(c.isspace() or c in '\"\'${}' for c in key):
            print('No valid key entered. Nothing was changed.')
            return 1
        if key.startswith('sk-'):
            print('That looks like an OpenAI key. Use a Gemini key from AI Studio. Nothing was changed.')
            return 1
        update_env(path,{**DEFAULTS,'FINN_LLM_API_KEY':key})
        print('Saved Gemini settings in .env. Bulk AI classification and polling are off.')
    from dotenv import load_dotenv
    load_dotenv(path,override=True)
    if os.getenv('FINN_LLM_BASE_URL','').rstrip('/')!=DEFAULTS['FINN_LLM_BASE_URL']:
        print('The settings do not point to Gemini. Run setup-free-ai.cmd first. No request was sent.')
        return 1
    return asyncio.run(check_connection(research=args.research_check))

if __name__=='__main__':
    try:sys.exit(main())
    except (KeyboardInterrupt,EOFError):
        print('\nSetup cancelled.');sys.exit(1)
    except OSError:
        print('Could not access the local configuration. Check folder permissions.');sys.exit(1)
