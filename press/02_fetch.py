"""Step 2: add "chief-of-staff" slugs, then download article text (cached in txt/, not committed). Vox blocks downloads and is dropped."""
import os; os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "press"), exist_ok=True); os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "press"))
import pandas as pd, re, os, hashlib, json, concurrent.futures as cf, trafilatura
WIN={'priebus':('2017-01-20','2017-07-31'),'kelly':('2017-07-31','2019-01-02'),'mulvaney':('2019-01-02','2020-03-31'),
     'meadows':('2020-03-31','2021-01-20'),'wiles':('2025-01-20','2026-11-06'),'miller':('2025-01-20','2026-11-06')}
import glob
# rebuild URL table from cached sitemaps, add 'chief-of-staff' slugs
U=[]
for p in glob.glob('sm/*'):
    t=open(p).read()
    for loc in re.findall(r'<loc>([^<]*)</loc>',t): U.append(loc.strip())
C=pd.read_csv('candidates.csv')
def udate(u):
    m=re.search(r'/(20\d\d)/(\d{1,2})/(\d{1,2})/',u)
    return f'{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}' if m else None
extra=[]
for u in set(U):
    if 'chief-of-staff' not in u.lower(): continue
    d=udate(u)
    o='cnn' if 'cnn.com' in u else 'nbc' if 'nbcnews' in u else 'vox' if 'vox.com' in u else 'wex'
    for k,(s,e) in WIN.items():
        if d is None or s<=d<=e: extra.append(dict(chief=k,outlet=o,url=u,date=d))
C=pd.concat([C,pd.DataFrame(extra)]).drop_duplicates(['chief','url'])
os.makedirs('txt',exist_ok=True)
def get(u):
    p='txt/'+hashlib.md5(u.encode()).hexdigest()+'.json'
    if os.path.exists(p): return p
    try:
        h=trafilatura.fetch_url(u)
        d=trafilatura.bare_extraction(h,with_metadata=True) if h else None
        d={'title':getattr(d,'title',None) if d is not None and not isinstance(d,dict) else (d or {}).get('title'),
           'date':getattr(d,'date',None) if d is not None and not isinstance(d,dict) else (d or {}).get('date'),
           'text':getattr(d,'text',None) if d is not None and not isinstance(d,dict) else (d or {}).get('text')}
    except Exception as ex: d={'text':None}
    json.dump(d,open(p,'w')); return p
C=C[C.outlet!='vox']; urls=C.url.unique().tolist(); print(len(urls),'articles to fetch',flush=True)
with cf.ThreadPoolExecutor(12) as ex: P=dict(zip(urls,ex.map(get,urls)))
C['path']=C.url.map(P); C.to_csv('candidates_all.csv',index=False)
ok=C.path.map(lambda p:(json.load(open(p)).get('text') or '')!='')
print('fetched with text:',ok.groupby(C.outlet).mean().round(2).to_dict())
