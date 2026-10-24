#!/usr/bin/env python3
"""Check the selected headline/art row with one complete paragraph below.

Uses readWrapProof capture records, but never requires a copy rectangle, float
or wrapReady flag. Old wrap helpers are reused only for approved-source ink
masks and image-coordinate projection, not as layout acceptance criteria.
"""
from pathlib import Path
import argparse
import json
import math
import runpy
import statistics

ROOT = Path(__file__).resolve().parents[1]
HELPERS = runpy.run_path(str(ROOT/'scripts/check-mobile-subject-wrap.py'))
rectangle, numeric, nonspace = [HELPERS[key] for key in ('rectangle','numeric','nonspace')]
subject_mask, image_mapping = [HELPERS[key] for key in ('subject_mask','image_mapping')]
PAGES = ('company','solutions','training')
WIDTHS = (320,390,430,600)
BASELINE = ROOT/'docs/safari-wrap-2026-10-23/baseline.json'
CLIP_TOLERANCE = .5


def paragraph_lines(boxes):
    """Cluster character tops, then isolate normal leading from empty gaps."""
    groups = []
    for box in sorted(boxes,key=lambda value:value[1]):
        if groups and abs(box[1]-statistics.mean(groups[-1])) <= 1:
            groups[-1].append(box[1])
        else: groups.append([box[1]])
    tops = [statistics.mean(group) for group in groups]
    deltas = [b-a for a,b in zip(tops,tops[1:])]
    # Exclude large outliers when calculating the median, so one long blank
    # break cannot inflate the very threshold used to detect that break.
    normal = [delta for delta in deltas if delta <= min(deltas)*1.5] if deltas else []
    leading = statistics.median(normal) if normal else None
    return {'line_tops_css':tops,'line_count':len(tops),'line_gaps_css':deltas,
            'normal_median_leading_css':leading,
            'maximum_gap_css':max(deltas) if deltas else 0,
            'contiguous':leading is None or max(deltas) <= 1.5*leading+.5}


def check_row(row, baseline_texts):
    page, width = row['page'],int(row['width'])
    failures = []
    def require(condition,message):
        if not condition:failures.append(message)
    hero, headline, paragraph, art = [rectangle(row[key]) for key in ('hero','headline','paragraph','art')]
    styles = row['styles']
    left = hero[0]+numeric(styles['paddingLeft'])
    right = hero[2]-numeric(styles['paddingRight'])
    reading_width = right-left
    require(reading_width>0,'hero reading width is invalid')
    require(abs(headline[0]-left)<=1.5,'headline does not start at the left reading gutter')
    require(headline[2] <= left+reading_width*.5+1.5,'headline is not confined to the left half of its row')
    require(headline[2]-headline[0] >= reading_width*.4-1.5,'headline column has collapsed')
    require(art[2] >= left+reading_width*.5,'artwork does not extend into the right half')
    overlap = min(headline[3],art[3])-max(headline[1],art[1])
    require(overlap >= min(headline[3]-headline[1],art[3]-art[1])*.5,
            'headline and artwork do not share a substantial vertical row')
    require(abs(paragraph[0]-left)<=1.5 and abs(paragraph[2]-right)<=1.5,
            'supporting paragraph does not use the complete hero reading width')
    separation = paragraph[1]-max(headline[3],art[3])
    require(separation >= 20-.5,'paragraph begins less than 20px below the complete headline/art row')
    require(float(row['scrollWidth']) <= width+1,'horizontal document overflow exceeds 1px')
    require(row.get('texts') == baseline_texts,
            'headline, paragraph or action text differs from the unchanged baseline')
    mask, mask_info = subject_mask(page)
    to_source, mapping = image_mapping(row)
    if row['image'].get('sha256'):
        require(row['image']['sha256']==mask_info['sha256'],'captured source hash differs')
    bounds=(max(0.0,hero[0]),hero[1],min(float(width),hero[2]),hero[3])
    glyphs=row.get('glyphs',[])
    texts=row.get('texts',{})
    for role in ('headline','paragraph','action'):
        expected=texts.get(role,'')
        captured=''.join(glyph.get('char','') for glyph in glyphs if glyph.get('role')==role)
        require(nonspace(captured)==nonspace(expected),role+' character capture is incomplete')
    paragraph_boxes,collisions=[],[]
    tested=0
    for glyph in glyphs:
        char=glyph.get('char','')
        if not nonspace(char):continue
        require(len(char)==1,'a character record contains multiple characters')
        boxes=[rectangle(value) for value in glyph.get('rects',[])]
        boxes=[box for box in boxes if box[2]>box[0] and box[3]>box[1]]
        require(bool(boxes),f'character {char!r} has no visible measured bounds')
        for box in boxes:
            tested+=1
            require(box[0]>=bounds[0]-CLIP_TOLERANCE and box[2]<=bounds[2]+CLIP_TOLERANCE and
                    box[1]>=bounds[1]-CLIP_TOLERANCE and box[3]<=bounds[3]+CLIP_TOLERANCE,
                    'character bounds leave the hero/viewport rectangle by more than 0.5px')
            if glyph.get('role')=='paragraph':paragraph_boxes.append(box)
            source=to_source(box)
            region=(max(0,math.floor(source[0])),max(0,math.floor(source[1])),
                    min(mask.width,math.ceil(source[2])),min(mask.height,math.ceil(source[3])))
            if region[2]>region[0] and region[3]>region[1] and mask.crop(region).getbbox():
                collisions.append({'char':char,'role':glyph.get('role'),'character_rect_css':box,
                                   'protected_source_region':region})
    require(tested>=2,'no meaningful character bounds were tested')
    require(bool(paragraph_boxes),'paragraph has no measured character bounds')
    lines=paragraph_lines(paragraph_boxes)
    require(lines['contiguous'],'paragraph has an inter-line gap greater than 1.5 times its normal median leading')
    require(not collisions,f'{len(collisions)} character bounds approach protected artwork ink within 10px')
    return {'page':page,'width':width,'browser':row.get('browser','unspecified'),
            'capture_kind':row.get('captureKind','unspecified'),'reading_width_css':reading_width,
            'paragraph_separation_css':separation,'text_equals_baseline':row.get('texts')==baseline_texts,
            'tested_character_boxes':tested,'clip_bounds_css':bounds,'clip_tolerance_css':CLIP_TOLERANCE,
            'paragraph_lines':lines,'protected_source_mask':mask_info,'image_mapping':mapping,
            'ink_clearance_css':10,'collisions':collisions[:30],'failures':failures,
            'passed':not failures,'screenshot':row.get('screenshot')}


def load_baseline(path):
    rows=json.loads(path.read_text())
    result={row['page']:row['texts'] for row in rows}
    if set(result)!=set(PAGES):raise ValueError('baseline must contain all three original page texts')
    return result


def self_test():
    # Synthetic geometry still samples the actual source mask, so the ink test
    # cannot pass merely because its source footprint was empty or omitted.
    for page in PAGES:
        sw,sh=HELPERS['PROFILES'][page]['size'];height=384*sh/sw
        texts={'headline':'H','paragraph':'PARA','action':''}
        top=100+height+26
        row={'page':page,'width':390,'scrollWidth':390,
             'hero':{'left':0,'top':0,'right':390,'bottom':900},
             'headline':{'left':24,'top':100,'right':188,'bottom':180},
             'paragraph':{'left':24,'top':top,'right':366,'bottom':top+92},
             'art':{'left':0,'top':100,'right':384,'bottom':100+height},
             'styles':{'paddingLeft':24,'paddingRight':24},
             'image':{'src':HELPERS['PROFILES'][page]['path'],'naturalWidth':sw,'naturalHeight':sh,
                      'objectFit':'contain','objectPosition':'50% 50%'},
             'texts':texts,'glyphs':[{'char':'H','role':'headline','rects':[{'left':24,'top':105,'right':30,'bottom':122}]}]}
        for index,char in enumerate('PARA'):
            row['glyphs'].append({'char':char,'role':'paragraph','rects':[{
                'left':24,'top':top+index*25,'right':32,'bottom':top+index*25+17}]})
        assert check_row(row,texts)['passed'],check_row(row,texts)['failures']
        cases=[]
        narrow=json.loads(json.dumps(row));narrow['paragraph']['right']=200;cases.append((narrow,'complete hero reading width'))
        short=json.loads(json.dumps(row));short['texts']['paragraph']='PAR';cases.append((short,'unchanged baseline'))
        early=json.loads(json.dumps(row));early['paragraph']['top']=100+height+10;cases.append((early,'20px below'))
        clipped=json.loads(json.dumps(row));clipped['glyphs'][0]['rects'][0]['right']=390.75;cases.append((clipped,'0.5px'))
        split=json.loads(json.dumps(row));split['glyphs'][-1]['rects'][0]['top']+=100;split['glyphs'][-1]['rects'][0]['bottom']+=100;cases.append((split,'inter-line gap'))
        mask,_=subject_mask(page);bounds=mask.getbbox();point=None
        for y in range(bounds[1],bounds[3]):
            for x in range(bounds[0],bounds[2]):
                if mask.getpixel((x,y)):point=(x,y);break
            if point:break
        x,y=point;scale=384/sw
        on_ink=json.loads(json.dumps(row))
        on_ink['glyphs'][0]['rects']=[{'left':x*scale,'top':100+y*scale,'right':x*scale+2,'bottom':102+y*scale}]
        cases.append((on_ink,'protected artwork ink'))
        for case,message in cases:
            assert any(message in failure for failure in check_row(case,texts)['failures']),page+': '+message
    print('PASS: full-width paragraph, unchanged text, row separation, clipped character, paragraph-gap and actual-source-ink negative controls.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('captures',nargs='?',type=Path)
    parser.add_argument('--baseline',type=Path,default=BASELINE)
    parser.add_argument('--widths',nargs='+',type=int,default=list(WIDTHS))
    parser.add_argument('--output',type=Path)
    parser.add_argument('--self-test',action='store_true')
    args=parser.parse_args()
    if args.self_test:self_test();return
    if not args.captures:parser.error('captures JSON or folder is required')
    baseline=load_baseline(args.baseline)
    rows=[row for row in HELPERS['load_rows'](args.captures)
          if row.get('page') in PAGES and int(row.get('width',0)) in args.widths]
    failures,results,seen=[],[],[]
    for row in rows:
        key=(row['page'],int(row['width']));seen.append(key)
        try:
            result=check_row(row,baseline[row['page']]);results.append(result)
            failures.extend(f'{key[0]}@{key[1]}: {value}' for value in result['failures'])
        except (KeyError,ValueError,TypeError) as error:failures.append(f'{key[0]}@{key[1]}: invalid capture: {error}')
    for page,width in sorted({(page,width) for page in PAGES for width in args.widths}-set(seen)):
        failures.append(f'{page}@{width}: missing capture')
    if len(seen)!=len(set(seen)):failures.append('duplicate page/width capture')
    report={'method':'Headline/art row above one intact full-width paragraph; per-character clipping and independent source-ink clearance.',
            'limits':'DOMRange boxes are conservative, not glyph outlines. Browser captures do not establish physical iPhone Safari appearance.',
            'results':results,'failures':failures}
    if args.output:args.output.write_text(json.dumps(report,indent=2)+'\n')
    if failures:raise SystemExit('\n'.join('FAIL: '+value for value in failures))
    print(f'PASS: {len(results)} mobile rows; exact baseline text, contiguous full-width paragraphs, character bounds and source-ink clearance.')


if __name__=='__main__':main()
