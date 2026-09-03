# AI-Powered Financial Insights Dashboard

A local-first, reproducible machine-learning project for **revenue forecasting** and **customer churn prediction**. It produces dashboard-ready CSVs for Tableau and includes an optional AWS S3 upload adapter.

> **Data notice:** this repository generates a fully **synthetic** financial-services dataset. It contains no real company, customer, transaction, or production data. The data is designed only to exercise the pipeline and demonstrate the project structure.

## What it does

- Generates monthly customer-level synthetic financial data with a fixed seed
- Loads it into SQLite and applies reusable SQL transformations
- Trains and evaluates a revenue forecasting model
- Trains and evaluates a churn-risk classification model
- Exports forecast, churn-risk, KPI, feature-importance, and evaluation files for Tableau
- Provides an optional, credential-free-by-default AWS S3 upload adapter

## Stack

Python · SQL (SQLite) · scikit-learn · AWS S3 adapter · Tableau-ready CSV outputs

## Project layout

```
src/financial_insights/    Pipeline and reusable modules
sql/                       SQL transformations
scripts/                   Command-line entry points
data/raw/                  Generated synthetic input (gitignored)
data/warehouse/            SQLite warehouse (gitignored)
outputs/                   Dashboard-ready artifacts (gitignored)
```

## Run locally

Requires Python 3.10+.

```bash
git clone <your-repository-url>
cd financial-insights-dashboard
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python scripts/run_pipeline.py
```

The command is deterministic by default and writes these files into `outputs/`:

| File | Tableau use |
| --- | --- |
| `revenue_forecast.csv` | Revenue trend and forecast line chart |
| `churn_risk.csv` | At-risk customer table, filters, and prioritization |
| `customer_kpis.csv` | Segment/region KPI cards and comparisons |
| `feature_importance.csv` | Model-driver bar chart |
| `model_metrics.json` | Model-quality documentation |

You can set a different seed or dataset size:

```bash
python scripts/run_pipeline.py --customers 1200 --months 48 --seed 7
```

Run the lightweight validation test with:

```bash
python -m unittest discover -s tests
```

## Tableau quick start

1. In Tableau, connect to the CSV files in `outputs/`.
2. Use `revenue_forecast.csv` for actual revenue through the historical period and forecast revenue thereafter.
3. Use `churn_risk.csv`, filtering `risk_band` to `High`, for a retention worklist.
4. Use `customer_kpis.csv` to build region and segment KPI cards.
5. Keep the synthetic-data note on any dashboard created from this repository.

See [docs/tableau.md](docs/tableau.md) for suggested views and field mappings.


## Reproducibility and responsible use

- A fixed random seed makes each run repeatable.
- Inputs, warehouse, and generated outputs are ignored by Git to prevent accidental data commits.
- This is a portfolio demonstration, not a production risk, retention, or financial-decision system.
- The models are illustrative and should not be used to make decisions about real people.

'''
