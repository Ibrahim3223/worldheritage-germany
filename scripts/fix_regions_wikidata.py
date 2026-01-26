#!/usr/bin/env python3
"""
Fix regions - map city/town regions to German states using Wikidata
Much faster than geocoding - uses SPARQL to query Wikidata in bulk
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, Optional
import time
import requests

# German states mapping (English names)
GERMAN_STATES_MAP = {
    'Q985': 'Baden-Württemberg',
    'Q980': 'Bavaria',
    'Q64': 'Berlin',
    'Q1208': 'Brandenburg',
    'Q24879': 'Bremen',
    'Q1055': 'Hamburg',
    'Q1199': 'Hesse',
    'Q1197': 'Lower Saxony',
    'Q1196': 'Mecklenburg-Vorpommern',
    'Q1198': 'North Rhine-Westphalia',
    'Q1200': 'Rhineland-Palatinate',
    'Q1201': 'Saarland',
    'Q1202': 'Saxony',
    'Q1206': 'Saxony-Anhalt',
    'Q1194': 'Schleswig-Holstein',
    'Q1205': 'Thuringia',
}

def query_wikidata_states(wikidata_ids: list) -> Dict[str, str]:
    """
    Query Wikidata for state information for multiple items
    Returns dict mapping wikidata_id to state name
    """
    # Build SPARQL query for multiple IDs
    ids_str = ' '.join([f'wd:{wid}' for wid in wikidata_ids])

    query = f"""
    SELECT ?item ?itemLabel ?state ?stateLabel WHERE {{
      VALUES ?item {{ {ids_str} }}
      OPTIONAL {{
        ?item wdt:P131* ?state.
        ?state wdt:P31/wdt:P279* wd:Q1221156.  # state of Germany
      }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    """

    url = 'https://query.wikidata.org/sparql'
    headers = {
        'User-Agent': 'WorldHeritageGuide/1.0',
        'Accept': 'application/json'
    }

    try:
        response = requests.get(url, params={'query': query, 'format': 'json'}, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Parse results
        state_map = {}
        for result in data['results']['bindings']:
            item_id = result['item']['value'].split('/')[-1]
            if 'state' in result:
                state_id = result['state']['value'].split('/')[-1]
                if state_id in GERMAN_STATES_MAP:
                    state_map[item_id] = GERMAN_STATES_MAP[state_id]
                elif 'stateLabel' in result:
                    # Fallback to label
                    state_label = result['stateLabel']['value']
                    # Try to match label
                    for qid, name in GERMAN_STATES_MAP.items():
                        if state_label == name or state_label in name:
                            state_map[item_id] = name
                            break

        return state_map
    except Exception as e:
        print(f"❌ Error querying Wikidata: {e}")
        return {}

def extract_frontmatter(content: str) -> tuple[str, str, Optional[str]]:
    """Extract frontmatter, content and get wikidata_id"""
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

def update_region_in_frontmatter(frontmatter: str, new_region: str) -> str:
    """Update region field in frontmatter"""
    # Update region field
    frontmatter = re.sub(
        r'^region:\s*".*"$',
        f'region: "{new_region}"',
        frontmatter,
        flags=re.MULTILINE
    )

    # Update regions array
    frontmatter = re.sub(
        r'^regions:\n\s*-\s*".*"$',
        f'regions:\n  - "{new_region}"',
        frontmatter,
        flags=re.MULTILINE
    )

    return frontmatter

def main():
    """Main function to fix regions"""
    print("🔧 Fixing regions - mapping to German states using Wikidata...")

    content_dir = Path('content/sites')
    if not content_dir.exists():
        print(f"❌ Directory {content_dir} not found")
        return

    md_files = list(content_dir.glob('*.md'))
    total = len([f for f in md_files if f.name != '_index.md'])
    print(f"📝 Found {total} site files")

    # First pass: collect all wikidata IDs
    print("📋 Collecting Wikidata IDs...")
    wikidata_to_file = {}

    for file_path in md_files:
        if file_path.name == '_index.md':
            continue

        try:
            content = file_path.read_text(encoding='utf-8')
            frontmatter, body, wikidata_id = extract_frontmatter(content)

            if wikidata_id:
                wikidata_to_file[wikidata_id] = file_path

        except Exception as e:
            print(f"❌ {file_path.name}: {e}")
            continue

    print(f"✅ Collected {len(wikidata_to_file)} Wikidata IDs")

    # Query Wikidata in batches
    print("🌐 Querying Wikidata for state information...")
    batch_size = 50  # Wikidata can handle ~50 items per query
    wikidata_ids = list(wikidata_to_file.keys())
    state_cache = {}

    for i in range(0, len(wikidata_ids), batch_size):
        batch = wikidata_ids[i:i + batch_size]
        print(f"📡 Querying batch {i//batch_size + 1}/{(len(wikidata_ids)-1)//batch_size + 1} ({len(batch)} items)...")

        state_map = query_wikidata_states(batch)
        state_cache.update(state_map)

        time.sleep(1)  # Rate limiting

    print(f"✅ Found state info for {len(state_cache)} items")

    # Second pass: update files
    print("✏️  Updating files...")
    updated = 0
    skipped = 0
    errors = 0

    for wikidata_id, file_path in wikidata_to_file.items():
        try:
            if wikidata_id not in state_cache:
                skipped += 1
                continue

            state = state_cache[wikidata_id]

            content = file_path.read_text(encoding='utf-8')
            frontmatter, body, _ = extract_frontmatter(content)

            # Update frontmatter
            new_frontmatter = update_region_in_frontmatter(frontmatter, state)

            # Write back
            new_content = f"---\n{new_frontmatter}\n---\n{body}"
            file_path.write_text(new_content, encoding='utf-8')

            updated += 1

            if updated % 100 == 0:
                print(f"✅ Updated {updated} files...")

        except Exception as e:
            print(f"❌ {file_path.name}: {e}")
            errors += 1
            continue

    print(f"\n✨ Done!")
    print(f"✅ Updated: {updated}")
    print(f"⚠️  Skipped: {skipped}")
    print(f"❌ Errors: {errors}")

    # Save cache for future use
    cache_file = Path('scripts/data/wikidata_state_cache.json')
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(state_cache, f, indent=2, ensure_ascii=False)
    print(f"💾 Cache saved to {cache_file}")

if __name__ == '__main__':
    main()
