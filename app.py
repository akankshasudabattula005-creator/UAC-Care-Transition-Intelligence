import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from pathlib import Path
from analytics import *

st.set_page_config(page_title="UAC Care Transition Intelligence", page_icon="◈", layout="wide", initial_sidebar_state="expanded")
pio.templates.default = "plotly_white"

NAVY="#102A43"; TEAL="#176B87"; BLUE="#2F80ED"; SLATE="#617386"; GRID="#E7EDF3"; BG="#F4F7FB"
COLORWAY=["#2F80ED","#16A085","#F2994A","#8E67C6","#D95D74","#4D7894"]

st.markdown("""
<style>
:root{--navy:#102A43;--teal:#176B87;--slate:#617386;--border:#DFE7EF;--bg:#F4F7FB}
html,body,[class*="css"]{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
[data-testid="stAppViewContainer"]{background:var(--bg);color:var(--navy)}
[data-testid="stHeader"]{background:rgba(244,247,251,.92)}
[data-testid="stSidebar"]{background:#0B2239;border-right:1px solid #173A56}
[data-testid="stSidebar"]{color:#F5F8FB}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,[data-testid="stSidebar"] p,[data-testid="stSidebar"] label,[data-testid="stSidebar"] span{color:#F5F8FB!important}
[data-testid="stSidebar"] input{color:#102A43!important;-webkit-text-fill-color:#102A43!important;background:#FFFFFF!important}
[data-testid="stSidebar"] [data-baseweb="input"]{background:#FFFFFF!important;border-radius:9px}
[data-testid="stSidebar"] svg{color:#607386!important;fill:#607386!important}
[data-testid="stSidebar"] [data-baseweb="slider"] div{color:#F5F8FB!important}
.block-container{padding-top:1rem;padding-bottom:2.2rem;max-width:1580px}
.hero{background:linear-gradient(120deg,#0B2239 0%,#123F5C 55%,#176B87 100%);padding:22px 28px;border-radius:20px;color:white;margin-bottom:14px;box-shadow:0 12px 34px rgba(11,34,57,.14)}
.hero h1{font-size:2rem;margin:0 0 6px;line-height:1.12;color:#FFFFFF!important;-webkit-text-fill-color:#FFFFFF!important}.hero p{margin:0;color:#DCECF4;font-size:.96rem}.eyebrow{font-size:.74rem;letter-spacing:.13em;text-transform:uppercase;font-weight:800;color:#8EDCF0;margin-bottom:8px}
.card{background:#fff;border:1px solid var(--border);border-radius:16px;padding:15px 17px;box-shadow:0 4px 15px rgba(15,40,65,.045);min-height:118px}.card-title{font-size:.73rem;color:#5F7387;text-transform:uppercase;letter-spacing:.07em;font-weight:800}.card-value{font-size:1.58rem;font-weight:800;color:var(--navy);margin-top:5px}.card-sub{font-size:.78rem;color:#7B8B9B;margin-top:4px;line-height:1.3}
.pipeline{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:18px;margin:12px 0 14px}.pipe-stage{position:relative;background:#fff;border:1px solid #DCE5EE;border-radius:15px;padding:14px 15px;min-width:0;box-shadow:0 4px 13px rgba(15,40,65,.04)}.pipe-stage:not(:last-child):after{content:'→';position:absolute;right:-15px;top:50%;transform:translateY(-50%);color:#4D7894;font-size:1.35rem;font-weight:800;z-index:2}.pipe-num{font-size:.67rem;font-weight:800;letter-spacing:.09em;color:#7B8B9B;margin-bottom:4px}.pipe-stage b{display:block;color:var(--navy);font-size:.96rem;white-space:nowrap}.pipe-stage span{display:block;color:#6B7C8F;font-size:.76rem;margin-top:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.section-title{font-size:1.08rem;font-weight:800;color:var(--navy);margin:7px 0 2px}.section-note{font-size:.84rem;color:#6B7C8F;margin-bottom:10px}.insight{background:#fff;border:1px solid #E4EAF1;border-left:4px solid var(--teal);border-radius:10px;padding:10px 13px;margin:7px 0;color:#263B4D;line-height:1.45}.guard{background:#EEF6F8;border:1px solid #D4E6EB;border-radius:13px;padding:13px 15px;color:#385466;font-size:.86rem;line-height:1.5}.status-low,.status-elevated,.status-high{display:inline-block;padding:4px 10px;border-radius:999px;font-weight:800;font-size:.76rem}.status-low{background:#E8F7F0;color:#18794E}.status-elevated{background:#FFF4D8;color:#8A5A00}.status-high{background:#FDE8E7;color:#B42318}
/* Metric contrast fix */
div[data-testid="stMetric"]{background:#fff!important;border:1px solid #E1E8EF!important;padding:13px 15px!important;border-radius:15px!important;box-shadow:0 4px 13px rgba(15,40,65,.04)!important}div[data-testid="stMetric"] label,div[data-testid="stMetric"] [data-testid="stMetricLabel"],div[data-testid="stMetric"] [data-testid="stMetricLabel"] *{color:#607386!important;opacity:1!important}div[data-testid="stMetric"] [data-testid="stMetricValue"],div[data-testid="stMetric"] [data-testid="stMetricValue"] *{color:#102A43!important;opacity:1!important;font-weight:800!important}
/* Tab contrast fix */
.stTabs [data-baseweb="tab-list"]{gap:3px;background:#E8EEF4;padding:4px;border-radius:12px;overflow-x:auto}.stTabs [data-baseweb="tab"]{height:40px;border-radius:8px;padding:0 12px;background:transparent}.stTabs [data-baseweb="tab"] p{color:#52677A!important;font-weight:700!important;font-size:.82rem!important}.stTabs [aria-selected="true"]{background:#fff!important;box-shadow:0 2px 7px rgba(15,40,65,.08)}.stTabs [aria-selected="true"] p{color:#176B87!important}
/* Main text + widgets */
[data-testid="stAppViewContainer"] h1,[data-testid="stAppViewContainer"] h2,[data-testid="stAppViewContainer"] h3,[data-testid="stAppViewContainer"] h4{color:#102A43}[data-testid="stAppViewContainer"] .hero h1{color:#FFFFFF!important;-webkit-text-fill-color:#FFFFFF!important}.stSelectbox label,.stSlider label,.stDateInput label{font-weight:650}.stDataFrame{border:1px solid #E1E8EF;border-radius:12px;overflow:hidden}.stDownloadButton button{border-radius:10px;font-weight:700}
@media(max-width:1100px){.pipeline{grid-template-columns:repeat(5,180px);overflow-x:auto;padding-bottom:8px}.pipe-stage{min-width:180px}.hero h1{font-size:1.7rem}}
</style>
""", unsafe_allow_html=True)

DATA_FILE=Path(__file__).parent/"HHS_Unaccompanied_Alien_Children_Program.csv"
@st.cache_data
def load_data(path):
    if not Path(path).exists():
        raise FileNotFoundError(f"Required dataset not found: {path}")
    d=pd.read_csv(path).dropna(how="all").copy()
    if d.shape[1] != 6:
        raise ValueError(f"Expected 6 source columns, found {d.shape[1]}.")
    d.columns=["date","apprehended","cbp_custody","transferred","hhs_care","discharged"]
    d["date"]=pd.to_datetime(d["date"],errors="coerce")
    for c in d.columns[1:]:
        d[c]=pd.to_numeric(d[c].astype(str).str.replace(",","",regex=False),errors="coerce")
    d=d.dropna(subset=["date"]).sort_values("date")
    if d.empty:
        raise ValueError("No valid dated observations remain after cleaning.")
    if d["date"].duplicated().any():
        d=d.groupby("date",as_index=False)[["apprehended","cbp_custody","transferred","hhs_care","discharged"]].mean()
    if (d[["apprehended","cbp_custody","transferred","hhs_care","discharged"]] < 0).any().any():
        raise ValueError("Negative source counts were detected; review the input dataset.")
    return engineer(d)

def style_fig(fig,height=350,title=None):
    fig.update_layout(template="plotly_white",height=height,paper_bgcolor="#FFFFFF",plot_bgcolor="#FFFFFF",font=dict(color=NAVY,size=12),colorway=COLORWAY,margin=dict(l=18,r=18,t=48 if title else 22,b=18),legend=dict(title_text="",orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1),hoverlabel=dict(bgcolor="white",font_color=NAVY),title=dict(text=title,font=dict(size=16,color=NAVY)) if title else None)
    fig.update_xaxes(gridcolor=GRID,zeroline=False,title_font=dict(color=SLATE),tickfont=dict(color=SLATE))
    fig.update_yaxes(gridcolor=GRID,zeroline=False,title_font=dict(color=SLATE),tickfont=dict(color=SLATE))
    return fig

def ratio(a,b): return a.sum()/b.sum() if b.sum() else np.nan
def fmt_ratio(x,pct): return "N/A" if pd.isna(x) else (f"{x:.1%}" if pct else f"{x:.3f}")

def dashboard_insights(data, threshold, anomaly_cut):
    ep=episodes(data,threshold=threshold)
    msgs=[]
    if len(ep):
        worst=ep.sort_values(["observations","peak_pressure"],ascending=False).iloc[0]
        msgs.append(f"Sustained HHS inflow pressure appeared in {len(ep)} episode(s); a priority episode ran {worst['start']:%d %b %Y}–{worst['end']:%d %b %Y} across {int(worst['observations'])} reporting observations.")
    else:
        msgs.append("No sustained HHS-pressure episode crossed the selected alert threshold in this date range.")
    msgs.append(f"Anomaly screening at |z| ≥ {anomaly_cut:.2f} flagged {int(data['anomaly_flag'].sum())} reporting observation(s) with unusual transfer or discharge movement.")
    msgs.append(f"Placement change detection identified {int(data['shift_flag'].sum())} observation(s) where recent discharge levels diverged materially from the preceding baseline.")
    msgs.append(f"The project-defined Pipeline Health Score averaged {data.pipeline_health_score.mean():.1f}/100 for the selected period; it is not an official HHS KPI.")
    return msgs

def quality_summary(data):
    source_cols=["apprehended","cbp_custody","transferred","hhs_care","discharged"]
    return {
        "observations": len(data),
        "start": data.date.min(),
        "end": data.date.max(),
        "missing_source_values": int(data[source_cols].isna().sum().sum()),
        "duplicate_dates": int(data.date.duplicated().sum()),
    }

try:
    df=load_data(DATA_FILE)
except Exception as exc:
    st.error(f"Application startup failed during data validation: {exc}")
    st.stop()

with st.sidebar:
    st.markdown("## ◈ UAC Intelligence"); st.caption("Operational analytics console"); st.divider(); st.markdown("### Analysis controls")
    dates=st.date_input("Reporting window",(df.date.min().date(),df.date.max().date()),min_value=df.date.min().date(),max_value=df.date.max().date())
    if isinstance(dates,(tuple,list)) and len(dates)==2: start,end=dates
    else: start=end=dates
    threshold=st.slider("HHS pressure alert threshold",0,150,20,5,help="Project-defined threshold used to screen sustained HHS accumulation.")
    anomaly_cut=st.slider("Anomaly sensitivity |z|",2.0,5.0,3.0,.25)
    show_ratio=st.toggle("Display ratios as percentages",True)
    st.divider(); st.caption("Source: supplied HHS UAC reporting dataset. Analytical scores are project-defined.")

f=df[(df.date.dt.date>=start)&(df.date.dt.date<=end)].copy()
if f.empty: st.warning("No observations are available in the selected reporting window."); st.stop()
f["anomaly_flag"]=(f.discharge_anomaly_z.abs()>=anomaly_cut)|(f.transfer_anomaly_z.abs()>=anomaly_cut)
transfer_eff=ratio(f.transferred,f.cbp_custody); discharge_eff=ratio(f.discharged,f.hhs_care); throughput=ratio(f.discharged,f.apprehended); health=f.pipeline_health_score.mean(); warning=early_warning(f,threshold); sev=severity_table(f,threshold); anomaly_count=int(f.anomaly_flag.sum())

st.markdown(f'''<div class="hero"><div class="eyebrow">Care Transition Efficiency & Placement Outcome Analytics</div><h1>UAC Care Transition Intelligence</h1><p>Executive decision-support for aggregate movement from CBP custody → HHS care → sponsor placement · {start:%b %d, %Y} – {end:%b %d, %Y}</p></div>''',unsafe_allow_html=True)

cols=st.columns(5); cards=[("Transfer flow ratio",fmt_ratio(transfer_eff,show_ratio),"Transfers ÷ CBP custody"),("Discharge flow ratio",fmt_ratio(discharge_eff,show_ratio),"Discharges ÷ HHS care"),("Pipeline throughput",fmt_ratio(throughput,show_ratio),"Discharges ÷ apprehensions"),("Pipeline health",f"{health:.1f}/100","Project-defined composite"),("Early warning",warning["level"],f"Risk score {warning['score']:.1f}/100")]
for col,(t,v,s) in zip(cols,cards):
    with col: st.markdown(f'<div class="card"><div class="card-title">{t}</div><div class="card-value">{v}</div><div class="card-sub">{s}</div></div>',unsafe_allow_html=True)

st.markdown(f'''<div class="pipeline"><div class="pipe-stage"><div class="pipe-num">01 · INTAKE</div><b>CBP intake</b><span>{int(f.apprehended.sum()):,} reported entries</span></div><div class="pipe-stage"><div class="pipe-num">02 · CUSTODY</div><b>CBP custody</b><span>{int(f.cbp_custody.mean()):,} mean active load</span></div><div class="pipe-stage"><div class="pipe-num">03 · TRANSFER</div><b>HHS transfer</b><span>{int(f.transferred.sum()):,} reported transfers</span></div><div class="pipe-stage"><div class="pipe-num">04 · CARE</div><b>HHS care</b><span>{int(f.hhs_care.mean()):,} mean active load</span></div><div class="pipe-stage"><div class="pipe-num">05 · OUTCOME</div><b>Placement / discharge</b><span>{int(f.discharged.sum()):,} reported exits</span></div></div>''',unsafe_allow_html=True)
st.caption("Flow ratios compare aggregate movements with same-period stock/intake measures. They are not conversion probabilities; throughput can exceed 100% because reported discharges may relate to earlier entrants.")

tabs=st.tabs(["Command Center","Pipeline","Bottlenecks","Outcomes","Forecast & Research","Validation","Data & Methods"])
with tabs[0]:
    left,right=st.columns([1.45,1])
    with left:
        st.markdown('<div class="section-title">Operational pulse</div><div class="section-note">Movement across the selected reporting window.</div>',unsafe_allow_html=True)
        movement=f.melt(id_vars="date",value_vars=["apprehended","transferred","discharged"],var_name="Stage",value_name="Children")
        fig=px.line(movement,x="date",y="Children",color="Stage",color_discrete_sequence=COLORWAY); style_fig(fig,330); fig.update_layout(hovermode="x unified"); st.plotly_chart(fig,use_container_width=True,theme=None)
    with right:
        st.markdown('<div class="section-title">Executive intelligence</div><div class="section-note">Automatically generated screening observations.</div>',unsafe_allow_html=True)
        for m in dashboard_insights(f,threshold,anomaly_cut): st.markdown(f'<div class="insight">{m}</div>',unsafe_allow_html=True)
        cls={"Low":"status-low","Elevated":"status-elevated","High":"status-high"}.get(warning["level"],"status-elevated"); st.markdown(f'<p style="color:#52677A">Current screening state: <span class="{cls}">{warning["level"]}</span></p>',unsafe_allow_html=True)
    a,b,c=st.columns(3); a.metric("Sustained pressure episodes",len(sev)); b.metric("Anomalous observations",anomaly_count); c.metric("Placement shift flags",int(f.shift_flag.sum()))
    st.markdown('<div class="section-title">Recommended operational review</div>',unsafe_allow_html=True)
    recs=recommendations(f,threshold)
    if anomaly_cut != 3.0:
        recs=[r for r in recs if "extreme discharge observations" not in r]
        if anomaly_count:
            recs.insert(min(1,len(recs)),f"Review the {anomaly_count} observations flagged at the selected |z| ≥ {anomaly_cut:.2f} sensitivity before using them in planning models.")
    for r in recs: st.markdown(f'<div class="insight">{r}</div>',unsafe_allow_html=True)

with tabs[1]:
    st.markdown('<div class="section-title">Care pipeline movement</div><div class="section-note">Aggregate volume relationships across intake, transfer and placement stages.</div>',unsafe_allow_html=True)
    sankey=go.Figure(go.Sankey(node=dict(label=["Reported apprehensions","Transfers to HHS","HHS discharges"],color=["#DCEBFA","#DDF3EE","#FCEAD8"],line=dict(color="#B8C8D6",width=1)),link=dict(source=[0,1],target=[1,2],value=[f.transferred.sum(),f.discharged.sum()],color=["rgba(47,128,237,.28)","rgba(22,160,133,.28)"])))
    style_fig(sankey,300); st.plotly_chart(sankey,use_container_width=True,theme=None)
    l,r=st.columns(2)
    fig=px.line(f,x="date",y=["cbp_custody","hhs_care"],color_discrete_sequence=COLORWAY); style_fig(fig,320,"Active care-load trend"); l.plotly_chart(fig,use_container_width=True,theme=None)
    fig=px.line(f,x="date",y=["transfer_efficiency","discharge_effectiveness"],color_discrete_sequence=COLORWAY); style_fig(fig,320,"Daily flow-to-stock indicators"); r.plotly_chart(fig,use_container_width=True,theme=None)

with tabs[2]:
    st.markdown('<div class="section-title">Bottleneck detection center</div><div class="section-note">Screens for sustained aggregate HHS pressure and unusual operational observations.</div>',unsafe_allow_html=True)
    f["pressure_alert"]=f.pressure_7d>threshold
    fig=px.bar(f,x="date",y="pressure_7d",color="pressure_alert",color_discrete_map={False:"#AFC6D8",True:"#D95D74"}); fig.add_hline(y=threshold,line_dash="dash",line_color="#B42318",annotation_text="Alert threshold"); style_fig(fig,330,"Rolling HHS pressure signal"); st.plotly_chart(fig,use_container_width=True,theme=None)
    x,y=st.columns(2); x.metric("Episodes detected",len(sev)); y.metric("Current 7-observation pressure",f"{f.pressure_7d.iloc[-1]:+.1f}")
    if len(sev): st.dataframe(sev,use_container_width=True,hide_index=True)
    else: st.success("No sustained-pressure episodes are detected at the selected threshold.")
    af=f[f.anomaly_flag]; fig=px.line(f,x="date",y=["transferred","discharged"],color_discrete_sequence=COLORWAY)
    if len(af): fig.add_scatter(x=af.date,y=af.discharged,mode="markers",name="Screening flag",marker=dict(size=9,symbol="x",color="#B42318"))
    style_fig(fig,330,"Anomaly screening"); st.plotly_chart(fig,use_container_width=True,theme=None)

with tabs[3]:
    st.markdown('<div class="section-title">Placement outcome analytics</div><div class="section-note">Temporal consistency, discharge behavior and possible level shifts.</div>',unsafe_allow_html=True)
    l,r=st.columns(2); grp=f.groupby("is_weekend",as_index=False)[["transferred","discharged"]].mean(); grp["Period"]=grp.is_weekend.map({False:"Weekday",True:"Weekend"})
    fig=px.bar(grp.melt(id_vars="Period",value_vars=["transferred","discharged"]),x="Period",y="value",color="variable",barmode="group",color_discrete_sequence=COLORWAY); style_fig(fig,320,"Weekday vs weekend"); l.plotly_chart(fig,use_container_width=True,theme=None)
    monthly=f.groupby("month",as_index=False).agg(discharged=("discharged","sum"),transferred=("transferred","sum")); fig=px.line(monthly.melt(id_vars="month"),x="month",y="value",color="variable",markers=True,color_discrete_sequence=COLORWAY); style_fig(fig,320,"Monthly movement"); r.plotly_chart(fig,use_container_width=True,theme=None)
    fig=px.line(f,x="date",y=["outcome_stability","placement_shift_z"],color_discrete_sequence=COLORWAY); style_fig(fig,330,"Outcome stability and placement-shift signal"); st.plotly_chart(fig,use_container_width=True,theme=None)
    flags=f[f.shift_flag][["date","discharged","placement_shift_z"]]
    if len(flags): st.dataframe(flags,use_container_width=True,hide_index=True)

with tabs[4]:
    st.markdown('<div class="section-title">Research & early warning</div><div class="section-note">Statistical evidence and transparent baseline projections; not causal or individual-level predictions.</div>',unsafe_allow_html=True)
    w1,w2,w3=st.columns(3); w1.metric("Screening level",warning["level"]); w2.metric("Risk score",f"{warning['score']:.1f}/100"); w3.metric("Risk drivers",len(warning["drivers"]))
    for d in warning["drivers"]: st.markdown(f'<div class="insight">{d}</div>',unsafe_allow_html=True)
    tt=trend_table(f); st.markdown("#### Statistical trend tests"); st.dataframe(tt,use_container_width=True,hide_index=True)
    metric=st.selectbox("Projection metric",["hhs_care","cbp_custody","transferred","discharged"]); horizon=st.slider("Projection horizon",7,30,14); fc=forecast_linear(f,metric,horizon)
    if len(fc):
        hist=f[["date",metric]].tail(90); fig=go.Figure(); fig.add_scatter(x=hist.date,y=hist[metric],name="Observed",line=dict(color=BLUE)); fig.add_scatter(x=fc.date,y=fc.forecast,name="Baseline projection",line=dict(color=TEAL)); fig.add_scatter(x=pd.concat([fc.date,fc.date[::-1]]),y=pd.concat([fc.upper_95,fc.lower_95[::-1]]),fill="toself",fillcolor="rgba(23,107,135,.12)",name="95% prediction interval",line=dict(width=0)); style_fig(fig,350,f"{metric.replace('_',' ').title()} baseline projection"); fig.update_layout(hovermode="x unified"); st.plotly_chart(fig,use_container_width=True,theme=None)

with tabs[5]:
    st.markdown('<div class="section-title">Model validation & sensitivity</div><div class="section-note">Held-out baseline forecast error and alert-threshold robustness.</div>',unsafe_allow_html=True)
    bt=backtest_table(f); st.dataframe(bt,use_container_width=True,hide_index=True); sens=sensitivity_table(f); fig=px.line(sens,x="threshold",y=["episodes","flagged_observations"],markers=True,color_discrete_sequence=COLORWAY); style_fig(fig,330,"Bottleneck threshold sensitivity"); st.plotly_chart(fig,use_container_width=True,theme=None)
    d1,d2=st.columns(2); d1.download_button("Download forecast validation",bt.to_csv(index=False).encode(),"forecast_backtest.csv","text/csv",use_container_width=True); d2.download_button("Download sensitivity results",sens.to_csv(index=False).encode(),"threshold_sensitivity.csv","text/csv",use_container_width=True)

with tabs[6]:
    q=quality_summary(f)
    st.markdown('<div class="section-title">Data quality & methodology</div><div class="section-note">Release-level checks for the selected analytical window.</div>',unsafe_allow_html=True)
    q1,q2,q3,q4=st.columns(4)
    q1.metric("Valid observations",f"{q['observations']:,}")
    q2.metric("Missing source values",f"{q['missing_source_values']:,}")
    q3.metric("Duplicate dates",f"{q['duplicate_dates']:,}")
    q4.metric("Coverage",f"{(q['end']-q['start']).days:,} days")
    st.markdown('<div class="guard"><b>Interpretation guardrails.</b> Transfer Efficiency = transfers ÷ CBP custody; Discharge Effectiveness = discharges ÷ HHS care; Pipeline Throughput = discharges ÷ apprehensions. These are aggregate flow-to-stock indicators, not individual waiting-time or placement-probability estimates. Throughput may exceed 1 because exits can correspond to earlier entrants. Health, anomaly, shift, severity and early-warning measures are transparent project-defined screening tools, not official HHS measures and not causal findings.</div>',unsafe_allow_html=True)
    st.markdown("#### Engineered analytical dataset"); st.dataframe(f,use_container_width=True,hide_index=True); st.download_button("Download engineered analytics CSV",f.to_csv(index=False).encode(),"uac_engineered_analytics.csv","text/csv",use_container_width=True)


st.divider()
with st.expander("About this analytical product"):
    st.markdown("""
**Purpose.** Operational decision-support prototype for aggregate UAC care-transition reporting.

**Data contract.** The application expects six source fields: reporting date, apprehensions, CBP custody, transfers out of CBP custody, HHS care, and HHS discharges. Blank rows are removed; dates and numeric values are validated before analytics run.

**Governance.** Composite health, anomaly, level-shift, severity, and early-warning outputs are project-defined analytical screening measures. They are not official HHS performance measures, do not identify individuals, and should not be interpreted as causal findings.

**Production path.** For organizational deployment, connect the application to an approved governed data source, add authentication/role-based access, monitoring, audit logging, automated data-quality alerts, accessibility review, and organizational security/privacy review.
""")

st.markdown("<div style='height:8px'></div><div style='text-align:center;color:#7B8B9B;font-size:.75rem'>UAC Care Transition Intelligence · Release 1.0.0 · Aggregate analytical decision-support prototype</div>", unsafe_allow_html=True)
