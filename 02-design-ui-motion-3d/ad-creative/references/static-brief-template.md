# Static Ad Brief Template

The brief you hand to Nano Banana 2 MCP (or any image-generation tool) to produce a static ad image.

## The template

```
Goal:           [One sentence — what this image must do]
Audience:       [The named ICP]
Anchor copy:    [The exact text overlay, or "no text overlay"]
Mood:           [Three adjectives]
Constraints:    [Hard rules — real product, real brand colors, no AI-looking composition]

---

Aspect ratio:   [1:1 | 9:16 | 16:9 | 4:5]
Subject:        [What's in the image — specific]
Setting:        [Background / context]
Composition:    [Where subject is in frame: rule of thirds, centered, top-left, etc.]
Style:          [Photographic | illustration | motion graphic | screenshot | composite]
Lighting:       [Soft / hard / dramatic / natural / studio]
Color palette:  [Brand colors as hex codes, or "match design-tokens.json"]
Text overlay:   [Exact text, or "no text"]
Font:           [If text — the brand font]
Logo:           [Where the logo goes, or "no logo"]

Hard nos:       "No generic stock photo, no corporate stockiness, no AI-looking composition,
                 no clip-art icons, no hexagon-grid background, no glowing edges,
                 no purple-to-blue gradient"
```

## Example: Price-comparison ad

```
Goal:           Make a viewer doing math on a competitor stop scrolling
Audience:       SaaS founders evaluating CRM tools
Anchor copy:    "$49 vs $180/mo" with "Lifetime" badge
Mood:           Confident, direct, slightly cheeky
Constraints:    Use real competitor name (HubSpot). No fake review badges.

Aspect ratio:   1:1
Subject:        Two price tags side by side
Setting:        Clean white background, slight texture
Composition:    Center, balanced
Style:          Editorial flat illustration with photographic shadows
Lighting:       Studio soft, top-left key
Color palette:  #FFDE33 (accent), #0b0d12 (primary text), #ffffff (bg)
Text overlay:   "$49 lifetime / $180 per month" (left side: $49, right side: $180)
Font:           Inter Tight, 800 weight on numbers
Logo:           Brand mark bottom-right, small

Hard nos:       "No stock photo, no AI-looking composition, no glowing edges,
                 no hexagon grid, no purple gradients"
```

## Example: UGC-style screenshot mockup

```
Goal:           Build trust by showing the actual tool
Audience:       Performance marketers evaluating analytics dashboards
Anchor copy:    "Real data. Real dashboard." (small, top corner)
Mood:           Honest, technical, trustworthy
Constraints:    Use the actual dashboard UI. Not a re-imagined version.

Aspect ratio:   9:16 (Reels / Stories / Pinterest)
Subject:        Mobile device showing a dashboard screenshot
Setting:        Slight desk surface, partial keyboard visible
Composition:    Phone occupies center 2/3 of frame, tilted slightly
Style:          Product photography, naturalistic
Lighting:       Window-side soft natural light
Color palette:  Brand teal + warm wood desk tone
Text overlay:   "Real data. Real dashboard." top-right corner, small caps
Font:           System UI
Logo:           Embedded in the screenshot itself

Hard nos:       "No fake dashboard, no glowing screen, no neon, no AI-looking composition"
```

## How Nano Banana 2 consumes this

Stitch the brief into one prompt:

```
Generate an image with these specs:

Aspect ratio: [from brief]
Subject: [from brief]
Setting: [from brief]
Composition: [from brief]
Style: [from brief]
Lighting: [from brief]
Color palette: [from brief]
Text overlay: [from brief]

Mood: [three adjectives]
Hard nos: [the explicit list]

Important: this is a paid ad creative. It must look like it was shot/designed
on purpose, not auto-generated. Reject any composition that reads as AI.
```

## What separates a good brief from a bad one

| Bad | Good |
|---|---|
| "A happy customer using our product" | "A 32-year-old woman, brown hair pulled back, looking down at her laptop on a wooden kitchen table, slight smile, sweater, morning light" |
| "Modern, clean design" | "Editorial flat illustration on off-white, sharp 4px stroke weights, type set in Inter Tight 800 at 96pt, single accent color #FFDE33" |
| "Show the product working" | "A close-up of the dashboard's 'spend by campaign' chart on a 13-inch MacBook screen, taken from a 30-degree angle, slight reflection on screen" |

The good versions can be photographed or designed by a real person. The bad versions are dreams.

## After the image generates

Run it through the `apple-grade-design` skill's `references/critique-checklist.md`. Specifically the swap test:

> Could you swap your product name for a competitor's and have the image still work? If yes, the image is too generic. Restart.
