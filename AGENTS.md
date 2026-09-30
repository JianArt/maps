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

## Scheduled agents

Preview locally with `python3 -m http.server 5192` and open http://127.0.0.1:5192/.

**Site Health** (daily) may push straight to `main` for objective fixes only:
broken links or images, missing alt text, heading order, missing or wrong meta
tags, JSON-LD or sitemap errors, console errors. If the fix belongs in generated
output, change `tools/build.py` and rerun it rather than editing the output.
Before pushing, load `/` and one city page (for example `/lisbon/`) at 390px
and 1440px with no console errors and nothing visibly different except the fix.
Anything that changes the look, the copy or a poster goes through a pull request
instead. Commit message: `Site Health: <fix>`.

**Elegance Review** (weekly) never pushes to `main`; it always opens a pull request.

For every agent:

- One topic per commit or pull request, small enough to review in a few minutes.
- Titles and commit messages start with the agent's name.
- Pull requests include before and after screenshots for anything visual, and
  put judgement calls in the description as suggestions instead of making them.
- If your previous pull request is still open, do not open another one.
- If a direct push would conflict with `main`, stop and open a pull request.
- Never add, remove, re-export or recolor a poster, and never change the
  Google Analytics ID.
