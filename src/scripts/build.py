import json, sys, os, datetime
cfg_path = sys.argv[1] if len(sys.argv) > 1 else None
out_path = sys.argv[2] if len(sys.argv) > 2 else '/home/claude/site/index.html'
cfg = json.load(open(cfg_path)) if cfg_path else {"signup": {}, "addDisplayUrl": "", "siteUrl": "", "contactEmail": ""}
t = open('/home/claude/site/template.html').read()
ev = json.load(open('/home/claude/data/events_final.json'))
dist = json.load(open('/home/claude/data/districts_named.json'))
t = t.replace('/*__CONFIG__*/{}', json.dumps(cfg))
t = t.replace('/*__EVENTS__*/[]', json.dumps(ev, separators=(',',':'), ensure_ascii=False))
t = t.replace('/*__DISTRICTS__*/{}', json.dumps(dist, separators=(',',':'), ensure_ascii=False))
t = t.replace('/*__CHECKED__*/', os.environ.get('FF_UPDATED') or datetime.date.today().isoformat())
assert '/*__' not in t
open(out_path, 'w').write(t)
print(out_path, len(t)//1024, 'KB')
