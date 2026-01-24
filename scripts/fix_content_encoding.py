"""
Fix encoding in all content JSON files
"""

import json
from pathlib import Path
import ftfy

def fix_text(text):
    """Fix encoding using ftfy"""
    if not isinstance(text, str):
        return text
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

# Fix all content files
base_dir = Path(__file__).parent.parent
content_dir = base_dir / 'data/content'

print("Fixing encoding in content files...")
print("=" * 60)

fixed_count = 0
for content_file in content_dir.glob('*.json'):
    try:
        # Read file
        with open(content_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Fix encoding
        fixed_data = fix_json_data(data)

        # Write back
        with open(content_file, 'w', encoding='utf-8') as f:
            json.dump(fixed_data, f, ensure_ascii=False, indent=2)

        fixed_count += 1
        print(f"Fixed: {content_file.name}")
    except Exception as e:
        print(f"Error: {content_file.name}: {e}")

print("=" * 60)
print(f"Fixed {fixed_count} content files")
