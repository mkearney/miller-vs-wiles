"""GDELT DOC API downloader (tone timelines for each chief and for Trump coverage, plus headline lists).
GDELT rate-limits shared addresses heavily; this script retries with back-off and resumes from its cache (gd/)."""
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "press"))
import json, os, time, urllib.parse, urllib.request, datetime as dt, sys
API="https://api.gdeltproject.org/api/v2/doc/doc"
P={ # name, query, start, end
 'priebus':('"Reince Priebus"','2017-01-20','2017-07-31'),
 'kelly':('"John Kelly"','2017-07-31','2019-01-02'),
 'mulvaney':('"Mick Mulvaney"','2019-01-02','2020-03-31'),
 'meadows':('"Mark Meadows"','2020-03-31','2021-01-20'),
 'wiles':('"Susie Wiles"','2025-01-20','2026-11-06'),
 'miller':('"Stephen Miller"','2025-01-20','2026-11-06'),
}
def f(d): return d.replace('-','')+'000000'
jobs=[]
for k,(q,s,e) in P.items():
    for mode in ['timelinetone','timelinevolraw']:
        jobs.append((f'{k}_{mode}', dict(query=q+' sourcelang:english',mode=mode,startdatetime=f(s),enddatetime=f(e),format='json')))
        jobs.append((f'base_{k}_{mode}', dict(query='Trump sourcelang:english',mode=mode,startdatetime=f(s),enddatetime=f(e),format='json')))
for k,(q,s,e) in P.items():
    a=dt.date.fromisoformat(s); end=dt.date.fromisoformat(e)
    while a<end:
        b=min(a+dt.timedelta(days=91),end)
        jobs.append((f'art_{k}_{a}', dict(query=q+' sourcelang:english',mode='artlist',maxrecords=250,sort='hybridrel',
             startdatetime=f(str(a)),enddatetime=f(str(b)),format='json')))
        a=b
print(len(jobs),'jobs',flush=True)
for name,params in jobs:
    p=f'gd/{name}.json'
    if os.path.exists(p): continue
    url=API+'?'+urllib.parse.urlencode(params)
    for attempt in range(10):
        time.sleep(8 if attempt==0 else min(60*2**(attempt-1),300))
        try:
            with urllib.request.urlopen(url,timeout=90) as r: b=r.read()
            if b.strip()[:1] in (b'{',b'['): 
                json.loads(b.decode('utf8','ignore'))  # validate
                open(p,'wb').write(b); print('ok',name,flush=True); break
            if not b.strip():  # empty = no results
                open(p,'wb').write(b'{}'); print('empty',name,flush=True); break
        except Exception as ex: pass
    else: print('FAIL',name,flush=True)
print('DONE',flush=True)
