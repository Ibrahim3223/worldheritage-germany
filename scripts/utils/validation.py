#!/usr/bin/env python3
"""
Validate WorldHeritage Germany project structure and content
Run this script to check for common issues before deployment
"""

import re
from pathlib import Path
from collections import Counter

SITES_DIR = Path("content/sites")

# German states list
VALID_REGIONS = {
    "Baden-Württemberg", "Bavaria", "Berlin", "Brandenburg", "Bremen",
    "Hamburg", "Hesse", "Lower Saxony", "Mecklenburg-Vorpommern",
    "North Rhine-Westphalia", "Rhineland-Palatinate", "Saarland",
    "Saxony", "Saxony-Anhalt", "Schleswig-Holstein", "Thuringia"
}

def validate_frontmatter():
    """Check frontmatter structure and content"""
    issues = []
    stats = {
        'total_files': 0,
        'missing_description': 0,
        'missing_regions_taxonomy': 0,
        'invalid_region': 0,
        'quote_issues': 0,
        'too_many_images': 0,
        'missing_wikidata': 0,
    }

    for md_file in SITES_DIR.glob("*.md"):
        if md_file.name == "_index.md":
            continue

        stats['total_files'] += 1
        content = md_file.read_text(encoding='utf-8')

        # Check for frontmatter
        if not content.startswith('---'):
            issues.append(f"[X] {md_file.name}: Missing frontmatter")
            continue

        parts = content.split('---')
        if len(parts) < 3:
            issues.append(f"[X] {md_file.name}: Malformed frontmatter")
            continue

        frontmatter = parts[1]

        # Check for required fields
        if not re.search(r'description:', frontmatter):
            stats['missing_description'] += 1
            issues.append(f"[!] {md_file.name}: Missing description field")

        if not re.search(r'regions:', frontmatter):
            stats['missing_regions_taxonomy'] += 1
            issues.append(f"[!] {md_file.name}: Missing regions taxonomy")

        if not re.search(r'wikidata_id:', frontmatter):
            stats['missing_wikidata'] += 1

        # Check region validity
        region_match = re.search(r'region:\s*"([^"]+)"', frontmatter)
        if region_match:
            region = region_match.group(1)
            if region not in VALID_REGIONS:
                stats['invalid_region'] += 1
                issues.append(f"[!] {md_file.name}: Invalid region '{region}'")

        # Check for quote issues
        if re.search(r":\s*'[^']*\"", frontmatter) or re.search(r":\s*\"[^\"]*'", frontmatter):
            stats['quote_issues'] += 1
            issues.append(f"[X] {md_file.name}: Mixed quotes detected")

        # Check image count
        image_lines = re.findall(r'^\s*-\s*"/images-sites/', frontmatter, re.MULTILINE)
        if len(image_lines) > 20:  # More than 5 images × 4 sizes
            stats['too_many_images'] += 1
            issues.append(f"[!] {md_file.name}: Too many images ({len(image_lines)} lines)")

    return issues, stats

def validate_images():
    """Check image directory structure"""
    issues = []
    image_dir = Path("static/images-sites")

    if not image_dir.exists():
        issues.append("[!] static/images-sites directory not found")
        return issues

    site_dirs = list(image_dir.glob("*/"))
    total_images = 0

    for site_dir in site_dirs:
        images = list(site_dir.glob("*.webp"))
        total_images += len(images)

        if len(images) > 20:
            issues.append(f"[!] {site_dir.name}: Has {len(images)} images (recommended max: 20)")

    print(f"\n[STATS] Image Statistics:")
    print(f"   - Total site directories: {len(site_dirs)}")
    print(f"   - Total images: {total_images}")

    if total_images > 5000:
        issues.append(f"[!] Total images ({total_images}) exceeds recommended limit (5000)")

    return issues

def validate_categories():
    """List all unique categories found"""
    categories = []

    for md_file in SITES_DIR.glob("*.md"):
        if md_file.name == "_index.md":
            continue

        content = md_file.read_text(encoding='utf-8')
        cat_matches = re.findall(r'categories:\s*\n((?:\s+-\s+"[^"]+"\s*\n)+)', content)

        for match in cat_matches:
            cats = re.findall(r'-\s+"([^"]+)"', match)
            categories.extend(cats)

    category_counts = Counter(categories)

    print(f"\n[STATS] Category Statistics:")
    for cat, count in category_counts.most_common():
        print(f"   - {cat}: {count} sites")

    return []

def validate_regions_distribution():
    """Check how sites are distributed across regions"""
    regions = []

    for md_file in SITES_DIR.glob("*.md"):
        if md_file.name == "_index.md":
            continue

        content = md_file.read_text(encoding='utf-8')
        region_match = re.search(r'region:\s*"([^"]+)"', content)

        if region_match:
            regions.append(region_match.group(1))

    region_counts = Counter(regions)

    print(f"\n[STATS] Regional Distribution:")
    for region, count in sorted(region_counts.items()):
        marker = "[OK]" if region in VALID_REGIONS else "[!]"
        print(f"   {marker} {region}: {count} sites")

    # Check for regions with no sites
    for region in VALID_REGIONS:
        if region not in region_counts:
            print(f"   [!] {region}: 0 sites")

    return []

def main():
    """Run all validation checks"""
    print("=" * 60)
    print("WorldHeritage Germany - Project Validation")
    print("=" * 60)

    all_issues = []

    # Validate frontmatter
    print("\n[*] Checking frontmatter...")
    fm_issues, fm_stats = validate_frontmatter()
    all_issues.extend(fm_issues)

    print(f"\n[STATS] Frontmatter Statistics:")
    print(f"   - Total site files: {fm_stats['total_files']}")
    print(f"   - Missing descriptions: {fm_stats['missing_description']}")
    print(f"   - Missing regions taxonomy: {fm_stats['missing_regions_taxonomy']}")
    print(f"   - Invalid regions: {fm_stats['invalid_region']}")
    print(f"   - Quote issues: {fm_stats['quote_issues']}")
    print(f"   - Too many images: {fm_stats['too_many_images']}")
    print(f"   - Missing Wikidata ID: {fm_stats['missing_wikidata']}")

    # Validate images
    print("\n[*] Checking images...")
    img_issues = validate_images()
    all_issues.extend(img_issues)

    # Validate categories
    print("\n[*] Checking categories...")
    cat_issues = validate_categories()
    all_issues.extend(cat_issues)

    # Validate regions
    print("\n[*] Checking regional distribution...")
    reg_issues = validate_regions_distribution()
    all_issues.extend(reg_issues)

    # Summary
    print("\n" + "=" * 60)
    if all_issues:
        print(f"\n[!] Found {len(all_issues)} issues:\n")
        for issue in all_issues[:20]:  # Show first 20
            print(f"   {issue}")
        if len(all_issues) > 20:
            print(f"\n   ... and {len(all_issues) - 20} more issues")
    else:
        print("\n[OK] No critical issues found!")

    print("\n" + "=" * 60)
    print("Validation complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
