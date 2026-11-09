"""Step 3: keep articles that name the chief in full and discuss them in 2+ sentences; extract those sentences (max 8 per article) and tag the speaker."""
import os; os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "press"), exist_ok=True); os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "press"))
import pandas as pd, json, re
NAMES={'priebus':('Reince Priebus','Priebus'),'kelly':('John Kelly','Kelly'),'mulvaney':('Mick Mulvaney','Mulvaney'),
       'meadows':('Mark Meadows','Meadows'),'wiles':('Susie Wiles','Wiles'),'miller':('Stephen Miller','Miller')}
ALT={'kelly':r'John (F\. )?Kelly|Gen(\.|eral) Kelly','priebus':r'Reince Priebus','mulvaney':r'Mick Mulvaney','meadows':r'Mark Meadows',
     'wiles':r'Susie Wiles|Susan Wiles','miller':r'Stephen Miller'}
OTHER={'kelly':r'(Megyn|Mark|Laura|Ryan|R\.)\s+Kelly|Kelly(anne| Loeffler| Craft| Ayotte| Sadler| Clarkson)',
       'miller':r'(Katie|Jason|Judith|Ross|Kathie|Dennis|Zell|Brad|Matt|Max|Cassidy|Chris|Mary|Tim|Carol|Greg)\s+Miller',
       'meadows':r'^$','wiles':r'^$','priebus':r'^$','mulvaney':r'^$'}
SPLIT=re.compile(r'(?:(?<=[.!?])|(?<=[.!?]["”]))\s+(?=["“A-Z])')
C=pd.read_csv('candidates_all.csv')
rows=[]; arts=[]
for r in C.itertuples():
    d=json.load(open(r.path)); t=d.get('text') or ''
    full,sur=NAMES[r.chief]
    if not re.search(ALT[r.chief],t): continue
    sents=[s.strip() for s in SPLIT.split(t.replace('\n',' '))]
    hits=[s for s in sents if sur in s and not re.search(OTHER[r.chief],s) and 30<len(s)<600]
    if len(hits)<2: continue                       # must be substantively about the chief, not a passing mention
    title=d.get('title') or ''
    opinion=bool(re.search(r'/opinion|/opinions/|/think/|/op-ed|opinion',r.url+' '+title,re.I))
    arts.append(dict(chief=r.chief,outlet=r.outlet,url=r.url,date=r.date,title=title,opinion=opinion,n=len(hits)))
    for s in hits[:8]:                             # cap so long profiles don't dominate the article mean
        rows.append(dict(chief=r.chief,outlet=r.outlet,url=r.url,date=r.date,opinion=opinion,sent=s))
A=pd.DataFrame(arts).drop_duplicates(['chief','url']); S=pd.DataFrame(rows).drop_duplicates(['chief','sent'])
# speaker tagging
def speaker(row):
    full,sur=NAMES[row.chief]; s=row.sent
    if re.search(rf'({sur}|{full})\s*,?\s*(said|says|told|wrote|added|tweeted|posted|argued|insisted|explained|stated)|(said|says|told|according to)\s+(the\s+)?([\w\s]*chief of staff\s+)?({full}|{sur})\b',s): return 'chief_speaking'
    if re.search(r'["“”]',s): return 'quoted_source'
    return 'reporter'
S['speaker']=S.apply(speaker,axis=1)
A.to_csv('articles.csv',index=False); S.to_csv('sentences.csv',index=False)
print(A.groupby(['chief','outlet']).size().unstack(fill_value=0))
print(S.groupby(['chief','speaker']).size().unstack(fill_value=0))
