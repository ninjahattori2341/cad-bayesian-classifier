import streamlit as st
import viz
from common import load_data, page_intro

data=load_data(); page_intro('COHORT','Data','Explore the cleaned Cleveland cohort used by the model.'); pos=(data.target>0)
a,b,c,d=st.columns(4); a.metric('Records',len(data)); b.metric('CAD-positive share',f'{pos.mean():.1%}'); c.metric('Inputs used',6); d.metric('Missing values',int(data.isna().sum().sum()))
view=st.pills('Explore',['Cohort','Distributions','Correlations','Records'],default='Cohort')
if view=='Cohort': st.plotly_chart(viz.class_balance(data),use_container_width=True)
elif view=='Distributions': st.plotly_chart(viz.gaussian_histograms(data),use_container_width=True)
elif view=='Correlations': st.plotly_chart(viz.correlation_heatmaps(data),use_container_width=True)
else:
    class_filter=st.multiselect('Recorded class',[0,1],default=[0,1]); cp_filter=st.multiselect('Chest pain type',[1,2,3,4],default=[1,2,3,4]); ex_filter=st.multiselect('Exercise-induced pain',[0,1],default=[0,1])
    shown=data[data.target.isin(class_filter)&data.cp.isin(cp_filter)&data.exang.isin(ex_filter)]
    st.caption(f'{len(shown)} of {len(data)} records'); st.dataframe(shown,use_container_width=True,hide_index=True); st.download_button('Download filtered records as CSV',shown.to_csv(index=False),'cardiorisk_records.csv','text/csv')
