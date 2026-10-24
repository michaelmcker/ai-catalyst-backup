# Hero paper continuity correction

The user supplied a physical iPhone screenshot showing darker paper outside the image and a white rectangular image region. Chromium reproduced the excessive paper contrast but did not reproduce the complete white box. A Safari-specific compositing cause is therefore an inference, not a verified hardware diagnosis.

## Targeted change

The ordered field retains its density pattern, time and pointer response. Only common paper ink opacity changes to 42% of the recovered value. Image profile strengths, source masters, layouts, copy and original interaction scripts are unchanged.

The previous separate CSS multiply layer above the masked artwork is removed. The same field function is multiplied into the hero image fragment output using shared world coordinates, time and pointer uniforms. A normal-blend field sits underneath, so transparent feathering and opaque white source paper receive the same screen exactly once. This removes dependency on Safari blending a WebGL canvas above another masked WebGL canvas.

## Verification

- `check-paper-continuity.py before-mobile.png` failed: mean paper luminance 0.936, darkest percentile 0.703. The test samples the empty left gutter, excluding text/art.
- After: mean paper luminance 0.967, darkest percentile 0.842. This is roughly half the measured darkness after screenshot rasterisation.
- `fixture.html` and `fixture-transparent.html` exercise the actual production renderer with otherwise identical opaque white and transparent source images at the same page coordinates. Their captures are pixel-identical. They are diagnostic documents outside the deployed current-site folder.
- All nine pages checked at 390x844, DPR 3 and at 1440x1000, DPR 1. Both geometry sets pass; no horizontal overflow. All nine actual mouse motion sequences pass. Home and Platform reduced-motion capture pairs are pixel-identical.
- Approved-source integrity, public contact/navigation, JavaScript syntax and image delivery budget checks pass. The 73 locked original/authorized assets and nine page texts remain unchanged.
- Screenshots are Chromium emulation. Physical iPhone Safari is not available for independent verification. The user's screenshot remains the direct evidence of its previous failure.

Canonical public source: current-site, mirrored to the root. Release cache key: 20261023-paper6. Publication results follow in deployment.json and live/.
