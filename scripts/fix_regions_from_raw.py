"""
Fix regions using data/raw/sites.json (output from script 1)
"""
from pathlib import Path
import json
import re

def load_regions_from_raw():
    """Load regions from data/raw/sites.json"""
    region_map = {}  # wikidata_id -> region

    with open('data/raw/sites.json', 'r', encoding='utf-8') as f:
        sites = json.load(f)
        for site in sites:
            wikidata_id = site.get('wikidata_id')
            region = site.get('region')
            if wikidata_id and region and region != 'Germany':
                region_map[wikidata_id] = region

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
    print("Loading regions from data/raw/sites.json...")
    region_map = load_regions_from_raw()
    print(f"Loaded {len(region_map)} regions")

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
    print(f"Updated {updated_count} files with regions")
    print(f"{not_found_count} files had region: Germany but not found in raw data")

if __name__ == '__main__':
    main()
