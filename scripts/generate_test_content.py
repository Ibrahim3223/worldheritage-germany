"""
Generate GPT content for test sites
Then update Hugo pages with the generated content
"""

import json
import time
import importlib.util
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import os

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
format_site_data_for_prompt = generate_content.format_site_data_for_prompt
build_content_prompt = generate_content.build_content_prompt
get_content_strategy = generate_content.get_content_strategy

# Load test sites
sites_file = base_dir / 'data/raw/sites_test.json'
with open(sites_file, 'r', encoding='utf-8') as f:
    sites = json.load(f)

content_dir = base_dir / 'data/content'
content_dir.mkdir(parents=True, exist_ok=True)

print("Generating GPT content for test sites...")
print("=" * 60)

successful = 0
failed = 0

for idx, site in enumerate(sites, 1):
    name = site.get('name', 'Unknown')
    wid = site.get('wikidata_id')
    completeness = site.get('completeness_score', 50)

    print(f"{idx:2d}. {name[:45]:45s}", end=" ", flush=True)

    try:
        # Get strategy based on completeness
        strategy = get_content_strategy(completeness)

        # Build prompt
        prompt = build_content_prompt(site, strategy)

        # Call GPT-4o-mini
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
        import re
        slug = name.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug).strip('-')

        # Save content as JSON
        content_data = {
            'site_name': name,
            'site_slug': slug,
            'wikidata_id': wid,
            'completeness_score': completeness,
            'content': {
                'full_article': content_text
            },
            'word_count': word_count,
            'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        }

        content_file = content_dir / f'{slug}.json'
        with open(content_file, 'w', encoding='utf-8') as f:
            json.dump(content_data, f, ensure_ascii=False, indent=2)

        print(f"[{word_count:4d} words]")
        successful += 1

        # Rate limiting
        time.sleep(2)

    except Exception as e:
        print(f"[ERROR: {str(e)[:30]}]")
        failed += 1

print("=" * 60)
print(f"Generated: {successful}/{len(sites)} sites")
print(f"Failed: {failed}")
print(f"\nContent saved to: {content_dir}")
print("\nNow recreating Hugo pages with GPT content...")
