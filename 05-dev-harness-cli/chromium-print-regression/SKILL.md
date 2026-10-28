---
name: chromium-print-regression
description: Use when testing CSS print with real Chromium PDFs.
---
# Real CSS print regression

- Discover Chrome/Chromium, `pdfinfo`, and `pdftotext` first. Explicitly skip if absent; never report a skipped gate as passing.
- SSR the real document/editor components inside actual page ancestors/siblings. Include global styles; map raw CSS module selectors to their exported class names when Vitest mocks module CSS. Reference local fonts with file URLs.
- Write only synthetic fixtures under configured TMPDIR/scratch. Invoke Chrome headless with an isolated user-data-dir, `--allow-file-access-from-files`, `--no-pdf-header-footer`, and `--print-to-pdf=PATH`.
- Inspect PDFs with Poppler. Assert application chrome absent, header on page one, all distinct end-to-end sentinels preserved, short document one page, long document more than two pages, and expected A4 dimensions/margins via word bounds.
- Allow dimension tolerance: Chromium rounds A4 to widths such as 594.96 pt. A 15 mm margin is about 42.52 pt. Check both minimum and maximum coordinates, including a tight lower-margin proximity assertion so oversized margins cannot silently pass.
- Font ascenders may extend outside tight heading line boxes: inspect word geometry and increase print heading line-height if needed, rather than merely trusting the article position.
- Use display:none for chrome, not visibility:hidden (which retains empty layout space). Preserve document headers instead of blanket-hiding header elements.
- Let long sections fragment, using block flow rather than nested grids where practical. Never clip content or shrink fonts to force a fixed page count.
- Establish RED before CSS changes, GREEN with real generated PDFs, then run project typecheck/lint/tests/build.
