# WorldHeritage Germany - Project Structure Documentation

## Overview
This documentation ensures the project remains organized and scalable for future multi-country versions.

## Project Statistics (Current)
- **Total Sites**: 1,086 heritage sites
- **Images**: 3,467 optimized WebP files (513MB total)
- **Regions**: 16 German states (Bundesländer)
- **Build Time**: ~35 seconds
- **Total Pages**: 1,167

## Directory Structure

```
worldheritage-germany/
├── content/
│   └── sites/              # All heritage site markdown files (1,086 files)
│       ├── *.md           # Individual site pages
│       └── _index.md      # Sites section index
├── data/                  # JSON data files (if any)
├── layouts/
│   ├── _default/
│   │   └── single.html    # Individual site page template
│   ├── partials/
│   │   └── site-card.html # Site card component
│   └── sites/
│       └── list.html      # Sites listing with filters
├── static/
│   └── [static assets]
├── config.toml            # Hugo configuration
└── *.py                   # Python maintenance scripts
```

## Content Organization

### Site Markdown Files
Each site file in `content/sites/` follows this frontmatter structure:

```yaml
---
title: "Site Name"
site_name: "Site Name"
slug: "site-slug"
region: "German State Name"
regions:
  - "German State Name"
heritage_type: "cultural site|natural site|mixed site"
wikidata_id: "Q123456"
description: "Clean description without quotes or markdown (max 155 chars)"
categories:
  - "church building"
  - "palace"
images:
  - "/images-sites/slug/image-320w.webp"
  - "/images-sites/slug/image-640w.webp"
  - "/images-sites/slug/image-1024w.webp"
  - "/images-sites/slug/image-1920w.webp"
---

## Overview
[Content starts here...]
```

### Required Frontmatter Fields
- **title**: Site name (must use double quotes)
- **site_name**: Same as title
- **slug**: URL-friendly identifier
- **region**: One of the 16 German states
- **regions**: Array with one state (for taxonomy)
- **heritage_type**: Type of heritage site
- **wikidata_id**: Wikidata identifier
- **description**: Clean SEO description (150-155 chars)
- **categories**: Array of category classifications
- **images**: Array of image paths (max 5 images per site)

### German States (16 Bundesländer)
1. Baden-Württemberg
2. Bavaria
3. Berlin
4. Brandenburg
5. Bremen
6. Hamburg
7. Hesse
8. Lower Saxony
9. Mecklenburg-Vorpommern
10. North Rhine-Westphalia
11. Rhineland-Palatinate
12. Saarland
13. Saxony
14. Saxony-Anhalt
15. Schleswig-Holstein
16. Thuringia

### Category Types Found
- church building
- palace
- cultural site
- [Add others as discovered]

## Image Organization

### Image Naming Convention
```
/images-sites/{site-slug}/{number}-{hash}-{width}w.webp
```

Example:
```
/images-sites/neuschwanstein-castle/01-abc123-320w.webp
/images-sites/neuschwanstein-castle/01-abc123-640w.webp
/images-sites/neuschwanstein-castle/01-abc123-1024w.webp
/images-sites/neuschwanstein-castle/01-abc123-1920w.webp
```

### Image Guidelines
- **Format**: WebP only
- **Sizes**: 320w, 640w, 1024w, 1920w
- **Max per site**: 5 images (to keep build time reasonable)
- **Total size**: Should stay under 1GB for fast builds

## Maintenance Scripts

### Python Scripts (Location: root directory)

1. **fix_regions_taxonomy.py**
   - Adds missing `regions:` taxonomy to site files
   - Maps `region:` field to `regions:` array

2. **fix_all_regions.py**
   - Converts city names to proper German states
   - Maintains CITY_TO_STATE mapping

3. **clean_and_fix_descriptions.py**
   - Removes old descriptions
   - Extracts clean descriptions from content
   - Properly escapes YAML values

4. **fix_all_frontmatter_quotes.py**
   - Fixes quote mismatches in frontmatter
   - Standardizes to double quotes

### When to Run Scripts
- **After bulk content updates**: Run all scripts in order
- **New site additions**: Run fix_regions_taxonomy.py
- **Description updates**: Run clean_and_fix_descriptions.py
- **YAML errors**: Run fix_all_frontmatter_quotes.py

## Key Layout Files

### layouts/sites/list.html
**Purpose**: Main heritage sites listing page with filters

**Key Features**:
- Alpine.js powered filtering (Category, Region, UNESCO, Search)
- Displays 12 sites per page with infinite scroll
- Filters match actual data from site files

**Filter Options**:
```javascript
- selectedCategory: All/church building/palace/cultural site
- selectedRegion: All/[16 German states]
- selectedUnesco: All/UNESCO/Non-UNESCO
- searchQuery: Text search
```

### layouts/partials/site-card.html
**Purpose**: Card component for displaying sites in grid

**Key Features** (Line 46-52):
- Shows description field if available
- Falls back to cleaned summary (no markdown)
- Removes ##Overview, **, and other markdown syntax
- Truncates to 150 characters

### layouts/_default/single.html
**Purpose**: Individual site detail page

**Key Features** (Line 68):
- Photo gallery with 600px (mobile) to 700px (desktop) height
- Navigation arrows and thumbnail strip
- Responsive image loading

## Hugo Configuration

### Important Settings in config.toml
```toml
[taxonomies]
  category = "categories"
  tag = "tags"
  region = "regions"
```

### Build Performance
- Development build: ~35 seconds
- Production build: Similar (no image processing)
- File watching: Enabled for fast rebuilds

## Common Issues and Solutions

### Issue: YAML parsing errors
**Solution**: Run `fix_all_frontmatter_quotes.py`

### Issue: Regions page empty
**Solution**: Run `fix_regions_taxonomy.py` to add regions taxonomy

### Issue: Markdown showing in descriptions
**Solution**: Run `clean_and_fix_descriptions.py`

### Issue: Slow build times
**Solution**:
- Check image count (should be ~3,500 max)
- Check content file count (should be ~1,100 max)
- Remove any backup folders from content/

### Issue: Filters not working
**Solution**: Verify filter options in list.html match actual data

## Archive Locations

**Moved outside Hugo directory** (to prevent processing):
```
../../sites_backup_archive/     # Duplicate sites backup
../../sites_full_archive/       # Duplicate sites full
../../content_locations_archive/ # Location files (2,901 files)
../../images-sites_temp_dev/    # Temporary image storage
```

## Preparing for Multi-Country Expansion

### Steps to Clone for Another Country:

1. **Copy entire project folder**
   ```bash
   cp -r worldheritage-germany worldheritage-france
   ```

2. **Update config.toml**
   ```toml
   baseURL = "https://worldheritage.guide/france/"
   languageCode = "fr"
   title = "World Heritage Sites - France"
   ```

3. **Replace content/sites/ files**
   - Remove all German site files
   - Add new country's site files

4. **Update region lists**
   - In `fix_all_regions.py`: Update CITY_TO_STATE mapping
   - In `layouts/sites/list.html`: Update region dropdown options

5. **Run maintenance scripts**
   ```bash
   python fix_all_regions.py
   python fix_regions_taxonomy.py
   python clean_and_fix_descriptions.py
   python fix_all_frontmatter_quotes.py
   ```

6. **Verify build**
   ```bash
   hugo server -D
   ```

### What to Keep the Same:
- Layout files (unless design changes needed)
- Python maintenance scripts (update mappings only)
- Image organization structure
- Frontmatter field structure

### What to Change:
- Site content files
- Region/state names
- Language settings
- Base URL

## Quality Checklist

Before considering the site "production ready":

- [ ] All sites have proper frontmatter (no YAML errors)
- [ ] All sites have descriptions
- [ ] All sites have region and regions fields
- [ ] Images are optimized WebP format
- [ ] Max 5 images per site
- [ ] Total image size under 1GB
- [ ] Build completes in under 60 seconds
- [ ] All filters work correctly
- [ ] No duplicate content folders
- [ ] No markdown appears in card descriptions
- [ ] Photo gallery displays at proper size
- [ ] Regions page shows all states with content

## Contact and Notes

**Created**: January 2026
**Hugo Version**: v0.152.2-extended
**Purpose**: Maintain clean, organized structure for multi-country expansion

**Key Philosophy**: "her şeyin tam bir düzeni olmalı" (everything should have proper order)
- Single source of truth for content (content/sites/)
- Consistent frontmatter structure
- Automated maintenance scripts
- Clear documentation for future developers
