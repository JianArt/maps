# maps.jianart.com — notes for agents

Static site on GitHub Pages: Jian's street-map posters, a sister to jianart.com
(repo `JianArt/site`). Everything on `main` deploys live; work on a branch and
open a pull request.

It has its own look and shares nothing with jianart.com except the favicon.
Each print gets a full screen in its own ground color, in Playfair Display plus
IBM Plex Mono.

## Adding a print

1. Export two AVIFs from the 1600×2000 source: `sips -s format avif -s formatOptions 50 -Z 1000`
   into `posters/800/<slug>.avif` and `-Z 2000` into `posters/1600/<slug>.avif`.
2. Add a row to `POSTERS` in `tools/build.py` (slug, city, country, edition, lat, lon).
3. Run `python3 tools/build.py`. It samples the ground and ink colors from the
   800px file and rewrites `index.html` (with its JSON-LD), `sitemap.xml` and
   `robots.txt`. Never edit those by hand.

When you change `maps.css` or `atlas.js`, bump its `?v=` in `tools/build.py`.

## Rules

- Screen colors come from the posters. Do not tint or recolor them.
- `prefers-reduced-motion`: plates scroll normally (no sticky stacking) and the
  index re-sorts without animating.
- Check at 390px and 1440px wide before opening a pull request.
