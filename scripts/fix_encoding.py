"""
Fix UTF-8 encoding issues in JSON files
"""

import json
from pathlib import Path

def fix_encoding(file_path):
    """Fix encoding issues in a JSON file"""
    # Try to read with different encodings
    for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                data = json.load(f)
            print(f"Successfully read {file_path.name} with {encoding} encoding")

            # Write back with proper UTF-8
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"✓ Fixed {file_path.name} - saved as UTF-8")
            return True
        except Exception as e:
            continue

    print(f"✗ Failed to fix {file_path.name}")
    return False

# Fix both files
base_dir = Path(__file__).parent.parent
sites_test = base_dir / 'data/raw/sites_test.json'
sites_main = base_dir / 'data/raw/sites.json'

print("Fixing encoding issues...")
print("=" * 60)

fix_encoding(sites_test)
fix_encoding(sites_main)

print("=" * 60)
print("Encoding fix complete!")
