from pathlib import Path
import sys,numpy as np,pandas as pd
from sklearn.naive_bayes import CategoricalNB,GaussianNB
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'app'))
from nb_model import MixedNaiveBayes,NUMERIC
DATA=ROOT.parent/'reasearch_paper'/'heart_cleveland_clean.csv'
def test_counts_and_trace_sum():
    frame=pd.read_csv(DATA); model=MixedNaiveBayes().fit(frame); assert model.counts=={0:164,1:139}; p=model.predict_one(frame.iloc[0].to_dict()); assert abs((model.log_prior[1]-model.log_prior[0]+sum(p.contributions.values()))-(p.log_scores[1]-p.log_scores[0]))<1e-12
def test_ten_posteriors_match_independent_sklearn_check():
    frame=pd.read_csv(DATA); x=frame[list(NUMERIC)+['cp','exang']]; y=frame.target.astype(int).to_numpy(); model=MixedNaiveBayes().fit(frame); g=GaussianNB(var_smoothing=0).fit(x[list(NUMERIC)],y); encoded=np.column_stack([x.cp.to_numpy()-1,x.exang.to_numpy()]).astype(int); c=CategoricalNB(alpha=1.0,min_categories=[4,2]).fit(encoded,y)
    joint=g._joint_log_likelihood(x.loc[:9,list(NUMERIC)])+c._joint_log_likelihood(encoded[:10])-np.log(g.class_prior_); expected=np.exp(joint[:,1]-np.logaddexp(joint[:,0],joint[:,1])); actual=model.predict_proba(x.iloc[:10])[:,1]; assert np.max(np.abs(actual-expected))<1e-6
