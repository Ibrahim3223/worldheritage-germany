"""
Quick fix: Add UNESCO tags to all UNESCO World Heritage Sites
"""
from SPARQLWrapper import SPARQLWrapper, JSON
from pathlib import Path
import re

def get_unesco_sites():
    """Fetch all UNESCO World Heritage Sites in Germany from Wikidata"""
    query = '''
    SELECT DISTINCT ?site ?siteLabel WHERE {
      ?site wdt:P1435 wd:Q9259 .  # UNESCO World Heritage Site
      ?site wdt:P17 wd:Q183 .      # in Germany
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en,de" . }
    }
    '''

    sparql = SPARQLWrapper('https://query.wikidata.org/sparql')
    sparql.setReturnFormat(JSON)
    sparql.setQuery(query)
    sparql.agent = 'WorldHeritageBot/1.0'

    results = sparql.query().convert()
    unesco_ids = set()

    for binding in results['results']['bindings']:
        site_uri = binding['site']['value']
        wikidata_id = site_uri.split('/')[-1]
        unesco_ids.add(wikidata_id)

    return unesco_ids

def add_unesco_tag_to_file(filepath):
    """Add UNESCO tag to a content file if missing"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if already has UNESCO tag
    if 'tags:\n  - unesco' in content or 'tags:\n- unesco' in content:
        return False  # Already has tag

    # Find where to insert the tag
    # Look for the tags section
    if 'tags:\n' in content:
        # Tags section exists but no unesco - add it
        content = content.replace('tags:\n', 'tags:\n  - unesco\n', 1)
    else:
        # No tags section - add it after regions
        regions_match = re.search(r'(regions:\n(?:  - [^\n]+\n)+)', content)
        if regions_match:
            regions_section = regions_match.group(1)
            content = content.replace(
                regions_section,
                regions_section + 'tags:\n  - unesco\n',
                1
            )
        else:
            # Fallback: add after region field
            region_match = re.search(r'(region: [^\n]+\n)', content)
            if region_match:
                content = content.replace(
                    region_match.group(1),
                    region_match.group(1) + 'tags:\n  - unesco\n',
                    1
                )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return True

def main():
    print("Fetching UNESCO World Heritage Sites from Wikidata...")
    unesco_ids = get_unesco_sites()
    print(f"Found {len(unesco_ids)} UNESCO sites in Germany")
    print(f"Sample UNESCO IDs: {list(unesco_ids)[:5]}")

    # Process content files
    content_dir = Path('content/sites')
    updated_count = 0
    matched_count = 0
    checked_count = 0

    for filepath in content_dir.glob('*.md'):
        checked_count += 1
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract wikidata_id
        match = re.search(r'wikidata_id:\s*["\']?([QP]\d+)["\']?', content)
        if match:
            wikidata_id = match.group(1)

            if wikidata_id in unesco_ids:
                matched_count += 1
                if add_unesco_tag_to_file(filepath):
                    updated_count += 1
                    print(f"[+] Added UNESCO tag to {filepath.name}")

    print(f"\n[DONE] Checked {checked_count} files, matched {matched_count} UNESCO sites, updated {updated_count} files with UNESCO tags")

if __name__ == '__main__':
    main()
