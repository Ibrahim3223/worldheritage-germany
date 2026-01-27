"""
Fix ALL files with unescaped quotes in descriptions
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
CONTENT_DIR = BASE_DIR / 'content' / 'sites'

def needs_fixing(content: str) -> bool:
    """Check if file needs quote fixing"""

    # Look for description line with unescaped quotes inside
    # Pattern: description: "...text "word" more text..."
    # This will have unescaped quotes that break YAML

    match = re.search(r'description:\s*"([^"]+)"', content, re.MULTILINE)
    if not match:
        return False

    desc_value = match.group(1)

    # Check if there are unescaped quotes (not preceded by backslash)
    # Look for " that is NOT \\"
    has_unescaped = bool(re.search(r'(?<!\\)"', desc_value))

    return has_unescaped

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

                # Check if it needs fixing (has unescaped quotes)
                if re.search(r'(?<!\\)"', desc_value):
                    # Escape any unescaped quotes in the value
                    # First unescape any already escaped quotes
                    desc_value = desc_value.replace('\\"', '"')
                    # Then escape all quotes
                    desc_value = desc_value.replace('"', '\\"')

                    fixed_line = f'{prefix}"{desc_value}"'
                    fixed_lines.append(fixed_line)
                    return '\n'.join(fixed_lines + lines[len(fixed_lines):])
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)

    return content

def main():
    print("="*80)
    print("FIX ALL YAML QUOTES IN DESCRIPTIONS")
    print("="*80)
    print()

    needs_fix = []

    # First pass: find all files that need fixing
    print("Scanning files...")
    for md_file in CONTENT_DIR.glob('*.md'):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if needs_fixing(content):
                needs_fix.append(md_file)
        except Exception as e:
            print(f"ERROR scanning {md_file.name}: {e}")

    print(f"Found {len(needs_fix)} files needing fixes")
    print()

    if not needs_fix:
        print("No files need fixing!")
        return

    # Show first 10
    print("Files to fix:")
    for f in needs_fix[:10]:
        print(f"  - {f.name}")
    if len(needs_fix) > 10:
        print(f"  ... and {len(needs_fix) - 10} more")
    print()

    # Second pass: fix all files
    fixed = 0
    errors = 0

    print("Fixing files...")
    for file_path in needs_fix:
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

            if fixed % 100 == 0:
                print(f"  Fixed {fixed}/{len(needs_fix)}...")

        except Exception as e:
            print(f"  ERROR: {file_path.name}: {e}")
            errors += 1

    print()
    print(f"Fixed: {fixed}/{len(needs_fix)}")
    print(f"Errors: {errors}")
    print()
    print("DONE!")

if __name__ == '__main__':
    main()
