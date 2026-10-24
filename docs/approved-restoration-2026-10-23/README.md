# Approved Vercel rendering restoration

## Reference and scope

The in-app browser loaded all nine actual Vercel pages. Their HTML plus shared scripts, styles and observed artwork were read from real network responses. All 42 captured files match GitHub backup `68dbb96` byte for byte. `live-vercel-source-audit.json` records URLs, response sizes and SHA-256 hashes. This resolves the concern about possible copy drift: there were no unexpected copy differences between the reference and the backup. The current page-text integrity check uses the backup plus the authorized contact/navigation updates at `9bc79bd`.

The restoration recovers the approved ordered print, image-specific continuous/engraving methods, original profile strengths, clock animation and pointer response. The core was recovered from the reference-preserving `9bc79bd` revision; delivery safeguards remain around it. Source images, original motion/shell/service scripts and all body CSS are preserved. Added supporting-scene layout overrides were removed.

## Explicit changes retained

- Email `randy@aicatalyst.biz`, phone `416-270-0132`, Toronto, Canada; LinkedIn and Catalyst Retail Solutions references removed, including founder/advisor links. Randy confirmed mailbox delivery already works.
- Expanded-menu Training and adoption immediately follows How We Work.
- Home keeps its substantial sword and full mobile headline. Company, Solutions/How We Work, Briefing and Training retain requested right-side portrait heroes.
- Commerce Command Centre, Creator Intelligence, Full Commerce MMM and Agentic Consumer Intelligence keep headline LEFT, support RIGHT and image BELOW on desktop and mobile, with no image/copy spacer. The latest user clarification explicitly requires the left/right text row on phones too.
- The original moving field is shared across every entire hero and its image. Subpage fields have no bottom fade. An overlay above the artwork provides the common paper screen; scenic highlight paper beneath it is plain so the screen is applied once. This adapts the approved effect to the requested hero primitives rather than replacing the effect.
- Fingerprinted responsive delivery, deferred below-fold loading and decoded texture replacement remain. Physical texels and the original author-width sampling footprint avoid the previous responsive-image blur without changing the approved shader's profile settings.

## Verification before publication

- `check-approved-restoration.py` verifies all nine approved page texts, 73 original/authorized public assets, and recovered shader fragments/profile values. It rejects the previous `2aac3c8` shader. The original image masters and video are included in this asset comparison.
- `rendered-checks.json` passes 54 all-page hero checks across 320/390/430/768/1024/1440. The strengthened geometry check requires the panoramic headline/support row at every width, complete moving-field coverage, flush images, ready physical textures and no horizontal overflow.
- `retina-checks.json` adds all nine pages at 390 by 844 with device pixel ratio 3 and mobile metrics. Captures are Chromium emulation, not physical iPhone Safari.
- `check-restored-motion.py` evaluates actual screenshot sequences during mouse movement. Every hero and image region changes visibly; observed image-region maxima range from 3.79% to 15.13% of pixels changing by more than five channel levels in these sequences. This diagnostic includes ambient animation as well as pointer response; source inspection independently confirms the active mouse-driven path.
- Reduced-motion Home and Platform screenshots remain pixel-identical while the pointer moves. Both corresponding capture pairs are retained.
- Menu open/close and Training route order were exercised. The How We Work film dialog opened the approved local full-film.mp4 and closed successfully. Original interaction scripts are byte-identical to the verified reference. Public contact checks, local-resource checks, JavaScript syntax and image budgets pass. No sampled browser warnings/errors were observed.

Publication and live-domain verification are recorded after deployment. No claim of physical iPhone Safari testing is made.
