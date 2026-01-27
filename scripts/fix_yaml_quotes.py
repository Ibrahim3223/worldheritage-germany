"""
Fix YAML quotes in description fields
Replace unescaped quotes inside description values
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
CONTENT_DIR = BASE_DIR / 'content' / 'sites'

FILES_TO_FIX = [
    '2000-jahre-christentum.md',
    'chronos-und-die-trauernde.md',
    'der-gescheiterte-varus.md',
    'fallturm-bremen.md',
    'gedenkstaette-museum-in-der-runden-ecke.md',
    'helm-ab-zum-gebet.md',
    'juratrockenhang-mit-der-felsgruppe-zwoelf-apostel.md',
    'luegenmuseum.md',
    'maerchenbrunnen-wuppertal.md',
    'munich-fair-tower.md',
    'nubian-woman.md',
    'phonomuseum-alte-schule.md',
    'rakotzbruecke.md',
    'schloss-nordkirchen.md',
    'the-sower.md',
]

def fix_description_quotes(content: str) -> str:
    """Fix quotes in description field"""

    lines = content.split('\n')
    fixed_lines = []

    for line in lines:
        # Check if this is a description line
        if line.strip().startswith('description:'):
            # Extract the description value
            match = re.match(r'(\s*description:\s*)"(.+)"', line)
            if match:
                prefix = match.group(1)
                desc_value = match.group(2)

                # Escape any unescaped quotes in the value
                # Replace " with \" but preserve already escaped ones
                fixed_value = desc_value.replace('\\', '\\\\').replace('"', '\\"')

                fixed_line = f'{prefix}"{fixed_value}"'
                fixed_lines.append(fixed_line)
                print(f"  Fixed description line")
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)

    return '\n'.join(fixed_lines)

def main():
    print("="*80)
    print("FIX YAML QUOTES IN DESCRIPTIONS")
    print("="*80)
    print()

    fixed = 0

    for filename in FILES_TO_FIX:
        file_path = CONTENT_DIR / filename

        if not file_path.exists():
            print(f"SKIP: {filename} (not found)")
            continue

        print(f"Processing: {filename}")

        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Fix quotes
            fixed_content = fix_description_quotes(content)

            # Write back
            with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(fixed_content)

            fixed += 1

        except Exception as e:
            print(f"  ERROR: {e}")

    print()
    print(f"Fixed: {fixed}/{len(FILES_TO_FIX)}")
    print()
    print("DONE!")

if __name__ == '__main__':
    main()
