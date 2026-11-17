# Blog release — 17 November 2026

The public blog contains an index and two video/transcript pages, with complete English, Quebec French, France French and Modern Standard Arabic editions. Source recordings:
- https://www.youtube.com/watch?v=qabmU8E7dCg — Prove It or Lose It
- https://www.youtube.com/watch?v=m7w5cVsCj5k — published as Coffee Chats on Agenetic Live Selling; the article is titled Where does the next dollar go?

Published automatic English captions were retrieved on November 16 through Firecrawl's YouTube transcript capability. Raw timed captions and joined text are preserved in content/blog/youtube-source.json. The Video Scripts chat was inspected. Its current Prove It script confirms COVID, MMM and Claude spellings. Final-video additions were retained rather than replaced by script wording. The site address and obvious caption typos were corrected. Claims are attributed to Randy's recorded commentary; no independent verification is implied.

The index and articles use the existing shared header/footer, analytics, twin, language switching and discovery system. Videos are lazy, privacy-enhanced YouTube embeds without autoplay, with descriptive iframe titles, referrer policy, fullscreen support and direct YouTube fallback links. Transcripts are HTML paragraphs, not text baked into images. French and Arabic translations are model reviewed, not native-speaker certified; videos remain English.

Checks: 56-edition localization invariants; blog embed/discovery tests; blog and case-study source reproducibility; public-site checks; preference switcher; 60 browser measurements (three blog routes × four locales × five widths), with no detected horizontal overflow or h1 clipping. Actual dropdown selection retained the equivalent article. Screenshots of representative desktop/Arabic phone compositions reviewed.

Enclosing portfolio npm suite remains 168/170 before and after, with the same pre-existing resource-article completeness and v2-about-mobile failures.

Preview deployment: d8a26cb5-a763-440d-a6e1-8600481713d7.

Both hosted preview iframes rendered the supplied video's title, AI Catalyst channel and visible YouTube play surface. No autoplay or conversation with the twin was initiated.
Production deployment: 9b89d26c-b6b5-4826-958f-5c7e03939c68.
