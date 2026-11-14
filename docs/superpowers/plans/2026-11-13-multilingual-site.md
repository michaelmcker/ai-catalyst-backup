# AI Catalyst multilingual site implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give every public AI Catalyst page a reviewed language edition, an accessible language switcher, and a respectful browser-language suggestion.

**Architecture:** Generate complete static localized pages at build time from an approved English snapshot, shared templates, and explicit locale content. Keep the existing English URLs, artwork, interactions, Analytics property, and HopShop placement. Each translation has its own URL, correct document language/direction, and a route map connecting equivalent pages.

**Tech Stack:** Existing static HTML/CSS/JavaScript and Python build scripts; Cloudflare Pages; locale content in UTF-8 JSON; browser-based layout and interaction checks.

---

## Proposed language scope and decision

Initial written editions:

| Edition | Document language | Route prefix | Direction |
| --- | --- | --- | --- |
| Existing English | en | existing URLs | left to right |
| Quebec French | fr-CA | /fr-ca/ | left to right |
| France/international French | fr-FR | /fr-fr/ | left to right |
| Modern Standard Arabic | ar | /ar/ | right to left |

This produces 44 public page editions from the current 11-page site: 11 existing English pages and 33 translated pages. Quebec French is a deliberate terminology and tone adaptation within the Canadian French locale; browser fr-CA is a preference signal, not proof that a visitor lives in Quebec. France French gets its own wording and typography review.

Gulf, Levantine, and Egyptian Arabic are proposed regional conversational priorities, not a claimed popularity ranking. Choose them according to Randy's actual target markets. Modern Standard Arabic is the recommended shared written edition. If regional written editions are requested, choose a specific audience/country and a native reviewer before creating distinct pages. Country codes such as ar-AE and ar-SA identify regional locales, not spoken dialects. Do not invent a single generic Levant country code or label one dialect translation as every Arabic locale. Persian, Turkish, Hebrew, and Kurdish are separate languages and are outside this initial Arabic scope unless requested.

The site’s 11 source pages are: homepage, How We Work, Training, Company, Command Centre, Creator Intelligence, Agentic Live Selling, Full Commerce MMM, Briefing, case-study index, and Analucia/Sofia detail.

## File responsibilities

All paths below are relative to the AI Catalyst repository, `ai-catalyst-backup/`, not the enclosing portfolio repository.

- `content/i18n/locales.json`: supported locale identifiers, native labels, direction and suggestion rules.
- `content/i18n/routes.json`: 11 stable page identifiers and their equivalent URLs in every edition. Keep existing English paths and use the same path suffix under each translated prefix initially; translated slugs are unnecessary for launch.
- `content/i18n/en.json`, `fr-CA.json`, `fr-FR.json`, `ar.json`: complete approved page copy and UI/accessibility strings, keyed by page and semantic field. Include metadata, image alternatives and dialogs.
- `content/i18n/glossary.json`: brand/product names, commercial terminology, approved translations and terms kept in English.
- `content/i18n/review.json`: review state, locale/page content hashes, reviewer decisions, and source revision. A source edit invalidates the corresponding translation approval.
- `templates/i18n/`: the 11 page templates extracted from the current production HTML without redesign. Preserve authored structure, classes and media. Use explicit translation slots, not global search-and-replace of English text.
- `scripts/build-localized-site.py`: deterministic generation of translated HTML and root mirrors, route links, canonicals, alternate links and sitemap. Provide `--check` to detect stale generated output and fail on missing translations or unapproved release content.
- `current-site/language-switcher.js` and root mirror: progressively enhanced menu and optional language suggestion; ordinary links work without JavaScript.
- `current-site/localization.css` and root mirror: language controls, Arabic typography and direction-aware adjustments.
- `current-site/fr-ca/`, `fr-fr/`, `ar/` and root mirrors: generated page editions. Relative image/script references must resolve to shared root assets.
- `current-site/assets/fonts/`: locally served Arabic webfont with its redistribution licence, selected after rendering the actual Arabic copy.
- `templates/case-studies-shell.html`, `scripts/build-case-studies.py`: keep case-study generation compatible; consume localized case-study content through the shared generation contract rather than maintaining two independent versions of the same localized output.
- `tests/localization/`: route/content generation, browser-language resolution, accessibility, RTL and viewport checks.
- `docs/localization/`: source inventory, terminology decisions, review evidence, preview screenshots and release manifest.

## Task 1: Freeze and inventory the production baseline

- [ ] Check status in both repositories and preserve the currently uncommitted HopShop changes. Record the current live Cloudflare release and compare its public assets with local production source before deriving templates.
- [ ] Run the AI Catalyst public-site and static-generation checks. Record enclosing portfolio `npm test` results separately; its previously observed two failures must not be mistaken for new localization regressions.
- [ ] Inventory all visible text, navigation, CTA labels, title/description/Open Graph text, image alternatives, aria labels, hidden fallback text, form labels/errors, menu Open/Close strings and modal controls across the 11 pages.
- [ ] Inventory text inside graphics, videos, captions and external widgets separately. Preserve artwork; use reviewed HTML/captions for essential translated information instead of pretending embedded English media has been translated.
- [ ] Approve the page/locale matrix and target-market choice before producing the full translation set.

## Task 2: Build the static localization foundation

- [ ] Extract templates from the baseline; initially rebuild English into a temporary directory and compare DOM structure, media references and rendered appearance with production.
- [ ] Establish semantic translation keys, a route map, and the terminology glossary. Keep AI Catalyst and official product/company names consistent. Preserve all factual claims, qualifiers, telephone numbers and destination addresses.
- [ ] Create the locale generator with strict missing-key, placeholder, internal-link and approval checks. Render localized markup directly; no browser translation service or translation API call on page load.
- [ ] Generate self-canonical URLs, reciprocal `hreflang` alternates, English `x-default`, correct `html lang`, and `dir="rtl"` on Arabic documents. Update both root and case-study discovery sitemaps without duplicate URLs.
- [ ] Keep internal navigation in the selected locale. Email and telephone links remain functional; translated email subjects are allowed, but a translated site must not imply multilingual staff availability without Randy's confirmation.
- [ ] Verify one HopShop tag and one existing Analytics script per page. Extend existing source-integrity checks only for the explicit new localization contract.

## Task 3: Switcher and language suggestion

- [ ] Put a compact language control in the shared header/menu, with native labels: English, Français (Québec), Français (France), العربية. Avoid flags as language identifiers.
- [ ] Use ordinary equivalent-page links: switching from an English service page opens its translated counterpart, not a generic homepage. Preserve a fragment only if the target exists on that edition.
- [ ] Respect the URL first. Then use a saved explicit choice, then `navigator.languages` for a suggestion. Match fr-CA to Quebec French, other supported French preferences to France French, Arabic preferences to the shared Arabic edition, and unsupported preferences to English.
- [ ] Show a small inline suggestion once; no blocking pop-up and no forced geolocation/IP redirect. Dismissing the suggestion leaves the current edition unchanged. Never override an explicitly visited localized URL.
- [ ] Store only a language preference locally with guarded storage access. The site and links continue working when storage is blocked. Do not add tracking, fingerprinting, cookies or an external language-detection service.
- [ ] Test keyboard opening/closing, Escape, focus return, current-language announcement and long native labels. Translate the existing script-controlled Menu/Close labels as well as static navigation.

## Task 4: Translate and adapt the complete content

- [ ] Produce Quebec French, France French, and Modern Standard Arabic drafts from the same frozen English revision. Keep plain, credible business language and all limitations; do not add results, partnerships or guarantees.
- [ ] Review Quebec and France variants separately for terminology, idiom, punctuation, spacing and tone. Translate metadata and accessibility text with the same care as headings.
- [ ] Have an Arabic language reviewer check meaning, terminology, names, numeral treatment and the target-market suitability of the shared written register. A second model can flag issues but does not replace native editorial approval.
- [ ] Check every source sentence against the translation for omissions, softened qualifiers, invented claims and unexplained English. Back-translation is a diagnostic tool, not proof of quality.
- [ ] Record review decisions per page/locale. Keep unreviewed drafts on preview; only approved content enters production.

## Task 5: Arabic layout and external services

- [ ] Use logical CSS properties for margins, padding, insets and alignment. Set Arabic reading direction deliberately; retain left-to-right isolation for email, phone numbers, URLs and other mixed-script identifiers.
- [ ] Select and self-host an Arabic font with complete shaping support. Avoid Latin-style letter spacing and uppercase transformations on Arabic. Preserve the existing Latin brand marks and illustrations; do not mirror artwork indiscriminately.
- [ ] Review each page's hero, menu, card grids, diagrams, modal close controls and directional arrows. Allow French and Arabic text to wrap naturally rather than shrinking it to fit the English geometry.
- [ ] Confirm with HopShop whether the existing show supports French/Arabic UI, regional speech, locale parameters or separate shows. Do not invent embed parameters, duplicate the widget or claim the twin switches language just because the surrounding page does.
- [ ] Preserve the current embed until supported localization behavior is known. Record any English-only twin/media limitation for release review. Conversation and voice QA require a separate approved interaction; website language switching alone does not translate video or voice.

## Task 6: Checks and staged release

- [ ] Automated checks: 44 expected page editions; no missing keys, accidental placeholders or stray untranslated UI; complete equivalent-page maps; correct language/direction, canonical and reciprocal alternate links; unique sitemap URLs; working local assets and navigation.
- [ ] Browser tests: each of the 44 page editions at 1440, 1024, 768, 390 and 320 pixels (220 page/viewport combinations). Check overflow, clipped text, overlapping copy/buttons, nav focus, modals, font loading, mixed-direction text and HopShop obstruction. Check reduced motion and blocked JavaScript/storage fallbacks on representative pages.
- [ ] Check browser-language cases fr-CA, fr-FR, generic fr, ar-SA, ar-EG, unsupported languages and multiple preferences. Explicit URL and manual selection must always win over a suggestion.
- [ ] Manually review representative desktop/mobile pages for every locale; obtain native language approval for all translated copy. Physical iPhone/Safari and live twin speech are separate checks and must be reported honestly.
- [ ] Deploy a complete Cloudflare preview manifest with the retained headers/redirects and new shared assets. Confirm English parity, translated pages, Analytics isolation and embed coverage before production.
- [ ] Publish only the approved locale set. Recheck all live URLs/assets and sitemap responses; submit the expanded sitemap to Google and Bing. Commit/push the final source, generator, content and sanitized release evidence. Keep the prior production release available for rollback.

## Acceptance and maintenance

A successful release offers complete readable editions, an equivalent-page language switch, optional browser-language suggestions, working RTL layouts, and search-discoverable URLs. It does not promise automatic translation of English films or Randy's external twin. Subsequent English edits flag corresponding locale content for re-review; the generator prevents silently publishing stale translations. Add languages through the same content/template pipeline rather than copying an independently maintained website.

## References

- Google multilingual site architecture: https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites
- Google localized versions and alternate annotations: https://developers.google.com/search/docs/specialty/international/localized-versions
- Unicode default Arabic content locale: https://cldr.unicode.org/translation/translation-guide-general/default-content
- W3C Arabic layout requirements: https://www.w3.org/TR/alreq/
