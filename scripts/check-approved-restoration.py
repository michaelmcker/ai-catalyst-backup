#!/usr/bin/env python3
"""Lock recovered artwork/effects and approved copy to the verified Vercel backup."""
from pathlib import Path
from html.parser import HTMLParser
import argparse, hashlib, json, re, subprocess
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--shader-revision');args=parser.parse_args()
def git(rev,path):return subprocess.check_output(['git','show',rev+':current-site/'+path],cwd=ROOT)
class Copy(HTMLParser):
    def __init__(self):super().__init__();self.out=[];self.hide=0
    def handle_starttag(self,t,a):
        if t in ('script','style'):self.hide+=1
    def handle_endtag(self,t):
        if t in ('script','style'):self.hide-=1
    def handle_data(self,s):
        if not self.hide and s.strip():self.out.append(re.sub(r'\s+',' ',s.strip()))
def words(s):p=Copy();p.feed(s);return p.out
fail=[];count=0
files=subprocess.check_output(['git','ls-tree','-r','--name-only','68dbb96','current-site'],cwd=ROOT,text=True).splitlines()
for path in files:
    rel=path.removeprefix('current-site/');current=ROOT/path
    if rel.endswith('.html'):
        if words(current.read_text())!=words(git('9bc79bd',rel).decode()):fail.append(rel+': copy differs from verified source plus approved contact/navigation changes')
    elif rel!='halftone-rendering.js':
        rev='9bc79bd' if rel in ('feedback-v3.css','revision-enquiry.js') else '68dbb96'
        if current.read_bytes()!=git(rev,rel):fail.append(rel+': approved source bytes changed')
        count+=1
baseline=git('9bc79bd','halftone-rendering.js').decode()
shader=git(args.shader_revision,'halftone-rendering.js').decode() if args.shader_revision else (ROOT/'current-site/halftone-rendering.js').read_text()
expected=baseline.replace('vec3 v1Paper(vec2 pixels,float t,vec2 size,vec3 pointer){','vec3 v1Paper(vec2 pixels,float t,vec2 size,vec3 pointer,float connected){').replace('float fade=smoothstep(0.,.14,1.-pixels.y/size.y);','float fade=mix(smoothstep(0.,.14,1.-pixels.y/size.y),1.,connected);').replace('v1Paper(worldPixels,clock,fieldSize,pointer)','v1Paper(worldPixels,clock,fieldSize,pointer,connectedPrint)').replace('v1Paper(v*cssSize,clock,cssSize,pointer)','v1Paper(v*cssSize,clock,cssSize,pointer,connectedPrint)').replace('if(removePaper<.5)col=mix(col,backdrop,whiteArea);','if(removePaper<.5)col=mix(col,hero>.5?paper:backdrop,whiteArea);')
# User-requested paper correction: lighten only the common screen and composite
# it in the hero image output, preserving original artwork profiles and motion.
expected=expected.replace('return mix(vec3(1.),vec3(.58,.74,.94),dotInk*fade);',
    '// Paper stays a light blue screen; artwork keeps its authored ink strength.\n      return mix(vec3(1.),vec3(.58,.74,.94),dotInk*fade*.42);')
expected=expected.replace('if(removePaper<.5)col=mix(col,hero>.5?paper:backdrop,whiteArea);',
    '''if(removePaper<.5)col=mix(col,hero>.5?paper:backdrop,whiteArea);
      // Apply the common paper here, in the artwork's own output. Safari does
      // not have to multiply a separate WebGL layer over a masked canvas.
      // Transparent edges reveal the identical field underneath; opaque source
      // paper receives that same field once, with matching world coordinates.
      if(hero>.5)col*=backdrop;''')
for block in ('printing','imageFragment','fieldFragment','mapFragment'):
    extract=lambda s:re.search(r'const '+block+r'=`([\s\S]*?)`;',s).group(1)
    if extract(shader)!=extract(expected):fail.append(block+': differs from recovered shader and explicit full-hero field adaptation')
if re.search(r'const profiles=\{[\s\S]*?\};',shader).group()!=re.search(r'const profiles=\{[\s\S]*?\};',baseline).group():fail.append('approved image profile values changed')
if "gl.uniform1f(u.continuous,['scene','architecture','painting','footer','map'].includes(stage.dataset.artProfile)?1:0)" not in shader:fail.append('image-specific print method missing')
if fail:raise SystemExit('\n'.join('FAIL: '+x for x in fail))
print(f'PASS: all nine approved page texts, {count} original/approved public assets and the recovered print/motion shader.')
