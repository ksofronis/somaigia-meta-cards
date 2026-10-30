"""Single self-contained gallery file (all thumbnails inline as data URIs) for sending to the client."""
import re, io, base64
from PIL import Image
B = 'https://ksofronis.github.io/somaigia-meta-cards'
s = open('review/index.html').read()
def uri(m):
    im = Image.open('review/' + m.group(1)).convert('RGB'); im.thumbnail((340, 340))
    b = io.BytesIO(); im.save(b, 'JPEG', quality=78, optimize=True)
    return 'src="data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode() + '"'
s, n = re.subn(r'src="((?:o|t)/[0-9a-f]+\.jpg)"', uri, s)
s = s.replace('href="../c/', f'href="{B}/c/')
out = 'Somaigia_Kartes_Prin_Meta.html'
open(out, 'w').write(s); print(n, 'images inlined ->', out)
