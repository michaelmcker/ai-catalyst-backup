#!/usr/bin/env python3
"""Build full-dimension delivery WebP derivatives without editing public HTML.

Original image files in the approved 83-file manifest are immutable inputs.
Near-lossless60 is permitted only for already-lossless WebP. Existing lossy
WebP is tested only with exact lossless recompression. Other formats stay put.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import tempfile

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'current-site'
REFERENCE = ROOT / 'docs/direct-vercel-2026-10-23/source-manifest.json'
MANIFEST = ROOT / 'docs/image-delivery-2026-10-24/manifest.json'
DELIVERY = Path('images/delivery-v1')
ENCODER = Path('/opt/homebrew/bin/cwebp')
CACHE = Path('/tmp/ai-catalyst-fullsize-compression-audit')
CACHE_SOURCES = {
    'images/art-v3/sword-hand-outpaint-v8.webp': 'home',
    'images/art-v3/company-knight.webp': 'company',
    'images/art-v3/kneeling-courtyard.webp': 'solutions',
    'images/art-v2/portrait-halftone.webp': 'training',
    'images/art-v3/briefing-arcade.webp': 'briefing',
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def source_images():
    return [row for row in json.loads(REFERENCE.read_text())
            if row.get('mime', '').startswith('image/')]


def verify_originals(rows):
    for row in rows:
        for base in (PUBLIC, ROOT):
            path = base / row['path']
            if not path.exists() or sha(path.read_bytes()) != row['sha256']:
                raise ValueError(f'Original image master changed or missing: {path}')


def coding(path):
    data = path.read_bytes()
    if data[:4] != b'RIFF' or data[8:12] != b'WEBP':
        return None
    offset = 12
    while offset + 8 <= len(data):
        kind = data[offset:offset + 4]
        size = int.from_bytes(data[offset + 4:offset + 8], 'little')
        if kind == b'VP8L':
            return 'VP8L'
        if kind == b'VP8 ':
            return 'VP8'
        offset += 8 + size + size % 2
    return None


def pixel_metrics(source, delivered):
    with Image.open(source) as source_im, Image.open(delivered) as target_im:
        if source_im.size != target_im.size:
            raise ValueError('Delivery dimensions differ from original')
        a = np.asarray(source_im.convert('RGBA'), dtype=np.int16)
        b = np.asarray(target_im.convert('RGBA'), dtype=np.int16)
        delta = np.abs(a[:, :, :3] - b[:, :, :3])
        return {'dimensions': list(source_im.size),
                'source_mode': source_im.mode, 'delivered_mode': target_im.mode,
                'max_rgb_error': int(delta.max()),
                'mean_absolute_rgb_error': round(float(delta.mean()), 8),
                'rgb_exact': bool(np.array_equal(a[:, :, :3], b[:, :, :3])),
                'alpha_exact': bool(np.array_equal(a[:, :, 3], b[:, :, 3])),
                'dimensions_exact': True}


def cached_candidate(row):
    page = CACHE_SOURCES.get(row['path'])
    records = CACHE / 'near-lossless-results.json'
    candidate = CACHE / f'{page}-webp-near60-m6.webp'
    if page and records.exists() and candidate.exists():
        for old in json.loads(records.read_text()):
            if (old.get('page') == page and old.get('encoding') == 'webp-near60-m6'
                    and old.get('source_sha256') == row['sha256']):
                return candidate
    return None


def build_one(row, temp):
    source = PUBLIC / row['path']
    result = {'source_path': row['path'], 'original_url': row['url'],
              'source_url': '/' + row['path'], 'source_sha256': row['sha256'],
              'source_bytes': source.stat().st_size}
    if source.suffix.lower() != '.webp':
        return {'status': 'skipped', 'reason': 'Non-WebP original preserved', **result}
    with Image.open(source) as im:
        if im.format != 'WEBP' or getattr(im, 'n_frames', 1) != 1:
            return {'status': 'skipped', 'reason': 'Non-static-WebP original preserved', **result}
        source_coding = coding(source)
        result['source_coding'] = source_coding
        mode = 'near-lossless60' if source_coding == 'VP8L' else 'exact-lossless-recompression'
        result['encoding_mode'] = mode
        candidate = cached_candidate(row) if mode == 'near-lossless60' else None
        cache_reused = candidate is not None
        if candidate is None:
            key = sha(row['path'].encode())[:16]
            png = temp / f'{key}.png'
            candidate = temp / f'{key}.webp'
            decoded = im.convert('RGBA' if 'A' in im.getbands() else 'RGB')
            metadata = {'icc_profile': im.info['icc_profile']} if im.info.get('icc_profile') else {}
            decoded.save(png, **metadata)
            command = [str(ENCODER), '-quiet', '-lossless', '-q', '100', '-m', '6', '-exact', '-metadata', 'all']
            if mode == 'near-lossless60':
                command += ['-near_lossless', '60']
            command += [str(png), '-o', str(candidate)]
            subprocess.run(command, check=True, capture_output=True)
    metrics = pixel_metrics(source, candidate)
    result.update(metrics)
    result['candidate_bytes'] = candidate.stat().st_size
    result['saving_fraction'] = round(1 - result['candidate_bytes'] / result['source_bytes'], 8)
    result['cache_reused'] = cache_reused
    maximum = 2 if mode == 'near-lossless60' else 0
    if not metrics['alpha_exact'] or metrics['max_rgb_error'] > maximum:
        raise ValueError(f'Pixel safety gate failed: {source}: {metrics}')
    if coding(candidate) != 'VP8L':
        raise ValueError(f'Delivery must remain lossless-coded WebP: {candidate}')
    if result['saving_fraction'] < .10:
        return {'status': 'skipped', 'reason': 'Less than 10% byte reduction', **result}
    data = candidate.read_bytes()
    digest = sha(data)
    path = DELIVERY / f'{source.stem}-{digest[:12]}.webp'
    for base in (PUBLIC, ROOT):
        target = base / path
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() or target.read_bytes() != data:
            target.write_bytes(data)
    return {'status': 'kept', **result, 'delivery_path': path.as_posix(),
            'delivery_url': '/' + path.as_posix(), 'delivered_sha256': digest,
            'delivered_bytes': len(data), 'delivered_coding': 'VP8L'}


def validate(manifest):
    originals = source_images()
    verify_originals(originals)
    if manifest['reference_manifest_sha256'] != sha(REFERENCE.read_bytes()):
        raise ValueError('Approved reference manifest changed')
    reference = {row['path']: row for row in originals}
    all_rows = manifest['entries'] + manifest['skipped']
    if len(all_rows) != len(reference) or {row['source_path'] for row in all_rows} != set(reference):
        raise ValueError('Delivery accounting omits or duplicates an original image')
    for row in all_rows:
        original = reference[row['source_path']]
        if (row['source_sha256'] != original['sha256'] or row['source_bytes'] != original['bytes']
                or row['source_url'] != '/' + row['source_path'] or row['original_url'] != original['url']):
            raise ValueError(f'Original image metadata differs: {row["source_path"]}')
    for row in manifest['entries']:
        source = PUBLIC / row['source_path']
        candidate = PUBLIC / row['delivery_path']
        data = candidate.read_bytes()
        if sha(data) != row['delivered_sha256'] or len(data) != row['delivered_bytes']:
            raise ValueError(f'Delivery checksum/size mismatch: {candidate}')
        if (ROOT / row['delivery_path']).read_bytes() != data:
            raise ValueError(f'Delivery mirror differs: {row["delivery_path"]}')
        expected_path = (DELIVERY / f'{source.stem}-{sha(data)[:12]}.webp').as_posix()
        if row['delivery_path'] != expected_path or row['delivery_url'] != '/' + expected_path:
            raise ValueError(f'Delivery name/URL does not match its content: {candidate}')
        if row['encoding_mode'] not in ('near-lossless60', 'exact-lossless-recompression'):
            raise ValueError(f'Unexpected delivery mode: {candidate}')
        expected_mode = 'near-lossless60' if coding(source) == 'VP8L' else 'exact-lossless-recompression'
        if row['encoding_mode'] != expected_mode:
            raise ValueError(f'Delivery mode is not permitted for this source: {source}')
        metrics = pixel_metrics(source, candidate)
        if metrics != {key: row[key] for key in metrics}:
            raise ValueError(f'Delivery pixel metrics changed: {candidate}')
        limit = 0 if row['encoding_mode'] == 'exact-lossless-recompression' else 2
        if metrics['max_rgb_error'] > limit or not metrics['alpha_exact']:
            raise ValueError(f'Delivery pixel safety gate failed: {candidate}')
        if 1 - len(data) / source.stat().st_size < .10:
            raise ValueError(f'Delivery byte reduction below 10%: {candidate}')
        if coding(candidate) != 'VP8L':
            raise ValueError(f'Unexpected delivery encoding: {candidate}')
    expected = {row['source_url']: row['delivery_url'] for row in manifest['entries']}
    if manifest['url_map'] != expected:
        raise ValueError('URL map does not match kept derivatives')
    expected_relative = {row['source_path']: row['delivery_path'] for row in manifest['entries']}
    if manifest['relative_url_map'] != expected_relative:
        raise ValueError('Relative URL map does not match kept derivatives')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='validate existing derivatives and all original image masters')
    parser.add_argument('--print-map', action='store_true', help='print original-relative-path to delivery-relative-path JSON without encoding')
    args = parser.parse_args()
    if args.print_map:
        manifest = json.loads(MANIFEST.read_text())
        print(json.dumps(manifest['relative_url_map'], indent=2))
        return
    if args.check:
        manifest = json.loads(MANIFEST.read_text())
        validate(manifest)
        print(f'PASS: {len(manifest["entries"])} full-size delivery files; exact dimensions/alpha; RGB error within declared gates; all {len(source_images())} original image masters unchanged.')
        return
    if not ENCODER.exists():
        raise SystemExit(f'Existing cwebp binary required: {ENCODER}; no package installation is performed.')
    rows = source_images()
    verify_originals(rows)
    results = []
    with tempfile.TemporaryDirectory(prefix='ai-catalyst-image-delivery-', dir='/tmp') as directory:
        with ThreadPoolExecutor(max_workers=2) as pool:
            pending = [pool.submit(build_one, row, Path(directory)) for row in rows]
            for future in as_completed(pending):
                row = future.result()
                results.append(row)
                if row['source_path'].endswith('.webp'):
                    print(f'{row["status"]}: {row["source_path"]} ({row.get("saving_fraction", 0):.1%} saved)', flush=True)
    kept = sorted((row for row in results if row['status'] == 'kept'), key=lambda row: row['source_path'])
    skipped = sorted((row for row in results if row['status'] != 'kept'), key=lambda row: row['source_path'])
    source_total = sum(row['source_bytes'] for row in results)
    replaced_source = sum(row['source_bytes'] for row in kept)
    replaced_delivery = sum(row['delivered_bytes'] for row in kept)
    saved = replaced_source - replaced_delivery
    manifest = {
        'schema_version': 1, 'reference_manifest': str(REFERENCE.relative_to(ROOT)),
        'reference_manifest_sha256': sha(REFERENCE.read_bytes()),
        'encoder': str(ENCODER), 'encoder_version': subprocess.check_output([str(ENCODER), '-version'], text=True).strip(),
        'policy': {'workers': 2, 'near_lossless': 60, 'method': 6, 'quality': 100,
                   'minimum_byte_saving_fraction': .10, 'maximum_rgb_error': 2,
                   'dimensions': 'full original intrinsic dimensions', 'alpha': 'pixel-exact',
                   'already_lossy_webp': 'exact lossless recompression only',
                   'masters': 'all original image files are preserved',
                   'html_substitution_applied': False},
        'totals': {'original_image_files': len(results), 'derivatives_kept': len(kept),
                   'unchanged_image_files': len(skipped), 'source_image_bytes': source_total,
                   'source_bytes_for_replaced_images': replaced_source,
                   'delivery_bytes_for_replaced_images': replaced_delivery,
                   'bytes_saved': saved,
                   'saving_fraction_for_replaced_images': saved / replaced_source if replaced_source else 0,
                   'image_bytes_after_substitution': source_total - saved,
                   'saving_fraction_all_images': saved / source_total if source_total else 0},
        'url_map': {row['source_url']: row['delivery_url'] for row in kept},
        'relative_url_map': {row['source_path']: row['delivery_path'] for row in kept},
        'entries': kept, 'skipped': skipped}
    validate(manifest)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest['totals'], indent=2))
    print(f'Manifest: {MANIFEST}')


if __name__ == '__main__':
    main()
