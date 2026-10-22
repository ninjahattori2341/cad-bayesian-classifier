"""Step-by-step calculation trace for the educational app."""
import hashlib,json,math,platform
import numpy as np,pandas as pd, sklearn, streamlit as st, plotly.graph_objects as go
from sklearn.naive_bayes import GaussianNB, CategoricalNB
from nb_model import NUMERIC,CATEGORICAL
def build_trace(model,values,csv_path):
    v=model.validate_inputs(values); p=model.predict_one(v); g={}; cat={}
    for f in NUMERIC:
        g[f]={}
        for c in (0,1):
            mean,var=model.means[c][f],model.variances[c][f]; z=(v[f]-mean)/math.sqrt(var); den=math.exp(-z*z/2)/math.sqrt(2*math.pi*var)
            g[f][str(c)]={"mean":mean,"variance":var,"z":z,"density":den,"log_density":math.log(den)}
    for f in CATEGORICAL: cat[f]={str(c):{"count":model.cat_counts[c][f][v[f]],"smoothed_probability":math.exp(model.cat_log_probs[c][f][v[f]]),"log_probability":model.cat_log_probs[c][f][v[f]]} for c in (0,1)}
    M=max(p.log_scores.values()); shifted={str(c):math.exp(p.log_scores[c]-M) for c in (0,1)}
    return {"inputs":v,"priors":{str(c):{"count":model.counts[c],"probability":model.counts[c]/model.n_records} for c in (0,1)},"gaussian":g,"categorical":cat,"scores":p.log_scores,"contributions":p.contributions,"log_sum_exp":{"M":M,"shifted_exponentials":shifted,"posterior":p.probability},"runtime":{"fit_seconds":model.fit_seconds,"inference_ms":p.inference_ms,"csv_sha256":hashlib.sha256(csv_path.read_bytes()).hexdigest(),"record_count":model.n_records,"python":platform.python_version(),"numpy":np.__version__,"pandas":pd.__version__,"scikit_learn":sklearn.__version__,"streamlit":st.__version__}}
def render_trace(model,values,theta,csv_path,controls):
    t=build_trace(model,values,csv_path)
    st.markdown("**Log-score · Equation 4**")
    st.latex(r"\log S(c\mid\mathbf{x})=\log P(C=c)+\sum_j\log P(x_j\mid C=c)")
    st.json(t["inputs"]); st.write("Priors: 164/303 controls; 139/303 CAD-positive records.")
    st.markdown("**Gaussian estimates · Equations 6–8**")
    st.latex(r"\begin{aligned}\hat{\mu}_{jc}&=\frac{1}{N_c}\sum_i x_{ij},\\[4pt]\hat{\sigma}^{2}_{jc}&=\max\!\left(\frac{1}{N_c}\sum_i(x_{ij}-\hat{\mu}_{jc})^2,\,10^{-6}\right)\end{aligned}")
    st.dataframe(pd.json_normalize(t["gaussian"],sep=".").T)
    st.markdown("**Smoothed categorical likelihood · Equation 9**")
    st.latex(r"P(x_j=v\mid C=c)=\frac{N_{jc}(v)+1}{N_c+|\mathcal{K}_j|}")
    st.json(t["categorical"])
    rows=[{"term":"prior","class 0":model.log_prior[0],"class 1":model.log_prior[1],"difference":model.log_prior[1]-model.log_prior[0]}]
    for f,d in t["contributions"].items(): rows.append({"term":f,"class 0":model.feature_log_terms(values,0)[f],"class 1":model.feature_log_terms(values,1)[f],"difference":d})
    st.dataframe(pd.DataFrame(rows)); st.plotly_chart(go.Figure(go.Waterfall(x=[r["term"] for r in rows],y=[r["difference"] for r in rows],measure=["relative"]*len(rows))),use_container_width=True)
    st.markdown("**Posterior normalization · Equation 10**")
    st.latex(r"P(C=1\mid\mathbf{x})=\frac{e^{\log S(1\mid\mathbf{x})-M}}{e^{\log S(0\mid\mathbf{x})-M}+e^{\log S(1\mid\mathbf{x})-M}}")
    st.json(t["log_sum_exp"])
    tau=math.log(theta/(1-theta)); st.markdown("**Decision threshold · Equation 5**")
    st.latex(r"\tau=\log\!\left(\frac{\theta}{1-\theta}\right)")
    st.write(f"Log-odds: {t['scores'][1]-t['scores'][0]:.4f}; threshold τ: {tau:.4f}. This is model arithmetic, not medical reasoning.")
    # Independent library cross-check uses the identical full training records.
    frame=pd.read_csv(csv_path); y=frame.target.astype(int).to_numpy(); g=GaussianNB(var_smoothing=0).fit(frame[list(NUMERIC)],y); enc=np.column_stack([frame.cp.to_numpy()-1,frame.exang.to_numpy()]).astype(int); c=CategoricalNB(alpha=1.0,min_categories=[4,2]).fit(enc,y)
    gx=pd.DataFrame([{f:values[f] for f in NUMERIC}]); cx=np.array([[int(values["cp"])-1,int(values["exang"])]])
    joint=g._joint_log_likelihood(gx)+c._joint_log_likelihood(cx)-np.log(g.class_prior_); check=float(np.exp(joint[0,1]-np.logaddexp(joint[0,0],joint[0,1])))
    st.write(t["runtime"]); st.write(f"Independent sklearn GaussianNB + CategoricalNB posterior: {check:.12f}; absolute difference: {abs(check-t['log_sum_exp']['posterior']):.3e}.")
    st.info(f"Among recorded controls, age and thalach have r = {controls.age.corr(controls.thalach):.3f}. Correlated predictors can make probabilities too extreme."); st.download_button("Download trace as JSON",json.dumps(t,indent=2),"cad_model_trace.json","application/json")
