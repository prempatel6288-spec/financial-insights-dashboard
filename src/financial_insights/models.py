"""Model training, evaluation, and dashboard-export helpers."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import average_precision_score, mean_absolute_error, mean_squared_error, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


def _read_view(warehouse_path: Path, view: str) -> pd.DataFrame:
    with sqlite3.connect(warehouse_path) as connection:
        return pd.read_sql_query(f"SELECT * FROM {view}", connection)


def train_revenue_forecast(warehouse_path: Path, seed: int) -> tuple[pd.DataFrame, dict]:
    revenue = _read_view(warehouse_path, "monthly_revenue")
    revenue["month"] = pd.to_datetime(revenue["month"])
    revenue["month_index"] = np.arange(len(revenue))
    revenue["month_of_year"] = revenue["month"].dt.month
    revenue["lag_1"] = revenue["revenue"].shift(1)
    revenue["lag_3"] = revenue["revenue"].shift(3)
    model_data = revenue.dropna().copy()
    holdout = min(6, max(3, len(model_data) // 5))
    train, test = model_data.iloc[:-holdout], model_data.iloc[-holdout:]
    features = ["month_index", "month_of_year", "lag_1", "lag_3"]
    model = RandomForestRegressor(n_estimators=150, min_samples_leaf=2, random_state=seed)
    model.fit(train[features], train["revenue"])
    predicted = model.predict(test[features])
    metrics = {
        "mae": round(float(mean_absolute_error(test["revenue"], predicted)), 2),
        "rmse": round(float(mean_squared_error(test["revenue"], predicted) ** 0.5), 2),
        "holdout_months": int(holdout),
    }
    actual = revenue[["month", "revenue"]].copy()
    actual["series"] = "actual"
    actual["lower_bound"] = np.nan
    actual["upper_bound"] = np.nan

    full_model = RandomForestRegressor(n_estimators=150, min_samples_leaf=2, random_state=seed)
    full_model.fit(model_data[features], model_data["revenue"])
    history = list(revenue["revenue"])
    future_rows = []
    last_month = revenue["month"].max()
    residual_spread = max(metrics["mae"] * 1.25, 1)
    for step in range(1, 7):
        month = last_month + pd.DateOffset(months=step)
        feature_row = pd.DataFrame([{
            "month_index": len(revenue) + step - 1,
            "month_of_year": month.month,
            "lag_1": history[-1],
            "lag_3": history[-3],
        }])
        value = float(full_model.predict(feature_row)[0])
        history.append(value)
        future_rows.append({"month": month, "revenue": round(value, 2), "series": "forecast",
                            "lower_bound": round(max(0, value - residual_spread), 2),
                            "upper_bound": round(value + residual_spread, 2)})
    return pd.concat([actual, pd.DataFrame(future_rows)], ignore_index=True), metrics


def train_churn_model(warehouse_path: Path, seed: int) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    data = _read_view(warehouse_path, "customer_features").dropna().copy()
    data["month"] = pd.to_datetime(data["month"])
    cutoff = data["month"].sort_values().unique()[-6]
    train, test = data[data["month"] < cutoff], data[data["month"] >= cutoff]
    numerical = ["tenure_months", "products_held", "transactions", "engagement_score", "support_tickets",
                 "marketing_touch", "monthly_revenue", "revenue_lag_1", "revenue_rolling_3", "engagement_rolling_4"]
    categorical = ["region", "segment"]
    preprocessor = ColumnTransformer([
        ("numeric", Pipeline([("impute", SimpleImputer(strategy="median"))]), numerical),
        ("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical),
    ])
    classifier = RandomForestClassifier(
        n_estimators=150, min_samples_leaf=3, class_weight="balanced", random_state=seed, n_jobs=-1
    )
    pipeline = Pipeline([("prepare", preprocessor), ("model", classifier)])
    pipeline.fit(train[numerical + categorical], train["churned"])
    probability = pipeline.predict_proba(test[numerical + categorical])[:, 1]
    metrics = {
        "roc_auc": round(float(roc_auc_score(test["churned"], probability)), 3),
        "average_precision": round(float(average_precision_score(test["churned"], probability)), 3),
        "test_records": int(len(test)),
    }
    risk = test[["month", "customer_id", "region", "segment", "monthly_revenue", "churned"]].copy()
    risk["churn_probability"] = probability.round(4)
    risk["risk_band"] = pd.cut(probability, bins=[-0.01, 0.2, 0.5, 1.0], labels=["Low", "Medium", "High"])
    risk = risk.sort_values("churn_probability", ascending=False)
    feature_names = pipeline.named_steps["prepare"].get_feature_names_out()
    importances = pd.DataFrame({"feature": feature_names, "importance": classifier.feature_importances_})
    importances["feature"] = importances["feature"].str.replace("numeric__", "", regex=False).str.replace("categorical__", "", regex=False)
    return risk, importances.sort_values("importance", ascending=False), metrics


def build_kpis(risk: pd.DataFrame) -> pd.DataFrame:
    return (
        risk.groupby(["month", "region", "segment"], as_index=False)
        .agg(
            customer_count=("customer_id", "nunique"),
            total_revenue=("monthly_revenue", "sum"),
            churn_rate=("churned", "mean"),
            average_churn_probability=("churn_probability", "mean"),
        )
        .round({"total_revenue": 2, "churn_rate": 4, "average_churn_probability": 4})
    )
