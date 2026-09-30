# Project Governance and Production Readiness

## Scope
This application analyzes aggregate UAC program reporting and provides descriptive, screening, statistical, and baseline forecasting views.

## Analytical boundaries
- No child-level records are present.
- Ratios are aggregate flow-to-stock indicators, not individual waiting-time estimates.
- Project-defined scores and alerts are decision-support screening tools, not official HHS KPIs.
- Statistical association or trend does not establish causation.

## Data quality controls
The application validates the source file, required six-column contract, parseable dates, non-negative counts, and presence of usable observations. Duplicate dates are aggregated before feature engineering.

## Deployment controls recommended for an organization
1. Approved governed data source and data owner.
2. Authentication, authorization, and least-privilege access.
3. HTTPS, secrets management, dependency scanning, and patch management.
4. Centralized application/error logs and audit trail.
5. Scheduled data-quality monitoring and freshness alerts.
6. Accessibility and cross-browser review.
7. Model/analytics change control and documented threshold ownership.
8. Privacy, legal, policy, and security review before operational use.

## Validation
Run `python tests.py` before release. Forecasting is presented as a transparent baseline and evaluated using held-out backtesting.
