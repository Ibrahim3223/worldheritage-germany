"""
Fix unescaped quotes in YAML frontmatter
When we replaced German quotes with regular quotes, we didn't escape them for YAML
"""

from pathlib import Path
import re

BASE_DIR = Path(__file__).parent.parent
CONTENT_DIR = BASE_DIR / 'content' / 'sites'

def fix_yaml_quotes(content: str) -> tuple[str, bool]:
    """Fix unescaped quotes in YAML frontmatter"""
    lines = content.split('\n')
    modified = False

    # Process only frontmatter (between first two ---)
    in_frontmatter = False
    frontmatter_end = -1

    for i, line in enumerate(lines):
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
            else:
                frontmatter_end = i
                break

    if frontmatter_end == -1:
        return content, False

    # Fix quotes in frontmatter lines
    for i in range(1, frontmatter_end):
        line = lines[i]

        # Match YAML fields: key: "value"
        match = re.match(r'^(\w+): "(.+)"$', line)
        if match:
            key, value = match.groups()

            # Check if value has unescaped quotes
            if '"' in value and '\\"' not in value:
                # Escape inner quotes
                escaped_value = value.replace('"', '\\"')
                lines[i] = f'{key}: "{escaped_value}"'
                modified = True
                print(f"  Fixed {key}: {value[:50]}...")

    return '\n'.join(lines), modified

def main():
    print("=" * 80)
    print("FIX YAML QUOTES - Escape inner quotes in frontmatter")
    print("=" * 80)
    print()

    files = sorted(CONTENT_DIR.glob('*.md'))
    print(f"Total files: {len(files)}")
    print()

    fixed = 0

    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            new_content, modified = fix_yaml_quotes(content)

            if modified:
                with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(new_content)
                print(f"[OK] {file_path.name}")
                fixed += 1

        except Exception as e:
            print(f"[ERROR] {file_path.name}: {e}")

    print()
    print(f"Fixed: {fixed}/{len(files)}")
    print()
    print("DONE!")

if __name__ == '__main__':
    main()
