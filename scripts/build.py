"""Gera a versão web do Live Court (GitHub Pages) a partir de src/live-court.html.

Uso (na pasta do projeto):  py scripts/build.py

Produz:
  index.html            página completa, instalável no iPhone/Android/PC
  sw.js                 service worker (abre offline na quadra)
  manifest.webmanifest  nome, cores e ícones do app
  icons/*               ícones PNG e favicon.ico (gerados só se faltarem; use --icons para refazer)
"""
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "live-court.html"
ICONS = ROOT / "icons"

NAVY = (12, 22, 38, 255)
NAVY_2 = (27, 76, 120, 255)
GOLD = (255, 209, 92, 255)
INK = (12, 22, 38, 255)


# ---------- ícones ----------
def _bezier(p0, p1, p2, p3, n=48):
    pts = []
    for i in range(n + 1):
        t = i / n
        a = (1 - t) ** 3
        b = 3 * (1 - t) ** 2 * t
        c = 3 * (1 - t) * t ** 2
        d = t ** 3
        pts.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                    a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return pts


# costuras da bola (mesmo desenho do logo da página, em coordenadas 0..24)
SEAMS = [
    ((12, 1.5), (10.8, 5.7), (12.2, 9.7), (15.2, 12.1)),
    ((22.4, 13.2), (18.6, 11.5), (14.5, 12.1), (11.8, 14.4)),
    ((4.6, 19.6), (6.3, 15.8), (9.2, 13.0), (12.0, 13.4)),
]


def draw_icon(size, maskable=False):
    from PIL import Image, ImageDraw

    ss = 4  # supersampling para bordas suaves
    S = size * ss
    img = Image.new("RGBA", (S, S), NAVY)
    d = ImageDraw.Draw(img)
    # fundo: brilho azul de ginásio
    for r in range(int(S * 0.75), 0, -max(1, S // 120)):
        k = r / (S * 0.75)
        col = tuple(int(NAVY_2[i] * (1 - k) + NAVY[i] * k) for i in range(3)) + (255,)
        d.ellipse([S / 2 - r, S * 0.42 - r, S / 2 + r, S * 0.42 + r], fill=col)
    # bola
    pad = 0.24 if maskable else 0.13
    R = S * (0.5 - pad)
    cx = cy = S / 2
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=GOLD)
    # costuras desenhadas numa camada e recortadas no formato da bola
    seams = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ds = ImageDraw.Draw(seams)
    scale = (2 * R) / 21.0
    ox, oy = cx - 12 * scale, cy - 12 * scale
    w = max(2, int(R * 0.075))
    for seg in SEAMS:
        pts = [(ox + x * scale, oy + y * scale) for x, y in _bezier(*seg)]
        ds.line(pts, fill=INK, width=w, joint="curve")
        for x, y in (pts[0], pts[-1]):
            ds.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=INK)
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).ellipse([cx - R, cy - R, cx + R, cy + R], fill=255)
    img.paste(seams, (0, 0), Image.composite(seams.getchannel("A"), Image.new("L", (S, S), 0), mask))
    d = ImageDraw.Draw(img)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=INK, width=int(R * 0.06))
    return img.resize((size, size), Image.LANCZOS)


def build_icons(force=False):
    ICONS.mkdir(exist_ok=True)
    targets = {
        "icon-192.png": (192, False),
        "icon-512.png": (512, False),
        "icon-maskable-512.png": (512, True),
        "apple-touch-icon.png": (180, True),
    }
    for name, (size, mask) in targets.items():
        p = ICONS / name
        if force or not p.exists():
            draw_icon(size, mask).save(p, optimize=True)
            print("ícone", p.relative_to(ROOT))
    ico = ICONS / "favicon.ico"
    if force or not ico.exists():
        draw_icon(256).save(ico, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
        print("ícone", ico.relative_to(ROOT))


# ---------- página ----------
HEAD_EXTRA = """<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0C1626">
<meta name="description" content="Placar de vôlei do grupo: jogadores, times, quadra com rotação e evolução.">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Live Court">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icons/favicon.ico" sizes="any">
<link rel="icon" type="image/png" href="icons/icon-192.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,-apple-system,'Segoe UI',sans-serif;-webkit-tap-highlight-color:transparent}img{max-width:100%}[hidden]{display:none!important}</style>
"""

SW_REGISTER = """<script>
if ('serviceWorker' in navigator && location.protocol === 'https:') {
  addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));
}
</script>"""

MANIFEST = {
    "name": "Live Court",
    "short_name": "Live Court",
    "description": "Placar de vôlei do grupo",
    "lang": "pt-BR",
    "start_url": "./",
    "scope": "./",
    "display": "standalone",
    "orientation": "any",
    "background_color": "#0C1626",
    "theme_color": "#0C1626",
    "icons": [
        {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}

SW = """// Gerado por scripts/build.py — não edite à mão.
const CACHE = 'live-court-%(version)s';
const SHELL = ['./', 'index.html', 'manifest.webmanifest', 'icons/icon-192.png', 'icons/icon-512.png', 'icons/apple-touch-icon.png', 'icons/favicon.ico'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const req = e.request; if (req.method !== 'GET') return;
  const url = new URL(req.url);
  // página: rede primeiro (pega atualizações), cache se estiver sem internet
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).then(r => { const c = r.clone(); caches.open(CACHE).then(x => x.put('index.html', c)); return r; }).catch(() => caches.match('index.html')));
    return;
  }
  // fontes e arquivos do app: cache primeiro, atualiza em segundo plano
  if (url.origin === location.origin || /fonts\\.(googleapis|gstatic)\\.com$/.test(url.hostname)) {
    e.respondWith(caches.match(req).then(hit => {
      const net = fetch(req).then(r => { if (r.ok || r.type === 'opaque') { const c = r.clone(); caches.open(CACHE).then(x => x.put(req, c)); } return r; }).catch(() => hit);
      return hit || net;
    }));
  }
});
"""


def build_page():
    src = SRC.read_text(encoding="utf-8")
    cut = src.index('<div id="app">')
    head, body = src[:cut], src[cut:]
    # o cabeçalho do arquivo-fonte traz title, fontes e estilos; charset/viewport vêm do HEAD_EXTRA
    head = "\n".join(l for l in head.splitlines()
                     if not l.strip().startswith(('<meta charset', '<meta name="viewport"', '<meta name="claude:')))
    html = ("<!doctype html>\n<html lang=\"pt-BR\">\n<head>\n" + HEAD_EXTRA + head.strip() +
            "\n</head>\n<body>\n" + body.strip() + "\n" + SW_REGISTER + "\n</body>\n</html>\n")
    (ROOT / "index.html").write_text(html, encoding="utf-8", newline="\n")
    version = hashlib.sha1(html.encode("utf-8")).hexdigest()[:10]
    (ROOT / "sw.js").write_text(SW % {"version": version}, encoding="utf-8", newline="\n")
    (ROOT / "manifest.webmanifest").write_text(json.dumps(MANIFEST, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"index.html, sw.js e manifest.webmanifest gerados (versão {version})")


if __name__ == "__main__":
    build_icons(force="--icons" in sys.argv)
    build_page()
