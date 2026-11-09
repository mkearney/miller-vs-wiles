"""Step 5: draw 50 random sentences per chief (excluding the chief's own words), mask the chief's name as [CHIEF],
and write validation_key.csv (with answers) and coder_sheet.csv (blind sheet for a human coder)."""
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "press"))
import pandas as pd, re
NAMES={'priebus':('Reince Priebus','Priebus'),'kelly':('John Kelly','Kelly'),'mulvaney':('Mick Mulvaney','Mulvaney'),
       'meadows':('Mark Meadows','Meadows'),'wiles':('Susie Wiles','Wiles'),'miller':('Stephen Miller','Miller')}
S=pd.read_csv('sentences.csv'); S=S[S.speaker!='chief_speaking']
samp=pd.concat([g.sample(min(50,len(g)),random_state=5) for _,g in S.groupby('chief')]).sample(frac=1,random_state=9).reset_index(drop=True)
def mask(chief,s):
    full,sur=NAMES[chief]; first=full.split()[0]
    s=re.sub(rf'\b{first}\s+(F\.\s+)?{sur}\b','[CHIEF]',s)
    s=re.sub(rf'\b(Mr\.|Ms\.|Gen\.|General)\s+{sur}\b','[CHIEF]',s)
    return re.sub(rf'\b{sur}\b','[CHIEF]',s)
samp['masked']=[mask(c,s) for c,s in zip(samp.chief,samp.sent)]; samp['id']=range(len(samp))
samp.to_csv('validation_key.csv',index=False)
samp[['id','masked']].assign(label='').rename(columns={'masked':'sentence'}).to_csv('coder_sheet.csv',index=False)
