"""
Find all heritage categories (P31 instance of) for UNESCO sites in Germany
"""
from SPARQLWrapper import SPARQLWrapper, JSON
import json
from collections import Counter

def get_unesco_site_types():
    """Query Wikidata for UNESCO sites and their types"""
    query = """
    SELECT ?site ?siteLabel ?type ?typeLabel WHERE {
      ?site wdt:P1435 wd:Q9259 .  # UNESCO World Heritage Site
      ?site wdt:P17 wd:Q183 .      # in Germany
      ?site wdt:P31 ?type .        # instance of
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en,de". }
    }
    """

    sparql = SPARQLWrapper('https://query.wikidata.org/sparql')
    sparql.setReturnFormat(JSON)
    sparql.setQuery(query)
    sparql.agent = 'WorldHeritageBot/1.0'

    try:
        results = sparql.query().convert()
        bindings = results['results']['bindings']

        # Collect all types
        types = []
        sites_by_type = {}

        for binding in bindings:
            site_label = binding.get('siteLabel', {}).get('value', '')
            type_uri = binding.get('type', {}).get('value', '')
            type_label = binding.get('typeLabel', {}).get('value', '')
            type_id = type_uri.split('/')[-1]

            types.append((type_id, type_label))

            if type_label not in sites_by_type:
                sites_by_type[type_label] = []
            sites_by_type[type_label].append(site_label)

        return types, sites_by_type

    except Exception as e:
        print(f"Error: {e}")
        return [], {}

def main():
    print("Fetching UNESCO site types from Wikidata...")
    types, sites_by_type = get_unesco_site_types()

    # Count occurrences
    type_counter = Counter(types)

    print(f"\nFound {len(set(types))} unique heritage types for UNESCO sites")
    print(f"\nMost common types:\n")

    for (type_id, type_label), count in type_counter.most_common(30):
        print(f"  {type_label} ({type_id}): {count} sites")

    print(f"\n\nSites by type (showing types with 2+ sites):\n")
    for type_label, sites in sorted(sites_by_type.items(), key=lambda x: len(x[1]), reverse=True):
        if len(sites) >= 2:
            print(f"\n{type_label} ({len(sites)} sites):")
            for site in sites[:5]:  # Show first 5
                print(f"  - {site}")
            if len(sites) > 5:
                print(f"  ... and {len(sites) - 5} more")

    # Save to JSON
    output = {
        'types': [{'id': type_id, 'label': type_label, 'count': count}
                  for (type_id, type_label), count in type_counter.most_common()],
        'sites_by_type': {k: v for k, v in sites_by_type.items() if len(v) >= 2}
    }

    with open('data/unesco_heritage_types.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n\nSaved to: data/unesco_heritage_types.json")

if __name__ == '__main__':
    main()
