# Command Centre Media Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore the original engine graphics and introduce the overall Command Centre film beside its introduction, across all four language editions.

**Architecture:** Edit the multilingual source template, reuse the existing click-to-play film component, and regenerate the published mirrors. Restore retained SVG/canvas figures rather than recreating artwork. Scope layout changes to the Command Centre introduction.

**Tech Stack:** Static HTML/CSS, SVG, canvas, existing service-films JavaScript, Python localization/build checks.

---

## Verified sources and scope

Repository: `/Users/michaelmckerracher/portfolio-publishing/work/ai-catalyst/ai-catalyst-backup`.

The public page is `https://aicatalyst.biz/platform#command-centre`. Its original graphics remain in both source and live DOM, marked `hidden` and `aria-hidden="true"`. The October 30 engine-film update retained them behind the replacement film previews.

| Engine | Original retained graphic | Proposed treatment |
| --- | --- | --- |
| Agentic Live Selling | SVG `#chat-scene`, conversation and product choices | Restore original figure |
| Creator Economy Intelligence | Canvas `#signals`, creator signals | Restore original figure |
| Full Commerce MMM | Canvas `#allocation`, allocation model | Restore original figure |

The homepage's “Creator intelligence” and platform's “Creator economy intelligence” refer to the same creator engine; there is no fourth missing graphic. Preserve the existing names in this change.

The sent email to Randy, subject `Re: Video links`, November 19, identifies the overall **Agentic Commerce Command Centre** film:

- YouTube: https://youtu.be/NkQtLriHVbA
- Source video in Drive: https://drive.google.com/file/d/12WX_xrUTd4495jjP0OD9PSyLyY_M06fv/view

Use that YouTube ID, not the separate MMM, Agentic Live Selling or Coffee Chat films. Verify public playback before implementation release; the email establishes identity, not playback availability.

## Exact placement and responsive composition

Keep the existing opening hero unchanged. Inside `#command-centre`, replace the full-width heading/intro arrangement with a two-column introduction:

```
Desktop English/French (>=1000px)
| Heading + existing introductory copy (45%) | Overview film (55%) |
| Existing diagram explanation and full-width diagram              |
| Existing GTM Decision Engine and three engine rows                |

Phone/tablet (<1000px)
| Overview film                         |
| Heading                               |
| Existing introductory copy            |
| Diagram explanation and diagram       |
| Existing engine content               |
```

Use a 32–48px desktop gap and a scoped heading scale around 42–64px so the heading fits its column. Confirm the actual breakpoint against French wrapping and tablet screenshots. Preserve the current white/navy visual language and existing body copy. Keep the second explanatory paragraph with the diagram below the introduction.

Arabic desktop places copy on the right and video on the left through logical layout. Mobile remains video-first. Never mirror the video, its poster, controls or readable graphics. Preserve a meaningful heading structure and accessible player label despite visual ordering.

The film is responsive 16:9, click-to-play and never autoplaying. Use an actual frame or official thumbnail as the poster, optimized locally with intrinsic dimensions. Reuse existing focus, play and loading behavior; verify duration before showing a time badge, otherwise omit it.

## File map

- `templates/i18n/platform.html`: source introduction, film and restored engine figures.
- `platform-command.css`, mirrored into `current-site/platform-command.css`: scoped responsive introduction layout.
- `engine-films.css`, mirrored counterpart: inspect whether any platform dependency remains; retain styles still required elsewhere.
- `service-films.css` and `service-films.js`: reuse the existing component; modify only if an actual compatibility issue requires it.
- `restored-platform-motion.js`, mirrored counterpart: existing graphic renderers; preserve unless visibility/resize testing demonstrates a defect.
- `assets/video-posters/command-centre-overview-20261119.jpg`, mirror: new source-derived poster if needed.
- `content/i18n/{en,fr-CA,fr-FR,ar}.json`, source manifest and review record: translated film labels and updated extraction.
- `tests/localization/command-centre-media.py`: focused structural regression.
- `AGENTS.md`: replace the October 30 instruction requiring platform engine-film previews with the approved graphics/overview-film contract.
- Generated root and `current-site/` English and locale platform pages: build outputs, not independent editing targets.

## Task 1: Establish baseline and media readiness

- [ ] Read applicable repository instructions and working notes; check Git status and preserve unrelated untracked assets.
- [ ] Run required existing checks and record pre-existing failures separately. If running enclosing `npm test`, distinguish its portfolio failures from this nested static site.
- [ ] Open the exact YouTube film and confirm playback, title and suitability for embedding. Capture an accurate poster; do not change Drive permissions.
- [ ] Save before screenshots at desktop and phone widths for English and Arabic.

## Task 2: Restore engine artwork

- [ ] Add a focused structural check asserting all three original graphic IDs are present in visible figures and that platform engine rows contain no inline film previews. Run it and confirm it fails against the current state.
- [ ] Remove `hidden` and the inherited `aria-hidden="true"` from the retained graphic figures in the source template. Remove the replacement film figures from those three platform rows.
- [ ] Retain accessible graphic descriptions and existing animation hooks. Ensure `.engine-media` still lays out each graphic correctly in ordinary and reversed rows.
- [ ] Confirm nonzero canvas sizing, rendered canvas content and visible SVG after normal loading, resizing and reduced-motion loading.

## Task 3: Add the overview film

- [ ] Extend the check to require exactly one overview film with ID `NkQtLriHVbA` inside the Command Centre introduction, a valid poster, and the existing heading/diagram IDs.
- [ ] Group the heading and introductory paragraph as the copy column; add the existing service-film component as its sibling. Keep diagram explanation and diagram below.
- [ ] Add scoped grid styles, mobile visual ordering and Arabic desktop placement. Avoid changing global heading scales or other service pages.
- [ ] Verify keyboard activation, visible focus, iframe loading only after play and responsive aspect ratio. Verify no autoplay or horizontal overflow.

## Task 4: Localize, regenerate and document

- [ ] Run `python3 scripts/refresh-localization-source.py`; translate affected labels into Quebec French, French and Arabic, retaining product terminology and unchanged factual claims.
- [ ] Complete editorial review and then run `python3 scripts/build-localized-site.py --record-review`. Do not use review recording to bypass incomplete translations.
- [ ] Update `AGENTS.md`: the platform uses original graphics in all three engine rows and one overall Command Centre film in its introduction; dedicated service-page films and homepage graphics/video links remain intact. Require all four editions and selective Arabic layout handling.
- [ ] Check generated root/current-site mirror parity and review the diff for unrelated changes.

## Task 5: Verify and release after implementation is authorized

- [ ] Run `python3 tests/localization/command-centre-media.py`, `python3 tests/localization/check.py`, `python3 scripts/build-localized-site.py --check`, `python3 scripts/check-public-site.py`, and existing discovery checks. Run any additional repository-required checks relevant to changed files.
- [ ] Review English at 1440, 1024, 768, 390 and 320px, plus French editions and Arabic at desktop/phone widths. Confirm video-first stacking, readable headings, graphic visibility, canvas paint and no overflow.
- [ ] Confirm the dedicated MMM and Agentic Live Selling pages retain their films and the homepage retains its original three graphics and video links.
- [ ] Confirm analytics, HopShop, navigation, canonical/hreflang and discovery output remain intact.
- [ ] Publish through the established feature-branch/Cloudflare path only after implementation authorization. Verify the live platform in all four locales and actual film playback; report deployment and live verification separately.

## Planning outcome

This document authorizes no implementation or deployment by itself. No production source was changed while preparing this plan.
