"""
Script 5: Update Sites with Wikimedia Commons Image URLs
Fetches image URLs directly from Wikidata/Wikimedia Commons
No downloading - just URL references for high-quality images
"""

import os
import re
import json
import time
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================
# CONFIGURATION
# ============================================

CONTENT_DIR = Path(__file__).parent.parent / "content" / "sites"
WIKIMEDIA_API = "https://commons.wikimedia.org/w/api.php"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"

# Image sizes for responsive images
IMAGE_SIZES = [400, 800, 1200, 1920]

HEADERS = {
    'User-Agent': 'WorldHeritageBot/1.0 (https://worldheritage.guide; contact@worldheritage.guide) Python/requests',
    'Accept': 'application/json',
}

# ============================================
# WIKIMEDIA URL HELPERS
# ============================================

def get_wikimedia_thumb_url(filename: str, width: int = 1200) -> str:
    """
    Generate Wikimedia Commons thumbnail URL for a given filename

    Args:
        filename: The Commons filename (e.g., "Aachen_Cathedral_north.jpg")
        width: Desired width in pixels

    Returns:
        Thumbnail URL
    """
    # Clean filename
    filename = filename.replace(' ', '_')

    # Calculate MD5 hash for path
    md5 = hashlib.md5(filename.encode('utf-8')).hexdigest()

    # Construct URL
    # Format: https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/filename/WIDTHpx-filename
    base_url = f"https://upload.wikimedia.org/wikipedia/commons/thumb/{md5[0]}/{md5[0:2]}/{filename}/{width}px-{filename}"

    # Handle SVG and other special formats
    if filename.lower().endswith('.svg'):
        base_url += '.png'
    elif filename.lower().endswith('.tif') or filename.lower().endswith('.tiff'):
        base_url = base_url.replace(filename, filename + '.jpg')

    return base_url


def get_wikimedia_original_url(filename: str) -> str:
    """Get original (full resolution) URL for a Wikimedia file"""
    filename = filename.replace(' ', '_')
    md5 = hashlib.md5(filename.encode('utf-8')).hexdigest()
    return f"https://upload.wikimedia.org/wikipedia/commons/{md5[0]}/{md5[0:2]}/{filename}"


# ============================================
# WIKIDATA IMAGE FETCHING
# ============================================

def get_wikidata_images(wikidata_id: str) -> List[str]:
    """
    Get image filenames from Wikidata entity

    Args:
        wikidata_id: Wikidata ID (e.g., "Q4176")

    Returns:
        List of Wikimedia Commons filenames
    """
    if not wikidata_id or not wikidata_id.startswith('Q'):
        return []

    # SPARQL query to get images
    sparql_url = "https://query.wikidata.org/sparql"

    query = f"""
    SELECT ?image WHERE {{
      wd:{wikidata_id} wdt:P18 ?image .
    }}
    """

    try:
        response = requests.get(
            sparql_url,
            params={'query': query, 'format': 'json'},
            headers=HEADERS,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        images = []
        for result in data.get('results', {}).get('bindings', []):
            image_url = result.get('image', {}).get('value', '')
            if image_url:
                # Extract filename from URL
                filename = image_url.split('/')[-1]
                images.append(filename)

        return images

    except Exception as e:
        print(f"Error fetching Wikidata images for {wikidata_id}: {e}")
        return []


def search_commons_images(site_name: str, limit: int = 5) -> List[Dict]:
    """
    Search Wikimedia Commons for images of a site

    Returns list of dicts with filename and metadata
    """
    params = {
        'action': 'query',
        'format': 'json',
        'generator': 'search',
        'gsrsearch': f'"{site_name}"',
        'gsrlimit': limit,
        'gsrnamespace': 6,  # File namespace
        'prop': 'imageinfo',
        'iiprop': 'url|size|mime|extmetadata',
    }

    try:
        response = requests.get(WIKIMEDIA_API, params=params, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()

        if 'query' not in data or 'pages' not in data['query']:
            return []

        images = []
        for page_id, page in data['query']['pages'].items():
            if 'imageinfo' not in page:
                continue

            info = page['imageinfo'][0]

            # Skip non-image files
            mime = info.get('mime', '')
            if not mime.startswith('image/'):
                continue

            # Skip small images
            width = info.get('width', 0)
            height = info.get('height', 0)
            if width < 400 or height < 300:
                continue

            # Get filename from title
            title = page.get('title', '')
            if title.startswith('File:'):
                filename = title[5:]
            else:
                filename = title

            images.append({
                'filename': filename,
                'width': width,
                'height': height,
                'mime': mime,
                'url': info.get('url', ''),
            })

        # Sort by resolution (larger first)
        images.sort(key=lambda x: x['width'] * x['height'], reverse=True)

        return images[:limit]

    except Exception as e:
        print(f"Error searching Commons for {site_name}: {e}")
        return []


# ============================================
# CONTENT FILE PROCESSING
# ============================================

def parse_frontmatter(content: str) -> Tuple[Dict, str]:
    """Parse YAML frontmatter from markdown content"""
    if not content.startswith('---'):
        return {}, content

    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content

    import yaml
    try:
        frontmatter = yaml.safe_load(parts[1])
        body = '---'.join(parts[2:])
        return frontmatter or {}, body
    except:
        return {}, content


def build_frontmatter(data: Dict) -> str:
    """Build YAML frontmatter string from dict"""
    import yaml

    # Custom representer for clean output
    def str_representer(dumper, data):
        if '\n' in data:
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)

    yaml.add_representer(str, str_representer)

    return yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)


def update_site_images(filepath: Path, dry_run: bool = False) -> Dict:
    """
    Update a single site's images with Wikimedia URLs

    Returns dict with update status
    """
    result = {
        'file': filepath.name,
        'status': 'skipped',
        'images_before': 0,
        'images_after': 0,
        'wikidata_id': None,
    }

    try:
        content = filepath.read_text(encoding='utf-8')
        frontmatter, body = parse_frontmatter(content)

        if not frontmatter:
            result['status'] = 'error'
            result['error'] = 'No frontmatter'
            return result

        # Get Wikidata ID
        wikidata_id = frontmatter.get('wikidata_id', '')
        site_name = frontmatter.get('site_name', '') or frontmatter.get('title', '')

        result['wikidata_id'] = wikidata_id
        result['images_before'] = len(frontmatter.get('images', []))

        # Collect image filenames
        image_filenames = []

        # 1. Get from Wikidata P18 property
        if wikidata_id:
            wikidata_images = get_wikidata_images(wikidata_id)
            image_filenames.extend(wikidata_images)

        # 2. Search Commons if we don't have enough
        if len(image_filenames) < 3 and site_name:
            commons_images = search_commons_images(site_name, limit=5 - len(image_filenames))
            for img in commons_images:
                if img['filename'] not in image_filenames:
                    image_filenames.append(img['filename'])

        # Limit to 5 images max
        image_filenames = image_filenames[:5]

        if not image_filenames:
            result['status'] = 'no_images'
            return result

        # Generate URLs for each image
        wikimedia_images = []
        for filename in image_filenames:
            # Use 1200px as default size (good balance of quality and load time)
            url = get_wikimedia_thumb_url(filename, 1200)
            wikimedia_images.append({
                'url': url,
                'filename': filename,
                'srcset': {
                    400: get_wikimedia_thumb_url(filename, 400),
                    800: get_wikimedia_thumb_url(filename, 800),
                    1200: get_wikimedia_thumb_url(filename, 1200),
                    1920: get_wikimedia_thumb_url(filename, 1920),
                }
            })

        # Update frontmatter with new image format
        # Store as simple URL list for backward compatibility
        frontmatter['images'] = [img['url'] for img in wikimedia_images]

        # Also store srcset data for responsive images
        frontmatter['image_srcset'] = {
            img['filename']: img['srcset']
            for img in wikimedia_images
        }

        result['images_after'] = len(frontmatter['images'])

        if not dry_run:
            # Rebuild content
            new_content = '---\n' + build_frontmatter(frontmatter) + '---' + body
            filepath.write_text(new_content, encoding='utf-8')
            result['status'] = 'updated'
        else:
            result['status'] = 'would_update'

        return result

    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
        return result


# ============================================
# MAIN EXECUTION
# ============================================

def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Update site images with Wikimedia URLs')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without writing')
    parser.add_argument('--limit', type=int, default=0, help='Limit number of files to process (0=all)')
    parser.add_argument('--file', type=str, help='Process single file')
    args = parser.parse_args()

    print("=" * 60)
    print("Wikimedia Commons Image URL Updater")
    print("=" * 60)

    if args.dry_run:
        print("DRY RUN MODE - No files will be modified")

    # Get files to process
    if args.file:
        files = [CONTENT_DIR / args.file]
    else:
        files = sorted(CONTENT_DIR.glob('*.md'))
        if args.limit:
            files = files[:args.limit]

    # Filter out _index.md
    files = [f for f in files if f.name != '_index.md']

    print(f"\nProcessing {len(files)} files...")

    # Process files
    stats = {'updated': 0, 'skipped': 0, 'no_images': 0, 'error': 0}

    for filepath in tqdm(files, desc="Updating images"):
        result = update_site_images(filepath, dry_run=args.dry_run)

        if result['status'] in ['updated', 'would_update']:
            stats['updated'] += 1
            if args.dry_run:
                print(f"\n  {result['file']}: {result['images_before']} -> {result['images_after']} images")
        elif result['status'] == 'no_images':
            stats['no_images'] += 1
        elif result['status'] == 'error':
            stats['error'] += 1
            print(f"\n  ERROR {result['file']}: {result.get('error', 'Unknown')}")
        else:
            stats['skipped'] += 1

        # Rate limiting
        time.sleep(0.1)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Updated: {stats['updated']}")
    print(f"No images found: {stats['no_images']}")
    print(f"Errors: {stats['error']}")
    print(f"Skipped: {stats['skipped']}")


if __name__ == '__main__':
    main()
