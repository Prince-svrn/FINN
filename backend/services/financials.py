"""Conservative extractor for labelled investor-presentation financial grids.

Unknown layouts remain unavailable. Values are not inferred from Screener and
operating profit is never silently renamed EBITDA.
"""
import re
from backend.domain import pct,bps

METRICS={'revenue':r'Revenue from Operations','ebitda':r'EBITDA','pbt':r'PBT','pat':r'PAT'}

def extract_presentation(doc):
    for page in doc['pages']:
        text=page['text']
        if not all(re.search(r'^'+label+r'\s',text,re.M|re.I) for label in METRICS.values()):continue
        unit=re.search(r'INR\s*MN|INR\s*MILLION|₹\s*(?:MN|MILLION)|Rs\.?\s*(?:in\s*)?Crores|₹\s*(?:in\s*)?Crores',text,re.I)
        if not unit:continue
        periods=re.findall(r'Q[1-4]\s*FY\s*\d{2,4}',text[:text.lower().find('revenue from operations')],re.I)
        periods=list(dict.fromkeys(re.sub(r'\s','',p.upper()) for p in periods))
        if len(periods)<3:continue
        indices=[int(p.split('FY')[1][-2:])*4+int(p[1]) for p in periods[:3]]
        if indices[0]-indices[1]!=1 or indices[0]-indices[2]!=4:continue
        rows=[]
        for key,label in METRICS.items():
            line=re.search(r'^'+label+r'(?:[ \t]*\([A-Z]\)(?:-\([A-Z]\))?)?[ \t]*([\s\S]*?)(?=\n[ \t]*[A-Za-z]|\Z)',text,re.M|re.I)
            if not line:break
            tokens=re.findall(r'(\(?-?\d[\d,]*\.?\d*\)?)[ \t]*(%)?',line[1])
            values=[value for value,percent in tokens if not percent]
            if len(values)<3:break
            vals=[float(v.replace(',','').replace('(','-').replace(')','')) for v in values[:3]]
            if 'crore' not in unit[0].lower():vals=[v/10 for v in vals]
            rows.append({'key':key,'label':{'revenue':'Revenue','ebitda':'Reported EBITDA','pbt':'PBT','pat':'PAT'}[key],
                         'values':vals,'qoq':pct(vals[0],vals[1]),'yoy':pct(vals[0],vals[2]),'unit':'₹ Cr'})
        if len(rows)!=4:continue
        revenue=rows[0]['values'];ebitda=rows[1]['values']
        margin=[e/r*100 if r>0 else None for e,r in zip(ebitda,revenue)]
        rows.insert(2,{'key':'margin','label':'EBITDA margin','values':margin,'qoq':bps(margin[0],margin[1]),'yoy':bps(margin[0],margin[2]),'unit':'%'})
        return {'periods':periods[:3],'rows':rows,'basis':('consolidated' if 'consolidated' in text.lower() else 'basis as presented; verify source')+'; company-reported EBITDA',
                'source':{'url':doc['url'],'page':page['page'],'name':doc['name'],'document_id':doc['id']},
                'method':'Labelled primary grid; INR million converted to ₹ crore; arithmetic computed in Python.'}
    return None
