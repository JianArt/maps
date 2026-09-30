#!/usr/bin/env python3
"""Writes index.html from the poster table below.

Colors are sampled from posters/800/<slug>.avif, so adding a print is one row
here plus its two AVIF files. Run from the repo root: python3 tools/build.py
"""
import colorsys
import datetime
import html
import json
import unicodedata
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://maps.jianart.com/'
BLACK = (10, 9, 8)
PAPER = (242, 237, 228)

# slug, city, country, edition, lat, lon
POSTERS = [
    ('abidjan', 'Abidjan', 'Côte d’Ivoire', '', 5.36, -4.01),
    ('accra', 'Accra', 'Ghana', '', 5.6, -0.19),
    ('alexandria', 'Alexandria', 'Egypt', '', 31.2, 29.92),
    ('algiers', 'Algiers', 'Algeria', '', 36.75, 3.06),
    ('amsterdam', 'Amsterdam', 'Netherlands', '', 52.37, 4.9),
    ('amsterdam-2', 'Amsterdam', 'Netherlands', 'Edition II', 52.37, 4.9),
    ('antwerp', 'Antwerp', 'Belgium', '', 51.22, 4.4),
    ('asuncion', 'Asunción', 'Paraguay', '', -25.26, -57.58),
    ('athens', 'Athens', 'Greece', '', 37.98, 23.73),
    ('auckland', 'Auckland', 'New Zealand', '', -36.85, 174.76),
    ('barcelona', 'Barcelona', 'Spain', '', 41.39, 2.17),
    ('barcelona-2', 'Barcelona', 'Spain', 'Edition II', 41.39, 2.17),
    ('bergen', 'Bergen', 'Norway', '', 60.39, 5.32),
    ('bern', 'Bern', 'Switzerland', '', 46.95, 7.45),
    ('bogota', 'Bogotá', 'Colombia', '', 4.71, -74.07),
    ('brasilia', 'Brasília', 'Brazil', '', -15.79, -47.88),
    ('brussels', 'Brussels', 'Belgium', '', 50.85, 4.35),
    ('bucharest', 'Bucharest', 'Romania', '', 44.43, 26.1),
    ('buenos-aires', 'Buenos Aires', 'Argentina', '', -34.6, -58.38),
    ('cairo', 'Cairo', 'Egypt', '', 30.04, 31.24),
    ('cali', 'Cali', 'Colombia', '', 3.45, -76.53),
    ('canberra', 'Canberra', 'Australia', '', -35.28, 149.13),
    ('cape-town', 'Cape Town', 'South Africa', '', -33.92, 18.42),
    ('coimbra', 'Coimbra', 'Portugal', '', 40.21, -8.43),
    ('dakar', 'Dakar', 'Senegal', '', 14.72, -17.47),
    ('fukuoka', 'Fukuoka', 'Japan', '', 33.59, 130.4),
    ('ghent', 'Ghent', 'Belgium', '', 51.05, 3.72),
    ('helsinki', 'Helsinki', 'Finland', '', 60.17, 24.94),
    ('kinshasa', 'Kinshasa', 'DR Congo', '', -4.44, 15.27),
    ('las-vegas', 'Las Vegas', 'United States', '', 36.17, -115.14),
    ('lausanne', 'Lausanne', 'Switzerland', '', 46.52, 6.63),
    ('lisbon', 'Lisbon', 'Portugal', '', 38.72, -9.14),
    ('liverpool', 'Liverpool', 'United Kingdom', '', 53.41, -2.99),
    ('london', 'London', 'United Kingdom', '', 51.51, -0.13),
    ('lucerne', 'Lucerne', 'Switzerland', '', 47.05, 8.31),
    ('madrid', 'Madrid', 'Spain', '', 40.42, -3.7),
    ('marseille', 'Marseille', 'France', '', 43.3, 5.37),
    ('marseille-watercolor', 'Marseille', 'France', 'Watercolor', 43.3, 5.37),
    ('medellin', 'Medellín', 'Colombia', '', 6.24, -75.58),
    ('medellin-2', 'Medellín', 'Colombia', 'Edition II', 6.24, -75.58),
    ('melbourne', 'Melbourne', 'Australia', '', -37.81, 144.96),
    ('mendoza', 'Mendoza', 'Argentina', '', -32.89, -68.83),
    ('merida', 'Mérida', 'Mexico', '', 20.97, -89.62),
    ('mexico-city', 'Mexico City', 'Mexico', '', 19.43, -99.13),
    ('miami', 'Miami', 'United States', '', 25.76, -80.19),
    ('montreal', 'Montréal', 'Canada', '', 45.5, -73.57),
    ('naples', 'Naples', 'Italy', '', 40.85, 14.27),
    ('new-york', 'New York', 'United States', '', 40.71, -74.01),
    ('new-york-2', 'New York', 'United States', 'Edition II', 40.71, -74.01),
    ('nice', 'Nice', 'France', '', 43.7, 7.27),
    ('oslo', 'Oslo', 'Norway', '', 59.91, 10.75),
    ('ottawa', 'Ottawa', 'Canada', '', 45.42, -75.7),
    ('paris', 'Paris', 'France', '', 48.86, 2.35),
    ('philadelphia', 'Philadelphia', 'United States', '', 39.95, -75.17),
    ('philadelphia-76ers', 'Philadelphia', 'United States', '76ers', 39.95, -75.17),
    ('praia', 'Praia', 'Cabo Verde', '', 14.93, -23.51),
    ('quito', 'Quito', 'Ecuador', '', -0.18, -78.47),
    ('rabat', 'Rabat', 'Morocco', '', 34.02, -6.84),
    ('raleigh', 'Raleigh', 'United States', '', 35.78, -78.64),
    ('reykjavik', 'Reykjavík', 'Iceland', '', 64.15, -21.94),
    ('rio-de-janeiro', 'Rio de Janeiro', 'Brazil', '', -22.91, -43.17),
    ('rome', 'Rome', 'Italy', '', 41.9, 12.5),
    ('salta', 'Salta', 'Argentina', '', -24.78, -65.41),
    ('sao-paulo', 'São Paulo', 'Brazil', '', -23.55, -46.63),
    ('sarajevo', 'Sarajevo', 'Bosnia and Herzegovina', '', 43.86, 18.41),
    ('seattle', 'Seattle', 'United States', '', 47.61, -122.33),
    ('seville', 'Seville', 'Spain', '', 37.39, -5.98),
    ('stockholm', 'Stockholm', 'Sweden', '', 59.33, 18.07),
    ('stockholm-2', 'Stockholm', 'Sweden', 'Edition II', 59.33, 18.07),
    ('sydney', 'Sydney', 'Australia', '', -33.87, 151.21),
    ('tokyo', 'Tokyo', 'Japan', '', 35.68, 139.69),
    ('toronto', 'Toronto', 'Canada', '', 43.65, -79.38),
    ('vienna', 'Vienna', 'Austria', '', 48.21, 16.37),
    ('vienna-watercolor', 'Vienna', 'Austria', 'Watercolor', 48.21, 16.37),
    ('washington', 'Washington', 'United States', '', 38.91, -77.04),
    ('zagreb', 'Zagreb', 'Croatia', '', 45.81, 15.98),
    ('zurich', 'Zürich', 'Switzerland', '', 47.38, 8.54),
]


def hexc(c):
    return '#%02x%02x%02x' % tuple(c)


def dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def luminance(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in c)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def dominant(im, n):
    q = im.quantize(colors=n, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()
    total = im.width * im.height
    return [(k / total, tuple(pal[i * 3:i * 3 + 3]))
            for k, i in sorted(q.getcolors(), reverse=True)]


def sample(slug):
    im = Image.open(ROOT / 'posters' / '800' / f'{slug}.avif').convert('RGB')
    w, h = im.size
    ground = dominant(im.crop((int(w * .1), int(h * .08), int(w * .9), int(h * .7))).resize((160, 160)), 6)[0][1]
    title = im.crop((int(w * .26), int(h * .76), int(w * .74), int(h * .84))).resize((240, 60))
    inks = [c for share, c in dominant(title, 5) if share > .03]
    ink = max(inks, key=lambda c: dist(c, ground))
    return ground, ink


def text_on(ground, ink):
    if contrast(ink, ground) >= 4.5:
        return ink
    return max((BLACK, PAPER), key=lambda c: contrast(c, ground))


def pin(ground):
    """A city's color on the globe: its ground, lifted until it reads on black."""
    c = ground
    while contrast(c, BLACK) < 5:
        c = tuple(round(v + (p - v) * .2) for v, p in zip(c, PAPER))
    return c


def hue_key(c):
    r, g, b = (v / 255 for v in c)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    if l < .09:
        return (0, l)
    if l > .9 or s < .12:
        return (2, l)
    return (1, (270 - h * 360) % 360)


def fold(s):
    return unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode().lower()


def coord(lat, lon):
    return '<span>%.2f° %s</span> <span>%.2f° %s</span>' % (abs(lat), 'N' if lat >= 0 else 'S', abs(lon), 'E' if lon >= 0 else 'W')


def main():
    rows = sorted(POSTERS, key=lambda p: (fold(p[1]), p[3]))
    n = len(rows)
    cities = len({p[1] for p in rows})
    data = []
    for i, (slug, city, country, edition, lat, lon) in enumerate(rows):
        ground, ink = sample(slug)
        data.append(dict(i=i, slug=slug, city=city, country=country, edition=edition,
                         lat=lat, lon=lon, g=ground, ink=ink, t=text_on(ground, ink)))
    by_hue = sorted(data, key=lambda d: hue_key(d['g']))
    for rank, d in enumerate(by_hue):
        d['hue'] = rank
    by_lat = sorted(data, key=lambda d: -d['lat'])
    for rank, d in enumerate(by_lat):
        d['north'] = rank

    e = html.escape
    plates, tiles = [], []
    for d in data:
        place = d['country'] + (' · ' + d['edition'] if d['edition'] else '')
        alt = f"Street map poster of {d['city']}, {d['country']}" + (f", {d['edition'].lower()} edition" if d['edition'] and d['edition'] != 'Edition II' else '')
        lazy = '' if d['i'] < 2 else ' loading="lazy"'
        chars = len(d['city'])
        plates.append(f'''      <article class="plate" id="{d['slug']}" style="--g:{hexc(d['g'])};--i:{hexc(d['ink'])};--t:{hexc(d['t'])};--n:{chars}" data-t="{hexc(d['t'])}" data-title="{e(poster_title(d))}">
        <p class="mono plate-no">{d['i'] + 1:03d} / {n:03d}</p>
        <p class="mono plate-geo">{coord(d['lat'], d['lon'])}</p>
        <div class="plate-stage">
          <h2 class="plate-name">{e(d['city'])}</h2>
          <div class="plate-print">
            <img src="/posters/800/{d['slug']}.avif" srcset="/posters/800/{d['slug']}.avif 800w, /posters/1600/{d['slug']}.avif 1600w" sizes="(max-width: 760px) 80vw, 60vh" alt="{e(alt)}" width="800" height="1000"{lazy} decoding="async">
          </div>
        </div>
        <p class="mono plate-place">{e(place)}</p>
        <a class="mono plate-open" href="#index">Index</a>
      </article>''')
        tiles.append(f'''        <li data-az="{d['i']}" data-north="{d['north']}" data-hue="{d['hue']}">
          <a class="tile" href="/{d['slug']}/" style="--g:{hexc(d['g'])}">
            <span class="tile-frame"><img src="/posters/800/{d['slug']}.avif" alt="" width="800" height="1000" loading="lazy" decoding="async"></span>
            <span class="tile-label">
              <span class="tile-city">{e(d['city'])}</span>
              <span class="mono tile-meta">{e(place)}</span>
            </span>
          </a>
        </li>''')
    first = {}
    for d in data:
        first.setdefault(d['city'], d)
    globe = html.escape(';'.join('%g|%g|%s|%s|%s|%s' % (d['lat'], d['lon'], hexc(pin(d['g'])), d['slug'], d['city'], d['country'])
                                 for d in first.values()))
    spectrum = '\n'.join(f'          <li style="--g:{hexc(d["g"])}"></li>' for d in by_hue)

    body = dict(cities=cities, n=n, plates='\n'.join(plates), tiles='\n'.join(tiles),
                spectrum=spectrum, globe=globe)

    def render(title, desc, url, image, image_alt, h1, ld, start=''):
        return TEMPLATE.format(title=e(title), desc=e(desc), url=url, image=image, image_alt=e(image_alt),
                               h1=e(h1), schema=ld, start=start, home_title=e(HOME_TITLE), **body)

    desc = (f'Minimal street map posters of {cities} cities by Jian Adornado, from Lisbon and Tokyo '
            f'to New York and Buenos Aires. {n} prints, each in one color.')
    (ROOT / 'index.html').write_text(render(
        HOME_TITLE, desc, SITE, f'{SITE}posters/share-lisbon.jpg', 'Street map poster of Lisbon, Portugal',
        f'Street map posters of {cities} cities', schema(data, HOME_TITLE, desc)))

    # One page per print: the same scroll, opened at that plate, with its own title and card.
    for d in data:
        share(d['slug'])
        name = poster_name(d)
        city_desc = (f"A minimal street map poster of {d['city']}, {d['country']}"
                     + (f" ({d['edition']})" if d['edition'] else '')
                     + f", by Jian Adornado. One of {n} prints of {cities} cities, each in one color.")
        out = ROOT / d['slug']
        out.mkdir(exist_ok=True)
        (out / 'index.html').write_text(render(
            poster_title(d), city_desc, f"{SITE}{d['slug']}/", f"{SITE}posters/share/{d['slug']}.jpg",
            f"Street map poster of {d['city']}, {d['country']}", name[0].upper() + name[1:],
            artwork(d, city_desc), start=d['slug']))

    (ROOT / 'sitemap.xml').write_text(sitemap(data))
    (ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n')
    print(f'index.html, {n} print pages, sitemap.xml, robots.txt: {n} prints, {cities} cities')


HOME_TITLE = 'City Street Map Posters — Jian Adornado'
ARTIST = {'@type': 'Person', 'name': 'Jian Adornado', 'url': 'https://jianart.com/'}


def poster_name(d):
    return f"{d['city']} street map poster" + (f" ({d['edition']})" if d['edition'] else '')


def poster_title(d):
    return f"{d['city']} Street Map Poster" + (f", {d['edition']}" if d['edition'] else '') + ' — Jian Adornado'


def share(slug):
    """A JPEG copy of the print for link previews, which don't all read AVIF."""
    path = ROOT / 'posters' / 'share' / f'{slug}.jpg'
    if path.exists():
        return
    path.parent.mkdir(exist_ok=True)
    Image.open(ROOT / 'posters' / '800' / f'{slug}.avif').convert('RGB').save(
        path, quality=82, optimize=True, progressive=True)


def artwork(d, desc):
    doc = {
        '@context': 'https://schema.org',
        '@type': 'VisualArtwork',
        'name': poster_name(d),
        'description': desc,
        'url': f"{SITE}{d['slug']}/",
        'image': f"{SITE}posters/1600/{d['slug']}.avif",
        'artform': 'Poster',
        'artMedium': 'Digital print',
        'creator': ARTIST,
        'about': {
            '@type': 'Place',
            'name': f"{d['city']}, {d['country']}",
            'geo': {'@type': 'GeoCoordinates', 'latitude': d['lat'], 'longitude': d['lon']},
        },
        'isPartOf': {'@type': 'CollectionPage', 'name': HOME_TITLE, 'url': SITE},
    }
    return json.dumps(doc, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def schema(data, title, desc):
    """JSON-LD: the page is a gallery, each print a VisualArtwork of a place."""
    artist = ARTIST
    items = [{
        '@type': 'ListItem',
        'position': k + 1,
        'item': {
            '@type': 'VisualArtwork',
            'name': poster_name(d),
            'url': f"{SITE}{d['slug']}/",
            'image': f"{SITE}posters/1600/{d['slug']}.avif",
            'artform': 'Poster',
            'artMedium': 'Digital print',
            'creator': artist,
            'about': {
                '@type': 'Place',
                'name': f"{d['city']}, {d['country']}",
                'geo': {'@type': 'GeoCoordinates', 'latitude': d['lat'], 'longitude': d['lon']},
            },
        },
    } for k, d in enumerate(data)]
    doc = {
        '@context': 'https://schema.org',
        '@type': 'CollectionPage',
        'name': title,
        'description': desc,
        'url': SITE,
        'inLanguage': 'en',
        'author': artist,
        'isPartOf': {'@type': 'WebSite', 'name': 'Jian Adornado', 'url': 'https://jianart.com/'},
        'mainEntity': {'@type': 'ItemList', 'numberOfItems': len(data), 'itemListElement': items},
    }
    return json.dumps(doc, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def sitemap(data):
    today = datetime.date.today().isoformat()
    images = '\n'.join(
        f"    <image:image><image:loc>{SITE}posters/1600/{d['slug']}.avif</image:loc></image:image>"
        for d in data)
    pages = '\n'.join(f'''  <url>
    <loc>{SITE}{d['slug']}/</loc>
    <lastmod>{today}</lastmod>
    <image:image><image:loc>{SITE}posters/1600/{d['slug']}.avif</image:loc></image:image>
  </url>''' for d in data)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
  <url>
    <loc>{SITE}</loc>
    <lastmod>{today}</lastmod>
{images}
  </url>
{pages}
</urlset>
'''


TEMPLATE = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta name="author" content="Jian Adornado">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="theme-color" content="#0a0908">
  <link rel="canonical" href="{url}">
  <link rel="icon" href="https://jianart.com/assets/img/SqNN7K6sQ9od4rxZ4x5qxdmnmo.svg">
  <link rel="sitemap" type="application/xml" href="/sitemap.xml">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Jian Adornado">
  <meta property="og:locale" content="en_US">
  <meta property="og:url" content="{url}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:image" content="{image}">
  <meta property="og:image:type" content="image/jpeg">
  <meta property="og:image:width" content="800">
  <meta property="og:image:height" content="1000">
  <meta property="og:image:alt" content="{image_alt}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{image}">
  <meta name="twitter:image:alt" content="{image_alt}">
  <script type="application/ld+json">
{schema}
  </script>
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-9888HFYBES"></script>
  <script src="/analytics.js?v=2"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Playfair+Display:wght@400;700;800&display=swap">
  <link rel="stylesheet" href="/maps.css?v=atlas26">
</head>
<body data-start="{start}">
  <header class="bar mono">
    <a href="/">Jian Adornado</a>
    <a href="#index">Index</a>
  </header>
  <main>
    <div class="deck">
      <section class="intro" id="top" data-t="#f2ede4" data-title="{home_title}">
        <canvas class="intro-globe" data-cities="{globe}" aria-hidden="true"></canvas>
        <p class="globe-label" aria-hidden="true"><span class="globe-city"></span><span class="mono globe-meta"></span></p>
        <h1 class="sr-only">{h1}</h1>
        <div class="intro-foot">
          <ol class="spectrum" aria-hidden="true">
{spectrum}
          </ol>
        </div>
      </section>
{plates}
    </div>
    <section class="index" id="index" aria-labelledby="index-title">
      <div class="index-head">
        <h2 id="index-title">Index</h2>
        <div class="sorts mono" role="group" aria-label="Sort the index">
          <button type="button" data-sort="az" aria-pressed="true">A–Z</button>
          <button type="button" data-sort="north" aria-pressed="false">North to south</button>
          <button type="button" data-sort="hue" aria-pressed="false">Color</button>
        </div>
      </div>
      <ol class="index-grid">
{tiles}
      </ol>
    </section>
    <footer class="foot">
      <canvas class="foot-globe" data-muted aria-hidden="true"></canvas>
      <ol class="spectrum foot-spectrum" aria-hidden="true">
{spectrum}
      </ol>
      <p class="foot-line">Every city has a signature.</p>
      <a class="foot-mail" href="mailto:jian@jianart.com?subject=A%20city%20map">jian@jianart.com</a>
      <p class="mono foot-meta"><a class="foot-home" href="https://jianart.com/">Portfolio</a><span aria-hidden="true">·</span><span>© 2026 Jian Adornado</span></p>
    </footer>
  </main>
  <script src="/atlas.js?v=atlas12" defer></script>
</body>
</html>
'''

if __name__ == '__main__':
    main()
