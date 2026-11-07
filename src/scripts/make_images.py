"""Render the hero scene from the page template into share/event images at several aspect ratios."""
import re, subprocess, sys, os
src = sys.argv[1]; outdir = sys.argv[2]
t = open(src).read()
svg = re.search(r'<svg viewBox="0 0 400 250"[\s\S]*?</svg>', t).group(0)
inner = svg[svg.index('>') + 1: svg.rindex('</svg>')]
os.makedirs(outdir, exist_ok=True)
# name: (viewBox x, y, w, h, pixel width, pixel height)
sizes = {
    'scene-16x9.png': (-22, 0, 444, 250, 1200, 675),
    'scene-4x3.png': (0, -25, 400, 300, 1200, 900),
    'scene-1x1.png': (0, -75, 400, 400, 1200, 1200),
    'share-1200x630.png': (-38, 0, 476, 250, 1200, 630),
}
for name, (x, y, w, h, pw, ph) in sizes.items():
    body = inner.replace('<rect width="400" height="250" fill="url(#wall)"/>',
                         f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#wall)"/>')
    body = body.replace('<rect y="214" width="400" height="36" fill="#cbbb98"/>',
                        f'<rect x="{x}" y="214" width="{w}" height="{y + h - 214}" fill="#cbbb98"/>')
    body = body.replace('<path d="M0 214h400"', f'<path d="M{x} 214h{w}"')
    doc = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {w} {h}" width="{pw}" height="{ph}">{body}</svg>'
    p = os.path.join(outdir, name.replace('.png', '.svg'))
    open(p, 'w').write(doc)
    subprocess.run(['rsvg-convert', '-w', str(pw), '-h', str(ph), '-o', os.path.join(outdir, name), p], check=True)
    os.remove(p)
    print(name)
