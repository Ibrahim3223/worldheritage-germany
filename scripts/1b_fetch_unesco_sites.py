"""
Script 1B: Fetch UNESCO World Heritage Sites ONLY
Fast targeted query to supplement existing data
"""

import json
import time
from SPARQLWrapper import SPARQLWrapper, JSON
from pathlib import Path
import re

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data' / 'raw'

def query_unesco_sites():
    """Query ONLY UNESCO World Heritage Sites in Germany"""

    query = """
SELECT
  ?item ?itemLabel ?itemDescription
  ?coords
  (GROUP_CONCAT(DISTINCT ?img; separator="|") AS ?images)
  ?heritage_type ?heritage_typeLabel
  ?admin ?adminLabel
  ?inception
  ?website

WHERE {
  # UNESCO World Heritage Sites in Germany
  ?item wdt:P1435 wd:Q9259 .  # UNESCO World Heritage Site
  ?item wdt:P17 wd:Q183 .      # in Germany
  ?item wdt:P625 ?coords .      # has coordinates

  # Get the heritage type (instance of)
  OPTIONAL { ?item wdt:P31 ?heritage_type . }

  # Essential fields - multiple images
  OPTIONAL { ?item wdt:P18 ?img . }
  OPTIONAL { ?item wdt:P131 ?admin . }
  OPTIONAL { ?item wdt:P571 ?inception . }
  OPTIONAL { ?item wdt:P856 ?website . }

  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "en,de" .
  }
}
GROUP BY ?item ?itemLabel ?itemDescription ?coords ?heritage_type ?heritage_typeLabel ?admin ?adminLabel ?inception ?website
"""

    print("Querying UNESCO World Heritage Sites in Germany...")

    sparql = SPARQLWrapper('https://query.wikidata.org/sparql')
    sparql.setReturnFormat(JSON)
    sparql.setTimeout(60)
    sparql.setMethod('POST')
    sparql.setQuery(query)
    sparql.agent = "WorldHeritageBot/1.0 (https://worldheritage.guide)"

    try:
        # Get raw response and sanitize
        response = sparql.query()
        raw_data = response.response.read()
        text = raw_data.decode('utf-8')
        # Remove control characters
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', text)
        results = json.loads(text)
        bindings = results['results']['bindings']
        print(f"Query returned {len(bindings)} results")
        return bindings
    except Exception as e:
        print(f"Query failed: {e}")
        return []

def parse_coordinate(coord_string):
    """Parse Wikidata coordinate to [lat, lng]"""
    try:
        coords = coord_string.replace('Point(', '').replace(')', '')
        lng, lat = map(float, coords.split())
        return [lat, lng]
    except:
        return None

def extract_value(binding, key, default=None):
    """Extract value from SPARQL binding"""
    if key in binding:
        value = binding[key].get('value', default)
        if isinstance(value, str):
            try:
                value = value.encode('utf-8').decode('utf-8')
            except:
                pass
        return value
    return default

def process_site(binding):
    """Process single UNESCO site"""
    item_uri = extract_value(binding, 'item')
    wikidata_id = item_uri.split('/')[-1] if item_uri else None

    coords_str = extract_value(binding, 'coords')
    coordinates = parse_coordinate(coords_str) if coords_str else None

    # Extract inception year
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
        'heritage_type': extract_value(binding, 'heritage_typeLabel', 'UNESCO World Heritage Site'),
        'country': 'Germany',
        'region': extract_value(binding, 'adminLabel'),
        'inception': inception,
        'official_website': extract_value(binding, 'website'),
        'unesco': True,  # All sites from this query are UNESCO
        'wikidata_images': wikidata_images,
        'completeness_score': 100,  # UNESCO sites are high priority
    }

    # Remove None values
    site = {k: v for k, v in site.items() if v is not None}
    return site

def merge_with_existing(unesco_sites):
    """Merge UNESCO sites with existing data"""
    sites_file = DATA_DIR / 'sites.json'

    # Load existing sites
    existing_sites = []
    if sites_file.exists():
        with open(sites_file, 'r', encoding='utf-8') as f:
            existing_sites = json.load(f)
        print(f"Loaded {len(existing_sites)} existing sites")

    # Create dict for deduplication
    sites_dict = {s['wikidata_id']: s for s in existing_sites if s.get('wikidata_id')}

    # Add/update UNESCO sites
    unesco_count = 0
    for unesco_site in unesco_sites:
        wikidata_id = unesco_site.get('wikidata_id')
        if wikidata_id:
            if wikidata_id in sites_dict:
                # Update existing site with UNESCO status
                sites_dict[wikidata_id]['unesco'] = True
                sites_dict[wikidata_id]['completeness_score'] = 100
            else:
                # Add new UNESCO site
                sites_dict[wikidata_id] = unesco_site
                unesco_count += 1

    print(f"Added {unesco_count} new UNESCO sites")

    # Convert to list and sort
    all_sites = list(sites_dict.values())
    all_sites.sort(key=lambda x: x.get('completeness_score', 0), reverse=True)

    return all_sites

def main():
    print("="*60)
    print("SCRIPT 1B: FETCH UNESCO SITES")
    print("="*60)
    print()

    # Query UNESCO sites
    results = query_unesco_sites()

    if not results:
        print("No results. Exiting.")
        return

    # Process sites
    print("\nProcessing UNESCO sites...")
    unesco_sites = []
    seen_ids = set()

    for binding in results:
        site = process_site(binding)
        wikidata_id = site.get('wikidata_id')

        if wikidata_id and wikidata_id not in seen_ids:
            if site.get('coordinates'):  # Must have coordinates
                unesco_sites.append(site)
                seen_ids.add(wikidata_id)

    print(f"Processed {len(unesco_sites)} unique UNESCO sites with coordinates")

    # Merge with existing data
    print("\nMerging with existing data...")
    all_sites = merge_with_existing(unesco_sites)

    # Save merged data
    output_file = DATA_DIR / 'sites.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_sites, f, ensure_ascii=False, indent=2)

    print()
    print("="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total sites: {len(all_sites)}")
    print(f"UNESCO sites: {len([s for s in all_sites if s.get('unesco')])}")
    print(f"Output: {output_file}")
    print()
    print("UNESCO sites:")
    for site in [s for s in all_sites if s.get('unesco')][:20]:
        print(f"  - {site['name']} ({site.get('region', 'Germany')})")
    print()
    print("Script 1B complete!")

if __name__ == '__main__':
    main()
