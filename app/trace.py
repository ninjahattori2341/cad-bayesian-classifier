"""Streamlit renderer for the calculation trace."""
import json

import pandas as pd
import streamlit as st
from trace_core import build_trace, sklearn_posterior


def render_trace(model, values, theta, csv_path, controls=None):
    t=build_trace(model,values,str(csv_path))
    posterior=t['log_sum_exp']['posterior']
    log_odds=t['scores'][1]-t['scores'][0]
    prior_log_odds=model.log_prior[1]-model.log_prior[0]
    feature_log_odds=sum(t['contributions'].values())
    st.markdown('#### Model output, decoded')
    st.caption('These are model probabilities for the recorded classes in the historical dataset—not measurements of a person’s health.')
    summary=pd.DataFrame([
        {'Quantity':'Posterior probability · recorded CAD-positive class','Value':f'{posterior:.6f} ({posterior:.1%})','Meaning':'Model output after combining the prior and six input fields.'},
        {'Quantity':'Posterior probability · recorded control class','Value':f'{1-posterior:.6f} ({1-posterior:.1%})','Meaning':'The complementary model output for the control class.'},
        {'Quantity':'Prior probability · recorded CAD-positive class','Value':f'{model.counts[1]/model.n_records:.6f} ({model.counts[1]/model.n_records:.1%})','Meaning':f"Before using the inputs: {model.counts[1]} of {model.n_records} records."},
        {'Quantity':'Posterior log-odds · CAD-positive vs control','Value':f'{log_odds:+.6f}','Meaning':'Positive values favour CAD-positive; negative values favour control.'},
        {'Quantity':'Prior log-odds · CAD-positive vs control','Value':f'{prior_log_odds:+.6f}','Meaning':'The class imbalance before seeing the inputs.'},
        {'Quantity':'Feature evidence · summed log-likelihood ratio','Value':f'{feature_log_odds:+.6f}','Meaning':'How the six entered values shift the prior log-odds.'},
    ])
    st.dataframe(summary,use_container_width=True,hide_index=True)
    st.caption(f'Accounting identity: prior log-odds ({prior_log_odds:+.3f}) + feature evidence ({feature_log_odds:+.3f}) = posterior log-odds ({log_odds:+.3f}).')
    st.markdown('#### Inputs and fitted terms')
    st.dataframe(
        pd.DataFrame([t['inputs']]).rename(columns={
            'age': 'Age (years)', 'trestbps': 'Resting BP (mm Hg)',
            'chol': 'Cholesterol (mg/dl)', 'thalach': 'Max heart rate (bpm)',
            'cp': 'Chest pain type', 'exang': 'Exercise-induced pain',
        }),
        use_container_width=True,
        hide_index=True,
    )
    st.markdown(r"\(\log S_c = \log P(C=c) + \sum_j \log P(x_j\mid C=c)\)")
    st.write(f"Priors: {model.counts[0]}/{model.n_records} control records; {model.counts[1]}/{model.n_records} CAD-positive records.")
    st.markdown('**Gaussian likelihood terms**')
    st.dataframe(pd.json_normalize(t['gaussian'],sep='.').T,use_container_width=True)
    st.markdown(r"\(P(x_j=v\mid C=c)=\frac{n_{jcv}+1}{N_c+|\mathcal K_j|}\)")
    st.markdown('**Smoothed categorical likelihood terms**')
    categorical_rows=[]
    for feature, classes in t['categorical'].items():
        for class_id, term in classes.items():
            categorical_rows.append({
                'Feature': feature,
                'Recorded class': 'CAD-positive' if class_id == '1' else 'Control',
                'Observed count': term['count'],
                'Smoothed likelihood': term['smoothed_probability'],
                'Log likelihood': term['log_probability'],
            })
    st.dataframe(pd.DataFrame(categorical_rows), use_container_width=True, hide_index=True)
    st.markdown(r"\(P(C=1\mid x)=\frac{e^{s_1-M}}{e^{s_0-M}+e^{s_1-M}},\quad M=\max(s_0,s_1)\)")
    normalization = t['log_sum_exp']
    st.dataframe(pd.DataFrame([
        {'Quantity': 'Maximum log-score M', 'Value': normalization['M']},
        {'Quantity': 'Shifted exponential · control', 'Value': normalization['shifted_exponentials']['0']},
        {'Quantity': 'Shifted exponential · CAD-positive', 'Value': normalization['shifted_exponentials']['1']},
        {'Quantity': 'Normalised posterior · CAD-positive', 'Value': normalization['posterior']},
    ]), use_container_width=True, hide_index=True)
    check=sklearn_posterior(str(csv_path),values)
    difference=abs(check-t['log_sum_exp']['posterior'])
    status='agrees' if difference < 1e-9 else 'differs — investigate'
    st.success(f"Independent scikit-learn cross-check: {status}. Posterior = {check:.12f}; absolute difference = {difference:.3e}.")
    st.download_button('Download trace as JSON',json.dumps(t,indent=2),'cad_model_trace.json','application/json')
