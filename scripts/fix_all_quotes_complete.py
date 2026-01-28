"""
Complete fix: ALL quote types including German-style quotes
"""

from pathlib import Path
import sys

BASE_DIR = Path(__file__).parent.parent
CONTENT_DIR = BASE_DIR / 'content' / 'sites'

# ALL quote types mapping (binary)
REPLACEMENTS = {
    # English-style smart quotes
    b'\xe2\x80\x9c': b'"',  # " Left double quote (U+201C)
    b'\xe2\x80\x9d': b'"',  # " Right double quote (U+201D)
    b'\xe2\x80\x98': b"'",  # ' Left single quote (U+2018)
    b'\xe2\x80\x99': b"'",  # ' Right single quote (U+2019)

    # German-style quotes
    b'\xe2\x80\x9e': b'"',  # „ Double low-9 quote (U+201E)
    b'\xe2\x80\x9f': b'"',  # ‟ Double high-reversed-9 quote (U+201F)
    b'\xe2\x80\x9a': b"'",  # ‚ Single low-9 quote (U+201A)
    b'\xe2\x80\x9b': b"'",  # ‛ Single high-reversed-9 quote (U+201B)

    # Angle quotes (guillemets)
    b'\xc2\xab': b'"',      # « Left-pointing double angle quote (U+00AB)
    b'\xc2\xbb': b'"',      # » Right-pointing double angle quote (U+00BB)
    b'\xe2\x80\xb9': b"'",  # ‹ Single left-pointing angle quote (U+2039)
    b'\xe2\x80\xba': b"'",  # › Single right-pointing angle quote (U+203A)
}

def fix_file(file_path: Path) -> bool:
    """Fix all quote types in binary mode"""
    try:
        # Read as binary
        with open(file_path, 'rb') as f:
            content = f.read()

        # Check if needs fixing
        needs_fix = any(sq in content for sq in REPLACEMENTS.keys())

        if not needs_fix:
            return False

        # Replace all fancy quotes
        for fancy, regular in REPLACEMENTS.items():
            content = content.replace(fancy, regular)

        # Write back as binary
        with open(file_path, 'wb') as f:
            f.write(content)

        return True

    except Exception as e:
        print(f"ERROR: {file_path.name}: {e}", file=sys.stderr)
        return False

def main():
    print("="*80)
    print("COMPLETE QUOTES FIX - ALL TYPES")
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
