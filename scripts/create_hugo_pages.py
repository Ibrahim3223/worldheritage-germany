"""
Quick Hugo Page Generator
Creates Hugo markdown files for test
Copies images from data/images to static/images for Hugo
"""

import json
import shutil
from pathlib import Path

# Paths
content_dir = Path(__file__).parent.parent / 'data/content'
sites_file = Path(__file__).parent.parent / 'data/raw/sites.json'
images_dir = Path(__file__).parent.parent / 'data/images'
hugo_dir = Path(__file__).parent.parent / 'content/sites'
static_images_dir = Path(__file__).parent.parent / 'static/images'

hugo_dir.mkdir(parents=True, exist_ok=True)
static_images_dir.mkdir(parents=True, exist_ok=True)

# Load sites with UTF-8 encoding
with open(sites_file, encoding='utf-8') as f:
    sites = json.load(f)

print("Creating Hugo pages...")
print("=" * 60)

# Create Hugo markdown for each site
created = 0

for content_file in sorted(content_dir.glob('*.json')):
    with open(content_file, encoding='utf-8') as f:
        content = json.load(f)

    wid = content['wikidata_id']
    site = next((s for s in sites if s.get('wikidata_id') == wid), None)
    if not site:
        print(f"Skipped: {wid} (site data not found)")
        continue

    slug = content['site_slug']
    name = site.get('name', 'Unknown')
    region = site.get('region', 'Germany')

    # Get images and copy to static/images (prioritize Wikimedia, then Satellite)
    img_dir = images_dir / slug / 'optimized'
    img_paths = []

    if img_dir.exists():
        dest_dir = static_images_dir / slug
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Priority 1: Wikimedia images (real photos)
        wikimedia_imgs = sorted(img_dir.glob('wikimedia-*.webp'))
        for img in wikimedia_imgs:
            if '1920w' in img.name:  # Use largest size
                dest_file = dest_dir / img.name
                if not dest_file.exists():
                    shutil.copy2(img, dest_file)
                img_paths.append(f'/images/{slug}/{img.name}')

        # Priority 2: Satellite images (fallback)
        satellite_imgs = sorted(img_dir.glob('satellite-*.webp'))
        for img in satellite_imgs:
            if '1920w' in img.name:  # Use largest size
                dest_file = dest_dir / img.name
                if not dest_file.exists():
                    shutil.copy2(img, dest_file)
                img_paths.append(f'/images/{slug}/{img.name}')

    # Build content body
    sections = content['content']
    body_parts = []
    for key, text in sections.items():
        # Skip adding heading for "full_article" - content already has headers
        if key != 'full_article':
            heading = key.replace('_', ' ').title()
            body_parts.append(f'## {heading}')
        body_parts.append(text)
        body_parts.append('')

    body = '\n'.join(body_parts)

    # Get coordinates
    coords = site.get('coordinates', [0, 0])
    lat = coords[0] if coords and len(coords) > 0 else 0
    lon = coords[1] if coords and len(coords) > 1 else 0

    # Create markdown frontmatter and content
    desc = site.get('description', '')[:150].replace('"', '\\"')

    # Format images array for YAML
    images_yaml = '\n'.join([f'  - "{path}"' for path in img_paths]) if img_paths else '  []'

    # Prepare taxonomies (Hugo plural format)
    heritage_type = site.get('heritage_type', '').strip()
    categories_yaml = f'\n  - "{heritage_type}"' if heritage_type else ''

    regions_yaml = f'\n  - "{region}"' if region else ''

    tags_yaml = ''
    if site.get('unesco'):
        tags_yaml = '\n  - "unesco"'

    # Visit information
    opening_hours = site.get('opening_hours', '')
    entry_fee = site.get('entry_fee', '')
    website = site.get('official_website', '')

    md = f'''---
title: "{name}"
site_name: "{name}"
date: 2026-01-11
draft: false
wikidata_id: "{wid}"
description: "{desc}"

# Display fields (for templates)
region: "{region}"
country: "Germany"
heritage_type: "{heritage_type}"

# Taxonomies (Hugo plural format)
categories:{categories_yaml}
regions:{regions_yaml}
tags:{tags_yaml}

# Location
latitude: {lat}
longitude: {lon}

# Visit Information'''

    if opening_hours:
        md += f'\nopening_hours: "{opening_hours}"'
    if entry_fee:
        md += f'\nentry_fee: "{entry_fee}"'
    if website:
        md += f'\nwebsite: "{website}"'

    md += f'''

# Images
images:
{images_yaml}
---

{body}
'''

    # Save
    outfile = hugo_dir / f'{slug}.md'
    with open(outfile, 'w', encoding='utf-8') as f:
        f.write(md)

    created += 1
    print(f'{created:2d}. {name[:40]:40s} -> {outfile.name}')

print("=" * 60)
print(f'Total Hugo pages created: {created}')
print(f'Output directory: {hugo_dir}')
