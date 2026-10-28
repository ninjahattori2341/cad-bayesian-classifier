import streamlit as st
from common import page_intro
from copy_text import APP_TAGLINE, DISCLOSURE, LIMITATIONS

page_intro('RESEARCH CONTEXT','About CardioRisk',APP_TAGLINE+'.'); st.write('The name CardioRisk is historical; the app does not estimate future risk.'); st.markdown('### What this is'); st.write('A transparent mixed Gaussian and categorical Naive Bayes classifier for the UCI Cleveland cohort.'); st.markdown('### Limitations'); st.write(LIMITATIONS); st.markdown('### Responsible use'); st.write('This is an educational research demonstration, not a medical device or diagnostic tool.'); st.markdown('### AI-assistance disclosure'); st.write(DISCLOSURE); st.markdown('### How to cite'); st.code('@misc{cardiorisk, title={CardioRisk}, note={Educational research demonstration}}')
