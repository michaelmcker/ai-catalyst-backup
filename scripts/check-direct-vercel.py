#!/usr/bin/env python3
"""Verify Vercel assets/copy plus the authorized compositor/responsive repair.

This source check does not establish Safari rendering or visible pointer motion.
Those require the separate paper/pointer captures and the user's iPhone review.
"""
from pathlib import Path
from html.parser import HTMLParser
import argparse, hashlib, json, re, runpy, subprocess
from PIL import Image, ImageChops

ROOT=Path(__file__).resolve().parents[1]
CONTENT=runpy.run_path(str(ROOT/'scripts/apply-approved-content.py'))
PANO={'platform','creator-social','marketing-investment','online-conversion'}
ROW={'company','solutions','training','briefing'}
ROW_CACHE='20261024-row5'
MANIFEST=ROOT/'docs/direct-vercel-2026-10-23/source-manifest.json'
CACHE='20261023-direct8'
RENDERER_CACHE='20261024-direct9'
IMAGE_LOADER_CACHE='20261024-load1'
IMAGE_LOADER_SHA256='767f07d5b0d122a1cd792a5c3dac0108d15f290ba16cc6f6e9f158b0573f044d'
APPROVED_LOGO_SHA256='60a31d37e3e7c084fc973861df45d81b9763e327a02afd4699b4bdd881393c84'
LOGO_URL='assets/logo.svg?v=filled-60a31d37'
DEFERRED_IMAGE_COUNTS={'index.html':2,'company.html':9,'briefing.html':2,'solutions.html':3,
                       'training.html':3,'platform.html':3,'creator-social.html':2,
                       'marketing-investment.html':3,'online-conversion.html':3}
DELIVERY_MANIFEST=ROOT/'docs/image-delivery-2026-10-24/manifest.json'
DELIVERY_MANIFEST_SHA256='9a5733fb7e18a2accd5854b0d56c68bb335c962fee076ae238b1aad9081d0c74'
HEADERS='/images/optimized/*\n  Cache-Control: public, max-age=31536000, immutable\n/images/delivery-v1/*\n  Cache-Control: public, max-age=31536000, immutable\n'
ARROW_ICON='<span class="arrow-icon" aria-hidden="true"><svg viewBox="0 0 20 20"><path d="M4 16 16 4M7 4h9v9"></path></svg></span>'
LITERAL_ARROW_COUNTS={
    'index.html':8,'company.html':1,'briefing.html':1,'solutions.html':1,
    'training.html':3,'platform.html':2,'creator-social.html':5,
    'marketing-investment.html':5,'online-conversion.html':5,
}
SOLUTIONS_ACTIONS='<a class="hero-link" href="#path">See the working model <span class="arrow-icon" aria-hidden="true"><svg viewbox="0 0 20 20"><path d="M4 16 16 4M7 4h9v9"></path></svg></span></a><button class="hero-film-button" type="button" aria-label="Watch the brand film"><span class="film-play-icon" aria-hidden="true"><svg viewbox="0 0 24 24"><path d="m9 6 9 6-9 6Z"></path></svg></span><span>Watch the film</span></button>'
PARAGRAPH_REVISIONS={
    'solutions':(
        'Start with your business problem. We bring validated capabilities, senior operators and a focused pilot. Full Commerce MMM puts initial findings in your hands in 2–6 weeks.',
        'We pair senior operators with validated AI in a focused pilot, with initial Full Commerce MMM findings in 2–6 weeks.'),
    'training':(
        "Practical training built around your team's work. Leave with usable tools, a shared way to evaluate the output and workflows you can run yourselves.",
        'Practical training gives your team usable tools, a shared way to assess AI output and workflows they can run.'),
    'briefing':(
        'Tell us where you want to improve: creator intelligence, marketing investment or online conversion. We work with your market and data. Initial Full Commerce MMM findings are available in 2–6 weeks.',
        'Tell us what you want to improve. We start with your market and data. Initial Full Commerce MMM findings arrive in 2–6 weeks.'),
}

def replace_literal_arrows(source,path):
    assert source.count('↗')==LITERAL_ARROW_COUNTS[path],path+': unexpected literal arrow count'
    source=source.replace('<span aria-hidden="true">↗</span>',ARROW_ICON)
    return source.replace('↗',ARROW_ICON)

def revise_paragraph(source,page):
    before,after=PARAGRAPH_REVISIONS[page]
    assert source.count('<p>'+before+'</p>')==1,page+': approved paragraph exception does not match its source'
    source=source.replace('<p>'+before+'</p>','<p>'+after+'</p>',1)
    if page=='training':
        headline='<h1>Put AI to work. Make it yours.</h1>'
        assert source.count(headline)==1,'training: original complete headline markup differs'
        source=source.replace(headline,'<h1><span class="training-headline__opening">Put AI to work.</span> <span class="training-headline__closing">Make it yours.</span></h1>',1)
    return source

def version_logo_urls(source,path):
    assert source.count('assets/logo.svg')==3 and source.count('assets/logo.svg"')==3,path+': expected exactly three unversioned logo references'
    return source.replace('assets/logo.svg',LOGO_URL)

def delivery_manifest():
    data=DELIVERY_MANIFEST.read_bytes()
    assert hashlib.sha256(data).hexdigest()==DELIVERY_MANIFEST_SHA256,'delivery manifest differs from the reviewed 17-entry mapping'
    manifest=json.loads(data)
    assert manifest['schema_version']==1 and len(manifest['entries'])==17,'delivery manifest schema/count differs'
    relative={entry['source_path']:entry['delivery_path'] for entry in manifest['entries']}
    assert len(relative)==17 and manifest['relative_url_map']==relative,'delivery mapping differs'
    assert manifest['url_map']=={'/'+source:'/'+target for source,target in relative.items()},'absolute delivery mapping differs'
    return manifest

def apply_image_delivery(source,path):
    mapping=delivery_manifest()['relative_url_map']
    # Change only img src attributes. Intrinsic dimensions, alt text, profile
    # attributes and other references retain the original Vercel bytes.
    source=re.sub(r'(<img\b[^>]*\bsrc=")([^"]+)(")',
                  lambda match:match[1]+mapping.get(match[2],match[2])+match[3],source)
    heroes=list(re.finditer(r'<(?:div|figure)\b[^>]*\bdata-site-art="hero"[^>]*>[\s\S]*?(<img\b[^>]*>)',source))
    assert len(heroes)==1,path+': expected exactly one hero image'
    image=heroes[0][1]
    if path=='solutions.html':
        assert 'fetchpriority=' not in image,path+': unexpected hero priority attribute'
        replacement=image.replace(' decoding="async"',' fetchpriority="high" decoding="async"',1)
        assert replacement!=image,path+': unexpected hero image decode attribute'
        source=source[:heroes[0].start(1)]+replacement+source[heroes[0].end(1):]
        image=replacement
    assert image.count('fetchpriority="high"')==1,path+': hero priority changed'
    hero_src=re.search(r'\bsrc="([^"]+)"',image)[1]
    assert hero_src in mapping.values(),path+': hero has no reviewed delivery mapping'
    preload=f'<link rel="preload" as="image" href="{hero_src}" fetchpriority="high">'
    assert source.count('<head>')==1 and 'rel="preload" as="image"' not in source,path+': unexpected image preload'
    return source.replace('<head>','<head>'+preload,1)

class DeferredImages(HTMLParser):
    """Locate only body artwork, advisor portraits and footer images."""
    VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
    def __init__(self,source):
        super().__init__()
        self.stack=[];self.images=[];self.offsets=[0]
        for line in source.splitlines(keepends=True):self.offsets.append(self.offsets[-1]+len(line))
        self.feed(source)
    def handle_starttag(self,tag,attrs):
        attributes=dict(attrs)
        if tag=='img':
            protected=any(name=='header' or values.get('data-site-art')=='hero' for name,values in self.stack)
            target=any(name=='footer' or values.get('data-site-art') not in (None,'hero') or
                       'team-portrait' in values.get('class','').split() for name,values in self.stack)
            if target and not protected:
                assert attributes.get('loading')=='lazy','deferred image lost its original lazy attribute'
                assert 'src' in attributes and 'data-deferred-src' not in attributes and 'srcset' not in attributes,'unexpected image source attributes'
                line,column=self.getpos()
                self.images.append((self.offsets[line-1]+column,self.get_starttag_text()))
        if tag not in self.VOID:self.stack.append((tag,attributes))
    def handle_endtag(self,tag):
        for index in range(len(self.stack)-1,-1,-1):
            if self.stack[index][0]==tag:del self.stack[index:];break

def apply_deferred_images(source,path):
    assert 'data-deferred-src' not in source and 'image-loading.js' not in source,path+': image deferral already applied or unexpected source'
    images=DeferredImages(source).images
    assert len(images)==DEFERRED_IMAGE_COUNTS[path],path+': unexpected body/advisor/footer image count'
    for offset,image in reversed(images):
        assert source[offset:offset+len(image)]==image,path+': image parser offset differs'
        assert image.count(' src="')==1,path+': unexpected image source markup'
        deferred=image.replace(' src="',' data-deferred-src="',1)
        source=source[:offset]+deferred+'<noscript>'+image+'</noscript>'+source[offset+len(image):]
    fallback='<noscript><style>img[data-deferred-src]{display:none!important}</style></noscript>'
    source=source.replace('<head>','<head>'+fallback,1)
    renderer=f'<script src="halftone-rendering.js?v={RENDERER_CACHE}" defer></script>'
    assert source.count(renderer)==1,path+': renderer script import differs'
    loader=f'<script src="image-loading.js?v={IMAGE_LOADER_CACHE}" defer></script>'
    return source.replace(renderer,loader+renderer,1)

def check_image_loader():
    source=(ROOT/'current-site/image-loading.js').read_bytes()
    assert hashlib.sha256(source).hexdigest()==IMAGE_LOADER_SHA256,'deferred image loader differs from its reviewed source'
    assert (ROOT/'image-loading.js').read_bytes()==source,'deferred image loader root mirror differs'
    result=subprocess.run(['node',str(ROOT/'scripts/check-image-loading.cjs'),'--self-test'],
                          cwd=ROOT,text=True,capture_output=True)
    assert result.returncode==0,'deferred image loader behavioral regression failed: '+result.stdout+result.stderr

def check_delivery():
    manifest=delivery_manifest()
    approved={row['path']:row['sha256'] for row in json.loads(MANIFEST.read_text())}
    assert hashlib.sha256(MANIFEST.read_bytes()).hexdigest()==manifest['reference_manifest_sha256'],'delivery reference manifest differs'
    for entry in manifest['entries']:
        source,target=entry['source_path'],entry['delivery_path']
        assert source in approved and entry['source_sha256']==approved[source],source+': derivative uses an unapproved master'
        assert target.startswith('images/delivery-v1/') and '..' not in Path(target).parts,target+': delivery path escapes scope'
        master=(ROOT/'current-site'/source).read_bytes();data=(ROOT/'current-site'/target).read_bytes()
        assert hashlib.sha256(master).hexdigest()==entry['source_sha256'],source+': original master changed'
        assert hashlib.sha256(data).hexdigest()==entry['delivered_sha256'],target+': delivery hash differs'
        assert (ROOT/source).read_bytes()==master and (ROOT/target).read_bytes()==data,target+': source or delivery root mirror differs'
        assert len(master)==entry['source_bytes'] and len(data)==entry['delivered_bytes'],target+': source or delivery byte count differs'
        with Image.open(ROOT/'current-site'/source) as a,Image.open(ROOT/'current-site'/target) as b:
            assert a.size==b.size==tuple(entry['dimensions']) and entry['dimensions_exact'] is True,target+': intrinsic dimensions changed'
            a,b=a.convert('RGBA'),b.convert('RGBA')
            assert ImageChops.difference(a.getchannel('A'),b.getchannel('A')).getbbox() is None and entry['alpha_exact'] is True,target+': alpha pixels changed'
            error=max(pair[1] for pair in ImageChops.difference(a.convert('RGB'),b.convert('RGB')).getextrema())
            assert error==entry['max_rgb_error'] and error<=2,target+': RGB error exceeds the reviewed two-level budget'
    return len(manifest['entries'])

def original(path):
    return subprocess.check_output(['git','show','68dbb96:current-site/'+path],cwd=ROOT)

def expected(path,source):
    if path=='site-system.css':
        assert source.count(b'Agentic consumer intelligence')==1,'site-system.css: operating-layer label differs'
        source=source.replace(b'Agentic consumer intelligence',b'Agentic live selling',1)
    if path in CONTENT['FILES']:
        source=CONTENT['patch'](source,path)
        CONTENT['validate_result'](source,path)
    if path=='client-layout-v3.css':
        css=source.decode()
        substitutions=(
            ('.quality-site .masthead.is-open .masthead-logo{width:180px;height:44px;',
             '.quality-site .masthead.is-open .masthead-logo{width:140px;height:44px;'),
            ('.masthead .masthead-logo img{width:174px;max-height:36px}',
             '.masthead .masthead-logo img{width:auto;height:auto;max-width:100%;max-height:44px}'),
            ('.masthead .masthead-logo img{width:138px;max-width:100%;max-height:30px}',
             '.masthead .masthead-logo img{width:auto;max-width:100%;max-height:44px}'),
        )
        for before,after in substitutions:
            assert css.count(before)==1,'client-layout-v3.css: original logo sizing rule differs'
            css=css.replace(before,after,1)
        source=css.encode()
    if path.endswith('.html'):
        s=source.decode()
        if Path(path).stem in PARAGRAPH_REVISIONS:
            s=revise_paragraph(s,Path(path).stem)
        s=replace_literal_arrows(s,path)
        if path=='solutions.html':
            assert s.count(SOLUTIONS_ACTIONS)==1,path+': unexpected hero actions markup'
            s=s.replace(SOLUTIONS_ACTIONS,'<div class="hero-actions-row">'+SOLUTIONS_ACTIONS+'</div>',1)
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
        s=re.sub(r'(halftone-rendering.js|feedback-v3.css)(?:\?[^"\s]+)?',lambda m:m[1]+'?v='+(RENDERER_CACHE if m[1]=='halftone-rendering.js' else CACHE),s)
        s=apply_image_delivery(s,path)
        s=apply_deferred_images(s,path)
        s=version_logo_urls(s,path)
        # October 27: the three authorized service films sit after each complete
        # hero. Keep the exact additions separate so every original byte still
        # passes the existing source-preservation comparison.
        films=json.loads((ROOT/'scripts/service-films-markup.json').read_text())
        if path in films['sections']:
            # Move the exact existing introduction above its film, with no
            # duplicate copy or changes to the remaining page narrative.
            move=films['moves'][path]
            assert s.count(move['remove'])==1,path+': original film introduction differs'
            s=s.replace(move['remove'],'',1)
            for before,after in move['replacements']:
                assert s.count(before)==1,path+': film follow-up section differs'
                s=s.replace(before,after,1)
            hero=s.index('<section class="page-hero ')
            end=s.index('</section>',hero)+len('</section>')
            s=s[:end]+films['sections'][path]+s[end:]
            s=s.replace('<main id="main">','<main id="main">'+films['filter'],1)
            s=s.replace('</head>',films['stylesheet']+'</head>',1)
            s=s.replace('</body>',films['script']+'</body>',1)
        s=add_case_study(s,path)
        s=add_footer_refinement(s,path)
        s=add_video_refresh(s,path)
        s=add_live_selling_revision(s,path)
        s=add_service_cleanup(s,path)
        source=s.encode()
    return source

def add_case_study(s,path):
    case=json.loads((ROOT/'scripts/case-study-markup.json').read_text())
    for key in ('menu','footer'):
        assert s.count(case[key+'Before'])==1,path+': original case-study navigation anchor differs'
        s=s.replace(case[key+'Before'],case[key+'After'],1)
    if path=='index.html':
        assert s.count(case['anchor'])==1,'homepage case-study anchor differs'
        s=s.replace(case['anchor'],case['section']+case['anchor'],1)
        s=s.replace('</head>',case['imports']+'</head>',1)
        s=s.replace('</body>',case['script']+'</body>',1)
    return s

def add_footer_refinement(s,path):
    marker='data-art-profile="footer"'
    assert s.count(marker)==1,path+': expected one footer artwork profile'
    s=s.replace(marker,marker+' data-art-print="0.34"',1)
    return s.replace('</head>','<link rel="stylesheet" href="footer-refinement.css?v=20261030-footer1"></head>',1)

def add_video_refresh(s,path):
    """Apply only the exact October 30 film-placement and menu edits."""
    patches=json.loads((ROOT/'scripts/video-refresh-markup.json').read_text())
    for before,after in patches.get(path,[]):
        assert s.count(before)==1,path+': October 30 film/menu source anchor differs'
        s=s.replace(before,after,1)
    return s

def add_live_selling_revision(s,path):
    assert s.count('site-system.css?v=20261003-audit1')==1,path+': shared system stylesheet cache key differs'
    s=s.replace('site-system.css?v=20261003-audit1','site-system.css?v=20261030-live-selling1',1)
    changes=json.loads((ROOT/'scripts/live-selling-markup.json').read_text())
    for before,change in changes.get(path,{}).items():
        if before=='_poster':
            assert s.count(change['before'])==1,path+': live-selling poster anchor differs'
            s=s.replace(change['before'],change['after'],1)
        else:
            assert s.count(before)==change['count'],path+': live-selling label count differs'
            s=s.replace(before,change['replacement'])
    return s

def add_service_cleanup(s,path):
    changes=json.loads((ROOT/'scripts/service-cleanup-markup.json').read_text())
    for change in changes.get(path,[]):
        if isinstance(change,dict):
            before,after,count=change['before'],change['after'],change['count']
        else:
            before,after=change
            count=1
        assert s.count(before)==count,path+': service cleanup source anchor differs'
        s=s.replace(before,after,count)
    return s

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
    for name in ('setting','motionPaused','wake','tick','texture','position','updateMapMask','resetMotion'):
        # motionPaused is an arrow expression in the original source.
        if name=='motionPaused':
            same(name,capture(source,r'(const motionPaused=[^\n]+)','motion pause'),
                 capture(baseline,r'(const motionPaused=[^\n]+)','motion pause'))
        else:same(name,function(source,name),function(baseline,name))
    pointer=r'(function stamp\(x,y,radius\)\{[\s\S]*?)(?=\n    canvas.addEventListener\(\'webglcontextlost\')'
    same('pointer / trail / scroll handling',capture(source,pointer,'pointer handling'),capture(baseline,pointer,'pointer handling'))
    fallback="    if(typeof IntersectionObserver!=='function'){state.visible=true;if(field)field.visible=true;state.dirty=true;wake();return;}\n"
    compact=lambda value:re.sub(r'\s+','',value)
    same('visibility with explicit no-observer fallback',compact(function(source,'visibility')),
         compact(function(baseline,'visibility').replace('function visibility(element,state,field){',
                                                'function visibility(element,state,field){'+fallback,1)))
    delegation='    if(isHero){if(field)setupHero(stage,img,field);return;}\n'
    # Delaying creation changes when resources initialize, never their source
    # calculations or draw path. Compare the complete original setup after
    # adding only its exact guard and once-per-near-viewport load wrapper.
    approved_setup=function(baseline,'setup')
    approved_setup=approved_setup.replace('    function initialise(){\n',
        '    let initialised=false;\n    function initialise(){\n'
        '      // A cached image may already be decoded when its viewport gate opens.\n'
        '      // Load and observer notifications must still create only one renderer.\n'
        '      if(initialised||!img.complete||!img.naturalWidth)return;\n'
        '      initialised=true;delete stage.dataset.artDeferred;\n',1)
    load="    if(img.complete&&img.naturalWidth)initialise();else img.addEventListener('load',initialise,{once:true});"
    approved_setup=approved_setup.replace(load,'    nearViewport(stage,()=>{\n  '+load+'\n    });',1)
    same('body artwork setup with viewport scheduling',function(source,'setup').replace(delegation,''),approved_setup)
    scheduler='''
  const deferredStarts=new WeakMap();
  const nearObserver=typeof IntersectionObserver==='function'?new IntersectionObserver(entries=>{
    for(const entry of entries){
      if(!entry.isIntersecting)continue;
      nearObserver.unobserve(entry.target);
      const start=deferredStarts.get(entry.target);deferredStarts.delete(entry.target);
      start?.();
    }
  },{rootMargin:'300px',threshold:0}):null;
  function nearViewport(element,start){
    let started=false;
    const once=()=>{if(started)return;started=true;start();};
    element.dataset.artDeferred='waiting';
    if(!nearObserver){once();return;}
    deferredStarts.set(element,once);nearObserver.observe(element);
  }
'''
    same('once-only near-viewport scheduler',
         capture(source,r'(  const deferredStarts=new WeakMap\(\);[\s\S]*?)(?=  document.querySelectorAll\(\'\[data-site-art\]\'\))','near viewport scheduler').strip(),scheduler.strip())
    loops=capture(source,r'(  document.querySelectorAll\(\'\[data-site-art\]\'\)[\s\S]*?)(?=  window.addEventListener\(\'resize\')','artwork scheduling loops')
    same('hero-immediate / body-map deferred scheduling',loops,
         "  document.querySelectorAll('[data-site-art]').forEach(setup);\n"
         "  document.querySelectorAll('.world-map.dotted-map').forEach(map=>nearViewport(map,()=>{delete map.dataset.artDeferred;heroField(map,true);}));\n")
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
    check_image_loader()
    baseline=original('halftone-rendering.js').decode()
    source=(ROOT/'current-site/halftone-rendering.js').read_text()
    assert not check_renderer(source,baseline),check_renderer(source,baseline)
    for before,after in (("scene:{print:.68","scene:{print:.28"),
                         ('density=.48+weather','density=.12+weather'),
                         ('pointer.z*.11','pointer.z*.01'),
                         ('.19+disturbance','.29+disturbance'),
                         ("rootMargin:'300px'","rootMargin:'30px'"),
                         ('if(initialised||!img.complete||!img.naturalWidth)return;','if(!img.complete||!img.naturalWidth)return;'),
                         ('const once=()=>{if(started)return;started=true;start();};','const once=()=>{start();};'),
                         ('state.visible=true;if(field)field.visible=true;state.dirty=true;wake();return;','return;'),
                         ('clock+=dt','clock+=0'),
                         ("event.pointerType==='touch'||motionPaused()","true||motionPaused()")):
        assert before in source,before
        assert check_renderer(source.replace(before,after,1),baseline),before
    css=(ROOT/'current-site/hero-responsive-fix.css').read_text()
    assert not check_responsive_css(css),check_responsive_css(css)
    assert check_responsive_css(css+'\n@media (min-width:1200px){#main .hero{height:1px}}')
    print('PASS: compositor and scheduling invariants; profile/paper/pointer/clock, scheduling/fallback mutations and unapproved desktop CSS are rejected.')

def check():
    rows=json.loads(MANIFEST.read_text());fail=[]
    derivatives=check_delivery()
    check_image_loader()
    for prefix in ('current-site/',''):
        if (ROOT/(prefix+'_headers')).read_text()!=HEADERS:fail.append(prefix+'_headers: changed outside the exact delivery cache rule')
    for row in rows:
        path=row['path'];source=original(path)
        if hashlib.sha256(source).hexdigest()!=row['sha256'] or not row['matches_git_reference']:
            fail.append(path+': downloaded Vercel source differs from reference')
        if path=='assets/logo.svg':
            logo=(ROOT/'current-site'/path).read_bytes()
            if hashlib.sha256(logo).hexdigest()!=APPROVED_LOGO_SHA256 or len(logo)!=4044:
                fail.append(path+': differs from the exact approved filled pill logo artwork')
            if (ROOT/path).read_bytes()!=logo:fail.append(path+': logo root mirror differs')
            continue
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
    # Preserve the accepted Briefing checkpoint except its explicitly requested
    # shorter paragraph, phone-row import and vector arrow replacement.
    approved=subprocess.check_output(['git','show','9763a3a:current-site/briefing.html'],cwd=ROOT).decode()
    approved=replace_literal_arrows(revise_paragraph(approved,'briefing'),'briefing.html')
    approved=approved.replace('halftone-rendering.js?v='+CACHE,'halftone-rendering.js?v='+RENDERER_CACHE)
    anchor=f'<link rel="stylesheet" href="hero-responsive-fix.css?v={CACHE}">'
    assert approved.count(anchor)==1,'Briefing checkpoint: unexpected responsive CSS import'
    approved=approved.replace(anchor,anchor+f'<link rel="stylesheet" href="mobile-hero-row.css?v={ROW_CACHE}">',1)
    approved=apply_image_delivery(approved,'briefing.html').encode()
    approved=apply_deferred_images(approved.decode(),'briefing.html').encode()
    approved=version_logo_urls(approved.decode(),'briefing.html').encode()
    approved=add_case_study(approved.decode(),'briefing.html').encode()
    approved=add_service_cleanup(add_live_selling_revision(add_video_refresh(add_footer_refinement(approved.decode(),'briefing.html'),'briefing.html'),'briefing.html'),'briefing.html').encode()
    for prefix in ('current-site/',''):
        if (ROOT/(prefix+'briefing.html')).read_bytes()!=approved:
            fail.append(prefix+'briefing.html: changed outside the explicit Briefing checkpoint exceptions')
    for page in ('index','company','solutions','briefing','training'):
        html=(ROOT/'current-site'/f'{page}.html').read_text()
        if 'hero-layout.css' in html or 'site-assets.js' in html or 'images/optimized' in html:
            fail.append(page+': previous adaptive renderer/delivery imports remain')
    if fail:raise SystemExit('\n'.join('FAIL: '+s for s in fail))
    print(f'PASS: {len(rows)} Vercel files and {derivatives} hash/dimension/alpha/RGB-checked derivatives against the explicit allowlist; exact approved filled pill logo artwork and three sizing substitutions; 30 deferred images with exact noscript fallbacks and the hash/behavior-checked hero-first loader; original image masters and other styles/interaction scripts, approved copy including three explicit shorter paragraphs, vector arrows, retained print/weather/pointer calculations, authorized compositor, viewport scheduling and scoped phone/tablet hero layouts. Safari/visual behavior requires separate rendered proof.')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--self-test',action='store_true')
    if parser.parse_args().self_test:self_test()
    else:check()
