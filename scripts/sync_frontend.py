from pathlib import Path
import shutil,re
r=Path(__file__).resolve().parents[1]
for p in (r/"frontend").iterdir():
    if p.is_file():shutil.copy2(p,r/"dist"/p.name)
html=(r/'dist/index.html').read_text()
css=(r/'dist/styles.css').read_text()
js=(r/'dist/app.js').read_text()
snapshot=(r/'dist/data/snapshot.json').read_text().replace('</','<\\/')
html=re.sub(r'<link[^>]+(?:rel="icon"|rel="manifest")[^>]*>','',html)
html=html.replace('<link rel="stylesheet" href="/styles.css">','<style>'+css+'</style>')
js=js[:js.index('async function init()')]+'''async function init(){try{data=JSON.parse(document.getElementById('embedded-snapshot').textContent);backend=false;render()}catch(e){document.getElementById('app').textContent='Could not load the saved demo: '+e.message}}
init();'''
html=html.replace('<script type="module" src="/app.js"></script>',
                  '<script id="embedded-snapshot" type="application/json">'+snapshot+'</script><script>'+js.replace('</script','<\\/script')+'</script>')
(r/'dist/FINN_Demo.html').write_text(html)
print("Frontend and standalone demo synchronized")
