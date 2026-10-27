from pathlib import Path
import shutil
r=Path(__file__).resolve().parents[1]
for p in (r/"frontend").iterdir():
    if p.is_file():shutil.copy2(p,r/"dist"/p.name)
print("Frontend synchronized to dist")
