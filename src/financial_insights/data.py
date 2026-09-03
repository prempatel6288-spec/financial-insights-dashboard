"""Synthetic data generation and local ingestion utilities."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd


def generate_synthetic_data(customers: int, months: int, seed: int) -> pd.DataFrame:
    """Create a deterministic, explicitly synthetic monthly customer dataset."""
    if customers < 50 or months < 18:
        raise ValueError("Use at least 50 customers and 18 months for meaningful demo models.")

    rng = np.random.default_rng(seed)
    customer_ids = [f"SYN-{index:05d}" for index in range(1, customers + 1)]
    customer_profile = pd.DataFrame(
        {
            "customer_id": customer_ids,
            "region": rng.choice(["Central", "East", "West"], customers, p=[0.45, 0.28, 0.27]),
            "segment": rng.choice(["Consumer", "Small Business", "Commercial"], customers, p=[0.68, 0.24, 0.08]),
            "tenure_months_start": rng.integers(3, 84, customers),
            "base_revenue": rng.lognormal(mean=4.2, sigma=0.45, size=customers),
            "baseline_engagement": rng.uniform(0.25, 0.95, customers),
        }
    )
    records: list[dict] = []
    start = pd.Timestamp("2022-01-01")
    for month_number, month in enumerate(pd.date_range(start, periods=months, freq="MS")):
        seasonality = 1 + 0.08 * np.sin(2 * np.pi * month_number / 12)
        for profile in customer_profile.itertuples(index=False):
            engagement = np.clip(profile.baseline_engagement + rng.normal(0, 0.12), 0.02, 1.0)
            support_tickets = int(rng.poisson(0.3 + (1 - engagement) * 2.3))
            products = int(rng.integers(1, 5))
            transactions = int(rng.poisson(16 + engagement * 35 + products * 5))
            marketing_touch = int(rng.binomial(1, 0.35))
            churn_logit = -3.1 + 2.4 * (1 - engagement) + 0.35 * support_tickets - 0.18 * products
            churn_probability = 1 / (1 + np.exp(-churn_logit))
            churned = int(rng.binomial(1, min(churn_probability, 0.85)))
            segment_multiplier = {"Consumer": 1.0, "Small Business": 1.7, "Commercial": 3.1}[profile.segment]
            revenue = max(
                0,
                profile.base_revenue * segment_multiplier * seasonality
                * (0.72 + 0.55 * engagement) * (1 + 0.03 * marketing_touch)
                + rng.normal(0, 9),
            )
            if churned:
                revenue *= rng.uniform(0.1, 0.65)
            records.append(
                {
                    "month": month.strftime("%Y-%m-%d"),
                    "customer_id": profile.customer_id,
                    "region": profile.region,
                    "segment": profile.segment,
                    "tenure_months": profile.tenure_months_start + month_number,
                    "products_held": products,
                    "transactions": transactions,
                    "engagement_score": round(float(engagement), 4),
                    "support_tickets": support_tickets,
                    "marketing_touch": marketing_touch,
                    "monthly_revenue": round(float(revenue), 2),
                    "churned": churned,
                    "data_source": "synthetic_demo",
                }
            )
    return pd.DataFrame.from_records(records)


def save_and_load_to_sqlite(data: pd.DataFrame, raw_path: Path, warehouse_path: Path, sql_path: Path) -> None:
    """Persist synthetic input then construct a local SQLite analytical warehouse."""
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    warehouse_path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(raw_path, index=False)
    with sqlite3.connect(warehouse_path) as connection:
        data.to_sql("customer_monthly", connection, if_exists="replace", index=False)
        connection.executescript(sql_path.read_text())

