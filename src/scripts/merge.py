import gzip, json, glob, re, sys, math
from collections import defaultdict
D = json.load(gzip.open('/home/claude/data/uk-address.json.gz','rt'))
pc = {}
dist_acc = defaultdict(lambda: [0.0,0.0,0])
for p in D['postcodes']:
    code, lat, lng = p[0], p[1], p[2]
    pc[code.replace(' ','').upper()] = (lat, lng)
    d = code.split(' ')[0]
    a = dist_acc[d]; a[0]+=lat; a[1]+=lng; a[2]+=1
districts = {d: (round(a[0]/a[2],4), round(a[1]/a[2],4)) for d,a in dist_acc.items() if a[2]}
# town centroid fallback: from streets' town index -> use postcodes? use district of event town via known map below
events = []
for f in sorted(glob.glob('/home/claude/data/events_*.json')):
    for e in json.load(open(f)):
        e['_file'] = f.split('events_')[1][:-5]
        events.append(e)
print('total rows', len(events))
missing = []
for e in events:
    code = (e.get('postcode') or '').replace(' ','').upper()
    if code and code in pc:
        e['lat'], e['lng'] = pc[code]; e['loc'] = 'postcode'
    elif code and len(code) >= 5 and code[:-3] in districts:
        e['lat'], e['lng'] = districts[code[:-3]]; e['loc'] = 'district'
        missing.append((e['name'], e.get('postcode'), 'postcode not found, used district'))
    else:
        e['lat'] = e['lng'] = None; e['loc'] = None
        missing.append((e['name'], e.get('postcode'), e['town']))
for m in missing: print('NOLOC', m)
json.dump(events, open('/home/claude/data/merged_raw.json','w'), indent=1)
json.dump(districts, open('/home/claude/data/districts.json','w'), separators=(',',':'))
print('districts', len(districts))
