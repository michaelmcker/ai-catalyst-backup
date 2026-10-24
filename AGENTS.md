# AI Catalyst website guidance

- Do not use eyebrows except for the homepage engine labels Michael explicitly requested on 30 September: Engine 1 for Creator Intelligence, Engine 2 for Consumer Intelligence, Engine 3 for Full Commerce MMM. Other small category captions above headings remain excluded.
- Keep partner attribution within meaningful body copy rather than using it as an eyebrow.
- Lead the engagement message with “We start with what matters to your business.”
- Preserve the approved visual assets and restrained dithered motion.

## Artwork and composition rules, updated 3 October 2026

- Exact human selections in `review/artwork-decisions-20261003.json` govern asset eligibility. Strongly rejected files and their visual directions must not be reused. Preserve the chosen source files and save adaptations separately.
- Use coastal cavalry, four riders approaching, river approach and cavalry wide as the main pool for scenic stacked heroes. Tournament is another eligible wide scene. The homepage's current sword-and-copy composition remains the reference unless Michael explicitly changes it.
- The Command Centre and all three engine pages use scenic openings spanning the full section width. Images have no side padding or inset card frame. On phones, images come first, then copy. On wider screens alternate image-first and text-first compositions deliberately. Only copy uses reading gutters. Supporting Z-pattern sections put the image first on phones. Close-ups, helmets and kneeling figures use side-by-side supporting placements; do not stretch them into scenic hero slots.
- Artwork has a blue, modestly halftoned base plus a controlled static dither shader. The moving dither field belongs in the hero and first-section zone. Body and footer artwork stay static. Detailed wide scenes need stronger suppression; close-ups need finer print; operator photos preserve identity.
- Keep dot size consistent in screen pixels. Full-width scenic panels have clean rectangular cuts and no edge feathering, including in the base image. Close-up cutouts retain feathering so they blend with the page. Avoid halos, dark rings and oversized empty image stages.
- Retain period horse costume, armour and natural adult proportions. Reduce fine rendering detail without removing equipment or changing anatomy. New action knights wear helmets; real historical painting figures preserve their distinct appearances, clothing and gestures.
- Adapt Cloister 1, 2 and 3 from their actual source compositions. Carpaccio's ambassadors and Piombo's four distinct figures remain historical references. The Arthurian painting follows its actual central-tree and foreground composition with simplified people and garments.
- Every V3 footer uses the retained bridge-halftone image and the same shared shell. Do not repeat it as body decoration on the same page. The selected map stays contained with its full dark outline and dotted border.

### Artwork refinement after the selected-scene preview
- Wide scenes retain continuous blue modeled shading. Additional dithering is a visible, fine tonal print finish, never a near-binary replacement that makes the image read like a retro game. Keep the homepage's existing finish intact.
- Stacked openings use clean rectangular cuts. Latest refinement: remove hard horizontal cuts; they were rejected as too literal. Fine vertical print bands can blend into the artwork, with heavier dithering within that area. No decorative linework below images. Hero artwork stays still while a coherent blue dither pass moves across it; reduced motion keeps the finish static. These are static overlays, not stripes baked into source images. The full-width shared navigation and opening share a white base, with the moving blue dither field across the opening. Avoid inset white cards, floating nav frames or extra background bands.
- The new Arthurian tree-left, castle-right variation is rejected. Future adaptations must adhere to the supplied painting's central tree, foreground grouping and coastal setting. Do not add generic castles or rearrange the figures into the same repeated landscape template.
- The Sauli-derived scene must be secular: retain the four distinct people and natural gestures, replacing clerical cap and vestments with historical civic clothing. Use the court paintings' painted depth and people treatment for the Arthurian adaptation as well.

- Latest mobile correction: stacked hero and body scenes become less tall as the viewport narrows. Show the full image composition at its source aspect ratio. Do not use fixed 280–340px stages or cover crops. All mobile hero images, including the homepage and close-ups, come first and show their full composition; desktop/tablet retain the sword beside copy with a much smaller gap below the nav.
- For figurative painting adaptations, simplify the people in the base artwork: broad modeled faces and garment folds, restrained hair and hand detail, no engraved armour or intricate brocade. The reclining king and clothing must follow the lower-fidelity supplied painting. Do not use heavy dithering as a substitute for reducing source detail.

- Tighten image-first openings: no nav-to-art gap, use the source aspect ratio rather than square letterboxing, and keep roughly 18px between art and mobile hero copy. Preserve the entire subject while removing unused image-stage space.

### Latest motion and composition refinement
- How We Work, Company, Briefing and Training use text left/image right on desktop and tablet, with a continuous patterned field around the subject. Below 701px, retain the complete source image first and copy immediately below.
- Keep all dither dot positions and thresholds static. Animate only a slow, low-amplitude blue tonal pass, weighted towards brighter, low-detail areas using local luminance and edge contrast. Protect figures, armour and detailed architecture. No animated binary dot thresholds or pointer-driven changes in dot scale. Reduced motion freezes the artwork and field.
- Remove vertical line overlays and dedicated vertical dither strips throughout V3. Michael rejected them. Preserve the fine print treatment without decorative image slicing.
- Map routes use discreet, shallow asymmetric curves; one slow, small traveller per route fades before reaching city markers. Preserve the contained map and current background.
- Command Centre “See the signals. Choose the next move.” is white knockout type directly on a shallower full-width image banner.
- For selected future stacked artwork, explore simplified background planes with stronger separation from the foreground. Use the existing blue palette and consistent print texture; this is a direction to trial selectively, not approval to recolour the whole image library.

## Current production contract — 23 October 2026

- Deploy only `current-site/` to Randy's Cloudflare Pages project `ai-catalyst`: https://ai-catalyst-9l3.pages.dev/. Mirror changed public files at the repository root. `lovable-source/` and the October 22 backup records are historical archives.
- `hero-layout.css` defines two primitives. `page-hero--side` is Solutions, Company, Briefing and Training. `page-hero--stacked` is Full Commerce MMM, Commerce Command Centre, Creator Intelligence and Agentic Consumer Intelligence. On wide screens the stacked primitive has headline left, support right and a flush landscape below. Do not convert Solutions into that primitive.
- The portrait field must remain patterned to every edge without white halos or a bottom fade. The stacked artwork has no spacer, mask or feathered strip between copy and image. Headers join the hero at 81px desktop/tablet and 73px mobile.
- Public contact is `randy@aicatalyst.biz`, `416-270-0132`, Toronto, Canada. Use mailto/tel links. Remove all LinkedIn contact and profile links, including the founder and advisors, and all Catalyst Retail Solutions references from the public site. A mailto link does not establish mailbox delivery.
- Every expanded menu includes `Training and adoption` linked to `training.html`, immediately after `How We Work`.
- Run `python3 scripts/check-public-site.py`, JavaScript syntax checks and rendered desktop/mobile checks after changes. The deployed static snapshot has no npm test script; the archived Lovable app and enclosing portfolio are separate projects.
- Pattern/hero correction evidence and the rendered pixel regression are documented in `docs/hero-correction-2026-10-23/README.md`.

### Mobile and performance correction — 23 October 2026

- The latest user direction supersedes the earlier image-first mobile rule for close-up heroes. Home, Company, How We Work, Briefing and Training keep text left and a smaller image right on phones. The four panoramic heroes retain their own image-first mobile layout and flush image/copy joins.
- `hero-layout.css` is loaded by Home as well as all subpages. Mobile close-up artwork occupies 40% of the hero; its copy occupies the remaining 60%, with contained text and no floated exclusion shape. Desktop subpage artwork is contained in the right 52% of the shared field.
- Keep the pale, continuous hero field and subtle tonal texture. Do not restore the homepage's 90% mobile binary dither pass. Mobile halftone canvases render statically; desktop uses a slow tonal pass with fixed dot positions. Enhancement must not fade the source image away while the canvas appears.
- Preserve original image masters. `scripts/build-image-variants.py` uses cwebp to create fingerprinted delivery variants under `current-site/images/optimized/`; HTML uses responsive srcset/sizes. Mirrors at the repository root must remain in sync. Never serve the multi-megabyte masters as the initial hero resource.
- SVG product images use `site-assets.js` because SVG image elements do not support native lazy loading. Hydrate them near their section. Optional artwork shaders and map rasterisation initialise near the viewport.
- Also run `python3 scripts/check-image-budget.py` and `python3 scripts/check-mobile-hero.py docs/mobile-performance-2026-10-23/mobile-after.json`. Browser evidence covers 1440/1024/768/390/320 widths. Verify responsive image texture replacement when resizing an already-loaded page.
- Randy confirmed that `randy@aicatalyst.biz` already receives mail. The custom domains `aicatalyst.biz` and `www.aicatalyst.biz` are attached to the Pages project; retain their DNS and mail records.
