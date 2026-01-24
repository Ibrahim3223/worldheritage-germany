#!/usr/bin/env python3
"""
MASTER PAGE CREATOR
Creates high-quality markdown pages with GPT enhancement and image downloading
Reads from master_fetch_sites.py output

Usage:
    python create_pages_master.py Germany
    python create_pages_master.py Germany --with-gpt
    python create_pages_master.py Germany --skip-images
"""

import json
import re
import argparse
import time
from pathlib import Path
from typing import Dict, List, Optional
import requests

# Optional: OpenAI for content enhancement
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("[INFO] OpenAI not available. Install with: pip install openai")

DATA_DIR = Path("data/fetched")
CONTENT_DIR = Path("content/sites")
IMAGES_DIR = Path("static/images-sites")

CONTENT_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def slugify(text):
    """Convert text to URL-friendly slug"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

def escape_quotes(text):
    """Escape quotes for YAML"""
    return text.replace('"', '\\"')

# ============================================================================
# GPT CONTENT ENHANCEMENT
# ============================================================================

def enhance_content_with_gpt(site_data: Dict, api_key: str) -> str:
    """
    Use GPT to create rich, engaging content

    Args:
        site_data: Site information from Wikidata
        api_key: OpenAI API key

    Returns:
        Enhanced markdown content
    """
    if not HAS_OPENAI:
        return generate_basic_content(site_data)

    try:
        openai.api_key = api_key

        prompt = f"""Create engaging, informative content for a heritage site page.

Site Information:
- Name: {site_data['title']}
- Type: {site_data['category']}
- Description: {site_data.get('description', 'N/A')}
- Country: Germany

Requirements:
- Write 2-3 paragraphs (150-200 words total)
- Focus on history, architecture, and visitor experience
- Be informative but engaging
- Use markdown formatting (headers, bold, lists)
- Include sections: ## Overview, ## History, ## Visiting

Do NOT include the site name as a title (it's already in frontmatter)."""

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # or gpt-3.5-turbo for cost savings
            messages=[
                {"role": "system", "content": "You are a travel writer specializing in cultural heritage sites."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.7
        )

        content = response['choices'][0]['message']['content'].strip()
        return content

    except Exception as e:
        print(f"    [WARN] GPT enhancement failed: {e}")
        return generate_basic_content(site_data)

def generate_basic_content(site_data: Dict) -> str:
    """Generate basic content without GPT"""
    category = site_data.get('category', 'site')
    description = site_data.get('description', '')

    content = f"""## Overview

{site_data['title']} is a {category.replace('_', ' ')} in Germany."""

    if description:
        content += f" {description}"

    content += """

## Visiting

Please check local regulations and visiting hours before planning your visit.
"""

    return content

# ============================================================================
# IMAGE DOWNLOADING
# ============================================================================

def download_image_from_commons(image_url: str, save_path: Path) -> bool:
    """
    Download image from Wikimedia Commons

    Args:
        image_url: Wikimedia Commons image URL
        save_path: Where to save the image

    Returns:
        Success boolean
    """
    try:
        # Get direct image URL from Commons
        # image_url format: http://commons.wikimedia.org/wiki/Special:FilePath/...
        # We want the actual file URL

        headers = {
            "User-Agent": "WorldHeritageBot/2.0 (https://worldheritage.guide)"
        }

        response = requests.get(image_url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()

        # Save image
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return True

    except Exception as e:
        print(f"    [WARN] Image download failed: {e}")
        return False

def process_images(site_data: Dict, slug: str, skip_images: bool = False) -> List[str]:
    """
    Download and process images for a site

    Args:
        site_data: Site information
        slug: Site slug for directory naming
        skip_images: Skip image downloading

    Returns:
        List of image paths
    """
    if skip_images or not site_data.get('has_image'):
        return []

    site_image_dir = IMAGES_DIR / slug
    site_image_dir.mkdir(parents=True, exist_ok=True)

    images = []

    # Download main image if available
    if 'image_url' in site_data:
        image_path = site_image_dir / "01-wikimedia-1920w.webp"

        if not image_path.exists():
            if download_image_from_commons(site_data['image_url'], image_path):
                images.append(f"/images-sites/{slug}/01-wikimedia-1920w.webp")

    # Check for existing images in directory
    for img in sorted(site_image_dir.glob("*.webp")):
        img_path = f"/images-sites/{slug}/{img.name}"
        if img_path not in images:
            images.append(img_path)

    return images

# ============================================================================
# PAGE CREATION
# ============================================================================

def create_page(site_data: Dict, country: str, use_gpt: bool = False,
                gpt_api_key: Optional[str] = None, skip_images: bool = False) -> bool:
    """
    Create a markdown page for a site

    Args:
        site_data: Site information from Wikidata
        country: Country name
        use_gpt: Use GPT for content enhancement
        gpt_api_key: OpenAI API key (required if use_gpt=True)
        skip_images: Skip image downloading

    Returns:
        Success boolean
    """
    slug = slugify(site_data['title'])
    md_file = CONTENT_DIR / f"{slug}.md"

    # Skip if already exists
    if md_file.exists():
        return False

    # Escape quotes for YAML
    title_escaped = escape_quotes(site_data['title'])
    desc_escaped = escape_quotes(site_data.get('description', ''))

    # Build frontmatter
    frontmatter = f"""---
title: "{title_escaped}"
site_name: "{title_escaped}"
slug: "{slug}"
draft: false
region: "{country}"

# Location"""

    # Add coordinates
    if site_data.get('has_coordinates'):
        frontmatter += f"""
latitude: {site_data['latitude']}
longitude: {site_data['longitude']}"""

    # Add categories
    frontmatter += """

# Classification
regions:
    - "{country}"
heritage_type: "{heritage_type}"
categories:"""

    category_tags = site_data['category_info']['category_tags']
    for tag in category_tags:
        frontmatter += f'\n  - "{tag}"'

    # Add metadata
    frontmatter += f"""

# Metadata
wikidata_id: "{site_data['wikidata_id']}"
description: "{desc_escaped}"
sitelinks: {site_data.get('sitelinks', 0)}"""

    # Process images
    images = process_images(site_data, slug, skip_images)

    if images:
        frontmatter += "\n\n# Images\nimages:"
        for img in images:
            frontmatter += f'\n  - "{img}"'

    frontmatter += "\n---\n"

    # Generate content
    if use_gpt and gpt_api_key:
        content = enhance_content_with_gpt(site_data, gpt_api_key)
    else:
        content = generate_basic_content(site_data)

    # Write file
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(frontmatter)
        f.write("\n")
        f.write(content)

    return True

# ============================================================================
# MASTER PROCESSOR
# ============================================================================

def process_all_categories(country: str, use_gpt: bool = False,
                           gpt_api_key: Optional[str] = None,
                           skip_images: bool = False):
    """
    Process all fetched categories and create pages

    Args:
        country: Country name
        use_gpt: Use GPT for content enhancement
        gpt_api_key: OpenAI API key
        skip_images: Skip image downloading
    """
    print("=" * 80)
    print(f"MASTER PAGE CREATOR - {country}")
    print("=" * 80)
    print(f"GPT Enhancement: {'Enabled' if use_gpt else 'Disabled'}")
    print(f"Image Downloading: {'Disabled' if skip_images else 'Enabled'}")
    print()

    # Find all JSON files for this country
    pattern = f"{country.lower()}_*.json"
    json_files = sorted(DATA_DIR.glob(pattern))

    if not json_files:
        print(f"[ERROR] No data files found for {country}")
        print(f"Expected pattern: {DATA_DIR}/{pattern}")
        return

    print(f"Found {len(json_files)} category files\n")

    total_created = 0
    total_skipped = 0

    for json_file in json_files:
        category_name = json_file.stem.replace(f"{country.lower()}_", "")

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                sites = json.load(f)

            print(f"Processing: {category_name} ({len(sites)} sites)")

            created = 0
            for site in sites:
                if create_page(site, country, use_gpt, gpt_api_key, skip_images):
                    created += 1
                else:
                    total_skipped += 1

                # Rate limiting for GPT API
                if use_gpt and created > 0 and created % 10 == 0:
                    time.sleep(1)

            total_created += created
            print(f"  Created: {created}, Skipped: {len(sites) - created}")

        except Exception as e:
            print(f"  [ERROR] Failed to process {json_file.name}: {e}")
            continue

    print(f"\n{'='*80}")
    print("PAGE CREATION COMPLETE")
    print(f"{'='*80}")
    print(f"Total pages created: {total_created:,}")
    print(f"Total pages skipped: {total_skipped:,}")

# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Master page creator with GPT enhancement')
    parser.add_argument('country', help='Country name (e.g., Germany)')
    parser.add_argument('--with-gpt', action='store_true', help='Use GPT for content enhancement')
    parser.add_argument('--gpt-key', help='OpenAI API key (or set OPENAI_API_KEY env var)')
    parser.add_argument('--skip-images', action='store_true', help='Skip image downloading')

    args = parser.parse_args()

    # Get API key
    gpt_api_key = args.gpt_key or os.getenv('OPENAI_API_KEY')

    if args.with_gpt and not gpt_api_key:
        print("[ERROR] GPT enhancement requires API key")
        print("Provide via --gpt-key or OPENAI_API_KEY environment variable")
        return

    process_all_categories(
        args.country,
        use_gpt=args.with_gpt,
        gpt_api_key=gpt_api_key,
        skip_images=args.skip_images
    )

if __name__ == "__main__":
    main()
