
import pandas as pd
import numpy as np
from pathlib import Path
from analytics import engineer, early_warning, severity_table, trend_table, backtest_table, sensitivity_table

DATA=Path(__file__).parent/"HHS_Unaccompanied_Alien_Children_Program.csv"
raw=pd.read_csv(DATA).dropna(how="all")
assert raw.shape[1] == 6, "Source schema must contain six columns."
raw.columns=["date","apprehended","cbp_custody","transferred","hhs_care","discharged"]
raw["date"]=pd.to_datetime(raw["date"],errors="coerce")
for c in raw.columns[1:]:
    raw[c]=pd.to_numeric(raw[c].astype(str).str.replace(",","",regex=False),errors="coerce")
raw=raw.dropna(subset=["date"]).sort_values("date")
assert len(raw)==720
assert not raw.date.duplicated().any()
assert not (raw.iloc[:,1:]<0).any().any()
df=engineer(raw)
for col in ["transfer_efficiency","discharge_effectiveness","pipeline_health_score","pressure_7d"]:
    assert col in df.columns
assert df.pipeline_health_score.dropna().between(0,100).all()
w=early_warning(df,20)
assert w["level"] in {"Low","Elevated","High"}
assert 0 <= w["score"] <= 100
assert isinstance(severity_table(df,20),pd.DataFrame)
assert isinstance(trend_table(df),pd.DataFrame)
assert isinstance(backtest_table(df),pd.DataFrame)
assert isinstance(sensitivity_table(df),pd.DataFrame)
print("QUALITY GATE PASSED", len(df))
