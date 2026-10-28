import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0,str(Path(__file__).resolve().parent))
from nb_model import MixedNaiveBayes
from paths import DATA_CSV, RESULTS_JSON


@st.cache_data
def load_data(): return pd.read_csv(DATA_CSV)
@st.cache_data
def load_results(): return json.loads(RESULTS_JSON.read_text(encoding='utf-8'))
@st.cache_resource
def load_model(): return MixedNaiveBayes().fit(load_data())
def values():
    d={'age':55,'trestbps':130,'chol':245,'thalach':150,'cp':3,'exang':0}
    for k,v in d.items(): st.session_state.setdefault(k,v)
    return {k:st.session_state[k] for k in d}
def page_intro(eyebrow,title,intro):
    st.markdown(f'<div class="eyebrow">{eyebrow}</div>',unsafe_allow_html=True); st.title(title); st.write(intro)
