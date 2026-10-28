import streamlit as st
import viz
from common import load_model, page_intro, values
from copy_text import (
    CLASS_CONTROL,
    CLASS_POSITIVE,
    CP_LABELS,
    EXANG_LABELS,
    PAGE_INTRO_PREDICT,
    PAGE_TITLE_PREDICT,
    RESULT_CAPTION,
    RESULT_LABEL,
)
from evidence import evidence_strip

try:
    from nb_model import NUMERIC_BOUNDS
except ImportError:
    # Compatibility with a Streamlit deployment running an older cached module.
    NUMERIC_BOUNDS = {
        'age': (20, 100),
        'trestbps': (80, 220),
        'chol': (100, 600),
        'thalach': (60, 220),
    }
from ui_components import big_number, narrate, prob_track

model=load_model(); page_intro('BAYESIAN CLASSIFICATION',PAGE_TITLE_PREDICT,PAGE_INTRO_PREDICT); v=values()
def preset(x):
    for k,val in x.items(): st.session_state[k]=val
c1,c2,c3=st.columns(3)
c1.button('Typical profile',on_click=preset,args=({'age':45,'trestbps':120,'chol':200,'thalach':170,'cp':3,'exang':0},),use_container_width=True)
c2.button('Profile resembling CAD-positive records',on_click=preset,args=({'age':62,'trestbps':150,'chol':290,'thalach':115,'cp':4,'exang':1},),use_container_width=True)
c3.button('Reset to defaults',on_click=preset,args=({'age':55,'trestbps':130,'chol':245,'thalach':150,'cp':3,'exang':0},),use_container_width=True)
for f,label in [('age','Age (years)'),('trestbps','Resting blood pressure (mm Hg)'),('chol','Cholesterol (mg/dl)'),('thalach','Max heart rate during exercise (bpm)')]:
    lo,hi=NUMERIC_BOUNDS[f]; v[f]=st.slider(label,lo,hi,key=f); st.markdown(evidence_strip(f,v[f],lo,hi,model),unsafe_allow_html=True)
v['cp']=st.pills('Chest pain type',options=list(CP_LABELS),format_func=lambda x:CP_LABELS[x],key='cp') or v['cp']; st.caption('Asymptomatic means no typical chest-pain pattern in this historical cohort; it is not a claim about health.')
v['exang']=st.pills('Exercise-induced chest pain',options=list(EXANG_LABELS),format_func=lambda x:EXANG_LABELS[x],key='exang')
theta=st.slider('Decision threshold',.30,.70,.50,.05,key='theta',help='Changes the class label only, not the probability.')
p=model.predict_one(v); label=CLASS_POSITIVE if p.probability>=theta else CLASS_CONTROL
st.markdown('### Model output')
with st.container(border=True):
    st.caption(RESULT_LABEL); st.markdown(f'<div class="likelihood">{big_number(p.probability)}</div>',unsafe_allow_html=True); st.markdown(prob_track(p.probability,theta),unsafe_allow_html=True)
    st.markdown(f'<div class="class-output" role="status" aria-live="polite">● Model class at threshold {theta:.2f}: <strong>{label}</strong></div>',unsafe_allow_html=True); st.caption(RESULT_CAPTION)
st.subheader('What drove this result?'); st.write(narrate(p.contributions,{'cp':'chest pain type','thalach':'max heart rate','age':'age','trestbps':'resting blood pressure','chol':'cholesterol','exang':'exercise-induced pain'})); st.plotly_chart(viz.contributions_bar(p.contributions),use_container_width=True,config={'displayModeBar':False})
