# Analucia / Sofia case study

Adds a homepage Case studies section immediately after the Commerce Command Centre and before Built Globally, with a link in the expanded menu and footer on all nine pages. The first feature describes Analucia’s Sofia shopping concierge, shows the existing 1:46 film, and explains the shopping challenge, delivered experience and customer actions. No conversion metrics or live-selling-show results are claimed.

The poster is a new 1280 × 720 still from the existing Sofia launch film at 00:24. Inline playback reuses the existing click-to-load privacy-enhanced YouTube player, with a normal video link as fallback. Approved artwork, service films, contact routes, renderer, loader and hero layouts remain unchanged. Canonical source and root mirrors match.

## Validation

- Public-site and strict source-preservation checks pass, including negative controls.
- Image-loading and deferred-renderer checks pass, including loader mutation controls.
- Rendered at 1280, 390 and 320px: no horizontal overflow; mobile stacks copy, film and detail paragraphs.
- Case studies menu navigation and inline Sofia playback verified in the browser.
- Enclosing portfolio npm test: 170 of 171 pass before and after. The same unrelated resources.test.mjs article-completeness assertion fails. A first post-change run lacked CHROME_PATH; rerunning with the installed browser restored the baseline result. This static site has no npm package.
- Release manifest contains 111 public assets: nine HTML updates and two new assets, preserving all other 100 asset hashes. Headers are unchanged.

Screenshots: desktop.jpg and mobile.jpg. Physical iPhone and separate Safari testing were not performed for this section.
