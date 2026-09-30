import numpy as np
import pandas as pd

NUMERIC=['apprehended','cbp_custody','transferred','hhs_care','discharged']

def safe_div(a,b): return np.where(b>0,a/b,np.nan)
def robust_z(s,window=28,min_periods=10):
    med=s.rolling(window,min_periods=min_periods).median(); mad=(s-med).abs().rolling(window,min_periods=min_periods).median()
    return ((s-med)/(1.4826*mad.replace(0,np.nan))).replace([np.inf,-np.inf],np.nan)

def engineer(df):
    x=df.copy().sort_values('date').reset_index(drop=True)
    x['transfer_efficiency']=safe_div(x.transferred,x.cbp_custody); x['discharge_effectiveness']=safe_div(x.discharged,x.hhs_care); x['throughput']=safe_div(x.discharged,x.apprehended)
    x['net_cbp_pressure']=x.apprehended-x.transferred; x['net_hhs_pressure']=x.transferred-x.discharged; x['total_pressure']=x.net_cbp_pressure+x.net_hhs_pressure
    x['pressure_7d']=x.net_hhs_pressure.rolling(7,min_periods=1).mean(); x['cbp_pressure_7d']=x.net_cbp_pressure.rolling(7,min_periods=1).mean()
    x['discharge_ma7']=x.discharged.rolling(7,min_periods=1).mean(); x['transfer_ma7']=x.transferred.rolling(7,min_periods=1).mean()
    mean=x.discharged.rolling(30,min_periods=7).mean(); cv=x.discharged.rolling(30,min_periods=7).std()/mean.replace(0,np.nan); x['outcome_stability']=(1/(1+cv)).clip(0,1)
    x['discharge_anomaly_z']=robust_z(x.discharged); x['transfer_anomaly_z']=robust_z(x.transferred)
    recent=x.discharged.rolling(7,min_periods=5).mean(); baseline=x.discharged.shift(7).rolling(28,min_periods=14).mean(); base_sd=x.discharged.shift(7).rolling(28,min_periods=14).std().replace(0,np.nan); x['placement_shift_z']=(recent-baseline)/base_sd
    te=x.transfer_efficiency.clip(0,1)*100; de=x.discharge_effectiveness.clip(0,1)*100; stability=x.outcome_stability.fillna(x.outcome_stability.median()).clip(0,1)*100
    pressure_penalty=(x.pressure_7d.clip(lower=0)/x.hhs_care.replace(0,np.nan)*1000).clip(0,100).fillna(0); anomaly_penalty=(x.discharge_anomaly_z.abs().sub(2).clip(lower=0)*10).clip(0,30).fillna(0)
    x['pipeline_health_score']=(.30*te+.35*de+.20*stability+15-pressure_penalty-anomaly_penalty).clip(0,100)
    x['anomaly_flag']=(x.discharge_anomaly_z.abs()>=3)|(x.transfer_anomaly_z.abs()>=3); x['shift_flag']=x.placement_shift_z.abs()>=2
    x['weekday']=x.date.dt.day_name(); x['is_weekend']=x.date.dt.dayofweek>=5; x['month']=x.date.dt.to_period('M').astype(str)
    return x

def episodes(df,pressure_col='pressure_7d',threshold=20):
    flag=df[pressure_col]>threshold; groups=(flag!=flag.shift()).cumsum(); out=[]
    for _,g in df[flag].groupby(groups[flag]): out.append({'start':g.date.min(),'end':g.date.max(),'observations':len(g),'peak_pressure':g[pressure_col].max(),'avg_pressure':g[pressure_col].mean()})
    return pd.DataFrame(out)

def trend_test(df,column):
    from scipy.stats import linregress
    z=df[['date',column]].dropna().copy()
    if len(z)<3:return {'n':len(z),'slope_per_30d':np.nan,'p_value':np.nan,'r_squared':np.nan,'ci_low_30d':np.nan,'ci_high_30d':np.nan}
    days=(z.date-z.date.min()).dt.total_seconds()/86400; r=linregress(days,z[column]); ci=1.96*r.stderr if pd.notna(r.stderr) else np.nan
    return {'n':len(z),'slope_per_30d':r.slope*30,'p_value':r.pvalue,'r_squared':r.rvalue**2,'ci_low_30d':(r.slope-ci)*30,'ci_high_30d':(r.slope+ci)*30}

def trend_table(df,columns=None):
    columns=columns or ['cbp_custody','hhs_care','transferred','discharged','transfer_efficiency','discharge_effectiveness','pipeline_health_score']; rows=[]
    for c in columns:
        r=trend_test(df,c); r['metric']=c; r['direction']='Increasing' if r['slope_per_30d']>0 else ('Decreasing' if r['slope_per_30d']<0 else 'Flat'); r['statistically_detectable']=bool(pd.notna(r['p_value']) and r['p_value']<.05); rows.append(r)
    return pd.DataFrame(rows)[['metric','n','direction','slope_per_30d','ci_low_30d','ci_high_30d','p_value','r_squared','statistically_detectable']]

def forecast_linear(df,column,horizon=14,lookback=90):
    from scipy.stats import linregress,t
    z=df[['date',column]].dropna().tail(lookback).copy()
    if len(z)<10:return pd.DataFrame()
    x=np.arange(len(z),dtype=float); y=z[column].to_numpy(float); r=linregress(x,y); fx=np.arange(len(z),len(z)+horizon,dtype=float); pred=r.intercept+r.slope*fx
    resid=y-(r.intercept+r.slope*x); dof=max(len(z)-2,1); s=np.sqrt(np.sum(resid**2)/dof); xbar=x.mean(); sxx=np.sum((x-xbar)**2); crit=t.ppf(.975,dof); se=s*np.sqrt(1+1/len(z)+(fx-xbar)**2/sxx) if sxx>0 else np.repeat(s,horizon)
    step=z.date.diff().dropna().median(); step=step if pd.notna(step) and step>pd.Timedelta(0) else pd.Timedelta(days=1); dates=[z.date.iloc[-1]+step*(i+1) for i in range(horizon)]
    return pd.DataFrame({'date':dates,'forecast':np.maximum(pred,0),'lower_95':np.maximum(pred-crit*se,0),'upper_95':np.maximum(pred+crit*se,0),'metric':column})

def backtest_linear(df,column,horizon=7,lookback=90,min_train=30):
    z=df[['date',column]].dropna().reset_index(drop=True); preds=[]
    if len(z)<min_train+horizon:return {'metric':column,'mae':np.nan,'rmse':np.nan,'mape':np.nan,'coverage_95':np.nan,'n_predictions':0}
    starts=range(max(min_train,len(z)-8*horizon),len(z)-horizon,horizon)
    for cut in starts:
        train=z.iloc[:cut]; actual=z.iloc[cut:cut+horizon]; fc=forecast_linear(train.rename(columns={column:column}),column,horizon=len(actual),lookback=lookback)
        if len(fc)!=len(actual):continue
        for a,p,l,u in zip(actual[column],fc.forecast,fc.lower_95,fc.upper_95): preds.append((float(a),float(p),float(l),float(u)))
    if not preds:return {'metric':column,'mae':np.nan,'rmse':np.nan,'mape':np.nan,'coverage_95':np.nan,'n_predictions':0}
    a=np.array([r[0] for r in preds]); p=np.array([r[1] for r in preds]); lo=np.array([r[2] for r in preds]); hi=np.array([r[3] for r in preds]); nz=a!=0
    return {'metric':column,'mae':np.mean(np.abs(a-p)),'rmse':np.sqrt(np.mean((a-p)**2)),'mape':np.mean(np.abs((a[nz]-p[nz])/a[nz]))*100 if nz.any() else np.nan,'coverage_95':np.mean((a>=lo)&(a<=hi))*100,'n_predictions':len(a)}

def backtest_table(df,columns=None):
    columns=columns or ['hhs_care','cbp_custody','transferred','discharged']; return pd.DataFrame([backtest_linear(df,c) for c in columns])

def severity_table(df,threshold=20):
    ep=episodes(df,threshold=threshold)
    if ep.empty:return ep
    scale=max(float(df.hhs_care.median()),1); ep['severity_score']=(ep.avg_pressure.clip(lower=0)*ep.observations/scale*100).round(1); q1,q2=ep.severity_score.quantile([.5,.8]) if len(ep)>1 else (ep.severity_score.iloc[0],ep.severity_score.iloc[0]); ep['severity']=np.select([ep.severity_score>=q2,ep.severity_score>=q1],['High','Moderate'],default='Low'); return ep.sort_values(['severity_score','peak_pressure'],ascending=False).reset_index(drop=True)

def early_warning(df,threshold=20):
    if df.empty:return {'level':'Unknown','score':np.nan,'drivers':[]}
    tail=df.tail(7); latest=df.iloc[-1]; pressure=max(float(latest.get('pressure_7d',0)),0); momentum=float(tail.net_hhs_pressure.mean()-df.tail(28).net_hhs_pressure.mean()) if len(df)>=28 else 0; anomaly=float(tail.anomaly_flag.mean())
    score=min(100,45*min(pressure/max(threshold,1),2)/2+35*min(max(momentum,0)/max(threshold,1),1)+20*anomaly); level='High' if score>=70 else ('Elevated' if score>=40 else 'Low'); drivers=[]
    if pressure>threshold:drivers.append('7-observation HHS pressure is above the selected threshold')
    if momentum>0:drivers.append('recent HHS pressure exceeds the broader 28-observation baseline')
    if anomaly>0:drivers.append('recent transfer/discharge anomalies are present')
    if not drivers:drivers.append('no selected pressure or anomaly trigger is currently active')
    return {'level':level,'score':score,'drivers':drivers}

def sensitivity_table(df,thresholds=(10,20,30,40,50)):
    rows=[]
    for t in thresholds:
        ep=episodes(df,threshold=t); rows.append({'threshold':t,'episodes':len(ep),'flagged_observations':int((df.pressure_7d>t).sum()),'max_episode_observations':int(ep.observations.max()) if len(ep) else 0})
    return pd.DataFrame(rows)

def recommendations(df,threshold=20):
    w=early_warning(df,threshold); ep=severity_table(df,threshold); rec=[]
    if w['level'] in ('Elevated','High'): rec.append('Prioritize review of recent transfer-versus-discharge imbalance and verify whether staffing, sponsor processing, or reporting disruptions coincide with the flagged period.')
    if len(ep): rec.append('Review the highest-severity sustained-pressure episodes first and compare them with operational calendars before attributing a cause.')
    if df.discharge_anomaly_z.abs().ge(3).any(): rec.append('Audit extreme discharge observations for reporting changes or one-time operational events before using them in planning models.')
    weekend=df.groupby('is_weekend').discharged.mean()
    if len(weekend)==2 and weekend.get(True,np.nan)<weekend.get(False,np.nan)*.8: rec.append('Examine weekend discharge workflow capacity; average weekend discharges are materially below weekday levels in the selected data.')
    rec.append('Use aggregate indicators for system screening only; child-level waiting-time or placement-probability conclusions require individual longitudinal records.')
    return rec

def executive_insights(df,threshold=20):
    if df.empty:return []
    ep=episodes(df,threshold=threshold); msgs=[]
    if len(ep):
        worst=ep.sort_values(['observations','peak_pressure'],ascending=False).iloc[0]; msgs.append(f"Sustained HHS inflow pressure appeared in {len(ep)} episode(s); a priority episode ran {worst['start']:%d %b %Y}–{worst['end']:%d %b %Y} across {int(worst['observations'])} reporting observations.")
    else:msgs.append('No sustained HHS-pressure episode crossed the selected alert threshold in this date range.')
    msgs.append(f"Robust rolling anomaly detection flagged {int(df.anomaly_flag.sum())} reporting observation(s) with unusually large transfer or discharge movement."); msgs.append(f"Placement change detection identified {int(df.shift_flag.sum())} observation(s) where recent discharge levels diverged materially from the preceding baseline."); msgs.append(f"The project-defined Pipeline Health Score averaged {df.pipeline_health_score.mean():.1f}/100 for the selected period; it is not an official HHS KPI.")
    return msgs
