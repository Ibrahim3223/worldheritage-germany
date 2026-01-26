"""
Comprehensive Metadata Fix Script
- Finds wikidata_id using coordinates and title
- Fetches region, UNESCO status, images from Wikidata
- Updates all metadata fields
"""
from pathlib import Path
import re
import json
import time
import hashlib
from SPARQLWrapper import SPARQLWrapper, JSON
import requests

# ============================================
# CONFIGURATION
# ============================================

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
HEADERS = {
    'User-Agent': 'WorldHeritageBot/1.0 (https://worldheritage.guide)',
}

# ============================================
# WIKIDATA SEARCH
# ============================================

def find_wikidata_id(title, lat, lon):
    """Find wikidata ID using SPARQL query with coordinates and title"""
    # Search within 1km radius
    query = f"""
    SELECT ?item ?itemLabel ?dist WHERE {{
      ?item wdt:P625 ?coords.
      ?item wdt:P17 wd:Q183.  # in Germany
      SERVICE wikibase:around {{
        ?item wdt:P625 ?coords.
        bd:serviceParam wikibase:center "Point({lon} {lat})"^^geo:wktLiteral.
        bd:serviceParam wikibase:radius "1".  # 1 km radius
        bd:serviceParam wikibase:distance ?dist.
      }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,de". }}
    }}
    ORDER BY ?dist
    LIMIT 5
    """

    try:
        sparql = SPARQLWrapper(SPARQL_ENDPOINT)
        sparql.setReturnFormat(JSON)
        sparql.setQuery(query)
        sparql.agent = HEADERS['User-Agent']

        results = sparql.query().convert()
        bindings = results['results']['bindings']

        if not bindings:
            return None

        # Try to match by title
        title_lower = title.lower().strip()
        for binding in bindings:
            item_label = binding.get('itemLabel', {}).get('value', '').lower().strip()
            if title_lower in item_label or item_label in title_lower:
                item_uri = binding['item']['value']
                return item_uri.split('/')[-1]

        # If no title match, return closest one
        item_uri = bindings[0]['item']['value']
        return item_uri.split('/')[-1]

    except Exception as e:
        print(f"Error finding wikidata ID for {title}: {e}")
        return None

def get_wikidata_metadata(wikidata_id):
    """Fetch comprehensive metadata from Wikidata"""
    metadata = {}

    try:
        # Fetch entity claims
        url = WIKIDATA_API
        params = {
            'action': 'wbgetentities',
            'ids': wikidata_id,
            'props': 'claims',
            'format': 'json'
        }

        response = requests.get(url, params=params, headers=HEADERS, timeout=15)
        data = response.json()

        if 'entities' not in data or wikidata_id not in data['entities']:
            return metadata

        claims = data['entities'][wikidata_id].get('claims', {})

        # P131: Administrative region
        if 'P131' in claims:
            for claim in claims['P131'][:1]:  # Take first one
                if 'mainsnak' in claim and 'datavalue' in claim['mainsnak']:
                    admin_id = claim['mainsnak']['datavalue']['value']['id']
                    admin_label = get_entity_label(admin_id)
                    if admin_label and admin_label != 'Germany':
                        metadata['region'] = admin_label
                        break

        # P1435: Heritage designation (UNESCO)
        if 'P1435' in claims:
            for claim in claims['P1435']:
                if 'mainsnak' in claim and 'datavalue' in claim['mainsnak']:
                    designation_id = claim['mainsnak']['datavalue']['value']['id']
                    if designation_id == 'Q9259':  # UNESCO
                        metadata['unesco'] = True
                        break

        # P18: Images
        images = []
        if 'P18' in claims:
            for claim in claims['P18'][:5]:  # Max 5 images
                if 'mainsnak' in claim and 'datavalue' in claim['mainsnak']:
                    filename = claim['mainsnak']['datavalue']['value']
                    image_url = get_wikimedia_thumb_url(filename, 1200)
                    images.append(image_url)

        if images:
            metadata['images'] = images

    except Exception as e:
        print(f"Error fetching metadata for {wikidata_id}: {e}")

    return metadata

def get_entity_label(entity_id):
    """Get label for a Wikidata entity"""
    try:
        params = {
            'action': 'wbgetentities',
            'ids': entity_id,
            'props': 'labels',
            'languages': 'en|de',
            'format': 'json'
        }
        response = requests.get(WIKIDATA_API, params=params, headers=HEADERS, timeout=10)
        data = response.json()

        if 'entities' in data and entity_id in data['entities']:
            labels = data['entities'][entity_id].get('labels', {})
            return labels.get('en', labels.get('de', {})).get('value')
    except:
        pass
    return None

def get_wikimedia_thumb_url(filename, width=1200):
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

def extract_metadata(content):
    """Extract current metadata from markdown file"""
    metadata = {}

    # Title
    title_match = re.search(r'^title:\s*(.+)$', content, re.MULTILINE)
    if title_match:
        metadata['title'] = title_match.group(1).strip(' "\n')

    # Coordinates
    lat_match = re.search(r'^latitude:\s*([\d.]+)', content, re.MULTILINE)
    lon_match = re.search(r'^longitude:\s*([\d.]+)', content, re.MULTILINE)
    if lat_match and lon_match:
        metadata['latitude'] = float(lat_match.group(1))
        metadata['longitude'] = float(lon_match.group(1))

    # Wikidata ID
    wikidata_match = re.search(r'wikidata_id:\s*["\']?([QP]\d+)["\']?', content)
    if wikidata_match:
        metadata['wikidata_id'] = wikidata_match.group(1)

    # Current region
    region_match = re.search(r'^region:\s*(.+)$', content, re.MULTILINE)
    if region_match:
        metadata['current_region'] = region_match.group(1).strip()

    return metadata

def update_file(filepath, updates):
    """Update markdown file with new metadata"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add wikidata_id if missing
    if 'wikidata_id' in updates and 'wikidata_id:' not in content:
        # Add after description or region
        region_match = re.search(r'(^region:.*\n)', content, re.MULTILINE)
        if region_match:
            content = content.replace(
                region_match.group(1),
                region_match.group(1) + f'wikidata_id: {updates["wikidata_id"]}\n',
                1
            )

    # Update region
    if 'region' in updates:
        content = re.sub(
            r'^region:\s*Germany\s*$',
            f'region: {updates["region"]}',
            content,
            flags=re.MULTILINE
        )
        # Also update regions list
        content = re.sub(
            r'regions:\n  - Germany',
            f'regions:\n  - {updates["region"]}',
            content
        )

    # Add site_name if missing
    if 'site_name' in updates and 'site_name:' not in content:
        title_match = re.search(r'(^title:.*\n)', content, re.MULTILINE)
        if title_match:
            content = content.replace(
                title_match.group(1),
                title_match.group(1) + f'site_name: "{updates["site_name"]}"\n',
                1
            )

    # Add UNESCO tag if applicable
    if updates.get('unesco') and 'tags:' not in content:
        regions_match = re.search(r'(regions:\n(?:  - [^\n]+\n)+)', content)
        if regions_match:
            content = content.replace(
                regions_match.group(1),
                regions_match.group(1) + 'tags:\n  - unesco\n',
                1
            )

    # Add images if missing
    if 'images' in updates and 'images:' not in content:
        # Find where to insert (after longitude)
        lon_match = re.search(r'(^longitude:.*\n)', content, re.MULTILINE)
        if lon_match:
            images_yaml = 'images:\n' + '\n'.join([f'- {img}' for img in updates['images']]) + '\n'
            content = content.replace(
                lon_match.group(1),
                lon_match.group(1) + images_yaml,
                1
            )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

# ============================================
# MAIN
# ============================================

def main():
    print("="*60)
    print("COMPREHENSIVE METADATA FIX")
    print("="*60)
    print()
    print("This script will:")
    print("  1. Find wikidata_id for files missing it (using coordinates)")
    print("  2. Fetch region, UNESCO status, and images from Wikidata")
    print("  3. Update all metadata fields")
    print()
    print("WARNING: This will make thousands of API calls and take 30-60 minutes")
    print("Starting automatically...")
    print()

    content_dir = Path('content/sites')

    # Find files needing fixes
    files_to_fix = []
    for filepath in content_dir.glob('*.md'):
        if filepath.name == '_index.md':
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if needs wikidata_id
        if not re.search(r'wikidata_id:', content):
            files_to_fix.append(filepath)

    print(f"\nFound {len(files_to_fix)} files needing wikidata_id")

    # TEST MODE - Process only first 10 files
    import sys
    if '--test' in sys.argv:
        files_to_fix = files_to_fix[:10]
        print(f"TEST MODE: Processing only {len(files_to_fix)} files")

    print("Starting processing...")
    print()

    stats = {
        'processed': 0,
        'wikidata_found': 0,
        'region_updated': 0,
        'unesco_added': 0,
        'images_added': 0,
        'failed': 0,
    }

    for i, filepath in enumerate(files_to_fix, 1):
        if i % 100 == 0:
            print(f"Progress: {i}/{len(files_to_fix)} - Stats: {stats}")
            time.sleep(2)  # Rate limiting

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            meta = extract_metadata(content)

            if 'latitude' not in meta or 'longitude' not in meta:
                stats['failed'] += 1
                continue

            # Find wikidata ID
            wikidata_id = find_wikidata_id(
                meta.get('title', ''),
                meta['latitude'],
                meta['longitude']
            )

            if not wikidata_id:
                stats['failed'] += 1
                continue

            stats['wikidata_found'] += 1

            # Fetch metadata
            wikidata_meta = get_wikidata_metadata(wikidata_id)

            # Prepare updates
            updates = {'wikidata_id': wikidata_id}

            if meta.get('current_region') == 'Germany' and 'region' in wikidata_meta:
                updates['region'] = wikidata_meta['region']
                stats['region_updated'] += 1

            if wikidata_meta.get('unesco'):
                updates['unesco'] = True
                stats['unesco_added'] += 1

            if 'images' in wikidata_meta and 'images:' not in content:
                updates['images'] = wikidata_meta['images']
                stats['images_added'] += 1

            if 'title' in meta and 'site_name' not in content:
                updates['site_name'] = meta['title']

            # Update file
            update_file(filepath, updates)
            stats['processed'] += 1

            # Rate limiting
            time.sleep(0.5)

        except Exception as e:
            print(f"Error processing {filepath.name}: {e}")
            stats['failed'] += 1

    print()
    print("="*60)
    print("FINAL STATS")
    print("="*60)
    print(f"Files processed: {stats['processed']}")
    print(f"Wikidata IDs found: {stats['wikidata_found']}")
    print(f"Regions updated: {stats['region_updated']}")
    print(f"UNESCO tags added: {stats['unesco_added']}")
    print(f"Images added: {stats['images_added']}")
    print(f"Failed: {stats['failed']}")

if __name__ == '__main__':
    main()
