# UAC Care Transition Efficiency & Placement Outcome Analytics

A research-oriented Streamlit analytics application for aggregate HHS UAC pipeline reporting data. It reframes capacity counts into transparent operational flow, pressure, stability, anomaly, bottleneck, trend, early-warning, and validation views.

## Run
```bash
python -m pip install -r requirements.txt
python tests.py
streamlit run app.py
```

## Major capabilities
- Data cleaning and feature engineering
- Transfer Efficiency, Discharge Effectiveness, Throughput, Pressure, Stability and project-defined Pipeline Health
- Sustained bottleneck episodes and severity ranking
- Robust rolling anomaly and placement level-shift screening
- Weekday/weekend and monthly temporal analysis
- OLS trend tests with 95% confidence intervals and p-values
- Auditable short-horizon linear baseline forecasts with 95% prediction intervals
- Rolling-origin forecast backtesting (MAE, RMSE, MAPE, interval coverage)
- Threshold sensitivity analysis
- Rule-based early-warning score and explainable drivers
- Automated executive insights and decision-support recommendations
- CSV exports and methodological guardrails

## Important interpretation limitation
The source is aggregate reporting data, not child-level longitudinal records. Ratios are therefore flow-to-stock indicators and must not be interpreted as individual waiting times, individual placement probabilities, or causal effects. Project-defined scores and alerts are analytical screening tools, not official HHS measures.

## Files
- `app.py` — Streamlit UI
- `analytics.py` — reusable analytical engine
- `tests.py` — smoke/invariant tests
- `HHS_Unaccompanied_Alien_Children_Program.csv` — supplied source data

## Final Executive UI
The final dashboard uses a presentation-ready executive analytics layout with:
- branded command-center header and dark control rail
- KPI cards and visible CBP → HHS → placement pipeline
- Command Center, Pipeline, Bottlenecks, Outcomes, Forecast & Research, Validation, and Data & Methods workspaces
- contextual executive intelligence and recommendation cards
- explicit research interpretation guardrails
- responsive Plotly visualizations and downloadable validation/analytics outputs

The interface intentionally separates operational screening signals from causal or individual-level conclusions.


## Production-readiness note
This repository is a submission-ready analytical prototype with defensive data validation, documented methodology, regression tests, explicit interpretation guardrails, and a professional Streamlit UI. Organizational production deployment still requires environment-specific authentication, governed data integration, security/privacy review, observability, accessibility review, and operational ownership. See `PROJECT_GOVERNANCE.md`.

## Release candidate
Version 1.0.0 is the master submission build. Run both checks before a demo:

```bash
python tests.py
python quality_gate.py
streamlit run app.py
```

The dashboard intentionally uses the terms **Transfer flow ratio** and **Discharge flow ratio** in the executive cards because the aggregate dataset cannot measure child-level transition speed or placement probability.
