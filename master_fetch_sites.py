#!/usr/bin/env python3
"""
MASTER SITE FETCHER
Complete system for fetching 12-17k high-quality sites with quality filters
Optimized for 100+ countries

Usage:
    python master_fetch_sites.py Germany
    python master_fetch_sites.py France --target 15000
"""

import requests
import json
import time
import argparse
from pathlib import Path
from wikidata_categories_comprehensive import (
    CATEGORIES, COUNTRIES, CATEGORY_LIMITS, QUALITY_FILTERS,
    get_category_limit, get_categories_by_priority
)

OUTPUT_DIR = Path("data/fetched")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# QUALITY FILTER FUNCTIONS
# ============================================================================

def meets_quality_threshold(entity_data):
    """
    Check if entity meets quality thresholds

    Quality criteria:
    - Minimum sitelinks (Wikipedia versions)
    - Has coordinates (if required)
    - Minimum number of claims/statements
    """
    # Check sitelinks (Wikipedia language versions)
    sitelinks = entity_data.get('sitelinks', {})
    if len(sitelinks) < QUALITY_FILTERS['min_sitelinks']:
        return False, f"Low sitelinks: {len(sitelinks)}"

    # Check for coordinates
    if QUALITY_FILTERS['require_coordinates']:
        claims = entity_data.get('claims', {})
        if 'P625' not in claims:  # P625 = coordinate location
            return False, "No coordinates"

    # Check minimum claims
    claims_count = len(entity_data.get('claims', {}))
    if claims_count < QUALITY_FILTERS['min_claims']:
        return False, f"Low claims: {claims_count}"

    return True, "OK"

def fetch_sites_with_quality_filter(country_code, category_key, limit=None):
    """
    Fetch sites from Wikidata with quality filtering

    Args:
        country_code: Country Wikidata ID (e.g., "Q183" for Germany)
        category_key: Category key from wikidata_categories_comprehensive.py
        limit: Maximum number of results (uses CATEGORY_LIMITS if None)

    Returns:
        List of high-quality sites
    """
    if limit is None:
        limit = get_category_limit(category_key)

    category_info = CATEGORIES.get(category_key)
    if not category_info:
        print(f"  [ERROR] Category '{category_key}' not found")
        return []

    wikidata_classes = category_info['wikidata_classes']
    class_values = " ".join([f"wd:{c}" for c in wikidata_classes])

    # Build SPARQL query with quality signals
    # We fetch more than needed to account for filtering
    fetch_limit = min(limit * 3, 1000)  # Fetch 3x to ensure enough after filtering

    query = f"""
SELECT DISTINCT ?item ?itemLabel ?itemDescription ?coord ?image ?sitelinks WHERE {{
  VALUES ?class {{ {class_values} }}
  ?item wdt:P31 ?class.
  ?item wdt:P17 wd:{country_code}.

  OPTIONAL {{ ?item wdt:P625 ?coord. }}
  OPTIONAL {{ ?item wdt:P18 ?image. }}

  # Count sitelinks (Wikipedia versions) - quality signal
  OPTIONAL {{
    ?item wikibase:sitelinks ?sitelinks.
  }}

  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,de". }}
}}
ORDER BY DESC(?sitelinks)
LIMIT {fetch_limit}
"""

    url = "https://query.wikidata.org/sparql"
    headers = {
        "User-Agent": "WorldHeritageBot/2.0 (https://worldheritage.guide; contact@worldheritage.guide)",
        "Accept": "application/json"
    }

    try:
        print(f"  Querying Wikidata (fetching up to {fetch_limit} for filtering)...")
        response = requests.get(url, params={'query': query}, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()

        sites = []
        filtered_out = {
            "low_sitelinks": 0,
            "no_coordinates": 0,
            "low_claims": 0,
            "limit_reached": 0,
        }

        for binding in data.get('results', {}).get('bindings', []):
            # Check if we've reached the limit
            if len(sites) >= limit:
                filtered_out["limit_reached"] += 1
                continue

            wikidata_id = binding['item']['value'].split('/')[-1]

            # Fetch detailed entity data for quality check
            entity_url = f"https://www.wikidata.org/w/api.php"
            entity_params = {
                "action": "wbgetentities",
                "ids": wikidata_id,
                "format": "json",
                "props": "claims|sitelinks"
            }

            try:
                entity_response = requests.get(entity_url, params=entity_params, headers=headers, timeout=10)
                entity_data = entity_response.json()['entities'][wikidata_id]

                # Apply quality filter
                passes, reason = meets_quality_threshold(entity_data)
                if not passes:
                    if "sitelinks" in reason:
                        filtered_out["low_sitelinks"] += 1
                    elif "coordinates" in reason:
                        filtered_out["no_coordinates"] += 1
                    elif "claims" in reason:
                        filtered_out["low_claims"] += 1
                    continue

            except Exception as e:
                print(f"    [WARN] Could not fetch details for {wikidata_id}: {e}")
                continue

            # Build site data
            site = {
                'wikidata_id': wikidata_id,
                'title': binding.get('itemLabel', {}).get('value', 'Unknown'),
                'description': binding.get('itemDescription', {}).get('value', ''),
                'has_coordinates': 'coord' in binding,
                'has_image': 'image' in binding,
                'sitelinks': int(binding.get('sitelinks', {}).get('value', 0)),
                'category': category_key,
                'category_info': category_info
            }

            if 'coord' in binding:
                coord_str = binding['coord']['value']
                coords = coord_str.replace('Point(', '').replace(')', '').split()
                site['longitude'] = float(coords[0])
                site['latitude'] = float(coords[1])

            if 'image' in binding:
                site['image_url'] = binding['image']['value']

            sites.append(site)

            # Rate limiting for API calls
            time.sleep(0.1)

        # Report filtering stats
        total_fetched = len(data.get('results', {}).get('bindings', []))
        print(f"  Fetched: {total_fetched}, Accepted: {len(sites)}, Filtered: {total_fetched - len(sites)}")
        if any(filtered_out.values()):
            print(f"    Reasons: {dict(filtered_out)}")

        return sites

    except Exception as e:
        print(f"  [ERROR] Failed to fetch {category_key}: {e}")
        return []

def save_results(sites, category_key, country_name):
    """Save results to JSON file"""
    filename = OUTPUT_DIR / f"{country_name.lower()}_{category_key}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(sites, f, indent=2, ensure_ascii=False)
    return filename

# ============================================================================
# MASTER FETCH ORCHESTRATOR
# ============================================================================

def fetch_all_categories(country_name, target_pages=15000, priorities=None):
    """
    Fetch all categories with quality filtering

    Args:
        country_name: Country name (e.g., "Germany")
        target_pages: Target number of pages (12000-17000 recommended)
        priorities: List of priority levels to fetch (default: all)

    Returns:
        Dictionary of category results
    """
    country_code = COUNTRIES.get(country_name)
    if not country_code:
        print(f"[ERROR] Country '{country_name}' not found")
        return {}

    if priorities is None:
        priorities = ["very_high", "high", "medium", "low"]

    print("=" * 80)
    print(f"MASTER SITE FETCHER - {country_name}")
    print("=" * 80)
    print(f"Target pages: {target_pages:,}")
    print(f"Quality filters: {QUALITY_FILTERS}")
    print(f"Priorities: {priorities}")
    print()

    all_results = {}
    total_sites = 0

    for priority in priorities:
        categories = get_categories_by_priority(priority)

        if not categories:
            continue

        print(f"\n{'='*80}")
        print(f"PRIORITY: {priority.upper()} ({len(categories)} categories)")
        print(f"{'='*80}\n")

        for i, category_key in enumerate(categories, 1):
            if total_sites >= target_pages:
                print(f"\n[INFO] Target reached ({total_sites:,} sites). Stopping.")
                return all_results

            category_info = CATEGORIES[category_key]
            limit = get_category_limit(category_key)

            print(f"[{i}/{len(categories)}] {category_key}")
            print(f"  Description: {category_info['description']}")
            print(f"  Target: {limit} sites")

            sites = fetch_sites_with_quality_filter(country_code, category_key, limit)

            if sites:
                filename = save_results(sites, category_key, country_name)
                all_results[category_key] = sites
                total_sites += len(sites)

                with_coords = sum(1 for s in sites if s['has_coordinates'])
                with_images = sum(1 for s in sites if s['has_image'])
                avg_sitelinks = sum(s.get('sitelinks', 0) for s in sites) / len(sites)

                print(f"  [OK] Collected: {len(sites)} sites")
                print(f"    - Coordinates: {with_coords} ({with_coords/len(sites)*100:.1f}%)")
                print(f"    - Images: {with_images} ({with_images/len(sites)*100:.1f}%)")
                print(f"    - Avg sitelinks: {avg_sitelinks:.1f}")
                print(f"    - Saved: {filename}")
                print(f"  Total progress: {total_sites:,}/{target_pages:,} ({total_sites/target_pages*100:.1f}%)")
            else:
                print(f"  [SKIP] No sites found")

            # Rate limiting between categories
            time.sleep(2)

    print(f"\n{'='*80}")
    print("FETCH COMPLETE")
    print(f"{'='*80}")
    print(f"Total sites collected: {total_sites:,}")
    print(f"Total categories: {len(all_results)}")
    print(f"\nCategory breakdown:")
    for cat, sites in sorted(all_results.items(), key=lambda x: -len(x[1]))[:20]:
        print(f"  {cat:30s}: {len(sites):4d} sites")
    if len(all_results) > 20:
        print(f"  ... and {len(all_results) - 20} more categories")

    return all_results

# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Master site fetcher with quality filters')
    parser.add_argument('country', help='Country name (e.g., Germany, France, Italy)')
    parser.add_argument('--target', type=int, default=15000, help='Target number of pages (default: 15000)')
    parser.add_argument('--priorities', nargs='+', choices=['very_high', 'high', 'medium', 'low'],
                       help='Priority levels to fetch (default: all)')
    parser.add_argument('--test', action='store_true', help='Test mode - fetch only 5 sites per category')

    args = parser.parse_args()

    # Test mode override
    if args.test:
        print("[TEST MODE] Limiting to 5 sites per category")
        for key in CATEGORY_LIMITS:
            CATEGORY_LIMITS[key] = 5
        args.target = 100

    fetch_all_categories(args.country, args.target, args.priorities)

if __name__ == "__main__":
    main()
