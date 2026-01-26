"""
Fix regions using Wikidata cache files
"""
from pathlib import Path
import json
import re
import glob as globlib

def load_all_cache_regions():
    """Load all regions from Wikidata cache files"""
    region_map = {}  # wikidata_id -> region

    cache_dir = Path('data/fetched')
    for cache_file in cache_dir.glob('germany_*.json'):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                sites = json.load(f)
                for site in sites:
                    wikidata_id = site.get('wikidata_id')
                    region = site.get('region')
                    if wikidata_id and region and region != 'Germany':
                        region_map[wikidata_id] = region
        except Exception as e:
            print(f"Error reading {cache_file}: {e}")

    return region_map

def update_region_in_file(filepath, new_region):
    """Update region in markdown file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace region: Germany with actual region
    new_content = re.sub(
        r'^region: Germany$',
        f'region: {new_region}',
        content,
        flags=re.MULTILINE
    )

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True

    return False

def main():
    print("Loading regions from Wikidata cache...")
    region_map = load_all_cache_regions()
    print(f"Loaded {len(region_map)} regions from cache")

    content_dir = Path('content/sites')
    updated_count = 0
    not_found_count = 0
    checked_count = 0

    for filepath in content_dir.glob('*.md'):
        checked_count += 1
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if has region: Germany
        if not re.search(r'^region: Germany$', content, re.MULTILINE):
            continue

        # Extract wikidata_id
        match = re.search(r'wikidata_id:\s*["\']?([QP]\d+)["\']?', content)
        if match:
            wikidata_id = match.group(1)
            if wikidata_id in region_map:
                region = region_map[wikidata_id]
                if update_region_in_file(filepath, region):
                    updated_count += 1
                    if updated_count % 100 == 0:
                        print(f"Updated {updated_count} files...")
            else:
                not_found_count += 1

    print(f"\n[DONE] Checked {checked_count} files")
    print(f"Updated {updated_count} files with regions from cache")
    print(f"{not_found_count} files had region: Germany but not found in cache")

if __name__ == '__main__':
    main()
