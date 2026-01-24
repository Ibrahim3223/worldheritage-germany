"""
Fix double-encoding issues in JSON files
Common issue: UTF-8 text encoded as Latin-1, then as UTF-8 again
"""

import json
from pathlib import Path

def fix_double_encoded_string(text):
    """Fix common double-encoding issues"""
    if not isinstance(text, str):
        return text

    # Common double-encoding patterns
    replacements = {
        'Ã¤': 'ä',
        'Ã¶': 'ö',
        'Ã¼': 'ü',
        'ÃŸ': 'ß',
        'Ã„': 'Ä',
        'Ã–': 'Ö',
        'Ãœ': 'Ü',
        'Ã©': 'é',
        'Ã¨': 'è',
        'Ã ': 'à',
        'Ã§': 'ç',
        'Ãª': 'ê',
        'NÃ¶rdliche': 'Nördliche',
        'VorstÃ¤dte': 'Vorstädte',
        'SchlÃ¼ter': 'Schlüter',
        'ÃÆÃÂ': '',  # Remove garbage
        'ÃÆ': '',    # Remove garbage
        'Ã‚': '',    # Remove garbage
    }

    result = text
    for old, new in replacements.items():
        result = result.replace(old, new)

    return result

def fix_json_data(data):
    """Recursively fix encoding in JSON data"""
    if isinstance(data, dict):
        return {key: fix_json_data(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [fix_json_data(item) for item in data]
    elif isinstance(data, str):
        return fix_double_encoded_string(data)
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

print("Fixing double-encoding issues...")
print("=" * 60)

process_file(sites_test)
process_file(sites_main)

print("=" * 60)
print("Done!")
