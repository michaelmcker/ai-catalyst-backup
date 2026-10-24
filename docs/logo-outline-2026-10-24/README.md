# Website outline logo refinement

Michael requested navy text/stars and a thin navy pill outline for the website, keeping the filled pill as a backup for other uses. The SVG changes only three paint attributes: pill fill becomes none, pill stroke becomes #0A2A5C, and the white text/star group becomes #0A2A5C. All paths, stroke width, intrinsic dimensions and viewBox remain unchanged. The header CSS and all other website files are unchanged.

The exact preceding filled asset is saved at brand/ai-catalyst-logo-filled-navy.svg. Its bytes match the published filled logo.

This is a one-file live patch over production b918019d-16b5-486b-b387-a6e3ff4a6f35: only /assets/logo.svg is uploaded, while103 existing asset hashes are reused. The backup stays in the repository for reuse rather than becoming a new website dependency.
