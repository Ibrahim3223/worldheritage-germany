"""
Final fix: Replace ALL smart quotes in ALL files
Force write with binary mode to ensure Git sees changes
"""

from pathlib import Path
import sys

BASE_DIR = Path(__file__).parent.parent
CONTENT_DIR = BASE_DIR / 'content' / 'sites'

# Smart quotes mapping
REPLACEMENTS = {
    b'\xe2\x80\x9c': b'"',  # Left double quote
    b'\xe2\x80\x9d': b'"',  # Right double quote
    b'\xe2\x80\x98': b"'",  # Left single quote
    b'\xe2\x80\x99': b"'",  # Right single quote
}

def fix_file(file_path: Path) -> bool:
    """Fix smart quotes in binary mode"""
    try:
        # Read as binary
        with open(file_path, 'rb') as f:
            content = f.read()

        # Check if needs fixing
        needs_fix = any(sq in content for sq in REPLACEMENTS.keys())

        if not needs_fix:
            return False

        # Replace all smart quotes
        for smart, regular in REPLACEMENTS.items():
            content = content.replace(smart, regular)

        # Write back as binary
        with open(file_path, 'wb') as f:
            f.write(content)

        return True

    except Exception as e:
        print(f"ERROR: {file_path.name}: {e}", file=sys.stderr)
        return False

def main():
    print("="*80)
    print("FINAL SMART QUOTES FIX - BINARY MODE")
    print("="*80)
    print()

    files = sorted(CONTENT_DIR.glob('*.md'))
    print(f"Total files: {len(files)}")
    print()

    fixed = 0
    batch_size = 100

    for i, file_path in enumerate(files, 1):
        if fix_file(file_path):
            fixed += 1

        if i % batch_size == 0:
            print(f"Processed {i}/{len(files)} files... (fixed: {fixed})")

    print()
    print(f"Fixed: {fixed}/{len(files)}")
    print()
    print("DONE!")

if __name__ == '__main__':
    main()
