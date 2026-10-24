# Direct transfer of the deployed Vercel site

## What changed in this attempt

The earlier "restoration" releases were custom adaptations. They changed renderer modes, dot strengths, layer compositing and Company proportions. Their whole-hero screenshot differences did not isolate mouse response from ambient animation. They are rejected as proof of equivalence.

This transfer downloads all 83 actual public files from https://ai-catalyst-wheat.vercel.app/. The downloaded 50,880,185 bytes match revision68dbb96 exactly. source-manifest.json records all URLs, sizes and SHA-256 hashes. The renderer is unchanged, with SHA-256 f634ede2e8c281f5f412e44142bcd9e1effa94ea237f2311b401ce5bd1454562. Every original stylesheet, interaction script and artwork asset is unchanged. The prior hero-layout.css and optimized-image substitutions are no longer imported.

## Narrow authorized exceptions

- scripts/apply-approved-content.py applies only Randy's email/phone/Toronto routes, removal of LinkedIn contact/profile links, expanded-menu Training after How We Work, and the enquiry fallback wording. The nine resulting page texts match9bc79bd. Original style/script tags and hero markup are preserved by this content patch.
- Four panoramic pages retain headline left, support right and a flush image below, including phones.
- The user subsequently rejected Vercel's stacked Company phone composition. Company therefore keeps text left and knight right below701px; desktop retains the exact Vercel presentation.
- The Command Centre phone row is rebalanced, with its CTA under the left headline and paragraph right. Other panoramic pages retain the previously requested arrangement.
- All presentation exceptions are isolated in migration-changes.css. The renderer is never edited. Fresh query keys bypass previous migration caches.

## Verification and limits

check-direct-vercel.py compares all83 public files against the exact downloaded source with only the deterministic allowlist above. check-public-site.py verifies contact/navigation and JavaScript syntax. Desktop and retina phone captures are retained alongside their geometry.

The test-only pointer-proof harness freezes the shader clock and queues frames, while loading the renderer unchanged. The stationary Home paper control has zero changed pixels. The first three mouse passes change2134,73,693 pixels in the chosen paper-only ROI on both the reference and candidate. This is causal pointer equivalence; ambient time cannot pass this check. Company paper returns zero in both sources, consistent with its original time-driven paperTone implementation. Its artwork wake is a separate behavior. Do not claim Company has pointer-driven background paper based on this test.

An early candidate Home screenshot caught the original CSS canvas entrance before opacity reached1 and looked washed out. The corrected candidate-index-390.png waits for the entrance to complete. This was a capture-readiness issue; no code was changed to hide it.

No iOS runtime is installed and no iPhone is connected. Native Safari is installed, but active user browsing interrupted UI control. No physical iOS Safari result is claimed. Michael has offered to check the stable Cloudflare preview on his iPhone. Production must not be replaced until that preview feedback is addressed.

Only the83 source files plus migration-changes.css are included in the preview manifest. Test fixtures, instructions, diagnostic source caches and proof screenshots are not deployed. DNS/mail settings remain untouched.
