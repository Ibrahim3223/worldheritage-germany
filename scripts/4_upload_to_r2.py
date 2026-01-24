#!/usr/bin/env python3
"""
Upload images to Cloudflare R2 bucket.
Uses boto3 with S3-compatible API.
"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

import boto3
from botocore.config import Config
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import mimetypes

# R2 Configuration - UPDATE THESE VALUES
R2_ACCOUNT_ID = os.getenv('R2_ACCOUNT_ID', 'YOUR_ACCOUNT_ID')
R2_ACCESS_KEY_ID = os.getenv('R2_ACCESS_KEY_ID', 'YOUR_ACCESS_KEY')
R2_SECRET_ACCESS_KEY = os.getenv('R2_SECRET_ACCESS_KEY', 'YOUR_SECRET_KEY')
R2_BUCKET_NAME = os.getenv('R2_BUCKET_NAME', 'worldheritage-germany-images')

# Paths
IMAGES_DIR = Path(__file__).parent.parent / 'static' / 'images-sites'

def get_r2_client():
    """Create R2 client using S3-compatible API."""
    return boto3.client(
        's3',
        endpoint_url=f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        config=Config(
            signature_version='s3v4',
            retries={'max_attempts': 3, 'mode': 'adaptive'}
        )
    )

def get_content_type(file_path):
    """Get MIME type for file."""
    mime_type, _ = mimetypes.guess_type(str(file_path))
    return mime_type or 'application/octet-stream'

def upload_file(client, file_path, bucket_name, key):
    """Upload single file to R2."""
    try:
        content_type = get_content_type(file_path)
        client.upload_file(
            str(file_path),
            bucket_name,
            key,
            ExtraArgs={
                'ContentType': content_type,
                'CacheControl': 'public, max-age=31536000'  # 1 year cache
            }
        )
        return True, key
    except Exception as e:
        return False, f"{key}: {e}"

def list_existing_keys(client, bucket_name, prefix=''):
    """List existing keys in bucket."""
    existing = set()
    paginator = client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
        for obj in page.get('Contents', []):
            existing.add(obj['Key'])
    return existing

def main():
    print("=" * 60, flush=True)
    print("Cloudflare R2 Image Uploader", flush=True)
    print("=" * 60, flush=True)

    # Validate config
    if 'YOUR_' in R2_ACCOUNT_ID or 'YOUR_' in R2_ACCESS_KEY_ID:
        print("\nERROR: Please set R2 credentials in .env file:")
        print("  R2_ACCOUNT_ID=your_account_id")
        print("  R2_ACCESS_KEY_ID=your_access_key")
        print("  R2_SECRET_ACCESS_KEY=your_secret_key")
        print("  R2_BUCKET_NAME=worldheritage-germany-images")
        return

    if not IMAGES_DIR.exists():
        print(f"ERROR: Images directory not found: {IMAGES_DIR}")
        return

    # Get R2 client
    print(f"\nConnecting to R2 bucket: {R2_BUCKET_NAME}")
    client = get_r2_client()

    # List existing files to skip
    print("Checking existing files in bucket...")
    try:
        existing_keys = list_existing_keys(client, R2_BUCKET_NAME)
        print(f"Found {len(existing_keys)} existing files")
    except Exception as e:
        print(f"Could not list bucket (might be empty): {e}")
        existing_keys = set()

    # Collect files to upload
    print(f"\nScanning: {IMAGES_DIR}")
    files_to_upload = []

    for site_dir in IMAGES_DIR.iterdir():
        if not site_dir.is_dir():
            continue
        for img_file in site_dir.iterdir():
            if img_file.suffix.lower() in ['.webp', '.jpg', '.jpeg', '.png', '.gif']:
                key = f"images-sites/{site_dir.name}/{img_file.name}"
                if key not in existing_keys:
                    files_to_upload.append((img_file, key))

    total = len(files_to_upload)
    print(f"Files to upload: {total}")

    if total == 0:
        print("No new files to upload!")
        return

    # Upload with progress
    success = 0
    failed = 0

    print(f"\nUploading with 10 parallel workers...")

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(upload_file, client, fp, R2_BUCKET_NAME, key): key
            for fp, key in files_to_upload
        }

        for i, future in enumerate(as_completed(futures), 1):
            ok, result = future.result()
            if ok:
                success += 1
            else:
                failed += 1
                print(f"  FAILED: {result}")

            if i % 100 == 0 or i == total:
                print(f"Progress: {i}/{total} (OK:{success} FAIL:{failed})")

    print("\n" + "=" * 60)
    print(f"COMPLETE - Success: {success}, Failed: {failed}")
    print("=" * 60)

if __name__ == '__main__':
    main()
