# Haigh Communications — website

Clean static rebuild of https://haigh.group (previously WordPress + Elementor).
Plain HTML, one stylesheet, one small script. No frameworks, no build step needed to host it.

## Hosting
Upload everything **except `_build/`** to any static host (GitLab/GitHub Pages, Netlify, Cloudflare Pages, Apache/Nginx).
`.gitlab-ci.yml` is included for GitLab Pages; `404.html` is picked up automatically by most hosts.

Old URLs are kept, so existing links and search results still work:
`/our-case-studies/`, `/portfolio/<case-study>/`, `/blog/`, `/<post-slug>/`.

## Editing
Small text fixes: edit the HTML files directly.

For anything bigger, edit the source and regenerate (needs Python 3 + Pillow):

```
pip install pillow
python3 _build/build.py
```

- `_build/build.py` — home page copy (services, packages, clients, team, contact details) and page templates
- `_build/content.json` — case studies and news posts
- `_build/source-images/` — original photos; resized copies are written to `assets/img/`

To add a news post: add an entry to `posts` in `content.json`, add its category and cover image to `POST_META` in `build.py`, then rebuild.

## Structure
```
index.html                     home
our-case-studies/              case study list
portfolio/<slug>/              5 case studies
blog/                          news list
<post-slug>/                   4 news posts
404.html
assets/css/site.css            all styles (colour + type tokens at the top)
assets/js/site.js              mobile menu + photo lightbox
assets/fonts/                  self-hosted Bricolage Grotesque + Source Serif 4 (SIL OFL)
assets/img/  assets/media/     optimised images, QEH video (720p)
```

## Design
- Colours: ink `#1f1d36`, logo orange `#dd6123`, sun `#f2ae1c`, mist `#f4f3f8`
- Type: Bricolage Grotesque (headings), Source Serif 4 (text)
- The logo is redrawn as SVG from the original mark; its orange line construction is reused around the hero portrait.
