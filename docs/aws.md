# Optional AWS S3 adapter

This repository is local-first. It does not provision cloud resources or require credentials to train models.

To upload generated dashboard artifacts to an existing S3 bucket:

1. Configure your own AWS credentials using your preferred secure method (for example, an AWS CLI profile or environment variables).
2. Ensure the identity has the least-privilege `s3:PutObject` permission for the target bucket/prefix.
3. Run `python scripts/upload_to_s3.py --bucket YOUR_BUCKET --prefix financial-insights-demo`.

The adapter uploads only the contents of `outputs/`. Do not upload real customer data without appropriate authorization, governance, encryption, and retention controls.

