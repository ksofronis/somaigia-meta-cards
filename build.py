"""Hourly pipeline: live feed -> shoe taxonomy -> missing cards rendered -> feeds + client review gallery.
  feed/labels.csv  id,custom_label_1..4 (season, category, gender, segment) for Meta product sets; always on
  feed/images.csv  id,image_link; card URLs only after APPROVED exists, first N of rollout order (img_count.txt)
Usage: python3 build.py [--feed local.xml] [--max N]"""
import os, io, sys, csv, json, hashlib, argparse, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from PIL import Image
from classify import classify
import cards
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
FEED = 'https://www.somaigia-shoes.gr/module/xmlfeeds/api?id=8'
BASE = 'https://ksofronis.github.io/somaigia-meta-cards'
NS = {'g': 'http://base.google.com/ns/1.0'}
ap = argparse.ArgumentParser(); ap.add_argument('--feed'); ap.add_argument('--max', type=int, default=80); args = ap.parse_args()
ua = lambda u: urllib.request.Request(urllib.parse.quote(u, safe=':/%?=&'), headers={'User-Agent': 'Mozilla/5.0'})
raw = open(args.feed, 'rb').read() if args.feed else urllib.request.urlopen(ua(FEED), timeout=180).read()
g = lambda it, k: (it.findtext('g:' + k, namespaces=NS) or '').strip()
items = []
for it in ET.fromstring(raw).findall('.//item'):
    c = classify(g(it, 'title'), g(it, 'product_type'), g(it, 'custom_label_0'), g(it, 'brand'))
    if not c: continue
    price = float((g(it, 'sale_price') or g(it, 'price') or '0').split()[0])
    p = dict(id=g(it, 'id'), image=g(it, 'image_link'), name=cards.clean_name(g(it, 'title')), brand=g(it, 'brand'), title=g(it, 'title'),
             ship=price > cards.FREE_SHIP_OVER, usps=[u for u, _ in cards.usps(g(it, 'description'))], link=g(it, 'link'), stock=g(it, 'availability'), **c)
    p['hash'] = cards.content_hash(p); items.append(p)
os.makedirs('feed', exist_ok=True)
with open('feed/labels.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['id', 'custom_label_1', 'custom_label_2', 'custom_label_3', 'custom_label_4'])
    w.writerows([p['id'], p['season'], p['category'], p['gender'], p['segment']] for p in items)

# render cards that do not exist yet (one per content hash: sizes of one model+colour share a card)
os.makedirs('c', exist_ok=True); os.makedirs('review/t', exist_ok=True); os.makedirs('review/o', exist_ok=True); os.makedirs('.cache', exist_ok=True)
bad = json.load(open('bad_images.json')) if os.path.exists('bad_images.json') else {}
todo = {p['hash']: p for p in items if not os.path.exists(f"c/{p['hash']}.jpg") and p['image'] not in bad}
def thumb(im, path, w=420): im = im.copy(); im.thumbnail((w, w), Image.LANCZOS); im.save(path, quality=82)
done = 0
if todo:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(channel='chrome'); pg = b.new_page(viewport={'width': 1080, 'height': 1080})
        for h, p in list(todo.items())[:args.max]:
            u = urllib.parse.urlparse(p['image'])
            if u.scheme != 'https' or u.hostname not in ('www.somaigia-shoes.gr', 'somaigia-shoes.gr'): bad[p['image']] = 'host'; continue
            src = '.cache/' + hashlib.sha1(p['image'].encode()).hexdigest()[:16] + '.jpg'
            try:
                if not os.path.exists(src): open(src, 'wb').write(urllib.request.urlopen(ua(p['image']), timeout=60).read())
                im = Image.open(src)
                if im.mode in ('RGBA', 'LA', 'P'): im = im.convert('RGBA'); bg = Image.new('RGBA', im.size, 'white'); bg.alpha_composite(im); im = bg
                im = im.convert('RGB')
            except Exception as ex: bad[p['image']] = str(ex)[:120]; continue
            png = '.cache/' + h + '.png'; cards.trim_white(im).save(png)
            hf = '.cache/' + h + '.html'; open(hf, 'w').write(cards.card_html(p, cards.uri(png)))
            pg.goto(cards.uri(hf)); pg.evaluate('document.fonts.ready'); shot = pg.screenshot(type='png')
            card = Image.open(io.BytesIO(shot)).convert('RGB'); card.save(f'c/{h}.jpg', quality=88, optimize=True)
            thumb(card, f'review/t/{h}.jpg'); thumb(im, f"review/o/{hashlib.sha1(p['image'].encode()).hexdigest()[:16]}.jpg")
            done += 1
        b.close()
json.dump(bad, open('bad_images.json', 'w'), ensure_ascii=False, indent=0)

# images feed: only cards that exist for the product's current content; gated by APPROVED + rollout count
ready = [p for p in items if os.path.exists(f"c/{p['hash']}.jpg")]
order = [l.strip() for l in open('rollout_order.txt')] if os.path.exists('rollout_order.txt') else []
n = int(open('img_count.txt').read()) if os.path.exists('img_count.txt') else 0
live_ids = set(order[:n]) if os.path.exists('APPROVED') and not os.path.exists('PAUSE') else set()
with open('feed/images.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['id', 'image_link'])
    w.writerows([p['id'], f"{BASE}/c/{p['hash']}.jpg"] for p in ready if p['id'] in live_ids)
json.dump({p['id']: {k: p[k] for k in ('hash', 'image', 'title', 'season', 'category', 'gender', 'segment', 'ship', 'stock', 'link', 'name', 'usps')} for p in items},
          open('manifest.json', 'w'), ensure_ascii=False, indent=0)
print(f'shoes {len(items)} | cards rendered now {done}, pending {max(0, len(todo) - done)}, bad images {len(bad)} | ready {len(ready)} | images.csv rows {len(live_ids & {p["id"] for p in ready})}')
