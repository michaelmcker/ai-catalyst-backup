# Outlined logo browser-cache correction

The public SVG was already the correct outlined logo, but its unchanged assets/logo.svg URL has Cache-Control public,max-age14400,must-revalidate. Existing clients can reuse the older filled SVG for four hours. HTML responses revalidate on a normal page load.

All nine public pages now reference assets/logo.svg?v=outline-b8383198 in the header, deferred footer and noscript footer. Only those three exact references change per page. Copy, markup geometry, scripts, CSS, artwork, dither, contact information and interactions remain byte-identical to the preceding production release. The filled navy backup is preserved.

The dedicated patch uploads the nine small HTML files and reuses95 unchanged asset hashes from production41144941/code4d3c734. This is a logo-reference patch over the live tree, not an older full-site snapshot. base-manifest.json is reconstructed from the checked-in preceding base manifest plus its one SVG hash replacement.

Before publication, the open in-app production Pages tab already rendered the correct outline (header-before.png); this does not establish what the user's separate Safari cache displayed. The URL version removes that cache ambiguity for subsequent normal page loads.

Production1f4f585e-269f-417b-bb36-ae1b44eab307 is successful and canonical. All nine public HTML bodies, both additional domain roots and the versioned logo match exact local source. A normal reload of the existing in-app Pages-domain homepage, without disabling cache, requests the versioned outlined SVG and reports it loaded. Header height remains81px. header-after.png captures the live header; outlined-header-logo.png is a crop of that actual screenshot.
