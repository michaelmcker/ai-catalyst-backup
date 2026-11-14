# Four-language website release — 13 November 2026

Production deployment: `f7b9f16a-29a2-44ec-876a-d15182f4bf25` at https://aicatalyst.biz/ . Prior release for rollback: `4e9514b5-7576-43ac-a10f-712344e3a77a`. Final hosted preview: https://a96beaaf.ai-catalyst-9l3.pages.dev/ .

All eleven public pages now have English, Quebec French, France French and Modern Standard Arabic editions (44 pages). The header switcher preserves the equivalent page. Browser-language and saved-preference suggestions are inline and never force a redirect. Arabic uses local Noto Sans Arabic fonts with RTL reading order; phone heroes separate copy from artwork. Original artwork and media remain shared. Arabic hero composition is reviewed separately: reposition or recrop artwork to support right-aligned copy, and mirror only suitable directional, text-free artwork after checking its meaning. Never flip lettering, logos, interfaces, charts or geography. Preserve source files and review fallbacks and all five viewport widths. The mandatory policy is in `AGENTS.md`; this policy update does not itself change live hero images.

427 source strings per catalog include visible text, metadata, alt text, aria labels and film titles. Runtime menu, enquiry, canvas-chart and map labels are also localized. Translation catalogs received model editorial/source checks. No certified native-speaker review was performed. The user authorized publication with that limitation disclosed. External films and HopShop UI/speech may remain English; translated pages include a notice. No live twin conversation, camera or microphone test was performed.

## Source maintenance

1. Edit the English template under `templates/i18n/` (for case studies, update `content/case-studies.json` or `templates/case-studies-shell.html` and run `python3 scripts/build-case-studies.py`). Never edit generated locale HTML directly.
2. Run `python3 scripts/refresh-localization-source.py` to update English strings and source hashes. Translate new/changed entries in **all three** catalogs; remove obsolete catalog keys when appropriate.
3. Review changed meaning, terminology, numerical claims and qualifiers. Run `python3 scripts/build-localized-site.py --record-review` only after completing that review. This records source/model review hashes, not native certification.
4. Run `python3 scripts/build-localized-site.py --check`, `python3 scripts/build-case-studies.py --check`, `python3 tests/localization/check.py`, `node tests/localization/switcher.cjs` and `python3 scripts/check-public-site.py`.
5. Review desktop/tablet/phone layouts and interactions on preview, publish the complete public manifest, and verify live pages. `AGENTS.md` makes all four editions mandatory for every new public page and material copy change.

The renderer fails on missing or uncatalogued copy, changed source hashes, and stale translation-review hashes. All generated HTML and sitemap files have exact root mirrors. No language-detection API or translation service runs in a visitor's browser. Only the language preference is stored by the switcher, guarded against denied storage.

## Verification

- 44-page structural checks: complete catalog keys, local assets, equivalent links, canonical/hreflang, direction, root mirrors, and exactly one retained Analytics/HopShop script.
- 220 page/viewport measurements in the in-app browser at 1440/1024/768/390/320: no detected horizontal overflow or clipped heading/paragraph/header containers. Representative French/Arabic screenshots reviewed, including fixes for expanded French headings and Arabic hero alignment. This is responsive desktop-browser evidence, not physical iPhone/Safari certification.
- Switcher preference, explicit-URL, blocked-storage, dismissal and Escape tests pass. Equivalent-page switching and keyboard disclosure also verified in the browser.
- AI Catalyst public-site and case-study source checks pass.
- Enclosing portfolio `npm test`: 168/170 before and after. Same existing failures: resources article parity and `tests/v2-about-mobile.test.mjs`.
- `live-verification.json` compares all 44 live pages with local generated output after decoding Cloudflare's existing email-protection transformation. Sitemap grows to 44 URLs; case-study sitemap contains the eight corresponding localized case-study URLs.

Release manifest and sanitized asset-upload receipt are retained in this directory. Existing Analytics ID `G-YWZYZKJV9J`, storage-denied tag configuration, HopShop show ID and DNS verification remain in place. Preview hosts cannot collect into production Analytics because the hostname gate is retained.

Google Search Console accepted the expanded sitemap resubmission; Bing accepted resubmission and showed Processing. Search engines had previously discovered the eleven English URLs; no claim is made that all new translations are indexed yet.
