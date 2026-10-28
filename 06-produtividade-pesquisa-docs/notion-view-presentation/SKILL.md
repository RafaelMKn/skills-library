---
name: notion-view-presentation
description: Use when slimming Notion tables without changing data.
---

# Presentation-only Notion views

Load notion and composio-apps. Validate workspace and ownership of every view's database by the authorized page before writes. Back up real view configs and source schemas privately, preserving these snapshots after writes.

Consult current `https://developers.notion.com/guides/data-apis/working-with-views.md`. Table `configuration.properties` entries accept `property_id` (ID or name), `visible`, `width`, `wrap`. Names avoid mistaken decoding of URL-encoded schema property IDs. Place chosen visible properties in desired order and explicitly hide every remaining schema property. `wrap_cells` wraps table content.

Send only `view_id` and `configuration`: omitted filters/sorts remain unchanged; do not send null accidentally. Read back exact targets and compare filter, sorts, quick_filters, type, source, parent and source schema. Check visible count/order/width. Sum of column widths excludes Notion controls and does not prove absence of rendered overflow.

Current public page update API has no full-width field. Never invent `full_width` payloads. Use only a verified authenticated UI; report local browser backend/profile blockers rather than substituting unauthenticated cloud profiles. Separate structural/API verification from real visual inspection. Never call partial table cleanup a completed full-width task.
