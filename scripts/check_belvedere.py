import json
import sys

# Set UTF-8 for stdout
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('data/raw/sites_test.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

belv = [s for s in data if 'Belvedere' in s['name']][0]
region = belv['region']

# Print as repr to see exact bytes
print(f"Region (repr): {repr(region)}")
print(f"Region (len): {len(region)}")

# Try to fix if needed
if 'N\x83\xb6rdliche' in region:
    print("Found \\x83\\xb6 - this is incorrect")
    fixed = region.replace('N\x83\xb6rdliche', 'Nördliche')
    fixed = fixed.replace('Vorst\x83\xa4dte', 'Vorstädte')
    print(f"Fixed: {repr(fixed)}")
