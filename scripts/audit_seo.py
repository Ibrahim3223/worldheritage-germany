"""
Phase 4: SEO & Performance Validation
Checks SEO meta tags, internal links, and site structure
"""

import os
from pathlib import Path
import re
from collections import defaultdict

def check_meta_tags():
    """Check for missing or poor SEO meta tags"""

    issues = []
    content_dir = Path('content/sites')

    stats = {
        'total': 0,
        'missing_description': 0,
        'short_description': 0,
        'long_description': 0,
        'missing_title': 0,
        'no_images': 0,
    }

    for md_file in content_dir.glob('**/*.md'):
        stats['total'] += 1

        with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

            # Check for frontmatter
            if not content.startswith('---'):
                continue

            # Extract frontmatter
            parts = content.split('---', 2)
            if len(parts) < 3:
                continue

            fm = parts[1]

            # Check description
            desc_match = re.search(r'description:\s*"([^"]*)"', fm)
            if not desc_match:
                stats['missing_description'] += 1
            else:
                desc = desc_match.group(1)
                if len(desc) < 50:
                    stats['short_description'] += 1
                elif len(desc) > 160:
                    stats['long_description'] += 1

            # Check title
            if 'title:' not in fm and 'site_name:' not in fm:
                stats['missing_title'] += 1

            # Check images
            if 'images:' not in content or re.search(r'images:\s*\[\s*\]', content):
                stats['no_images'] += 1

    return stats

def check_sitemap():
    """Check if sitemap exists and is valid"""

    sitemap_path = Path('public/sitemap.xml')

    if not sitemap_path.exists():
        return {
            'exists': False,
            'url_count': 0,
            'error': 'Sitemap not found (need to build site first)'
        }

    try:
        with open(sitemap_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # Count URLs
            url_count = content.count('<loc>')

            return {
                'exists': True,
                'url_count': url_count,
                'size': sitemap_path.stat().st_size,
            }
    except:
        return {
            'exists': False,
            'error': 'Could not read sitemap'
        }

def check_config_seo():
    """Check config.toml for SEO settings"""

    config_path = Path('config.toml')
    issues = []

    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()

        # Check for essential settings
        if 'baseURL' not in content:
            issues.append('Missing baseURL')

        if 'title' not in content:
            issues.append('Missing title')

        if 'description' not in content:
            issues.append('Missing description')

        # Check sitemap config
        if '[sitemap]' not in content:
            issues.append('Missing sitemap configuration')

        # Check if minification is enabled
        if 'minifyOutput = true' not in content:
            issues.append('Minification not enabled')

    return issues

def analyze_site_structure():
    """Analyze site structure and organization"""

    stats = {
        'total_sites': 0,
        'regions': defaultdict(int),
        'heritage_types': defaultdict(int),
        'unesco_sites': 0,
    }

    content_dir = Path('content/sites')

    for md_file in content_dir.glob('**/*.md'):
        stats['total_sites'] += 1

        with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

            # Extract region
            region_match = re.search(r'region:\s*"([^"]*)"', content)
            if region_match:
                stats['regions'][region_match.group(1)] += 1

            # Extract heritage type
            type_match = re.search(r'heritage_type:\s*"([^"]*)"', content)
            if type_match:
                stats['heritage_types'][type_match.group(1)] += 1

            # Check if UNESCO
            if 'unesco' in content.lower() or 'tags:\n  - unesco' in content:
                stats['unesco_sites'] += 1

    return stats

def print_report(meta_stats, sitemap_info, config_issues, structure_stats):
    """Print SEO & Performance audit report"""

    print("Starting Phase 4: SEO & Performance Validation")
    print("=" * 80)
    print()

    # Meta Tags
    print("[*] META TAGS ANALYSIS")
    print("-" * 80)

    total = meta_stats['total']
    print(f"Total sites analyzed: {total:,}")
    print()

    desc_ok = total - meta_stats['missing_description'] - meta_stats['short_description'] - meta_stats['long_description']
    desc_ok_pct = (desc_ok / total * 100) if total > 0 else 0

    print(f"Description Quality:")
    print(f"  [+] Good (50-160 chars):    {desc_ok:,} ({desc_ok_pct:.1f}%)")
    print(f"  [!] Missing:                {meta_stats['missing_description']:,}")
    print(f"  [!] Too short (<50 chars):  {meta_stats['short_description']:,}")
    print(f"  [!] Too long (>160 chars):  {meta_stats['long_description']:,}")
    print()

    if meta_stats['missing_title'] > 0:
        print(f"[!] Missing titles: {meta_stats['missing_title']}")
    else:
        print("[+] All sites have titles")
    print()

    images_pct = ((total - meta_stats['no_images']) / total * 100) if total > 0 else 0
    print(f"Images: {total - meta_stats['no_images']:,} sites ({images_pct:.1f}%)")
    print()

    # Sitemap
    print("[*] SITEMAP VALIDATION")
    print("-" * 80)

    if sitemap_info['exists']:
        print(f"[+] Sitemap exists: public/sitemap.xml")
        print(f"    URLs: {sitemap_info['url_count']:,}")
        print(f"    Size: {sitemap_info['size']:,} bytes")
    else:
        print(f"[!] {sitemap_info.get('error', 'Sitemap not found')}")
    print()

    # Config
    print("[*] CONFIG SEO SETTINGS")
    print("-" * 80)

    if config_issues:
        for issue in config_issues:
            print(f"[!] {issue}")
    else:
        print("[+] All essential SEO settings present")
    print()

    # Site Structure
    print("[*] SITE STRUCTURE")
    print("-" * 80)
    print(f"Total heritage sites: {structure_stats['total_sites']:,}")
    print(f"UNESCO sites: {structure_stats['unesco_sites']}")
    print(f"Regions: {len(structure_stats['regions'])}")
    print(f"Heritage types: {len(structure_stats['heritage_types'])}")
    print()

    print("Top 5 Regions:")
    for region, count in sorted(structure_stats['regions'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {region:30s}: {count:4d} sites")
    print()

    print("Top 5 Heritage Types:")
    for htype, count in sorted(structure_stats['heritage_types'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {htype:30s}: {count:4d} sites")
    print()

    # Summary
    print("=" * 80)
    print("[*] SEO HEALTH SCORE")
    print("=" * 80)
    print()

    # Calculate score
    score_items = []

    # Meta descriptions (40 points)
    meta_score = (desc_ok / total * 40) if total > 0 else 0
    score_items.append(('Meta Descriptions', meta_score, 40))

    # Titles (20 points)
    title_score = ((total - meta_stats['missing_title']) / total * 20) if total > 0 else 0
    score_items.append(('Titles', title_score, 20))

    # Images (20 points)
    image_score = ((total - meta_stats['no_images']) / total * 20) if total > 0 else 0
    score_items.append(('Images', image_score, 20))

    # Config (10 points)
    config_score = 10 if not config_issues else 5
    score_items.append(('Config', config_score, 10))

    # Sitemap (10 points)
    sitemap_score = 10 if sitemap_info['exists'] else 0
    score_items.append(('Sitemap', sitemap_score, 10))

    total_score = sum(s for _, s, _ in score_items)

    for name, score, max_score in score_items:
        bar_length = 20
        filled = int((score / max_score) * bar_length)
        bar = '[' + '=' * filled + ' ' * (bar_length - filled) + ']'
        print(f"{name:20s} {bar} {score:5.1f}/{max_score}")

    print()
    print(f"TOTAL SEO SCORE: {total_score:.1f}/100")
    print()

    if total_score >= 90:
        grade = "A+ (Excellent)"
    elif total_score >= 80:
        grade = "A (Very Good)"
    elif total_score >= 70:
        grade = "B (Good)"
    elif total_score >= 60:
        grade = "C (Fair)"
    else:
        grade = "D (Needs Improvement)"

    print(f"Grade: {grade}")
    print()

    # Recommendations
    print("[ACTION] RECOMMENDATIONS")
    print("-" * 80)

    if meta_stats['missing_description'] > 100:
        print(f"[ ] Add descriptions to {meta_stats['missing_description']} sites")

    if meta_stats['short_description'] > 100:
        print(f"[ ] Expand {meta_stats['short_description']} short descriptions")

    if meta_stats['no_images'] > 2000:
        print(f"[ ] Run image import for {meta_stats['no_images']} sites")

    if not sitemap_info['exists']:
        print("[ ] Build site to generate sitemap (hugo --minify)")

    if config_issues:
        print("[ ] Fix config.toml SEO issues")

    if not any([
        meta_stats['missing_description'] > 100,
        meta_stats['short_description'] > 100,
        meta_stats['no_images'] > 2000,
        not sitemap_info['exists'],
        config_issues
    ]):
        print("[+] No critical SEO issues - site is well optimized!")

    print()

if __name__ == "__main__":
    # Run checks
    print("Running SEO audit...")
    print()

    meta_stats = check_meta_tags()
    sitemap_info = check_sitemap()
    config_issues = check_config_seo()
    structure_stats = analyze_site_structure()

    # Print report
    print_report(meta_stats, sitemap_info, config_issues, structure_stats)
