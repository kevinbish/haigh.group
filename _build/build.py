"""Generate the Haigh Communications static site.

Usage:  python3 _build/build.py            (run from the repo root)
Content lives in _build/content.json (posts + case studies) and in the
PAGE data below (home page copy, team, services).
Source images are read from _build/source-images/ and written, resized, to assets/img/.
"""
import html, json, os, re, shutil
from datetime import datetime
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_IMG = os.path.join(ROOT, "_build", "source-images")
OUT_IMG = os.path.join(ROOT, "assets", "img")
SITE_URL = "https://haigh.group"
YEAR = datetime.now().year
e = html.escape

# ----------------------------------------------------------------- images
_done = {}
def image(rel, max_w=1400, thumb_w=720):
    """rel = path under source-images. Returns (full, thumb) paths relative to site root."""
    if rel in _done:
        return _done[rel]
    src = os.path.join(SRC_IMG, rel)
    im = Image.open(src)
    has_alpha = False
    if im.mode in ("RGBA", "LA", "P"):
        alpha = im.convert("RGBA").split()[3]
        has_alpha = alpha.getextrema()[0] < 250          # only keep PNG when there is real transparency
    base = os.path.splitext(os.path.basename(rel))[0].lower()
    if re.fullmatch(r"[\d_-]+|img[_-]?\d+", base):        # generic camera/number names: prefix the upload month
        base = rel[:7].replace("/", "-") + "-" + base
    stem = re.sub(r"[^a-z0-9]+", "-", base).strip("-")[:60]
    ext = ".png" if has_alpha else ".jpg"
    out = {}
    for tag, w in (("", max_w), ("-sm", thumb_w)):
        name = f"{stem}{tag}{ext}"
        path = os.path.join(OUT_IMG, name)
        if not os.path.exists(path):
            copy = im.convert("RGBA" if has_alpha else "RGB")
            copy.thumbnail((w, w * 3))
            if has_alpha:
                copy.save(path, optimize=True)
            else:
                copy.save(path, quality=76, optimize=True, progressive=True)
        out[tag] = f"assets/img/{name}"
    _done[rel] = (out[""], out["-sm"])
    return _done[rel]

def size(rel_out):
    with Image.open(os.path.join(ROOT, rel_out)) as im:
        return im.size

# ----------------------------------------------------------------- shared bits
LOGO = """<svg viewBox="0 0 206 58" role="img" aria-label="Haigh Communications"><g class="bars" stroke-width="3.4" fill="none" stroke-linecap="square">
<path d="M33 2v24M33 31v25M52 2v54M33 28.5h41M52 54.5h21"/></g>
<g fill="currentColor" font-family="Rubik, 'Century Gothic', sans-serif" font-weight="700">
<text x="63" y="19" font-size="16" letter-spacing=".6">AIGH</text>
<text x="61" y="48.5" font-size="12.4" letter-spacing=".4">OMMUNICATIONS</text>
<text x="35" y="55" font-size="4.6" font-weight="500" letter-spacing=".3">INC</text></g></svg>"""

ICON = {
    "whatsapp": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.6.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.7-1.4.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6a2.7 2.7 0 0 0 1.8-1.3 2.2 2.2 0 0 0 .1-1.3c0-.1-.2-.2-.5-.3z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" d="M3 5h18v14H3zM3 6l9 7 9-7"/></svg>',
    "phone": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" d="M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 5a2 2 0 0 1 2-2z"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5" fill="none" stroke="currentColor" stroke-width="2"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" aria-hidden="true"><path stroke="currentColor" stroke-width="2" d="M3 7h18M3 12h18M3 17h18"/></svg>',
}
PHONE_DISPLAY, PHONE_TEL, WHATSAPP = "+1 246 836 4629", "+12468364629", "https://wa.me/12468364629"
EMAIL = "info@haigh.group"
ADDRESS = "#33 Union Park, St. Philip, Barbados"
SOCIAL = [("Facebook", "https://www.facebook.com/haighcommunications"),
          ("Instagram", "https://www.instagram.com/haighcommbb/"),
          ("LinkedIn", "https://www.linkedin.com/company/haigh-communications/about/"),
          ("X (Twitter)", "https://twitter.com/HaighComm")]
NAV = [("Work", "our-case-studies/"), ("Services", "#services"), ("News", "blog/"),
       ("Team", "#team"), ("Contact", "#contact")]

DOTS = '<div class="dots" aria-hidden="true">' + "<i></i>" * 8 + "</div>"

def page(path, title, desc, body, current=None, og_image=None):
    depth = path.count("/")
    r = "../" * depth                      # relative root
    canon = SITE_URL + "/" + (path[:-len("index.html")] if path.endswith("index.html") else path)
    nav = []
    for label, href in NAV:
        h = (r + "index.html" + href) if href.startswith("#") else r + href + "index.html"
        if href.startswith("#") and depth == 0:
            h = href
        cur = ' aria-current="page"' if current == label else ""
        nav.append(f'<a href="{h}"{cur}>{label}</a>')
    contact_href = "#contact" if depth == 0 else r + "index.html#contact"
    og = SITE_URL + "/" + (og_image or "assets/img/og-default.jpg")
    full_title = title if title.startswith("Haigh") else f"{title} – Haigh Communications"
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Haigh Communications Inc">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{og}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@HaighComm">
<meta name="theme-color" content="#3b3663">
<link rel="icon" href="{r}assets/img/favicon.svg" type="image/svg+xml">
<link rel="preload" href="{r}assets/fonts/rubik-wght.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{r}assets/css/site.css">
<script defer src="{r}assets/js/site.js"></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-head">
  <div class="wrap">
    <a class="logo" href="{r}index.html">{LOGO}</a>
    <button class="menu-btn" aria-controls="nav" aria-expanded="false" aria-label="Open menu">{ICON['menu']}</button>
    <nav id="nav" class="nav" aria-label="Main">{''.join(nav)}</nav>
    <a class="btn dark head-cta" href="{WHATSAPP}">{ICON['whatsapp']}{PHONE_DISPLAY}</a>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-foot{'' if path == 'index.html' else ' plain'}">
  <div class="wrap">
    <a class="logo" href="{r}index.html">{LOGO}</a>
    <div class="social">{''.join(f'<a href="{u}">{n}</a>' for n, u in SOCIAL)}</div>
    <div>© {YEAR} Haigh Communications Inc. · <a href="{contact_href}">Contact</a></div>
  </div>
</footer>
</body>
</html>
"""
    out = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(out) or ROOT, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)

def picture(full, thumb, alt, sizes="100vw", cls="", lazy=True, r=""):
    w, h = size(full)
    tw, _ = size(thumb)
    load = ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"'
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="{r}{full}" srcset="{r}{thumb} {tw}w, {r}{full} {w}w" sizes="{sizes}" '
            f'width="{w}" height="{h}" alt="{e(alt)}"{load}>')

def fmt_date(iso):
    d = datetime.fromisoformat(iso)
    return d.strftime("%-d %B %Y"), d.strftime("%Y-%m-%d")

# ----------------------------------------------------------------- content
C = json.load(open(os.path.join(ROOT, "_build", "content.json"), encoding="utf-8"))

CASE_META = {   # client, summary, cover image — order = order on the site
    "the-golden-square-freedom-park": ("Barbados Tourism Investment Inc.",
        "Supporting almost 100 vendors through their relocation from the old NIS building, with dislocation grants and business workshops.",
        "2021/02/Workers-from-the-Ministry-of-Transport-Works-and-Maintenance-seen-removing-stop-lights-from-the-location.jpg"),
    "halls-road-case-study": ("Barbados Tourism Investment Inc.",
        "Public relations for the final phase of the Constitution River upgrade, Bridgetown’s main drainage channel, from ground-breaking to community notices.",
        "2019/07/Halls-Road-Flood-MitigationII.jpg"),
    "salt-pond-project-phase-ii": ("Barbados Tourism Investment Inc.",
        "Communications for the CDB-financed Speightstown flood mitigation project, including site visits and progress updates.",
        "2021/02/IMG_1882.jpg"),
    "the-national-tree-planting-project": ("National Tree Planting Project",
        "Taking the national tree-planting drive into schools through planting exercises, Arbofest 2020 and creative media.",
        "2021/03/Trees-Photo.png"),
    "qeh-accident-emergency": ("Queen Elizabeth Hospital",
        "Keeping patients, staff and the public informed while the Accident & Emergency department was rebuilt.",
        "2021/03/Queen-Elizabeth-Hospital.jpg"),
}
POST_META = {
    "operation-seek-and-save-donation": ("Special projects", "2021/02/Operation-Seek-and-Save-Water-Donation.jpeg"),
    "tablets-donated": ("Special projects", "2020/08/wiltshireweb.jpg"),
    "haigh-on-board": ("Marketing", "2020/08/1-1-768x368-1.jpg"),
    "work-underway": ("Planning", "2020/08/1DSC_4634.jpg"),
}
cases = sorted(C["cases"], key=lambda c: list(CASE_META).index(c["slug"]))
posts = sorted(C["posts"], key=lambda p: p["date"], reverse=True)

def src_rel(p):
    return p.split("wp-content/uploads/", 1)[-1]

def summary(body, n=170):
    for b in body:
        if b["type"] == "p":
            t = b["text"]
            return t if len(t) <= n else t[:n].rsplit(" ", 1)[0] + "…"
    return ""

def render_body(body, r, slug):
    out, i, in_list = [], 0, False
    for b in body:
        t = b["type"]
        if t != "li" and in_list:
            out.append("</ul>"); in_list = False
            if slug == "qeh-accident-emergency":
                poster, _ = image("2021/03/QEH-Progress-Report.mp4_snapshot_00.09.192.jpg")
                out.append(f'<figure class="wide"><video controls preload="none" poster="{r}{poster}" '
                           f'src="{r}assets/media/qeh-progress-report.mp4"></video>'
                           f'<figcaption class="source">A&amp;E renovation progress report, March 2021</figcaption></figure>')
        if t == "quote" and "View this post on Instagram" in b["text"]:
            continue
        if t == "p":
            cls = ' class="source"' if b["text"].lower().startswith("source:") else ""
            out.append(f"<p{cls}>{e(b['text'])}</p>")
        elif t == "h":
            out.append(f"<h2>{e(b['text'])}</h2>")
        elif t == "quote":
            out.append(f"<blockquote><p>{e(b['text'])}</p></blockquote>")
        elif t == "li":
            if not in_list:
                out.append("<ul>"); in_list = True
            out.append(f"<li>{e(b['text'])}</li>")
        elif t == "img":
            g = b["imgs"][0]
            full, th = image(src_rel(g["src"]))
            out.append(f'<figure>{picture(full, th, g["alt"] if not g["alt"].startswith("IMG_") else "", "(max-width: 700px) 100vw, 672px", r=r)}</figure>')
        elif t == "gallery":
            items = []
            for g in b["imgs"]:
                full, th = image(src_rel(g["src"]))
                alt = "" if g["alt"].startswith("IMG_") else g["alt"]
                items.append(f'<a href="{r}{full}"><img src="{r}{th}" alt="{e(alt) or "Project photo"}" loading="lazy" decoding="async"></a>')
            out.append(f'<div class="gallery">{"".join(items)}</div>')
    if in_list:
        out.append("</ul>")
    return "\n".join(out)

# ----------------------------------------------------------------- favicon + og
os.makedirs(OUT_IMG, exist_ok=True)
with open(os.path.join(OUT_IMG, "favicon.svg"), "w") as f:
    f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="6" fill="#1f1d36"/>'
            '<path d="M9 5v10M9 18v10M17 5v23M9 16.5h16M17 26.5h9" stroke="#dd6123" stroke-width="3" fill="none"/></svg>')
from PIL import ImageFilter
def hero_cutout():
    """Original hero is a circle crop with a pink ring. Take the largest clean circle inside it
    (centre 525,430 r 430 in the 958x995 source) and save as a transparent WebP."""
    from PIL import ImageDraw
    im = Image.open(os.path.join(SRC_IMG, "2020/08/home_03_img_01-re.png")).convert("RGBA")
    cx, cy, r = 525, 430, 430
    im = im.crop((cx - r, cy - r, cx + r, cy + r))
    big = Image.new("L", (r * 8, r * 8), 0)
    ImageDraw.Draw(big).ellipse((0, 0, r * 8 - 1, r * 8 - 1), fill=255)
    im.putalpha(big.resize(im.size, Image.LANCZOS))
    out = []
    for name, w in (("joyann-haigh.webp", 860), ("joyann-haigh-sm.webp", 520)):
        c = im.copy(); c.thumbnail((w, w)); c.save(os.path.join(OUT_IMG, name), quality=82, method=6)
        out.append(f"assets/img/{name}")
    return out
hero_full, hero_th = hero_cutout()
og = Image.open(os.path.join(SRC_IMG, "2020/08/home_03_img_01-re.png")).convert("RGB")
og = og.crop((0, 160, og.width, 160 + int(og.width / 1.91))).resize((1200, 628))
og.save(os.path.join(OUT_IMG, "og-default.jpg"), quality=82)

# ----------------------------------------------------------------- home
case_cards = []
for i, c in enumerate(cases):
    client, summ, cover = CASE_META[c["slug"]]
    full, th = image(cover)
    lead = i == 0
    case_cards.append(f"""<article{' class="lead"' if lead else ''}>
  <a class="card" href="portfolio/{c['slug']}/index.html">
    <div class="thumb">{picture(full, th, '', '(max-width: 760px) 100vw, 700px' if lead else '(max-width: 760px) 100vw, 560px')}</div>
  </a>
  <div>
    <div class="client">{e(client)}</div>
    <a class="card" href="portfolio/{c['slug']}/index.html"><h3>{e(c['title'])}</h3></a>
    <p>{e(summ)}</p>
  </div>
</article>""")

def news_items(posts, r):
    items = []
    for p in posts:
        cat, cover = POST_META[p["slug"]]
        full, th = image(cover)
        human, iso = fmt_date(p["date"])
        items.append(f"""<li><a href="{r}{p['slug']}/index.html">
  <img src="{r}{th}" alt="" loading="lazy" decoding="async" width="{size(th)[0]}" height="{size(th)[1]}">
  <div><h3>{e(p['title'])}</h3><p>{e(summary(p['body'], 140))}</p></div>
  <time datetime="{iso}">{human}</time></a></li>""")
    return "\n".join(items)

SERVICE_ICONS = {"Media relations": "06", "Crisis communications": "07", "Brand positioning & messaging": "08",
                 "Social media marketing": "04", "Thought leadership": "05", "Content marketing": "09"}
SERVICES = [
    ("Media relations", "Earned media builds thought leadership and can be repurposed to strengthen sales, SEO, social media, online reputation and conference communications."),
    ("Crisis communications", "Crisis planning, issues management and response, handled by PR professionals with deep media relations and corporate communications experience."),
    ("Brand positioning & messaging", "Positioning and messaging that sets you apart, engages stakeholders and lays the foundation for every marketing, PR and communications initiative."),
    ("Social media marketing", "Social media fuelled by credible, engaging content strengthens SEO, online reputation, direct marketing and conference marketing — for B2B businesses too."),
    ("Thought leadership", "Become a recognised voice through influencer and content marketing, earned media, speaking, PR surveys, white papers, videos and webinars."),
    ("Content marketing", "Thought leadership articles, social posts, email campaigns, video, photography and internal and external communications that drive and nurture leads."),
]
CLIENTS = [("2021/02/logo.png", "Barbados Tourism Investment Inc."),
           ("2021/02/QEH.png", "Queen Elizabeth Hospital"),
           ("2021/02/METV-Logo-1.png", "Ministry of Education, Technological & Vocational Training"),
           ("2021/02/weplantin-logo-sm.png", "National Tree Planting Project")]
TEAM = [
    ("Joyann Haigh", "CEO & Communications Specialist", None,
        [("Email", "mailto:joyann@haigh.group"), ("LinkedIn", "https://bb.linkedin.com/in/joy-ann-haigh-677b51207")]),
    ("Ziggy Marshall", "Executive Assistant", "2021/02/Ziggy.png",
        [("Email", "mailto:ziggy@haigh.group"), ("LinkedIn", "https://bb.linkedin.com/in/r-ziggy-marshall-321a2572"), ("Facebook", "https://www.facebook.com/ZigsM")]),
    ("Kevin Bishop", "ICT & Information Management", "2021/02/KevinBishops.png",
        [("Email", "mailto:kevin@haigh.group"), ("LinkedIn", "https://www.linkedin.com/in/kevinbishp/"), ("Website", "https://www.kevin-bish.com"), ("Instagram", "https://www.instagram.com/kevinbish/")]),
]

def team_img(rel):
    """Square portrait, trimmed to the circle the source photo already sits in."""
    if rel is None:
        return hero_th
    stem = re.sub(r"[^a-z0-9]+", "-", os.path.basename(rel).lower().rsplit(".", 1)[0])
    out = f"assets/img/team-{stem}.jpg"
    im = Image.open(os.path.join(SRC_IMG, rel)).convert("RGBA")
    bg = Image.new("RGB", im.size, (244, 243, 248)); bg.paste(im, mask=im.split()[3])
    bb = im.split()[3].point(lambda v: 255 if v > 200 else 0).getbbox() or (0, 0) + im.size
    w = bb[2] - bb[0]; inset = int(w * .02)
    bg = bg.crop((bb[0] + inset, bb[1] + inset, bb[2] - inset, bb[3] - inset)).resize((560, 560))
    bg.save(os.path.join(ROOT, out), quality=82)
    return out

logos = "".join(
    f'<figure><img src="{image(f, 400, 240)[1]}" alt="{e(n)}" loading="lazy"><figcaption>{e(n)}</figcaption></figure>'
    for f, n in CLIENTS)

home = f"""
<section class="hero">
  <div class="blobs" aria-hidden="true"><b></b><b></b><b></b></div>
  {DOTS}
  <div class="wrap">
    <div>
      <h1 aria-label="#1 PR agency in Barbados"><span class="w" aria-hidden="true">#1</span> <span class="w" aria-hidden="true">PR</span> <span class="w" aria-hidden="true">agency</span> <span class="w" aria-hidden="true">in</span> <span class="w grad-text shimmer" aria-hidden="true">Barbados</span></h1>
      <blockquote>
        <p>“We do it with excellence! Whether the goal is building awareness or generating leads and sales, this public relations consultancy achieves results and measures its impact.”</p>
        <cite>Joyann Haigh <small>CEO & Communications Specialist</small></cite>
      </blockquote>
      <div class="actions">
        <a class="btn warm" href="#contact">Contact us</a>
        <a class="btn" href="our-case-studies/index.html">See our work</a>
      </div>
    </div>
    <div class="portrait"><span class="halo" aria-hidden="true"></span><span class="orbit o1" aria-hidden="true"><i></i></span><span class="orbit o2" aria-hidden="true"><i></i></span><span class="orbit o3" aria-hidden="true"><i></i></span><span class="ring">{picture(hero_full, hero_th, 'Joyann Haigh, CEO of Haigh Communications', '(max-width: 820px) 82vw, 460px', lazy=False)}</span></div>
  </div>
</section>

<section class="section lilac wavy" id="work">
  <div class="wrap">
    <div class="section-head"><h2>Our work</h2><a class="more" href="our-case-studies/index.html">All case studies</a></div>
    <div class="work">
{''.join(case_cards[:3])}
    </div>
  </div>
</section>

<section class="section" id="clients">
  <div class="wrap">
    <div class="section-head center"><h2>Our clients</h2><p>Driving communications forward for public bodies and national projects across Barbados.</p></div>
    <div class="clients">{logos}</div>
  </div>
</section>

<section class="section cream wavy" id="services">
  <div class="wrap">
    <div class="section-head center"><h2>How we can help</h2><p>At Haigh Communications, we always start with strategy.</p></div>
    <div class="services">{''.join(f'<div><img src="{image(f"2019/07/img_box_{SERVICE_ICONS[t]}.png", 240, 240)[0]}" alt="" width="92" height="79" loading="lazy"><h3>{e(t)}</h3><p>{e(d)}</p></div>' for t, d in SERVICES)}</div>
  </div>
</section>

<section class="section cream wavy" id="news">
  <div class="wrap">
    <div class="section-head"><h2>Latest news</h2><a class="more" href="blog/index.html">All news</a></div>
    <ul class="news">{news_items(posts, '')}</ul>
  </div>
</section>

<section class="section" id="team">
  <div class="wrap">
    <div class="section-head center"><h2>Our team</h2></div>
    <div class="team">
{''.join(f'''<div><span class="ph"><img src="{team_img(img)}" alt="{e(n)}" width="560" height="560" loading="lazy"></span>
<h3>{e(n)}</h3><div class="role">{e(role)}</div>
<div class="links">{''.join(f'<a href="{u}">{l}</a>' for l, u in links)}</div></div>''' for n, role, img, links in TEAM)}
    </div>
  </div>
</section>

<section class="section cream wavy-top contact" id="contact" style="padding-bottom:40px">
  <div class="wrap">
    <div>
      <h2>Being different… <span class="grad-text">makes a difference.</span></h2>
      <p>PR and communications for your business or project. Tell us what you’re working on and we’ll get back to you.</p>
      <div class="actions">
        <a class="btn warm" href="mailto:{EMAIL}">{ICON['mail']}Email us</a>
        <a class="btn" href="{WHATSAPP}">{ICON['whatsapp']}WhatsApp</a>
      </div>
      <dl>
        <div><span class="ic">{ICON['mail']}</span><div><dt>Email</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd></div></div>
        <div><span class="ic">{ICON['phone']}</span><div><dt>Phone & WhatsApp</dt><dd><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></dd></div></div>
        <div><span class="ic">{ICON['pin']}</span><div><dt>Office</dt><dd>{e(ADDRESS)}</dd></div></div>
      </dl>
    </div>
    <div class="art">{picture(*image("2020/08/contact-us.png", 1000, 600), "", "(max-width: 820px) 90vw, 560px")}</div>
  </div>
</section>
"""
page("index.html", "Haigh Communications – #1 PR agency in Barbados",
     "Public relations, media relations, crisis communications and content marketing in Barbados. We do it with excellence.", home)

# ----------------------------------------------------------------- case studies index
page("our-case-studies/index.html", "Case studies",
     "Public relations case studies from Haigh Communications: flood mitigation, the Bridgetown transformation, the National Tree Planting Project and the QEH.",
     f"""<section class="page-head">{DOTS}<div class="wrap"><div class="crumb"><a href="../index.html">Home</a></div>
<h1>Case studies</h1><p class="meta">Public relations for national projects across Barbados.</p></div></section>
<section class="section" style="padding-top:0"><div class="wrap"><div class="work">
{''.join(c.replace('href="portfolio/', 'href="../portfolio/').replace('src="assets/', 'src="../assets/').replace(', assets/', ', ../assets/').replace('srcset="assets/', 'srcset="../assets/') for c in case_cards)}
</div></div></section>""", current="Work")

# ----------------------------------------------------------------- case study pages
for i, c in enumerate(cases):
    r = "../../"
    client, summ, cover = CASE_META[c["slug"]]
    full, th = image(cover)
    prev_c, next_c = cases[i - 1] if i > 0 else None, cases[i + 1] if i + 1 < len(cases) else None
    pager = ""
    if prev_c: pager += f'<a href="../{prev_c["slug"]}/index.html"><span>Previous</span>{e(prev_c["title"])}</a>'
    if next_c: pager += f'<a href="../{next_c["slug"]}/index.html"><span>Next</span>{e(next_c["title"])}</a>'
    page(f"portfolio/{c['slug']}/index.html", c["title"], summ, f"""
<section class="page-head">{DOTS}<div class="wrap">
<div class="crumb"><a href="{r}our-case-studies/index.html">Case studies</a></div>
<h1>{e(c['title'])}</h1><div class="meta"><strong>{e(client)}</strong><span>Public relations</span></div>
</div></section>
<div class="cover">{picture(full, th, '', '(max-width: 1180px) 100vw, 1180px', lazy=False, r=r)}</div>
<article class="prose">
<p><strong>{e(summ)}</strong></p>
{render_body(c['body'], r, c['slug'])}
</article>
<nav class="pager" aria-label="More case studies">{pager}</nav>""", current="Work", og_image=full)

# ----------------------------------------------------------------- blog index + posts
page("blog/index.html", "News", "News and updates from Haigh Communications.",
     f"""<section class="page-head">{DOTS}<div class="wrap"><div class="crumb"><a href="../index.html">Home</a></div><h1>News</h1></div></section>
<section class="section" style="padding-top:0"><div class="wrap"><ul class="news">{news_items(posts, '../')}</ul></div></section>""",
     current="News")

for i, p in enumerate(posts):
    r = "../"
    cat, cover = POST_META[p["slug"]]
    full, th = image(cover)
    human, iso = fmt_date(p["date"])
    body = p["body"]
    # drop a leading image block that repeats the cover
    if body and body[0]["type"] == "img" and os.path.basename(src_rel(body[0]["imgs"][0]["src"])).split(".")[0] in cover:
        body = body[1:]
    prev_p, next_p = posts[i - 1] if i > 0 else None, posts[i + 1] if i + 1 < len(posts) else None
    pager = ""
    if next_p: pager += f'<a href="../{next_p["slug"]}/index.html"><span>Older</span>{e(next_p["title"])}</a>'
    if prev_p: pager += f'<a href="../{prev_p["slug"]}/index.html"><span>Newer</span>{e(prev_p["title"])}</a>'
    page(f"{p['slug']}/index.html", p["title"], summary(p["body"], 155), f"""
<section class="page-head">{DOTS}<div class="wrap">
<div class="crumb"><a href="{r}blog/index.html">News</a></div>
<h1>{e(p['title'])}</h1><div class="meta"><strong>{e(cat)}</strong><time datetime="{iso}">{human}</time></div>
</div></section>
<div class="cover">{picture(full, th, '', '(max-width: 1180px) 100vw, 1180px', lazy=False, r=r)}</div>
<article class="prose">
{render_body(body, r, p['slug'])}
</article>
<nav class="pager" aria-label="More news">{pager}</nav>""", current="News", og_image=full)

# ----------------------------------------------------------------- 404
page("404.html", "Page not found", "This page doesn’t exist.", """
<section class="notfound"><div class="wrap"><h1>This page doesn’t exist</h1>
<p>It may have moved when the site was rebuilt. Try the <a href="/index.html">home page</a>, our <a href="/our-case-studies/">case studies</a> or the <a href="/blog/">news</a>.</p></div></section>""")

print("built", len(cases), "case studies,", len(posts), "posts,", len(os.listdir(OUT_IMG)), "images")
