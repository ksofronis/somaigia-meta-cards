"""Client review gallery: one before/after tile per unique card, grouped season -> category. Writes review/index.html."""
import json, hashlib, html, collections

SEASONS = ['Χειμερινά', 'Όλο το χρόνο', 'Καλοκαιρινά']
m = json.load(open('manifest.json'))

tiles = {}
for pid, p in m.items():
    t = tiles.setdefault(p['hash'], {**p, 'n': 0})
    t['n'] += 1
groups = collections.defaultdict(list)
for t in tiles.values():
    groups[(t['season'], t['category'])].append(t)

def tile(t):
    o = hashlib.sha1(t['image'].encode()).hexdigest()[:16]
    name = html.escape(t['name']); brand = html.escape(t.get('brand') or '')
    return (f'<figure class="tile" data-q="{html.escape((t["name"] + " " + t["title"]).lower())}" data-g="{html.escape(t["gender"])}" data-s="{html.escape(t["segment"])}">'
            f'<div class="pair"><img loading="lazy" src="o/{o}.jpg" alt="Πριν: {name}" width="210" height="210">'
            f'<a href="../c/{t["hash"]}.jpg" target="_blank" rel="noopener"><img loading="lazy" src="t/{t["hash"]}.jpg" alt="Μετά: {name}" width="210" height="210"></a></div>'
            '<div class="legend"><span>Πριν</span><span>Μετά</span></div>'
            f'<figcaption><a href="{html.escape(t["link"])}" target="_blank" rel="noopener">{name}</a>'
            f'<span>{" · ".join(x for x in (brand, html.escape(t["gender"]), f"{t[chr(110)]} κωδ.") if x)}</span></figcaption></figure>')

nav, body = [], []
for s in SEASONS:
    cats = sorted((c for (ss, c) in groups if ss == s), key=lambda c: -len(groups[(s, c)]))
    if not cats: continue
    total = sum(len(groups[(s, c)]) for c in cats)
    sid = f's{SEASONS.index(s)}'
    nav.append(f'<a href="#{sid}">{s} <b>{total}</b></a>')
    body.append(f'<section class="season" id="{sid}"><h2>{s} <small>{total} κάρτες</small></h2>')
    for i, c in enumerate(cats):
        ts = sorted(groups[(s, c)], key=lambda t: t['name'])
        body.append(f'<details open class="cat"><summary><h3>{html.escape(c)}</h3><small>{len(ts)}</small></summary>'
                    f'<div class="grid">{"".join(tile(t) for t in ts)}</div></details>')
    body.append('</section>')

genders = sorted({t['gender'] for t in tiles.values()})
segs = sorted({t['segment'] for t in tiles.values()})
opt = lambda xs: ''.join(f'<option>{html.escape(x)}</option>' for x in xs)

page = f'''<!doctype html><html lang="el"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow">
<title>Σώμα &amp; Υγεία · Κάρτες καταλόγου</title>
<style>
:root{{--bg:#FAF7F2;--ink:#2B2620;--mute:#7A7064;--line:#E5DCCD;--sand:#E8DFCF;--card:#fff}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}}
header{{position:sticky;top:0;z-index:10;background:var(--bg);border-bottom:1px solid var(--line);padding:14px 16px}}
h1{{font:600 20px/1.2 Georgia,serif;margin:0 0 4px}}header p{{margin:0 0 10px;color:var(--mute);font-size:13px}}
.bar{{display:flex;flex-wrap:wrap;gap:8px;align-items:center}}
.bar a{{padding:6px 12px;border:1px solid var(--line);border-radius:999px;text-decoration:none;color:var(--ink);background:var(--card);font-size:13px}}
.bar input,.bar select{{padding:7px 10px;border:1px solid var(--line);border-radius:8px;font:inherit;font-size:13px;background:#fff;min-height:36px}}
.bar input{{flex:1;min-width:160px}}
main{{max-width:1400px;margin:0 auto;padding:8px 16px 60px}}
h2{{font:600 26px/1.2 Georgia,serif;margin:32px 0 8px;padding-top:8px}}h2 small,summary small{{color:var(--mute);font:400 14px system-ui}}
summary{{cursor:pointer;display:flex;gap:10px;align-items:baseline;padding:10px 0;border-bottom:1px solid var(--line);list-style:none}}
summary h3{{margin:0;font-size:17px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px;padding:14px 0}}
.tile{{margin:0;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}}
.pair{{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--line)}}
.pair img{{width:100%;height:auto;aspect-ratio:1;object-fit:contain;background:#fff;display:block}}
.legend{{display:grid;grid-template-columns:1fr 1fr;padding:4px 10px 0;font-size:11px;color:var(--mute);text-transform:uppercase;letter-spacing:.06em}}
figcaption{{padding:8px 10px;font-size:13px}}figcaption a{{color:var(--ink);text-decoration:none;font-weight:600;display:block}}
figcaption span{{color:var(--mute);font-size:12px}}.hide{{display:none}}
@media (max-width:480px){{.grid{{grid-template-columns:1fr}}}}
</style></head><body>
<header><h1>Κάρτες δυναμικών διαφημίσεων · Πριν / Μετά</h1>
<p>{len(tiles)} κάρτες για {len(m)} κωδικούς παπουτσιών. Αριστερά η σημερινή φωτογραφία, δεξιά η νέα κάρτα. Μεγέθη του ίδιου μοντέλου και χρώματος μοιράζονται μία κάρτα. Πάτημα στη νέα κάρτα: πλήρες μέγεθος.</p>
<div class="bar">{"".join(nav)}
<input id="q" type="search" placeholder="Αναζήτηση μοντέλου ή κωδικού" aria-label="Αναζήτηση">
<select id="g" aria-label="Φύλο"><option value="">Όλα τα φύλα</option>{opt(genders)}</select>
<select id="s" aria-label="Τύπος"><option value="">Όλοι οι τύποι</option>{opt(segs)}</select></div></header>
<main>{"".join(body)}</main>
<script>
const q=document.getElementById('q'),g=document.getElementById('g'),s=document.getElementById('s');
function f(){{const v=q.value.trim().toLowerCase();document.querySelectorAll('.tile').forEach(t=>{{
t.classList.toggle('hide',!((!v||t.dataset.q.includes(v))&&(!g.value||t.dataset.g===g.value)&&(!s.value||t.dataset.s===s.value)))}});
document.querySelectorAll('details.cat').forEach(d=>{{d.classList.toggle('hide',!d.querySelector('.tile:not(.hide)'))}})}}
let tm;q.addEventListener('input',()=>{{clearTimeout(tm);tm=setTimeout(f,200)}});g.onchange=f;s.onchange=f;
</script></body></html>'''
open('review/index.html', 'w').write(page)
print('tiles', len(tiles), 'groups', len(groups))
