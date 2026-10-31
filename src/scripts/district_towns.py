import gzip, json
from collections import defaultdict, Counter
D = json.load(gzip.open('/home/claude/data/uk-address.json.gz','rt'))
towns, streets = D['towns'], D['streets']
cnt = defaultdict(Counter); acc = defaultdict(lambda:[0,0,0])
for p in D['postcodes']:
    d = p[0].split(' ')[0]
    a = acc[d]; a[0]+=p[1]; a[1]+=p[2]; a[2]+=1
    if p[3]:
        cnt[d][towns[streets[p[3][0]][1]]] += 1
out = {}
for d,a in acc.items():
    t = cnt[d].most_common(1)[0][0] if cnt[d] else ''
    out[d] = [round(a[0]/a[2],4), round(a[1]/a[2],4), t]
json.dump(out, open('/home/claude/data/districts_named.json','w'), separators=(',',':'))
for k in ['SL6','SL4','RG1','RG40','HP9','GU22','SW1A','M1','EH1']: print(k, out.get(k))
print(len(out))
