#!/usr/bin/env python3
"""Upload locally generated demo artifacts to an existing S3 bucket."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from financial_insights.aws import upload_outputs_to_s3
from financial_insights.config import OUTPUT_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload existing output files to S3.")
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--prefix", default="financial-insights-demo")
    args = parser.parse_args()
    uploaded = upload_outputs_to_s3(OUTPUT_DIR, args.bucket, args.prefix)
    print("Uploaded:\n" + "\n".join(uploaded))


if __name__ == "__main__":
    main()

