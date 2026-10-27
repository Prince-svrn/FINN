"""Fetch build inputs. Does not run paid models or overwrite reviewed snapshot.

The reviewed case expects the original document hashes. A changed PDF stops the
capture so its page references must be reviewed before rebuilding.
"""
import asyncio,json,os
from pathlib import Path
os.environ['FINN_LLM_API_KEY']=''
from backend.services.screener_service import fetch_company
from backend.services.filings_service import filings
from backend.services.eod_service import prices
from backend.services.documents import ingest
R=Path(__file__).resolve().parents[1]
async def main():
    universe=json.loads((R/'config/universe.json').read_text());market={};companies={}
    for row in universe:
        symbol=row['symbol'];company=await fetch_company(symbol,True)
        f,p=await asyncio.gather(filings(symbol,True),prices(symbol,True))
        companies[symbol]=company;market[symbol]={'filings':f,'prices':p}
        print(symbol,len(f['items']),len(p['bars']))
    (R/'data/companies.json').write_text(json.dumps(companies))
    (R/'data/market.json').write_text(json.dumps(market))
    manifest=json.loads((R/'config/reviewed_sources.json').read_text())
    for name,refs in manifest.items():
        docs=[]
        for ref in refs:
            d=await ingest(ref)
            if d['id']!=ref['id']:raise RuntimeError('Source changed: review its pages before rebuilding: '+ref['url'])
            docs.append(d)
        (R/'data'/name).write_text(json.dumps(docs if name.endswith('documents.json') else docs[0]))
    print('Captured public inputs. Review source dates before rebuilding the historical snapshot.')
if __name__=='__main__':asyncio.run(main())
