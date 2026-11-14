# Arabic hero composition — 14 November 2026

| Page | Decision | Reason |
| --- | --- | --- |
| Home | Mirror sword-hand art; copy right, art left | Text-free directional illustration supports RTL composition. |
| Company | Mirror knight art; copy right, art left | Helmet now faces toward the copy. |
| How We Work | Mirror kneeler art; copy right, art left | Text-free fictional illustration now faces inward. |
| Training | Mirror portrait art; copy right, art left | Figure now looks toward the copy. |
| Start a conversation | Reposition/crop architecture to left desktop column; retain orientation | Preserve architectural details and separate art from copy. |
| Command Centre | Unchanged panorama | Art occupies its own full-width row below RTL copy. |
| Creator intelligence | Unchanged panorama | Full-width scene needs no directional adaptation. |
| Agentic live selling | Unchanged panorama | Full-width scene needs no directional adaptation. |
| Full Commerce MMM | Unchanged panorama | Full-width scene needs no directional adaptation. |
| Case studies index | Unchanged | No side hero requiring mirroring. |
| Analucia Sofia case study | Unchanged | Preserve content imagery and its meaning. |

At tablet widths the side-hero columns swap while each copy block keeps the full column width. Phone art and copy occupy separate full-width rows, with the obsolete English minimum copy height removed. Original source images, maps, logos, portraits in the team section, and all other locale compositions are retained.

The hero renderer composites artwork into a sibling opaque canvas, so a CSS flip alone cannot mirror the animated output. The renderer now mirrors the measured texture crop when its artwork stage has a negative horizontal scale. This preserves the shader source, paper field, pointer coordinates, original assets, and the fallback crop. Arabic pages load the versioned renderer; other locales keep their existing reference.

Validation:
- All 11 Arabic routes at 1440/1024/768/390/320: 55 browser measurements; no horizontal overflow or clipped h1 containers detected. Four selected artwork stages reported mirrored and ready; architecture and panoramas reported unmirrored.
- Desktop, tablet and phone screenshots reviewed for the changed compositions. Browser viewport tests are not physical-device certification.
- Reduced-motion Training view rendered the mirrored artwork and readable copy.
- A temporary local server omitted the renderer: the Company image fallback remained visible and mirrored on phone.
- Hosted preview and live Arabic homepage rendered the mirrored canvas; English and both French live homepages retained art-right/copy-left geometry and no mirroring.
- Localization checks, switcher tests, case-study source check, public-site check and JavaScript syntax check passed.
- Enclosing portfolio npm test suite: same two pre-existing failures before and after, 168/170 passed (resource-article completeness and v2-about-mobile).

Preview: c831282a-94d3-42ba-841d-83fff9f5e037.
Production: 882a148b-df1a-4820-9138-e1297a648626.
