# Move case studies into a CMS collection

Michael requested a link-only homepage and a separate editable collection where visitors can browse all case studies. The homepage now contains only View case studies. Expanded menu and footer links on all nine static pages go to `/case-studies/`.

The official EmDash Cloudflare starter supplies the native CMS. Analucia/Sofia is one published entry at `/case-studies/analucia-sofia/`; its existing text and film have moved off the homepage. A D1-backed collection contains eight owner-editable fields. Existing public pages remain on Cloudflare Pages, and only the collection, native CMS and its generated asset routes use the new Worker. No DNS, mail or existing service-film changes were made.

The public collection and case study were verified on the live domain. The Sofia film played inline; phone widths 390 and 320px showed no horizontal overflow. The same header/footer and original poster are reused. A temporary draft fixture in local production preview stayed absent from the collection and redirected away from its direct URL, then was removed. Native production preview rejects the dev-bypass endpoint with 403 and reports setup complete. Owner editing requires completing the private native passkey invitation; no credentials were registered by the agent and no invitation email was sent. See the CMS README for ownership and initial provisioning.

Public-site, strict source-preservation and negative controls, loader and renderer checks pass. CMS seed validation, build and type checks pass. The enclosing portfolio suite returns 170 passes and the same unrelated article-completeness failure among 171 tests before/after.

The static release changes ten assets (nine HTML files and the link stylesheet), preserving the other 101 asset hashes and headers. The separate Worker release uses 69 client assets and 604 minified server modules, approximately 1.7 MiB compressed. Its content is managed by EmDash, not reimported on code deploys. Image and YouTube URLs are editable; binary media upload is not configured.
