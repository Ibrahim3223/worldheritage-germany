#!/usr/bin/env python3
"""
MASTER IMAGE OPTIMIZER
Download and optimize images from Wikimedia Commons
Single size (1920w) for quality, Hugo handles responsive sizing

Usage:
    python optimize_images_master.py --source data/fetched
    python optimize_images_master.py --country Germany --limit 5
    python optimize_images_master.py --reprocess  # Re-download all
"""

import argparse
import json
import time
import hashlib
from pathlib import Path
from typing import List, Optional
import requests
from urllib.parse import unquote

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("[INFO] PIL not available. Install with: pip install Pillow")

DATA_DIR = Path("data/fetched")
OUTPUT_DIR = Path("static/images-sites")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# WIKIMEDIA COMMONS IMAGE PROCESSING
# ============================================================================

def get_commons_image_url(image_url: str, target_width: int = 1920) -> Optional[str]:
    """
    Convert Wikimedia Commons image URL to specific size

    Args:
        image_url: Original Commons URL
        target_width: Desired width (default: 1920)

    Returns:
        Direct image URL or None
    """
    try:
        # Commons URLs come in format: http://commons.wikimedia.org/wiki/Special:FilePath/...
        # We need to get the actual file URL at specific size

        # Extract filename
        if "Special:FilePath/" in image_url:
            filename = image_url.split("Special:FilePath/")[1]
        elif "File:" in image_url:
            filename = image_url.split("File:")[1]
        else:
            filename = image_url.split("/")[-1]

        filename = unquote(filename)

        # Build thumbnail URL
        # Wikimedia uses MD5 hash for file storage
        md5 = hashlib.md5(filename.encode('utf-8')).hexdigest()

        # Thumbnail URL format:
        # https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/filename.jpg/1920px-filename.jpg
        thumb_url = f"https://upload.wikimedia.org/wikipedia/commons/thumb/{md5[0]}/{md5[0:2]}/{filename}/{target_width}px-{filename}"

        return thumb_url

    except Exception as e:
        print(f"    [WARN] Could not parse image URL: {e}")
        return None

def download_image(url: str, output_path: Path, max_retries: int = 3) -> bool:
    """
    Download image from URL with retries

    Args:
        url: Image URL
        output_path: Where to save
        max_retries: Number of retry attempts

    Returns:
        Success boolean
    """
    headers = {
        "User-Agent": "WorldHeritageBot/2.0 (https://worldheritage.guide)"
    }

    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=30, stream=True)
            response.raise_for_status()

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return True

        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            else:
                print(f"    [ERROR] Download failed after {max_retries} attempts: {e}")
                return False

def convert_to_webp(image_path: Path, quality: int = 85) -> bool:
    """
    Convert image to WebP format

    Args:
        image_path: Path to image
        quality: WebP quality (1-100)

    Returns:
        Success boolean
    """
    if not HAS_PIL:
        print("    [WARN] PIL not available, skipping conversion")
        return False

    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

            # Save as WebP
            webp_path = image_path.with_suffix('.webp')
            img.save(webp_path, 'WEBP', quality=quality)

            # Remove original if different
            if webp_path != image_path:
                image_path.unlink()

            return True

    except Exception as e:
        print(f"    [ERROR] WebP conversion failed: {e}")
        return False

# ============================================================================
# SITE IMAGE PROCESSING
# ============================================================================

def process_site_images(site_data: dict, slug: str, max_images: int = 5,
                       reprocess: bool = False) -> int:
    """
    Download and optimize images for a site

    Args:
        site_data: Site information from JSON
        slug: Site slug for directory naming
        max_images: Maximum images per site
        reprocess: Re-download even if exists

    Returns:
        Number of images processed
    """
    site_dir = OUTPUT_DIR / slug
    site_dir.mkdir(parents=True, exist_ok=True)

    # Check existing images
    existing = list(site_dir.glob("*.webp"))
    if existing and not reprocess:
        if len(existing) >= max_images:
            return 0  # Already has enough images

    processed = 0

    # Download main image if available
    if site_data.get('has_image') and 'image_url' in site_data:
        image_num = len(existing) + 1
        if image_num <= max_images:
            output_name = f"{image_num:02d}-wikimedia-1920w.webp"
            output_path = site_dir / output_name

            if not output_path.exists() or reprocess:
                # Try to get sized URL
                sized_url = get_commons_image_url(site_data['image_url'], 1920)

                # Fallback to original URL if sizing fails
                url = sized_url if sized_url else site_data['image_url']

                # Download
                temp_path = output_path.with_suffix('.tmp')
                if download_image(url, temp_path):
                    # Convert to WebP if needed
                    if temp_path.suffix.lower() != '.webp':
                        if convert_to_webp(temp_path):
                            processed += 1
                    else:
                        temp_path.rename(output_path)
                        processed += 1
                else:
                    if temp_path.exists():
                        temp_path.unlink()

    return processed

# ============================================================================
# BATCH PROCESSING
# ============================================================================

def process_all_sites(country: str = "Germany", max_images: int = 5,
                     reprocess: bool = False):
    """
    Process images for all sites in fetched data

    Args:
        country: Country name
        max_images: Maximum images per site
        reprocess: Re-download all images
    """
    print("=" * 80)
    print(f"MASTER IMAGE OPTIMIZER - {country}")
    print("=" * 80)
    print(f"Max images per site: {max_images}")
    print(f"Reprocess existing: {reprocess}")
    print(f"Target size: 1920w WebP")
    print()

    # Find all JSON files for this country
    pattern = f"{country.lower()}_*.json"
    json_files = sorted(DATA_DIR.glob(pattern))

    if not json_files:
        print(f"[ERROR] No data files found for {country}")
        return

    print(f"Found {len(json_files)} category files\n")

    total_sites = 0
    total_images = 0
    sites_with_images = 0

    for json_file in json_files:
        category_name = json_file.stem.replace(f"{country.lower()}_", "")

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                sites = json.load(f)

            print(f"Processing: {category_name} ({len(sites)} sites)")

            processed_in_category = 0

            for site in sites:
                # Generate slug
                slug = site.get('title', '').lower()
                slug = slug.replace(' ', '-')
                slug = ''.join(c for c in slug if c.isalnum() or c == '-')

                # Process images
                num_images = process_site_images(site, slug, max_images, reprocess)

                if num_images > 0:
                    processed_in_category += num_images
                    total_images += num_images
                    sites_with_images += 1

                total_sites += 1

                # Rate limiting
                if num_images > 0:
                    time.sleep(0.5)  # Be nice to Wikimedia

            print(f"  Processed: {processed_in_category} images")

        except Exception as e:
            print(f"  [ERROR] Failed to process {json_file.name}: {e}")
            continue

    print(f"\n{'='*80}")
    print("IMAGE OPTIMIZATION COMPLETE")
    print(f"{'='*80}")
    print(f"Total sites processed: {total_sites:,}")
    print(f"Sites with images: {sites_with_images:,} ({sites_with_images/total_sites*100:.1f}%)")
    print(f"Total images downloaded: {total_images:,}")
    print(f"Average images per site: {total_images/sites_with_images:.1f}" if sites_with_images > 0 else "N/A")

# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Master image optimizer')
    parser.add_argument('--country', default='Germany', help='Country name')
    parser.add_argument('--limit', type=int, default=5, help='Max images per site')
    parser.add_argument('--reprocess', action='store_true', help='Re-download all images')
    parser.add_argument('--source', type=Path, help='Custom data directory')

    args = parser.parse_args()

    if args.source:
        global DATA_DIR
        DATA_DIR = args.source

    process_all_sites(args.country, args.limit, args.reprocess)

if __name__ == "__main__":
    main()
