"""
Optimized Image Fetcher for WorldHeritage Germany
- Max 3 images per site
- Only 2 sizes: 800w (main) and 400w (thumbnail)
- WebP format, quality 75
- Skips already downloaded sites
- Clear progress display
"""

import os
import sys
import json
import time
import hashlib
import argparse
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
from io import BytesIO

# ============================================
# CONFIGURATION
# ============================================

CONFIG = {
    'max_images_per_site': 1,  # Just 1 primary image (faster)
    'sizes': [400, 800],  # thumbnail and main only
    'quality': 75,
    'timeout': 10,
    'rate_limit': 0.2,  # seconds between requests
    'max_workers': 4,  # parallel downloads
    'min_width': 600,
    'min_height': 400,
    'skip_commons_if_wikidata': True,  # Don't search Commons if Wikidata has image
}

BASE_DIR = Path(__file__).parent.parent
IMAGES_DIR = BASE_DIR / 'static' / 'images-sites'
DATA_DIR = BASE_DIR / 'data' / 'fetched'
PROGRESS_FILE = BASE_DIR / 'image_fetch_progress.txt'

HEADERS = {
    'User-Agent': 'WorldHeritageBot/1.0 (https://worldheritage.guide) Python/requests',
}

# ============================================
# UTILITIES
# ============================================

def generate_slug(title: str) -> str:
    """Generate URL-friendly slug from title"""
    import re
    slug = title.lower()
    slug = re.sub(r'[äÄ]', 'ae', slug)
    slug = re.sub(r'[öÖ]', 'oe', slug)
    slug = re.sub(r'[üÜ]', 'ue', slug)
    slug = re.sub(r'[ß]', 'ss', slug)
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug[:80]

def log(message: str, level: str = 'INFO'):
    """Print log message with timestamp"""
    timestamp = time.strftime('%H:%M:%S')
    print(f"[{timestamp}] {level}: {message}")
    sys.stdout.flush()

def write_progress(message: str):
    """Write progress to file for monitoring"""
    with open(PROGRESS_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

# ============================================
# IMAGE PROCESSING
# ============================================

def download_and_optimize(url: str, site_slug: str, index: int) -> bool:
    """Download image and create optimized versions"""
    try:
        # Download
        response = requests.get(url, headers=HEADERS, timeout=CONFIG['timeout'], stream=True)
        response.raise_for_status()

        # Open with PIL
        img = Image.open(BytesIO(response.content))

        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        # Check minimum size
        if img.width < CONFIG['min_width'] or img.height < CONFIG['min_height']:
            return False

        # Create site directory
        site_dir = IMAGES_DIR / site_slug
        site_dir.mkdir(parents=True, exist_ok=True)

        # Generate hash for filename
        file_hash = hashlib.md5(url.encode()).hexdigest()[:8]

        # Create optimized versions
        for width in CONFIG['sizes']:
            if img.width >= width:
                # Calculate height maintaining aspect ratio
                ratio = width / img.width
                height = int(img.height * ratio)

                # Resize
                resized = img.resize((width, height), Image.Resampling.LANCZOS)

                # Save as WebP
                output_path = site_dir / f"{index:02d}-{file_hash}-{width}w.webp"
                resized.save(output_path, 'WEBP', quality=CONFIG['quality'], method=6)

        return True

    except Exception as e:
        return False

def get_wikimedia_image_url(commons_url: str, width: int = 1200) -> str:
    """Convert Commons URL to direct image URL with specific width"""
    if not commons_url:
        return None

    # Handle Special:FilePath URLs
    if 'Special:FilePath' in commons_url:
        filename = commons_url.split('Special:FilePath/')[-1]
        # Use Wikimedia thumbnail API for specific size
        return f"https://commons.wikimedia.org/wiki/Special:FilePath/{filename}?width={width}"

    return commons_url

def search_commons_images(site_name: str, limit: int = 5) -> list:
    """Search Wikimedia Commons for additional images"""
    API_URL = "https://commons.wikimedia.org/w/api.php"

    params = {
        'action': 'query',
        'format': 'json',
        'generator': 'search',
        'gsrsearch': f'"{site_name}"',
        'gsrlimit': limit,
        'gsrnamespace': 6,
        'prop': 'imageinfo',
        'iiprop': 'url|size|mime',
        'iiurlwidth': 1200,
    }

    try:
        response = requests.get(API_URL, params=params, headers=HEADERS, timeout=CONFIG['timeout'])
        response.raise_for_status()
        data = response.json()

        if 'query' not in data or 'pages' not in data['query']:
            return []

        images = []
        for page in data['query']['pages'].values():
            if 'imageinfo' not in page:
                continue

            info = page['imageinfo'][0]
            mime = info.get('mime', '')

            # Only accept standard image formats
            if mime not in ['image/jpeg', 'image/png', 'image/webp']:
                continue

            # Check size
            if info.get('width', 0) >= CONFIG['min_width'] and info.get('height', 0) >= CONFIG['min_height']:
                images.append(info.get('url'))

        return images[:limit]

    except Exception:
        return []

# ============================================
# MAIN PROCESSING
# ============================================

def process_site(site: dict) -> dict:
    """Process images for a single site"""
    title = site.get('title', '')
    slug = generate_slug(title)
    site_dir = IMAGES_DIR / slug

    # Check if already processed
    if site_dir.exists():
        existing = list(site_dir.glob('*.webp'))
        if len(existing) >= 2:  # At least 1 image with 2 sizes
            return {'slug': slug, 'status': 'skipped', 'count': len(existing) // 2}

    # Collect image URLs
    image_urls = []

    # 1. Primary image from Wikidata
    if site.get('image_url'):
        primary_url = get_wikimedia_image_url(site['image_url'], 1200)
        if primary_url:
            image_urls.append(primary_url)

    # 2. Search Commons only if no Wikidata image and option enabled
    if not image_urls or (not CONFIG.get('skip_commons_if_wikidata') and len(image_urls) < CONFIG['max_images_per_site']):
        commons_images = search_commons_images(title, limit=3)
        for img_url in commons_images:
            if img_url not in image_urls and len(image_urls) < CONFIG['max_images_per_site']:
                image_urls.append(img_url)

    if not image_urls:
        return {'slug': slug, 'status': 'no_images', 'count': 0}

    # Download and optimize
    successful = 0
    for idx, url in enumerate(image_urls, 1):
        if download_and_optimize(url, slug, idx):
            successful += 1
        time.sleep(CONFIG['rate_limit'])

    status = 'success' if successful > 0 else 'failed'
    return {'slug': slug, 'status': status, 'count': successful}

def load_all_sites() -> list:
    """Load all sites from fetched JSON files"""
    all_sites = []

    for json_file in DATA_DIR.glob('germany_*.json'):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                sites = json.load(f)
                all_sites.extend(sites)
        except Exception as e:
            log(f"Error loading {json_file.name}: {e}", 'ERROR')

    return all_sites

def main():
    parser = argparse.ArgumentParser(description='Fetch and optimize images for heritage sites')
    parser.add_argument('--test', type=int, help='Test mode: process only N sites')
    parser.add_argument('--category', type=str, help='Process only specific category')
    parser.add_argument('--force', action='store_true', help='Re-download existing images')
    args = parser.parse_args()

    # Clear progress file
    PROGRESS_FILE.write_text('')

    log("=" * 60)
    log("OPTIMIZED IMAGE FETCHER")
    log("=" * 60)
    write_progress("Starting image fetch")

    # Create images directory
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    # Load sites
    if args.category:
        json_file = DATA_DIR / f'germany_{args.category}.json'
        if not json_file.exists():
            log(f"Category file not found: {json_file}", 'ERROR')
            return
        with open(json_file, 'r', encoding='utf-8') as f:
            sites = json.load(f)
        log(f"Loaded {len(sites)} sites from {args.category}")
    else:
        sites = load_all_sites()
        log(f"Loaded {len(sites)} total sites")

    if args.test:
        sites = sites[:args.test]
        log(f"Test mode: processing {len(sites)} sites")

    write_progress(f"Total sites to process: {len(sites)}")

    # Count existing
    existing_count = sum(1 for s in sites if (IMAGES_DIR / generate_slug(s.get('title', ''))).exists())
    log(f"Already processed: {existing_count}")
    log(f"To process: {len(sites) - existing_count}")
    log("")

    # Process sites
    stats = {'success': 0, 'skipped': 0, 'failed': 0, 'no_images': 0}
    start_time = time.time()

    for i, site in enumerate(sites, 1):
        result = process_site(site)
        stats[result['status']] += 1

        # Progress display
        elapsed = time.time() - start_time
        rate = i / elapsed if elapsed > 0 else 0
        eta = (len(sites) - i) / rate if rate > 0 else 0

        status_icon = {'success': '+', 'skipped': '>', 'failed': 'X', 'no_images': '-'}[result['status']]

        # Print progress (use \r for terminal, full line for file)
        progress_str = f"[{i}/{len(sites)}] {status_icon} {result['slug'][:35]:<35} OK:{stats['success']} Skip:{stats['skipped']} ETA:{int(eta//60)}m"

        # Check if output is a terminal
        if sys.stdout.isatty():
            print(f"\r{progress_str}", end='', flush=True)
        else:
            # For file output, print every 25 sites
            if i % 25 == 0 or result['status'] in ('failed', 'no_images'):
                print(progress_str)
                sys.stdout.flush()

        # Log every 100 sites
        if i % 100 == 0:
            write_progress(f"Progress: {i}/{len(sites)} - OK:{stats['success']} Skip:{stats['skipped']}")

    print()  # New line after progress

    # Summary
    elapsed = time.time() - start_time
    log("")
    log("=" * 60)
    log("SUMMARY")
    log("=" * 60)
    log(f"Total processed: {sum(stats.values())}")
    log(f"  Success: {stats['success']}")
    log(f"  Skipped (existing): {stats['skipped']}")
    log(f"  Failed: {stats['failed']}")
    log(f"  No images found: {stats['no_images']}")
    log(f"Time: {int(elapsed//60)}m {int(elapsed%60)}s")

    write_progress(f"COMPLETE - Success:{stats['success']} Skipped:{stats['skipped']} Failed:{stats['failed']}")

    # Calculate disk usage
    try:
        total_size = sum(f.stat().st_size for f in IMAGES_DIR.rglob('*.webp'))
        log(f"Total disk usage: {total_size / (1024*1024):.1f} MB")
    except:
        pass

if __name__ == '__main__':
    main()
