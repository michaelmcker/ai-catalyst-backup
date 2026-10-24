#!/usr/bin/env python3
"""Verify Vercel assets/copy plus the authorized compositor/responsive repair.

This source check does not establish Safari rendering or visible pointer motion.
Those require the separate paper/pointer captures and the user's iPhone review.
"""
from pathlib import Path
import argparse, hashlib, json, re, runpy, subprocess

ROOT=Path(__file__).resolve().parents[1]
CONTENT=runpy.run_path(str(ROOT/'scripts/apply-approved-content.py'))
PANO={'platform','creator-social','marketing-investment','online-conversion'}
ROW={'company','solutions','training'}
ROW_CACHE='20261023-row2'
MANIFEST=ROOT/'docs/direct-vercel-2026-10-23/source-manifest.json'
CACHE='20261023-direct8'
PARAGRAPH_REVISIONS={
    'solutions':(
        'Start with your business problem. We bring validated capabilities, senior operators and a focused pilot. Full Commerce MMM puts initial findings in your hands in 2–6 weeks.',
        'We pair senior operators with validated AI in a focused pilot, with initial Full Commerce MMM findings in 2–6 weeks.'),
    'training':(
        "Practical training built around your team's work. Leave with usable tools, a shared way to evaluate the output and workflows you can run yourselves.",
        'Practical training gives your team usable tools, a shared way to assess AI output and workflows they can run.'),
}

def original(path):
    return subprocess.check_output(['git','show','68dbb96:current-site/'+path],cwd=ROOT)

def expected(path,source):
    if path in CONTENT['FILES']:
        source=CONTENT['patch'](source,path)
        CONTENT['validate_result'](source,path)
    if path.endswith('.html'):
        s=source.decode()
        if Path(path).stem in PARAGRAPH_REVISIONS:
            before,after=PARAGRAPH_REVISIONS[Path(path).stem]
            assert s.count('<p>'+before+'</p>')==1,path+': approved paragraph exception does not match its source'
            s=s.replace('<p>'+before+'</p>','<p>'+after+'</p>',1)
        if Path(path).stem in PANO:
            s=s.replace('class="subpage ','class="subpage migration-pano ',1)
            s=s.replace('class="page-hero ','class="page-hero page-hero--stacked ',1)
            s,n=re.subn(r'(<div class="page-hero__copy"><h1>[\s\S]*?</h1>)(<p>[\s\S]*?</p>)(<a class="hero-link"[\s\S]*?</a>)(</div>)',r'\1<div class="page-hero__support">\2<div class="page-hero__actions">\3</div></div>\4',s,count=1)
            assert n==1,path
        imports=(f'<link rel="stylesheet" href="migration-changes.css?v={CACHE}">'
                 f'<link rel="stylesheet" href="hero-responsive-fix.css?v={CACHE}">')
        if Path(path).stem in ROW:
            imports+=f'<link rel="stylesheet" href="mobile-hero-row.css?v={ROW_CACHE}">'
        s=s.replace('</head>',imports+'</head>',1)
        s=re.sub(r'(halftone-rendering.js|feedback-v3.css)(?:\?[^"\s]+)?',lambda m:m[1]+'?v='+CACHE,s)
        source=s.encode()
    return source

def capture(source,pattern,label):
    result=re.search(pattern,source)
    if not result:raise ValueError('missing '+label)
    return result[1]

def shader(source,name):
    return capture(source,r'const '+re.escape(name)+r'=`([\s\S]*?)`;',name)

def function(source,name):
    """Extract a JS function without counting braces inside strings/comments."""
    found=re.search(r'\bfunction '+re.escape(name)+r'\(',source)
    if not found:raise ValueError('missing function '+name)
    start=found.start();index=source.index('{',found.end());depth=0;quote=None
    while index<len(source):
        char=source[index]
        if quote:
            if char=='\\':index+=2;continue
            if char==quote:quote=None
        elif source.startswith('//',index):
            end=source.find('\n',index);index=len(source) if end<0 else end;continue
        elif source.startswith('/*',index):
            end=source.find('*/',index+2)
            if end<0:raise ValueError('unterminated comment in '+name)
            index=end+2;continue
        elif char in "'\"`":quote=char
        elif char=='{':depth+=1
        elif char=='}':
            depth-=1
            if depth==0:return source[start:index+1]
        index+=1
    raise ValueError('unterminated function '+name)

def check_renderer(source,baseline):
    """Lock original image/motion calculations; allow only the new paper path."""
    fail=[]
    def same(label,current,approved):
        if current!=approved:fail.append('renderer: original '+label+' changed')
    same('profile values',capture(source,r'const profiles=\{([\s\S]*?)\};','profiles'),
         capture(baseline,r'const profiles=\{([\s\S]*?)\};','profiles'))
    # Includes Bayer order4/order8, weather, paper opacity, v1 density and
    # pointer Gaussian. No lowered paper strength or replacement grain passes.
    same('ordered print / weather / pointer functions',shader(source,'printing'),shader(baseline,'printing'))
    same('field shader',shader(source,'fieldFragment'),shader(baseline,'fieldFragment'))
    same('map color/print calculations',shader(source,'mapFragment'),
         shader(baseline,'mapFragment').replace('gl_FragColor=vec4(color,mask);','gl_FragColor=vec4(color*mask,mask);'))
    current=shader(source,'imageFragment');approved=shader(baseline,'imageFragment')
    same('image sampling',capture(current,r'(vec3 imageSample\([\s\S]*?\n    \})','image sampling'),
         capture(approved,r'(vec3 imageSample\([\s\S]*?\n    \})','image sampling'))
    start='vec3 base=imageSample(imageUV);'
    same('image thresholds / tonal pass / luminance / detail',
         current[current.index(start):current.index('if(composite<.5&&clearPaper<.5)')],
         approved[approved.index(start):approved.index('if(clearPaper<.5)')])
    for marker in ('float edges=','float feather='):
        same(marker,capture(current,r'('+re.escape(marker)+r'[^\n]+)','image '+marker),
             capture(approved,r'('+re.escape(marker)+r'[^\n]+)','image '+marker))
    # Authorized extension for non-white heroes: at zero pointer this rebuilds
    # the exact original paperTone; moving input adds the original Gaussian to
    # its ordered density. It must not recolor or amplify the resting paper.
    response=capture(current,r'if\(whiteSurface<\.5\)\{([\s\S]*?)\n        \}','subpage paper response')
    response=re.sub(r'//[^\n]*','',response)
    response=re.sub(r'\s+','',response)
    approved_response='''
      float disturbance=max(0.,v1Field(worldPixels,clock,fieldSize,pointer)-v1Field(worldPixels,clock,fieldSize,vec3(pointer.xy,0.)));
      float dots=step(order8(worldPixels),.19+disturbance);
      float fade=smoothstep(0.,.14,1.-worldPixels.y/fieldSize.y);
      float density=.48+weather(worldPixels,clock)*1.8;
      commonPaper=mix(vec3(1.),vec3(.58,.74,.94),dots*density*fade);
    '''
    same('zero-rest subpage pointer extension',response,re.sub(r'\s+','',approved_response))
    for name in ('setting','motionPaused','wake','tick','texture','visibility','position','updateMapMask','resetMotion'):
        # motionPaused is an arrow expression in the original source.
        if name=='motionPaused':
            same(name,capture(source,r'(const motionPaused=[^\n]+)','motion pause'),
                 capture(baseline,r'(const motionPaused=[^\n]+)','motion pause'))
        else:same(name,function(source,name),function(baseline,name))
    pointer=r'(function stamp\(x,y,radius\)\{[\s\S]*?)(?=\n    canvas.addEventListener\(\'webglcontextlost\')'
    same('pointer / trail / scroll handling',capture(source,pointer,'pointer handling'),capture(baseline,pointer,'pointer handling'))
    delegation='    if(isHero){if(field)setupHero(stage,img,field);return;}\n'
    same('body artwork setup',function(source,'setup').replace(delegation,''),function(baseline,'setup'))
    same('motion reset listeners',source[source.index("  document.addEventListener('visibilitychange'"):],
         baseline[baseline.index("  document.addEventListener('visibilitychange'"):])
    hero=function(source,'heroArtUniforms')
    settings=(
        "gl.uniform1f(u.printDepth,['map','footer'].includes(stage.dataset.artProfile)?.13:.34);",
        "gl.uniform1f(u.printPattern,stage.dataset.artPrintPattern==='drift'?2:0);",
        "gl.uniform1f(u.continuous,['scene','architecture','painting','footer','map'].includes(stage.dataset.artProfile)?1:0);",
        'gl.uniform2f(u.texel,1/img.naturalWidth,1/img.naturalHeight);',
        'gl.uniform1f(u.softness,setting(stage.dataset.artSoftness,profile?profile.softness:0));',
        "const edges=(stage.dataset.artFeather||(profile?profile.edges:'.24 .13 .17 .3')).split(' ').map(Number);",
        'gl.uniform1f(u.printStrength,Math.max(0,Math.min(1,setting(innerWidth<=700?stage.dataset.mobileArtPrint??stage.dataset.artPrint:stage.dataset.artPrint,profile?profile.print:.72))));',
    )
    for statement in settings:
        if statement not in hero:fail.append('renderer: hero profile uniform changed: '+statement)
    required=(
        "const area=isMap?hero:hero.closest('.art-opening,.hero-scene')||hero;",
        "const whiteSurface=isMap||area.dataset.artSurface==='white-flow';",
        "alpha:!opaque&&fragment!==fieldFragment,premultipliedAlpha:true",
        'renderer(canvas,isMap?mapFragment:imageFragment,!isMap)',
        "area.dataset.artComposite='single-opaque-surface'",
        'gl.uniform1f(u.composite,1);gl.uniform1f(u.sourceReady,ready?1:0);',
        'gl_FragColor=vec4(mix(commonPaper,col,coverage),1.);return;',
        'gl_FragColor=vec4(col*alpha,alpha);',
        'opaque?3:2',
    )
    for statement in required:
        if statement not in source:fail.append('renderer: compositor invariant missing: '+statement)
    return fail

def check_responsive_css(css):
    """Only two responsive geometry scopes plus three compositor layer rules."""
    plain=re.sub(r'/\*[\s\S]*?\*/','',css).strip();fail=[]
    global_rules=(
        '#main .site-hero-field.site-hero-composite{z-index:0!important;opacity:1!important;mix-blend-mode:normal!important}',
        '#main .hero-copy,#main .page-hero__copy{position:relative;z-index:3!important}',
        '#main [data-site-art="hero"]{z-index:1!important}',
    )
    for rule in global_rules:
        if plain.count(rule)!=1:fail.append('responsive CSS: expected compositor layer rule differs')
        plain=plain.replace(rule,'')
    allowed={'@media (min-width:701px) and (max-width:1199px)','@media (max-width:700px)'}
    seen=[]
    while plain.strip():
        plain=plain.lstrip();opening=plain.find('{')
        if opening<0:fail.append('responsive CSS: unparsed content');break
        header=plain[:opening].strip()
        if header not in allowed:fail.append('responsive CSS: unapproved desktop/global rule '+header);break
        depth=1;end=opening+1
        while end<len(plain) and depth:
            if plain[end]=='{':depth+=1
            elif plain[end]=='}':depth-=1
            end+=1
        if depth:fail.append('responsive CSS: unmatched braces');break
        body=plain[opening+1:end-1]
        if '@' in body:fail.append('responsive CSS: nested at-rule outside allowlist')
        for selector in re.findall(r'(?:^|\})([^{}]+)\{',body):
            if '#main' not in selector:fail.append('responsive CSS: selector escapes hero scope '+selector.strip())
            if '.subpage' in selector and ':not(.migration-pano)' not in selector and '.subpage-company' not in selector and '.subpage-solutions' not in selector:
                fail.append('responsive CSS: panoramic exclusion missing '+selector.strip())
        seen.append(header);plain=plain[end:]
    if set(seen)!=allowed:fail.append('responsive CSS: expected phone/tablet media scopes missing')
    return fail

def self_test():
    baseline=original('halftone-rendering.js').decode()
    source=(ROOT/'current-site/halftone-rendering.js').read_text()
    assert not check_renderer(source,baseline),check_renderer(source,baseline)
    for before,after in (("scene:{print:.68","scene:{print:.28"),
                         ('density=.48+weather','density=.12+weather'),
                         ('pointer.z*.11','pointer.z*.01'),
                         ('.19+disturbance','.29+disturbance'),
                         ('clock+=dt','clock+=0'),
                         ("event.pointerType==='touch'||motionPaused()","true||motionPaused()")):
        assert before in source,before
        assert check_renderer(source.replace(before,after,1),baseline),before
    css=(ROOT/'current-site/hero-responsive-fix.css').read_text()
    assert not check_responsive_css(css),check_responsive_css(css)
    assert check_responsive_css(css+'\n@media (min-width:1200px){#main .hero{height:1px}}')
    print('PASS: compositor invariants; profile/paper/pointer/clock mutations and unapproved desktop CSS are rejected.')

def check():
    rows=json.loads(MANIFEST.read_text());fail=[]
    for row in rows:
        path=row['path'];source=original(path)
        if hashlib.sha256(source).hexdigest()!=row['sha256'] or not row['matches_git_reference']:
            fail.append(path+': downloaded Vercel source differs from reference')
        if path=='halftone-rendering.js':
            try:fail.extend(check_renderer((ROOT/'current-site'/path).read_text(),source.decode()))
            except (ValueError,IndexError) as error:fail.append('renderer: '+str(error))
            if (ROOT/path).read_bytes()!=(ROOT/'current-site'/path).read_bytes():fail.append('renderer mirror differs')
            continue
        result=expected(path,source)
        for prefix in ('current-site/',''):
            if (ROOT/(prefix+path)).read_bytes()!=result:
                fail.append(prefix+path+': change outside approved content/panorama allowlist')
    css=(ROOT/'current-site/migration-changes.css').read_text()
    if (ROOT/'migration-changes.css').read_text()!=css:fail.append('migration CSS mirror differs')
    if any(x in css for x in ('site-hero-field','site-art-tones','mix-blend-mode','.hero-art','white-flow')):
        fail.append('migration CSS changes the original rendering system')
    approved_css=subprocess.check_output(['git','show','803176a:current-site/migration-changes.css'],cwd=ROOT,text=True)
    strip_comments=lambda value:re.sub(r'/\*[\s\S]*?\*/','',value).strip()
    if strip_comments(css)!=strip_comments(approved_css):fail.append('migration CSS differs from approved panorama/contact rules')
    responsive=(ROOT/'current-site/hero-responsive-fix.css').read_text()
    if (ROOT/'hero-responsive-fix.css').read_text()!=responsive:fail.append('responsive CSS mirror differs')
    fail.extend(check_responsive_css(responsive))
    # Briefing was explicitly accepted and is outside the three-page row fix.
    for prefix in ('current-site/',''):
        approved=subprocess.check_output(['git','show','9763a3a:current-site/briefing.html'],cwd=ROOT)
        if (ROOT/(prefix+'briefing.html')).read_bytes()!=approved:
            fail.append(prefix+'briefing.html: changed from the approved Briefing checkpoint 9763a3a')
    for page in ('index','company','solutions','briefing','training'):
        html=(ROOT/'current-site'/f'{page}.html').read_text()
        if 'hero-layout.css' in html or 'site-assets.js' in html or 'images/optimized' in html:
            fail.append(page+': previous adaptive renderer/delivery imports remain')
    if fail:raise SystemExit('\n'.join('FAIL: '+s for s in fail))
    print(f'PASS: {len(rows)} Vercel files against the explicit allowlist; original assets/styles/interaction scripts, approved copy including two explicit shorter paragraphs, retained print/weather/pointer calculations, authorized compositor and scoped phone/tablet hero layouts. Safari/visual behavior requires separate rendered proof.')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--self-test',action='store_true')
    if parser.parse_args().self_test:self_test()
    else:check()
