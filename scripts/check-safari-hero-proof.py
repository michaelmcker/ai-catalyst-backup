#!/usr/bin/env python3
"""Verify captured hero geometry and frozen-clock causal pointer responses.

This reads existing evidence; it does not launch browsers or change the site.
Passing Chromium captures does not constitute physical iPhone verification.
"""
from pathlib import Path
import argparse
import json
import math

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / 'docs/safari-paper-2026-10-23'
PORTRAITS = ('index', 'company', 'solutions', 'briefing', 'training')
PANORAMAS = ('platform', 'creator-social', 'marketing-investment', 'online-conversion')
PAGES = PORTRAITS + PANORAMAS
WIDTHS = (320, 390, 430, 600, 768, 1024, 1180, 1440)
ROIS = {'home': (100, 350, 650, 550),
        'portrait': (640, 300, 850, 500),
        'panorama': (730, 150, 775, 300)}


def near(a, b, tolerance=1):
    return abs(float(a) - float(b)) <= tolerance


def check_geometry(folder, failures):
    results = []
    for width in WIDTHS:
        path = folder / f'geometry-{width}.json'
        if not path.exists():
            failures.append(f'missing {path}')
            continue
        rows = json.loads(path.read_text())
        expected = set(('briefing', 'training') if width in (430, 600) else
                       PORTRAITS if width in (1024, 1180) else PAGES)
        actual = [row.get('page') for row in rows]
        if len(actual) != len(set(actual)) or set(actual) != expected:
            failures.append(f'{path.name}: expected pages {sorted(expected)}, got {actual}')
        for row in rows:
            page = row['page']
            label = f'{page}@{width}'
            before = len(failures)

            def require(condition, message):
                if not condition:
                    failures.append(f'{label}: {message}')

            require(row.get('width') == width, 'capture viewport width does not match its filename')
            require(row['scrollWidth'] <= width + 1, 'horizontal document overflow exceeds 1px')
            hero, copy, art = row['hero'], row['copy'], row['art']
            headline, paragraph = row['headline'], row['paragraph']
            require(headline['left'] >= -1 and headline['right'] <= width + 1,
                    'headline extends beyond viewport')
            require(paragraph['left'] >= -1 and paragraph['right'] <= width + 1,
                    'supporting paragraph extends beyond viewport')
            require(hero['width'] > 0 and hero['height'] > 0, 'hero has no visible geometry')
            require(row.get('artData', {}).get('artComposite') == 'single-opaque-surface',
                    'art is not assigned to the single hero compositor')
            require(row.get('artData', {}).get('artDrawReady') == 'true', 'art draw is not ready')
            canvases = row.get('canvases', [])
            require(len(canvases) == 1, f'expected one hero drawing surface, got {len(canvases)}')
            if len(canvases) == 1:
                canvas = canvases[0]
                data = canvas.get('data', {})
                rect = canvas['rect']
                require(data.get('artOpaque') == 'true', 'hero surface is not opaque')
                require(data.get('artDrawReady') == 'true', 'hero surface is not drawn')
                require(canvas.get('blend') == 'normal', 'hero still uses CSS blend compositing')
                require(near(canvas.get('opacity', 0), 1, .001), 'hero canvas is not fully visible')
                require(near(rect['left'], hero['left']) and near(rect['width'], hero['width']),
                        'opaque surface does not span the full hero width')
                ratio = float(data.get('artBackingRatio', 0))
                require(ratio > 0, 'canvas backing ratio is missing')
                require(near(canvas['width'], rect['width'] * ratio) and
                        near(canvas['height'], rect['height'] * ratio),
                        'canvas bitmap does not match its recorded backing ratio')
                if width <= 700:
                    require(near(row.get('dpr', 0), 3, .001), 'phone proof was not captured at DPR 3')
                    require(near(ratio, 3, .001), 'phone hero does not use native 3x backing pixels')
            if width <= 700 and page in PORTRAITS:
                gutter = 20 if width <= 360 else 24
                require(near(headline['left'], hero['left'] + gutter),
                        f'mobile headline is not on the upper-left {gutter}px gutter')
                require(near(headline['top'], hero['top'] + 28),
                        'mobile headline is not 28px below the hero top')
                require(headline['bottom'] <= hero['bottom'] + 1,
                        'mobile headline leaves the hero')
                if page in ('briefing', 'training'):
                    require(art['width'] <= 561,
                            'Training/Briefing mobile artwork exceeds the 560px cap')
                    if width >= 430:
                        require(art['left'] >= hero['right'] - 561 and art['right'] >= hero['right'] - 1,
                                'wide-phone Training/Briefing artwork is not anchored at the right')
            if (701 <= width <= 1199 and page in PORTRAITS) or (width >= 701 and page == 'index'):
                require(copy['right'] <= art['left'] + 1,
                        'tablet/desktop portrait copy and art have stacked or collide')
                overlap = min(copy['bottom'], art['bottom']) - max(copy['top'], art['top'])
                require(overlap >= min(copy['height'], art['height']) * .5,
                        'portrait copy and art do not occupy a shared vertical row')
                require(copy['width'] >= hero['width'] * .25 and art['width'] >= hero['width'] * .25,
                        'portrait split has collapsed one side')
            if page in PANORAMAS:
                require(headline['right'] <= paragraph['left'] - 1,
                        'panorama headline is not left of its supporting paragraph')
                require(near(headline['top'], paragraph['top'], 8),
                        'panorama text blocks are not aligned in one row')
                require(near(art['top'], copy['bottom']),
                        'panorama has a gap or overlap between text row and image')
                require(near(art['left'], hero['left']) and near(art['right'], hero['right']),
                        'panorama image is not flush full-width')
                require(max(headline['bottom'], paragraph['bottom']) <= art['top'] + 1,
                        'panorama text overflows into the image')
            results.append({'page': page, 'width': width,
                            'document_overflow': max(0, row['scrollWidth'] - width),
                            'composition': 'headline-left/support-right/image-below' if page in PANORAMAS else
                            ('headline-upper-left-over-image' if width <= 700 else
                             ('copy-left/art-right' if width <= 1199 or page == 'index' else 'approved-full-stage')),
                            'passed': len(failures) == before})
    return results


def pixel_difference(a, b, roi):
    if a.size != b.size:
        raise ValueError(f'screenshot dimensions differ: {a.size} vs {b.size}')
    if roi[2] > a.width or roi[3] > a.height:
        raise ValueError(f'ROI {roi} exceeds capture {a.size}')
    pixels = list(ImageChops.difference(a.crop(roi), b.crop(roi)).get_flattened_data())
    maxima = [max(pixel) for pixel in pixels]
    return {'changed_pixels': sum(value > 0 for value in maxima),
            'pixel_count': len(pixels), 'max_channel_delta': max(maxima),
            'mean_channel_delta': sum(sum(pixel) for pixel in pixels) / (len(pixels) * 3)}


def check_pointer(folder, failures):
    manifest_path = folder / 'manifest.json'
    if not manifest_path.exists():
        failures.append(f'missing {manifest_path}')
    else:
        manifest = json.loads(manifest_path.read_text())
        if manifest.get('clockUniformFrozen') is not True or manifest.get('sourceFilesModified') is not False:
            failures.append('pointer harness must freeze clock without modifying source files')
    results = []
    for source, page in [('candidate', page) for page in PAGES] + [('reference', 'company')]:
        before = len(failures)
        stem = f'{source}-{page}'
        paths = [folder / f'{stem}-{suffix}.png' for suffix in ('stationary0', 'stationary1', 'pointer')]
        meta_path = folder / f'{stem}-capture.json'
        missing = [str(path) for path in paths + [meta_path] if not path.exists()]
        if missing:
            failures.extend('missing ' + value for value in missing)
            continue
        metadata = json.loads(meta_path.read_text())
        attrs = metadata.get('attributes', {})
        if attrs.get('pointerProofPaused') != 'false' or attrs.get('pointerProofReduced') != 'false':
            failures.append(f'{stem}: pointer proof is paused or reduced-motion')
        if not math.isfinite(float(attrs.get('pointerProofPhase', 'nan'))):
            failures.append(f'{stem}: frozen clock phase missing')
        if int(attrs.get('pointerProofClockWrites', '0')) < 1 or int(attrs.get('pointerProofFrames', '0')) < 1:
            failures.append(f'{stem}: virtual frames or clock writes are missing')
        if source == 'candidate':
            canvases = metadata.get('canvas', [])
            if (len(canvases) != 1 or canvases[0].get('data', {}).get('artDrawReady') != 'true'
                    or canvases[0].get('data', {}).get('artOpaque') != 'true'):
                failures.append(f'{stem}: opaque candidate drawing surface is not ready')
        roi = ROIS['home' if page == 'index' else 'panorama' if page in PANORAMAS else 'portrait']
        images = [Image.open(path).convert('RGB') for path in paths]
        stationary = pixel_difference(images[0], images[1], roi)
        pointer = pixel_difference(images[0], images[2], roi)
        if stationary['changed_pixels'] != 0:
            failures.append(f'{stem}: stationary control changes at frozen clock')
        if source == 'candidate' and pointer['changed_pixels'] == 0:
            failures.append(f'{stem}: pointer does not change the selected paper region')
        if source == 'reference' and pointer['changed_pixels'] != 0:
            failures.append(f'{stem}: original Company paper unexpectedly responds to pointer')
        results.append({'source': source, 'page': page, 'roi_css': roi,
                        'image_size': images[0].size, 'phase_seconds': float(attrs['pointerProofPhase']),
                        'stationary': stationary, 'pointer': pointer,
                        'passed': len(failures) == before})
    return {'method': 'Frozen clock uniform; stepped virtual frames; stationary pair vs real pointer movement.',
            'claim': 'Paper response is causal to pointer input in these captured regions, not ambient time.',
            'limitations': 'Does not measure FPS, every artwork pixel, or physical iOS behavior.',
            'results': results}


def check_reduced(folder, failures):
    stem = 'reduced-company'
    paths = [folder / f'{stem}-{suffix}.png' for suffix in ('stationary0', 'stationary1', 'pointer')]
    metadata_path = folder / f'{stem}-capture.json'
    missing = [str(path) for path in paths + [metadata_path] if not path.exists()]
    if missing:
        failures.extend('missing ' + value for value in missing)
        return {'passed': False, 'missing': missing}
    metadata = json.loads(metadata_path.read_text())
    if metadata.get('attributes', {}).get('pointerProofReduced') != 'true':
        failures.append('reduced-company: captured preference is not reduced-motion')
    images = [Image.open(path).convert('RGB') for path in paths]
    stationary = pixel_difference(images[0], images[1], ROIS['portrait'])
    pointer = pixel_difference(images[0], images[2], ROIS['portrait'])
    if stationary['changed_pixels'] or pointer['changed_pixels']:
        failures.append('reduced-company: paper changes after virtual frames or pointer movement')
    return {'page': 'company', 'roi_css': ROIS['portrait'],
            'stationary': stationary, 'pointer': pointer,
            'captured_reduced_motion': metadata['attributes']['pointerProofReduced'],
            'passed': not stationary['changed_pixels'] and not pointer['changed_pixels']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, default=DEFAULT)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    geometry_failures, pointer_failures, reduced_failures = [], [], []
    geometry = check_geometry(args.evidence / 'responsive', geometry_failures)
    pointer = check_pointer(args.evidence / 'pointer', pointer_failures)
    reduced = check_reduced(args.evidence / 'pointer', reduced_failures)
    failures = geometry_failures + pointer_failures + reduced_failures
    pointer['reduced_motion'] = reduced
    pointer['failures'] = pointer_failures + reduced_failures
    (args.evidence / 'pointer/pixel-results.json').write_text(json.dumps(pointer, indent=2) + '\n')
    report = {'geometry': geometry, 'pointer_summary': pointer['results'], 'reduced_motion': reduced, 'failures': failures,
              'device_limit': 'Responsive Chromium and native macOS Safari responsive-mode evidence are not physical iPhone Safari verification.'}
    output = args.output or args.evidence / 'verification-results.json'
    output.write_text(json.dumps(report, indent=2) + '\n')
    if failures:
        raise SystemExit('\n'.join('FAIL: ' + failure for failure in failures))
    print(f'PASS: {len(geometry)} responsive hero records; 9 causal pointer responses; stationary controls unchanged; original Company and reduced-motion paper pointer deltas zero.')


if __name__ == '__main__':
    main()
