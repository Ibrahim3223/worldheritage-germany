"""
Test version: Add images to just 10 sites to verify the approach works
"""

import os
import re
import sys
import time
import yaml
import requests
from pathlib import Path
from typing import List

# Unbuffer output
sys.stdout.reconfigure(line_buffering=True)

# Wikidata SPARQL endpoint
SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

def get_images_from_wikidata(wikidata_id: str, limit: int = 8, max_retries: int = 3) -> List[str]:
    """
    Fetch image URLs from Wikidata using SPARQL

    Args:
        wikidata_id: Wikidata ID (e.g., "Q5908")
        limit: Maximum number of images to fetch
        max_retries: Maximum number of retry attempts

    Returns:
        List of image URLs
    """
    query = f"""
    SELECT DISTINCT ?image WHERE {{
      wd:{wikidata_id} wdt:P18 ?image.
    }}
    LIMIT {limit}
    """

    headers = {
        'User-Agent': 'WorldHeritageBot/1.0 (https://worldheritage.guide)',
        'Accept': 'application/json'
    }

    for attempt in range(max_retries):
        try:
            response = requests.get(
                SPARQL_ENDPOINT,
                params={'query': query, 'format': 'json'},
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            images = []
            for result in data.get('results', {}).get('bindings', []):
                image_url = result.get('image', {}).get('value', '')
                if image_url:
                    images.append(image_url)

            return images
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                # Rate limited - wait longer before retry
                wait_time = (attempt + 1) * 5
                print(f"[!] Rate limited on {wikidata_id}, waiting {wait_time}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                print(f"[!] HTTP Error fetching images for {wikidata_id}: {e}")
                return []
        except Exception as e:
            print(f"[!] Error fetching images for {wikidata_id}: {e}")
            return []

    print(f"[!] Failed to fetch images for {wikidata_id} after {max_retries} attempts")
    return []


def update_markdown_images(file_path: Path, new_images: List[str]) -> bool:
    """
    Update images array in markdown frontmatter
    Keeps existing image, adds new ones

    Args:
        file_path: Path to markdown file
        new_images: List of new image URLs to add

    Returns:
        True if updated successfully
    """
    try:
        content = file_path.read_text(encoding='utf-8')

        # Extract frontmatter
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
        if not match:
            print(f"[!] No frontmatter found in {file_path.name}")
            return False

        frontmatter_text = match.group(1)
        body = match.group(2)

        # Parse frontmatter
        frontmatter = yaml.safe_load(frontmatter_text)

        # Get existing images
        existing_images = frontmatter.get('images', [])

        # Combine: keep first existing image, add new ones
        combined_images = []
        if existing_images:
            combined_images.append(existing_images[0])  # Keep first image

        # Add new images (avoid duplicates)
        for img in new_images:
            if img not in combined_images:
                combined_images.append(img)

        # Limit to 8 images total
        combined_images = combined_images[:8]

        # Only update if we added new images
        if len(combined_images) <= len(existing_images):
            return False

        # Update frontmatter
        frontmatter['images'] = combined_images

        # Write back
        new_frontmatter = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)
        new_content = f"---\n{new_frontmatter}---\n\n{body}"

        file_path.write_text(new_content, encoding='utf-8')
        return True

    except Exception as e:
        print(f"[!] Error updating {file_path.name}: {e}")
        return False


def main():
    """Process just 10 site markdown files for testing"""

    sites_dir = Path('content/sites')

    if not sites_dir.exists():
        print(f"[!] Sites directory not found: {sites_dir}")
        return

    # Get all markdown files
    md_files = list(sites_dir.glob('*.md'))
    md_files = [f for f in md_files if f.name != '_index.md']

    # Only process first 10 files for testing
    test_files = md_files[:10]

    print(f"[*] Testing with {len(test_files)} site files")
    print(f"[*] Starting to fetch and add images...")
    print()

    updated_count = 0
    skipped_count = 0
    error_count = 0

    for i, file_path in enumerate(test_files, 1):
        # Read wikidata_id from frontmatter
        try:
            content = file_path.read_text(encoding='utf-8')
            match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if not match:
                skipped_count += 1
                continue

            fm = yaml.safe_load(match.group(1))
            wikidata_id = fm.get('wikidata_id')
            site_name = fm.get('site_name', file_path.stem)

            if not wikidata_id:
                print(f"[{i}/{len(test_files)}] Skipped: {site_name} (no wikidata_id)")
                skipped_count += 1
                continue

            # Fetch images from Wikidata
            print(f"[{i}/{len(test_files)}] Fetching images for: {site_name} ({wikidata_id})...")
            new_images = get_images_from_wikidata(wikidata_id, limit=8)

            if new_images:
                # Update markdown file
                if update_markdown_images(file_path, new_images):
                    updated_count += 1
                    print(f"[{i}/{len(test_files)}] ✓ Updated: {site_name} (+{len(new_images)} images)")
                else:
                    skipped_count += 1
                    print(f"[{i}/{len(test_files)}] - Skipped: {site_name} (no new images)")
            else:
                skipped_count += 1
                print(f"[{i}/{len(test_files)}] - Skipped: {site_name} (no images found)")

            # Rate limiting - be respectful to Wikidata
            time.sleep(2.0)

        except Exception as e:
            print(f"[!] Error processing {file_path.name}: {e}")
            error_count += 1

    print()
    print("="*50)
    print(f"[*] Test Complete!")
    print(f"[*] Updated: {updated_count} files")
    print(f"[*] Skipped: {skipped_count} files")
    print(f"[*] Errors: {error_count} files")


if __name__ == '__main__':
    main()
