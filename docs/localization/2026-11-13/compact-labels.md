# Compact language labels — 14 November 2026

The header and dropdown now show CAN EN, CAN FR, FRA FR and AR. Full language names remain in hover titles and accessible labels. Locale IDs, translations and equivalent-page destinations are unchanged.

The redundant contact-arrow button is hidden at widths up to 360px in English as it already was in translated editions, keeping the longer label and Menu inside the header. The contact destination remains available in the menu and page. CSS URL is versioned 20261114-1.

Verification: all 44 generated editions, localization invariants, preference-switcher tests, case-study source check and public-site check passed. Actual pointer opening passed in all four editions at 320, 390 and 1440px. Preview selection from Company to CAN FR retained the equivalent Company page. Live homepage displayed all four abbreviations and opened by pointer. These are browser viewport checks, not physical touch-device certification.

The enclosing portfolio npm test suite has the same two existing failures before and after (168/170 pass): approved resource-article completeness and v2-about-mobile.

Preview: a962fbc7-f66d-4fa2-b95a-b9cc58eab6c8.
Production: 37d5fcd1-c5d1-4e7e-a4a3-ce5121d7721c.
