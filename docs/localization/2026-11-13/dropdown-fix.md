# Dropdown pointer fix

Production deployment: `4f88a0e3-67e6-4181-b17f-44b3bd368fb5`.

The header inherits `pointer-events: none` and explicitly enables only its existing controls. The new language disclosure inherited the disabled pointer state, so mouse clicks passed through to the page while keyboard/AX activation still worked. The shared `.language-picker` now explicitly enables pointer events. All 44 page editions reference stylesheet version `20261113-2`, avoiding the previous cached CSS URL.

Verified through actual pointer clicks on the hosted preview for English, Quebec French, France French and Arabic, then on production at desktop and 390px phone width. Menu opening and language selection succeeded; Escape remains functional. A raw touch-event command was unsupported by the in-app browser, so no physical-touch-device certification is claimed.

Localization, switcher and public-site checks pass. Enclosing portfolio npm tests retain the two known failures. No copy, locale, media or telemetry settings changed.
