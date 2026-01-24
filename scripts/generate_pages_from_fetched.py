"""
Generate Hugo Pages from Fetched Wikidata
- Reads from data/fetched/*.json
- Generates AI content with OpenAI
- Creates Hugo markdown pages
- Skips existing pages
- Progress tracking
"""

import os
import sys
import json
import time
import re
import argparse
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment
load_dotenv(Path(__file__).parent.parent / '.env')

# ============================================
# CONFIGURATION
# ============================================

CONFIG = {
    'model': 'gpt-4o-mini',
    'temperature': 0.7,
    'max_tokens': 6000,
    'rate_limit': 1.0,  # seconds between API calls
    'word_count_target': 1500,
}

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data' / 'fetched'
CONTENT_DIR = BASE_DIR / 'content' / 'sites'
IMAGES_DIR = BASE_DIR / 'static' / 'images-sites'
PROGRESS_FILE = BASE_DIR / 'content_generation_progress.txt'

# ============================================
# UTILITIES
# ============================================

def generate_slug(title: str) -> str:
    """Generate URL-friendly slug from title"""
    slug = title.lower()
    slug = re.sub(r'[äÄ]', 'ae', slug)
    slug = re.sub(r'[öÖ]', 'oe', slug)
    slug = re.sub(r'[üÜ]', 'ue', slug)
    slug = re.sub(r'[ß]', 'ss', slug)
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug[:80]

def log(message: str, level: str = 'INFO'):
    """Print log message"""
    timestamp = time.strftime('%H:%M:%S')
    print(f"[{timestamp}] {level}: {message}")
    sys.stdout.flush()

def write_progress(message: str):
    """Write progress to file"""
    with open(PROGRESS_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

# ============================================
# CONTENT GENERATION
# ============================================

def format_site_data_for_prompt(site: dict) -> str:
    """Format site data clearly for the GPT prompt - matches original script"""

    sections = []

    title = site.get('title', 'Unknown')
    description = site.get('description', '')
    category = site.get('category', 'heritage site')
    category_info = site.get('category_info', {})
    heritage_type = category.replace('_', ' ').title()

    # Basic Info
    sections.append("=== BASIC INFORMATION ===")
    sections.append(f"Name: {title}")
    sections.append(f"Type: {heritage_type}")
    sections.append(f"Region: Germany")
    sections.append(f"Country: Germany")
    if description:
        sections.append(f"Description: {description}")

    # Location
    if site.get('latitude') and site.get('longitude'):
        sections.append(f"\n=== LOCATION ===")
        sections.append(f"Coordinates: {site['latitude']}, {site['longitude']}")

    # Category info
    if category_info:
        sections.append(f"\n=== CATEGORY INFO ===")
        if category_info.get('category_tags'):
            sections.append(f"Tags: {', '.join(category_info['category_tags'])}")
        if category_info.get('description'):
            sections.append(f"Category: {category_info['description']}")

    return "\n".join(sections)


def build_prompt(site: dict) -> str:
    """Build comprehensive data-driven prompt for GPT - matches original quality"""

    title = site.get('title', 'Unknown')
    category = site.get('category', 'heritage site')
    heritage_type = category.replace('_', ' ').title()

    # Format site data clearly
    formatted_data = format_site_data_for_prompt(site)

    prompt = f"""You are writing for WorldHeritage.guide, a premium heritage travel platform.

================================================================================
MISSION: Write a comprehensive and detailed guide to {title}
================================================================================

TARGET: 1500-2000 words
STYLE: National Geographic meets Lonely Planet - authoritative yet engaging

================================================================================
CRITICAL RULE #1: DATA INTEGRITY (MOST IMPORTANT)
================================================================================

You MUST follow these rules with ZERO exceptions:

1. ONLY use facts from the SITE DATA section below
2. If information is missing, write around it gracefully - readers won't notice
3. NEVER invent or guess:
   - Specific dates, years, or centuries
   - Prices or admission fees
   - Opening hours or schedules
   - Heights, areas, or dimensions
   - Names of architects, builders, or historical figures
   - Visitor statistics or numbers
   - Any specific facts not in the data

4. For missing practical info, use these EXACT phrases:
   - Hours: "Check the official website for current opening hours"
   - Prices: "Visit the official website for current admission prices"
   - Contact: "Contact the site directly for the latest information"

5. For historical/architectural sections with missing data:
   - Use general language: "historically significant", "over the centuries"
   - Focus on what CAN be said from the data
   - Skip sections entirely if no relevant data exists

6. GEOGRAPHIC ACCURACY:
   - NEVER mention specific geographic features (valleys, rivers, mountains) not in the data
   - NEVER mention specific nearby cities, towns, or regions not in the data
   - Use only GENERAL directional language: "the surrounding landscape", "the vista below", "the nearby area"
   - Do NOT invent specific place names, valleys, or regions

7. DOUBLE-CHECK BEFORE WRITING:
   - Before mentioning ANY specific fact, verify it exists in the SITE DATA section
   - When in doubt, use general language instead of specific claims
   - It's better to be vague than wrong

================================================================================
CRITICAL RULE #2: FORBIDDEN PHRASES (AI CLICHÉS)
================================================================================

NEVER use these phrases - they mark content as AI-generated:

- "nestled in/among"
- "boasts" (as in "the castle boasts")
- "rich tapestry"
- "testament to"
- "stands as a beacon"
- "jewel of" / "crown jewel"
- "journey through time"
- "step back in time"
- "hidden gem" (unless provably obscure)
- "breathtaking views" (be specific instead)
- "a feast for the senses"
- "where history comes alive"
- "steeped in history"
- "treasure trove"
- "picture-perfect"
- "postcard-worthy"

INSTEAD: Use specific, concrete, vivid language.
BAD: "The castle boasts breathtaking views"
GOOD: "From the north tower, the landscape stretches to the horizon"

================================================================================
CRITICAL RULE #3: WRITING EXCELLENCE
================================================================================

1. SENTENCE VARIETY:
   - Mix short punchy sentences with longer flowing ones
   - Start some sentences with: And, But, So, Yet, Or
   - Use questions occasionally: "What draws visitors here?"

2. VOICE & TENSE:
   - Active voice 90%+ of the time
   - Present tense for descriptions
   - Past tense only for historical events
   - Second person welcome: "you'll discover", "your visit"

3. SPECIFICITY:
   - Concrete details over vague adjectives
   - Sensory details: what you see, hear, feel
   - Directional language: "to the east", "at the entrance"

================================================================================
SITE DATA - YOUR ONLY SOURCE OF FACTS
================================================================================

{formatted_data}

================================================================================
ARTICLE STRUCTURE
================================================================================

Write these sections with CLEAR MARKDOWN HEADERS (## for H2):

## Overview (200-300 words)
   - Hook: Start with a surprising fact, vivid scene, or historical moment
   - Geographic context: Where is it? What's the landscape like?
   - Significance: Why does this place matter?
   - Promise: What will the reader discover?

## History and Significance (400-600 words)
   - Use ONLY dates/facts from the data
   - If no dates: use general phrases ("over centuries", "through the ages")
   - Key figures: ONLY mention if in the data
   - Major events and transformations
   - Cultural importance

## Architecture and Features (300-500 words)
   - Physical description
   - Architectural style (general if not in data)
   - Notable features visitors should look for
   - What makes it visually distinctive

## Visiting Information (400-500 words) - REQUIRED
   - Getting there: General transport options for the region
   - Hours/Fees: "Check official website for current information"
   - What to expect: The visitor experience
   - Time needed: Estimate based on site type (1-2 hours typical)
   - Best times: Morning for fewer crowds, spring/fall for weather
   - Accessibility: Mention if relevant

## Nearby Attractions (200-300 words)
   - 3-5 nearby places worth visiting
   - Brief description of each
   - Can mention general regional attractions

## Insider Tips (150-200 words) - REQUIRED
   - Best photography spots and times
   - Lesser-known details to look for
   - How to avoid crowds
   - Local tips

## Practical Information (200-250 words)
   - Consolidate all visitor details
   - What to bring
   - Seasonal considerations

## Frequently Asked Questions (300-400 words) - REQUIRED
   Write 8-10 common questions visitors would ask, with detailed answers.
   Use this EXACT format for SEO and accordion compatibility:

   ### How long should I spend visiting?
   [Detailed answer 2-3 sentences]

   ### Is photography allowed inside?
   [Answer]

   ### Are there guided tours available?
   [Answer]

   ### What's the best time of day to visit?
   [Answer]

   ### Is the site wheelchair accessible?
   [Answer]

   ### Can I buy tickets online?
   [Answer]

   ### Are there facilities like restrooms and cafes?
   [Answer]

   ### What should I wear when visiting?
   [Answer]

   IMPORTANT: Use ### (H3) for each question. Answer directly below.

================================================================================
OUTPUT FORMAT
================================================================================

IMPORTANT: Use markdown headers (##) for each section.
Write flowing prose within each section.
The article should be well-structured and easy to scan.

================================================================================
BEGIN WRITING
================================================================================

Remember the priority: DATA ACCURACY > ENGAGING WRITING > WORD COUNT

Start with a compelling opening line that draws the reader in.
"""

    return prompt


def generate_content(site: dict, client: OpenAI) -> str:
    """Generate article content using OpenAI"""

    prompt = build_prompt(site)

    response = client.chat.completions.create(
        model=CONFIG['model'],
        messages=[
            {
                "role": "system",
                "content": "You are an expert travel writer creating factual, engaging heritage site guides. Never invent facts."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=CONFIG['temperature'],
        max_tokens=CONFIG['max_tokens'],
    )

    return response.choices[0].message.content


def create_hugo_page(site: dict, content: str, slug: str) -> str:
    """Create Hugo markdown page"""

    title = site.get('title', 'Unknown').replace('"', '\\"')
    description = site.get('description', '')[:150].replace('"', '\\"')
    category = site.get('category', 'heritage site').replace('_', ' ').title()
    lat = site.get('latitude', 0)
    lon = site.get('longitude', 0)

    # Find images
    img_dir = IMAGES_DIR / slug
    images = []
    if img_dir.exists():
        for img in sorted(img_dir.glob('*-800w.webp'))[:3]:
            images.append(f'/images-sites/{slug}/{img.name}')

    images_yaml = '\n'.join([f'  - "{img}"' for img in images]) if images else '  []'

    # Build frontmatter
    md = f'''---
title: "{title}"
date: {time.strftime('%Y-%m-%d')}
draft: false
description: "{description}"

# Display fields
region: "Germany"
country: "Germany"
heritage_type: "{category}"

# Taxonomies
categories:
  - "{category}"
regions:
  - "Germany"

# Location
latitude: {lat}
longitude: {lon}

# Images
images:
{images_yaml}
---

{content}
'''
    return md


# ============================================
# MAIN PROCESSING
# ============================================

def load_all_sites() -> list:
    """Load all sites from fetched JSON files"""
    all_sites = []

    for json_file in sorted(DATA_DIR.glob('germany_*.json')):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                sites = json.load(f)
                all_sites.extend(sites)
        except Exception as e:
            log(f"Error loading {json_file.name}: {e}", 'ERROR')

    return all_sites


def get_existing_pages() -> set:
    """Get set of existing page slugs"""
    existing = set()
    for md_file in CONTENT_DIR.glob('*.md'):
        if md_file.name != '_index.md':
            existing.add(md_file.stem)
    return existing


def main():
    parser = argparse.ArgumentParser(description='Generate Hugo pages from fetched data')
    parser.add_argument('--test', type=int, help='Test mode: process only N sites')
    parser.add_argument('--category', type=str, help='Process only specific category')
    parser.add_argument('--force', action='store_true', help='Regenerate existing pages')
    parser.add_argument('--skip-existing', action='store_true', default=True, help='Skip existing pages (default)')
    args = parser.parse_args()

    # Initialize
    PROGRESS_FILE.write_text('')
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)

    log("=" * 60)
    log("HUGO PAGE GENERATOR")
    log("=" * 60)

    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        log("ERROR: OPENAI_API_KEY not found in .env", 'ERROR')
        return

    client = OpenAI(api_key=api_key)
    log(f"OpenAI client initialized (model: {CONFIG['model']})")

    # Load sites
    if args.category:
        json_file = DATA_DIR / f'germany_{args.category}.json'
        if not json_file.exists():
            log(f"Category file not found: {json_file}", 'ERROR')
            return
        with open(json_file, 'r', encoding='utf-8') as f:
            sites = json.load(f)
        log(f"Loaded {len(sites)} sites from {args.category}")
    else:
        sites = load_all_sites()
        log(f"Loaded {len(sites)} total sites")

    if args.test:
        sites = sites[:args.test]
        log(f"Test mode: processing {len(sites)} sites")

    # Get existing pages
    existing = get_existing_pages()
    log(f"Existing pages: {len(existing)}")

    # Filter sites
    if not args.force:
        sites_to_process = []
        for site in sites:
            slug = generate_slug(site.get('title', ''))
            if slug and slug not in existing:
                sites_to_process.append(site)
        log(f"New sites to process: {len(sites_to_process)}")
    else:
        sites_to_process = sites
        log(f"Force mode: processing all {len(sites_to_process)} sites")

    if not sites_to_process:
        log("No new sites to process!")
        return

    write_progress(f"Starting: {len(sites_to_process)} sites to process")

    # Process sites
    stats = {'success': 0, 'failed': 0, 'skipped': 0}
    start_time = time.time()
    total_tokens = 0

    for i, site in enumerate(sites_to_process, 1):
        title = site.get('title', 'Unknown')
        slug = generate_slug(title)

        if not slug:
            stats['skipped'] += 1
            continue

        try:
            # Generate content
            content = generate_content(site, client)

            # Create Hugo page
            md_content = create_hugo_page(site, content, slug)

            # Save
            output_file = CONTENT_DIR / f'{slug}.md'
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(md_content)

            stats['success'] += 1

            # Progress
            elapsed = time.time() - start_time
            rate = i / elapsed if elapsed > 0 else 0
            eta = (len(sites_to_process) - i) / rate if rate > 0 else 0

            progress_str = f"[{i}/{len(sites_to_process)}] + {slug[:40]:<40} OK:{stats['success']} ETA:{int(eta//60)}m"

            if sys.stdout.isatty():
                print(f"\r{progress_str}", end='', flush=True)
            else:
                if i % 10 == 0:
                    print(progress_str)

            # Log every 50
            if i % 50 == 0:
                write_progress(f"Progress: {i}/{len(sites_to_process)} - OK:{stats['success']}")

            # Rate limit
            time.sleep(CONFIG['rate_limit'])

        except Exception as e:
            stats['failed'] += 1
            log(f"Failed: {title} - {e}", 'ERROR')
            time.sleep(2)  # Extra delay on error

    print()  # New line

    # Summary
    elapsed = time.time() - start_time
    log("")
    log("=" * 60)
    log("SUMMARY")
    log("=" * 60)
    log(f"Total processed: {sum(stats.values())}")
    log(f"  Success: {stats['success']}")
    log(f"  Failed: {stats['failed']}")
    log(f"  Skipped: {stats['skipped']}")
    log(f"Time: {int(elapsed//60)}m {int(elapsed%60)}s")

    # Cost estimate (gpt-4o-mini: ~$0.15/1M input, $0.60/1M output)
    estimated_cost = stats['success'] * 0.002  # ~$0.002 per article
    log(f"Estimated cost: ${estimated_cost:.2f}")

    write_progress(f"COMPLETE - Success:{stats['success']} Failed:{stats['failed']}")

    log("")
    log("Next: Run 'hugo server' to preview the site")


if __name__ == '__main__':
    main()
