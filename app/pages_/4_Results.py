import pandas as pd
import streamlit as st
import viz
from common import load_results, page_intro

r=load_results(); page_intro('EVALUATION','Results','Saved cross-validation and threshold results from the paper.'); st.plotly_chart(viz.cv_metrics(r),use_container_width=True); st.dataframe(pd.DataFrame({m:{k:round(v[m][0],3) for k,v in r['cv'].items()} for m in ('auc','brier')}).T,use_container_width=True)
st.markdown('### Discrimination vs calibration'); st.info('AUC 0.831 vs 0.830 (similar), but Brier 0.183 vs 0.168; logistic regression was better calibrated in this evaluation.'); st.plotly_chart(viz.threshold_sweep(r),use_container_width=True)
with st.expander('Holdout metrics and confidence intervals'): st.dataframe(pd.DataFrame(r['holdout']).T); st.caption('Holdout n = 61; intervals are wide.')
