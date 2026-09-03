"""Optional AWS adapter. No AWS calls occur unless this function is invoked."""

from __future__ import annotations

from pathlib import Path


def upload_outputs_to_s3(output_dir: Path, bucket: str, prefix: str = "") -> list[str]:
    import boto3

    client = boto3.client("s3")
    uploaded = []
    for file_path in sorted(output_dir.glob("*")):
        if file_path.is_file() and file_path.name != ".gitkeep":
            key = f"{prefix.strip('/')}/{file_path.name}".lstrip("/")
            client.upload_file(str(file_path), bucket, key)
            uploaded.append(f"s3://{bucket}/{key}")
    return uploaded

