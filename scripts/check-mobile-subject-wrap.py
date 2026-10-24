#!/usr/bin/env python3
"""Check captured mobile text flow against independent source-art ink masks.

Reads evidence only. Character DOMRange bounds are conservative boxes, not
glyph outlines. Native Safari screenshots without glyph JSON remain visual
evidence and must not be represented as passing this automated collision test.
"""
from collections import deque
from functools import lru_cache
from pathlib import Path
from urllib.parse import unquote, urlparse
import argparse
import hashlib
import json
import math

from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
PAGES = ('company', 'solutions', 'training')
WIDTHS = (320, 390, 430, 600)
CLEARANCE = 10.0
# These source-space figure ROIs are independent of the CSS float polygons.
# Actual dark pixels inside them define the protected footprint; the entire
# rectangular image and its empty paper are deliberately not exclusions.
PROFILES = {
    'company': {'path': 'images/art-v3/company-knight.webp', 'size': (1536, 1024),
                'roi': [(620,45),(1515,45),(1515,945),(620,945)]},
    'solutions': {'path': 'images/art-v3/kneeling-courtyard.webp', 'size': (1672, 941),
                  'roi': [(1080,10),(1250,40),(1390,180),(1460,470),(1580,810),
                          (1530,905),(880,905),(880,480),(960,280),(1040,220)]},
    'training': {'path': 'images/art-v2/portrait-halftone.webp', 'size': (1672, 941),
                 'roi': [(1340,85),(1570,110),(1660,230),(1672,870),(1450,941),
                         (1050,941),(930,700),(1130,560),(1280,490),(1200,330),(1240,150)]},
    'briefing': {'path': 'images/art-v3/briefing-arcade.webp', 'size': (1672, 941),
                 'roi': [(800,0),(1672,0),(1672,941),(800,941)]},
}
DELIVERY_MANIFEST = ROOT/'docs/image-delivery-2026-10-24/manifest.json'
SOURCE_MANIFEST = ROOT/'docs/direct-vercel-2026-10-23/source-manifest.json'


def rectangle(value):
    left = float(value.get('left', value.get('x', 0)))
    top = float(value.get('top', value.get('y', 0)))
    right = float(value.get('right', left + float(value.get('width', 0))))
    bottom = float(value.get('bottom', top + float(value.get('height', 0))))
    return left, top, right, bottom


def numeric(value):
    return float(str(value).removesuffix('px'))


def nonspace(value):
    return ''.join(char for char in value if not char.isspace())


def retain_components(mask, minimum=16):
    """Remove isolated source dots; retain every substantial ink component.

    Keeping just the largest component could discard a helmet, hand or other
    real detail disconnected by the authored print. The 16-source-pixel floor
    removes tiny independent dots without joining pale regions artificially.
    """
    width, height = mask.size
    values = bytearray(mask.tobytes())
    retained = bytearray(len(values))
    count = 0
    for initial, value in enumerate(values):
        if not value:
            continue
        values[initial] = 0
        pending = deque([initial])
        component = []
        while pending:
            index = pending.pop()
            component.append(index)
            x, y = index % width, index // width
            for yy in range(max(0, y-1), min(height, y+2)):
                for xx in range(max(0, x-1), min(width, x+2)):
                    other = yy*width + xx
                    if values[other]:
                        values[other] = 0
                        pending.append(other)
        if len(component) >= minimum:
            count += 1
            for index in component:
                retained[index] = 255
    result = Image.frombytes('L', mask.size, bytes(retained))
    return result, count


@lru_cache(maxsize=4)
def subject_mask(page):
    profile = PROFILES[page]
    path = ROOT / 'current-site' / profile['path']
    data = path.read_bytes()
    with Image.open(path) as image:
        if image.size != profile['size']:
            raise ValueError(f'{page}: original source dimensions changed')
        # PIL L uses the same .299/.587/.114 luminance family as the shader.
        ink = image.convert('RGB').convert('L').point(lambda value: 255 if value < .82*255 else 0)
    roi = Image.new('L', ink.size)
    ImageDraw.Draw(roi).polygon(profile['roi'], fill=255)
    mask, components = retain_components(ImageChops.multiply(ink, roi))
    pixels = mask.histogram()[255]
    if pixels < 1000 or mask.getbbox() is None:
        raise ValueError(f'{page}: source-ink mask is empty or too small to test meaningfully')
    return mask, {'source': profile['path'], 'sha256': hashlib.sha256(data).hexdigest(),
                  'dimensions': profile['size'], 'luminance_threshold': .82,
                  'minimum_component_source_pixels': 16, 'retained_components': components,
                  'protected_source_pixels': pixels, 'roi_source': profile['roi']}


def position(value):
    if value in ('left', 'top'): return 0.0
    if value in ('right', 'bottom'): return 1.0
    if value == 'center': return .5
    if value.endswith('%'): return float(value[:-1])/100
    raise ValueError('object-position must use resolved percentages or edge/center keywords')


def image_mapping(row):
    page = row['page']
    image = row['image']
    source_size = PROFILES[page]['size']
    if (int(image['naturalWidth']), int(image['naturalHeight'])) != source_size:
        raise ValueError('captured natural dimensions differ from the approved image')
    location=urlparse(image['src'])
    path=unquote(location.path)
    # Local evidence serves the canonical directory beneath /current-site/.
    # Only a literal loopback host may shed that development-only prefix;
    # deployed URLs must still match the reviewed root-relative path exactly.
    if (location.scheme in ('http','https') and
            location.hostname in ('127.0.0.1','localhost','::1') and
            path.startswith('/current-site/')):
        path=path[len('/current-site/'):]
    else:path=path.lstrip('/')
    delivery = approved_delivery(page,path)
    left, top, right, bottom = rectangle(row['art'])
    width, height = right-left, bottom-top
    if width <= 0 or height <= 0:
        raise ValueError('art has no visible dimensions')
    crop = image.get('crop')
    if isinstance(crop, str): crop = [float(value) for value in crop.split()]
    if crop:
        offset_x, offset_y, crop_x, crop_y = map(float, crop)
    else:
        method = min if image['objectFit'] == 'contain' else max if image['objectFit'] == 'cover' else None
        if method is None: raise ValueError('unsupported object-fit '+image['objectFit'])
        scale = method(width/source_size[0], height/source_size[1])
        crop_x, crop_y = width/(source_size[0]*scale), height/(source_size[1]*scale)
        values = image['objectPosition'].split()
        if len(values) != 2: raise ValueError('object-position must contain two resolved values')
        offset_x, offset_y = (1-crop_x)*position(values[0]), (1-crop_y)*position(values[1])
    if crop_x <= 0 or crop_y <= 0: raise ValueError('invalid source crop')
    def to_source(rect, padding=CLEARANCE):
        x0, y0, x1, y1 = rect
        return ((offset_x+(x0-padding-left)/width*crop_x)*source_size[0],
                (offset_y+(y0-padding-top)/height*crop_y)*source_size[1],
                (offset_x+(x1+padding-left)/width*crop_x)*source_size[0],
                (offset_y+(y1+padding-top)/height*crop_y)*source_size[1])
    return to_source, {'offset': [offset_x,offset_y], 'crop': [crop_x,crop_y], **delivery}


def approved_delivery(page,path):
    """Allow only this source or its exact, hash-checked delivery mapping.

    Independent collision masks always use the original pixels. A derivative
    may change encoding only; source identity and natural geometry stay fixed.
    """
    profile=PROFILES[page]
    source_path=profile['path']
    source_data=(ROOT/'current-site'/source_path).read_bytes()
    source_sha=hashlib.sha256(source_data).hexdigest()
    approved={row['path']:row['sha256'] for row in json.loads(SOURCE_MANIFEST.read_text())}
    if approved.get(source_path)!=source_sha:
        raise ValueError('approved original artwork hash differs from the Vercel source manifest')
    if path==source_path:
        return {'source_path':source_path,'source_sha256':source_sha,
                'delivered_path':path,'delivered_sha256':source_sha,'derivative':False}
    if not DELIVERY_MANIFEST.exists():
        raise ValueError('captured source is not the approved page artwork; delivery manifest is absent')
    manifest=json.loads(DELIVERY_MANIFEST.read_text())
    entries=[entry for entry in manifest['entries'] if entry['source_path']==source_path]
    if len(entries)!=1:
        raise ValueError('delivery manifest must contain exactly one mapping for the approved artwork')
    entry=entries[0]
    if (path!=entry['delivery_path'] or
            manifest['relative_url_map'].get(source_path)!=path or
            manifest['url_map'].get('/'+source_path)!='/'+path):
        raise ValueError('captured source is not the exact approved original-to-delivery mapping')
    if Path(path).is_absolute() or '..' in Path(path).parts:
        raise ValueError('delivery mapping escapes the public directory')
    if (entry['source_sha256']!=source_sha or
            tuple(entry['dimensions'])!=profile['size'] or
            entry.get('dimensions_exact') is not True or entry.get('alpha_exact') is not True or
            not 0<=float(entry['max_rgb_error'])<=2):
        raise ValueError('delivery mapping changes the approved source identity, geometry or pixel budget')
    delivered=ROOT/'current-site'/path
    data=delivered.read_bytes()
    if hashlib.sha256(data).hexdigest()!=entry['delivered_sha256']:
        raise ValueError('delivered artwork hash differs from its exact manifest mapping')
    if (ROOT/path).read_bytes()!=data:
        raise ValueError('delivered artwork root mirror differs')
    with Image.open(delivered) as image:
        if image.size!=profile['size']:
            raise ValueError('delivered artwork dimensions differ from the approved original')
    return {'source_path':source_path,'source_sha256':source_sha,
            'delivered_path':path,'delivered_sha256':entry['delivered_sha256'],'derivative':True}


def check_row(row):
    failures = []
    page, width = row['page'], int(row['width'])
    label = f'{page}@{width}'
    require = lambda condition, message: None if condition else failures.append(message)
    hero, copy, headline, paragraph, art = [rectangle(row[key]) for key in ('hero','copy','headline','paragraph','art')]
    # Text may continue below the initial screen via normal page scrolling,
    # but no character may leave its hero or the horizontal viewport.
    text_bounds = (max(0.0,hero[0]),hero[1],min(float(width),hero[2]),hero[3])
    styles = row['styles']
    inner_width = copy[2]-copy[0]-numeric(styles['paddingLeft'])-numeric(styles['paddingRight'])
    require(abs((paragraph[2]-paragraph[0])-inner_width) <= 1.5,
            'paragraph is not the complete reading width; a fixed 54% column cannot pass')
    require(abs((headline[2]-headline[0])-inner_width) <= 1.5,
            'headline element is not the complete reading width')
    ready = row.get('wrapReady', row.get('heroData', {}).get('mobileWrap'))
    require(ready in (True, 'ready'), 'mobile wrap did not report ready')
    require(row.get('afterHeadline') is True, 'mobile float is not immediately after the headline')
    require(float(row['scrollWidth']) <= width+1, 'horizontal document overflow exceeds 1px')
    require(styles.get('artPosition') == 'absolute', 'art stage is not positioned independently of copy flow')
    natural = PROFILES[page]['size']
    expected_height = (art[2]-art[0])*natural[1]/natural[0]
    require(abs((art[3]-art[1])-expected_height) <= 1.5,
            'art height does not follow its fixed source aspect ratio')
    mask, mask_info = subject_mask(page)
    to_source, mapping = image_mapping(row)
    if row['image'].get('sha256'):
        require(row['image']['sha256'] == mapping['delivered_sha256'], 'captured delivered source hash differs')
    texts = row.get('texts', {})
    glyphs = row.get('glyphs', [])
    collisions, tested = [], 0
    for role in ('headline','paragraph'):
        expected = texts.get(role, row.get(role+'Text'))
        require(isinstance(expected, str) and bool(nonspace(expected or '')), f'{role} text completeness record missing')
        captured = ''.join(glyph.get('char','') for glyph in glyphs if glyph.get('role') == role)
        require(nonspace(captured) == nonspace(expected or ''), f'{role} character capture is incomplete')
    if texts.get('action'):
        captured = ''.join(glyph.get('char','') for glyph in glyphs if glyph.get('role') == 'action')
        require(nonspace(captured) == nonspace(texts['action']), 'action character capture is incomplete')
    for glyph in glyphs:
        char = glyph.get('char', '')
        if not nonspace(char): continue
        require(len(char) == 1, 'a glyph record contains multiple characters')
        boxes = glyph.get('rects', [])
        require(bool(boxes), f'character {char!r} has no measured bounds')
        for value in boxes:
            box = rectangle(value)
            if box[2] <= box[0] or box[3] <= box[1]: continue
            tested += 1
            require(box[0] >= text_bounds[0]-.5 and box[2] <= text_bounds[2]+.5 and
                    box[1] >= text_bounds[1]-.5 and box[3] <= text_bounds[3]+.5,
                    'character bounds leave the hero/viewport rectangle by more than 0.5px')
            source = to_source(box)
            region = (max(0,math.floor(source[0])),max(0,math.floor(source[1])),
                      min(mask.width,math.ceil(source[2])),min(mask.height,math.ceil(source[3])))
            if region[2] > region[0] and region[3] > region[1] and mask.crop(region).getbbox():
                collisions.append({'char': char, 'role': glyph.get('role'), 'character_rect_css': box,
                                   'protected_source_region': region})
    require(tested >= 2, 'no meaningful character bounds were tested')
    require(not collisions, f'{len(collisions)} character bounds intersect protected source ink within {CLEARANCE:g}px clearance')
    return {'page': page, 'width': width, 'browser': row.get('browser','unspecified'),
            'capture_kind': row.get('captureKind','unspecified'), 'paragraph_width': paragraph[2]-paragraph[0],
            'available_reading_width': inner_width, 'tested_character_boxes': tested,
            'character_clip_bounds_css': text_bounds, 'character_clip_tolerance_css': .5,
            'clearance_css_pixels': CLEARANCE, 'mask': mask_info, 'mapping': mapping,
            'collisions': collisions[:30], 'failures': failures, 'passed': not failures,
            'screenshot': row.get('screenshot')}


def load_rows(path):
    files = sorted(path.glob('*-capture.json')) if path.is_dir() else [path]
    if not files: raise ValueError('no *-capture.json files found')
    rows = []
    for filename in files:
        value = json.loads(filename.read_text())
        rows.extend(value if isinstance(value,list) else value.get('captures',[value]))
    return rows


def self_test():
    # The geometry test must not accept another artwork simply because a
    # similarly sized derivative has been captured under its filename.
    for page,profile in PROFILES.items():
        assert not approved_delivery(page,profile['path'])['derivative']
        width,height=profile['size']
        probe={'page':page,'art':{'left':0,'top':0,'width':width,'height':height},
               'image':{'src':'http://127.0.0.1:8856/current-site/'+profile['path'],
                        'naturalWidth':width,'naturalHeight':height,
                        'objectFit':'contain','objectPosition':'50% 50%'}}
        assert image_mapping(probe)[1]['source_path']==profile['path']
        for origin in ('https://example.com','http://127.0.0.1.example.com'):
            probe['image']['src']=origin+'/current-site/'+profile['path']
            try:image_mapping(probe)
            except ValueError:pass
            else:raise AssertionError(page+': remote development-prefix path was accepted')
        try:approved_delivery(page,'images/delivery-v1/unlisted.webp')
        except ValueError:pass
        else:raise AssertionError(page+': unlisted delivery path was accepted')
    if DELIVERY_MANIFEST.exists():
        manifest=json.loads(DELIVERY_MANIFEST.read_text())
        for page,profile in PROFILES.items():
            delivered=manifest['relative_url_map'].get(profile['path'])
            if delivered:assert approved_delivery(page,delivered)['derivative']
    for page in PAGES:
        mask, info = subject_mask(page)
        assert info['protected_source_pixels'] >= 1000
        w, h = PROFILES[page]['size']
        row = {'page':page,'width':390,'scrollWidth':390,'wrapReady':True,'afterHeadline':True,
               'hero':{'left':0,'top':0,'right':390,'bottom':900},
               'copy':{'left':0,'top':0,'right':390,'bottom':900},
               'headline':{'left':24,'top':20,'right':366,'bottom':40},
               'paragraph':{'left':24,'top':50,'right':366,'bottom':70},
               'span':{'left':200,'top':40,'right':390,'bottom':800},
               'art':{'left':0,'top':100,'right':384,'bottom':100+384*h/w},
               'styles':{'paddingLeft':24,'paddingRight':24,'artPosition':'absolute'},
               'image':{'src':PROFILES[page]['path'],'naturalWidth':w,'naturalHeight':h,
                        'objectFit':'contain','objectPosition':'50% 50%'},
               'texts':{'headline':'H','paragraph':'P'},
               'glyphs':[{'char':'H','role':'headline','rects':[{'left':24,'top':20,'right':30,'bottom':35}]},
                         {'char':'P','role':'paragraph','rects':[{'left':24,'top':50,'right':30,'bottom':65}]}]}
        assert check_row(row)['passed'], check_row(row)['failures']
        baseline = json.loads(json.dumps(row));baseline['paragraph']['right']=24+342*.54
        assert any('54%' in value for value in check_row(baseline)['failures'])
        clipped = json.loads(json.dumps(row))
        clipped['glyphs'][0]['rects'][0]['right']=390.75
        assert any('0.5px' in value for value in check_row(clipped)['failures']), page+' clipped-character sensitivity failed'
        bad = json.loads(json.dumps(row))
        bounds = mask.getbbox(); point = None
        for y in range(bounds[1],bounds[3]):
            for x in range(bounds[0],bounds[2]):
                if mask.getpixel((x,y)): point=(x,y);break
            if point:break
        x,y=point;scale=384/w
        bad['glyphs'][1]['rects']=[{'left':x*scale,'top':100+y*scale,'right':x*scale+2,'bottom':102+y*scale}]
        assert check_row(bad)['collisions'], page+' collision sensitivity failed'
    print('PASS: independent masks are substantial; fixed-54% baselines, 0.75px clipped characters and synthetic character/ink collisions are rejected.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('captures', nargs='?', type=Path)
    parser.add_argument('--widths', nargs='+', type=int, default=list(WIDTHS))
    parser.add_argument('--output', type=Path)
    parser.add_argument('--expect-baseline-failure', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test: self_test();return
    if not args.captures: parser.error('captures JSON or folder is required')
    results, failures = [], []
    rows = [row for row in load_rows(args.captures) if row.get('page') in PAGES and int(row.get('width',0)) in args.widths]
    seen = []
    for row in rows:
        key=(row['page'],int(row['width']));seen.append(key)
        try:
            result=check_row(row);results.append(result)
            failures.extend(f'{key[0]}@{key[1]}: {value}' for value in result['failures'])
        except (KeyError,ValueError,TypeError) as error: failures.append(f'{key[0]}@{key[1]}: invalid capture: {error}')
    expected={(page,width) for page in PAGES for width in args.widths}
    for key in sorted(expected-set(seen)):failures.append(f'{key[0]}@{key[1]}: missing capture')
    if len(seen)!=len(set(seen)):failures.append('duplicate page/width capture')
    report={'method':'Complete per-character DOMRange bounds against independent approved-source dark-ink masks, with 10 CSS px clearance.',
            'limits':'Character bounds are conservative boxes, not glyph outlines. Pale silhouette, every background detail, animation and physical iPhone Safari appearance require visual review.',
            'results':results,'failures':failures,'baseline_mode':args.expect_baseline_failure}
    if args.output:args.output.write_text(json.dumps(report,indent=2)+'\n')
    if args.expect_baseline_failure:
        if not any('54%' in failure for failure in failures):raise SystemExit('FAIL: baseline did not reproduce the fixed-column failure')
        print('PASS: baseline fixed-column failure reproduced; this is sensitivity evidence, not an accepted layout.');return
    if failures:raise SystemExit('\n'.join('FAIL: '+value for value in failures))
    print(f'PASS: {len(results)} mobile captures; full reading widths, after-headline floats, source-aspect artwork and protected-ink clearance.')


if __name__ == '__main__':
    main()
