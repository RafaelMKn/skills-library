# impeccable

> Use when the user wants to design, redesign, shape, critique, audit, polish, clarify, distill, harden, optimize, adapt, animate, colorize, extract, or otherwise improve a frontend interface. Covers websites, landing pages, dashboards, product UI, app shells, components, forms, settings, onboarding, and empty states. Handles UX review, visual hierarchy, information architecture, cognitive load, accessibility, performance, responsive behavior, theming, anti-patterns, typography, fonts, spacing, layout, alignment, color, motion, micro-interactions, UX copy, error states, edge cases, i18n, and reusable design systems or tokens. Also use for bland designs that need to become bolder or more delightful, loud designs that should become quieter, live browser iteration on UI elements, or ambitious visual effects that should feel technically extraordinary. Not for backend-only or non-UI tasks.

## 📖 Visão Geral

Esta skill fornece diretrizes, padrões e instruções especializadas para **impeccable**.


## 📁 Estrutura de Arquivos

- [SKILL.md](SKILL.md)
- [agents\impeccable_asset_producer.toml](agents\impeccable_asset_producer.toml)
- [agents\impeccable_documenter.toml](agents\impeccable_documenter.toml)
- [agents\impeccable_finish_reviewer.toml](agents\impeccable_finish_reviewer.toml)
- [agents\impeccable_manual_edit_applier.toml](agents\impeccable_manual_edit_applier.toml)
- [agents\openai.yaml](agents\openai.yaml)
- [reference\adapt.md](reference\adapt.md)
- [reference\adapt.native.md](reference\adapt.native.md)
- [reference\android.md](reference\android.md)
- [reference\animate.md](reference\animate.md)
- [reference\audit.md](reference\audit.md)
- [reference\audit.native.md](reference\audit.native.md)
- [reference\bolder.md](reference\bolder.md)
- [reference\clarify.md](reference\clarify.md)
- [reference\colorize.md](reference\colorize.md)
- [reference\craft-floor.md](reference\craft-floor.md)
- [reference\craft.md](reference\craft.md)
- [reference\critique.md](reference\critique.md)
- [reference\degraded\asset-producer.md](reference\degraded\asset-producer.md)
- [reference\degraded\documenter.md](reference\degraded\documenter.md)
- [reference\degraded\finish-reviewer.md](reference\degraded\finish-reviewer.md)
- [reference\degraded\manual-edit-applier.md](reference\degraded\manual-edit-applier.md)
- [reference\delight.md](reference\delight.md)
- [reference\distill.md](reference\distill.md)
- [reference\doctor.md](reference\doctor.md)
- [reference\document.md](reference\document.md)
- [reference\extract.md](reference\extract.md)
- [reference\harden.md](reference\harden.md)
- [reference\hooks.md](reference\hooks.md)
- [reference\init.md](reference\init.md)
- [reference\ios.md](reference\ios.md)
- [reference\layout.md](reference\layout.md)
- [reference\live-setup.md](reference\live-setup.md)
- [reference\live.md](reference\live.md)
- [reference\new-work.md](reference\new-work.md)
- [reference\onboard.md](reference\onboard.md)
- [reference\operate.md](reference\operate.md)
- [reference\optimize.md](reference\optimize.md)
- [reference\overdrive.md](reference\overdrive.md)
- [reference\polish.md](reference\polish.md)
- [reference\quieter.md](reference\quieter.md)
- [reference\routing.md](reference\routing.md)
- [reference\shape.md](reference\shape.md)
- [reference\typeset.md](reference\typeset.md)
- [reference\visualize.md](reference\visualize.md)
- [scripts\command-metadata.json](scripts\command-metadata.json)
- [scripts\concept-seed.mjs](scripts\concept-seed.mjs)
- [scripts\context-signals.mjs](scripts\context-signals.mjs)
- [scripts\context.mjs](scripts\context.mjs)
- [scripts\critique-storage.mjs](scripts\critique-storage.mjs)
- [scripts\detect-csp.mjs](scripts\detect-csp.mjs)
- [scripts\detect.mjs](scripts\detect.mjs)
- [scripts\detector\browser\injected\index.mjs](scripts\detector\browser\injected\index.mjs)
- [scripts\detector\cli\main.mjs](scripts\detector\cli\main.mjs)
- [scripts\detector\design-system.mjs](scripts\detector\design-system.mjs)
- [scripts\detector\detect-antipatterns-browser.js](scripts\detector\detect-antipatterns-browser.js)
- [scripts\detector\detect-antipatterns.mjs](scripts\detector\detect-antipatterns.mjs)
- [scripts\detector\engines\browser\detect-url.mjs](scripts\detector\engines\browser\detect-url.mjs)
- [scripts\detector\engines\regex\detect-text.mjs](scripts\detector\engines\regex\detect-text.mjs)
- [scripts\detector\engines\static-html\css-cascade.mjs](scripts\detector\engines\static-html\css-cascade.mjs)
- [scripts\detector\engines\static-html\detect-html.mjs](scripts\detector\engines\static-html\detect-html.mjs)
- [scripts\detector\engines\visual\screenshot-contrast.mjs](scripts\detector\engines\visual\screenshot-contrast.mjs)
- [scripts\detector\findings.mjs](scripts\detector\findings.mjs)
- [scripts\detector\node\file-system.mjs](scripts\detector\node\file-system.mjs)
- [scripts\detector\profile\profiler.mjs](scripts\detector\profile\profiler.mjs)
- [scripts\detector\registry\antipatterns.mjs](scripts\detector\registry\antipatterns.mjs)
- [scripts\detector\rules\checks.mjs](scripts\detector\rules\checks.mjs)
- [scripts\detector\shared\color.mjs](scripts\detector\shared\color.mjs)
- [scripts\detector\shared\constants.mjs](scripts\detector\shared\constants.mjs)
- [scripts\detector\shared\fonts.mjs](scripts\detector\shared\fonts.mjs)
- [scripts\detector\shared\inline-ignores.mjs](scripts\detector\shared\inline-ignores.mjs)
- [scripts\detector\shared\page.mjs](scripts\detector\shared\page.mjs)
- [scripts\doctor.mjs](scripts\doctor.mjs)
- [scripts\embed-prompt.mjs](scripts\embed-prompt.mjs)
- [scripts\generate-image.mjs](scripts\generate-image.mjs)
- [scripts\hook-admin.mjs](scripts\hook-admin.mjs)
- [scripts\hook-before-edit.mjs](scripts\hook-before-edit.mjs)
- [scripts\hook-lib.mjs](scripts\hook-lib.mjs)
- [scripts\hook.mjs](scripts\hook.mjs)
- [scripts\lib\artifact-schema.mjs](scripts\lib\artifact-schema.mjs)
- [scripts\lib\composition-catalog.mjs](scripts\lib\composition-catalog.mjs)
- [scripts\lib\concept-catalog.mjs](scripts\lib\concept-catalog.mjs)
- [scripts\lib\design-parser.mjs](scripts\lib\design-parser.mjs)
- [scripts\lib\impeccable-config.mjs](scripts\lib\impeccable-config.mjs)
- [scripts\lib\impeccable-paths.mjs](scripts\lib\impeccable-paths.mjs)
- [scripts\lib\is-generated.mjs](scripts\lib\is-generated.mjs)
- [scripts\lib\open-system-browser.mjs](scripts\lib\open-system-browser.mjs)
- [scripts\lib\provider.mjs](scripts\lib\provider.mjs)
- [scripts\lib\roll-selection.mjs](scripts\lib\roll-selection.mjs)
- [scripts\lib\staleness-deep.mjs](scripts\lib\staleness-deep.mjs)
- [scripts\lib\staleness-notice.mjs](scripts\lib\staleness-notice.mjs)
- [scripts\lib\staleness.mjs](scripts\lib\staleness.mjs)
- [scripts\lib\surface-briefs.mjs](scripts\lib\surface-briefs.mjs)
- [scripts\lib\target-args.mjs](scripts\lib\target-args.mjs)
- [scripts\lib\target-slug.mjs](scripts\lib\target-slug.mjs)
- [scripts\lib\template-extensions.mjs](scripts\lib\template-extensions.mjs)
- [scripts\live-accept.mjs](scripts\live-accept.mjs)
- [scripts\live-browser-dom.js](scripts\live-browser-dom.js)
- [scripts\live-browser-session.js](scripts\live-browser-session.js)
- [scripts\live-browser.js](scripts\live-browser.js)
- [scripts\live-commit-manual-edits.mjs](scripts\live-commit-manual-edits.mjs)
- [scripts\live-complete.mjs](scripts\live-complete.mjs)
- [scripts\live-copy-edit-agent.mjs](scripts\live-copy-edit-agent.mjs)
- [scripts\live-discard-manual-edits.mjs](scripts\live-discard-manual-edits.mjs)
- [scripts\live-inject.mjs](scripts\live-inject.mjs)
- [scripts\live-insert.mjs](scripts\live-insert.mjs)
- [scripts\live-manual-edit-evidence.mjs](scripts\live-manual-edit-evidence.mjs)
- [scripts\live-poll.mjs](scripts\live-poll.mjs)
- [scripts\live-resume.mjs](scripts\live-resume.mjs)
- [scripts\live-server.mjs](scripts\live-server.mjs)
- [scripts\live-status.mjs](scripts\live-status.mjs)
- [scripts\live-target.mjs](scripts\live-target.mjs)
- [scripts\live-wrap.mjs](scripts\live-wrap.mjs)
- [scripts\live.mjs](scripts\live.mjs)
- [scripts\live\accept-css.mjs](scripts\live\accept-css.mjs)
- [scripts\live\accept-verify.mjs](scripts\live\accept-verify.mjs)
- [scripts\live\browser-script-parts.mjs](scripts\live\browser-script-parts.mjs)
- [scripts\live\completion.mjs](scripts\live\completion.mjs)
- [scripts\live\event-validation.mjs](scripts\live\event-validation.mjs)
- [scripts\live\frameworks\astro.mjs](scripts\live\frameworks\astro.mjs)
- [scripts\live\frameworks\detect-utils.mjs](scripts\live\frameworks\detect-utils.mjs)
- [scripts\live\frameworks\index.mjs](scripts\live\frameworks\index.mjs)
- [scripts\live\frameworks\journal.mjs](scripts\live\frameworks\journal.mjs)
- [scripts\live\frameworks\nextjs.mjs](scripts\live\frameworks\nextjs.mjs)
- [scripts\live\frameworks\nuxt.mjs](scripts\live\frameworks\nuxt.mjs)
- [scripts\live\frameworks\script-src.mjs](scripts\live\frameworks\script-src.mjs)
- [scripts\live\frameworks\static-html.mjs](scripts\live\frameworks\static-html.mjs)
- [scripts\live\frameworks\sveltekit.mjs](scripts\live\frameworks\sveltekit.mjs)
- [scripts\live\frameworks\tag-strategy.mjs](scripts\live\frameworks\tag-strategy.mjs)
- [scripts\live\frameworks\tanstack-start.mjs](scripts\live\frameworks\tanstack-start.mjs)
- [scripts\live\frameworks\vite-generic.mjs](scripts\live\frameworks\vite-generic.mjs)
- [scripts\live\generation-preflight.mjs](scripts\live\generation-preflight.mjs)
- [scripts\live\insert-ui.mjs](scripts\live\insert-ui.mjs)
- [scripts\live\instructions.mjs](scripts\live\instructions.mjs)
- [scripts\live\manual-apply.mjs](scripts\live\manual-apply.mjs)
- [scripts\live\manual-edit-routes.mjs](scripts\live\manual-edit-routes.mjs)
- [scripts\live\manual-edits-buffer.mjs](scripts\live\manual-edits-buffer.mjs)
- [scripts\live\poll-lanes.mjs](scripts\live\poll-lanes.mjs)
- [scripts\live\roots.mjs](scripts\live\roots.mjs)
- [scripts\live\session-store.mjs](scripts\live\session-store.mjs)
- [scripts\live\source-lock.mjs](scripts\live\source-lock.mjs)
- [scripts\live\source-search.mjs](scripts\live\source-search.mjs)
- [scripts\live\svelte-ast.mjs](scripts\live\svelte-ast.mjs)
- [scripts\live\svelte-component.mjs](scripts\live\svelte-component.mjs)
- [scripts\live\sveltekit-adapter.mjs](scripts\live\sveltekit-adapter.mjs)
- [scripts\live\tanstack-adapter.mjs](scripts\live\tanstack-adapter.mjs)
- [scripts\live\ui-surfaces.mjs](scripts\live\ui-surfaces.mjs)
- [scripts\live\vocabulary.mjs](scripts\live\vocabulary.mjs)
- [scripts\modern-screenshot.umd.js](scripts\modern-screenshot.umd.js)
- [scripts\palette.mjs](scripts\palette.mjs)
- [scripts\pin.mjs](scripts\pin.mjs)
- [scripts\serve-question.mjs](scripts\serve-question.mjs)
- [scripts\surface-brief.mjs](scripts\surface-brief.mjs)

---

## 🛠️ Conteúdo da Skill

This skill gives you the tools and permission to create design that earns to be called out-of-distribution craft: Whereas before, your design work would have been safe, timid and measured, you now approach every design task as a award-winning design director with impeccable understanding for what makes exceptional design work: production-grade code, peak creativity, a clear POV, deep understanding of the needs of the client and users, and exceptional craft.

Core principles:
- Go all out. No hedging, no shortcuts. The deliverable must be complete (except assets the user must provide).
- Dream big and bold. Distinct, beautiful, outstanding and highly inspiring work.
- Verify in bounded passes, not a loop, and the ceiling covers the whole cycle: screenshots, defect scans, micro-edits, and rebuilds alike. Build fully, inspect once with a batched round (desktop and mobile together on the web; the shipped device classes on a native platform), fix everything it shows in one batch, confirm with at most one more round, and stop polishing. Open-ended self-QA burns the user's money doing worse what the finish handoffs do better.

## Setup

1. Run `node <skill-base-dir>/scripts/context.mjs` once per session, where `<skill-base-dir>` is the loaded base directory the runtime reports for this skill; keep cwd at the user's project. That base directory resolves every `node .agents/skills/impeccable/scripts/...` command in this skill and its references, and `.agents/skills/impeccable/scripts` is the fallback only when the runtime reports no base directory. Pass a named source file or route as `--target <path>`. It loads PRODUCT.md, DESIGN.md, the matching surface brief, and native-platform guidance when applicable; follow its directives and do not rerun it.
2. Before acting, load the one playbook that owns the request: the Commands table's reference for an explicit or clearly implied sub-command, or [reference/new-work.md](reference/new-work.md) for a new surface or replacement visual world. Then inspect the target and at least one representative source of incumbent visual truth (tokens, theme, CSS, component, or asset) before editing.
3. After analysis and direction are resolved, load [reference/craft-floor.md](reference/craft-floor.md) immediately before editing UI. It carries the quality floor, the absolute bans, and the reflexes no detector catches. Do not load it for planning-only work.

## How to design

- **The brief wins.** Honor pinned aesthetics, eras, materials, fonts, and palettes even when they conflict with a saturated-pattern warning. Redirecting a clear brief toward your taste is failure.
- **Refinement preserves; redesign replaces.** Refinement keeps the incumbent identity, behavior, copy, and everything outside scope. Ask before replacing factual copy or adding claims. Redesign keeps product truth, content, function, native affordances, and constraints, but treats the old look as evidence and anti-reference; choose a replacement world in new-work and replace DESIGN.md. Never split the difference into polish on the discarded look.
- **Visual authority is evidence, not a filename.** Missing DESIGN.md alone does not make a project greenfield; new-work decides whether to preserve, expand, or replace the incumbent world.

## Modes

The mode names what the visitor's success looks like on this surface.

- **Persuade:** the visitor decides and acts; design is the product. Landing pages, marketing, campaigns, pricing. Earn attention and action. Ship real imagery when the brief needs it; follow the committed world, not category habit.
- **Operate:** the visitor completes a task. App UI, dashboards, editors, admin, settings, tools. Scanability, consistency, native expectations, and the real usage scene outrank expression. Brand lives in precise details.
- **Read:** the visitor understands something. Docs, articles, guides, help, changelogs. Structure for comprehension, then make the reading experience worth staying in.
- **Experience:** the visitor is inside the work itself. Portfolios, galleries, showcases. Let the artifact lead from the first viewport; the interface recedes.

Choose the mode from the requested surface, not the product, and persist it only in that surface brief. A tool's landing page is still Persuade; a fashion house's documentation is still Read; a docs index is Read, not Persuade. See [new-work.md](reference/new-work.md) for new surfaces and [operate.md](reference/operate.md) for deeper Operate/Read guidance.

## Commands

| Command | Category | Description | Reference |
|---|---|---|---|
| `craft [feature]` | Build | Deprecated alias for an ordinary new-work request | [reference/craft.md](reference/craft.md) |
| `shape [feature]` | Build | Plan UX/UI before writing code | [reference/shape.md](reference/shape.md) |
| `init` | Build | Capture durable product context in PRODUCT.md | [reference/init.md](reference/init.md) |
| `document` | Build | Generate DESIGN.md from existing project code | [reference/document.md](reference/document.md) |
| `extract [target]` | Build | Pull reusable tokens and components into design system | [reference/extract.md](reference/extract.md) |
| `critique [target]` | Evaluate | UX design review with heuristic scoring | [reference/critique.md](reference/critique.md) |
| `audit [target]` | Evaluate | Technical quality checks (a11y, perf, responsive) | [reference/audit.md](reference/audit.md) · native: [reference/audit.native.md](reference/audit.native.md) |
| `polish [target]` | Refine | Final quality pass before shipping | [reference/polish.md](reference/polish.md) |
| `bolder [target]` | Refine | Amplify safe or bland designs | [reference/bolder.md](reference/bolder.md) |
| `quieter [target]` | Refine | Tone down aggressive or overstimulating designs | [reference/quieter.md](reference/quieter.md) |
| `distill [target]` | Refine | Strip to essence, remove complexity | [reference/distill.md](reference/distill.md) |
| `harden [target]` | Refine | Production-ready: errors, i18n, edge cases | [reference/harden.md](reference/harden.md) |
| `onboard [target]` | Refine | Design first-run flows, empty states, activation | [reference/onboard.md](reference/onboard.md) |
| `animate [target]` | Enhance | Add purposeful animations and motion | [reference/animate.md](reference/animate.md) |
| `colorize [target]` | Enhance | Add strategic color to monochromatic UIs | [reference/colorize.md](reference/colorize.md) |
| `typeset [target]` | Enhance | Improve typography hierarchy and fonts | [reference/typeset.md](reference/typeset.md) |
| `layout [target]` | Enhance | Fix spacing, rhythm, and visual hierarchy | [reference/layout.md](reference/layout.md) |
| `delight [target]` | Enhance | Add personality and memorable touches | [reference/delight.md](reference/delight.md) |
| `overdrive [target]` | Enhance | Push past conventional limits | [reference/overdrive.md](reference/overdrive.md) |
| `clarify [target]` | Fix | Improve UX copy, labels, and error messages | [reference/clarify.md](reference/clarify.md) |
| `adapt [target]` | Fix | Adapt for different devices and screen sizes | [reference/adapt.md](reference/adapt.md) · native: [reference/adapt.native.md](reference/adapt.native.md) |
| `optimize [target]` | Fix | Diagnose and fix UI performance | [reference/optimize.md](reference/optimize.md) |
| `live` | Iterate | Visual variant mode: pick elements in the browser, generate alternatives | [reference/live.md](reference/live.md) |

Routing:

- **No argument:** read [routing.md](reference/routing.md) and present its context-aware menu; never auto-run a command.
- **Explicit or clearly implied command:** load its reference (native variant on native platforms) and follow it. Ask once if two commands fit.
- **Otherwise:** treat the request as general design work. Missing PRODUCT.md routes a new surface or replacement world through init, then new-work; a narrow refinement of existing code proceeds on the incumbent implementation as context.mjs directs, offering init afterward rather than blocking on it.
- `teach` aliases `init`. `craft` is a deprecated alias for ordinary new-work and adds nothing. `shape` owns task discovery, then enters new-work only for visual-world and surface-concept decisions.

After init writes PRODUCT.md, resume without rerunning `context.mjs`; init loads the native platform reference itself when the platform it recorded is `ios`, `android`, or `adaptive`.

**Pin / Unpin:** `node .agents/skills/impeccable/scripts/pin.mjs <pin|unpin> <command>` creates or removes a standalone `$<command>` shortcut. Report the script's result concisely; relay stderr verbatim on error.

**Hooks:** `$impeccable hooks <on|off|status|ignore-rule|ignore-file|ignore-value|reset>` manages the design detector hook for this project (auto-runs the detector after UI file edits and surfaces findings). Load [reference/hooks.md](reference/hooks.md) when the user invokes it with any argument.

**Doctor:** `$impeccable doctor` reports and repairs drift between this project's Impeccable artifacts (PRODUCT.md, DESIGN.md and its sidecar, config, surface briefs, the hook) and what this version reads. Load [reference/doctor.md](reference/doctor.md) when the user invokes it, or when they ask what is out of date, stale, or needs refreshing. A `CONTEXT_STALE` directive in Setup's output is the cheap subset of the same report; act on it there per its own instructions rather than running doctor unasked.

**Never repair drift as a side effect of a design task.** A `CONTEXT_STALE` finding is reported, not acted on, unless the user asks. The one exception is a finding marked `auto`, which the next write to that file performs anyway.

---
*Parte da [Skills Library](../../README.md)*
