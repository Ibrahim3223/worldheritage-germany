# Quick Start Guide - WorldHeritage Platform

Get from zero to 15,000 pages in 3 steps.

---

## ⚡ Prerequisites

```bash
# Install Python packages
pip install requests pillow

# Optional: For GPT enhancement
pip install openai
export OPENAI_API_KEY=your_key_here

# Verify Hugo installation
hugo version  # Should be v0.120+ extended
```

---

## 🚀 3-Step Workflow

### Step 1: Fetch Sites (2-4 hours)

```bash
# Fetch 15,000 high-quality sites from Wikidata
python master_fetch_sites.py Germany --target 15000
```

**What happens:**
- Queries Wikidata for 80+ categories
- Applies quality filters (coordinates, sitelinks, claims)
- Saves to `data/fetched/germany_*.json`

**Expected output:**
```
Processing: museum (2500 sites)
  Fetched: 3000, Accepted: 2500, Filtered: 500
  [OK] Collected: 2500 sites
    - Coordinates: 2500 (100.0%)
    - Images: 2100 (84.0%)
    - Avg sitelinks: 8.5
  Total progress: 2,500/15,000 (16.7%)

... (80+ more categories)

FETCH COMPLETE
Total sites collected: 15,247
```

### Step 2: Create Pages (2-8 hours)

**Option A: Basic Mode (No GPT, Fast)**
```bash
python create_pages.py Germany
```

**Option B: With GPT (High Quality)**
```bash
python create_pages.py Germany --with-gpt
```

**Option C: Skip Images (Fastest)**
```bash
python create_pages.py Germany --skip-images
```

**What happens:**
- Reads JSON files from `data/fetched/`
- Generates markdown with YAML frontmatter
- Downloads images from Wikimedia Commons
- (Optional) Enhances content with GPT-4
- Saves to `content/sites/*.md`

**Expected output:**
```
Processing: museum (2500 sites)
  Created: 2500, Skipped: 0

... (80+ more categories)

PAGE CREATION COMPLETE
Total pages created: 15,247
Total pages skipped: 0
```

### Step 3: Build Site (5-10 minutes)

```bash
# Development server
hugo server

# Production build
hugo --minify
```

**What happens:**
- Hugo builds static site
- Generates 15,000+ pages
- Creates category/region taxonomies
- Builds search index
- Minifies CSS/JS

**Expected output:**
```
Start building sites …
Built in 8432 ms

Total pages: 15,247
Categories: 80
Regions: 16
```

---

## 📊 What You Get

After completion:

```
worldheritage-germany/
├── content/sites/          # 15,247 markdown pages
├── static/images-sites/    # ~12,000 images (~8GB)
├── public/                 # Static website (ready to deploy)
├── data/fetched/           # JSON data (80+ files)
└── README_MASTER_SYSTEM.md # Full documentation
```

**Site features:**
- ✅ 15,247 heritage sites
- ✅ Interactive maps (Leaflet)
- ✅ Photo galleries with lightbox
- ✅ Advanced filtering (category, region, UNESCO)
- ✅ Search functionality
- ✅ Responsive design
- ✅ SEO optimized

---

## 🎯 Customization

### Adjust Target Pages

```bash
# More pages (max ~20k)
python master_fetch_sites.py Germany --target 18000

# Fewer pages (min ~10k)
python master_fetch_sites.py Germany --target 12000
```

### Change Quality Filters

Edit `wikidata_categories_comprehensive.py`:

```python
QUALITY_FILTERS = {
    "min_sitelinks": 3,          # More = higher quality
    "require_coordinates": True,  # False = allow without location
    "min_claims": 5,             # More = more complete data
}
```

### Adjust Category Limits

Edit `wikidata_categories_comprehensive.py`:

```python
CATEGORY_LIMITS = {
    "museum": 3000,     # Increase for more museums
    "castle": 500,      # Decrease for fewer castles
    # ... etc
}
```

---

## 🌍 Multi-Country

Same workflow for any country:

```bash
# France
python master_fetch_sites.py France --target 15000
python create_pages.py France --with-gpt

# Italy
python master_fetch_sites.py Italy --target 18000
python create_pages.py Italy --with-gpt

# USA
python master_fetch_sites.py USA --target 25000
python create_pages.py USA
```

**Supported:** 190+ countries in Wikidata

---

## 🔧 Troubleshooting

### "Wikidata timeout"
```bash
# Wait 5 minutes, then resume
# The script picks up where it left off
```

### "No images downloaded"
```bash
# Re-run image optimization separately
python optimize_images.py --country Germany --reprocess
```

### "GPT rate limit"
```bash
# Use basic mode instead
python create_pages.py Germany
```

### "Hugo build error"
```bash
# Validate project first
python validate_project.py

# Check specific file
hugo --debug
```

---

## 💰 Cost Breakdown

### Free Tier (No GPT)
- **Data fetching:** Free (Wikidata)
- **Images:** Free (Wikimedia Commons)
- **Hosting:** Free (Netlify/Vercel/GitHub Pages)
- **Total:** $0

### Premium Tier (With GPT)
- **GPT API:** ~$30-50 for 15k pages
- **Images:** Free
- **Hosting:** Free
- **Total:** ~$30-50 per country

---

## ⏱️ Time Estimates

| Task | Without GPT | With GPT |
|------|-------------|----------|
| Fetch Sites | 2-4 hours | 2-4 hours |
| Create Pages | 2-3 hours | 6-8 hours |
| Download Images | 4-6 hours | 4-6 hours |
| Build Hugo | 5-10 min | 5-10 min |
| **Total** | **8-13 hours** | **12-18 hours** |

*Can run overnight unattended*

---

## ✅ Quality Check

After build, verify:

```bash
# Run validation
python validate_project.py

# Check stats
ls content/sites/*.md | wc -l  # Should be ~15,000
du -sh static/images-sites/    # Should be ~8-10GB
ls public/ | wc -l              # Should be ~15,000+
```

---

## 🚢 Deployment

**Option 1: Netlify**
```bash
# Connect GitHub repo
# Set build command: hugo --minify
# Set publish directory: public
# Deploy!
```

**Option 2: Vercel**
```bash
vercel --prod
```

**Option 3: GitHub Pages**
```bash
# Push to gh-pages branch
git subtree push --prefix public origin gh-pages
```

---

## 📚 Next Steps

1. **Customize theme** - Edit `layouts/` and `assets/`
2. **Add analytics** - Google Analytics, Plausible
3. **Optimize SEO** - Meta tags, sitemaps
4. **Add features** - Comments, ratings, user submissions
5. **Scale to more countries** - Repeat workflow

---

**Ready to build your heritage platform?**

```bash
python master_fetch_sites.py Germany --target 15000
```

🎉 Let's go!
