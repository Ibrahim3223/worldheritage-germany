#!/usr/bin/env python3
"""
Add multiple images to heritage sites from Wikidata/Wikimedia Commons
Updates existing site frontmatter to add more images for photo galleries
"""

import re
import json
import time
import requests
from pathlib import Path
from typing import List, Optional
from SPARQLWrapper import SPARQLWrapper, JSON as SPARQL_JSON

def query_wikidata_images(wikidata_id: str, limit: int = 10) -> List[str]:
    """
    Query Wikidata for multiple images of a heritage site
    Returns list of image URLs
    """
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setUserAgent("WorldHeritageGuide/1.0 (https://worldheritage.guide)")

    query = f"""
    SELECT DISTINCT ?image WHERE {{
      wd:{wikidata_id} wdt:P18 ?image.
    }}
    LIMIT {limit}
    """

    try:
        sparql.setQuery(query)
        sparql.setReturnFormat(SPARQL_JSON)
        results = sparql.query().convert()

        images = []
        for result in results["results"]["bindings"]:
            image_url = result["image"]["value"]
            # Convert to Wikimedia Commons URL with proper size
            if "Special:FilePath" in image_url:
                # Get filename
                filename = image_url.split("/")[-1]
                # Create thumbnail URL
                thumb_url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{filename}?width=1200"
                images.append(thumb_url)
            else:
                images.append(image_url)

        return images
    except Exception as e:
        print(f"❌ Error querying Wikidata for {wikidata_id}: {e}")
        return []

def extract_frontmatter(content: str) -> tuple[str, str, Optional[str]]:
    """Extract frontmatter, body content and wikidata_id"""
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not match:
        return '', content, None

    frontmatter = match.group(1)
    body = match.group(2)

    # Extract wikidata_id
    wid_match = re.search(r'^wikidata_id:\s*"([^"]+)"', frontmatter, re.MULTILINE)
    if wid_match:
        return frontmatter, body, wid_match.group(1)

    return frontmatter, body, None

def update_images_in_frontmatter(frontmatter: str, new_images: List[str]) -> str:
    """Update images array in frontmatter"""
    # Find existing images section
    images_match = re.search(r'^images:\n((?:  - .*\n)*)', frontmatter, re.MULTILINE)

    if not images_match:
        return frontmatter

    existing_images_text = images_match.group(1)
    existing_images = re.findall(r'  - (.*)', existing_images_text)

    # Combine and deduplicate
    all_images = existing_images + [img for img in new_images if img not in existing_images]

    # Limit to 8 images (good balance for galleries)
    all_images = all_images[:8]

    # Build new images section
    new_images_text = "images:\n"
    for img in all_images:
        new_images_text += f"  - {img}\n"

    # Replace in frontmatter
    frontmatter = re.sub(
        r'^images:\n(?:  - .*\n)*',
        new_images_text,
        frontmatter,
        flags=re.MULTILINE
    )

    return frontmatter

def main():
    """Main function to add multiple images"""
    print("📸 Adding multiple images to heritage sites...")

    content_dir = Path('content/sites')
    if not content_dir.exists():
        print(f"❌ Directory {content_dir} not found")
        return

    md_files = list(content_dir.glob('*.md'))
    total = len([f for f in md_files if f.name != '_index.md'])
    print(f"📝 Found {total} site files")

    updated = 0
    skipped = 0
    errors = 0
    batch_size = 100  # Process in batches for progress tracking

    for i, file_path in enumerate(md_files, 1):
        if file_path.name == '_index.md':
            continue

        try:
            content = file_path.read_text(encoding='utf-8')
            frontmatter, body, wikidata_id = extract_frontmatter(content)

            if not wikidata_id:
                skipped += 1
                continue

            # Check current image count
            current_images = re.findall(r'  - http', frontmatter)
            if len(current_images) >= 5:
                # Already has multiple images
                skipped += 1
                continue

            # Query Wikidata for more images
            new_images = query_wikidata_images(wikidata_id, limit=8)

            if len(new_images) <= 1:
                # No additional images found
                skipped += 1
                continue

            # Update frontmatter
            new_frontmatter = update_images_in_frontmatter(frontmatter, new_images)

            # Write back
            new_content = f"---\n{new_frontmatter}---\n{body}"
            file_path.write_text(new_content, encoding='utf-8')

            updated += 1

            # Rate limiting
            if i % 10 == 0:
                time.sleep(1)

            if i % batch_size == 0:
                print(f"✅ [{i}/{total}] Processed {updated} files, skipped {skipped}")

        except Exception as e:
            print(f"❌ [{i}/{total}] {file_path.name}: {e}")
            errors += 1
            continue

    print(f"\n✨ Done!")
    print(f"✅ Updated: {updated}")
    print(f"⚠️  Skipped: {skipped}")
    print(f"❌ Errors: {errors}")

if __name__ == '__main__':
    main()
