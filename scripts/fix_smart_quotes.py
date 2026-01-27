"""
Replace smart quotes with regular quotes in all markdown files
Smart quotes (curly quotes) break YAML parsing
"""

from pathlib import Path
from tqdm import tqdm

BASE_DIR = Path(__file__).parent.parent
CONTENT_DIR = BASE_DIR / 'content' / 'sites'

# Smart quotes to replace
SMART_QUOTES = {
    '"': '"',  # Left double quotation mark (U+201C)
    '"': '"',  # Right double quotation mark (U+201D)
    ''': "'",  # Left single quotation mark (U+2018)
    ''': "'",  # Right single quotation mark (U+2019)
}

def fix_smart_quotes(content: str) -> tuple[str, int]:
    """Replace all smart quotes with regular quotes"""

    replacements = 0
    for smart, regular in SMART_QUOTES.items():
        count = content.count(smart)
        if count > 0:
            content = content.replace(smart, regular)
            replacements += count

    return content, replacements

def main():
    print("="*80)
    print("FIX SMART QUOTES IN ALL FILES")
    print("="*80)
    print()

    files = list(CONTENT_DIR.glob('*.md'))
    print(f"Total files: {len(files)}")
    print()

    total_replacements = 0
    files_modified = 0
    errors = 0

    for file_path in tqdm(files, desc="Processing"):
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Fix smart quotes
            fixed_content, replacements = fix_smart_quotes(content)

            if replacements > 0:
                # Write back
                with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(fixed_content)

                files_modified += 1
                total_replacements += replacements

        except Exception as e:
            print(f"\nERROR: {file_path.name}: {e}")
            errors += 1

    print()
    print(f"Files modified: {files_modified}/{len(files)}")
    print(f"Total replacements: {total_replacements}")
    print(f"Errors: {errors}")
    print()
    print("DONE!")

if __name__ == '__main__':
    main()
