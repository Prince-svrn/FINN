"""Create a portable source ZIP with no credentials, caches or full PDF text."""
from pathlib import Path
import sys,zipfile,shutil
r=Path(__file__).resolve().parents[1]
out=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else r/'dist/FINN_Source.zip'
out.parent.mkdir(parents=True,exist_ok=True)
allowed={'backend','frontend','dist','config','scripts','tests','docs'}
root_files={'README.md','START_HERE.txt','requirements.txt','start.sh','start.ps1','start.cmd','setup-free-ai.cmd','Dockerfile','compose.yaml','render.yaml','.env.example','.gitignore','.dockerignore'}
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(r.rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(r)
        if any(x in rel.parts for x in ['__pycache__','.pytest_cache','.git','.venv']):continue
        if p.suffix in ['.zip','.pyc'] or p.name=='qa-mobile.html':continue
        if rel.parts[0] in allowed or str(rel) in root_files or str(rel) in ['data/seed_cache.db','data/companies.json']:
            z.write(p,'FINN/'+str(rel))
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    assert 'FINN/dist/FINN_Demo.html' in z.namelist()
    assert not any('/runtime/' in n or n.endswith('/.env') for n in z.namelist())
print(str(out),out.stat().st_size,'bytes')
