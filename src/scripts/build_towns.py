"""Build one static page per town ("Fireworks near Reading") plus sitemap.xml and robots.txt.

Run after build_data.py. Writes into the repo folder given as argv[1] (default: /home/claude/fireworks-forecast).
"""
import json, math, os, sys, datetime, html, re

REPO = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/fireworks-forecast'
SITE = 'https://fireworksforecast.co.uk'
TODAY = os.environ.get('FF_UPDATED') or datetime.date.today().isoformat()
RADIUS = 10

TOWNS = [
    ('Reading', 'RG1'), ('Caversham', 'RG4'), ('Earley', 'RG6'), ('Woodley', 'RG5'), ('Tilehurst', 'RG31'),
    ('Wokingham', 'RG40'), ('Twyford', 'RG10'), ('Bracknell', 'RG12'), ('Binfield', 'RG42'), ('Crowthorne', 'RG45'),
    ('Sandhurst', 'GU47'), ('Ascot', 'SL5'), ('Windsor', 'SL4'), ('Maidenhead', 'SL6'), ('Slough', 'SL1'),
    ('Langley', 'SL3'), ('Marlow', 'SL7'), ('Henley-on-Thames', 'RG9'), ('Newbury', 'RG14'), ('Thatcham', 'RG19'),
    ('Theale', 'RG7'), ('Pangbourne', 'RG8'), ('Hungerford', 'RG17'), ('Camberley', 'GU15'), ('Farnborough', 'GU14'),
    ('Fleet', 'GU51'), ('Yateley', 'GU46'), ('Woking', 'GU22'), ('Egham', 'TW20'), ('High Wycombe', 'HP11'),
    ('Beaconsfield', 'HP9'), ('Gerrards Cross', 'SL9'),
]

ev = json.load(open('/home/claude/data/events_final.json'))
dist = json.load(open('/home/claude/data/districts_named.json'))

def miles(a, b, c, d):
    R = 3958.8
    p1, p2 = math.radians(a), math.radians(c)
    dp, dl = p2 - p1, math.radians(d - b)
    h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(h))

def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')
def e(s): return html.escape(s or '', quote=True)
def nice(d):
    dt = datetime.date.fromisoformat(d)
    return dt.strftime('%A ') + str(dt.day) + dt.strftime(' %B')

STYLE = open('/home/claude/site/plan.html').read().split('<style>')[1].split('</style>')[0]
EXTRA = """
.day{margin-top:22px}
.day h2{font-size:22px;margin:0 0 6px;border-bottom:1.5px solid var(--line);padding-bottom:6px}
.ev{display:grid;grid-template-columns:78px 1fr;gap:12px;padding:11px 0;border-bottom:1px solid #e0e7e0}
.ev:last-child{border-bottom:0}
.time{font:700 20px/1.1 var(--sans);color:#8a5a12}
.time small{display:block;font:400 13px var(--sans);color:var(--moss);margin-top:3px}
.time.unk{font-size:15px;color:var(--pine)}
.ev b{display:block}
.ev .sub{color:var(--moss);font-size:15px}
.ev .evnote{color:#3b4a45;font-size:14.5px;margin-top:3px}
.ev a{font-size:14.5px}
.cta{margin:22px 0;background:#22304f;color:#eef0f5;border-radius:18px;padding:18px 20px}
.cta h2{font-size:22px;margin:0 0 6px;color:#fff}
.cta p{margin:0 0 12px;color:#d8dbe4}
.cta .btn{margin:0 8px 8px 0}
.cta .btn.quiet{background:transparent;color:#fff;border:1.5px solid #4a5a80}
.empty{color:var(--moss)}
.towns{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:15px}
.peaks{margin:0;padding-left:20px;color:#34443f}
"""

LOGO = '''<svg width="34" height="34" viewBox="0 0 40 40" aria-hidden="true"><circle cx="20" cy="20" r="19" fill="#22304f"/><path d="M24.5 9.5a11 11 0 1 0 6 18.6A9 9 0 0 1 24.5 9.5z" fill="#f3efe4"/><g stroke="#f2b44c" stroke-width="2" stroke-linecap="round"><path d="M11 11l2 2M9 17h2.6M14 7.5l.6 2.6"/></g></svg>'''

GC = '''<script>
(function(){ var src=''; try{ var q=new URLSearchParams(location.search); src=q.get('src')||''; }catch(e){}
  window.goatcounter = { path: function(){ return location.pathname; }, referrer: function(){ return src || document.referrer || ''; } }; })();
</script>
<script data-goatcounter="https://fireworksforecast.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>'''

def page(town, code, others):
    lat, lng, _ = dist[code]
    s = slug(town)
    near = []
    for x in ev:
        if x['s'] != 'on' or x['d'] < TODAY:
            continue
        m = miles(lat, lng, x['lat'], x['lng'])
        if m <= RADIUS:
            near.append((x, m))
    near.sort(key=lambda p: (p[0]['d'], p[0]['f'] or p[0]['g'] or '99', p[1]))
    by_day = {}
    for x, m in near:
        by_day.setdefault(x['d'], []).append((x, m))

    days_html = []
    ld = []
    for d, items in by_day.items():
        rows = []
        for x, m in items:
            if x['f']:
                t = f'<div class="time">{e(x["f"])}<small>fireworks{(", gates " + e(x["g"])) if x["g"] else ""}</small></div>'
            elif x['g']:
                t = f'<div class="time unk">After dark<small>gates {e(x["g"])}</small></div>'
            else:
                t = '<div class="time unk">After dark<small>time not published</small></div>'
            link = f'<a href="{e(x["u"])}" rel="noopener nofollow" target="_blank">Organiser or tickets page</a>' if x.get('u') else ''
            note = f'<div class="evnote">{e(x["note"])}</div>' if x.get('note') else ''
            rows.append(f'<div class="ev">{t}<div><b>{e(x["n"])}</b><div class="sub">{e(x["t"])}, {m:.1f} miles from {e(town)}</div>{note}{link}</div></div>')
            start = d + ('T' + x['f'] + ':00' if x['f'] else '')
            when = (f"Fireworks {x['f']}" if x['f'] else 'Fireworks after dark') + (f", gates {x['g']}" if x['g'] else '') + '.'
            about = f"Public fireworks display at {x.get('v') or x['t']}, {x['t']}. {when}" + (f" {x['note']}" if x.get('note') else '')
            ld.append({'@type': 'Event', 'name': x['n'], 'startDate': start, 'endDate': d, 'description': about,
                       'image': [SITE + '/img/scene-1x1.png', SITE + '/img/scene-4x3.png', SITE + '/img/scene-16x9.png'],
                       'eventStatus': 'https://schema.org/EventScheduled',
                       'eventAttendanceMode': 'https://schema.org/OfflineEventAttendanceMode',
                       'location': {'@type': 'Place', 'name': x.get('v') or x['t'], 'address': {'@type': 'PostalAddress', 'addressLocality': x['t'], 'addressCountry': 'GB'}},
                       **({'url': x['u']} if x.get('u') else {})})
        days_html.append(f'<section class="day"><h2>{e(nice(d))}</h2>{"".join(rows)}</section>')

    count = len(near)
    if count:
        lede = (f'{count} public fireworks display{"s" if count != 1 else ""} within {RADIUS} miles of {e(town)} from {e(nice(near[0][0]["d"]))}, '
                'with start times, so you can get the dog walked and settle your pets before the bangs start.')
        body = ''.join(days_html)
    else:
        lede = (f'There are no more public displays listed within {RADIUS} miles of {e(town)} this autumn. '
                "The next big night is New Year's Eve, when fireworks are allowed until 1am.")
        body = '<p class="empty">Join the list below and we will remind you before New Year\'s Eve.</p>'

    title = f'Fireworks near {town} 2026: display times for pet owners'
    desc = f'Every public fireworks display near {town} with start times, so dog and cat owners can plan walks and settle pets before the bangs. Free, updated {nice(TODAY)}.'
    url = f'{SITE}/near/{s}/'
    src = f'town-{s}'
    other_links = ''.join(f'<a href="/near/{slug(o)}/">{e(o)}</a>' for o in others if o != town)
    ld_json = json.dumps({'@context': 'https://schema.org', '@graph': ld}, ensure_ascii=False) if ld else ''
    return s, f'''<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{SITE}/img/share-1200x630.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#eaf0ea">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=Fraunces:opsz,wght,SOFT@9..144,500..700,100&display=swap" rel="stylesheet">
<style>{STYLE}{EXTRA}</style>
{('<script type="application/ld+json">' + ld_json + '</script>') if ld_json else ''}
{GC}
</head>
<body>
<div class="wrap">
  <header>{LOGO}<a class="brand" href="/?src={src}">Fireworks Forecast</a></header>
  <h1>Fireworks near {e(town)}</h1>
  <p class="lede">{lede}</p>
  {body}
  <div class="cta">
    <h2>Join the Quiet Nights list</h2>
    <p>For people whose dog or cat hates fireworks. Get a free Quiet Night plan, a heads-up on the morning of any display near you, and a reminder before New Year's Eve.</p>
    <a class="btn" href="/?src={src}#signupSec">Join the list</a><a class="btn quiet" href="/?src={src}#{code.lower()}">Check your own postcode</a>
  </div>
  <section class="day">
    <h2>Garden fireworks</h2>
    <p class="lede" style="margin:0">Back-garden fireworks aren't listed anywhere. They peak on Bonfire Night, the weekend around it, Diwali (Sunday 8 November) and New Year's Eve. By law they must stop at 11pm, except midnight on Bonfire Night and 1am on Diwali and New Year's Eve.</p>
  </section>
  <section class="day">
    <h2>Fireworks near other towns</h2>
    <div class="towns">{other_links}</div>
  </section>
  <footer>
    <p>Listings are compiled by hand from organiser, council and ticketing pages. Updated {e(nice(TODAY))}. Times can change, so check the organiser's page before you plan around it. Distances are straight-line from the middle of {e(code)}. Not affiliated with any organiser.</p>
    <p>Fireworks Forecast is free and non-commercial, run by a local dog owner.</p>
  </footer>
</div>
</body>
</html>
'''

def main():
    names = [t for t, _ in TOWNS]
    urls = [f'{SITE}/', f'{SITE}/plan.html']
    for town, code in TOWNS:
        assert code in dist, code
        s, doc = page(town, code, names)
        assert '—' not in doc
        os.makedirs(f'{REPO}/near/{s}', exist_ok=True)
        open(f'{REPO}/near/{s}/index.html', 'w').write(doc)
        urls.append(f'{SITE}/near/{s}/')
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f'  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>' for u in urls]
    sm.append('</urlset>')
    open(f'{REPO}/sitemap.xml', 'w').write('\n'.join(sm) + '\n')
    open(f'{REPO}/robots.txt', 'w').write(f'User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n')
    print(len(TOWNS), 'town pages,', len(urls), 'urls in sitemap')

if __name__ == '__main__':
    main()
