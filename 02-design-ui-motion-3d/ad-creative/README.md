# ad-creative

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://makeapullrequest.com)

A [Claude Code](https://claude.com/claude-code) skill that generates paid ad creative at the scale paid ads actually need.

Most agents produce 2-3 generic ad options. This skill produces 15 RSA headlines, 5-10 Meta hooks, 3-5 static briefs, and full UGC scripts — enough variation to actually run a test.

## Why this exists

Hooks are the variable that matters most in paid ads. Same creator, same offer, different first line — 2-3x CAC swing.

But generating enough hook variation is tedious. Generating it well, against your ICP and your brand voice, with character-count enforcement and platform-format awareness — that's a skill, not a copy-paste prompt.

## What it outputs

| Platform / format | Volume | Notes |
|---|---|---|
| Google RSA headlines | 15 (the platform max) | ≤30 chars each |
| Google RSA descriptions | 4 (the platform max) | ≤90 chars each |
| Meta primary text | 5-10 | First 3 lines matter most |
| Meta headlines | 5-10 | ≤40 chars |
| Video hook scripts | 5-10 | The first 3 seconds determine watch rate |
| Static ad briefs | 3-5 | Format that Nano Banana 2 MCP can consume |
| UGC scripts | 1-3 | Full 30-60s scripts, bracket format |

## Requirements

- [Claude Code](https://claude.com/claude-code)
- Recommended: [`paid-ads-context`](https://github.com/nickyc1/paid-ads-context) installed and filled in (provides ICP and voice context)
- Optional: [`voice-profile-kit`](https://github.com/nickyc1/voice-profile-kit) for brand voice enforcement

## Install

```bash
git clone https://github.com/nickyc1/ad-creative.git ~/.claude/skills/ad-creative
```

Restart Claude Code. The skill is available.

## Usage

In Claude Code:

```
Use ad-creative to generate 15 RSA headlines and 4 descriptions for
my Google Ads campaign on [product]. Target audience: [from context].
```

```
Generate 8 Meta hooks for the same campaign, spread across
problem-statement, contrarian-belief, and specific-result patterns.
```

```
Write a UGC script for [creator name] promoting [product]. 45 seconds.
```

```
Build static brief for a price-comparison ad. $49 vs $180. 1:1 ratio.
```

## How it thinks

The skill enforces opinions that hold up in production paid-ad work:

- **Hooks are the variable that matters.** Same product, same creator — different hook = 2-3x CAC swing. Volume of hook variation is the point.
- **Test across patterns, not within one.** Generate 4 hooks across 4 different patterns (problem statement, contrarian, specific result, curiosity gap). The winner tells you which pattern your audience responds to.
- **The five-line brief.** Every ad gets built against Goal / Audience / Anchor copy / Mood / Constraints. Same brief format as `apple-grade-design` so copy → visuals carries the same intent.
- **Self-audit before delivery.** Every line gets char-count checked, brand-voice checked, and specificity checked. Lines that fail get rewritten or flagged.

## Hard nos the skill enforces

Pulled from `paid-ads-context.md` section 5, plus universal AI-tells:

- No em dashes for dramatic effect
- No "It's not X, it's Y" contradictory takes
- No "Here's the thing..." / "The truth is..." / "The best part?"
- No "No fluff. No filler." staccato
- No "In the ever-evolving world of..."
- No corporate buzzwords
- No fake testimonials, no invented customer quotes

## Related skills

| Skill | Relationship |
|---|---|
| [`paid-ads-context`](https://github.com/nickyc1/paid-ads-context) | Provides ICP, brand voice, hard nos |
| [`voice-profile-kit`](https://github.com/nickyc1/voice-profile-kit) | Provides the brand voice doc this skill audits against |
| [`apple-grade-design`](https://github.com/nickyc1/apple-grade-design) | Consumes the static brief output to produce visuals |
| [`paid-channel-recap`](https://github.com/nickyc1/paid-channel-recap) | Outputs from here are what get measured in the recap; recap winners feed back as input |
| [`customer-research`](https://github.com/nickyc1/customer-research) | Provides real-customer language that anchors hooks |
| [`google-ads-manager`](https://github.com/nickyc1/google-ads-manager) | Consumes the RSA CSV output for campaign builds |

## Repo structure

```
ad-creative/
├── SKILL.md
├── references/
│   ├── hook-patterns.md                # 10 hook patterns with examples
│   ├── platform-character-limits.md    # current limits across platforms
│   ├── static-brief-template.md        # for Nano Banana 2 MCP consumption
│   └── ugc-script-template.md          # bracket-format script structure
├── templates/
│   ├── rsa-output.csv                  # Google Ads Editor bulk upload
│   └── meta-bulk-output.csv            # Meta Bulk Import format
└── README.md
```

## License

MIT — see [LICENSE](LICENSE).

Built by [Nick Christensen](https://github.com/nickyc1).
