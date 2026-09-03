"""Smoke test for the synthetic, local-first pipeline."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from financial_insights.pipeline import run_pipeline


class PipelineTest(unittest.TestCase):
    def test_pipeline_exports_dashboard_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            result = run_pipeline(
                raw_path=temp / "raw.csv",
                warehouse_path=temp / "warehouse.db",
                sql_path=ROOT / "sql" / "01_transformations.sql",
                output_dir=temp / "outputs",
                customers=60,
                months=24,
                seed=11,
            )
            self.assertEqual(result["outputs"], 5)
            for filename in [
                "revenue_forecast.csv",
                "churn_risk.csv",
                "customer_kpis.csv",
                "feature_importance.csv",
                "model_metrics.json",
            ]:
                self.assertTrue((temp / "outputs" / filename).exists())
            metrics = json.loads((temp / "outputs" / "model_metrics.json").read_text())
            self.assertEqual(metrics["data_notice"], "All records are synthetic demonstration data.")


if __name__ == "__main__":
    unittest.main()

