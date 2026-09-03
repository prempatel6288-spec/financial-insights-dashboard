#!/usr/bin/env python3
"""Generate synthetic data, train models, and export dashboard-ready outputs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from financial_insights.config import OUTPUT_DIR, RAW_DATA_PATH, SQL_PATH, WAREHOUSE_PATH
from financial_insights.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the synthetic financial insights pipeline.")
    parser.add_argument("--customers", type=int, default=500)
    parser.add_argument("--months", type=int, default=36)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    result = run_pipeline(RAW_DATA_PATH, WAREHOUSE_PATH, SQL_PATH, OUTPUT_DIR, args.customers, args.months, args.seed)
    print(f"Generated {result['records_generated']:,} synthetic records and {result['outputs']} dashboard-ready outputs.")
    print(f"Forecast MAE: {result['metrics']['forecast']['mae']}; churn ROC-AUC: {result['metrics']['churn']['roc_auc']}")


if __name__ == "__main__":
    main()

