# Analytics and search setup

The production site at `https://aicatalyst.biz/` loads the AI Catalyst GA4 web stream, measurement ID `G-YWZYZKJV9J`, via `analytics.js`. Analytics and advertising storage default to denied; Google Signals and ad personalization are disabled in the tag. The stream's enhanced measurement setting was observed enabled. Cookieless signals provide limited reporting; receipt in Analytics was not confirmed during deployment.

`sitemap.xml` lists the eleven current public pages. The sitemap was submitted to Google Search Console and Bing Webmaster Tools; submission does not guarantee indexing. Google and Bing ownership verification records must remain in DNS.

Cloudflare Pages production deployment `286991d1-76f4-4d97-a106-75c26fb30ed7` served the tag and sitemap. Local production source is `current-site/`, with root mirrors. The case-study shell is generated from `templates/case-studies-shell.html` by `scripts/build-case-studies.py`.
