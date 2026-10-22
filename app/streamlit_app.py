from __future__ import annotations
import json,sys
from pathlib import Path
import pandas as pd
import streamlit as st
APP_DIR=Path(__file__).resolve().parent; ROOT=APP_DIR.parent
# Resolve data relative to this file so Streamlit Cloud's working directory
# and the configured app entry point cannot change where the assets are read.
PAPER_CANDIDATES=(ROOT/'paper', ROOT.parent/'reasearch_paper')
PAPER=next((path for path in PAPER_CANDIDATES if (path/'heart_cleveland_clean.csv').is_file() and (path/'results.json').is_file()),PAPER_CANDIDATES[0])
if not (PAPER/'heart_cleveland_clean.csv').is_file() or not (PAPER/'results.json').is_file():
    raise FileNotFoundError(f"Required app data is missing. Expected heart_cleveland_clean.csv and results.json under {PAPER}.")
sys.path.insert(0,str(APP_DIR))
from nb_model import MixedNaiveBayes
from trace import render_trace
import viz
st.set_page_config(page_title="CardioRisk | Bayesian Intelligence",page_icon="CR",layout="wide")
st.markdown("""
<style>
:root{--navy:#142a43;--teal:#147d78;--ink:#1c2c3d;--muted:#657487;--line:#dce4e9;--paper:#f5f7f8}
.stApp{background:var(--paper);color:var(--ink)} [data-testid="stHeader"]{background:rgba(245,247,248,.92)}
.block-container{max-width:1220px;padding:1.8rem 2.4rem 3rem} [data-testid="stSidebar"]{background:var(--navy);border-right:1px solid #263e57}
[data-testid="stSidebar"] *{color:#e7eef4} h1,h2,h3{color:var(--navy);letter-spacing:-.025em} h1{font-size:2.05rem!important;font-weight:680!important}
.brand{display:flex;align-items:center;gap:12px;padding:.35rem 0 1.25rem;border-bottom:1px solid #344c63;margin-bottom:1.25rem}
.brand-mark{width:38px;height:38px;display:grid;place-items:center;border:1px solid #4d7382;border-radius:8px;color:#74c7bd;font-weight:750}
.brand-name{font-weight:700;color:#fff}.brand-sub{font-size:.7rem;color:#a9bac9;letter-spacing:.08em}
.eyebrow,.section-label{color:var(--teal);text-transform:uppercase;letter-spacing:.11em;font-size:.7rem;font-weight:750}
.page-intro{color:var(--muted);max-width:760px;margin:.2rem 0 1.4rem;line-height:1.6}
.safety{background:#fff;border:1px solid #e3ded1;border-left:4px solid #aa7a31;border-radius:6px;padding:.8rem 1rem;color:#4c4d4b;font-size:.84rem;margin:.3rem 0 1.4rem}
.result-panel{background:#fff;border:1px solid var(--line);border-top:3px solid var(--teal);border-radius:8px;padding:1rem 1.2rem;height:100%}
div[data-testid="stMetric"]{background:#fff;border:1px solid var(--line);border-radius:8px;padding:.8rem 1rem}
.stFormSubmitButton>button[kind="primary"]{background:var(--teal);border-color:var(--teal);border-radius:6px;font-weight:650;min-height:2.6rem}
[data-testid="stPlotlyChart"],[data-testid="stDataFrame"]{background:#fff;border:1px solid var(--line);border-radius:8px}
div[data-testid="stExpander"]{border:1px solid var(--line);border-radius:8px;background:#fff}
button:focus-visible,input:focus-visible,[tabindex]:focus-visible{outline:3px solid #55aaa0!important;outline-offset:2px!important}
.footer{border-top:1px solid var(--line);margin-top:2.4rem;padding-top:.9rem;color:var(--muted);font-size:.75rem}
@media(max-width:720px){.block-container{padding:1.2rem 1rem 2rem}h1{font-size:1.7rem!important}}
</style>""",unsafe_allow_html=True)
SAFETY="Research demonstration trained on a 1980s, single-site dataset of 303 records. This is not a medical device or diagnostic tool. In the paper's repeated cross-validation, Mixed NB calibration was lower than logistic regression (Brier 0.183 vs 0.168)."
@st.cache_data
def load_data(): return pd.read_csv(PAPER/'heart_cleveland_clean.csv')
@st.cache_data
def load_results(): return json.loads((PAPER/'results.json').read_text())
@st.cache_resource
def load_model(): return MixedNaiveBayes().fit(load_data())
data,results,model=load_data(),load_results(),load_model()
st.sidebar.markdown('<div class="brand"><div class="brand-mark">CR</div><div><div class="brand-name">CardioRisk</div><div class="brand-sub">BAYESIAN INTELLIGENCE</div></div></div>',unsafe_allow_html=True)
st.sidebar.caption("RESEARCH INTERFACE")
page=st.sidebar.radio("Navigate",["Predict","Data & Results","About"],label_visibility="collapsed")
st.sidebar.markdown('<div class="footer" style="border-color:#344c63;color:#adbdca">UCI Cleveland cohort · 303 records<br>Educational research use</div>',unsafe_allow_html=True)
st.markdown(f'<div class="safety"><b>Research use only</b> &nbsp; {SAFETY}</div>',unsafe_allow_html=True)
if page=="Predict":
    st.markdown('<div class="eyebrow">BAYESIAN CLASSIFICATION · INTERACTIVE DEMONSTRATION</div>',unsafe_allow_html=True); st.title("Explore the model")
    st.markdown('<div class="page-intro">Enter a hypothetical record to inspect how the paper’s mixed Gaussian and categorical Naive Bayes model combines feature likelihoods.</div>',unsafe_allow_html=True)
    defaults={"age":55,"trestbps":130,"chol":245,"thalach":150,"cp":3,"exang":0}
    with st.form("predict"):
        st.markdown("**Demographic and exercise response**"); a,b,c=st.columns(3)
        age=a.slider("Age · years",20,100,55); thalach=b.slider("Maximum heart rate · bpm",60,220,150); exang=c.selectbox("Exercise-induced angina",[0,1],format_func=lambda x:"Absent (0)" if x==0 else "Present (1)")
        st.markdown("**Measurements and symptom category**"); d,e,f=st.columns(3)
        trestbps=d.slider("Resting blood pressure · mm Hg",80,220,130); chol=e.slider("Serum cholesterol · mg/dl",100,600,245); cp=f.selectbox("Chest pain type",[1,2,3,4],format_func=lambda x:{1:"1 · Typical angina",2:"2 · Atypical angina",3:"3 · Non-anginal pain",4:"4 · Asymptomatic"}[x],index=2)
        submitted=st.form_submit_button("Calculate model output",type="primary",use_container_width=True)
    values={"age":age,"trestbps":trestbps,"chol":chol,"thalach":thalach,"cp":cp,"exang":exang}
    theta=st.slider("Decision threshold θ",.30,.70,.50,.05,help="Changes the displayed class label. It does not change the fitted probability."); p=model.predict_one(values)
    st.markdown('<div class="section-label">MODEL OUTPUT</div>',unsafe_allow_html=True); left,right=st.columns([1,1.5])
    with left:
        st.markdown('<div class="result-panel"><div class="eyebrow">THRESHOLDED MODEL CLASS</div>',unsafe_allow_html=True); st.subheader("Positive class" if p.probability>=theta else "Control class"); st.markdown(f'<span style="color:#657487">Decision threshold θ = {theta:.2f}</span></div>',unsafe_allow_html=True)
    with right: st.metric("Model posterior · positive class",f"{p.probability:.1%}",help="For this hypothetical record; not a clinically validated risk estimate.")
    st.caption("This output describes the model’s calculation for entered values. It is not a diagnosis or advice."); st.plotly_chart(viz.contributions_bar(p.contributions),use_container_width=True,config={"displayModeBar":False,"responsive":True})
    near=min(results["threshold_sweep"],key=lambda x:abs(float(x)-theta)); st.info(f"Paper sweep nearest θ={near}: recall {results['threshold_sweep'][near]['recall']:.1%}; specificity {results['threshold_sweep'][near]['specificity']:.1%}.")
    with st.expander("Calculation trace and model diagnostics"): render_trace(model,values,theta,PAPER/'heart_cleveland_clean.csv',data.loc[data.target==0])
elif page=="Data & Results":
    st.markdown('<div class="eyebrow">COHORT · DISTRIBUTIONS · EVALUATION</div>',unsafe_allow_html=True); st.title("Data & results"); st.markdown('<div class="page-intro">Interactive summaries from the cleaned Cleveland dataset and saved experimental results. Values reflect the paper’s reported pipeline.</div>',unsafe_allow_html=True)
    st.plotly_chart(viz.class_balance(data),use_container_width=True,config={"displayModeBar":False,"responsive":True}); a,b=st.columns(2); a.plotly_chart(viz.categorical_distribution(data,"cp"),use_container_width=True,config={"displayModeBar":False,"responsive":True}); b.plotly_chart(viz.categorical_distribution(data,"exang"),use_container_width=True,config={"displayModeBar":False,"responsive":True})
    st.plotly_chart(viz.gaussian_histograms(data),use_container_width=True,config={"displayModeBar":False,"responsive":True}); st.plotly_chart(viz.correlation_heatmaps(data),use_container_width=True,config={"displayModeBar":False,"responsive":True}); st.plotly_chart(viz.cv_metrics(results),use_container_width=True,config={"displayModeBar":False,"responsive":True}); st.plotly_chart(viz.threshold_sweep(results),use_container_width=True,config={"displayModeBar":False,"responsive":True})
    st.markdown('<div class="section-label">SOURCE RECORDS</div>',unsafe_allow_html=True); classes=st.multiselect("Recorded target values",sorted(data.target.unique()),default=sorted(data.target.unique())); st.dataframe(data[data.target.isin(classes)],use_container_width=True,hide_index=True)
    st.caption("ROC and reliability curves are retained in the paper figures; results.json contains their summary metrics, not individual out-of-fold probabilities.")
else:
    st.markdown('<div class="eyebrow">RESEARCH CONTEXT</div>',unsafe_allow_html=True); st.title("About this project"); st.markdown("A research companion for an IEEE-style study of mixed Gaussian and categorical Naive Bayes classification. Dataset: [UCI Heart Disease — Cleveland subset](https://doi.org/10.24432/C52P4X).")
    st.subheader("Limitations"); st.write("Historical, single-site data; small sample; Gaussian departures; and conditional dependence mean these outputs must not be used for clinical decisions.")
    st.subheader("AI-assistance disclosure"); st.write("Generative AI tools were used as learning and editorial assistants to explain statistical concepts, revise manuscript wording and organization, review consistency between the report and project code, and suggest citation checks. The reported numerical results were generated by the documented Python pipeline; AI suggestions were not treated as evidence or as a substitute for cited sources. The author is responsible for verifying the data, code, calculations, references, and interpretations, and for understanding and explaining the work.")
st.markdown('<div class="footer">CardioRisk · Bayesian Intelligence &nbsp;|&nbsp; Educational research demonstration · UCI Cleveland cohort</div>',unsafe_allow_html=True)
