"""
Update Hugo pages with GPT-generated content
Replaces placeholder content with actual GPT-generated articles
"""

import json
import shutil
from pathlib import Path

# Paths
base_dir = Path(__file__).parent.parent
content_dir = base_dir / 'data/content'
sites_file = base_dir / 'data/raw/sites_test.json'
images_dir = base_dir / 'data/images'
hugo_dir = base_dir / 'content/sites'
static_images_dir = base_dir / 'static/images'

# Load sites with UTF-8 encoding
with open(sites_file, encoding='utf-8') as f:
    sites = json.load(f)

print("Updating Hugo pages with GPT content...")
print("=" * 60)

# Delete old Hugo pages
if hugo_dir.exists():
    shutil.rmtree(hugo_dir)
hugo_dir.mkdir(parents=True, exist_ok=True)

static_images_dir.mkdir(parents=True, exist_ok=True)

updated = 0

for content_file in sorted(content_dir.glob('*.json')):
    with open(content_file, encoding='utf-8') as f:
        content_data = json.load(f)

    wid = content_data['wikidata_id']
    site = next((s for s in sites if s.get('wikidata_id') == wid), None)
    if not site:
        print(f"Skipped: {wid} (site data not found)")
        continue

    slug = content_data['site_slug']
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

    # Get the GPT-generated content
    gpt_content = content_data['content']['full_article']

    # Get coordinates
    coords = site.get('coordinates', [0, 0])
    lat = coords[0] if coords and len(coords) > 0 else 0
    lon = coords[1] if coords and len(coords) > 1 else 0

    # Create markdown frontmatter and content
    desc = site.get('description', '')[:150].replace('"', '\\"')

    # Format images array for YAML
    images_yaml = '\n'.join([f'  - "{path}"' for path in img_paths]) if img_paths else '  []'

    md = f'''---
title: "{name}"
site_name: "{name}"
date: 2026-01-11
draft: false
region: "{region}"
heritage_type: "{site.get('heritage_type', 'site')}"
unesco: {str(site.get('unesco', False)).lower()}
wikidata_id: "{wid}"
description: "{desc}"
images:
{images_yaml}
latitude: {lat}
longitude: {lon}
---

{gpt_content}
'''

    # Save
    outfile = hugo_dir / f'{slug}.md'
    with open(outfile, 'w', encoding='utf-8') as f:
        f.write(md)

    word_count = content_data['word_count']
    updated += 1
    print(f'{updated:2d}. {name[:35]:35s} -> {outfile.name:40s} [{word_count} words]')

print("=" * 60)
print(f'Total Hugo pages updated: {updated}')
print(f'Output directory: {hugo_dir}')
print("\nPages now have GPT-generated content!")
