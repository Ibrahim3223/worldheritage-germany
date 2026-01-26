"""
Analyze all content files to identify issues
"""
from pathlib import Path
import re
import json

def analyze_file(filepath):
    """Analyze a single file for issues"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    issues = []

    # Check for wikidata_id
    has_wikidata = bool(re.search(r'wikidata_id:', content))
    if not has_wikidata:
        issues.append('no_wikidata_id')

    # Check for region: Germany
    has_region_germany = bool(re.search(r'^region:\s*Germany\s*$', content, re.MULTILINE))
    if has_region_germany:
        issues.append('region_germany')

    # Check for site_name
    has_site_name = bool(re.search(r'^site_name:', content, re.MULTILINE))
    if not has_site_name:
        issues.append('no_site_name')

    # Check for images
    has_images = bool(re.search(r'^images:', content, re.MULTILINE))
    if not has_images:
        issues.append('no_images')

    # Check for broken thumbnail images
    if has_images:
        images_section = re.search(r'^images:\n((?:- .*\n)+)', content, re.MULTILINE)
        if images_section:
            first_image = images_section.group(1).split('\n')[0]
            if 'thumbnail' in first_image.lower() or 'thumb.jpg' in first_image.lower():
                issues.append('broken_thumbnail')

    # Check for tags
    has_tags = bool(re.search(r'^tags:', content, re.MULTILINE))

    return issues, has_wikidata, has_tags

def main():
    content_dir = Path('content/sites')

    stats = {
        'total': 0,
        'no_wikidata_id': 0,
        'region_germany': 0,
        'no_site_name': 0,
        'no_images': 0,
        'broken_thumbnail': 0,
        'has_tags': 0,
        'no_issues': 0,
    }

    files_by_issue = {
        'no_wikidata_id': [],
        'region_germany': [],
        'no_site_name': [],
        'no_images': [],
        'broken_thumbnail': [],
    }

    for filepath in content_dir.glob('*.md'):
        stats['total'] += 1
        issues, has_wikidata, has_tags = analyze_file(filepath)

        if has_tags:
            stats['has_tags'] += 1

        if not issues:
            stats['no_issues'] += 1
        else:
            for issue in issues:
                stats[issue] += 1
                if len(files_by_issue[issue]) < 5:  # Store first 5 examples
                    files_by_issue[issue].append(filepath.name)

    # Print report
    print("=" * 60)
    print("CONTENT FILES ANALYSIS REPORT")
    print("=" * 60)
    print(f"\nTotal files: {stats['total']}")
    print(f"Files with NO issues: {stats['no_issues']}")
    print(f"\nISSUES FOUND:")
    print(f"  - Missing wikidata_id: {stats['no_wikidata_id']} files")
    print(f"  - Region is 'Germany': {stats['region_germany']} files")
    print(f"  - Missing site_name: {stats['no_site_name']} files")
    print(f"  - Missing images: {stats['no_images']} files")
    print(f"  - Broken thumbnail: {stats['broken_thumbnail']} files")
    print(f"\n  - Files with tags: {stats['has_tags']} files")

    print("\n" + "=" * 60)
    print("SAMPLE FILES WITH ISSUES:")
    print("=" * 60)
    for issue, files in files_by_issue.items():
        if files:
            print(f"\n{issue}:")
            for f in files[:3]:
                print(f"  - {f}")

    # Calculate priority
    print("\n" + "=" * 60)
    print("FIX PRIORITY:")
    print("=" * 60)
    print(f"1. Add wikidata_id: {stats['no_wikidata_id']} files (HIGH - needed for all other fixes)")
    print(f"2. Fix region: {stats['region_germany']} files (HIGH - user visibility)")
    print(f"3. Add site_name: {stats['no_site_name']} files (MEDIUM - affects cards)")
    print(f"4. Fix broken thumbnails: {stats['broken_thumbnail']} files (MEDIUM - affects images)")
    print(f"5. Add missing images: {stats['no_images']} files (LOW - may not have images)")

if __name__ == '__main__':
    main()
