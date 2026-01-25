# Heritage Site Data Pipeline

Complete pipeline for generating heritage site content from Wikidata for any country.

## 🚀 Quick Start (for new countries)

1. Update `config.py` with target country Wikidata ID
2. Run scripts in order: `0 → 1 → 2 → 2b → 3`
3. Deploy to Cloudflare Pages

## 📋 Pipeline Scripts

### Core Production Scripts (Run in order)

#### `0_define_categories.py`
- Defines heritage site categories (castle, church, museum, etc.)
- Configures category mappings for content generation
- **One-time setup** - rarely needs changes

#### `1_fetch_wikidata.py` ✅ **COMPLETE**
- Fetches all heritage sites from Wikidata SPARQL endpoint
- Includes: coordinates, images, regions, UNESCO status, architect, style, etc.
- Output: `data/fetched/germany_*.json`
- **✅ Includes proper region extraction (P131)**
- **✅ Includes UNESCO designation (P1435)**
- **✅ Includes Wikidata image URLs (P18)**

#### `2_fetch_images.py`
- Downloads images from Wikimedia Commons
- **⚠️ DEPRECATED** - Now handled by script 3

#### `2b_optimize_images.py`
- Optimizes downloaded images (resize, WebP conversion)
- **⚠️ DEPRECATED** - Now using direct Wikimedia URLs

#### `3_generate_content.py` ✅ **COMPLETE & READY**
- **Main content generator** - creates Hugo markdown files
- Uses OpenAI GPT-4o-mini for high-quality content (1500-2000 words)
- **✅ NEW: Fetches Wikimedia Commons images directly (no local download)**
- **✅ NEW: Generates responsive image srcset (400, 800, 1200, 1920px)**
- **✅ NEW: Includes site_name, correct region, UNESCO tags**
- **✅ NEW: Adds wikidata_id for data traceability**
- Parallel processing (5 workers) for 5x speed
- Output: `content/sites/*.md`

**Features:**
- ✅ Site name from Wikidata
- ✅ Actual region (state/province) not just country
- ✅ UNESCO World Heritage Site tags
- ✅ Wikimedia Commons images (no R2 storage needed)
- ✅ Responsive image srcset
- ✅ Complete visitor information
- ✅ SEO-optimized content

#### `4_upload_to_r2.py`
- Uploads optimized images to Cloudflare R2
- **⚠️ DEPRECATED** - No longer needed (using Wikimedia URLs)

### Utility Scripts

#### `fix_all_metadata.py` ✅ **OPTIMIZED**
- **Fixes existing content files** with missing metadata
- Adds site_name, corrects regions, adds UNESCO tags
- **✅ Cache-only mode** (no API calls, super fast: 11 seconds for 5,855 files)
- Use when updating old content or fixing data issues

**Usage:**
```bash
python scripts/fix_all_metadata.py
```

## 🌍 Adapting for Other Countries

### 1. Update Config
Edit `config.py`:
```python
PROJECT = {
    'name': 'France',  # Change country
    'wikidata_id': 'Q142',  # France Wikidata ID
    'country_code': 'FR'
}
```

### 2. Run Pipeline
```bash
# Fetch data from Wikidata
python scripts/1_fetch_wikidata.py

# Generate content (includes images automatically)
python scripts/3_generate_content.py

# Optional: Fix any metadata issues
python scripts/fix_all_metadata.py
```

### 3. Deploy
```bash
hugo
# Deploy to Cloudflare Pages
```

## ✅ System is Clean & Ready

All scripts have been optimized for:
- **No R2 dependency** - Images from Wikimedia Commons CDN
- **Fast processing** - Parallel API calls, cache-only metadata fixes
- **Complete data** - site_name, regions, UNESCO tags, responsive images
- **Multi-country ready** - Just change Wikidata ID in config

## 📊 Data Quality

**From Wikidata (via script 1):**
- ✅ Site name and description
- ✅ Precise coordinates
- ✅ Administrative region (state/province)
- ✅ UNESCO designation
- ✅ Architectural style, architect
- ✅ Inception year
- ✅ Official website
- ✅ Entry fees, opening hours
- ✅ Wikimedia Commons images

**Generated (via script 3):**
- ✅ 1500-2000 word articles
- ✅ Responsive images (4 sizes)
- ✅ Hugo frontmatter
- ✅ SEO optimization
- ✅ Visitor information

## 🗑️ Deprecated Scripts

These scripts are no longer needed:
- ~~`2_fetch_images.py`~~ - Images now fetched directly via URLs
- ~~`2b_optimize_images.py`~~ - Using Wikimedia's thumbnail service
- ~~`4_upload_to_r2.py`~~ - No local storage needed
- ~~`5_update_wikimedia_images.py`~~ - Integrated into script 3

## 📝 Notes

- Script 3 (`generate_content.py`) is the heart of the system
- All new sites automatically get complete metadata
- For existing sites, use `fix_all_metadata.py` to update
- Wikidata cache in `data/fetched/` speeds up processing
- No API keys needed except OpenAI (for content generation)

## 🎯 Next Country Deployment

1. Update country in `config.py`
2. Run `1_fetch_wikidata.py`
3. Run `3_generate_content.py`
4. Done! ✨

System is production-ready for any country with heritage sites in Wikidata.
