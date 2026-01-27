"""
Phase 3: Config Optimization & Multi-Country Preparation
Finds hardcoded country references and prepares for multi-country deployment
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def find_hardcoded_references():
    """Find all hardcoded Germany references in layouts"""

    results = defaultdict(list)
    layouts_dir = Path('layouts')

    patterns = {
        'germany': r'\bGermany(?:\'s)?\b',
        'german': r'\bGerman\b',
        'de_code': r'\bde\.worldheritage\b',
    }

    for html_file in layouts_dir.rglob('*.html'):
        with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')

            for line_num, line in enumerate(lines, 1):
                for pattern_name, pattern in patterns.items():
                    if re.search(pattern, line, re.IGNORECASE):
                        results[str(html_file)].append({
                            'line': line_num,
                            'content': line.strip(),
                            'pattern': pattern_name
                        })

    return results

def analyze_config():
    """Analyze config.toml for hardcoded values"""

    config_path = Path('config.toml')
    issues = []

    with open(config_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            # Check for hardcoded country references
            if 'Germany' in line:
                issues.append({
                    'line': line_num,
                    'content': line.strip(),
                    'type': 'HARDCODED_COUNTRY'
                })

            # Check for hardcoded country code
            if 'de.worldheritage' in line:
                issues.append({
                    'line': line_num,
                    'content': line.strip(),
                    'type': 'HARDCODED_COUNTRY_CODE'
                })

    return issues

def generate_config_template():
    """Generate parametrized config template"""

    template = '''# Multi-Country Config Template
# Replace {{COUNTRY_*}} placeholders with actual values

baseURL = "https://{{COUNTRY_CODE}}.worldheritage.guide/"
languageCode = "en-us"
title = "WorldHeritage.guide - {{COUNTRY_NAME}} | Comprehensive Heritage Travel Guide"

# Content
contentDir = "content"
dataDir = "data"
layoutDir = "layouts"
staticDir = "static"
publishDir = "public"

# Build
[build]
writeStats = true

# Pagination
paginate = 100

# Permalinks
[permalinks]
  posts = "/:section/:slug/"

# Taxonomies
[taxonomies]
  category = "categories"
  tag = "tags"
  region = "regions"
  heritage_type = "heritage_types"
  author = "authors"
  blog_category = "blog_categories"

# Menu (same for all countries)
[menu]
  [[menu.main]]
    name = "Home"
    url = "/"
    weight = 1

  [[menu.main]]
    name = "Heritage Sites"
    url = "/sites/"
    weight = 2

  [[menu.main]]
    name = "Regions"
    url = "/regions/"
    weight = 3

  [[menu.main]]
    name = "UNESCO Sites"
    url = "/tags/unesco/"
    weight = 4

  [[menu.main]]
    name = "Blog"
    url = "/blog/"
    weight = 5

# Country-specific parameters
[params]
  # Country configuration
  country = "{{COUNTRY_NAME}}"
  countryCode = "{{COUNTRY_CODE}}"
  wikidataQID = "{{WIKIDATA_QID}}"

  # SEO
  description = "Discover {{COUNTRY_NAME}}'s rich cultural and natural heritage. Comprehensive guides to UNESCO sites, monuments, castles, museums, and hidden gems."
  author = "WorldHeritage.guide"

  # External Image CDN (Cloudflare R2)
  imageBaseURL = "https://pub-{{R2_BUCKET_ID}}.r2.dev"

  # Social
  twitter = ""
  facebook = ""
  instagram = ""

  # Analytics
  googleAnalytics = ""

  # Design
  primaryColor = "#2C5F2D"
  accentColor = "#97BC62"

  # Features
  enableSearch = false
  enableComments = false
  enableShareButtons = true

# Markup
[markup]
  [markup.goldmark]
    [markup.goldmark.renderer]
      unsafe = true
  [markup.highlight]
    style = "monokai"
    lineNos = false

# Output formats
[outputFormats.SitesJSON]
  mediaType = "application/json"
  baseName = "sites-data"
  isPlainText = true
  notAlternative = true

[outputs]
  home = ["HTML", "RSS"]
  section = ["HTML", "SitesJSON"]
  page = ["HTML"]
  taxonomy = ["HTML"]
  term = ["HTML"]

# Minification
[minify]
  disableCSS = false
  disableHTML = false
  disableJS = false
  disableJSON = false
  disableSVG = false
  disableXML = false
  minifyOutput = true
  [minify.tdewolff]
    [minify.tdewolff.html]
      keepWhitespace = false

# Sitemap
[sitemap]
  changefreq = "weekly"
  filename = "sitemap.xml"
  priority = 0.5
'''

    return template

def print_report(layout_refs, config_issues):
    """Print Phase 3 audit report"""

    print("Starting Phase 3: Config Optimization & Multi-Country Preparation")
    print("=" * 80)
    print()

    # Config Issues
    print("[!] CONFIG.TOML HARDCODED REFERENCES")
    print("-" * 80)

    if config_issues:
        for issue in config_issues:
            print(f"Line {issue['line']:3d}: {issue['content']}")
            print(f"           Type: {issue['type']}")
            print()
        print(f"Total config issues: {len(config_issues)}")
    else:
        print("[OK] No hardcoded references in config.toml")

    print()

    # Layout References
    print("[*] LAYOUT FILES WITH HARDCODED REFERENCES")
    print("-" * 80)

    total_refs = sum(len(refs) for refs in layout_refs.values())

    if layout_refs:
        print(f"Found {total_refs} references in {len(layout_refs)} files\n")

        for filepath, refs in sorted(layout_refs.items())[:10]:
            filename = Path(filepath).name
            print(f"\n{filepath} ({len(refs)} refs):")
            for ref in refs[:3]:
                print(f"  Line {ref['line']:3d}: {ref['content'][:70]}")
            if len(refs) > 3:
                print(f"  ... and {len(refs) - 3} more")

        if len(layout_refs) > 10:
            print(f"\n... and {len(layout_refs) - 10} more files")
    else:
        print("[OK] No hardcoded references in layouts")

    print()
    print()

    # Summary
    print("=" * 80)
    print("[*] MULTI-COUNTRY READINESS ASSESSMENT")
    print("=" * 80)
    print()

    print("[CURRENT STATE]")
    print(f"  Config hardcoded refs: {len(config_issues)}")
    print(f"  Layout hardcoded refs: {total_refs} in {len(layout_refs)} files")
    print()

    print("[REQUIRED CHANGES FOR MULTI-COUNTRY]")
    print("-" * 80)
    print()
    print("1. CONFIG.TOML")
    print("   - Add [params.country] and [params.countryCode] variables")
    print("   - Replace 'Germany' with {{.Site.Params.country}}")
    print("   - Replace 'de' with {{.Site.Params.countryCode}}")
    print()

    print("2. LAYOUTS/*.HTML")
    print("   - Replace hardcoded 'Germany' with {{ .Site.Params.country }}")
    print("   - Replace hardcoded 'de' with {{ .Site.Params.countryCode }}")
    print(f"   - Total files to update: {len(layout_refs)}")
    print()

    print("3. CONTENT GENERATION")
    print("   - Update Wikidata query to use country QID parameter")
    print("   - Update LLM prompts to use country parameter")
    print("   - Update region lists per country")
    print()

    print("[TEMPLATE GENERATED]")
    print("-" * 80)
    print("Created: docs/config.template.toml")
    print("Use this template for new countries")
    print()

    print("[ACTION ITEMS]")
    print("-" * 80)
    print("[ ] Review config issues above")
    print("[ ] Update config.toml with country parameters")
    print("[ ] Update layout files to use Site.Params.country")
    print("[ ] Test with current Germany setup")
    print("[ ] Document deployment process for new countries")
    print()

if __name__ == "__main__":
    # Find references
    layout_refs = find_hardcoded_references()
    config_issues = analyze_config()

    # Print report
    print_report(layout_refs, config_issues)

    # Generate template
    template = generate_config_template()

    # Save template
    docs_dir = Path('docs')
    docs_dir.mkdir(exist_ok=True)

    template_path = docs_dir / 'config.template.toml'
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template)

    print(f"\nTemplate saved to: {template_path}")
