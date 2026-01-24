# Internal Linking Strategy

Internal linking is critical for SEO, user experience, and converting blog readers into site users. This document defines our internal linking strategy.

---

## Strategic Goals

**SEO Goals:**
- Distribute page authority throughout site
- Help search engines understand site structure
- Boost rankings for target pages
- Reduce bounce rate by encouraging exploration

**User Experience Goals:**
- Guide readers to relevant content
- Create natural discovery paths
- Build trust through depth of content
- Convert blog readers to heritage site explorers

**Conversion Goals:**
- 15%+ of blog readers click to heritage site pages
- 10%+ explore multiple heritage sites
- 5%+ use trip planner (when launched)

---

## Link Types & Requirements

### 1. Blog Post → Heritage Site Pages

**Requirement:** Every blog post must link to minimum 5 heritage site pages (10-15 ideal)

**Best Practices:**
- Use contextual anchor text (site names, descriptive phrases)
- Link naturally within content (not forced)
- Distribute throughout post (not all at end)
- Link to variety of sites (not just famous ones)
- Include in examples, comparisons, recommendations

**Examples of Good Anchor Text:**
✅ "Cologne Cathedral is Germany's most visited landmark"
✅ "The Gothic masterpiece of Cologne Cathedral dominates the skyline"
✅ "Visit the stunning Neuschwanstein Castle in Bavaria"
✅ "Explore the medieval old town of Regensburg"

**Examples of Bad Anchor Text:**
❌ "Click here to learn more"
❌ "This site" (too vague)
❌ "Link" or "Read more"
❌ Over-optimized: "UNESCO World Heritage Site Cologne Cathedral Germany"

**Template for Blog Posts:**

```markdown
<!-- Natural integration in content -->
The Gothic architecture of [Cologne Cathedral](/sites/cologne-cathedral/)
represents one of the finest examples of High Gothic construction...

<!-- Comparison context -->
While Neuschwanstein gets more attention, [Hohenzollern Castle](/sites/hohenzollern-castle/)
offers equally stunning views...

<!-- List/recommendation context -->
Must-visit sites in Bavaria:
- [Neuschwanstein Castle](/sites/neuschwanstein-castle/): Fairy tale fantasy
- [Würzburg Residence](/sites/wurzburg-residence/): Baroque masterpiece
- [Regensburg Old Town](/sites/regensburg/): Medieval preservation
```

---

### 2. Heritage Site Pages → Blog Posts

**Requirement:** Add "Related Articles" section to heritage site single page template

**Implementation:**
Add to `layouts/sites/single.html` after main content:

```html
<!-- Related Blog Articles -->
{{ $siteName := .Title }}
{{ $siteSlug := .File.BaseFileName }}
{{ $relatedPosts := slice }}

<!-- Find posts that link to this site or mention it -->
{{ range where .Site.RegularPages "Section" "blog" }}
  {{ if or (in .Content $siteName) (in .Content $siteSlug) }}
    {{ $relatedPosts = $relatedPosts | append . }}
  {{ end }}
{{ end }}

{{ if gt (len $relatedPosts) 0 }}
<section class="related-articles bg-cream py-12 mt-12">
  <div class="container-custom">
    <h2 class="text-3xl font-serif font-bold text-charcoal mb-8">Related Articles</h2>
    <div class="grid md:grid-cols-3 gap-8">
      {{ range first 3 $relatedPosts }}
        <article class="bg-white rounded-xl shadow-soft overflow-hidden hover:shadow-medium transition-shadow">
          {{ with .Params.featured_image }}
            <img src="{{ . | relURL }}" alt="{{ $.Title }}" class="w-full h-48 object-cover">
          {{ end }}
          <div class="p-6">
            {{ with .Params.blog_category }}
              <span class="badge badge-small">{{ . }}</span>
            {{ end }}
            <h3 class="text-xl font-serif font-bold mt-3 mb-2">
              <a href="{{ .Permalink }}" class="hover:text-forest-600">{{ .Title }}</a>
            </h3>
            <p class="text-stone text-sm mb-4 line-clamp-2">{{ .Params.excerpt }}</p>
            <a href="{{ .Permalink }}" class="text-forest-600 hover:text-forest-700 font-semibold text-sm">
              Read Article →
            </a>
          </div>
        </article>
      {{ end }}
    </div>
  </div>
</section>
{{ end }}
```

**Manual Curation Option:**
For key sites, manually specify related posts in front matter:

```yaml
# In site front matter
related_posts:
  - /blog/cologne-cathedral-guide/
  - /blog/gothic-architecture-germany/
  - /blog/how-to-photograph-cathedrals/
```

---

### 3. Blog Post → Blog Post

**Requirement:** Link to 3-5 related blog posts in each post

**Implementation Methods:**

**Method A: Contextual Links (Best)**
Naturally link within content when relevant topic arises:

```markdown
For more on Gothic architecture, see our [complete guide to Gothic
architecture in Germany](/blog/gothic-architecture-guide/).

If you're planning a multi-site trip, check out our guide on
[how to plan a German heritage road trip](/blog/heritage-road-trip/).
```

**Method B: "See Also" Boxes**
Use callout boxes for related topics:

```markdown
**Related Reading:** Learn more about [photographing German cathedrals](/blog/cathedral-photography/)
in our complete photography guide.
```

**Method C: Related Posts at Bottom (Automatic)**
Use Hugo's `.Site.RegularPages.Related` function:

```html
<!-- Add to blog single template -->
{{ $related := .Site.RegularPages.Related . | first 3 }}
{{ with $related }}
<section class="related-posts mt-12 pt-12 border-t border-sand">
  <h3 class="text-2xl font-serif font-bold mb-6">You Might Also Like</h3>
  <div class="grid md:grid-cols-3 gap-8">
    {{ range . }}
      <!-- Blog card partial -->
      {{ partial "blog-card-small.html" . }}
    {{ end }}
  </div>
</section>
{{ end }}
```

**Configuration for Related Posts:**
Add to `config.toml`:

```toml
[related]
  includeNewer = true
  threshold = 80
  toLower = false

  [[related.indices]]
    name = "blog_category"
    weight = 100

  [[related.indices]]
    name = "tags"
    weight = 80

  [[related.indices]]
    name = "date"
    weight = 10
```

---

### 4. Category Pages → Relevant Content

**Blog Category Pages:**
Link to relevant heritage sites of same type

Example for `Travel Guides` category page:
```html
<div class="recommended-sites mt-8">
  <h3>Plan Your Trip</h3>
  <p>Explore our heritage site guides to start planning:</p>
  <ul>
    <li><a href="/sites/">Browse All Sites</a></li>
    <li><a href="/tags/unesco/">UNESCO World Heritage Sites</a></li>
    <li><a href="/regions/">Sites by Region</a></li>
  </ul>
</div>
```

**Heritage Site Category Pages:**
Link to relevant blog posts

Example for `Castles` category:
```html
<div class="blog-links mt-8">
  <h3>Castle Guides & Tips</h3>
  <ul>
    <li><a href="/blog/best-castles-germany/">50 Most Beautiful Castles</a></li>
    <li><a href="/blog/castle-photography/">How to Photograph Castles</a></li>
    <li><a href="/blog/castle-history/">Medieval Castle History</a></li>
  </ul>
</div>
```

---

### 5. Author Pages → Their Content

**Implementation:**
Author archive pages should link to:
- Sites they've "covered" (based on linking)
- Their blog posts (automatic)
- Their area of expertise

```html
<!-- In layouts/authors/term.html -->
<section class="expert-insights">
  <h3>{{ $authorData.name }}'s Expertise</h3>
  <div class="grid md:grid-cols-2 gap-6">
    <div>
      <h4>Featured Sites</h4>
      <!-- List sites this author writes about most -->
    </div>
    <div>
      <h4>Latest Articles</h4>
      <!-- Their blog posts -->
    </div>
  </div>
</section>
```

---

## Link Distribution Guidelines

### For Ultimate Guides (3000-5000 words)
- **Heritage sites:** 10-15 links
- **Blog posts:** 3-5 links
- **Category pages:** 1-2 links
- **Total internal links:** 15-20

### For Listicles (1500-2500 words)
- **Heritage sites:** 10-25 links (one per list item)
- **Blog posts:** 2-3 links
- **Category pages:** 1 link
- **Total internal links:** 15-30

### For How-To Guides (1800-2500 words)
- **Heritage sites:** 8-12 links
- **Blog posts:** 3-5 links
- **Tool/resource pages:** 1-2 links
- **Total internal links:** 12-18

### For Comparison Posts (2000-3000 words)
- **Heritage sites:** 5-10 links (sites being compared)
- **Blog posts:** 3-4 links
- **Category pages:** 1-2 links
- **Total internal links:** 10-15

---

## Strategic Linking Priorities

### Tier 1: Priority Pages (Link Often)
These should receive most internal links:

**Heritage Sites:**
- UNESCO sites
- Most popular sites (Neuschwanstein, Cologne Cathedral, etc.)
- Sites with best content/photos

**Blog Posts:**
- 10 link magnet posts
- Ultimate guides
- Evergreen how-to guides

**Pages:**
- Homepage
- Main category pages
- Trip planner (when live)

### Tier 2: Support Pages (Link Moderately)
- Lesser-known heritage sites
- Seasonal guides
- Specific photography tutorials
- Regional guides

### Tier 3: Deep Content (Link Occasionally)
- Historical narratives
- Conservation stories
- Very specific guides

---

## Link Patterns to Avoid

**Over-Optimization:**
❌ Don't use exact match keywords repeatedly
❌ Don't link same page multiple times in one post (unless far apart)
❌ Don't use robotic, unnatural anchor text

**Poor User Experience:**
❌ Don't link in first sentence (readers just started)
❌ Don't have walls of links (break them up)
❌ Don't link to irrelevant content (destroys trust)

**Technical Issues:**
❌ Don't link to 404 pages (audit regularly)
❌ Don't create orphan pages (no internal links in or out)
❌ Don't create circular link patterns

---

## Link Maintenance

### Monthly Audit Tasks

**Check for Broken Links:**
```bash
# Use broken link checker
npm install -g broken-link-checker
blc http://localhost:1313 -ro
```

**Review Link Distribution:**
- Are new posts getting linked from older posts?
- Are older posts still getting links?
- Which pages have no/few internal links?

**Update Links:**
- When publishing new comprehensive guide, update older posts to link to it
- When site page is significantly updated, verify blog links are still relevant

### Quarterly Review

**Analyze Internal Link Performance:**
- Which internal links get most clicks?
- Which blog posts drive most traffic to sites?
- Which heritage sites get most blog referral traffic?

**Strategic Adjustments:**
- Add more links to underperforming pages
- Create new content to support priority pages
- Update link anchor text based on keyword research

---

## Link Tracking

### Implementation

**Add Click Tracking (Optional):**
Use data attributes for analytics:

```html
<a href="/sites/cologne-cathedral/"
   data-link-type="blog-to-site"
   data-link-source="ultimate-guide-post">
  Cologne Cathedral
</a>
```

**Track in Analytics:**
- Blog → Site click-through rate
- Most clicked internal links
- Path analysis (what do readers click after blog post?)

### Key Metrics to Monitor

**Overall:**
- Average internal links per post
- Click-through rate (blog → sites)
- Pages per session (from blog entry)

**Per Post:**
- Which internal links get clicked
- Scroll depth to links
- Exit rate vs pages with more links

---

## Quick Reference Checklist

**Before Publishing Any Blog Post:**

- [ ] Minimum 10 total internal links?
- [ ] At least 5 links to heritage site pages?
- [ ] At least 2-3 links to other blog posts?
- [ ] Natural, contextual anchor text?
- [ ] Links distributed throughout post?
- [ ] All links tested and working?
- [ ] Link to at least one priority page?
- [ ] Variety of link targets (not all same site)?

---

## Examples of Excellent Internal Linking

### Example 1: From "50 Most Beautiful Castles" Post

```markdown
## 1. Neuschwanstein Castle

Bavaria's iconic [Neuschwanstein Castle](/sites/neuschwanstein-castle/)
sits perched on a rugged hill above the village of Hohenschwangau.
Built by King Ludwig II in the late 19th century, this Romanesque
Revival palace inspired Disney's Sleeping Beauty Castle.

**Why It's #1:** The combination of dramatic Alpine setting, fairy-tale
architecture, and fascinating history make Neuschwanstein Germany's
most photographed building. For tips on capturing the perfect shot,
see our [castle photography guide](/blog/how-to-photograph-castles/).

**Visit Info:**
- Location: [Bavaria](/regions/bavaria/)
- Best viewed from: Marienbrücke
- Also visit: Nearby [Hohenschwangau Castle](/sites/hohenschwangau-castle/)
```

**Analysis:**
- ✅ Natural integration of links
- ✅ Contextual anchor text
- ✅ Mix of site pages and blog posts
- ✅ Regional link for broader exploration
- ✅ Related site recommendation

---

### Example 2: From "Gothic Architecture Guide" Post

```markdown
## Cologne Cathedral: The Ultimate Gothic Achievement

No discussion of German Gothic is complete without [Cologne Cathedral](/sites/cologne-cathedral/),
the country's most visited landmark and a UNESCO World Heritage Site.
Construction began in 1248 but wasn't completed until 1880—a 632-year
building project that resulted in one of the world's largest cathedrals.

**What Makes It Special:**

The cathedral showcases High Gothic architecture at its finest. The twin
spires soar 157 meters, making them the tallest twin spires in the world.
Inside, the Shrine of the Three Kings draws pilgrims from around the world.

For a detailed guide to visiting, see our [complete Cologne Cathedral guide](/blog/cologne-cathedral-complete-guide/).
Photography enthusiasts should read our [cathedral photography tutorial](/blog/photographing-german-cathedrals/)
for tips on capturing the stunning stained glass windows.

**Compare:** How does Cologne Cathedral stack up against other European
giants? Read our [cathedral comparison](/blog/cologne-cathedral-vs-european-cathedrals/).
```

**Analysis:**
- ✅ Primary site link prominent
- ✅ Supporting blog posts linked naturally
- ✅ Cross-references create content web
- ✅ Provides clear value for clicking
- ✅ Different link types (site, guide, tutorial, comparison)

---

**Last Updated:** January 2026
**Review Frequency:** Monthly
**Owner:** Content Team
