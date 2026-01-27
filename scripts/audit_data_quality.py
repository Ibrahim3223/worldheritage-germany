"""
Phase 1: Data Quality Audit
Checks for geographic errors, duplicates, missing fields, and content issues
"""

import os
import re
import yaml
from collections import Counter, defaultdict
from pathlib import Path

def parse_frontmatter(content):
    """Extract YAML frontmatter from markdown"""
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                return yaml.safe_load(parts[1])
            except:
                return None
    return None

def audit_geographic_accuracy():
    """Check for geographic inconsistencies"""
    issues = []
    content_dir = Path('content/sites')

    # Countries that should NOT be in Germany dataset
    wrong_countries = ['poland', 'france', 'austria', 'czech', 'switzerland',
                       'netherlands', 'denmark', 'belgium', 'luxembourg']

    # Wrong regions (non-German regions)
    wrong_regions = ['subcarpathian', 'voivodeship', 'île-de-france',
                     'provence', 'catalonia', 'lombardy']

    for md_file in content_dir.glob('**/*.md'):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            fm = parse_frontmatter(content)

            if not fm:
                continue

            # Check country field
            country = fm.get('country', '').lower()
            if country and country != 'germany':
                issues.append({
                    'type': 'WRONG_COUNTRY',
                    'file': md_file.name,
                    'country': fm.get('country'),
                    'severity': 'CRITICAL'
                })

            # Check region field
            region = fm.get('region', '').lower()
            for wrong_region in wrong_regions:
                if wrong_region in region:
                    issues.append({
                        'type': 'WRONG_REGION',
                        'file': md_file.name,
                        'region': fm.get('region'),
                        'severity': 'CRITICAL'
                    })

            # Check content for wrong country mentions in location context
            content_lower = content.lower()
            for wrong_country in wrong_countries:
                # Only flag if it appears in a location context
                if re.search(rf'\b{wrong_country}\b.*(?:located|region|territory|voivodeship)',
                           content_lower):
                    issues.append({
                        'type': 'CONTENT_WRONG_COUNTRY',
                        'file': md_file.name,
                        'mention': wrong_country,
                        'severity': 'WARNING'
                    })

    return issues

def audit_duplicates():
    """Check for duplicate entries"""
    issues = []
    content_dir = Path('content/sites')

    titles = defaultdict(list)
    wikidata_ids = defaultdict(list)
    coords = defaultdict(list)

    for md_file in content_dir.glob('**/*.md'):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            fm = parse_frontmatter(content)

            if not fm:
                continue

            # Collect by title
            title = fm.get('title', '')
            if title:
                titles[title].append(md_file.name)

            # Collect by wikidata_id
            wikidata_id = fm.get('wikidata_id', '')
            if wikidata_id:
                wikidata_ids[wikidata_id].append(md_file.name)

            # Collect by coordinates (rounded)
            lat = fm.get('latitude', 0)
            lon = fm.get('longitude', 0)
            if lat and lon:
                coord_key = f"{round(lat, 3)},{round(lon, 3)}"
                coords[coord_key].append(md_file.name)

    # Find duplicates
    for title, files in titles.items():
        if len(files) > 1:
            issues.append({
                'type': 'DUPLICATE_TITLE',
                'title': title,
                'files': files,
                'count': len(files),
                'severity': 'WARNING'
            })

    for wikidata_id, files in wikidata_ids.items():
        if len(files) > 1:
            issues.append({
                'type': 'DUPLICATE_WIKIDATA',
                'wikidata_id': wikidata_id,
                'files': files,
                'count': len(files),
                'severity': 'CRITICAL'
            })

    return issues

def audit_missing_fields():
    """Check for missing required fields"""
    issues = []
    content_dir = Path('content/sites')

    required_fields = ['title', 'site_name', 'description', 'region', 'country',
                       'heritage_type', 'latitude', 'longitude', 'wikidata_id']

    stats = {field: 0 for field in required_fields}
    total_files = 0

    for md_file in content_dir.glob('**/*.md'):
        total_files += 1
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            fm = parse_frontmatter(content)

            if not fm:
                issues.append({
                    'type': 'NO_FRONTMATTER',
                    'file': md_file.name,
                    'severity': 'CRITICAL'
                })
                continue

            missing = []
            for field in required_fields:
                value = fm.get(field)
                if not value or (isinstance(value, (int, float)) and value == 0):
                    missing.append(field)
                else:
                    stats[field] += 1

            if missing:
                issues.append({
                    'type': 'MISSING_FIELDS',
                    'file': md_file.name,
                    'missing': missing,
                    'severity': 'WARNING' if len(missing) < 3 else 'CRITICAL'
                })

    # Add completion stats
    completion = {field: f"{(count/total_files)*100:.1f}%"
                  for field, count in stats.items()}

    return issues, completion, total_files

def audit_content_quality():
    """Check for content quality issues"""
    issues = []
    content_dir = Path('content/sites')

    short_content = []
    very_short = []
    no_images = []

    for md_file in content_dir.glob('**/*.md'):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            fm = parse_frontmatter(content)

            if not fm:
                continue

            # Extract content after frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    body = parts[2].strip()
                else:
                    body = ""
            else:
                body = content

            # Check content length
            if len(body) < 200:
                very_short.append(md_file.name)
            elif len(body) < 500:
                short_content.append(md_file.name)

            # Check for images
            images = fm.get('images', [])
            if not images or len(images) == 0:
                no_images.append(md_file.name)

    if very_short:
        issues.append({
            'type': 'VERY_SHORT_CONTENT',
            'count': len(very_short),
            'examples': very_short[:5],
            'severity': 'WARNING'
        })

    if no_images:
        issues.append({
            'type': 'NO_IMAGES',
            'count': len(no_images),
            'percentage': f"{(len(no_images)/10174)*100:.1f}%",
            'severity': 'INFO'
        })

    return issues

def print_report(geographic, duplicates, missing, completion, total_files, quality):
    """Print formatted audit report"""

    print("=" * 80)
    print("AUDIT REPORT - PHASE 1: DATA QUALITY")
    print("=" * 80)
    print()

    # Critical Issues
    critical = [i for i in geographic + duplicates + missing if i.get('severity') == 'CRITICAL']
    if critical:
        print("🔴 CRITICAL ISSUES (Must fix immediately)")
        print("-" * 80)
        for i, issue in enumerate(critical[:20], 1):
            print(f"{i}. [{issue['type']}] {issue.get('file', '')}")
            for key, value in issue.items():
                if key not in ['type', 'severity', 'file']:
                    print(f"   - {key}: {value}")
        print(f"\nTotal critical issues: {len(critical)}")
        print()

    # Warnings
    warnings = [i for i in geographic + duplicates + missing + quality
                if i.get('severity') == 'WARNING']
    if warnings:
        print("🟡 WARNINGS (Should review)")
        print("-" * 80)
        for i, issue in enumerate(warnings[:10], 1):
            print(f"{i}. [{issue['type']}]")
            for key, value in issue.items():
                if key not in ['type', 'severity']:
                    if isinstance(value, list) and len(value) > 3:
                        print(f"   - {key}: {value[:3]} ... (+ {len(value)-3} more)")
                    else:
                        print(f"   - {key}: {value}")
        print(f"\nTotal warnings: {len(warnings)}")
        print()

    # Statistics
    print("📈 STATISTICS")
    print("-" * 80)
    print(f"Total files analyzed: {total_files}")
    print(f"Critical issues: {len(critical)}")
    print(f"Warnings: {len(warnings)}")
    print()
    print("Field Completion Rates:")
    for field, rate in sorted(completion.items()):
        print(f"  {field:20s}: {rate}")
    print()

    # Info
    info = [i for i in quality if i.get('severity') == 'INFO']
    if info:
        print("ℹ️  INFORMATION")
        print("-" * 80)
        for issue in info:
            print(f"[{issue['type']}]")
            for key, value in issue.items():
                if key not in ['type', 'severity']:
                    print(f"  - {key}: {value}")
        print()

    # Summary
    print("✅ ACTION ITEMS")
    print("-" * 80)
    print(f"[ ] Fix {len(critical)} critical issues")
    print(f"[ ] Review {len(warnings)} warnings")
    print(f"[ ] Improve content for {info[0]['count'] if info else 0} pages with no images")
    print()

if __name__ == "__main__":
    print("Starting Phase 1: Data Quality Audit...")
    print()

    print("1/4 Checking geographic accuracy...")
    geographic = audit_geographic_accuracy()

    print("2/4 Checking for duplicates...")
    duplicates = audit_duplicates()

    print("3/4 Checking missing fields...")
    missing, completion, total_files = audit_missing_fields()

    print("4/4 Checking content quality...")
    quality = audit_content_quality()

    print()
    print_report(geographic, duplicates, missing, completion, total_files, quality)
