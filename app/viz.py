"""Plotly charts built from the cleaned CSV and results JSON."""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from nb_model import NUMERIC
COLORS={0:"#5b6f5b",1:"#b35f4b"}; LABELS={0:"Recorded control",1:"Recorded CAD-positive"}
def _data(data):
    d=data.copy(); d["class"]=(d.target>0).astype(int); d["class_label"]=d["class"].map(LABELS); return d
def class_balance(data):
    d=_data(data).groupby("class_label").size().reset_index(name="records")
    return px.bar(d,x="class_label",y="records",color="class_label",title="Class balance")
def categorical_distribution(data,feature):
    return px.histogram(_data(data),x=feature,color="class_label",barmode="group",histnorm="percent",title=f"{feature} distribution by recorded class")
def gaussian_histograms(data, marker=None):
    d=_data(data); fig=make_subplots(rows=2,cols=2,subplot_titles=list(NUMERIC))
    for i,f in enumerate(NUMERIC):
        r,c=divmod(i,2); r+=1;c+=1
        for k in (0,1):
            v=d.loc[d["class"]==k,f].to_numpy(); fig.add_trace(go.Histogram(x=v,histnorm="probability density",opacity=.35,name=LABELS[k],legendgroup=str(k),showlegend=i==0,marker_color=COLORS[k]),row=r,col=c)
            xs=np.linspace(v.min(),v.max(),150); sd=v.std(ddof=0); den=np.exp(-.5*((xs-v.mean())/sd)**2)/(sd*np.sqrt(2*np.pi)); fig.add_trace(go.Scatter(x=xs,y=den,mode="lines",line=dict(color=COLORS[k]),showlegend=False),row=r,col=c)
        if marker and f in marker: fig.add_vline(x=float(marker[f]),line_dash="dot",row=r,col=c)
    return fig.update_layout(barmode="overlay",height=620,title="Numeric distributions and fitted Gaussian densities")
def correlation_heatmaps(data):
    d=_data(data); fig=make_subplots(rows=1,cols=2,subplot_titles=[LABELS[0],LABELS[1]])
    for col,k in enumerate((0,1),1):
        corr=d.loc[d["class"]==k,list(NUMERIC)].corr(); fig.add_trace(go.Heatmap(z=corr.values,x=NUMERIC,y=NUMERIC,zmin=-1,zmax=1,colorscale="RdBu"),row=1,col=col)
    return fig.update_layout(height=430,title="Within-class correlations")
def cv_metrics(results):
    rows=[]
    for model,metrics in results["cv"].items():
        for m in ("acc","prec","rec","spec","f1","auc"): rows.append({"model":model,"metric":m.upper(),"value":metrics[m][0],"sd":metrics[m][1]})
    return px.bar(pd.DataFrame(rows),x="metric",y="value",color="model",barmode="group",error_y="sd",title="Repeated CV metrics (mean ± SD)")
def threshold_sweep(results):
    rows=[{"threshold":float(t),"metric":m,"value":v} for t,x in results["threshold_sweep"].items() for m,v in x.items()]
    return px.line(pd.DataFrame(rows),x="threshold",y="value",color="metric",markers=True,title="Mixed NB threshold sweep")
def contributions_bar(contributions):
    d=pd.DataFrame({"feature":list(contributions),"log-odds contribution":list(contributions.values())})
    return px.bar(d,x="log-odds contribution",y="feature",orientation="h",color="log-odds contribution",color_continuous_scale="RdYlGn",title="Per-feature log-odds contributions")
