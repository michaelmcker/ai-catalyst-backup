#!/usr/bin/env python3
"""Compare tinted/grained source paper with transparent controls at each DPR.

Capture fixture pages at 390x600 CSS pixels with deviceScaleFactor 1, 2, 3.
The DPR suffix records the browser setting, not a claim inferred from a PNG.
Browser engines, OS and actual device must be recorded by the capture operator.
"""
from pathlib import Path
import argparse
import json

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / 'docs/safari-paper-2026-10-23/proof'


def difference(source, control, roi, css_width):
    if source.size != control.size:
        raise ValueError(f'capture sizes differ: {source.size} vs {control.size}')
    scale = source.width / css_width
    box = tuple(round(v * scale) for v in roi)
    pixels = list(ImageChops.difference(source.crop(box), control.crop(box)).getdata())
    maxima = [max(pixel) for pixel in pixels]
    return {'max_channel_delta': max(maxima),
            'mean_channel_delta': sum(sum(p) for p in pixels) / (len(pixels) * 3),
            'fraction_above_2': sum(v > 2 for v in maxima) / len(maxima),
            'pixel_count': len(pixels), 'screenshot_roi': box}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('captures', type=Path, help='directory containing manifest-named PNG screenshots')
    parser.add_argument('--fixtures', type=Path, default=DEFAULT)
    parser.add_argument('--dprs', type=int, nargs='+', default=[1, 2, 3])
    parser.add_argument('--output', type=Path)
    parser.add_argument('--require-original-failure', action='store_true', help='fail if original never differs >2, ensuring this capture set exposes a regression')
    args = parser.parse_args()
    manifest = json.loads((args.fixtures / 'manifest.json').read_text())
    rows, failures = [], []
    originals_failed = False
    for dpr in args.dprs:
        original_failures_at_dpr = 0
        for renderer in ('original', 'candidate'):
            for scene in manifest['paper_rgb']:
                control_path = args.captures / f'{renderer}-{scene}-transparent-dpr{dpr}.png'
                if not control_path.exists():
                    failures.append(f'missing {control_path.name}')
                    continue
                control = Image.open(control_path).convert('RGB')
                for variant in ('tinted', 'grain'):
                    source_path = args.captures / f'{renderer}-{scene}-{variant}-dpr{dpr}.png'
                    if not source_path.exists():
                        failures.append(f'missing {source_path.name}')
                        continue
                    source = Image.open(source_path).convert('RGB')
                    if source.height / source.width < 500 / 390:
                        failures.append(f'{source_path.name}: capture is too short for the paper ROIs')
                        continue
                    for name, roi in manifest['rois_css'].items():
                        stats = difference(source, control, roi, manifest['viewport']['width'])
                        failed = stats['max_channel_delta'] > 2
                        row = {'renderer': renderer, 'scene': scene, 'variant': variant,
                               'requested_dpr': dpr, 'roi': name, 'capture': source_path.name,
                               'image_size': source.size, **stats, 'within_tolerance': not failed}
                        rows.append(row)
                        if failed and renderer == 'candidate':
                            failures.append(f'{source_path.name} {name}: maximum difference {stats["max_channel_delta"]} >2')
                        if failed and renderer == 'original':
                            originals_failed = True
                            original_failures_at_dpr += 1
        if args.require_original_failure and not original_failures_at_dpr:
            failures.append(f'DPR{dpr}: original fixtures did not expose a >2 paper discontinuity')
    report = {'tolerance': 'max RGB channel difference <=2',
              'comparison': 'same renderer, geometry, phase and DPR; tinted/grain against transparent source',
              'original_failure_observed': originals_failed,
              'device_limit': 'PNG comparison does not establish actual iOS execution; browser/device capture evidence is separate.',
              'results': rows, 'failures': failures}
    text = json.dumps(report, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    else:
        print(text, end='')
    if failures:
        raise SystemExit('\n'.join('FAIL: ' + failure for failure in failures))
    print(f'PASS: {len(rows)} paper ROI comparisons; candidate maximum differences <=2; original failure observed={originals_failed}.')


if __name__ == '__main__':
    main()
