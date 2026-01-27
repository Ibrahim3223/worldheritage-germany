"""
SEO Description Enhancement Script
Extracts first sentence from content Overview section as SEO description
Germany-specific: Uses existing content, no GPT calls needed
"""

import os
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
CONTENT_DIR = BASE_DIR / 'content' / 'sites'

def extract_first_sentence_from_overview(content: str) -> str:
    """
    Extract first sentence from Overview section
    Remove 'Overview' prefix if present
    Target: 100-140 characters for optimal SEO
    """

    # Find Overview section
    # Pattern: ## Overview followed by content
    overview_match = re.search(r'##\s*Overview\s*\n\n(.*?)(?=\n##|\Z)', content, re.DOTALL)

    if not overview_match:
        # Try without header (some might start directly with content)
        # Get first paragraph after frontmatter
        parts = content.split('---', 2)
        if len(parts) >= 3:
            body = parts[2].strip()
            # Get first paragraph
            first_para = body.split('\n\n')[0].strip()
        else:
            return ""
    else:
        first_para = overview_match.group(1).strip()

    # Get first 1-2 sentences (until first '. ' or '! ' or '? ')
    sentences = re.split(r'(?<=[.!?])\s+', first_para)

    if not sentences:
        return ""

    # Take first sentence
    first_sentence = sentences[0].strip()

    # Remove "Overview" or "Overview:" or "Overview." from beginning
    first_sentence = re.sub(r'^Overview[:\.]?\s*', '', first_sentence, flags=re.IGNORECASE)

    # If too short, add second sentence
    if len(first_sentence) < 80 and len(sentences) > 1:
        second_sentence = sentences[1].strip()
        first_sentence = f"{first_sentence} {second_sentence}"

    # Clean up
    first_sentence = first_sentence.strip()

    # Ensure it ends with period
    if first_sentence and not first_sentence[-1] in '.!?':
        first_sentence += '.'

    # Truncate if too long (max 160 chars)
    if len(first_sentence) > 160:
        # Cut at last complete word before 160 chars
        truncated = first_sentence[:157]
        last_space = truncated.rfind(' ')
        if last_space > 100:  # Keep at least 100 chars
            first_sentence = truncated[:last_space] + '...'
        else:
            first_sentence = truncated + '...'

    return first_sentence

def update_frontmatter_description(file_path: Path, new_description: str):
    """
    Update description field in frontmatter
    Properly escape quotes for YAML
    """

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if it starts with frontmatter
    if not content.startswith('---'):
        return False

    parts = content.split('---', 2)
    if len(parts) < 3:
        return False

    frontmatter = parts[1]
    body = parts[2]

    # Escape quotes in description for YAML
    # Replace " with \" but only if not already escaped
    escaped_description = new_description.replace('\\', '\\\\').replace('"', '\\"')

    # Replace description
    # Pattern: description: "anything"
    if 'description:' in frontmatter:
        # Replace existing description
        new_frontmatter = re.sub(
            r'description:\s*"[^"]*"',
            f'description: "{escaped_description}"',
            frontmatter
        )
    else:
        # Add description after title
        new_frontmatter = re.sub(
            r'(title:[^\n]*\n)',
            r'\1description: "' + escaped_description + '"\n',
            frontmatter
        )

    # Reconstruct file
    new_content = f'---{new_frontmatter}---{body}'

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True

def analyze_current_descriptions():
    """
    Analyze current description quality
    """

    stats = {
        'total': 0,
        'missing': 0,
        'too_short': 0,  # < 50 chars
        'short': 0,      # 50-80 chars
        'good': 0,       # 80-140 chars
        'long': 0,       # 140-160 chars
        'too_long': 0,   # > 160 chars
    }

    for md_file in CONTENT_DIR.glob('**/*.md'):
        stats['total'] += 1

        with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

            # Extract description from frontmatter
            desc_match = re.search(r'description:\s*"([^"]*)"', content)

            if not desc_match:
                stats['missing'] += 1
                continue

            desc = desc_match.group(1)
            length = len(desc)

            if length < 50:
                stats['too_short'] += 1
            elif length < 80:
                stats['short'] += 1
            elif length < 140:
                stats['good'] += 1
            elif length <= 160:
                stats['long'] += 1
            else:
                stats['too_long'] += 1

    return stats

def enhance_all_descriptions(dry_run=False):
    """
    Enhance descriptions for all sites
    """

    print("=" * 80)
    print("SEO DESCRIPTION ENHANCEMENT")
    print("=" * 80)
    print()

    # Analyze current state
    print("Analyzing current descriptions...")
    stats_before = analyze_current_descriptions()

    print(f"Total sites: {stats_before['total']:,}")
    print(f"  Missing: {stats_before['missing']}")
    print(f"  Too short (<50): {stats_before['too_short']}")
    print(f"  Short (50-80): {stats_before['short']}")
    print(f"  Good (80-140): {stats_before['good']}")
    print(f"  Long (140-160): {stats_before['long']}")
    print(f"  Too long (>160): {stats_before['too_long']}")
    print()

    # Calculate target
    need_enhancement = stats_before['missing'] + stats_before['too_short'] + stats_before['short']

    print(f"Sites needing enhancement: {need_enhancement:,}")
    print()

    if dry_run:
        print("DRY RUN MODE - No files will be modified")
        print()

    # Process files
    updated = 0
    skipped = 0
    errors = 0

    print("Processing files...")
    print()

    for i, md_file in enumerate(CONTENT_DIR.glob('**/*.md'), 1):
        if i % 1000 == 0:
            print(f"  Processed {i:,} files... (updated: {updated}, skipped: {skipped})")

        try:
            with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Check current description
            desc_match = re.search(r'description:\s*"([^"]*)"', content)

            if desc_match:
                current_desc = desc_match.group(1)
                # Skip if description is already good (80+ chars)
                if len(current_desc) >= 80:
                    skipped += 1
                    continue

            # Extract new description from content
            new_desc = extract_first_sentence_from_overview(content)

            # Skip if extraction failed or too short
            if not new_desc or len(new_desc) < 50:
                skipped += 1
                continue

            # Update description
            if not dry_run:
                if update_frontmatter_description(md_file, new_desc):
                    updated += 1
                else:
                    errors += 1
            else:
                # In dry run, just count what would be updated
                updated += 1

                # Show first 5 examples
                if updated <= 5:
                    print(f"Example {updated}:")
                    print(f"  File: {md_file.name}")
                    print(f"  Old: {current_desc if desc_match else '(missing)'}")
                    print(f"  New: {new_desc}")
                    print(f"  Length: {len(new_desc)} chars")
                    print()

        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"ERROR: {md_file.name}: {str(e)}")

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"Total processed: {stats_before['total']:,}")
    print(f"Updated: {updated:,}")
    print(f"Skipped (already good): {skipped:,}")
    print(f"Errors: {errors}")
    print()

    if not dry_run:
        # Analyze after enhancement
        print("Analyzing results...")
        stats_after = analyze_current_descriptions()

        print()
        print("BEFORE vs AFTER:")
        print(f"  Too short (<50): {stats_before['too_short']} -> {stats_after['too_short']}")
        print(f"  Short (50-80): {stats_before['short']} -> {stats_after['short']}")
        print(f"  Good (80-140): {stats_before['good']} -> {stats_after['good']}")
        print(f"  Long (140-160): {stats_before['long']} -> {stats_after['long']}")
        print()

        # Calculate improvement
        before_good = stats_before['good'] + stats_before['long']
        after_good = stats_after['good'] + stats_after['long']
        improvement = after_good - before_good

        print(f"Good descriptions: {before_good:,} -> {after_good:,} (+{improvement:,})")

        # Calculate new SEO score
        if stats_after['total'] > 0:
            desc_score = (after_good / stats_after['total']) * 40
            total_seo_score = desc_score + 20 + 15.8 + 10 + 10  # desc + titles + images + config + sitemap
            print(f"Estimated new SEO score: {total_seo_score:.1f}/100")

            if total_seo_score >= 85:
                grade = "A (Excellent)"
            elif total_seo_score >= 75:
                grade = "B (Very Good)"
            elif total_seo_score >= 65:
                grade = "C (Good)"
            else:
                grade = "D (Fair)"

            print(f"Estimated grade: {grade}")

    print()
    print("DONE!")
    print()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Enhance SEO descriptions')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without modifying files')
    parser.add_argument('--run', action='store_true',
                       help='Actually modify files (required for real execution)')

    args = parser.parse_args()

    if not args.dry_run and not args.run:
        print("Please specify either --dry-run or --run")
        print()
        print("Usage:")
        print("  python scripts/enhance_descriptions.py --dry-run   # Preview changes")
        print("  python scripts/enhance_descriptions.py --run       # Apply changes")
        sys.exit(1)

    enhance_all_descriptions(dry_run=args.dry_run)
