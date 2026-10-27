import json
from pathlib import Path
rows=[
('HDFCBANK','HDFC Bank','Banking & finance','Large'),('BAJFINANCE','Bajaj Finance','Banking & finance','Large'),('CDSL','Central Depository Services','Banking & finance','Mid'),
('TCS','Tata Consultancy Services','IT & SaaS','Large'),('KPITTECH','KPIT Technologies','IT & SaaS','Mid'),('RATEGAIN','RateGain Travel Technologies','IT & SaaS','Small'),
('LT','Larsen & Toubro','Industrials & defence','Large'),('HAL','Hindustan Aeronautics','Industrials & defence','Large'),('KAYNES','Kaynes Technology India','Industrials & defence','Mid'),
('M&M','Mahindra & Mahindra','Auto & EV','Large'),('SONACOMS','Sona BLW Precision Forgings','Auto & EV','Mid'),
('SUNPHARMA','Sun Pharmaceutical Industries','Pharma & healthcare','Large'),('MAXHEALTH','Max Healthcare Institute','Pharma & healthcare','Large'),
('TRENT','Trent','Consumer & retail','Large'),('TITAN','Titan Company','Consumer & retail','Large'),('RELIANCE','Reliance Industries','Energy','Large'),
('DEEPAKNTR','Deepak Nitrite','Chemicals','Mid'),('DIXON','Dixon Technologies','EMS & manufacturing','Mid'),
('ETERNAL','Eternal (formerly Zomato)','New-age technology','Large'),('INDHOTEL','Indian Hotels Company','Hospitality','Large'),('ABB','ABB India','Capital goods','Large'),('NH','Narayana Hrudayalaya','Healthcare','Mid')]
data=[{'symbol':r[0],'name':r[1],'sector':r[2],'cap_tier':r[3],'group':'portfolio' if i<18 else 'research','yahoo':r[0]+'.NS'} for i,r in enumerate(rows)]
data[-1]['aliases']=['NARAYANA']
Path(__file__).with_name('universe.json').write_text(json.dumps(data,indent=2))
