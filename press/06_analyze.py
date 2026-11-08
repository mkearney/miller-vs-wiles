"""Step 6: validate the model against hand labels, then estimate net favorability per chief
(each chief-month weighted equally, adjusted for outlet, 95% ranges from resampling whole months) plus robustness splits."""
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "press"))
import pandas as pd, numpy as np, warnings; warnings.filterwarnings('ignore')
L=pd.read_csv('validation_labels_claude.csv').set_index('id').label.to_dict()
ORDER=['wiles','kelly','priebus','meadows','mulvaney','miller']
START={'priebus':'2017-01-20','kelly':'2017-07-31','mulvaney':'2019-01-02','meadows':'2020-03-31','wiles':'2025-01-20','miller':'2025-01-20'}
END={'priebus':'2017-07-31','kelly':'2019-01-02','mulvaney':'2020-03-31','meadows':'2021-01-20','wiles':'2026-11-06','miller':'2026-11-06'}
S=pd.read_csv('sentences_scored.csv'); S=S[S.speaker!='chief_speaking'].copy()
S['net']=S.fav-S.unf
S['label']=np.select([S.fav>=np.maximum(S.unf,S.neu),S.unf>=np.maximum(S.fav,S.neu)],[1,-1],0)

# ---------- 1. validation against my blind labels ----------
V=pd.read_csv('validation_key.csv'); V['mine']=V.id.map(L)
V=V.merge(S[['chief','sent','label','net']],on=['chief','sent'],how='left')
def kappa(a,b):
    a,b=np.asarray(a),np.asarray(b); po=(a==b).mean(); cats=np.union1d(a,b)
    pe=sum((a==c).mean()*(b==c).mean() for c in cats); return (po-pe)/(1-pe)
print('VALIDATION (n=%d)'%V.label.notna().sum())
print(' agreement %.0f%%  kappa %.2f  corr(model net, my label) %.2f'%(100*(V.label==V.mine).mean(),kappa(V.label,V.mine),V[['net','mine']].corr().iloc[0,1]))
print(' direction errors (model fav vs my unfav or reverse): %d'%((V.label*V.mine)==-1).sum())
print(V.groupby('chief').apply(lambda g: pd.Series({'agree%':100*(g.label==g.mine).mean(),'model_mean':g.label.mean(),'my_mean':g.mine.mean()})).round(2).loc[ORDER])

# ---------- 2. main estimate ----------
rng=np.random.default_rng(1)
def fit(A,chiefs,outlets):
    X=np.column_stack([(A.chief==k).astype(float) for k in chiefs]+[(A.outlet==o).astype(float) for o in outlets[1:]])
    w=np.sqrt(A.w.to_numpy()); b=np.linalg.lstsq(X*w[:,None],A.net.to_numpy()*w,rcond=None)[0]
    mix=np.array([(A.outlet==o).mean() for o in outlets[1:]])
    return b[:len(chiefs)]+ (b[len(chiefs):]*mix).sum()      # chief mean at the average outlet mix
def estimate(D,label,B=1000):
    A=D.groupby(['chief','outlet','url','date']).net.mean().reset_index()
    A['month']=A.chief+'|'+A.date.str[:7]
    A['w']=1/A.groupby('month').url.transform('size')     # every chief-month counts equally
    chiefs=[k for k in ORDER if k in set(A.chief)]; outlets=sorted(A.outlet.unique())
    est=fit(A,chiefs,outlets)
    months={k:A[A.chief==k].month.unique() for k in chiefs}; groups=dict(tuple(A.groupby('month')))
    bs=[]
    for _ in range(B):   # resample whole chief-months within each chief
        parts=[groups[m] for k in chiefs for m in rng.choice(months[k],len(months[k]))]
        Ab=pd.concat(parts); bs.append(fit(Ab,chiefs,outlets))
    bs=np.array(bs); lo,hi=np.percentile(bs,[2.5,97.5],axis=0)
    return pd.DataFrame(dict(spec=label,chief=chiefs,net=est,lo=lo,hi=hi,articles=[(A.chief==k).sum() for k in chiefs]))
R=[estimate(S,'main: all non-self sentences'),
   estimate(S[S.speaker=='reporter'],'reporter voice only'),
   estimate(S[~S.opinion],'news only (no opinion)'),
   estimate(S[S.outlet.isin(['cnn','nbc'])],'CNN + NBC only'),
   estimate(S[S.outlet=='wex'],'Washington Examiner only')]
# early vs late (first/last 90 days of tenure)
S['d']=pd.to_datetime(S.date)
S['phase']=np.where(S.d<pd.to_datetime(S.chief.map(START))+pd.Timedelta(days=90),'first 90 days',
           np.where(S.d>pd.to_datetime(S.chief.map(END))-pd.Timedelta(days=90),'last 90 days','middle'))
R+= [estimate(S[S.phase=='first 90 days'],'first 90 days'), estimate(S[S.phase=='last 90 days'],'last 90 days')]
R=pd.concat(R); R.to_csv('final_results.csv',index=False)
print(R.pivot(index='chief',columns='spec',values='net').loc[ORDER].round(2).to_string())
print(R[R.spec.str.startswith('main')].round(2).to_string(index=False))
# hand-coded-only estimate (fully human)
print('HAND-CODED ONLY (mean of my labels, 50/chief):'); print(V.groupby('chief').mine.agg(['mean','count']).round(2).loc[ORDER])
