# Approved pill logo swap

Michael authorized recreating the attached rough reference as an SVG pill logo using navy #0A2A5C, three white sparkles, a thin rim and white AI Catalyst wordmark. The SVG uses outlined text and no external font/image dependencies. The surrounding screenshot background is not part of the logo. Source reference: user-reference.png.

Exactly two public paths change: assets/logo.svg and client-layout-v3.css, mirrored at root/current-site. CSS changes only the shared logo box180→140px, image sizing to width:auto/max-height44px with intrinsic proportions, and the corresponding mobile image override. Existing header heights remain81px desktop/tablet and73px phone. No HTML, hero, copy, contact, menu, shader, motion, artwork, DNS or mail changes.

The base104-asset manifest is the recorded live production d6752c2e/code c9c841c manifest (SHA256881782c91698fefafbb301353b62aff3167486e9423afbc476cbd7d91864120c). The patch replaces only two asset hashes and retains102. Its dedicated transport can upload only these two files; it cannot upload a whole snapshot.

Checks: check-public-site.py; check-direct-vercel.py --self-test; check-direct-vercel.py; exact two-path public diff against production; SVG hash lock; native Safari desktop and390px header renders. Physical iPhone testing is user-side.

Production deployment b918019d-16b5-486b-b387-a6e3ff4a6f35 is successful/canonical. Transport uploaded exactly assets/logo.svg and client-layout-v3.css and reused102 unchanged live assets. Both public-domain responses return200 and match the local approved bytes exactly (live-source-verification.json). The new live SVG was rendered in the in-app browser and captured in live-logo.png. Native Safari local header screenshots show desktop and390px sizing. User activity interrupted the attempted native live screenshot, so no unrelated captured screen is retained as site evidence. Public files currently use max-age14400/must-revalidate; an already-open browser may require a hard refresh to see the new logo immediately.
