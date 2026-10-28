from __future__ import annotations

import functools
import hashlib
import math

import numpy as np
import pandas as pd
from nb_model import CATEGORICAL, NUMERIC
from sklearn.naive_bayes import CategoricalNB, GaussianNB


@functools.lru_cache(maxsize=4)
def _fit_reference(csv_path):
    frame=pd.read_csv(csv_path); y=frame.target.astype(int).to_numpy()
    g=GaussianNB(var_smoothing=0).fit(frame[list(NUMERIC)],y)
    enc=np.column_stack([frame.cp.to_numpy()-1,frame.exang.to_numpy()]).astype(int)
    return g,CategoricalNB(alpha=1.0,min_categories=[4,2]).fit(enc,y)
def sklearn_posterior(csv_path, values):
    g,c=_fit_reference(str(csv_path)); gx=pd.DataFrame([{f:values[f] for f in NUMERIC}]); cx=np.array([[int(values['cp'])-1,int(values['exang'])]])
    joint=g._joint_log_likelihood(gx)+c._joint_log_likelihood(cx)-np.log(g.class_prior_)
    return float(np.exp(joint[0,1]-np.logaddexp(joint[0,0],joint[0,1])))
@functools.lru_cache(maxsize=4)
def csv_sha256(csv_path): return hashlib.sha256(open(csv_path,'rb').read()).hexdigest()
def build_trace(model, values, csv_path):
    v=model.validate_inputs(values); p=model.predict_one(v); g={}; cat={}
    for f in NUMERIC:
        g[f]={}
        for c in (0,1):
            mean,var=model.means[c][f],model.variances[c][f]; z=(v[f]-mean)/math.sqrt(var); den=math.exp(-z*z/2)/math.sqrt(2*math.pi*var)
            g[f][str(c)]={'mean':mean,'variance':var,'z':z,'density':den,'log_density':math.log(den)}
    for f in CATEGORICAL: cat[f]={str(c):{'count':model.cat_counts[c][f][v[f]],'smoothed_probability':math.exp(model.cat_log_probs[c][f][v[f]]),'log_probability':model.cat_log_probs[c][f][v[f]]} for c in (0,1)}
    M=max(p.log_scores.values()); shifted={str(c):math.exp(p.log_scores[c]-M) for c in (0,1)}
    return {'inputs':v,'priors':{str(c):{'count':model.counts[c],'probability':model.counts[c]/model.n_records} for c in (0,1)},'gaussian':g,'categorical':cat,'scores':p.log_scores,'contributions':p.contributions,'log_sum_exp':{'M':M,'shifted_exponentials':shifted,'posterior':p.probability},'runtime':{'fit_seconds':model.fit_seconds,'inference_ms':p.inference_ms,'csv_sha256':csv_sha256(str(csv_path)),'record_count':model.n_records}}
