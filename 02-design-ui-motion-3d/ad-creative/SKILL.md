---
name: ad-creative
description: Generate, iterate, and scale paid ad creative — hooks, headlines, descriptions, primary text, static image briefs, video scripts. Use when asked to "write ad copy", "generate ad variations", "RSA headlines", "ad creative for [campaign]", "bulk ad copy", "ad iterations", or "creative testing". Pairs with paid-ads-context for ICP and voice, with apple-grade-design for visual production, and with paid-channel-recap to know which creatives won.
metadata:
  version: 1.0.0
---

# Ad Creative

Generate paid ad creative at the scale paid ads actually need — 10-20 headlines per RSA, 5-10 hooks per video concept, 3-5 static image briefs per ad set. Most agents produce 2-3 generic options. This skill produces enough variation to actually run a test.

## Before starting

**Read `paid-ads-context.md` first** if it exists. The skill needs:

- ICP (section 1) — who this is talking to
- Brand voice + hard nos (section 5) — what NOT to say
- Recent winning creative (if you've run a `paid-channel-recap`, the section 4 creative attribution is the input)

If no context file exists, ask 5-7 focused questions and offer to write a partial one back.

## What the skill outputs

| Format | Volume | Notes |
|---|---|---|
| Google RSA headlines | 15 (the max Google accepts) | Each ≤30 chars including spaces |
| Google RSA descriptions | 4 (the max) | Each ≤90 chars |
| Meta primary text | 5-10 | First 3 lines matter most (Meta truncates) |
| Meta headlines | 5-10 | ≤40 chars |
| Meta descriptions | 5-10 | ≤30 chars |
| Video hook scripts | 5-10 first lines | The first 3 seconds determine watch rate |
| Static ad briefs | 3-5 concepts | One paragraph per concept, generates the Nano Banana prompt |
| UGC scripts | 1-3 full 30-60s scripts | Bracket-formatted for the creator to follow |

## The hook is the variable that matters most

Same product, same offer, same creator — different opening line — 2-3x CAC swing. The skill prioritizes hook generation over body copy.

Hook patterns that work (test 3-4 per campaign):

| Pattern | Example shape | When to use |
|---|---|---|
| Problem statement | "Stop {bad thing customers do}" | Their pain is named and obvious |
| Contrarian belief | "Everyone says {X}. They're wrong." | You have a sharp POV |
| Specific result | "How [named person] hit [specific number] in [timeframe]" | You have a real customer to point to |
| Curiosity gap | "I tried [X] for 30 days. Here's what happened." | Your category is novel |
| Direct offer | "Get [product] for [price] — today only" | Price is a real edge |
| Question | "What do [ICP] do when [bad situation]?" | You want to filter for ICP self-selection |
| Pattern interrupt | "STOP scrolling. This is for [ICP] only." | High-volume cold audiences |

The skill generates 5-10 hooks per campaign, spread across these patterns. Then you test, the winners earn more budget.

## The five-line brief format

For every creative the skill produces, it builds against this brief:

```
Goal:        [What this ad does in one verb]
Audience:    [The named ICP, not "everyone"]
Anchor copy: [The single line you will NOT change in testing]
Mood:        [Three adjectives]
Constraints: [Hard rules — real numbers, real names, no inventions]
```

This is the same brief format as the `apple-grade-design` skill — so when you go from copy to visuals, the brief travels.

## Hard nos the skill enforces

Pulled from `paid-ads-context.md` section 5, plus universal AI-tell guardrails:

- No em dashes for dramatic effect
- No "It's not X, it's Y" contradictory takes
- No "The best part?" / "Here's the thing..." / "The truth is..."
- No "No fluff. No filler." staccato phrasing
- No "In the ever-evolving world of..."
- No corporate buzzwords (unlock, empower, transform, leverage, synergy, ecosystem)
- No fake testimonials, no invented customer quotes
- No fake scarcity unless the scarcity is real
- No outcome claims without a real source

If your brand has additional hard nos in section 5, the skill enforces those too.

## Workflow

### 1. Spec gathering

The skill asks (or reads from context):

- The campaign / offer
- The ICP (from `paid-ads-context.md` section 1)
- The platform(s) — formats vary
- Any winning patterns from previous tests
- Length constraints
- Hard nos

### 2. Generate

Produces volume per the table above. Each variation is built against the five-line brief.

### 3. Self-audit

Before returning the output, the skill checks every line against:

- Character count limits (RSA = 30/90, Meta varies)
- Hard nos list
- Brand voice rules (if `voice-profile.md` exists, also runs the voice audit)
- Specificity check — does the line have a real number / name / claim, or is it generic?

Lines that fail any check are rewritten or flagged.

### 4. Output

Markdown table with: variation #, copy, format, char count, pattern type (hook / body / CTA), expected use case.

If asked, can also output as a CSV ready for bulk upload to Google Ads Editor or Meta Bulk Import.

## Static ad briefs (when needed)

For static image ads, the skill produces a brief Nano Banana 2 MCP can consume:

```
Aspect ratio: 1:1 (Meta feed) | 9:16 (story/reel) | 16:9 (YouTube)
Subject:      [What's in the image — describe specifically]
Setting:      [Background / context]
Composition:  [Where the subject is in frame]
Style:        [Photographic / illustration / motion graphic]
Text overlay: [The exact copy that goes on the image, or "no text"]
Color palette: [Brand colors or hex codes]
Mood:         [Three adjectives]
Hard nos:     "No generic stock photo, no corporate stockiness, no AI-looking composition"
```

Then call `apple-grade-design` or Nano Banana 2 MCP directly to generate.

## UGC scripts

For UGC video, the skill produces a 30-60s script with brackets the creator can follow:

```
[0:00 - HOOK]  Direct-to-camera. First line, designed to stop the scroll.
[0:03 - PIVOT] One-line acknowledgment of the viewer's problem.
[0:08 - DEMO]  Show the product. Specific feature, not generic.
[0:18 - PROOF] One real number, one real outcome.
[0:30 - CTA]   "Get [product] at [URL]. Code [code] for [discount]."
```

Scripts are written for ONE creator at a time. If you have multiple, each gets its own script tuned to their tone.

## Don't do these (anti-patterns)

| Anti-pattern | Why | Fix |
|---|---|---|
| "Write 5 RSA headlines for [product]" | You'll get 5 versions of the same headline | Specify: 5 with the problem-statement pattern, 5 with the specific-result pattern, 5 with curiosity-gap |
| Generating without an ICP | Output is generic mush | Make `paid-ads-context.md` mandatory before generation |
| One round of generation, ship | Volume is the point of the skill | At least 2 rounds: generate 20, cut to 10, iterate the 10, ship 5 |
| No char-count check | Truncated ads die quietly | Self-audit step is non-negotiable |
| Voice match without a profile | Sounds like AI | If no `voice-profile.md`, ask for 2-3 real lines the brand has shipped as anchors |

## Related skills

- [`paid-ads-context`](https://github.com/nickyc1/paid-ads-context) — provides ICP, voice, hard nos
- [`voice-profile-kit`](https://github.com/nickyc1/voice-profile-kit) — provides the brand voice doc this skill audits against
- [`apple-grade-design`](https://github.com/nickyc1/apple-grade-design) — consumes the static brief output to produce the visuals
- [`paid-channel-recap`](https://github.com/nickyc1/paid-channel-recap) — outputs from this skill are what get measured there; recap winners feed back as input here
- [`customer-research`](https://github.com/nickyc1/customer-research) — provides the real-customer language that anchors hooks
- [`google-ads-manager`](https://github.com/nickyc1/google-ads-manager) — consumes the RSA output for campaign builds

## References

- [`references/hook-patterns.md`](references/hook-patterns.md) — full library of hook patterns with examples
- [`references/platform-character-limits.md`](references/platform-character-limits.md) — current char limits per platform / format
- [`references/static-brief-template.md`](references/static-brief-template.md) — the brief format for static image generation
- [`references/ugc-script-template.md`](references/ugc-script-template.md) — bracket-format script template
- [`templates/rsa-output.csv`](templates/rsa-output.csv) — CSV format for Google Ads Editor bulk upload
- [`templates/meta-bulk-output.csv`](templates/meta-bulk-output.csv) — CSV format for Meta Bulk Import
