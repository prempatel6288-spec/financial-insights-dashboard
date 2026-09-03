"""Orchestration for the reproducible local financial-insights pipeline."""

from __future__ import annotations

import json
from pathlib import Path

from .data import generate_synthetic_data, save_and_load_to_sqlite
from .models import build_kpis, train_churn_model, train_revenue_forecast


def run_pipeline(raw_path: Path, warehouse_path: Path, sql_path: Path, output_dir: Path, customers: int, months: int, seed: int) -> dict:
    data = generate_synthetic_data(customers=customers, months=months, seed=seed)
    save_and_load_to_sqlite(data, raw_path, warehouse_path, sql_path)
    forecast, forecast_metrics = train_revenue_forecast(warehouse_path, seed)
    churn_risk, feature_importance, churn_metrics = train_churn_model(warehouse_path, seed)
    kpis = build_kpis(churn_risk)
    output_dir.mkdir(parents=True, exist_ok=True)
    forecast.to_csv(output_dir / "revenue_forecast.csv", index=False)
    churn_risk.to_csv(output_dir / "churn_risk.csv", index=False)
    kpis.to_csv(output_dir / "customer_kpis.csv", index=False)
    feature_importance.to_csv(output_dir / "feature_importance.csv", index=False)
    metrics = {"data_notice": "All records are synthetic demonstration data.", "forecast": forecast_metrics, "churn": churn_metrics}
    (output_dir / "model_metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    return {"records_generated": len(data), "outputs": 5, "metrics": metrics}

