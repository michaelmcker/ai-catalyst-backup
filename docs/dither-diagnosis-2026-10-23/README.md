# Live dither regression analysis

This is a diagnosis of the rejected Cloudflare rendering, not a new release. No production source was edited or deployed during this analysis.

## Verified live sources

The Vercel reference shader was read from the actual network response loaded by the in-app browser at `https://ai-catalyst-wheat.vercel.app/halftone-rendering.js?v=20261015-continuity2`. Its bytes exactly match `68dbb96:current-site/halftone-rendering.js`; SHA-256 is `f634ede2e8c281f5f412e44142bcd9e1effa94ea237f2311b401ce5bd1454562`. The actual Cloudflare response for `halftone-rendering.js?v=20261023-repair4` exactly matches the current local source.

The built-in Vercel connector had already confirmed project ownership and deployment metadata. Its team-scoped file reads failed. Public rendered-page inspection through the in-app browser supplied the source and visual evidence used here; API access failure is not the cause of the rendering regression.

## What changed

1. `ff882fa` changes `v1=whiteSurface*hero` to `v1=0`, removes the field fragment's call to `v1Paper`, and forces `continuous=1` for every image. The original shared field reacts to pointer position and time through ordered dot density. Cloudflare retains the event handlers, but the background fragment no longer consumes that pointer field. The artwork's original threshold animation is multiplied by zero. A faint tonal pass remains; this is a different effect.
2. `2aac3c8` replaces the ordered print screen with fixed random grain. Original engraving-style close-ups become mostly continuous shading. Home changes from its original 72% desktop / 90% mobile print defaults to 32% in both. Scenic profile strength changes from 68% to 20%, architecture from 58% to 24%, and painting from 62% to 24%. These are shared renderer settings, so they affect multiple heroes and supporting images.
3. The same change moves Home's common field from above the artwork with multiply blending to below it with normal blending. The rendered image canvas can retain source-paper pixels according to a luminance/detail mask. Those surviving pixels now cover the background grain rather than receiving the same overlaid screen. Together with smooth image shading versus grainy paper and the still-ordered edge feathering, this breaks the single print treatment and can expose the rectangular image region.
4. The optimized responsive variants and physical texel-size fix are separate from the visual rewrite. Smaller image delivery did not require disabling the effect. The original image masters remain recoverable and unchanged.

## Correction to the earlier explanation

The previous claim that the visible original `<img>` was covering the field was incorrect. Computed styles show `visibility:hidden` on that image after `site-art-ready`; opacity alone was misleading. Both actual deployments hide the image and show the WebGL canvas. The compositing issue concerns retained paper in that canvas and the changed field layer, not an exposed underlying image.

## Captured behaviour

`desktop-layer-facts.json` records actual visibility, blending, stacking, canvas pixel sizes and geometry. Desktop PNG sequences were captured at 1440 by 1000 with the pointer initially outside the hero and then moved through three locations. In the final frame, 28.44% of sampled artwork pixels changed by more than five channel levels on Vercel, compared with 0.22% on Cloudflare. The corresponding text-field figures were 5.54% and 0.40%. These comparisons include ambient elapsed animation and are diagnostic observations, not isolated causal performance benchmarks. See `frame-differences.json`.

Mobile captures also use a 390 by 844 viewport with device pixel ratio 3 and mobile metrics. Both canvases cap rendering density at 2, so a screenshot preview also resamples the print screen. These are Chromium emulations, not physical iPhone Safari. `vercel-mobile-dpr3-clip.png` is the correctly bounded reference capture; the earlier un-clipped Vercel mobile PNG is a capture-viewport mismatch and must not be used as evidence of page layout. Cloudflare visibly uses fine noise and smooth image shading where the reference uses ordered dots across the image and copy area.

The reported extra darkening during a physical iPhone screenshot was not reproduced or explained conclusively. There is no verified basis here to attribute it to a particular Safari or display setting.

## Why earlier verification missed this

The previous release checks validated layout, resource budgets and the existence of pale blue pixels. They did not validate the intended moving ordered print, pointer response, image/background screen continuity, or real iPhone appearance. Passing those checks did not establish visual equivalence. The fixed-grain contract written during that repair encoded the mistaken design change.

The required correction is to recover the shared animated print behaviour and consistent artwork/paper compositing while retaining the requested hero primitives, contact/navigation changes and efficient responsive image delivery. The reference's original mobile flaws still need to be corrected; restoring a whole old site snapshot would also lose later requested changes.
