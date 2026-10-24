Latest refinement: the user then requested larger, wider How We Work/Training headlines and shorter subheads. Current source uses row2; see larger-headlines/README.md for the two explicit copy revisions and newer evidence. Earlier captures below retain the original longer text.

# Mobile hero row: full subheads below the artwork

The user rejected splitting supporting copy above and below an illustration.
Their chosen alternative is a headline at the left, the original artwork at the
right, then the complete supporting paragraph below that row. This release
implements that composition on Company, How We Work/Solutions and Training at
700px and below. It preserves all wording. Home, Briefing/Start a Conversation,
the four panoramic pages, tablet and desktop compositions remain unchanged.

Only `mobile-hero-row.css?v=20261023-row1` is imported by the three pages. It
uses CSS Grid, with the unchanged copy wrapper contributing its children to the
hero grid. Headline and image share row one; the full-width paragraph owns row
two, followed by the original actions. Artwork keeps its natural aspect ratio.
Copy remains above the original shared canvas layers. There is no new layout
JavaScript, float, shape exclusion, line clamp or text replacement. The rejected
mobile-subject-wrap CSS/JS files and their HTML imports were removed.

The shared renderer, paper compositor, source artwork, original interaction
scripts, contact changes and the approved Briefing checkpoint are preserved.
The previous float experiment is historical evidence under
`../safari-wrap-2026-10-23/` and is not the accepted current treatment.

## Evidence

- `candidate.json` and 12 matching screenshots cover all three pages at 320,
  390, 430 and 600 CSS pixels, DPR 3, in the in-app Chromium browser.
- `results.json`: all 12 pass exact headline/paragraph/action text equality with
  the original deployed baseline, complete per-character bounds, headline/figure
  clearance against independent source ink masks, no horizontal overflow and a
  full-width supporting paragraph at least 20px below the entire image/headline
  row. Paragraph lines have ordinary uninterrupted leading.
- `native-safari/`: 12 page-only screenshots from actual macOS Safari Responsive
  Design Mode at those widths. The image and supporting paragraph were reviewed
  visually. These are WebKit desktop rendering evidence, not physical iPhone
  captures or automated native character-mask results. Safari's desktop scrollbar
  leaves a narrower content viewport than Chromium phone emulation.
- `desktop-tablet.json`: 12 paired previous-preview/current-source controls at
  768, 1024 and 1440px for the three affected pages plus Briefing. All hero,
  headline, paragraph and artwork rectangles, plus scroll widths, match exactly
  when captured under the same browser settings.

Run `python3 scripts/check-mobile-hero-row.py candidate.json --output results.json`
from this folder with the script's actual repository-relative path, or from the
repository root using the full proof paths. The script reuses independent
approved-source dark-ink masks, not the CSS layout dimensions, for figure
clearance. Source verification remains `scripts/check-direct-vercel.py`; the
public contact/navigation/reference contract is `scripts/check-public-site.py`.
No npm test script exists in this static snapshot.

This remains a preview for the user's physical iPhone check. A screenshot and
source pass do not establish all iOS hardware/compositor behavior. Production
must not be promoted from this proof alone. Deployment metadata and live
response verification are recorded separately after publication.

## Published preview

https://90a37db4.ai-catalyst-9l3.pages.dev/ is a successful preview deployment of code commit 95cda1bf91f3b40e0f265c5eff67fe24ff9037a4, with 86 public files. The built-in Cloudflare connection published it to Randy’s existing ai-catalyst project. All seven browser-loaded HTML/CSS/renderer responses in preview/ match source exactly; the three live 390px row captures also pass the uninterrupted-paragraph checks. Production remains f87c264b-eafd-441a-ade0-d4a03d7f02e4. Physical iPhone review is pending.
