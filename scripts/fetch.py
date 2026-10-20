"""Fetch public SEC XBRL company facts through the documented data API."""
import hashlib
import json
import urllib.request
from pathlib import Path
root=Path(__file__).resolve().parents[1];data=root/'data';data.mkdir(exist_ok=True)
url='https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json'
raw=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'IndependentEngineeringPortfolio public research'}),timeout=60).read()
company=json.loads(raw);facts=[]
for concept,definition in sorted(company['facts']['us-gaap'].items()):
    for unit,records in definition['units'].items():
        candidates=[r for r in records if r.get('form')=='10-K' and r.get('filed')=='2024-11-01']
        if candidates:
            row=candidates[-1];facts.append({'concept':'us-gaap:'+concept,'context':row.get('end','')+'-'+unit,'text':str(row['val']),'scale':'0','unit':unit,'accession':row['accn'],'filed':row['filed']})
assert len(facts)>=50
(data/'facts.json').write_text(json.dumps(facts,indent=2))
(data/'source.json').write_text(json.dumps({'url':url,'sha256':hashlib.sha256(raw).hexdigest(),'note':'SEC companyfacts; filtered to public 10-K facts filed 2024-11-01. Values are as reported in the API.'},indent=2))
assets=company['facts']['us-gaap']['Assets']['units']['USD']
(data/'filing-history.json').write_text(json.dumps([r for r in assets if r.get('form') in ['10-K','10-Q']],indent=2))
print(f'Extracted {len(facts)} public SEC facts')
