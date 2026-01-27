"""
Simple Data Quality Audit - No external dependencies
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def parse_frontmatter_simple(content):
    """Simple frontmatter parser without YAML dependency"""
    if not content.startswith('---'):
        return None

    parts = content.split('---', 2)
    if len(parts) < 3:
        return None

    fm_text = parts[1]
    fm = {}

    # Parse simple key: value pairs
    for line in fm_text.split('\n'):
        line = line.strip()
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip(' "\'')
            fm[key] = value

    return fm

def audit_critical_issues():
    """Check for critical geographic and data errors"""
    print("Starting Phase 1: Data Quality Audit (Simple Mode)")
    print("=" * 80)
    print()

    content_dir = Path('content/sites')
    total_files = 0
    issues = {
        'wrong_country': [],
        'wrong_region': [],
        'no_title': [],
        'no_description': [],
        'no_images': [],
        'duplicate_wikidata': defaultdict(list)
    }

    # German states for validation
    german_states = [
        'Baden-Württemberg', 'Bavaria', 'Berlin', 'Brandenburg', 'Bremen',
        'Hamburg', 'Hesse', 'Lower Saxony', 'Mecklenburg-Vorpommern',
        'North Rhine-Westphalia', 'Rhineland-Palatinate', 'Saarland',
        'Saxony', 'Saxony-Anhalt', 'Schleswig-Holstein', 'Thuringia'
    ]

    print("Scanning files...")
    for md_file in content_dir.glob('**/*.md'):
        total_files += 1

        if total_files % 1000 == 0:
            print(f"  Processed {total_files} files...")

        with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            fm = parse_frontmatter_simple(content)

            if not fm:
                continue

            # Check country
            country = fm.get('country', '').lower()
            if country and country != 'germany':
                issues['wrong_country'].append({
                    'file': md_file.name,
                    'country': fm.get('country')
                })

            # Check region - flag if not in German states
            region = fm.get('region', '')
            if region and region not in german_states:
                # Check if it's a suspicious region
                suspicious = ['Subcarpathian', 'Voivodeship', 'Île-de-France',
                             'Provence', 'Catalonia', 'Lombardy', 'Tuscany']
                for sus in suspicious:
                    if sus.lower() in region.lower():
                        issues['wrong_region'].append({
                            'file': md_file.name,
                            'region': region
                        })
                        break

            # Check required fields
            if not fm.get('title'):
                issues['no_title'].append(md_file.name)

            if not fm.get('description'):
                issues['no_description'].append(md_file.name)

            # Check images
            if 'images:' in content:
                # Simple check - look for empty array
                if re.search(r'images:\s*\[\s*\]', content):
                    issues['no_images'].append(md_file.name)
            else:
                issues['no_images'].append(md_file.name)

            # Track wikidata_id for duplicates
            wikidata_id = fm.get('wikidata_id')
            if wikidata_id:
                issues['duplicate_wikidata'][wikidata_id].append(md_file.name)

    print(f"\nTotal files scanned: {total_files}")
    print()

    # Print Report
    print("=" * 80)
    print("AUDIT RESULTS")
    print("=" * 80)
    print()

    # Critical Issues
    critical_count = len(issues['wrong_country']) + len(issues['wrong_region'])

    if critical_count > 0:
        print("[!] CRITICAL ISSUES")
        print("-" * 80)

        if issues['wrong_country']:
            print(f"\n[X] Wrong Country Field ({len(issues['wrong_country'])} files):")
            for item in issues['wrong_country'][:10]:
                print(f"   - {item['file']} -> country: {item['country']}")
            if len(issues['wrong_country']) > 10:
                print(f"   ... and {len(issues['wrong_country']) - 10} more")

        if issues['wrong_region']:
            print(f"\n[X] Suspicious Region ({len(issues['wrong_region'])} files):")
            for item in issues['wrong_region'][:10]:
                print(f"   - {item['file']} -> region: {item['region']}")
            if len(issues['wrong_region']) > 10:
                print(f"   ... and {len(issues['wrong_region']) - 10} more")

        # Check for duplicate Wikidata IDs
        duplicates = {k: v for k, v in issues['duplicate_wikidata'].items() if len(v) > 1}
        if duplicates:
            print(f"\n[X] Duplicate Wikidata IDs ({len(duplicates)} IDs):")
            for wid, files in list(duplicates.items())[:5]:
                print(f"   - {wid}: {files}")
            if len(duplicates) > 5:
                print(f"   ... and {len(duplicates) - 5} more")

        print()
    else:
        print("[OK] No critical geographic issues found!")
        print()

    # Warnings
    warning_count = len(issues['no_title']) + len(issues['no_description'])

    if warning_count > 0:
        print("[WARNING] WARNINGS")
        print("-" * 80)

        if issues['no_title']:
            print(f"[!] Missing Title: {len(issues['no_title'])} files")

        if issues['no_description']:
            print(f"[!] Missing Description: {len(issues['no_description'])} files")

        print()

    # Info
    print("[INFO] INFORMATION")
    print("-" * 80)
    print(f"Files without images: {len(issues['no_images'])} ({len(issues['no_images'])/total_files*100:.1f}%)")
    print()

    # Summary
    print("[*] SUMMARY")
    print("-" * 80)
    print(f"Total files: {total_files:,}")
    print(f"Critical issues: {critical_count}")
    print(f"Warnings: {warning_count}")
    print(f"Files need images: {len(issues['no_images'])}")
    print()

    print("[ACTION] NEXT ACTIONS")
    print("-" * 80)
    if critical_count > 0:
        print("[ ] Review and fix critical geographic issues")
    if duplicates:
        print("[ ] Resolve duplicate Wikidata entries")
    if len(issues['no_images']) > 5000:
        print("[ ] Consider running image import script")
    print()

    return issues

if __name__ == "__main__":
    audit_critical_issues()
