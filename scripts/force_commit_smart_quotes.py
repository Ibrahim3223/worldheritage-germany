"""
Force commit all smart quote changes by adding a trailing newline
"""

from pathlib import Path
from tqdm import tqdm

BASE_DIR = Path(__file__).parent.parent
CONTENT_DIR = BASE_DIR / 'content' / 'sites'

# Smart quotes to replace
SMART_QUOTES = {
    '"': '"',
    '"': '"',
    ''': "'",
    ''': "'",
}

def process_file(file_path: Path) -> bool:
    """Replace smart quotes and ensure file is modified"""

    try:
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Replace smart quotes
        modified = False
        for smart, regular in SMART_QUOTES.items():
            if smart in content:
                content = content.replace(smart, regular)
                modified = True

        if modified:
            # Write back with LF line endings
            with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"\nERROR: {file_path.name}: {e}")
        return False

def main():
    print("="*80)
    print("FORCE COMMIT SMART QUOTES FIX")
    print("="*80)
    print()

    files = list(CONTENT_DIR.glob('*.md'))
    print(f"Total files: {len(files)}")
    print()

    modified = 0
    errors = 0

    for file_path in tqdm(files, desc="Processing"):
        if process_file(file_path):
            modified += 1

    print()
    print(f"Modified: {modified}/{len(files)}")
    print(f"Errors: {errors}")
    print()
    print("DONE!")

if __name__ == '__main__':
    main()
