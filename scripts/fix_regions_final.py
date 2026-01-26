"""
Final fix for regions - fetch from Wikidata directly for sites with region: Germany
"""
from SPARQLWrapper import SPARQLWrapper, JSON
from pathlib import Path
import re
import time

def get_region_from_wikidata(wikidata_id):
    """Fetch administrative region from Wikidata"""
    query = f"""
    SELECT ?adminLabel WHERE {{
      wd:{wikidata_id} wdt:P131 ?admin .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,de" . }}
    }}
    LIMIT 1
    """

    sparql = SPARQLWrapper('https://query.wikidata.org/sparql')
    sparql.setReturnFormat(JSON)
    sparql.setQuery(query)
    sparql.agent = 'WorldHeritageBot/1.0'

    try:
        results = sparql.query().convert()
        bindings = results['results']['bindings']
        if bindings and 'adminLabel' in bindings[0]:
            region = bindings[0]['adminLabel']['value']
            # Skip if it's just "Germany" or country-level
            if region != 'Germany' and 'Q183' not in region:
                return region
    except Exception as e:
        print(f"Error querying {wikidata_id}: {e}")

    return None

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

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

def main():
    print("Fixing regions for sites with 'region: Germany'...")

    content_dir = Path('content/sites')
    files_to_fix = []

    # Find all files with region: Germany
    for filepath in content_dir.glob('*.md'):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if re.search(r'^region: Germany$', content, re.MULTILINE):
                # Extract wikidata_id
                match = re.search(r'wikidata_id:\s*["\']?([QP]\d+)["\']?', content)
                if match:
                    files_to_fix.append((filepath, match.group(1)))

    print(f"Found {len(files_to_fix)} files to fix")
    print(f"This will make {len(files_to_fix)} API calls to Wikidata")
    print("Processing in batches...")

    updated_count = 0
    failed_count = 0

    for i, (filepath, wikidata_id) in enumerate(files_to_fix, 1):
        if i % 10 == 0:
            print(f"Progress: {i}/{len(files_to_fix)} ({updated_count} updated, {failed_count} failed)")
            time.sleep(1)  # Rate limiting

        region = get_region_from_wikidata(wikidata_id)
        if region:
            update_region_in_file(filepath, region)
            updated_count += 1
        else:
            failed_count += 1

        # Rate limiting
        if i % 50 == 0:
            time.sleep(2)

    print(f"\n[DONE] Updated {updated_count} files, {failed_count} couldn't be updated")

if __name__ == '__main__':
    main()
