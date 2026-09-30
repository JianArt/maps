#!/usr/bin/env python3
"""Writes land.png, the 360x180 land mask the intro globe samples.

One pixel per degree, white is land. Source: Natural Earth 1:110m land.
Run from the repo root: python3 tools/land.py
"""
import json
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SRC = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_land.geojson'
S = 4


def main():
    data = json.load(urllib.request.urlopen(SRC))
    im = Image.new('L', (360 * S, 180 * S), 0)
    draw = ImageDraw.Draw(im)
    for f in data['features']:
        g = f['geometry']
        polys = [g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']
        for poly in polys:
            for k, ring in enumerate(poly):
                pts = [((lon + 180) * S, (90 - lat) * S) for lon, lat in ring]
                draw.polygon(pts, fill=0 if k else 255)
    im = im.resize((360, 180), Image.LANCZOS).point(lambda v: 255 if v > 96 else 0).convert('1')
    im.save(ROOT / 'land.png', optimize=True)
    print('land.png written')


if __name__ == '__main__':
    main()
