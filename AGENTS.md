# maps.jianart.com — notes for agents

Static site on GitHub Pages, the map-work sister of jianart.com (repo `JianArt/site`).
No build step. Everything on `main` deploys live; work on a branch and open a
pull request.

Styles, the hero dot field and reveal animations load from `https://jianart.com/assets/`,
so the two sites share one design system. Follow the rules in `JianArt/site`'s
`AGENTS.md` and `.cursor/rules/jianart-design-system.mdc`. New hero solids belong in
`JianArt/site`'s `data-weather.js`; name one here with `data-shape` on the hero.

The page carries `noindex` until launch; remove it when the site goes live.
