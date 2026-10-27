"""Optional Push-only career research. Never used by Pull synthesis."""
import os
import httpx

async def executive_background(name,company):
    key=os.getenv('BRAVE_SEARCH_API_KEY')
    if not key:return {'status':'unavailable','sources':[],'reason':'Configure BRAVE_SEARCH_API_KEY for cited professional background search.'}
    async with httpx.AsyncClient(timeout=15) as client:
        r=await client.get('https://api.search.brave.com/res/v1/web/search',params={'q':f'"{name}" "{company}" career executive biography','count':4},headers={'X-Subscription-Token':key})
        r.raise_for_status()
    return {'status':'available','sources':[{'title':x['title'],'url':x['url'],'excerpt':x.get('description','')} for x in r.json().get('web',{}).get('results',[])],
            'warning':'Secondary Push-only search; verify identity and employer before relying on a biography.'}
