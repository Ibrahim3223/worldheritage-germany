"""
Script 1C: Fetch Balanced Categories from Wikidata
Queries each category individually with limits for 10-15k balanced sites
"""

import json
import time
from SPARQLWrapper import SPARQLWrapper, JSON
from pathlib import Path
import re
from collections import Counter

# Import comprehensive categories from Script 0
import sys
import importlib.util

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

spec = importlib.util.spec_from_file_location("define_categories", script_dir / "0_define_categories.py")
cat_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cat_module)
CATEGORIES = cat_module.CATEGORIES
CATEGORY_LIMITS = cat_module.CATEGORY_LIMITS

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data' / 'raw'

def query_category(category_key: str, category_info: dict, limit: int):
    """Query single category from Wikidata"""

    wikidata_classes = category_info['wikidata_classes']
    type_values = ' '.join([f'wd:{qid}' for qid in wikidata_classes])

    query = f"""
SELECT
  ?item ?itemLabel ?itemDescription
  ?coords
  (GROUP_CONCAT(DISTINCT ?img; separator="|") AS ?images)
  ?heritage_type ?heritage_typeLabel
  ?admin ?adminLabel
  ?inception
  ?website
  ?unesco

WHERE {{
  VALUES ?heritage_type {{ {type_values} }}

  ?item wdt:P31 ?heritage_type .
  ?item wdt:P17 wd:Q183 .
  ?item wdt:P625 ?coords .

  OPTIONAL {{ ?item wdt:P18 ?img . }}
  OPTIONAL {{ ?item wdt:P131 ?admin . }}
  OPTIONAL {{ ?item wdt:P571 ?inception . }}
  OPTIONAL {{ ?item wdt:P856 ?website . }}

  OPTIONAL {{
    ?item wdt:P1435 wd:Q9259 .
    BIND(true AS ?unesco)
  }}

  SERVICE wikibase:label {{
    bd:serviceParam wikibase:language "en,de" .
  }}
}}
GROUP BY ?item ?itemLabel ?itemDescription ?coords ?heritage_type ?heritage_typeLabel ?admin ?adminLabel ?inception ?website ?unesco
LIMIT {limit}
"""

    print(f"  Querying {category_key} (limit: {limit})...")

    sparql = SPARQLWrapper('https://query.wikidata.org/sparql')
    sparql.setReturnFormat(JSON)
    sparql.setTimeout(120)
    sparql.setMethod('POST')
    sparql.setQuery(query)
    sparql.agent = "WorldHeritageBot/1.0 (https://worldheritage.guide)"

    try:
        response = sparql.query()
        raw_data = response.response.read()
        text = raw_data.decode('utf-8')
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', text)
        results = json.loads(text)
        bindings = results['results']['bindings']
        print(f"    -> Got {len(bindings)} results")
        return bindings
    except Exception as e:
        print(f"    -> ERROR: {str(e)[:100]}")
        return []

def parse_coordinate(coord_string):
    try:
        coords = coord_string.replace('Point(', '').replace(')', '')
        lng, lat = map(float, coords.split())
        return [lat, lng]
    except:
        return None

def extract_value(binding, key, default=None):
    if key in binding:
        value = binding[key].get('value', default)
        if isinstance(value, str):
            try:
                value = value.encode('utf-8').decode('utf-8')
            except:
                pass
        return value
    return default

def process_site(binding, category_key: str):
    """Process single site"""
    item_uri = extract_value(binding, 'item')
    wikidata_id = item_uri.split('/')[-1] if item_uri else None

    coords_str = extract_value(binding, 'coords')
    coordinates = parse_coordinate(coords_str) if coords_str else None

    inception_raw = extract_value(binding, 'inception')
    inception = None
    if inception_raw:
        if 'T' in inception_raw:
            inception = inception_raw.split('T')[0][:4]
        else:
            inception = inception_raw[:4] if len(inception_raw) >= 4 else inception_raw

    # Extract images (up to 8 from GROUP_CONCAT)
    images_str = extract_value(binding, 'images')
    wikidata_images = []
    if images_str:
        wikidata_images = images_str.split('|')[:8]

    site = {
        'wikidata_id': wikidata_id,
        'name': extract_value(binding, 'itemLabel'),
        'description': extract_value(binding, 'itemDescription'),
        'coordinates': coordinates,
        'heritage_type': extract_value(binding, 'heritage_typeLabel'),
        'category_key': category_key,  # Track which category this came from
        'country': 'Germany',
        'region': extract_value(binding, 'adminLabel'),
        'inception': inception,
        'official_website': extract_value(binding, 'website'),
        'unesco': extract_value(binding, 'unesco') == 'true',
        'wikidata_images': wikidata_images,
    }

    site = {k: v for k, v in site.items() if v is not None and v != []}
    return site

def calculate_completeness_score(site):
    """Calculate site data completeness (0-100)"""
    score = 0

    # Critical fields (50 points)
    if site.get('name'): score += 10
    if site.get('coordinates'): score += 10
    if site.get('country'): score += 5
    if site.get('heritage_type'): score += 5
    if site.get('description'): score += 10
    if site.get('wikidata_id'): score += 10

    # Important fields (30 points)
    if site.get('region'): score += 10
    if site.get('wikidata_images') and len(site.get('wikidata_images', [])) > 0: score += 10
    if site.get('official_website'): score += 5
    if site.get('inception'): score += 5

    # Bonus for UNESCO (20 points)
    if site.get('unesco'): score += 20

    return min(score, 100)

def main():
    print("="*70)
    print("SCRIPT 1C: BALANCED CATEGORY FETCHER")
    print("="*70)
    print(f"Total categories: {len(CATEGORIES)}")
    print(f"Target sites: {sum(CATEGORY_LIMITS.values()):,}")
    print()

    # First, ensure we have UNESCO sites
    print("[1/2] Ensuring UNESCO coverage...")
    unesco_file = DATA_DIR / 'sites.json'
    existing_sites = {}

    if unesco_file.exists():
        with open(unesco_file, 'r', encoding='utf-8') as f:
            existing = json.load(f)
            for s in existing:
                if s.get('wikidata_id'):
                    existing_sites[s['wikidata_id']] = s
        print(f"  Loaded {len(existing_sites)} existing sites")

    # Categorize by priority
    priority_order = ['very_high', 'high', 'medium', 'low']
    categorized = {p: [] for p in priority_order}

    for cat_key, cat_info in CATEGORIES.items():
        priority = cat_info.get('priority', 'low')
        categorized[priority].append(cat_key)

    print("\nCategories by priority:")
    for priority in priority_order:
        cats = categorized[priority]
        if cats:
            print(f"  {priority.upper()}: {len(cats)} categories")

    # Process categories by priority
    print("\n[2/2] Fetching categories...")
    all_sites = {}
    stats = {'fetched': 0, 'low_quality': 0, 'total_queries': 0}

    for priority in priority_order:
        for cat_key in categorized[priority]:
            if cat_key not in CATEGORY_LIMITS:
                continue

            limit = CATEGORY_LIMITS[cat_key]
            cat_info = CATEGORIES[cat_key]

            stats['total_queries'] += 1
            print(f"\n[{stats['total_queries']}/{len(CATEGORY_LIMITS)}] {cat_key} ({priority})")

            results = query_category(cat_key, cat_info, limit)

            if not results:
                time.sleep(2)
                continue

            # Process results
            for binding in results:
                site = process_site(binding, cat_key)
                wikidata_id = site.get('wikidata_id')

                if not wikidata_id or not site.get('coordinates'):
                    continue

                # Calculate quality score
                score = calculate_completeness_score(site)
                site['completeness_score'] = score

                # Quality filter: minimum 45 points
                if score < 45:
                    stats['low_quality'] += 1
                    continue

                # Add or update site
                if wikidata_id in all_sites:
                    # Keep the one with higher score
                    if score > all_sites[wikidata_id].get('completeness_score', 0):
                        all_sites[wikidata_id] = site
                else:
                    all_sites[wikidata_id] = site
                    stats['fetched'] += 1

            # Be nice to Wikidata
            time.sleep(3)

            # Progress update every 10 categories
            if stats['total_queries'] % 10 == 0:
                print(f"\n  PROGRESS: {len(all_sites):,} sites | {stats['low_quality']} filtered out")

    # Merge with existing sites (preserve UNESCO)
    for wid, site in existing_sites.items():
        if wid not in all_sites:
            # Add if quality is good
            score = calculate_completeness_score(site)
            if score >= 45:
                site['completeness_score'] = score
                all_sites[wid] = site

    # Convert to list and sort by score
    sites_list = list(all_sites.values())
    sites_list.sort(key=lambda x: x.get('completeness_score', 0), reverse=True)

    # Save
    output_file = DATA_DIR / 'sites.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sites_list, f, ensure_ascii=False, indent=2)

    # Statistics
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total sites: {len(sites_list):,}")
    print(f"Filtered out (low quality): {stats['low_quality']:,}")
    print(f"UNESCO sites: {len([s for s in sites_list if s.get('unesco')]):,}")
    print(f"Average quality: {sum(s.get('completeness_score', 0) for s in sites_list) / len(sites_list):.1f}")
    print(f"Output: {output_file}")

    # Category distribution
    print("\nTop 20 categories by count:")
    category_counts = Counter([s.get('category_key', 'unknown') for s in sites_list])
    for cat_key, count in category_counts.most_common(20):
        print(f"  {count:4d} - {cat_key}")

    print("\n" + "="*70)
    print("Script 1C complete!")

if __name__ == '__main__':
    main()
