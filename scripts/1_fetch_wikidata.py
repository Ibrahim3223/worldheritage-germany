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
        PROJECT, HERITAGE_TYPES, SPARQL_ENDPOINT,
        SPARQL_TIMEOUT, PATHS, DATA_QUALITY
    )
    from .utils import (
        save_json, calculate_completeness_score,
        validate_coordinates, logger, log_progress
    )
except ImportError:
    from config import (
        PROJECT, HERITAGE_TYPES, SPARQL_ENDPOINT,
        SPARQL_TIMEOUT, PATHS, DATA_QUALITY
    )
    from utils import (
        save_json, calculate_completeness_score,
        validate_coordinates, logger, log_progress
    )

# ============================================
# SPARQL QUERY
# ============================================

def build_sparql_query(country_wikidata_id: str, heritage_types: Dict) -> str:
    """Build SPARQL query for heritage sites - balanced for quality and performance"""

    type_values = ' '.join([f'wd:{qid}' for qid in heritage_types.keys()])

    # Comprehensive query with important fields for content quality
    query = f"""
SELECT DISTINCT
  ?item ?itemLabel ?itemDescription
  ?coords ?image
  ?heritage_type ?heritage_typeLabel
  ?admin ?adminLabel
  ?inception
  ?architect ?architectLabel
  ?style ?styleLabel
  ?height ?area ?elevation
  ?website ?opening_hours ?admission_fee
  ?visitor_count
  ?unesco
  ?material ?materialLabel
  ?religion ?religionLabel

WHERE {{
  VALUES ?heritage_type {{ {type_values} }}

  ?item wdt:P31 ?heritage_type .
  ?item wdt:P17 wd:{country_wikidata_id} .
  ?item wdt:P625 ?coords .

  # Essential fields
  OPTIONAL {{ ?item wdt:P18 ?image . }}
  OPTIONAL {{ ?item wdt:P131 ?admin . }}
  OPTIONAL {{ ?item wdt:P571 ?inception . }}
  OPTIONAL {{ ?item wdt:P84 ?architect . }}
  OPTIONAL {{ ?item wdt:P149 ?style . }}

  # Physical attributes
  OPTIONAL {{ ?item wdt:P2048 ?height . }}
  OPTIONAL {{ ?item wdt:P2046 ?area . }}
  OPTIONAL {{ ?item wdt:P2044 ?elevation . }}
  OPTIONAL {{ ?item wdt:P186 ?material . }}

  # Visitor info
  OPTIONAL {{ ?item wdt:P856 ?website . }}
  OPTIONAL {{ ?item wdt:P3025 ?opening_hours . }}
  OPTIONAL {{ ?item wdt:P2555 ?admission_fee . }}
  OPTIONAL {{ ?item wdt:P1174 ?visitor_count . }}

  # UNESCO status
  OPTIONAL {{
    ?item wdt:P1435 wd:Q9259 .
    BIND(true AS ?unesco)
  }}

  # Additional context
  OPTIONAL {{ ?item wdt:P140 ?religion . }}

  SERVICE wikibase:label {{
    bd:serviceParam wikibase:language "en,de" .
  }}
}}
LIMIT 10000
"""

    return query

# ============================================
# DATA PROCESSING
# ============================================

def query_wikidata(query: str) -> List[Dict]:
    """Execute SPARQL query with proper UTF-8 encoding"""
    logger.info("Executing Wikidata query...")

    sparql = SPARQLWrapper(SPARQL_ENDPOINT)
    sparql.setReturnFormat(JSON)
    sparql.setTimeout(SPARQL_TIMEOUT)
    sparql.setMethod('POST')  # Use POST for large queries
    sparql.setQuery(query)

    # Add User-Agent header (required by Wikidata)
    sparql.agent = "WorldHeritageBot/1.0 (https://worldheritage.guide; contact@worldheritage.guide)"

    try:
        results = sparql.query().convert()
        bindings = results['results']['bindings']
        logger.info(f"Query returned {len(bindings)} results")
        return bindings
    except Exception as e:
        logger.error(f"Query failed: {e}")
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

    site = {
        'wikidata_id': wikidata_id,
        'name': extract_value(binding, 'itemLabel'),
        'description': extract_value(binding, 'itemDescription'),
        'coordinates': coordinates,
        'heritage_type': extract_value(binding, 'heritage_typeLabel'),
        'country': 'Germany',
        'region': extract_value(binding, 'adminLabel'),
        'inception': inception,
        'architect': extract_value(binding, 'architectLabel'),
        'style': extract_value(binding, 'styleLabel'),
        # Physical attributes
        'height_m': extract_value(binding, 'height'),
        'area_sqm': extract_value(binding, 'area'),
        'elevation': extract_value(binding, 'elevation'),
        'material': extract_value(binding, 'materialLabel'),
        # Visitor info
        'official_website': extract_value(binding, 'website'),
        'opening_hours': extract_value(binding, 'opening_hours'),
        'entry_fee': extract_value(binding, 'admission_fee'),
        'annual_visitors': extract_value(binding, 'visitor_count'),
        # Status
        'unesco': extract_value(binding, 'unesco') == 'true',
        'religion': extract_value(binding, 'religionLabel'),
        # Image
        'wikidata_image': extract_value(binding, 'image'),
    }

    site = {k: v for k, v in site.items() if v is not None}
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
    """Main execution"""

    logger.info("="*60)
    logger.info("SCRIPT 1: FETCH WIKIDATA")
    logger.info("="*60)
    logger.info(f"Country: {PROJECT['country']}")
    logger.info(f"Wikidata ID: {PROJECT['wikidata_id']}")
    logger.info(f"Heritage types: {len(HERITAGE_TYPES)}")
    logger.info("")

    query = build_sparql_query(PROJECT['wikidata_id'], HERITAGE_TYPES)
    results = query_wikidata(query)

    if not results:
        logger.error("No results. Exiting.")
        return

    logger.info("Processing sites...")
    sites_dict = {}  # Use dict to deduplicate by wikidata_id
    skipped = []

    for binding in tqdm(results, desc="Processing"):
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
    logger.info(f"Total results: {len(results)}")
    logger.info(f"Valid sites: {len(sites)}")
    logger.info(f"Skipped: {len(skipped)}")
    logger.info(f"Average completeness: {sum(s['completeness_score'] for s in sites) / len(sites):.1f}")
    logger.info(f"Output: {output_file}")
    logger.info("")

    logger.info("Top 10 by completeness:")
    for i, site in enumerate(sites[:10], 1):
        logger.info(f"{i}. {site['name']} (score: {site['completeness_score']})")

    logger.info("")
    logger.info("Script 1 complete!")

if __name__ == '__main__':
    main()
