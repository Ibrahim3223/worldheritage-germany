"""
Fix duplicate descriptions caused by incorrect regex pattern
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
CONTENT_DIR = BASE_DIR / 'content' / 'sites'

def fix_duplicate_description(file_path: Path):
    """Fix files with duplicate descriptions"""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if it has duplicate description
    # Pattern: description: "...\"..." followed by more text on same line
    if not re.search(r'description:\s*"[^"]*\\"[^"]*"[^"\n]', content):
        return False

    # Split into frontmatter and body
    if not content.startswith('---'):
        return False

    parts = content.split('---', 2)
    if len(parts) < 3:
        return False

    frontmatter = parts[1]
    body = parts[2]

    # Extract the description line
    desc_match = re.search(r'description:\s*(.+)', frontmatter)
    if not desc_match:
        return False

    desc_line = desc_match.group(1)

    # Find the first closing quote (accounting for escaped quotes)
    # We need to find: opening ", then content with possible \", then closing "
    # Pattern: starts with ", ends with first unescaped "

    # Simple approach: Split at ..."[space or newline] pattern
    # The description should end at the first " followed by newline or another field

    # Use a more robust pattern: Find content between first " and last " followed by newline
    match = re.match(r'"(.+?)"\s*$', desc_line)
    if match:
        # Already correct format
        return False

    # Find the end of the actual description (first " that's NOT escaped)
    i = 0
    if desc_line[0] == '"':
        i = 1
        in_escape = False
        while i < len(desc_line):
            if in_escape:
                in_escape = False
                i += 1
                continue

            if desc_line[i] == '\\':
                in_escape = True
                i += 1
                continue

            if desc_line[i] == '"':
                # Found closing quote
                correct_desc = desc_line[:i+1]

                # Replace in frontmatter
                new_frontmatter = frontmatter.replace(desc_line, correct_desc)

                # Reconstruct
                new_content = f'---{new_frontmatter}---{body}'

                # Write back
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                print(f"Fixed: {file_path.name}")
                return True

            i += 1

    return False

def main():
    print("="*80)
    print("FIX DUPLICATE DESCRIPTIONS")
    print("="*80)
    print()

    fixed = 0
    errors = 0

    # Process all markdown files
    for md_file in CONTENT_DIR.glob('*.md'):
        try:
            if fix_duplicate_description(md_file):
                fixed += 1
        except Exception as e:
            print(f"ERROR: {md_file.name}: {e}")
            errors += 1

    print()
    print(f"Fixed: {fixed}")
    print(f"Errors: {errors}")
    print()
    print("DONE!")

if __name__ == '__main__':
    main()
