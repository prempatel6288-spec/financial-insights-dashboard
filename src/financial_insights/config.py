from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_PATH = ROOT / "data" / "raw" / "synthetic_customer_monthly.csv"
WAREHOUSE_PATH = ROOT / "data" / "warehouse" / "financial_insights.db"
SQL_PATH = ROOT / "sql" / "01_transformations.sql"
OUTPUT_DIR = ROOT / "outputs"

