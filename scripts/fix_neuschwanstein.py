"""
Fix Neuschwanstein content - regenerate with corrected prompt
"""

import json
import importlib.util
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import os
import re

# Load environment
load_dotenv()
base_dir = Path(__file__).parent.parent

# OpenAI setup
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Load the 3_generate_content module
spec = importlib.util.spec_from_file_location("generate_content", base_dir / 'scripts' / '3_generate_content.py')
generate_content = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate_content)

# Get the functions
build_content_prompt = generate_content.build_content_prompt
get_content_strategy = generate_content.get_content_strategy

# Load test sites
sites_file = base_dir / 'data/raw/sites_test.json'
with open(sites_file, 'r', encoding='utf-8') as f:
    sites = json.load(f)

# Find Neuschwanstein
site = next((s for s in sites if 'Neuschwanstein' in s.get('name', '')), None)

if site:
    print(f"Regenerating content for: {site['name']}")

    # Get strategy
    strategy = get_content_strategy(site.get('completeness_score', 50))

    # Build prompt
    prompt = build_content_prompt(site, strategy)

    # Call GPT
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an expert travel writer for WorldHeritage.guide. You write engaging, factual, SEO-optimized heritage site guides that are 1800-2200 words long. You NEVER invent facts - only use provided data. IMPORTANT: Write detailed, comprehensive articles that hit the target word count."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=8000
    )

    content_text = response.choices[0].message.content
    word_count = len(content_text.split())

    # Generate slug
    slug = 'neuschwanstein-castle'

    # Save content
    content_data = {
        'site_name': site['name'],
        'site_slug': slug,
        'wikidata_id': site['wikidata_id'],
        'completeness_score': site.get('completeness_score', 50),
        'content': {
            'full_article': content_text
        },
        'word_count': word_count,
        'generated_at': __import__('time').strftime('%Y-%m-%d %H:%M:%S'),
    }

    content_file = base_dir / 'data/content' / f'{slug}.json'
    with open(content_file, 'w', encoding='utf-8') as f:
        json.dump(content_data, f, ensure_ascii=False, indent=2)

    print(f"Generated: {word_count} words")
    print(f"Saved to: {content_file}")
    print("\nNow updating Hugo page...")

    # Update Hugo page
    from update_hugo_with_gpt_content import *

else:
    print("Neuschwanstein not found!")
