"""Step 1: list every article in the CNN, NBC News, Vox and Washington Examiner sitemaps for each tenure,
and keep URLs whose slug names a chief. Writes candidates.csv (sitemap cache in sm/, not committed)."""
import os; os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "press"), exist_ok=True); os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "press"))
import re, subprocess, datetime as dt, concurrent.futures as cf, pandas as pd, os, hashlib
WIN={'priebus':('2017-01-20','2017-07-31'),'kelly':('2017-07-31','2019-01-02'),'mulvaney':('2019-01-02','2020-03-31'),
     'meadows':('2020-03-31','2021-01-20'),'wiles':('2025-01-20','2026-11-06'),'miller':('2025-01-20','2026-11-06')}
SLUG={'priebus':r'priebus','kelly':r'kelly','mulvaney':r'mulvaney','meadows':r'meadows','wiles':r'wiles','miller':r'stephen-miller|miller'}
NOT={'kelly':r'kellyanne|megyn|mark-kelly|laura-kelly|r-kelly|clarkson|loeffler|kelly-craft|ayotte|sadler|ripa|ryan-kelly|kelly-osbourne|machine-gun',
     'miller':r'katie-miller|jason-miller|miller-lite|judith-miller|ross-miller|dennis-miller|kathie|zell|miller-time|millers?-crossing|brad-miller',
     'meadows':r'meadowlands|meadows-mall|meadows-park','wiles':r'wilesco','priebus':r'^$','mulvaney':r'^$'}
def months(a,b):
    a=dt.date.fromisoformat(a).replace(day=1); b=dt.date.fromisoformat(b)
    while a<=b:
        yield a.year,a.month
        a=(a.replace(day=28)+dt.timedelta(days=4)).replace(day=1)
def days(a,b):
    a=dt.date.fromisoformat(a); b=dt.date.fromisoformat(b)
    while a<=b: yield a; a+=dt.timedelta(days=1)
spans=[('2017-01-20','2021-01-20'),('2025-01-20','2026-11-06')]
maps=[]
for s,e in spans:
    for y,m in months(s,e):
        maps.append(('cnn',f'https://www.cnn.com/sitemap/article/politics/{y}/{m:02d}.xml'))
        maps.append(('nbc',f'https://www.nbcnews.com/sitemap/nbcnews/sitemap-{y}-{m:02d}-article.xml'))
        maps.append(('vox',f'https://www.vox.com/sitemaps/entries/{y}/{m}'))
    for d in days(s,e):
        maps.append(('wex',f'https://www.washingtonexaminer.com/sitemap.xml?yyyy={d.year}&mm={d.month:02d}&dd={d.day:02d}'))
os.makedirs('sm',exist_ok=True)
def get(job):
    o,u=job; p='sm/'+hashlib.md5(u.encode()).hexdigest()
    if not os.path.exists(p) or os.path.getsize(p)<50:
        r=subprocess.run(['curl','-sSL','-m','60','-A','Mozilla/5.0 (research)',u],capture_output=True,text=True)
        open(p,'w').write(r.stdout)
    t=open(p).read()
    out=[]
    for blk in re.findall(r'<url>(.*?)</url>',t,re.S) or [f'<loc>{x}</loc>' for x in re.findall(r'<loc>([^<]*)</loc>',t)]:
        loc=re.search(r'<loc>([^<]*)</loc>',blk); lm=re.search(r'<(?:lastmod|news:publication_date)>([^<]*)<',blk)
        if loc: out.append((o,loc.group(1).strip(),lm.group(1)[:10] if lm else None,u))
    return out
print(len(maps),'sitemaps',flush=True)
with cf.ThreadPoolExecutor(10) as ex: res=[x for r in ex.map(get,maps) for x in r]
U=pd.DataFrame(res,columns=['outlet','url','lastmod','sitemap']).drop_duplicates('url')
print('urls',U.groupby('outlet').size().to_dict(),flush=True)
# date: from URL if present, else sitemap month/day
def udate(r):
    m=re.search(r'/(20\d\d)/(\d{1,2})/(\d{1,2})/',r.url)
    if m: return f'{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}'
    m=re.search(r'yyyy=(\d+)&mm=(\d+)&dd=(\d+)',r.sitemap)
    if m: return f'{m.group(1)}-{m.group(2)}-{m.group(3)}'
    return r.lastmod
U['date']=U.apply(udate,axis=1)
rows=[]
for k in WIN:
    s,e=WIN[k]
    sub=U[(U.date>=s)&(U.date<=e)]
    slug=sub.url.str.lower()
    hit=sub[slug.str.contains(SLUG[k])&~slug.str.contains(NOT[k])]
    for r in hit.itertuples(): rows.append(dict(chief=k,outlet=r.outlet,url=r.url,date=r.date))
C=pd.DataFrame(rows); C.to_csv('candidates.csv',index=False)
print(C.groupby(['chief','outlet']).size().unstack(fill_value=0))
