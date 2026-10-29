"""Atelier card template (approved 29.10.2026, sand #E8DFCF shipping band) + USP rules. HTML -> headless Chrome -> 1080x1080 JPEG."""
import os, re, html, hashlib, unicodedata
from urllib.parse import quote
from PIL import Image, ImageChops
HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(HERE, 'assets')
VERSION = 'atelier-sand-1'  # bump on any design change -> every card gets a new URL, Meta re-downloads
FREE_SHIP_OVER = 50.0  # site header: free shipping all Greece over 50 EUR
STORE = [('repeat-2', 'Δωρεάν 1η αλλαγή'), ('map-pin', '3 καταστήματα')]  # return policy page + site footer

def norm(s): return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn')
BADGES = [  # (regex on one accent-free description line, badge); order = priority; only claims stated in the feed
    (r'αποσπωμεν\w* ανατομικ\w* (πατο|πελμα)', 'Αποσπώμενος ανατομικός πάτος'),
    (r'ανατομικ\w* (πατο|πελμα|παταρι)', 'Ανατομικός πάτος'),
    (r'αποσπωμεν\w* (πατο|πελμα)', 'Αποσπώμενος πάτος'),
    (r'γνησι\w* δερμα|φυσικ\w* δερμα', 'Γνήσιο δέρμα'),
    (r'αντικραδασμ', 'Αντικραδασμική σόλα'),
    (r'αντιολισθ', 'Αντιολισθητική σόλα'),
    (r'πλενομεν\w* (πατο|πελμα)', 'Πλενόμενος πάτος'),
    (r'κατασκευ\w* .{0,20}ιταλια|made in italy', 'Made in Italy'),
    (r'3 χρονια εγγυηση', '3 χρόνια εγγύηση'),
    (r'αντιβακτηριδ|αντιμικροβ', 'Αντιβακτηριδιακό'),
    (r'μαλακ\w* δερμα', 'Μαλακό δέρμα'),
]
def usps(desc, n=3):
    hits = {}
    for line in re.split(r'[\n|•]+', desc or ''):
        t = norm(' '.join(line.split()))
        for rx, b in BADGES:
            if b not in hits and re.search(rx, t): hits[b] = line.strip()[:160]
    if 'Ανατομικός πάτος' in hits and 'Αποσπώμενος πάτος' in hits: hits.setdefault('Αποσπώμενος ανατομικός πάτος', hits['Ανατομικός πάτος'])  # stated on two lines
    order = [b for _, b in BADGES if b in hits]
    if 'Αποσπώμενος ανατομικός πάτος' in order: order = [b for b in order if b not in ('Ανατομικός πάτος', 'Αποσπώμενος πάτος')]
    return [(b, hits[b]) for b in order[:n]]
VAR = re.compile(r'\s*,?\s*(?:ΧΡΩΜΑ|Χρώμα|Νούμερο|Μέγεθος|Μεγεθος)\b.*$')
def clean_name(t): return VAR.sub('', t).strip(' ,-')
def trim_white(im):
    box = ImageChops.difference(im, Image.new('RGB', im.size, 'white')).convert('L').point(lambda p: 255 if p > 12 else 0).getbbox()
    return im.crop(box) if box else im
uri = lambda p: 'file://' + quote(os.path.abspath(p))
icon = lambda n: open(os.path.join(A, 'icons', n + '.svg')).read().replace('<svg', '<svg class="ic"', 1)
CSS = f'''@font-face{{font-family:Serif;src:url("{uri(os.path.join(A,'NotoSerifDisplay-var.ttf'))}")}}@font-face{{font-family:Sans;src:url("{uri(os.path.join(A,'Inter-var.ttf'))}")}}
:root{{--ink:#1C1917;--ink2:#44403C;--gold-deep:#8A7444;--bg:#FAFAF9;--sand:#E8DFCF;--line:#D6D3D1}}
*{{box-sizing:border-box;margin:0}}html,body{{width:1080px;height:1080px;overflow:hidden}}body{{font-family:Sans;color:var(--ink);-webkit-font-smoothing:antialiased}}
.card{{width:1080px;height:1080px;display:flex;flex-direction:column;background:var(--bg);padding:0 64px 52px}}
.ph{{flex:1;min-height:0;display:flex;align-items:center;justify-content:center;padding:20px 0}}.ph img{{max-width:100%;max-height:100%;object-fit:contain;mix-blend-mode:multiply}}
.ic{{width:1em;height:1em;flex:none;stroke-width:1.6}}
.ship{{margin:0 -64px;height:92px;background:var(--sand);color:var(--ink);display:flex;align-items:center;justify-content:center;gap:18px;font:600 34px/1 Sans;letter-spacing:.16em;text-transform:uppercase}}.ship .ic{{color:var(--gold-deep);font-size:44px}}
.head{{padding-top:48px}}.kick{{font:600 28px/1 Sans;letter-spacing:.22em;text-transform:uppercase;color:var(--gold-deep)}}.name{{margin-top:14px;font:500 64px/1.08 Serif;letter-spacing:-.01em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.foot{{border-top:1.5px solid var(--line);padding-top:26px;display:flex;justify-content:space-between;gap:24px}}
ul{{list-style:none;padding:0;display:grid;gap:12px}}li{{display:flex;align-items:center;gap:14px;font:500 36px/1.15 Sans;color:var(--ink2);white-space:nowrap}}li .ic{{color:var(--gold-deep);font-size:36px;stroke-width:2.2}}
.side li{{font:500 28px/1.15 Sans;justify-content:flex-end}}.side li .ic{{font-size:28px}}'''
FIT = '''<script>document.querySelectorAll('.name').forEach(e=>{let s=parseFloat(getComputedStyle(e).fontSize);while(e.scrollWidth>e.clientWidth&&s>40){s-=1;e.style.fontSize=s+'px'}})</script>'''
e = html.escape
def card_html(p, img_uri):
    ship = f'<div class="ship">{icon("truck")}Δωρεάν μεταφορικά</div>' if p['ship'] else ''
    lis = ''.join(f'<li>{icon("check")}{e(u)}</li>' for u in p['usps'])
    side = ''.join(f'<li>{icon(i)}{e(t)}</li>' for i, t in STORE)
    kick = f'<div class="kick">{e(p["brand"])}</div>' if p['brand'] else ''
    return (f'<!doctype html><html lang="el"><meta charset="utf-8"><style>{CSS}</style><div class="card">{ship}<div class="head">{kick}'
            f'<div class="name">{e(p["name"])}</div></div><div class="ph"><img src="{img_uri}"></div><div class="foot"><ul>{lis}</ul><ul class="side">{side}</ul></div></div>{FIT}')
def content_hash(p):
    return hashlib.sha1('|'.join([VERSION, p['image'], p['name'], p['brand'], str(p['ship']), *p['usps']]).encode()).hexdigest()[:12]
