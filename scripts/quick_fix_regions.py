#!/usr/bin/env python3
"""
Quick region fix - Map coordinates to German states
Much faster than Wikidata queries - uses coordinate boundaries
"""

import re
from pathlib import Path
from typing import Optional

# German states with approximate coordinate boundaries
# Format: (min_lat, max_lat, min_lon, max_lon)
GERMAN_STATES = {
    'Baden-Württemberg': (47.5, 49.8, 7.5, 10.5),
    'Bavaria': (47.3, 50.6, 8.9, 13.9),
    'Berlin': (52.3, 52.7, 13.1, 13.8),
    'Brandenburg': (51.4, 53.6, 11.3, 14.8),
    'Bremen': (53.0, 53.7, 8.5, 9.0),
    'Hamburg': (53.4, 53.8, 9.7, 10.4),
    'Hesse': (49.4, 51.7, 7.8, 10.3),
    'Lower Saxony': (51.3, 54.0, 6.6, 11.7),
    'Mecklenburg-Vorpommern': (53.1, 54.7, 10.6, 14.5),
    'North Rhine-Westphalia': (50.3, 52.6, 5.9, 9.5),
    'Rhineland-Palatinate': (48.9, 50.9, 6.1, 8.6),
    'Saarland': (49.1, 49.7, 6.3, 7.5),
    'Saxony': (50.2, 51.7, 11.9, 15.1),
    'Saxony-Anhalt': (50.9, 53.1, 10.6, 13.2),
    'Schleswig-Holstein': (53.4, 55.1, 8.0, 11.4),
    'Thuringia': (50.2, 51.7, 9.9, 12.7),
}

def get_state_from_coordinates(lat: float, lon: float) -> Optional[str]:
    """Determine German state from coordinates"""
    for state, (min_lat, max_lat, min_lon, max_lon) in GERMAN_STATES.items():
        if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
            return state
    return None

def extract_frontmatter(content: str) -> tuple[str, str, Optional[tuple]]:
    """Extract frontmatter, body and coordinates"""
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not match:
        return '', content, None

    frontmatter = match.group(1)
    body = match.group(2)

    # Extract latitude and longitude
    lat_match = re.search(r'^latitude:\s*([0-9.-]+)', frontmatter, re.MULTILINE)
    lon_match = re.search(r'^longitude:\s*([0-9.-]+)', frontmatter, re.MULTILINE)

    if lat_match and lon_match:
        return frontmatter, body, (float(lat_match.group(1)), float(lon_match.group(1)))

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
    """Main function"""
    print("[*] Quick region fix using coordinate boundaries...")

    content_dir = Path('content/sites')
    if not content_dir.exists():
        print(f"[!] Directory {content_dir} not found")
        return

    md_files = list(content_dir.glob('*.md'))
    total = len([f for f in md_files if f.name != '_index.md'])
    print(f"[*] Found {total} site files")

    updated = 0
    skipped = 0
    errors = 0

    for i, file_path in enumerate(md_files, 1):
        if file_path.name == '_index.md':
            continue

        try:
            content = file_path.read_text(encoding='utf-8')
            frontmatter, body, coords = extract_frontmatter(content)

            if not coords:
                skipped += 1
                continue

            lat, lon = coords
            state = get_state_from_coordinates(lat, lon)

            if not state:
                skipped += 1
                continue

            # Update frontmatter
            new_frontmatter = update_region_in_frontmatter(frontmatter, state)

            # Write back
            new_content = f"---\n{new_frontmatter}---\n{body}"
            file_path.write_text(new_content, encoding='utf-8')

            updated += 1

            if i % 500 == 0:
                print(f"[+] [{i}/{total}] Updated {updated} files")

        except Exception as e:
            print(f"[!] [{i}/{total}] {file_path.name}: {e}")
            errors += 1
            continue

    print(f"\n[*] Done!")
    print(f"[+] Updated: {updated}")
    print(f"[-] Skipped: {skipped}")
    print(f"[!] Errors: {errors}")

if __name__ == '__main__':
    main()
