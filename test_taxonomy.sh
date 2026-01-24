#!/bin/bash

# Test Hugo taxonomies
echo "=== Testing Hugo Taxonomies ==="
echo ""

# Build site
hugo --cleanDestinationDir --quiet

# Check generated pages
echo "Generated pages:"
find public -name "index.html" -path "*/heritage-types/*" -o -path "*/regions/*" -path "*/tags/*" 2>/dev/null | head -20

echo ""
echo "Checking public directory structure:"
ls -la public/heritage-types/ 2>/dev/null || echo "heritage-types not found"
ls -la public/regions/ 2>/dev/null || echo "regions not found"
ls -la public/tags/ 2>/dev/null || echo "tags not found"

