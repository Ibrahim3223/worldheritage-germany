"""
Fix all encoding issues using ftfy library
"""

import json
from pathlib import Path
import ftfy

def fix_text(text):
    """Fix encoding using ftfy"""
    if not isinstance(text, str):
        return text
    # ftfy can fix multiple layers of encoding issues
    return ftfy.fix_text(text)

def fix_json_data(data):
    """Recursively fix encoding in JSON data"""
    if isinstance(data, dict):
        return {key: fix_json_data(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [fix_json_data(item) for item in data]
    elif isinstance(data, str):
        return fix_text(data)
    else:
        return data

def process_file(file_path):
    """Process a single JSON file"""
    try:
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Fix encoding issues
        fixed_data = fix_json_data(data)

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(fixed_data, f, ensure_ascii=False, indent=2)

        print(f"Fixed: {file_path.name}")
        return True
    except Exception as e:
        print(f"Error fixing {file_path.name}: {e}")
        return False

# Fix both files
base_dir = Path(__file__).parent.parent
sites_test = base_dir / 'data/raw/sites_test.json'
sites_main = base_dir / 'data/raw/sites.json'

print("Fixing encoding with ftfy...")
print("=" * 60)

process_file(sites_test)
process_file(sites_main)

print("=" * 60)
print("Done! All encoding issues fixed.")
