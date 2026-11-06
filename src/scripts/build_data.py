import gzip, json, re
from collections import defaultdict
D = json.load(gzip.open('/home/claude/data/uk-address.json.gz','rt'))
pc = {}; sector = defaultdict(lambda:[0,0,0])
for p in D['postcodes']:
    k = p[0].replace(' ','').upper(); pc[k] = (p[1], p[2])
    s = p[0][:-2]; a = sector[s]; a[0]+=p[1]; a[1]+=p[2]; a[2]+=1
districts = json.load(open('/home/claude/data/districts.json'))
ev = json.load(open('/home/claude/data/merged_raw.json'))

fix_pc = {'Wallingford Bonfire and Fireworks (Wallingford 1155)': 'OX10 0DB',
          'Cookham Scouts Bonfire and Fireworks Display': 'SL6 9SR'}
names = {
 'Fireworks Spectacular Family Raceday': 'Ascot Racecourse Fireworks Spectacular Raceday',
 'Halloween Fireworks Night at High Wycombe Cricket Club': 'High Wycombe Cricket Club Halloween Fireworks',
 'Twyford Round Table Bonfire & Fireworks 2026': 'Twyford Round Table Bonfire & Fireworks',
 'Fireworks Night at Wentworth 2026 - Public Access': 'Wentworth Club Fireworks Night',
 'Mapledurham Fireworks Night 2026 (The Club at Mapledurham)': 'The Club at Mapledurham Fireworks Night',
 'Light Up The Sky! (Mytchett Community Association)': 'Light Up The Sky, Mytchett Centre',
 'Bonfire Night at The Barn (Fireworks & Chilli Night)': 'Bottle & Glass Inn Bonfire Night',
 'Chieveley Village Fireworks & Bonfire 2026': 'Chieveley Village Fireworks & Bonfire',
 'Falkland Cricket Club 2026 Fireworks Night': 'Falkland Cricket Club Fireworks Night',
 'Sonning CE Primary Presents Family Fun, Food & Fireworks': 'Sonning CE Primary Fireworks',
 'Fireworks Night at Stripes Maidenhead (Maidenhead United FC)': 'Maidenhead United FC Fireworks Night',
 'The Amazing Fireworks at Amersham & Chiltern Rugby Club': 'Amersham & Chiltern Rugby Club Fireworks',
 'Foxhills Fireworks Night 2026': 'Foxhills Fireworks Night',
 'Dorney Fireworks Night 2026': 'Dorney School Fireworks Night',
 'Fire.FEST Fireworks Maidenhead': 'Fire.FEST, Braywick Park',
 'Beaconsfield Fireworks Display (Little Bang and Big Bang)': 'Beaconsfield Cricket Club Fireworks',
 'Fleet Lions Firework Fiesta 2026': 'Fleet Lions Firework Fiesta',
 'Magic in the Sky - Chalfont St Giles Fireworks & Bonfire': 'Magic in the Sky, Chalfont St Giles',
 'Pangbourne Fireworks Fiesta 2026 (Friends of Pangbourne Primary School)': 'Pangbourne Fireworks Fiesta',
 'Wallingford Bonfire and Fireworks (Wallingford 1155)': 'Wallingford Bonfire & Fireworks',
 'Woking Fireworks Extravaganza 2026': 'Woking Fireworks Extravaganza',
 '1st Lightwater Scouts Bonfire Night 2026': '1st Lightwater Scouts Bonfire Night',
 'Wokingham Charity Fireworks Spectacular 2026': 'Wokingham Charity Fireworks, Cantley Park',
 'Newbury Lions Club Charity Spectacular Fireworks': 'Newbury Lions Fireworks, Newbury Racecourse',
 'Windsor Fireworks Night': 'Royal Windsor Racecourse Fireworks Night',
 'Fireworks & Bonfire Night at The Atrium Health Club': 'The Atrium Health Club Bonfire Night',
 'Reading Football Club Fireworks & Food 2026': 'Reading FC Fireworks & Food',
 'Meath School Fireworks 2026': 'Meath School Fireworks',
 'Farnborough FC Fireworks & Fun Fair 2026': 'Farnborough FC Fireworks & Fun Fair',
 'Stoke Park Bonfire Event 2026': 'Stoke Park Bonfire Night',
 'Bracknell Rugby Club Fireworks 2026': 'Bracknell Rugby Club Fireworks',
 'Lagoona Park Firework Nights 2026 - Fireworks Over the Lake': 'Lagoona Park Fireworks Over the Lake',
}
notes = {
 'Ascot': 'Raceday from late morning. Fireworks after the final race; exact time not published.',
 'Beaconsfield Cricket': 'Two displays: a quieter "Little Bang" at 17:45 and the main display at 19:45.',
 'Wallingford': "Bonfire about 18:30, lower-noise children's display about 19:00, then the main display. Event ends about 20:00.",
 'Wokingham Charity': 'Funfair from 17:30; torchlight procession leaves Market Place at 18:15.',
 'Kempton': 'Time from the organiser page; check nearer the day.',
 'Lambourn': 'Venue and times not yet published.',
 'Marlow Bottom': 'Fireworks between 19:00 and 20:00.',
 'Flackwell': 'Bonfire 18:45. Quieter display for younger children 19:15-19:25, louder display 19:45-20:00 (organiser\'s estimates).',
 'Reading FC': 'Event runs 16:00-20:00.',
 'Fire.FEST': 'Event runs 17:00-20:00.',
 'Maidenhead United': 'Event runs 17:00-21:00.',
 'Dorney': 'Gates 17:00, fireworks 18:00 (confirmed by the organiser). Event ends 19:00.',
 'Foxhills': 'Event runs 17:00-20:00.',
 'Rushmoor': 'Gates 16:00, last entry 19:30. Fireworks, drone and light show about 20:00, ends 21:30.',
 'Sonning CE': 'Event runs 17:30-21:00.',
 'Cove CC': 'Event runs 18:00-23:00.',
 'Cookham': 'Location approximate (Odney Lane).',
 'Spinfield': 'Gates 17:30; fireworks set to music.',
}
out = []
for i, e in enumerate(sorted(ev, key=lambda e:(e['date'], e['fireworks_time'] or '99'))):
    nm = e['name']
    code = fix_pc.get(nm, e.get('postcode'))
    loc = None; lat = lng = None
    if code and code.replace(' ','').upper() in pc:
        lat, lng = pc[code.replace(' ','').upper()]; loc = 'pc'
    elif code and code.split(' ')[0] in districts:
        lat, lng = districts[code.split(' ')[0]]; loc = 'area'
    elif nm.startswith('Lambourn'):
        a = sector['RG17 8']; lat, lng = a[0]/a[2], a[1]/a[2]; loc = 'area'
    assert lat is not None, nm
    clean = names.get(nm) or next((v for k,v in names.items() if nm.startswith(k.split(' (')[0][:28])), None) or nm
    if nm.startswith('Bonfire Night at The Barn'): clean = 'Bottle & Glass Inn Bonfire Night'
    if nm.startswith('Sonning CE Primary'): clean = 'Sonning CE Primary Fireworks'
    if nm.startswith('Magic in the Sky'): clean = 'Magic in the Sky, Chalfont St Giles'
    clean = clean.replace(' 2026','')
    note = next((v for k,v in notes.items() if k.lower() in clean.lower() or k.lower() in nm.lower()), '')
    out.append({'id': i, 'n': clean, 't': e['town'], 'v': e['venue'], 'd': e['date'],
        'f': e['fireworks_time'], 'g': e['gates_time'], 'k': e['kind'], 's': e['status'],
        'u': e['source_url'], 'st': e['source_type'], 'lat': round(lat,5), 'lng': round(lng,5),
        'loc': loc, 'note': note})
    if clean.startswith('Ascot'): out[-1]['g'] = None
    if clean.startswith('Rushmoor'): out[-1]['f'] = '20:00'
    if clean.startswith('Wokingham Charity'): out[-1]['g'] = None
    if clean.startswith('Flackwell'): out[-1]['f'] = '19:15'
    if clean.startswith('Dorney'): out[-1]['f'] = '18:00'; out[-1]['g'] = '17:00'
    if clean.startswith('Magic in the Sky'): out[-1]['g'] = '17:45'; out[-1]['note'] = 'Bonfire 18:15, fireworks about 19:00 (organiser).'
    if clean.startswith('Fire.FEST'): out[-1]['g'] = '17:00'
    if clean.startswith('Woking Fireworks'): out[-1]['u'] = 'https://www.wokingfireworks.org/'; out[-1]['st'] = 'organiser'; out[-1]['note'] = 'Funfair and food from 17:30. Details and tickets on the organiser site.'
json.dump(out, open('/home/claude/data/events_final.json','w'), indent=1)
print(len(out), 'events')
for o in out:
    if not o['note'] and not o['f']: print('NO TIME/NOTE:', o['n'])
