# Call-to-Action (CTA) Strategy

This document defines how to guide blog readers to take desired actions.

---

## Strategic Goals

**Primary Goals:**
1. Drive traffic to heritage site pages (15%+ CTR)
2. Encourage site exploration (3+ pages per session)
3. Build email list (5%+ conversion, when launched)
4. Trip planner usage (10%+ when launched)

**Secondary Goals:**
- Social follows
- Content sharing
- Comment engagement
- Return visits

---

## CTA Types & Placement

### 1. Inline Contextual CTAs

**What:** Natural links within content
**Where:** Throughout post body
**Goal:** Heritage site exploration

**Format:**
```markdown
[Cologne Cathedral](/sites/cologne-cathedral/) dominates the Cologne skyline...

For a complete guide to visiting, see our [Cologne Cathedral page](/sites/cologne-cathedral/).

Explore our [complete guide to Neuschwanstein Castle](/sites/neuschwanstein-castle/)
for visiting hours, tickets, and insider tips.
```

**Best Practices:**
- 5-15 per post
- Natural integration
- Descriptive anchor text
- Mix of site and blog links

---

### 2. End-of-Post Primary CTA

**What:** Main action at post conclusion
**Where:** Final paragraph before author bio
**Goal:** Next step aligned with post topic

**Templates by Content Type:**

**Ultimate Guide:**
```markdown
Ready to explore? Browse our [complete collection of German heritage sites](/sites/)
or start planning your trip with our [interactive trip planner](/trip-planner/).
```

**Listicle (Castles):**
```markdown
Which castle will you visit first? Explore detailed guides for each castle
on our [castles page](/heritage-types/castle/) or plan your [castle road trip](/blog/castle-road-trip/).
```

**How-To (Road Trip):**
```markdown
Start planning your heritage road trip with our [interactive map of all sites](/map/)
or browse [sites by region](/regions/) to plan your route.
```

**Photography Guide:**
```markdown
Ready to capture stunning heritage photos? Find the [best viewpoints at each site](/sites/)
or explore our [photography guides collection](/blog/category/photography/).
```

**Historical Narrative:**
```markdown
Visit [this historic site today](/sites/[site-slug]/) to experience the history
firsthand, or explore [more historical stories](/blog/category/history/).
```

---

### 3. Visual CTA Boxes

**What:** Styled callout boxes with clear action
**Where:** Mid-content or end of major sections
**Goal:** Break monotony, draw attention

**HTML Component:**
```html
<div class="cta-box">
  <h3>Plan Your Visit</h3>
  <p>Ready to explore German heritage sites? Use our interactive tools:</p>
  <div class="cta-buttons">
    <a href="/sites/" class="btn btn-primary">Browse All Sites</a>
    <a href="/map/" class="btn btn-secondary">View Map</a>
  </div>
</div>
```

**CSS Styling:**
```css
.cta-box {
  background: linear-gradient(135deg, #f8f6f3 0%, #e8e4de 100%);
  border-left: 4px solid #2C5F2D;
  padding: 2rem;
  margin: 3rem 0;
  border-radius: 8px;
}

.cta-buttons {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}
```

**Placement:**
- After major section (every 800-1000 words)
- Before FAQ section
- At end of post

---

### 4. Sidebar CTAs (Desktop)

**What:** Persistent CTAs in sidebar
**Where:** Desktop view only (no mobile clutter)
**Goal:** Always-visible next steps

**Components:**

**Newsletter Signup (when launched):**
```html
<div class="sidebar-cta">
  <h3>Weekly Heritage Insights</h3>
  <p>Get expert tips, new site guides, and travel inspiration.</p>
  <form>
    <input type="email" placeholder="Your email">
    <button type="submit">Subscribe</button>
  </form>
</div>
```

**Featured Sites:**
```html
<div class="sidebar-cta">
  <h3>Featured Sites</h3>
  <ul class="featured-sites-list">
    <li><a href="/sites/neuschwanstein/">Neuschwanstein Castle</a></li>
    <li><a href="/sites/cologne-cathedral/">Cologne Cathedral</a></li>
    <li><a href="/sites/rothenburg/">Rothenburg ob der Tauber</a></li>
  </ul>
  <a href="/sites/" class="text-link">View all sites →</a>
</div>
```

**Trip Planner Promo (when launched):**
```html
<div class="sidebar-cta highlight">
  <h3>Plan Your Perfect Trip</h3>
  <p>Create custom itineraries with our trip planner.</p>
  <a href="/trip-planner/" class="btn btn-primary">Start Planning</a>
</div>
```

---

### 5. Exit-Intent Popup (Future)

**What:** Popup when user about to leave
**When:** After 30 seconds on page, on exit intent
**Goal:** Capture email or drive to trip planner

**Template:**
```html
<div class="exit-popup">
  <button class="close">×</button>
  <h2>Wait! Before You Go...</h2>
  <p>Get our free "10 Must-Visit Heritage Sites" guide + weekly tips</p>
  <form>
    <input type="email" placeholder="Enter your email">
    <button type="submit">Get Free Guide</button>
  </form>
  <p class="privacy">We respect your privacy. Unsubscribe anytime.</p>
</div>
```

**Best Practices:**
- Only show once per user
- Easy to close
- Clear value proposition
- A/B test offers

---

## CTA Copy Guidelines

### Principles

**Be Specific:**
❌ "Click here"
✅ "Explore Cologne Cathedral's complete guide"

**Use Action Verbs:**
- Explore
- Discover
- Plan
- Start
- Find
- Learn
- Browse
- Create

**Emphasize Benefit:**
❌ "View sites"
✅ "Find your perfect heritage destination"

**Create Urgency (when appropriate):**
- "Start planning your summer trip"
- "Limited time: Spring travel guide"

**Make it Easy:**
❌ "Navigate to our comprehensive site database to begin your research"
✅ "Browse all sites"

### Examples by Goal

**Goal: Site Exploration**
- "Explore [number] UNESCO World Heritage Sites"
- "Discover hidden heritage gems"
- "Find castles near you"
- "Browse sites by region"

**Goal: Trip Planning**
- "Plan your heritage road trip"
- "Create your custom itinerary"
- "Start planning your visit"
- "Build your perfect trip"

**Goal: Email Signup**
- "Get weekly heritage travel tips"
- "Join 10,000+ heritage travelers"
- "Never miss a new site guide"
- "Get free planning resources"

**Goal: Content Discovery**
- "Read more castle guides"
- "Explore our photography tutorials"
- "Discover more historical stories"
- "See all architecture guides"

---

## CTA Hierarchy

### Primary CTA (One per post)
**Most Important Action:**
- End of post
- Most prominent
- Aligns with post topic

### Secondary CTAs (2-3 per post)
**Supporting Actions:**
- Mid-content visual boxes
- Sidebar elements
- Related content links

### Tertiary CTAs (Multiple)
**Inline Links:**
- Contextual site links
- Related post links
- Category links

---

## CTA Performance Tracking

### Metrics to Monitor

**Click-Through Rate:**
- Overall CTA CTR
- CTR by CTA type
- CTR by placement
- CTR by copy variation

**Conversion Goals:**
- Blog → Site page visits
- Blog → Trip planner usage
- Blog → Email signups
- Blog → Social follows

**Engagement:**
- Pages per session from blog
- Time on site (blog entry)
- Return visit rate

### A/B Testing

**Test Variables:**
- CTA copy
- Button vs text link
- Placement
- Color/styling
- Urgency vs no urgency

**Testing Process:**
1. Hypothesis: "Button CTA will outperform text link"
2. Create variants (A/B)
3. Split traffic 50/50
4. Run for 2-4 weeks (or 1000+ visitors)
5. Analyze results
6. Implement winner
7. Test next variable

---

## CTA Templates by Post Type

### Ultimate Guide CTA

**Primary:**
```markdown
## Ready to Visit?

Explore our complete guides to every [topic] site in Germany, with
visiting hours, tickets, photography tips, and insider advice.

[Browse All [Topic] Sites](/heritage-types/[type]/) or
[Plan Your Trip](/trip-planner/)
```

### Listicle CTA

**Primary:**
```markdown
## Start Your [Topic] Journey

Which [item type] is calling your name? Explore detailed guides for
each one, complete with practical visiting information.

[View Complete [Item] Guides](/heritage-types/[type]/)
```

### How-To Guide CTA

**Primary:**
```markdown
## Ready to Put This Into Action?

Use our tools to plan your perfect German heritage trip:

[Browse Sites by Region](/regions/) | [View Interactive Map](/map/) |
[Create Custom Itinerary](/trip-planner/)
```

### Photography Tutorial CTA

**Primary:**
```markdown
## Capture Your Own Stunning Photos

Find the best photography spots at each heritage site, with golden hour
timing, viewpoint GPS coordinates, and composition tips.

[Explore Photography-Friendly Sites](/sites/?filter=photography)
```

### Historical Narrative CTA

**Primary:**
```markdown
## Experience This History Yourself

Visit [site name] today to walk where history was made.

[Plan Your Visit to [Site]](/sites/[slug]/) | [More Historical Stories](/blog/category/history/)
```

---

## Responsive CTA Design

### Mobile Considerations

**Do:**
- Large tap targets (44px minimum)
- Fixed bottom CTAs for important actions
- Minimize popup interruptions
- Simple, clear copy

**Don't:**
- Multiple CTAs competing for attention
- Small buttons
- Aggressive popups
- Complex multi-step CTAs

### Desktop Enhancements

**Leverage Space:**
- Sidebar persistent CTAs
- Larger visual CTA boxes
- Hover effects on buttons
- More detailed copy

---

## CTA Shortcodes (Hugo)

**Create reusable CTA components:**

```html
<!-- layouts/shortcodes/cta-browse-sites.html -->
<div class="cta-box">
  <h3>Explore German Heritage Sites</h3>
  <p>{{ .Get "text" | default "Discover detailed guides to every heritage site in Germany." }}</p>
  <a href="{{ .Get "url" | default "/sites/" }}" class="btn btn-primary">
    {{ .Get "button" | default "Browse All Sites" }}
  </a>
</div>
```

**Usage in markdown:**
```markdown
{{< cta-browse-sites
    text="Ready to explore Bavaria's finest castles?"
    url="/regions/bavaria/"
    button="See Bavaria Sites"
>}}
```

**Additional Shortcodes to Create:**
- `cta-trip-planner`
- `cta-newsletter`
- `cta-related-posts`
- `cta-map`

---

## Implementation Checklist

**Every Blog Post Must Have:**
- [ ] 5-15 inline contextual links (heritage sites)
- [ ] 2-3 related post links
- [ ] One clear primary CTA at end
- [ ] 1-2 visual CTA boxes (for longer posts)
- [ ] Sidebar CTA (desktop)
- [ ] All CTAs tested and working

**Monthly Review:**
- [ ] Analyze CTA performance
- [ ] A/B test underperforming CTAs
- [ ] Update copy based on results
- [ ] Test new CTA placements

---

**Last Updated:** January 2026
**Owner:** Content Team
**Review Frequency:** Monthly
