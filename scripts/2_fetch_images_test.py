"""
Fetch images for test sites only
Modified version of Script 2 for testing
"""

import os
import time
from pathlib import Path
from typing import List, Dict
import requests
from PIL import Image
import json

# Paths
base_dir = Path(__file__).parent.parent
sites_file = base_dir / 'data/raw/sites_test.json'
images_dir = base_dir / 'data/images'
mapbox_token = "pk.eyJ1IjoiaWJyYWhpbTMyMjMiLCJhIjoiY21rOHQwdWdlMHZpNzNkc212emZldGtuciJ9.tgnuRT2jSAT2ZsHVWHrMOw"

# Image sizes
IMAGE_SIZES = [320, 640, 1024, 1920]

def generate_slug(text):
    """Generate URL-friendly slug"""
    import re
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

def download_wikimedia_image(url, output_path):
    """Download image from Wikimedia Commons"""
    try:
        # Add user agent to avoid 403
        headers = {
            'User-Agent': 'WorldHeritageGuide/1.0 (https://worldheritage.guide; contact@worldheritage.guide)'
        }
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"  Failed to download from Wikimedia: {e}")
        return False

def download_satellite_image(lat, lon, output_path, zoom=16):
    """Download satellite image from Mapbox"""
    try:
        # Mapbox Static Images API
        url = f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/{lon},{lat},{zoom}/1200x800@2x"
        params = {'access_token': mapbox_token}

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"  Failed to download satellite: {e}")
        return False

def optimize_and_resize(input_path, output_dir, base_name):
    """Create multiple optimized sizes"""
    try:
        img = Image.open(input_path)

        # Convert to RGB if needed
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        # Create optimized versions
        output_dir.mkdir(parents=True, exist_ok=True)

        for width in IMAGE_SIZES:
            # Calculate height maintaining aspect ratio
            ratio = width / img.width
            height = int(img.height * ratio)

            # Resize
            resized = img.resize((width, height), Image.Resampling.LANCZOS)

            # Save as WebP
            output_path = output_dir / f'{base_name}-{width}w.webp'
            resized.save(output_path, 'WEBP', quality=85, method=6)

        return True
    except Exception as e:
        print(f"  Failed to optimize: {e}")
        return False

# Load test sites
with open(sites_file, 'r', encoding='utf-8') as f:
    sites = json.load(f)

print("Fetching images for test sites...")
print("=" * 60)

for idx, site in enumerate(sites, 1):
    name = site.get('name', 'Unknown')
    slug = generate_slug(name)
    wikidata_image = site.get('wikidata_image')
    coords = site.get('coordinates', [0, 0])

    print(f"{idx:2d}. {name[:45]:45s}", end=" ")

    # Create site image directory
    site_dir = images_dir / slug
    raw_dir = site_dir / 'raw'
    optimized_dir = site_dir / 'optimized'
    raw_dir.mkdir(parents=True, exist_ok=True)

    images_downloaded = 0

    # 1. Try Wikimedia Commons
    if wikidata_image:
        wikimedia_path = raw_dir / 'wikimedia-original.jpg'
        if download_wikimedia_image(wikidata_image, wikimedia_path):
            if optimize_and_resize(wikimedia_path, optimized_dir, 'wikimedia'):
                images_downloaded += 1
                print("[W]", end=" ")

    # 2. Get satellite image
    if coords and len(coords) == 2:
        satellite_path = site_dir / 'satellite-original.jpg'
        if download_satellite_image(coords[0], coords[1], satellite_path):
            if optimize_and_resize(satellite_path, optimized_dir, 'satellite'):
                images_downloaded += 1
                print("[S]", end=" ")

    # Save metadata
    metadata = {
        'site_name': name,
        'slug': slug,
        'wikidata_id': site.get('wikidata_id'),
        'images_count': images_downloaded,
        'has_wikimedia': (wikidata_image is not None) and (raw_dir / 'wikimedia-original.jpg').exists(),
        'has_satellite': (site_dir / 'satellite-original.jpg').exists()
    }

    with open(site_dir / 'metadata.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"({images_downloaded} images)")
    time.sleep(0.5)  # Be nice to APIs

print("=" * 60)
print("Image fetching complete!")
