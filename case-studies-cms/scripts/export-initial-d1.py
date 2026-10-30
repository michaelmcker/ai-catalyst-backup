"""Export only a newly seeded CMS database for its first D1 import."""
import sqlite3,json
from pathlib import Path
c=sqlite3.connect('data.db'); c.row_factory=sqlite3.Row
assert c.execute('SELECT count(*) FROM users WHERE disabled=0').fetchone()[0]==0
assert c.execute('SELECT count(*) FROM credentials').fetchone()[0]==0
objects=c.execute("SELECT type,name,tbl_name,sql FROM sqlite_master WHERE sql IS NOT NULL AND name NOT LIKE 'sqlite_%' ORDER BY rowid").fetchall()
virtual={x['name'] for x in objects if x['type']=='table' and 'CREATE VIRTUAL TABLE' in x['sql'].upper()}
def shadow(n): return any(n.startswith(v+'_') for v in virtual)
schema=[x['sql']+';' for x in objects if x['type']=='table' and not shadow(x['name'])]
rows=[]
for x in objects:
 if x['type']!='table' or shadow(x['name']):continue
 name=x['name']
 for row in c.execute('SELECT * FROM "'+name+'"').fetchall():
  values=','.join(c.execute('SELECT quote(?)',(value,)).fetchone()[0] for value in row)
  rows.append('INSERT INTO "'+name+'" VALUES('+values+');')
indexes=[x['sql']+';' for x in objects if x['type'] in ('index','trigger') and not shadow(x['tbl_name'])]
statements=schema+rows+indexes
batches=[]; group=[]; size=0
for s in statements:
 if size+len(s)>45000 and group:batches.append('\n'.join(group));group=[];size=0
 group.append(s);size+=len(s)+1
if group:batches.append('\n'.join(group))
Path('/private/tmp/catalyst-initial-d1.json').write_text(json.dumps(batches))
Path('/private/tmp/catalyst-initial-d1.sql').write_text('\n'.join(statements))
print(json.dumps({'schema':len(schema),'rows':len(rows),'indexes':len(indexes),'batches':len(batches),'bytes':sum(map(len,batches))}))
