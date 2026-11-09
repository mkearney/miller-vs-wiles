"""Step 4: zero-shot stance model labels each sentence favorable / unfavorable / neutral toward the named chief."""
import os; os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "press"), exist_ok=True); os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "press"))
import pandas as pd, numpy as np, sys, os, warnings; warnings.filterwarnings('ignore')
from transformers import pipeline
NAMES={'priebus':('Reince Priebus','Priebus'),'kelly':('John Kelly','Kelly'),'mulvaney':('Mick Mulvaney','Mulvaney'),'meadows':('Mark Meadows','Meadows'),'wiles':('Susie Wiles','Wiles'),'miller':('Stephen Miller','Miller')}
inp=sys.argv[1] if len(sys.argv)>1 else 'sentences.csv'; out=inp.replace('.csv','_scored.csv')
S=pd.read_csv(inp)
done=pd.read_csv(out) if os.path.exists(out) else pd.DataFrame(columns=list(S.columns)+['fav','unf','neu'])
key=lambda d: d.chief+'|'+d.sent
todo=S[~key(S).isin(set(key(done)))]
clf=pipeline('zero-shot-classification',model='MoritzLaurer/deberta-v3-base-zeroshot-v2.0',device=-1)
rows=[]
for k,g in todo.groupby('chief'):
    sur=NAMES[k][1]; L=[f'favorable toward {sur}',f'unfavorable toward {sur}',f'neutral about {sur}']
    res=clf(g.sent.tolist(),L,hypothesis_template='This text is {}.',batch_size=16)
    for r,(i,row) in zip(res,g.iterrows()):
        sc=dict(zip(r['labels'],r['scores'])); d=row.to_dict()
        d.update(fav=sc[L[0]],unf=sc[L[1]],neu=sc[L[2]]); rows.append(d)
pd.concat([done,pd.DataFrame(rows)]).to_csv(out,index=False); print('scored',len(rows),'->',out)
