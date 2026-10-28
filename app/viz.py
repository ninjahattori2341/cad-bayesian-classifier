"""Plotly charts built from the cleaned CSV and results JSON."""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from nb_model import NUMERIC
from plotly.subplots import make_subplots

IS_DARK=False
COLORS={0:"#496779",1:"#087f73"}; LABELS={0:"Recorded control",1:"Recorded CAD-positive"}
MODEL_COLORS={"Mixed NB":"#087f73","Gaussian NB (numeric)":"#71818a","Logistic regression":"#253f50","Decision tree (fixed)":"#a97832"}
def set_theme(dark):
    global IS_DARK, COLORS, MODEL_COLORS
    IS_DARK=bool(dark)
    COLORS={0:"#a8bac8",1:"#70d2c0"} if IS_DARK else {0:"#496779",1:"#087f73"}
    MODEL_COLORS={"Mixed NB":"#70d2c0","Gaussian NB (numeric)":"#a9b8c2","Logistic regression":"#8eb5d7","Decision tree (fixed)":"#dfb66f"} if IS_DARK else {"Mixed NB":"#087f73","Gaussian NB (numeric)":"#71818a","Logistic regression":"#253f50","Decision tree (fixed)":"#a97832"}
def _style(fig, height=400):
    dark=IS_DARK; bg="#131d27" if dark else "#ffffff"; ink="#e7edf2" if dark else "#1c2b36"; grid="#354754" if dark else "#e8edef"; navy="#f4f7f9" if dark else "#142a36"; muted="#b0bec8" if dark else "#5f707b"
    fig.update_layout(template="plotly_dark" if dark else "plotly_white",height=height,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor=bg,font=dict(family="DM Sans, sans-serif",color=ink,size=12),title=dict(font=dict(size=16,color=navy),x=0.02,xanchor="left"),legend=dict(orientation="h",yanchor="bottom",y=1.02,x=0),margin=dict(l=24,r=20,t=70,b=35),hoverlabel=dict(bgcolor="#1b2938" if dark else "#142a43",font_color=ink))
    fig.update_xaxes(showgrid=True,gridcolor=grid,zerolinecolor=grid,tickfont_color=muted)
    fig.update_yaxes(showgrid=True,gridcolor=grid,zerolinecolor=grid,tickfont_color=muted)
    return fig
def _data(data):
    d=data.copy(); d["class"]=(d.target>0).astype(int); d["class_label"]=d["class"].map(LABELS); return d
def class_balance(data):
    d=_data(data).groupby("class_label").size().reset_index(name="records")
    fig=px.bar(d,x="class_label",y="records",color="class_label",color_discrete_map={LABELS[k]:v for k,v in COLORS.items()},title="Class balance",text="records"); fig.update_traces(marker_line_width=0); return _style(fig,330)
def categorical_distribution(data,feature):
    fig=px.histogram(_data(data),x=feature,color="class_label",barmode="group",histnorm="percent",color_discrete_map={LABELS[k]:v for k,v in COLORS.items()},title=f"{feature} distribution by recorded class"); return _style(fig,350)
def gaussian_histograms(data, marker=None):
    d=_data(data); fig=make_subplots(rows=2,cols=2,subplot_titles=list(NUMERIC))
    for i,f in enumerate(NUMERIC):
        r,c=divmod(i,2); r+=1;c+=1
        for k in (0,1):
            v=d.loc[d["class"]==k,f].to_numpy(); fig.add_trace(go.Histogram(x=v,histnorm="probability density",opacity=.35,name=LABELS[k],legendgroup=str(k),showlegend=i==0,marker_color=COLORS[k]),row=r,col=c)
            xs=np.linspace(v.min(),v.max(),150); sd=v.std(ddof=0); den=np.exp(-.5*((xs-v.mean())/sd)**2)/(sd*np.sqrt(2*np.pi)); fig.add_trace(go.Scatter(x=xs,y=den,mode="lines",line=dict(color=COLORS[k]),showlegend=False),row=r,col=c)
        if marker and f in marker: fig.add_vline(x=float(marker[f]),line_dash="dot",row=r,col=c)
    fig.update_layout(barmode="overlay",title="Numeric distributions and fitted Gaussian densities"); return _style(fig,620)
def correlation_heatmaps(data):
    d=_data(data); fig=make_subplots(rows=1,cols=2,subplot_titles=[LABELS[0],LABELS[1]])
    for col,k in enumerate((0,1),1):
        corr=d.loc[d["class"]==k,list(NUMERIC)].corr(); scale=[[0,"#bd625b" if IS_DARK else "#b6534b"],[.5,"#263541" if IS_DARK else "#f1f4f4"],[1,"#70d2c0" if IS_DARK else "#087f73"]]; fig.add_trace(go.Heatmap(z=corr.values,x=NUMERIC,y=NUMERIC,zmin=-1,zmax=1,colorscale=scale,colorbar=dict(title="r")),row=1,col=col)
    fig.update_layout(title="Within-class correlations"); return _style(fig,430)
def cv_metrics(results):
    rows=[]
    for model,metrics in results["cv"].items():
        for m in ("acc","prec","rec","spec","f1","auc"): rows.append({"model":model,"metric":m.upper(),"value":metrics[m][0],"sd":metrics[m][1]})
    fig=px.bar(pd.DataFrame(rows),x="metric",y="value",color="model",color_discrete_map=MODEL_COLORS,barmode="group",error_y="sd",title="Repeated CV metrics · mean ± SD"); return _style(fig,430)
def threshold_sweep(results):
    rows=[{"threshold":float(t),"metric":m,"value":v} for t,x in results["threshold_sweep"].items() for m,v in x.items()]
    colors=["#70d2c0","#8eb5d7"] if IS_DARK else ["#087f73","#253f50"]
    fig=px.line(pd.DataFrame(rows),x="threshold",y="value",color="metric",color_discrete_sequence=colors,markers=True,title="Mixed NB threshold sweep"); return _style(fig,360)
def contributions_bar(contributions):
    d=pd.DataFrame({"feature":list(contributions),"log-odds contribution":list(contributions.values())})
    d=d.reindex(d["log-odds contribution"].abs().sort_values().index)
    positive="#70d2c0" if IS_DARK else "#087f73"; negative="#e2b66e" if IS_DARK else "#a97832"
    d["direction_color"]=d["log-odds contribution"].map(lambda value:positive if value>=0 else negative)
    fig=go.Figure(go.Bar(x=d["log-odds contribution"],y=d["feature"],orientation="h",marker_color=d["direction_color"],marker_pattern_shape=["" if v>=0 else "/" for v in d["log-odds contribution"]],text=[f"{v:+.2f}" for v in d["log-odds contribution"]],textposition="outside"))
    fig.update_layout(title="What drove this result?",showlegend=False); fig.update_xaxes(zeroline=True,zerolinewidth=2,title="toward control ← 0 → toward CAD-positive"); return _style(fig,350)
