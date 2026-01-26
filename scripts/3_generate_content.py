"""
PARALLEL Hugo Page Generator - 5x Faster
Uses async/concurrent API calls to OpenAI
"""

import os
import sys
import json
import time
import re
import argparse
import asyncio
import hashlib
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).parent.parent / '.env')

# ============================================
# CONFIGURATION
# ============================================

CONFIG = {
    'model': 'gpt-4o-mini',
    'temperature': 0.7,
    'max_tokens': 6000,
    'max_workers': 5,  # Parallel API calls (5x speed)
    'rate_limit_per_worker': 0.5,  # seconds between each worker's calls
}

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data' / 'raw'  # Changed from 'fetched' to 'raw' for proper metadata
CONTENT_DIR = BASE_DIR / 'content' / 'sites'
IMAGES_DIR = BASE_DIR / 'static' / 'images-sites'
PROGRESS_FILE = BASE_DIR / 'content_generation_progress.txt'

# ============================================
# UTILITIES
# ============================================

def get_wikimedia_thumb_url(filename: str, width: int = 1200) -> str:
    """Generate Wikimedia Commons thumbnail URL"""
    filename = filename.replace(' ', '_')
    md5 = hashlib.md5(filename.encode('utf-8')).hexdigest()
    base_url = f"https://upload.wikimedia.org/wikipedia/commons/thumb/{md5[0]}/{md5[0:2]}/{filename}/{width}px-{filename}"

    # Handle special formats
    if filename.lower().endswith('.svg'):
        base_url += '.png'
    elif filename.lower().endswith(('.tif', '.tiff')):
        base_url = base_url.replace(filename, filename + '.jpg')

    return base_url

def get_wikidata_images(wikidata_id: str) -> list:
    """Fetch image filenames from Wikidata"""
    if not wikidata_id:
        return []

    try:
        url = "https://www.wikidata.org/w/api.php"
        params = {
            'action': 'wbgetclaims',
            'entity': wikidata_id,
            'property': 'P18',  # image property
            'format': 'json'
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if 'claims' in data and 'P18' in data['claims']:
            images = []
            for claim in data['claims']['P18'][:5]:  # Max 5 images
                if 'mainsnak' in claim and 'datavalue' in claim['mainsnak']:
                    filename = claim['mainsnak']['datavalue']['value']
                    images.append(filename)
            return images
    except:
        pass

    return []

def generate_slug(title: str) -> str:
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

def log(message: str):
    timestamp = time.strftime('%H:%M:%S')
    print(f"[{timestamp}] {message}")
    sys.stdout.flush()

def write_progress(message: str):
    with open(PROGRESS_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

# ============================================
# PROMPT (Same quality as before)
# ============================================

def build_prompt(site: dict) -> str:
    title = site.get('title', site.get('name', 'Unknown'))
    description = site.get('description', '')
    category = site.get('category', site.get('heritage_type', 'heritage site'))
    category_info = site.get('category_info', {})
    heritage_type = category.replace('_', ' ').title()

    # Get region - prefer specific region over Germany
    region = site.get('region', 'Germany')
    if not region or region == 'Germany':
        region = 'Germany'

    # Extract coordinates from the coordinates field
    coords = site.get('coordinates', [])
    lat = coords[0] if len(coords) >= 2 else 'N/A'
    lon = coords[1] if len(coords) >= 2 else 'N/A'

    formatted_data = f"""=== BASIC INFORMATION ===
Name: {title}
Type: {heritage_type}
Region: {region}
Country: Germany
Description: {description}

=== LOCATION ===
Coordinates: {lat}, {lon}

=== CATEGORY INFO ===
Tags: {', '.join(category_info.get('category_tags', [category]))}
Category: {category_info.get('description', heritage_type)}"""

    prompt = f"""You are writing for WorldHeritage.guide, a premium heritage travel platform.

================================================================================
MISSION: Write a comprehensive and detailed guide to {title}
================================================================================

TARGET: 1500-2000 words
STYLE: National Geographic meets Lonely Planet - authoritative yet engaging

================================================================================
CRITICAL RULE #1: DATA INTEGRITY (MOST IMPORTANT)
================================================================================

You MUST follow these rules with ZERO exceptions:

1. ONLY use facts from the SITE DATA section below
2. If information is missing, write around it gracefully
3. NEVER invent dates, prices, hours, dimensions, names, or statistics
4. For missing info use: "Check the official website for current information"
5. NEVER mention specific geographic features not in the data
6. Use general language when specific facts are missing

================================================================================
CRITICAL RULE #2: FORBIDDEN PHRASES (AI CLICHÉS)
================================================================================

NEVER use: "nestled in", "boasts", "rich tapestry", "testament to", "stands as a beacon",
"jewel of", "journey through time", "step back in time", "hidden gem", "breathtaking views",
"feast for the senses", "where history comes alive", "steeped in history", "treasure trove"

================================================================================
SITE DATA - YOUR ONLY SOURCE OF FACTS
================================================================================

{formatted_data}

================================================================================
ARTICLE STRUCTURE (Use ## for headers)
================================================================================

## Overview (200-300 words)
Hook, geographic context, significance, promise.

## History and Significance (400-600 words)
Use general language if no dates. Cultural importance.

## Architecture and Features (300-500 words)
Physical description, notable features.

## Visiting Information (400-500 words)
Transport, "check official website for hours/prices", what to expect, time needed, best times.

## Nearby Attractions (200-300 words)
3-5 nearby places.

## Insider Tips (150-200 words)
Photography tips, crowd avoidance.

## Practical Information (200-250 words)
What to bring, seasonal considerations.

## Frequently Asked Questions (300-400 words)
8-10 FAQs with ### headers:
### How long should I spend visiting?
### Is photography allowed?
### Are there guided tours?
### What's the best time to visit?
### Is it wheelchair accessible?
### Can I buy tickets online?
### Are there restrooms and cafes?
### What should I wear?

Start with a compelling opening line."""

    return prompt


def generate_content(site: dict, client: OpenAI) -> tuple:
    """Generate content for a single site"""
    title = site.get('title', 'Unknown')
    slug = generate_slug(title)

    if not slug:
        return (slug, None, 'invalid_slug')

    # Check if already exists
    output_file = CONTENT_DIR / f'{slug}.md'
    if output_file.exists():
        return (slug, None, 'skipped')

    try:
        prompt = build_prompt(site)

        response = client.chat.completions.create(
            model=CONFIG['model'],
            messages=[
                {"role": "system", "content": "You are an expert travel writer creating factual, engaging heritage site guides. Never invent facts."},
                {"role": "user", "content": prompt}
            ],
            temperature=CONFIG['temperature'],
            max_tokens=CONFIG['max_tokens'],
        )

        content = response.choices[0].message.content

        # Create Hugo page
        description = site.get('description', '')[:150].replace('"', '\\"')
        category = site.get('category', 'heritage site').replace('_', ' ').title()

        # Extract coordinates from coordinates field
        coords = site.get('coordinates', [0, 0])
        lat = coords[0] if len(coords) >= 2 else 0
        lon = coords[1] if len(coords) >= 2 else 0

        # Try to get Wikimedia images
        images = []
        image_srcset = {}

        # First check if we have wikidata_image in the data (from Script 1)
        wikidata_image_url = site.get('wikidata_image', '')
        if wikidata_image_url:
            # Extract filename from Wikimedia Commons URL
            # Format: http://commons.wikimedia.org/wiki/Special:FilePath/Filename.jpg
            if 'FilePath/' in wikidata_image_url:
                filename = wikidata_image_url.split('FilePath/')[-1]
                # Decode URL encoding
                import urllib.parse
                filename = urllib.parse.unquote(filename)

                # Main image URL (1200px)
                main_url = get_wikimedia_thumb_url(filename, 1200)
                images.append(main_url)

                # Generate srcset for responsive images
                srcset_key = filename.replace(' ', '%20')
                image_srcset[srcset_key] = {
                    400: get_wikimedia_thumb_url(filename, 400),
                    800: get_wikimedia_thumb_url(filename, 800),
                    1200: get_wikimedia_thumb_url(filename, 1200),
                    1920: get_wikimedia_thumb_url(filename, 1920),
                }
        else:
            # Fallback: Query Wikidata API for images
            wikidata_id = site.get('wikidata_id', '')
            if wikidata_id:
                wiki_filenames = get_wikidata_images(wikidata_id)
                if wiki_filenames:
                    for filename in wiki_filenames[:5]:  # Max 5 images
                        # Main image URL (1200px)
                        main_url = get_wikimedia_thumb_url(filename, 1200)
                        images.append(main_url)

                        # Generate srcset for responsive images
                        srcset_key = filename.replace(' ', '%20')
                        image_srcset[srcset_key] = {
                            400: get_wikimedia_thumb_url(filename, 400),
                            800: get_wikimedia_thumb_url(filename, 800),
                            1200: get_wikimedia_thumb_url(filename, 1200),
                            1920: get_wikimedia_thumb_url(filename, 1920),
                        }

        # Fallback to local images if no Wikimedia images
        if not images:
            img_dir = IMAGES_DIR / slug
            if img_dir.exists():
                for img in sorted(img_dir.glob('*-800w.webp'))[:3]:
                    images.append(f'/images-sites/{slug}/{img.name}')

        # Generate YAML for images
        images_yaml = '\n'.join([f'  - {img}' for img in images]) if images else '  []'

        # Generate YAML for srcset
        srcset_yaml = ''
        if image_srcset:
            srcset_yaml = '\nimage_srcset:'
            for key, sizes in image_srcset.items():
                srcset_yaml += f'\n  {key}:'
                for size, url in sizes.items():
                    srcset_yaml += f'\n    {size}: {url}'

        # Extract metadata
        site_name = title
        region = site.get('region', 'Germany')
        wikidata_id = site.get('wikidata_id', '')
        is_unesco = site.get('unesco', False)

        # Build tags list
        tags = []
        if is_unesco:
            tags.append('unesco')
        tags_yaml = '\n'.join([f'  - {tag}' for tag in tags]) if tags else ''

        # Build regions list - use actual region if available
        regions_list = [region] if region and region != 'Germany' else ['Germany']
        regions_yaml = '\n'.join([f'  - "{r}"' for r in regions_list])

        md_content = f'''---
title: "{title.replace('"', '\\"')}"
site_name: "{site_name.replace('"', '\\"')}"
date: {time.strftime('%Y-%m-%d')}
draft: false
description: "{description}"
region: "{region}"
country: "Germany"
heritage_type: "{category}"
categories:
  - "{category}"
regions:
{regions_yaml}'''

        if wikidata_id:
            md_content += f'\nwikidata_id: "{wikidata_id}"'

        if tags_yaml:
            md_content += f'\ntags:\n{tags_yaml}'

        md_content += f'''
latitude: {lat}
longitude: {lon}
images:
{images_yaml}'''

        if srcset_yaml:
            md_content += srcset_yaml

        md_content += f'''
---

{content}
'''

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)

        time.sleep(CONFIG['rate_limit_per_worker'])
        return (slug, title, 'success')

    except Exception as e:
        return (slug, title, f'error: {str(e)[:50]}')


def load_all_sites() -> list:
    """Load sites from data/raw/sites.json (Script 1 output)"""
    sites_file = DATA_DIR / 'sites.json'

    if not sites_file.exists():
        log(f"ERROR: {sites_file} not found. Run script 1 first!")
        return []

    try:
        with open(sites_file, 'r', encoding='utf-8') as f:
            sites = json.load(f)
        log(f"Loaded {len(sites)} sites from {sites_file}")

        # Convert 'name' to 'title' for compatibility
        for site in sites:
            if 'name' in site and 'title' not in site:
                site['title'] = site['name']
            if 'heritage_type' in site and 'category' not in site:
                site['category'] = site['heritage_type']

        return sites
    except Exception as e:
        log(f"Error loading {sites_file}: {e}")
        return []


def get_existing_pages() -> set:
    existing = set()
    for md_file in CONTENT_DIR.glob('*.md'):
        if md_file.name != '_index.md':
            existing.add(md_file.stem)
    return existing


def main():
    parser = argparse.ArgumentParser(description='Parallel Hugo page generator')
    parser.add_argument('--test', type=int, help='Test mode: process only N sites')
    parser.add_argument('--workers', type=int, default=5, help='Number of parallel workers (default: 5)')
    args = parser.parse_args()

    if args.workers:
        CONFIG['max_workers'] = args.workers

    CONTENT_DIR.mkdir(parents=True, exist_ok=True)

    log("=" * 60)
    log("PARALLEL HUGO PAGE GENERATOR")
    log(f"Workers: {CONFIG['max_workers']} (5x faster)")
    log("=" * 60)

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        log("ERROR: OPENAI_API_KEY not found")
        return

    client = OpenAI(api_key=api_key)
    log(f"OpenAI client ready (model: {CONFIG['model']})")

    # Load sites
    sites = load_all_sites()
    log(f"Loaded {len(sites)} total sites")

    # Filter existing
    existing = get_existing_pages()
    log(f"Existing pages: {len(existing)}")

    sites_to_process = [s for s in sites if generate_slug(s.get('title', '')) not in existing]
    log(f"New sites to process: {len(sites_to_process)}")

    if args.test:
        sites_to_process = sites_to_process[:args.test]
        log(f"Test mode: {len(sites_to_process)} sites")

    if not sites_to_process:
        log("No new sites to process!")
        return

    write_progress(f"PARALLEL START: {len(sites_to_process)} sites, {CONFIG['max_workers']} workers")

    # Process with thread pool
    stats = {'success': 0, 'skipped': 0, 'error': 0}
    start_time = time.time()
    completed = 0

    with ThreadPoolExecutor(max_workers=CONFIG['max_workers']) as executor:
        futures = {executor.submit(generate_content, site, client): site for site in sites_to_process}

        for future in as_completed(futures):
            completed += 1
            slug, title, status = future.result()

            if status == 'success':
                stats['success'] += 1
            elif status == 'skipped':
                stats['skipped'] += 1
            else:
                stats['error'] += 1

            # Progress
            elapsed = time.time() - start_time
            rate = completed / elapsed if elapsed > 0 else 0
            eta = (len(sites_to_process) - completed) / rate if rate > 0 else 0

            icon = '+' if status == 'success' else ('>' if status == 'skipped' else 'X')

            if sys.stdout.isatty():
                print(f"\r[{completed}/{len(sites_to_process)}] {icon} {slug[:30]:<30} OK:{stats['success']} ETA:{int(eta//60)}m", end='', flush=True)
            elif completed % 25 == 0:
                print(f"[{completed}/{len(sites_to_process)}] OK:{stats['success']} Skip:{stats['skipped']} Err:{stats['error']} ETA:{int(eta//60)}m")

            if completed % 100 == 0:
                write_progress(f"Progress: {completed}/{len(sites_to_process)} - OK:{stats['success']}")

    print()
    elapsed = time.time() - start_time

    log("")
    log("=" * 60)
    log("SUMMARY")
    log("=" * 60)
    log(f"Total: {completed}")
    log(f"Success: {stats['success']}")
    log(f"Skipped: {stats['skipped']}")
    log(f"Errors: {stats['error']}")
    log(f"Time: {int(elapsed//60)}m {int(elapsed%60)}s")
    log(f"Speed: {completed/elapsed*60:.1f} pages/minute")
    log(f"Cost: ~${stats['success'] * 0.002:.2f}")

    write_progress(f"COMPLETE - OK:{stats['success']} Err:{stats['error']} Time:{int(elapsed//60)}m")


if __name__ == '__main__':
    main()
