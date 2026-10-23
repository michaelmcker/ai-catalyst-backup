# Corrected hero contract — 23 October 2026

This supersedes the preceding hero-refinement notes. The first pass incorrectly made Solutions stacked and left a fading paper field around the portrait artwork.

## Two primitives

- `page-hero--side`: Solutions, Company, Briefing and Training. Desktop and tablet put the complete copy on the left and the subject on the right, inside one shared full-width patterned field. Phone layouts show the complete image first and copy immediately below.
- `page-hero--stacked`: Full Commerce MMM, Commerce Command Centre, Creator Intelligence and Agentic Consumer Intelligence. Desktop and tablet use a headline/support row followed immediately by the full-width landscape. Phone layouts retain the image-first order. No spacer, image mask or image-edge feather separates the two regions.

The field reaches all hero edges. Its former bottom fade is disabled for subpages. Light source paper around close-up subjects reveals the common pattern instead of painting a white halo. The homepage keeps its existing rendering behavior. Header offsets are exactly 81px on desktop/tablet and 73px on phones, including pages with the `art-opening` wrapper.

## Verification

- `before.json` and its three screenshots reproduce the incorrect Solutions layout and blank bottom bands. `after.json` and its screenshots show the correction.
- Run `python3 scripts/check-hero-pattern.py docs/hero-correction-2026-10-23 before` to observe the regression, and repeat with `after` to verify the corrected geometry and visible blue pattern at the top and bottom edges.
- `geometry.json`: all eight subpages at 1440, 1024, 768, 390 and 320px. Forty checks pass for the intended primitive, image/copy join, header join, full hero field and horizontal overflow.
- Reduced motion retains artwork and the common field. The relocated film button opens the dialog and its Close control works.
- All original page text and forty media files are unchanged. All local HTML references resolve; all fifteen JavaScript files pass syntax checking.

The static deployment source is `current-site/`, mirrored by matching root files. The archived Lovable export is unchanged. These edits are local and uncommitted; Cloudflare deployment metadata records a dirty working tree against the original backup commit.

## Verified publication

Production deployment `1bf159c3-aaaf-42bf-8874-b9e180aff86a` succeeded in Randy's `ai-catalyst` Pages project. All seven specifically requested live routes were checked. `live.json` and the three `live-*.png` screenshots pass the pattern/side-layout check. `live-stacked.json` confirms the four landscape routes have the stacked primitive, zero header gap, zero copy/image gap and zero horizontal overflow at 1440px.
