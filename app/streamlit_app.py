import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0,str(Path(__file__).resolve().parent))
from paths import require_inputs

require_inputs()
from common import load_data
from copy_text import APP_NAME, SAFETY_SHORT
from theme import inject_css

st.set_page_config(page_title=APP_NAME,layout='wide')
with st.sidebar:
    st.markdown('<div class="brand-lockup"><div><div class="brand">CardioRisk</div><div class="brand-sub">RESEARCH EXPLORER</div></div></div>',unsafe_allow_html=True)
    st.caption(f"UCI Cleveland cohort · {len(load_data())} records")
    st.markdown('[Read the paper PDF](https://github.com/ninjahattori2341/cad-bayesian-classifier/blob/main/paper/paper.pdf)')
inject_css('light')
st.markdown(f'<div class="safety-banner"><strong>Educational research demonstration</strong><span>{SAFETY_SHORT}</span></div>',unsafe_allow_html=True)
pages=[st.Page('pages_/1_Classify.py',title='Classify',default=True),st.Page('pages_/2_How_it_works.py',title='How it works'),st.Page('pages_/3_Data.py',title='Data'),st.Page('pages_/4_Results.py',title='Results'),st.Page('pages_/5_About.py',title='About')]
st.navigation(pages).run()
st.caption('CardioRisk · Educational research demonstration · MIT License')
