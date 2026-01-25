"""
Script 6: Fix All Metadata Issues in Existing Content
- Adds missing site_name
- Corrects region from "Germany" to actual state/region
- Adds UNESCO tags where applicable
- Updates to Wikimedia Commons image URLs
"""

import os
import re
import json
import hashlib
import requests
from pathlib import Path
from typing import Dict, List, Optional
from tqdm import tqdm

# ============================================
# CONFIGURATION
# ============================================

BASE_DIR = Path(__file__).parent.parent
CONTENT_DIR = BASE_DIR / "content" / "sites"
DATA_DIR = BASE_DIR / 'data' / 'fetched'

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
IMAGE_SIZES = [400, 800, 1200, 1920]

HEADERS = {
    'User-Agent': 'WorldHeritageBot/1.0 (https://worldheritage.guide)',
    'Accept': 'application/json',
}

# ============================================
# WIKIDATA HELPERS
# ============================================

def load_wikidata_cache() -> Dict:
    """Load all Wikidata JSON files into a lookup dict"""
    cache = {}
    for json_file in sorted(DATA_DIR.glob('germany_*.json')):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                sites = json.load(f)
                for site in sites:
                    wikidata_id = site.get('wikidata_id')
                    if wikidata_id:
                        cache[wikidata_id] = site
        except Exception as e:
            print(f"Error loading {json_file.name}: {e}")
    return cache

def get_wikidata_info(wikidata_id: str) -> Optional[Dict]:
    """Fetch comprehensive info from Wikidata"""
    if not wikidata_id:
        return None

    try:
        # Fetch entity data
        url = "https://www.wikidata.org/w/api.php"
        params = {
            'action': 'wbgetentities',
            'ids': wikidata_id,
            'props': 'claims',
            'format': 'json'
        }

        response = requests.get(url, params=params, headers=HEADERS, timeout=15)
        data = response.json()

        if 'entities' not in data or wikidata_id not in data['entities']:
            return None

        entity = data['entities'][wikidata_id]
        claims = entity.get('claims', {})

        info = {}

        # P131: located in administrative territorial entity (region)
        if 'P131' in claims:
            for claim in claims['P131']:
                if 'mainsnak' in claim and 'datavalue' in claim['mainsnak']:
                    admin_id = claim['mainsnak']['datavalue']['value']['id']
                    # Fetch the label
                    admin_label = get_entity_label(admin_id)
                    if admin_label:
                        info['region'] = admin_label
                        break

        # P1435: heritage designation (UNESCO check)
        if 'P1435' in claims:
            for claim in claims['P1435']:
                if 'mainsnak' in claim and 'datavalue' in claim['mainsnak']:
                    designation_id = claim['mainsnak']['datavalue']['value']['id']
                    if designation_id == 'Q9259':  # UNESCO World Heritage Site
                        info['unesco'] = True
                        break

        # P18: image
        if 'P18' in claims:
            images = []
            for claim in claims['P18'][:5]:
                if 'mainsnak' in claim and 'datavalue' in claim['mainsnak']:
                    filename = claim['mainsnak']['datavalue']['value']
                    images.append(filename)
            info['images'] = images

        return info if info else None

    except Exception as e:
        print(f"Error fetching {wikidata_id}: {e}")
        return None

def get_entity_label(entity_id: str) -> Optional[str]:
    """Get English label for a Wikidata entity"""
    try:
        url = "https://www.wikidata.org/w/api.php"
        params = {
            'action': 'wbgetentities',
            'ids': entity_id,
            'props': 'labels',
            'languages': 'en',
            'format': 'json'
        }

        response = requests.get(url, params=params, headers=HEADERS, timeout=10)
        data = response.json()

        if 'entities' in data and entity_id in data['entities']:
            labels = data['entities'][entity_id].get('labels', {})
            if 'en' in labels:
                return labels['en']['value']

    except:
        pass

    return None

# ============================================
# WIKIMEDIA IMAGE HELPERS
# ============================================

def get_wikimedia_thumb_url(filename: str, width: int = 1200) -> str:
    """Generate Wikimedia Commons thumbnail URL"""
    filename = filename.replace(' ', '_')
    md5 = hashlib.md5(filename.encode('utf-8')).hexdigest()
    base_url = f"https://upload.wikimedia.org/wikipedia/commons/thumb/{md5[0]}/{md5[0:2]}/{filename}/{width}px-{filename}"

    if filename.lower().endswith('.svg'):
        base_url += '.png'
    elif filename.lower().endswith(('.tif', '.tiff')):
        base_url = base_url.replace(filename, filename + '.jpg')

    return base_url

# ============================================
# FILE PROCESSING
# ============================================

def extract_frontmatter(content: str) -> tuple:
    """Extract YAML frontmatter and body content"""
    if not content.startswith('---'):
        return None, content

    parts = content.split('---', 2)
    if len(parts) < 3:
        return None, content

    return parts[1].strip(), parts[2].strip()

def parse_yaml_field(frontmatter: str, field: str) -> Optional[str]:
    """Extract a field value from YAML frontmatter"""
    pattern = rf'^{field}:\s*["\']?(.+?)["\']?\s*$'
    match = re.search(pattern, frontmatter, re.MULTILINE)
    return match.group(1) if match else None

def update_frontmatter(frontmatter: str, updates: Dict) -> str:
    """Update YAML frontmatter with new values"""
    lines = frontmatter.split('\n')
    updated_lines = []
    fields_added = set()

    # Track if we're inside a list (images, tags, etc.)
    in_list = None

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Check if we're entering/exiting a list
        if ':' in line and not line.startswith(' '):
            field_name = line.split(':')[0].strip()
            if field_name in ['images', 'tags', 'categories', 'regions', 'image_srcset']:
                in_list = field_name
            else:
                in_list = None

        # Handle field updates
        field_updated = False
        for key, value in updates.items():
            if line.startswith(f'{key}:'):
                if key == 'images' and isinstance(value, list):
                    # Replace images list
                    updated_lines.append(f'{key}:')
                    for img in value:
                        updated_lines.append(f'  - {img}')
                    fields_added.add(key)
                    field_updated = True

                    # Skip existing image lines
                    i += 1
                    while i < len(lines) and (lines[i].startswith('  -') or lines[i].strip() == ''):
                        i += 1
                    i -= 1

                elif key == 'image_srcset' and isinstance(value, dict):
                    # Add srcset after images
                    fields_added.add(key)
                    # Will be added later
                    field_updated = False

                elif key == 'tags' and isinstance(value, list):
                    # Replace tags list
                    updated_lines.append(f'{key}:')
                    for tag in value:
                        updated_lines.append(f'  - {tag}')
                    fields_added.add(key)
                    field_updated = True

                    # Skip existing tag lines
                    i += 1
                    while i < len(lines) and (lines[i].startswith('  -') or lines[i].strip() == ''):
                        i += 1
                    i -= 1

                else:
                    # Simple field replacement
                    updated_lines.append(f'{key}: "{value}"')
                    fields_added.add(key)
                    field_updated = True
                break

        if not field_updated:
            updated_lines.append(line)

        i += 1

    # Add new fields that don't exist
    insert_index = len(updated_lines)

    # Find where to insert new fields (before latitude/longitude)
    for idx, line in enumerate(updated_lines):
        if line.startswith('latitude:'):
            insert_index = idx
            break

    new_fields = []
    for key, value in updates.items():
        if key not in fields_added:
            if key == 'site_name':
                new_fields.append(f'site_name: "{value}"')
            elif key == 'wikidata_id':
                new_fields.append(f'wikidata_id: "{value}"')
            elif key == 'region':
                new_fields.append(f'region: "{value}"')
            elif key == 'tags' and isinstance(value, list):
                new_fields.append('tags:')
                for tag in value:
                    new_fields.append(f'  - {tag}')
            elif key == 'image_srcset' and isinstance(value, dict):
                new_fields.append('image_srcset:')
                for img_key, sizes in value.items():
                    new_fields.append(f'  {img_key}:')
                    for size, url in sizes.items():
                        new_fields.append(f'    {size}: {url}')

    # Insert new fields
    updated_lines = updated_lines[:insert_index] + new_fields + updated_lines[insert_index:]

    return '\n'.join(updated_lines)

def process_file(file_path: Path, wikidata_cache: Dict) -> bool:
    """Process a single markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        frontmatter, body = extract_frontmatter(content)
        if not frontmatter:
            return False

        # Extract current metadata
        title = parse_yaml_field(frontmatter, 'title')
        wikidata_id = parse_yaml_field(frontmatter, 'wikidata_id')
        current_region = parse_yaml_field(frontmatter, 'region')

        updates = {}
        changed = False

        # 1. Add site_name if missing
        site_name = parse_yaml_field(frontmatter, 'site_name')
        if not site_name and title:
            updates['site_name'] = title
            changed = True

        # 2. Fix region if it's just "Germany"
        if current_region == 'Germany' and wikidata_id:
            # Try cache first
            if wikidata_id in wikidata_cache:
                cached_region = wikidata_cache[wikidata_id].get('region')
                if cached_region and cached_region != 'Germany':
                    updates['region'] = cached_region
                    changed = True
            else:
                # Fetch from Wikidata
                info = get_wikidata_info(wikidata_id)
                if info and 'region' in info:
                    updates['region'] = info['region']
                    changed = True

        # 3. Add UNESCO tag if applicable
        if wikidata_id:
            # Check if already has UNESCO tag
            has_unesco_tag = 'tags:\n  - unesco' in frontmatter or 'tags:\n- unesco' in frontmatter

            if not has_unesco_tag:
                # Check cache
                is_unesco = False
                if wikidata_id in wikidata_cache:
                    is_unesco = wikidata_cache[wikidata_id].get('unesco', False)
                else:
                    info = get_wikidata_info(wikidata_id)
                    is_unesco = info.get('unesco', False) if info else False

                if is_unesco:
                    updates['tags'] = ['unesco']
                    changed = True

        # 4. Update to Wikimedia images if available
        if wikidata_id and 'images:' in frontmatter:
            # Check if already using Wikimedia URLs
            has_wikimedia = 'upload.wikimedia.org' in frontmatter

            if not has_wikimedia:
                # Get Wikimedia images
                images = []
                srcset = {}

                if wikidata_id in wikidata_cache:
                    wiki_img = wikidata_cache[wikidata_id].get('wikidata_image')
                    if wiki_img:
                        images = [wiki_img]
                else:
                    info = get_wikidata_info(wikidata_id)
                    if info and 'images' in info:
                        images = info['images']

                if images:
                    # Generate URLs
                    image_urls = []
                    for filename in images[:5]:
                        main_url = get_wikimedia_thumb_url(filename, 1200)
                        image_urls.append(main_url)

                        # Generate srcset
                        srcset_key = filename.replace(' ', '%20')
                        srcset[srcset_key] = {
                            400: get_wikimedia_thumb_url(filename, 400),
                            800: get_wikimedia_thumb_url(filename, 800),
                            1200: get_wikimedia_thumb_url(filename, 1200),
                            1920: get_wikimedia_thumb_url(filename, 1920),
                        }

                    if image_urls:
                        updates['images'] = image_urls
                        updates['image_srcset'] = srcset
                        changed = True

        if changed and updates:
            new_frontmatter = update_frontmatter(frontmatter, updates)
            new_content = f"---\n{new_frontmatter}\n---\n\n{body}"

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            return True

    except Exception as e:
        print(f"\nError processing {file_path.name}: {e}")

    return False

# ============================================
# MAIN
# ============================================

def main():
    print("=" * 60)
    print("Metadata Fixer - Comprehensive Update")
    print("=" * 60)
    print()

    # Load Wikidata cache
    print("Loading Wikidata cache...")
    wikidata_cache = load_wikidata_cache()
    print(f"Loaded {len(wikidata_cache)} sites from cache")
    print()

    # Get all markdown files
    md_files = [f for f in CONTENT_DIR.glob('*.md') if f.name != '_index.md']
    print(f"Found {len(md_files)} content files")
    print()

    # Process files
    updated_count = 0
    with tqdm(total=len(md_files), desc="Fixing metadata") as pbar:
        for md_file in md_files:
            if process_file(md_file, wikidata_cache):
                updated_count += 1
            pbar.update(1)

    print()
    print("=" * 60)
    print(f"✅ Complete! Updated {updated_count}/{len(md_files)} files")
    print("=" * 60)

if __name__ == '__main__':
    main()
