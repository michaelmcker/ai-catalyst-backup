# Hero layout refinement — 23 October 2026

Superseded by `../hero-correction-2026-10-23/README.md`: Solutions must remain text left/image right, and all portrait heroes require an uninterrupted patterned field. The measurements below record the earlier pass, not the final contract.

The editable static deployment is `current-site/`. Matching root files are kept in sync. `lovable-source/` and the October 22 backup records remain the historical export.

## Changes

- How We Work, Commerce Command Centre, Creator Intelligence, Agentic Consumer Intelligence and Full Commerce MMM use a two-column headline/support row on desktop and tablet, followed by the original image.
- Phone openings retain the complete source image first and readable copy below.
- Company, Training and Briefing share a corrected compact image-first layout below 1001px, without the old absolute image offset or reserved subject spacer.
- Subpage artwork and paper use one hero-sized print field with a common screen origin. Scenic edges blend into that field. Homepage rendering retains its approved V1 print behavior.
- Later supporting scenes sit beside their text on desktop. The existing Command Centre knockout banner keeps its authored layout.

`current-site/hero-layout.css` owns the refinement. `current-site/halftone-rendering.js` owns print coordinates. Approved copy and all 40 source media files are unchanged.

## Verification

- Forty rendered geometry checks: all eight subpages at 1440, 1024, 768, 390 and 320px. No horizontal overflow, missing hero field, duplicate H1 or desktop headline/support collision.
- Film dialog opens and closes; main menu opens and closes.
- Reduced motion retains the complete heading, image and static print composition.
- All nine documents preserve their original text and resolve local references. All fifteen JavaScript files pass `node --check`.
- Impeccable's mechanical scan of the new stylesheet reports no findings.
- This static snapshot has no package.json or npm test suite; the archived Lovable application and enclosing portfolio project are separate projects.

`site-manifest.json` records the revised 84-file upload. `geometry-checks.json` records the rendered measurements.

## Published state

- Randy's Cloudflare account: `bbbb85e86074305e7fd5623be9406076`, Pages project `ai-catalyst`.
- Production deployment `1c880be7-c476-4594-b9b1-d7933fdae118` completed successfully on October 23, 2026.
- Live base: https://ai-catalyst-9l3.pages.dev/.
- Live MMM desktop check confirms two text columns, the shared hero field, rendered artwork and no horizontal overflow.
- Live How We Work check at 390px confirms the artwork starts exactly at the header's 73px lower edge, the shared field is present, artwork renders and horizontal overflow is zero.
- Source changes are local, uncommitted edits in this checkout; the deployment records `commit_dirty: true` against the original backup commit. GitHub and the historical Lovable source export have not been updated.
