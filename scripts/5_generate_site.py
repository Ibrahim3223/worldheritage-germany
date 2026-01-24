"""
Script 5: Generate Hugo Site
Creates Hugo markdown files from approved content
Copies images to static/images for Hugo
"""

import re
import shutil
from pathlib import Path
from typing import Dict, List
from tqdm import tqdm

# Handle imports for both package and direct execution
try:
    from .config import (
        PROJECT, PATHS, SEO_CONFIG, IMAGE_CONFIG
    )
    from .utils import (
        load_json, save_json, generate_slug, logger
    )
except ImportError:
    from config import (
        PROJECT, PATHS, SEO_CONFIG, IMAGE_CONFIG
    )
    from utils import (
        load_json, save_json, generate_slug, logger
    )

# ============================================
# SEO METADATA
# ============================================

def generate_seo_title(site: Dict) -> str:
    """
    Generate SEO-optimized title

    Args:
        site: Site data

    Returns:
        Title string (50-60 chars)
    """

    template = SEO_CONFIG['title_template']

    title = template.format(
        site_name=site['name'],
        category=site.get('heritage_type', 'Heritage Site'),
        region=site.get('region', PROJECT['country'])
    )

    # Truncate if too long
    max_len = SEO_CONFIG['title_length'][1]
    if len(title) > max_len:
        title = title[:max_len-3] + '...'

    return title

def generate_seo_description(site: Dict, content: str) -> str:
    """
    Generate SEO meta description

    Args:
        site: Site data
        content: Article content

    Returns:
        Description string (150-160 chars)
    """

    # Try to use first 2 sentences
    sentences = re.split(r'[.!?]+', content)
    sentences = [s.strip() for s in sentences if s.strip()]

    if len(sentences) >= 2:
        desc = '. '.join(sentences[:2]) + '.'
    elif sentences:
        desc = sentences[0] + '.'
    else:
        # Fallback to template
        template = SEO_CONFIG['description_template']
        desc = template.format(
            site_name=site['name'],
            region=site.get('region', ''),
            country=site.get('country', PROJECT['country']),
            key_info=site.get('heritage_type', 'heritage site')
        )

    # Truncate to max length
    max_len = SEO_CONFIG['description_length'][1]
    if len(desc) > max_len:
        desc = desc[:max_len-3] + '...'

    return desc

def generate_keywords(site: Dict) -> List[str]:
    """Generate SEO keywords"""

    keywords = [
        site['name'],
        site.get('heritage_type', ''),
        site.get('region', ''),
        site.get('country', ''),
    ]

    # Add style, period if available
    if site.get('style'):
        keywords.append(site['style'])
    if site.get('period'):
        keywords.append(site['period'])
    if site.get('unesco'):
        keywords.append('UNESCO World Heritage')

    # Remove empty and duplicates
    keywords = list(set([k.strip() for k in keywords if k]))

    return keywords

# ============================================
# HUGO FRONTMATTER
# ============================================

def generate_frontmatter(site: Dict, content_data: Dict, image_metadata: Dict = None) -> str:
    """
    Generate Hugo frontmatter (YAML)

    Args:
        site: Site data
        content_data: Generated content
        image_metadata: Image metadata (if exists)

    Returns:
        YAML frontmatter string
    """

    slug = generate_slug(site['name'])

    # SEO
    title = generate_seo_title(site)
    description = generate_seo_description(site, content_data['content'])
    keywords = generate_keywords(site)

    # Escape quotes in title and description for YAML
    title = title.replace('"', '\\"')
    description = description.replace('"', '\\"')

    # Images
    images = []
    if image_metadata and image_metadata.get('images'):
        for img in image_metadata['images'][:5]:  # Max 5 for frontmatter
            if img.get('srcset') and '1024w' in img['srcset']:
                # Fix Windows backslashes to forward slashes for web URLs
                img_path = img['srcset']['1024w'].replace('\\', '/')
                images.append('/images-sites/' + img_path)

    # Build frontmatter
    fm = f"""---
title: "{title}"
description: "{description}"
date: {content_data['generated_at']}
draft: false

# Site Info
site_name: "{site['name']}"
slug: "{slug}"
wikidata_id: "{site['wikidata_id']}"
country: "{site.get('country', PROJECT['country'])}"

# Coordinates
latitude: {site['coordinates'][0]}
longitude: {site['coordinates'][1]}

# Taxonomies (Hugo plural format)
"""

    # Categories (from heritage_type)
    heritage_type = site.get('heritage_type', '').strip()
    if heritage_type:
        # Normalize heritage type (lowercase, hyphenated for URL)
        fm += f"categories:\n  - \"{heritage_type}\"\n"

    # Regions (from region)
    region = site.get('region', '').strip()
    if region:
        fm += f"regions:\n  - \"{region}\"\n"

    # Tags (UNESCO and other tags)
    tags = []
    if site.get('unesco'):
        tags.append('unesco')
    if tags:
        fm += f"tags:\n"
        for tag in tags:
            fm += f"  - \"{tag}\"\n"

    # UNESCO criteria (if exists)
    if site.get('unesco_criteria'):
        fm += f'unesco_criteria: "{site["unesco_criteria"]}"\n'

    # Visit info (if exists)
    if site.get('opening_hours'):
        fm += f'opening_hours: "{site["opening_hours"]}"\n'
    if site.get('entry_fee'):
        fm += f'entry_fee: "{site["entry_fee"]}"\n'
    if site.get('official_website'):
        fm += f'website: "{site["official_website"]}"\n'

    # Images
    if images:
        fm += "\nimages:\n"
        for img in images:
            fm += f"  - {img}\n"

    # Keywords
    if keywords:
        fm += "\nkeywords:\n"
        for kw in keywords[:10]:  # Max 10
            fm += f"  - {kw}\n"

    # Quality metadata
    fm += f"""
# Quality
word_count: {content_data['word_count']}
quality_score: {content_data.get('validation', {}).get('quality_score', 0)}
completeness_score: {content_data['completeness_score']}
"""

    fm += "---\n\n"

    return fm

# ============================================
# HUGO MARKDOWN GENERATION
# ============================================

def generate_hugo_markdown(site: Dict, content_data: Dict,
                           image_metadata: Dict = None) -> str:
    """
    Generate complete Hugo markdown file

    Args:
        site: Site data
        content_data: Generated content
        image_metadata: Image metadata

    Returns:
        Complete markdown content
    """

    # Frontmatter
    markdown = generate_frontmatter(site, content_data, image_metadata)

    # Article content
    markdown += content_data['content']

    # Add image gallery (if images exist)
    if image_metadata and image_metadata.get('images'):
        markdown += "\n\n## Photo Gallery\n\n"

        for i, img in enumerate(image_metadata['images'], 1):
            if img.get('srcset'):
                # Use Hugo shortcode for responsive images
                srcset_1024 = img['srcset'].get('1024w', '').replace('\\', '/')
                alt_text = img.get('alt_text', f"{site['name']} - Image {i}")

                markdown += f"![{alt_text}](/images-sites/{srcset_1024})\n\n"

                if img.get('photographer') and img['photographer'] != 'Unknown':
                    markdown += f"*Photo: {img['photographer']}*\n\n"

    # Add map section
    markdown += f"""
## Location Map

{{{{< map latitude="{site['coordinates'][0]}" longitude="{site['coordinates'][1]}" >}}}}

**Coordinates:** {site['coordinates'][0]}, {site['coordinates'][1]}

[Get Directions on Google Maps](https://www.google.com/maps/dir/?api=1&destination={site['coordinates'][0]},{site['coordinates'][1]})
"""

    return markdown

# ============================================
# MAIN EXECUTION
# ============================================

def main():
    """Main execution"""

    logger.info("="*60)
    logger.info("SCRIPT 5: GENERATE HUGO SITE")
    logger.info("="*60)
    logger.info("")

    # Load sites data
    sites_file = PATHS['raw'] / 'sites.json'
    if not sites_file.exists():
        logger.error("Sites file not found.")
        return

    sites = load_json(sites_file)
    sites_dict = {s['wikidata_id']: s for s in sites}

    # Load validated content
    content_files = list(PATHS['content'].glob('*.json'))

    if not content_files:
        logger.error("No content files found.")
        return

    logger.info(f"Processing {len(content_files)} articles...")
    logger.info("")

    # Create Hugo content directory
    hugo_content_dir = PATHS['hugo_content']
    hugo_content_dir.mkdir(parents=True, exist_ok=True)

    # Create static images directory (images-sites to match config)
    static_images_dir = PATHS['hugo_content'].parent / 'static' / 'images-sites'
    static_images_dir.mkdir(parents=True, exist_ok=True)

    # Process each article
    generated = 0
    skipped = 0
    images_copied = 0

    for content_file in tqdm(content_files, desc="Generating Hugo files"):
        try:
            content_data = load_json(content_file)
            wikidata_id = content_data['wikidata_id']

            # Check quality score (skip only if very low quality)
            quality_score = content_data.get('validation', {}).get('quality_score', 50)
            if quality_score < 40:
                skipped += 1
                logger.debug(f"Skipped (quality too low: {quality_score}): {content_data['site_name']}")
                continue

            if wikidata_id not in sites_dict:
                logger.warning(f"Site data not found for {content_file.name}")
                continue

            site_data = sites_dict[wikidata_id]
            slug = content_data['site_slug']

            # Copy images from data/images/slug/optimized to static/images
            source_img_dir = PATHS['images'] / slug / 'optimized'
            if source_img_dir.exists():
                dest_img_dir = static_images_dir / slug
                dest_img_dir.mkdir(parents=True, exist_ok=True)
                for img_file in source_img_dir.glob('*.webp'):
                    dest_file = dest_img_dir / img_file.name
                    if not dest_file.exists():
                        shutil.copy2(img_file, dest_file)
                        images_copied += 1

            # Load image metadata (if exists)
            image_meta_file = PATHS['images'] / slug / 'metadata.json'
            image_metadata = None
            if image_meta_file.exists():
                image_metadata = load_json(image_meta_file)

            # Generate markdown
            markdown = generate_hugo_markdown(site_data, content_data, image_metadata)

            # Save Hugo file
            # Structure: content/region/site-slug.md
            region = generate_slug(site_data.get('region', 'other'))
            region_dir = hugo_content_dir / region
            region_dir.mkdir(parents=True, exist_ok=True)

            hugo_file = region_dir / f"{slug}.md"

            with open(hugo_file, 'w', encoding='utf-8') as f:
                f.write(markdown)

            generated += 1

        except Exception as e:
            logger.error(f"Failed to generate Hugo file for {content_file.name}: {e}")
            skipped += 1

    # Summary
    logger.info("")
    logger.info("="*60)
    logger.info("HUGO GENERATION SUMMARY")
    logger.info("="*60)
    logger.info(f"Total content files: {len(content_files)}")
    logger.info(f"Hugo files generated: {generated}")
    logger.info(f"Images copied: {images_copied}")
    logger.info(f"Skipped: {skipped}")
    logger.info("")
    logger.info(f"Content directory: {hugo_content_dir}")
    logger.info(f"Images directory: {static_images_dir}")
    logger.info("")
    logger.info("Script 5 complete!")
    logger.info("")
    logger.info("Next: Run 'hugo server' to preview the site")

if __name__ == '__main__':
    main()
