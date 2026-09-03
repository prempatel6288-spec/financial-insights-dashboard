# Tableau dashboard guide

All sources come from a synthetic demonstration dataset. Add a visible note to any published dashboard stating that it uses synthetic data.

## Suggested dashboard

1. **Revenue outlook:** connect `revenue_forecast.csv`; plot `month` against `revenue`, colour by `series` (`actual` or `forecast`). Add `lower_bound` and `upper_bound` as a confidence-range band if desired.
2. **Churn worklist:** connect `churn_risk.csv`; show `customer_id`, `churn_probability`, `risk_band`, `monthly_revenue`, `segment`, and `region`. Filter to `High` risk and sort by probability descending.
3. **Portfolio KPIs:** connect `customer_kpis.csv`; show total revenue, customer count, churn rate, and average churn probability by `region` and `segment`.
4. **Model drivers:** connect `feature_importance.csv`; plot `importance` by `feature`.

For a single workbook, relate `churn_risk.csv` to `customer_kpis.csv` by `region` and `segment` only when the analysis needs that aggregation; otherwise keep sources separate to avoid duplicate-counting customer records.

