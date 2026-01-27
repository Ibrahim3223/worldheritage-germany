"""
Script 1: Fetch Heritage Sites from Wikidata
Queries Wikisparql for all heritage sites in Germany
"""

import time
from SPARQLWrapper import SPARQLWrapper, JSON
from typing import List, Dict
from tqdm import tqdm

# Handle imports for both package and direct execution
try:
    from .config import (
        PROJECT, SPARQL_ENDPOINT,
        SPARQL_TIMEOUT, PATHS, DATA_QUALITY
    )
    from .utils import (
        save_json, calculate_completeness_score,
        validate_coordinates, logger, log_progress
    )
    # Import comprehensive categories from Script 0
    try:
        from ._0_define_categories import CATEGORIES
    except ImportError:
        from __main__0_define_categories import CATEGORIES
except ImportError:
    from config import (
        PROJECT, SPARQL_ENDPOINT,
        SPARQL_TIMEOUT, PATHS, DATA_QUALITY
    )
    from utils import (
        save_json, calculate_completeness_score,
        validate_coordinates, logger, log_progress
    )
    # Import comprehensive categories from Script 0
    import importlib.util
    spec = importlib.util.spec_from_file_location("define_categories", "0_define_categories.py")
    cat_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cat_module)
    CATEGORIES = cat_module.CATEGORIES

# Convert Script 0 CATEGORIES to heritage_types format for SPARQL query
HERITAGE_TYPES = {}
for category_key, category_info in CATEGORIES.items():
    for qid in category_info['wikidata_classes']:
        # Use first word of description as label
        label = category_info['description']
        HERITAGE_TYPES[qid] = label

# ============================================
# SPARQL QUERY
# ============================================

def build_sparql_query(country_wikidata_id: str, heritage_types: Dict) -> str:
    """Build SPARQL query for heritage sites - balanced for quality and performance"""

    type_values = ' '.join([f'wd:{qid}' for qid in heritage_types.keys()])

    # Comprehensive query with important fields for content quality
    # Updated to fetch multiple images (up to 8) using GROUP_CONCAT
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
  ?item wdt:P17 wd:{country_wikidata_id} .
  ?item wdt:P625 ?coords .

  # Essential fields only
  OPTIONAL {{ ?item wdt:P18 ?img . }}
  OPTIONAL {{ ?item wdt:P131 ?admin . }}
  OPTIONAL {{ ?item wdt:P571 ?inception . }}
  OPTIONAL {{ ?item wdt:P856 ?website . }}

  # UNESCO status - CRITICAL
  OPTIONAL {{
    ?item wdt:P1435 wd:Q9259 .
    BIND(true AS ?unesco)
  }}

  SERVICE wikibase:label {{
    bd:serviceParam wikibase:language "en,de" .
  }}
}}
GROUP BY ?item ?itemLabel ?itemDescription ?coords ?heritage_type ?heritage_typeLabel ?admin ?adminLabel ?inception ?website ?unesco
LIMIT 10000
"""

    return query

# ============================================
# DATA PROCESSING
# ============================================

def query_wikidata(query: str) -> List[Dict]:
    """Execute SPARQL query with proper UTF-8 encoding and control character handling"""
    import re
    import json

    logger.info("Executing Wikidata query...")

    sparql = SPARQLWrapper(SPARQL_ENDPOINT)
    sparql.setReturnFormat(JSON)
    sparql.setTimeout(SPARQL_TIMEOUT)
    sparql.setMethod('POST')  # Use POST for large queries
    sparql.setQuery(query)

    # Add User-Agent header (required by Wikidata)
    sparql.agent = "WorldHeritageBot/1.0 (https://worldheritage.guide; contact@worldheritage.guide)"

    try:
        # Get raw response
        response = sparql.query()
        raw_data = response.response.read()

        # Decode and sanitize - remove control characters except newline, tab, carriage return
        text = raw_data.decode('utf-8')
        # Remove control characters (0x00-0x1F) except \t (0x09), \n (0x0A), \r (0x0D)
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', text)

        # Parse sanitized JSON
        results = json.loads(text)
        bindings = results['results']['bindings']
        logger.info(f"Query returned {len(bindings)} results")
        return bindings
    except Exception as e:
        logger.error(f"Query failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []

def parse_coordinate(coord_string: str) -> List[float]:
    """Parse Wikidata coordinate to [lat, lng]"""
    try:
        coords = coord_string.replace('Point(', '').replace(')', '')
        lng, lat = map(float, coords.split())
        return [lat, lng]
    except:
        return None

def extract_value(binding: Dict, key: str, default=None):
    """Extract value from SPARQL binding with proper UTF-8 handling"""
    if key in binding:
        value = binding[key].get('value', default)
        # Ensure string values are properly decoded as UTF-8
        if isinstance(value, str):
            try:
                # Handle any encoding issues by normalizing the string
                value = value.encode('utf-8').decode('utf-8')
            except (UnicodeEncodeError, UnicodeDecodeError):
                pass
        return value
    return default

def process_site_data(binding: Dict) -> Dict:
    """Process single site from SPARQL result"""

    item_uri = extract_value(binding, 'item')
    wikidata_id = item_uri.split('/')[-1] if item_uri else None

    coords_str = extract_value(binding, 'coords')
    coordinates = parse_coordinate(coords_str) if coords_str else None

    # Extract inception year from date string
    inception_raw = extract_value(binding, 'inception')
    inception = None
    if inception_raw:
        # Handle various date formats from Wikidata
        if 'T' in inception_raw:
            inception = inception_raw.split('T')[0][:4]  # Get year part
        else:
            inception = inception_raw[:4] if len(inception_raw) >= 4 else inception_raw

    # Extract images (up to 8 from GROUP_CONCAT)
    images_str = extract_value(binding, 'images')
    wikidata_images = []
    if images_str:
        # Split by | separator and take first 8
        wikidata_images = images_str.split('|')[:8]

    site = {
        'wikidata_id': wikidata_id,
        'name': extract_value(binding, 'itemLabel'),
        'description': extract_value(binding, 'itemDescription'),
        'coordinates': coordinates,
        'heritage_type': extract_value(binding, 'heritage_typeLabel'),
        'country': 'Germany',
        'region': extract_value(binding, 'adminLabel'),
        'inception': inception,
        # Visitor info
        'official_website': extract_value(binding, 'website'),
        # Status - CRITICAL
        'unesco': extract_value(binding, 'unesco') == 'true',
        # Images (up to 8)
        'wikidata_images': wikidata_images,
    }

    site = {k: v for k, v in site.items() if v is not None and v != []}
    return site

def validate_site(site: Dict) -> tuple[bool, str]:
    """Validate if site meets requirements"""

    for field in DATA_QUALITY['required_fields']:
        if not site.get(field):
            return False, f"Missing: {field}"

    if not validate_coordinates(site.get('coordinates')):
        return False, "Invalid coordinates"

    score = calculate_completeness_score(site)
    if score < DATA_QUALITY['completeness_minimum']:
        return False, f"Score too low: {score}"

    return True, "Valid"

# ============================================
# MAIN
# ============================================

def main():
    """Main execution - Query categories in batches to avoid timeout"""

    logger.info("="*60)
    logger.info("SCRIPT 1: FETCH WIKIDATA (BATCHED)")
    logger.info("="*60)
    logger.info(f"Country: {PROJECT['country']}")
    logger.info(f"Wikidata ID: {PROJECT['wikidata_id']}")
    logger.info(f"Total heritage types: {len(HERITAGE_TYPES)}")
    logger.info("")

    # Split heritage types into batches of 10 to avoid timeout
    heritage_items = list(HERITAGE_TYPES.items())
    batch_size = 10
    batches = [dict(heritage_items[i:i+batch_size]) for i in range(0, len(heritage_items), batch_size)]

    logger.info(f"Querying in {len(batches)} batches (batch size: {batch_size})")
    logger.info("")

    all_results = []
    for batch_num, batch in enumerate(batches, 1):
        logger.info(f"Batch {batch_num}/{len(batches)}: {len(batch)} types")
        query = build_sparql_query(PROJECT['wikidata_id'], batch)
        results = query_wikidata(query)
        all_results.extend(results)
        logger.info(f"  -> Got {len(results)} results")

        # Small delay between batches to be nice to Wikidata
        if batch_num < len(batches):
            time.sleep(2)

    logger.info(f"\nTotal results from all batches: {len(all_results)}")

    if not all_results:
        logger.error("No results. Exiting.")
        return

    logger.info("\nProcessing sites...")
    sites_dict = {}  # Use dict to deduplicate by wikidata_id
    skipped = []

    for binding in tqdm(all_results, desc="Processing"):
        site = process_site_data(binding)
        wikidata_id = site.get('wikidata_id')

        # Skip if no wikidata_id
        if not wikidata_id:
            continue

        # If we've seen this site before, merge data (keep the more complete version)
        if wikidata_id in sites_dict:
            existing = sites_dict[wikidata_id]
            # Merge: keep existing values, add new ones if missing
            for key, value in site.items():
                if value and not existing.get(key):
                    existing[key] = value
            continue

        is_valid, reason = validate_site(site)

        if is_valid:
            site['completeness_score'] = calculate_completeness_score(site)
            sites_dict[wikidata_id] = site
        else:
            skipped.append({
                'name': site.get('name', 'Unknown'),
                'wikidata_id': wikidata_id,
                'reason': reason
            })

    # Convert dict to list and sort
    sites = list(sites_dict.values())
    sites.sort(key=lambda x: x['completeness_score'], reverse=True)

    output_file = PATHS['raw'] / 'sites.json'
    save_json(sites, output_file)

    skipped_file = PATHS['logs'] / 'skipped_sites.json'
    save_json(skipped, skipped_file)

    logger.info("")
    logger.info("="*60)
    logger.info("SUMMARY")
    logger.info("="*60)
    logger.info(f"Total raw results: {len(all_results)}")
    logger.info(f"Valid unique sites: {len(sites)}")
    logger.info(f"Skipped: {len(skipped)}")
    logger.info(f"Average completeness: {sum(s['completeness_score'] for s in sites) / len(sites):.1f}")
    logger.info(f"Output: {output_file}")
    logger.info("")

    # Count UNESCO sites
    unesco_sites = [s for s in sites if s.get('unesco')]
    logger.info(f"UNESCO World Heritage Sites: {len(unesco_sites)}")

    logger.info("\nTop 10 by completeness:")
    for i, site in enumerate(sites[:10], 1):
        unesco_mark = " [UNESCO]" if site.get('unesco') else ""
        logger.info(f"{i}. {site['name']}{unesco_mark} (score: {site['completeness_score']})")

    logger.info("")
    logger.info("Script 1 complete!")

if __name__ == '__main__':
    main()
