"""Build portfolio.html, blog.html, music.html and education.html.

Content comes from the approved design generator (gen_hifi.py); shared head,
header, footer and buttons come from build_site.py. Images referenced by the
design are copied into the repo with readable names.

Usage: python3 -I build_pages.py /home/user/romeorozario.com
"""
import contextlib, hashlib, html, io, json, os, re, runpy, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
ROOT = sys.argv[1]
sys.path.insert(0, HERE)
import build_site as S  # noqa: E402

e, ea, btn, ARR = S.e, S.ea, S.btn, S.ARR
PAGES = S.PAGES

# ---------------------------------------------------------------------------
# Design data
# ---------------------------------------------------------------------------
os.makedirs(os.path.join(SCRATCH, "tmpgen", "project"), exist_ok=True)
shutil.copy(os.path.join(SCRATCH, "articles-final.json"), os.path.join(SCRATCH, "tmpgen"))
_argv = sys.argv
sys.argv = ["gen", os.path.join(SCRATCH, "tmpgen", "project"), "7950", "6650", "2300", "6150", "light", "6350", "4200", "2650"]
with contextlib.redirect_stdout(io.StringIO()):
    G = runpy.run_path(os.path.join(SCRATCH, "gen_hifi.py"))
sys.argv = _argv
A, CERT = G["A"], G["CERT"]
BLOBS = json.load(open(os.path.join(SCRATCH, "blobmap.json")))


def slug(s, n=70):
    s = html.unescape(s).lower().replace("&", "and")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:n].rstrip("-")


_REPO_INDEX = None


def _repo_by_sha():
    global _REPO_INDEX
    if _REPO_INDEX is None:
        _REPO_INDEX = {}
        for root, ds, fs in os.walk(ROOT):
            if ".git" in root:
                continue
            for x in fs:
                p = os.path.join(root, x)
                if os.path.getsize(p) < 40_000_000:
                    _REPO_INDEX.setdefault(hashlib.sha256(open(p, "rb").read()).hexdigest(), p)
    return _REPO_INDEX


def asset(ref, folder, name=None):
    """Return a site path for a design asset, copying it into the repo if needed."""
    bid = ref.rsplit("/", 1)[-1]
    bid = A.get(bid, bid)
    v = BLOBS[bid]
    p = _repo_by_sha().get(v["sha"]) or v.get("repo")
    if p and os.path.exists(p):
        return "/" + os.path.relpath(p, ROOT)
    ext = os.path.splitext(v["path"])[1] or os.path.splitext(v["name"])[1]
    fname = (slug(name) + ext) if name else v["name"]
    dest_dir = os.path.join(ROOT, folder)
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, fname)
    n = 2
    while os.path.exists(dest) and hashlib.sha256(open(dest, "rb").read()).hexdigest() != v["sha"]:
        dest = os.path.join(dest_dir, os.path.splitext(fname)[0] + f"-{n}" + ext)
        n += 1
    if not os.path.exists(dest):
        shutil.copy(v["path"], dest)
    _repo_by_sha()[v["sha"]] = dest
    return "/" + os.path.relpath(dest, ROOT)


def img_size(site_path):
    try:
        from PIL import Image
        return Image.open(os.path.join(ROOT, site_path.lstrip("/"))).size
    except Exception:
        return None


def img(src, alt, cls="", zoom=False, eager=False, style=""):
    wh = img_size(src)
    dims = f' width="{wh[0]}" height="{wh[1]}"' if wh else ""
    return (f'<img src="{src}" alt="{ea(alt)}"{dims}{" loading=\"lazy\"" if not eager else " fetchpriority=\"high\""} decoding="async"'
            + (f' class="{cls}"' if cls else "") + (" data-zoom" if zoom else "") + (f' style="{style}"' if style else "") + ">")


def eyebrow(t):
    return f'<p class="eyebrow" aria-hidden="true">{e(t)}</p>'


def cta_band(title, text, primary, secondary, hid):
    (l1, h1), (l2, h2) = primary, secondary
    return f'''<section class="cta-wrap" id="contact" aria-labelledby="{hid}">
<div class="wrap">
<div class="cta-band" data-reveal="scale">
<div><h2 class="h2" id="{hid}">{e(title)}</h2><p>{e(text)}</p></div>
<div class="ctas">{btn(l1, h1, "dark", extra_attr=' download' if h1 == S.CV else '')}{btn(l2, h2, "line", extra_attr=' download' if h2 == S.CV else '')}</div>
</div>
</div>
</section>'''


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>\n"


def crumbs(name, url):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://romeorozario.com/"},
        {"@type": "ListItem", "position": 2, "name": name, "item": url}]}


# ===========================================================================
# PORTFOLIO
# ===========================================================================
def bento(cols, rowh, cells, gap=14, cls=""):
    """cells: (inner_html, colspan, rowspan, label or None, mobile size class)"""
    out = []
    for c in cells:
        inner, cs, rs = c[0], c[1], c[2]
        label = c[3] if len(c) > 3 else None
        size = c[4] if len(c) > 4 else ""
        chip = f'<figcaption class="bchip">{e(label)}</figcaption>' if label else ""
        out.append(f'<figure class="{size}" style="grid-column: span {cs}; grid-row: span {rs}" data-reveal>{inner}{chip}</figure>')
    return (f'<div class="bento {cls}" style="--cols: {cols}; --rowh: {rowh}px; --gap: {gap}px" data-stagger>' + "".join(out) + "</div>")


def bfit(ref, alt, folder, name, kind=""):
    return f'<div class="fit {kind}">' + img(asset(ref, folder, name), alt, zoom=True) + "</div>"


def bimg(ref, alt, folder, name, pos="top"):
    return img(asset(ref, folder, name), alt, cls="fill", zoom=True, style=f"object-position: {pos}")


def bfull(ref, alt, folder, name):
    return img(asset(ref, folder, name), alt, cls="contain", zoom=True)


def pf_section(sid, num, short, title, text, results, wall, tint, accent, links=None):
    results = [r for r in results if not r.startswith("[ADD")]
    lis = "".join(f"<li>{e(r)}</li>" for r in results)
    lk = ""
    if links:
        lk = '<div class="links">' + "".join(btn(t, h, "ghost", "sm", magnetic=False) for t, h in links) + "</div>"
    return f'''<section class="pf tint-{tint} acc-{accent}" id="{sid}" aria-labelledby="{sid}-h">
<div class="wrap">
<div class="pf-head">
<div class="lead" data-reveal>
{eyebrow(f"{num:02d} / {short}")}
<h2 class="h2" id="{sid}-h">{e(title)}</h2>
<p>{e(text)}</p>
{lk}
</div>
<div class="results" data-reveal><h3>Key results</h3><ul>{lis}</ul></div>
</div>
{wall}
</div>
</section>'''


def compact_card(a, folder="images/blog-covers"):
    src = asset(a["img"], folder, a.get("pub", "") + " " + a["title"])
    inner = (f'<span class="cover">{img(src, "")}</span><span class="pub">{e(a["pub"])}</span><span class="title">{e(a["title"])}</span>'
             + (f'<span class="tag">{e(a["badge"])}</span>' if a.get("badge") else ""))
    if a.get("url"):
        return f'<a class="ccard" href="{a["url"]}" target="_blank" rel="noopener" data-reveal>{inner}</a>'
    return f'<div class="ccard" data-reveal>{inner}</div>'


def social_wall():
    slides = "".join(f'<figure class="slide">{img(asset(k, "images/social-media-designs", t), alt, zoom=True)}</figure>' for k, t, alt in G["POSTS_MIX"])
    n = len(G["POSTS_MIX"])
    slider = f'''<div class="slider" data-slider data-reveal>
<div class="slider-head"><h3 class="sub-h">Social posts</h3><p class="count" aria-live="polite">4 of {n} posts</p></div>
<div class="slider-view">
<div class="slider-track" tabindex="0" aria-label="Social posts, scroll sideways">{slides}</div>
<button type="button" class="arrow-btn prev" aria-label="Previous posts"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M11 6l-6 6 6 6"/></svg></button>
<button type="button" class="arrow-btn next" aria-label="Next posts"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></button>
</div>
</div>'''
    strips = "".join(f'<div class="strip-scroll" data-reveal>{img(asset(k, "images/social-media-designs", "carousel " + t), alt, zoom=True)}</div>'
                     for k, t, nn, w, h, wp, alt in G["CAROUSELS"])
    carousels = f'<div class="strips"><h3 class="sub-h" data-reveal>Carousels</h3>{strips}</div>'
    return ('<div style="display: flex; flex-direction: column; gap: 44px">' + slider + carousels
            + '<div class="motion"><h3 class="sub-h" data-reveal>Motion graphics</h3>' + motion_row(G["VIDEOS"]) + motion_row(G["VIDEOS2"]) + "</div></div>")


WEB_VIDEO = {"serpely-demo-v4-square.mp4": "serpely-demo-v4-square-web.mp4"}


def video_src(ref):
    p = asset(ref, "videos/motion-graphics")
    base = os.path.basename(p)
    if base in WEB_VIDEO:
        p = p.replace(base, WEB_VIDEO[base])
    return p


def motion_row(rows):
    figs = []
    for vid, poster, ar, fl, meta, title, label in rows:
        cls = "tall" if ar.startswith("9 /") else ("wide" if ar.startswith("16 /") else "")
        figs.append(f'<figure style="flex: {fl}" class="{cls}" data-reveal>'
                    f'<video controls muted loop playsinline preload="none" data-autoplay poster="{asset(poster, "videos/motion-graphics")}" aria-label="{ea(label)}" style="aspect-ratio: {ar}">'
                    f'<source src="{video_src(vid)}" type="video/mp4"></video>'
                    f"<figcaption>{e(title)}</figcaption></figure>")
    return '<div class="motion-row" data-stagger>' + "".join(figs) + "</div>"


def ad_wall():
    H = 320
    ads = [("42a45518d31f67c46ae96654ee0a68fd", "Black Friday feed ad", "E-Warmup BFCM sale, 1:1",
            "E-Warmup Black Friday ad: Stop landing in spam, with spam and inbox cards and up to 85% off", 1200, 1200, False),
           ("982aae84a28548231c1ff7dc43e397f8", "Cyber Monday feed ad", "E-Warmup BFCM sale, 4:5",
            "E-Warmup Cyber Monday ad: up to 85% off, 85% off first month, 60% off yearly plans", 1080, 1350, False),
           ("266c23e7022cffe62683c73185d42295", "Facebook feed ad", "E-Warmup 11.11 Sale",
            "Facebook sponsored post for the E-Warmup 11.11 Sale: starting from $11.11 a month, up to 77% off monthly and yearly plans", 294, 440, True),
           ("fe78961b7f48b16b98edd4594fc04193", "Instagram feed ad", "E-Warmup 11.11 Sale",
            "Instagram ad for the E-Warmup 11.11 Sale with an orange envelope: starting from $11.11 a month, up to 77% off", 260, 440, True)]
    figs = "".join(f'<figure data-reveal>{img(asset(k, "images/ad-creatives", t), alt, cls="mock" if mock else "", zoom=True, style=f"width: {round(H * w / h)}px")}'
                   f'<figcaption><p class="t">{e(t)}</p><p class="s">{e(sub)}</p></figcaption></figure>'
                   for k, t, sub, alt, w, h, mock in ads)
    return f'<div class="ads-wall" data-stagger>{figs}</div>'


def email_flows():
    flows = [("Signup flow", "Serpely and E-Warmup", ["Sign up", "Confirm email", "Welcome", "Onboarding"]),
             ("Abandoned cart", "Care Skills Training", ["Cart abandoned", "Reminder email", "Follow-up email", "Order recovered"])]
    rows = ""
    for name, who, steps in flows:
        pills = '<span class="ar" aria-hidden="true">→</span>'.join(
            f'<span class="st{" last" if k == len(steps) - 1 else ""}">{e(st)}</span>' for k, st in enumerate(steps))
        rows += f'<div class="flow"><div class="name"><b>{e(name)}</b><span>{e(who)}</span></div><div class="steps">{pills}</div></div>'
    tools = "".join(f"<span>{t}</span>" for t in ["Mailchimp", "MailerLite", "Claude (AI)", "HTML email"])
    return f'<div class="flows" data-reveal><div class="flows-head"><h3 class="sub-h">Automations I\'ve built</h3><div class="tools">{tools}</div></div>{rows}</div>'


def email_wall():
    cards = "".join(f'<figure data-reveal>{img(asset(k, "images/email-designs", b + " " + t), b + " email: " + t, zoom=True)}'
                    f"<figcaption><span>{e(b)}</span><b>{e(t)}</b></figcaption></figure>" for k, b, t in G["EMAILS"])
    return f'<div class="email-grid" data-stagger>{cards}</div>'


def build_portfolio():
    U = "images/seo-analytics"
    W = "images/ui-ux"
    paid_panel = ('<div class="panel-stats">' + eyebrow("Paid media results")
                  + "".join(f'<div><b class="{c}">{e(v)}</b><span>{e(l)}</span></div>' for v, l, c in
                            [("3x", "Best ROAS", "c-orange"), ("£7,176", "Gross sales from 232 orders", ""), ("3", "Ad platforms: Google, Microsoft, Meta", "c-link")])
                  + "</div>")
    topk = G["TOPPER_K"]
    topper = (f'<div class="topper"><div class="zoomed">{img(asset(topk, W, "ewarmup bfcm topper bar"), "E-Warmup Black Friday x Cyber Monday topper bar, close-up: up to 85% off, countdown timer")}</div>'
              + img(asset(topk, W, "ewarmup bfcm topper bar"), "E-Warmup Black Friday x Cyber Monday topper bar, full width with Claim the deal button", zoom=True) + "</div>")

    pf_blogs = G["pf_blogs"] + [dict(img=G["B"](k), pub=b, date=d, title=t) for k, b, d, t in G["BYLINES"]]
    sections = {
        "blogs": lambda n: pf_section("blogs", n, "Blogs", "Blogs and content marketing",
            "I plan, research and write SEO content that ranks and gets cited by AI: keyword research, content calendars, briefs and the writing itself.",
            ["200+ blogs written in total", "50+ articles written for E-Warmup", "100+ blogs published for Care Skills Training",
             "Content strategy for Welltravel, InnoTix and trueAct at WellDev", "SEO content writing for D2C eCommerce brands and travel businesses"],
            '<div class="ccards" data-stagger>' + "".join(compact_card(a) for a in pf_blogs) + "</div>"
            + f'<div class="center-cta">{btn("Read more of my blogs", PAGES["blogs"], "ink")}</div>',
            "bg", "orange", [("Bylines on Muck Rack", "https://muckrack.com/romeo-rozario/portfolio")]),
        "social": lambda n: pf_section("social", n, "Social and motion", "Social media design and motion graphics",
            "Posts, carousels, graphics and short motion videos for LinkedIn, Instagram, Facebook and X, planned as part of a content calendar.",
            ["Grew a LinkedIn newsletter to 15K+ subscribers", "50K+ LinkedIn followers for a Swiss software firm", "Posts for product launches, promos, education and news",
             "Carousels that tell one story across every slide", "Product demos for Serpely and E-Warmup, GetGenie sale promos and a DOPAMINE teaser"],
            social_wall(), "sky", "cobalt"),
        "ads": lambda n: pf_section("ads", n, "Paid media", "Ad creatives and paid media",
            "Concept, copy and design for paid campaigns on Meta, Google, Microsoft and LinkedIn, plus running and optimising them.",
            ["2x ROAS on E-Warmup campaigns", "3x ROAS for Care Skills Training", "Ran Google, Microsoft and Meta campaigns",
             "£7,176 gross sales from 232 orders on paid campaigns", "Black Friday, Cyber Monday and 11.11 sale creatives for E-Warmup"],
            ad_wall() + bento(6, 40, [(bfit("6a8f6cb4846866713ceee69122caf46e", "eCommerce revenue report from paid campaigns: £7,176.30 gross sales, 232 orders", U, "paid campaigns revenue report"), 4, 9, "Google, Microsoft and Meta ads: £7,176 gross sales, 232 orders"),
                                      (paid_panel, 2, 9)]),
            "bg", "orange"),
        "lp-web": lambda n: pf_section("lp-web", n, "Web and UI/UX", "Landing pages, web and UI/UX",
            "Landing pages and websites from positioning to final layout: the conversion copy, the wireframes and the design. Plus working app dashboards designed with AI, where the interface and the words are built together.",
            ["Full website copy and positioning for serpely.com", "Landing page copy and content supervision for e-warmup.com",
             "Black Friday and Cyber Monday sale landing page for E-Warmup, desktop and mobile", "Homepage hero copy for Care Skills Training",
             "Customer case study pages for E-Warmup", "Service page copy for a Cincinnati landscaping company", "Serpely app dashboard: UI/UX design"],
            bento(6, 104, [(bimg("shot_serpely", "serpely.com hero and copy", W, "serpely homepage"), 4, 3, "serpely.com: website copy and positioning"),
                           (bimg("a42127ffc2f70e70519041736231a83b", "E-Warmup Black Friday and Cyber Monday landing page, full desktop design: Stop landing in spam, save up to 85%", W, "ewarmup bfcm landing desktop"), 2, 5, "E-Warmup BFCM landing page", "tall"),
                           (bimg("shot_ewarmup", "e-warmup.com landing page", W, "ewarmup landing page"), 2, 2, "e-warmup.com: landing page copy"),
                           (bimg("proof_serpely", "Serpely website copy section", W, "serpely website copy"), 2, 2, "Conversion copy"),
                           (bimg(G["DASH_DARK"], "Serpely app dashboard: Command Center with site health, organic performance and AI visibility", W, "serpely dashboard", "left top"), 4, 4, "Serpely app dashboard: UI/UX design"),
                           (bimg("a4c0eae29aa05977f10918242d02e4d0", "E-Warmup Black Friday landing page on mobile: Pay less per mailbox as you grow", W, "ewarmup bfcm landing mobile"), 2, 4, "BFCM landing page: mobile", "tall"),
                           (bimg("7f2e0e2a9ad8ed62017f680ea4db34bd", "JPK Landscaping service page: Retaining Wall Contractors in Cincinnati, OH", W, "jpk retaining walls service page", "center top"), 2, 8, "Service page copy: retaining walls", "tall"),
                           (bfull("0ae7863d3d70bd959f46953a870123d7", "Care Skills Training homepage hero: UK's Leading Health and Social Care Training Provider", W, "care skills hero"), 4, 4, "Care Skills Training: hero copy"),
                           (bfull("ee7c7dcd2ca1b089eba86a313b478e4c", "E-Warmup case study page: How Laurence Thomas hit 96% inbox with E-Warmup", W, "ewarmup case study page"), 4, 4, "E-Warmup case study page"),
                           (topper, 6, 2, "BFCM sitewide topper bar")]),
            "peach", "cobalt", [("serpely.com", "https://serpely.com"), ("e-warmup.com", "https://e-warmup.com"), ("Retaining walls service page", "https://www.jpklandscaping.com/retaining-walls/")]),
        "seo": lambda n: pf_section("seo", n, "Analytics", "SEO and AI SEO analytics",
            "Technical, on-page and content SEO, plus GEO and AEO so pages show up in AI Overviews, ChatGPT and Perplexity. I track every move in Search Console, GA4, Microsoft Clarity and Ahrefs.",
            ["1.53K clicks and 55.3K impressions in 3 months for an email deliverability SaaS", "5.2K active users in 28 days on a SaaS website",
             "2M+ search impressions and 30K+ monthly traffic for a UK training provider", "#1 on Google for “conversion funnel optimization” (61K impressions)",
             "Heatmaps and session insights in Microsoft Clarity"],
            bento(6, 40, [(bfit("84bcf232794b529a135b1ad8cb8f122f", "Google Search Console performance over 3 months: 1.53K clicks, 55.3K impressions, 2.8% CTR, average position 20", U, "search console 3 months"), 6, 10, "Search Console: 1.53K clicks, 55.3K impressions in 3 months"),
                          (bfit("3342069bf1adfec56d1070e4b5274e5e", "GA4 realtime overview: active users map and per-minute chart", U, "ga4 realtime"), 3, 6, "GA4: realtime overview"),
                          (bfit("24103e4e85eeed9c05dc4524ef8146ef", "Microsoft Clarity overview: 394 sessions, 3.03 pages per session, 92.47% scroll depth, rage and dead click insights", U, "microsoft clarity overview"), 3, 6, "Microsoft Clarity: sessions and UX insights"),
                          (bfit("b8507a5e613a9c0ffbb2a46e01198aba", "GA4 reports snapshot, last 28 days: 5.2K active users, 5K new users, 1m 24s average engagement, 71K events", U, "ga4 28 days"), 6, 7, "GA4: 5.2K active users in 28 days"),
                          (bfit("9d06f82db3da1ef62971e4f525c5343b", "GA4 engagement: 1m 24s average engagement time, 29K views, 71K events", U, "ga4 engagement"), 2, 9, "GA4: engagement and views", "tall"),
                          (bfit("proof_care", "SEO dashboard: 253.47K impressions, 9.45K keywords, 2K clicks, average position 19.67", U, "seo dashboard 253k impressions"), 4, 9, "SEO dashboard: 253K impressions, 9.45K keywords"),
                          (bfit("cf77756a455eee9b6a5eabd308457a1d", "Google results: page 1 for software development life cycle (SDLC)", U, "serp sdlc page 1", "dark"), 3, 7, "Page 1 for “software development life cycle”"),
                          (bfit("b9e7de12b560488182d802604d81740d", "Google results: #1 for problems with creating content at scale", U, "serp content at scale", "dark"), 3, 7, "#1 on Google for “problems with creating content at scale”"),
                          (bfit("proof_wpmn", "Google results: #1 for conversion funnel optimization", U, "serp conversion funnel", "dark"), 3, 10, "#1 on Google for “conversion funnel optimization”"),
                          (bfit("ed82c97520ae5e062c03814fdfb7f827", "Google results: #2 for care certificate answers, a high-volume keyword", U, "serp care certificate answers", "dark"), 3, 10, "#2 on Google for “care certificate answers”, a high-volume keyword")]),
            "bg", "orange"),
        "email": lambda n: pf_section("email", n, "Email", "Email marketing and design",
            "Lifecycle emails and the automations behind them, from the signup flow to abandoned carts. I design and build them in Mailchimp, MailerLite and with AI (Claude), and write them to get opened and clicked.",
            ["Signup flow automation: sign up, confirm email, welcome and onboarding", "Abandoned cart automation for Care Skills Training",
             "Email designs built with Mailchimp, MailerLite and Claude (AI)", "15K+ newsletter subscribers", "2,000+ email leads for Care Skills Training"],
            email_flows() + email_wall(), "sky", "orange"),
    }
    order = ["blogs", "social", "ads", "lp-web", "seo", "email"]
    labels = {"blogs": "Blogs", "social": "Social and motion", "ads": "Ads", "lp-web": "Landing pages and UI/UX", "seo": "SEO analytics", "email": "Email"}
    jump = "".join(f'<a href="#{k}"><span class="n">{n:02d}</span>{e(labels[k])}</a>' for n, k in enumerate(order, 1))
    highlights = "".join(f"<li>{e(t)}</li>" for t in [
        "200+ blogs written across SaaS, WordPress, eLearning and more", "2M+ search impressions and 30K+ monthly traffic for a UK training provider",
        "2,000+ email leads and 3x ROAS from full-funnel campaigns", "50K+ LinkedIn followers and 15K+ newsletter subscribers for a Swiss software firm",
        "Website copy and positioning for an agentic SEO product built for AI search", "End-to-end content operations: design, long and short-form content, social, email and growth"])
    portrait = asset("portrait_burg", "images/site", "portrait burgundy blazer")
    body = f'''
<section class="intro" aria-labelledby="intro-h">
<div class="glow" aria-hidden="true"></div>
<div class="wrap intro-grid">
<div class="intro-photo">{img(portrait, "Romeo Rozario in a burgundy blazer, smiling", eager=True)}</div>
<div class="intro-copy">
<h1 id="intro-h" data-split>Hi, I'm <span class="accent">Romeo</span> Rozario</h1>
<p class="badge" data-enter style="--d: 380">Digital marketer and content strategist</p>
<p data-enter style="--d: 480">5+ years in digital marketing across SaaS, WordPress, eLearning, eCommerce and D2C. I run a one-person content engine: I write the blogs and landing page copy, then design the ads, social posts, motion and emails around them.</p>
<div class="highlights" data-enter style="--d: 600"><h2>Career highlights</h2><ul>{highlights}</ul></div>
</div>
</div>
</section>

<section class="pf-brands" aria-labelledby="pf-brands-h">
<div class="wrap">
<h2 class="eyebrow" id="pf-brands-h" data-reveal="fade">Brands I've worked with</h2>
{S.logo_wall()}
</div>
</section>

<nav class="jump" data-jump aria-label="Jump to a type of work">
<div class="wrap"><span class="lbl">Jump to:</span>{jump}</div>
</nav>
{"".join(sections[k](n) for n, k in enumerate(order, 1))}

<div style="height: 56px"></div>
{cta_band("Thanks for looking.", "Like what you see? Let's talk about your next campaign.", ("Get in touch", "mailto:" + S.EMAIL), ("Download CV", S.CV), "pf-cta-h")}
'''
    url = "https://romeorozario.com/portfolio.html"
    extra = ld({"@context": "https://schema.org", "@type": "CollectionPage", "name": "Portfolio of Romeo Nicholas Rozario", "url": url,
                "about": {"@id": "https://romeorozario.com/#person"},
                "description": "Blogs, social media design, motion graphics, ad creatives, landing pages, UI/UX, SEO analytics and email marketing work."}) + ld(crumbs("Portfolio", url))
    S.page("portfolio.html", "Portfolio: Content, SEO, Ads, Social and UI/UX Work | Romeo Nicholas Rozario",
           "Selected marketing work by Romeo Nicholas Rozario: SEO blogs, social and motion design, paid ads with 3x ROAS, landing pages, UI/UX and email campaigns.",
           "portfolio", body, og_image="https://romeorozario.com" + portrait, extra_head=extra)


# ===========================================================================
# BLOGS
# ===========================================================================
def build_blogs():
    per = G["PER_PAGE"]
    posts = G["BLOG_ALL"] + []
    pages = [posts[i:i + per] for i in range(0, len(posts), per)]

    def bcard(a):
        src = asset(a["img"], "images/blog-covers", a["pub"] + " " + a["title"])
        return (f'<a class="bcard" href="{a["url"]}" target="_blank" rel="noopener">'
                f'<span class="cover">{img(src, "")}</span><span class="pub">{e(a["pub"])}</span>'
                f'<span class="title">{e(a["title"])}</span><span class="date">{e(a["date"])}</span></a>')
    pg_html = "".join(f'<div class="pager-page{" is-current" if n == 0 else ""}" role="group" aria-label="Page {n + 1} of {len(pages)}">'
                      + "".join(bcard(a) for a in pg) + "</div>" for n, pg in enumerate(pages))
    body = f'''
<section class="hero" aria-labelledby="w-h1">
<div class="glow glow--a" aria-hidden="true" style="background: radial-gradient(circle, var(--glow-b), transparent 70%)"></div>
<div class="wrap hero-grid single">
<div class="hero-copy">
<h1 id="w-h1" data-split>My <span class="accent">Blogs</span></h1>
<p class="hero-sub" data-enter style="--d: 300">Professional blogs I've written for the teams I've worked with, on SEO, AI search, email deliverability and SaaS. Plus a personal journal, coming soon. 200+ blogs written in total.</p>
<div class="chips-row" data-enter style="--d: 420"><a class="chip-link is-primary" href="#professional">Professional blogs ({len(posts)})</a><a class="chip-link" href="#journal">My personal journal</a></div>
</div>
</div>
</section>

<section class="sec" id="professional" aria-labelledby="pro-h">
<div class="wrap">
<div class="section-head" data-reveal>
<div>{eyebrow("01 / For the teams I've worked with")}<h2 class="h2" id="pro-h">Professional blogs</h2></div>
<p class="count" data-pager-label aria-live="polite">1 / {len(pages)}</p>
</div>
<div class="pager" data-pager data-reveal>
<div class="pager-pages">{pg_html}</div>
<button type="button" class="arrow-btn prev" aria-label="Previous blogs"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M11 6l-6 6 6 6"/></svg></button>
<button type="button" class="arrow-btn next" aria-label="Next blogs"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></button>
</div>
<div data-reveal>{btn("All bylines on Muck Rack", "https://muckrack.com/romeo-rozario/portfolio", "ghost", "sm")}</div>
</div>
</section>

<section class="sec" id="journal" aria-labelledby="journal-h" style="padding-top: 0; padding-bottom: 104px">
<div class="wrap">
<div class="journal" data-reveal="scale">
{eyebrow("02 / Coming soon")}
<h2 class="h2" id="journal-h">My personal journal</h2>
<p>Not the blogs I write for brands, but the ones I write for myself. On strategy, creativity, music, and where they overlap.</p>
<ul aria-label="Upcoming topics">{"".join(f"<li>{t}</li>" for t in ["SEO and AI search", "SaaS growth", "Content and storytelling", "Music and creativity"])}</ul>
</div>
</div>
</section>
'''
    url = "https://romeorozario.com/blog.html"
    items = [{"@type": "ListItem", "position": i + 1, "url": a["url"], "name": a["title"]} for i, a in enumerate(posts)]
    extra = ld({"@context": "https://schema.org", "@type": "CollectionPage", "name": "Blogs by Romeo Nicholas Rozario", "url": url,
                "author": {"@id": "https://romeorozario.com/#person"}, "mainEntity": {"@type": "ItemList", "itemListElement": items}}) + ld(crumbs("Blogs", url))
    S.page("blog.html", "Blogs by Romeo Nicholas Rozario: SEO, AI Search, Email and SaaS",
           f"{len(posts)} professional blogs by Romeo Nicholas Rozario on SEO, AI search, email deliverability and SaaS growth, written for E-Warmup, Serpely, WellDev and more.",
           "blogs", body, og_image="https://romeorozario.com" + asset(posts[0]["img"], "images/blog-covers", posts[0]["pub"] + " " + posts[0]["title"]), extra_head=extra)


# ===========================================================================
# MUSIC
# ===========================================================================
def build_music():
    M = "images/music"
    hero = asset("music_hero", M, "romeo on stage green guitar")
    bands = G["bands"]

    def links(ls):
        return '<div class="band-links">' + "".join(f'<a href="{u}" target="_blank" rel="noopener">{t}</a>' for t, u in ls) + "</div>"

    b0 = bands[0]
    feature = f'''<article class="band-feature" data-reveal>
<div class="photo">{img(asset(b0[3], M, b0[0] + " band"), b0[0] + " band members")}</div>
<div class="band-body">
{img(asset(b0[4], M, b0[0] + " logo"), b0[0] + " logo", cls="logo")}
<p class="genre">{e(b0[1])}</p>
<h3>{e(b0[0])}</h3>
<p>{e(b0[2])}</p>
{links(b0[5])}
</div>
</article>'''
    cards = "".join(f'''<article class="band-card" data-reveal>
<div class="photo">{img(asset(b[3], M, b[0] + " band"), b[0] + " band photo")}</div>
<div class="band-body">
<div class="row">{img(asset(b[4], M, b[0] + " logo"), b[0] + " logo", cls="logo")}<div><p class="genre">{e(b[1])}</p><h3>{e(b[0])}</h3></div></div>
<p>{e(b[2])}</p>
{links(b[5])}
</div>
</article>''' for b in bands[1:])
    rel = [("DOPAMINE", [("1% (One Percent)", "Official music video"), ("Good Job", "Music video, teaser out now"), ("Sporshohin", "Guitar, production, mix and master")]),
           ("Buffering", [("Bishomomatrik", "Debut album, 2026"), ("Chondrobhuk", "Track 01, official music video"), ("Tumi Heena", "Track 02, with Masha Islam"),
                          ("Kromosho", "Single, 2023"), ("Jana Ki Chhilo?", "Single, 2022, official music video"), ("Prokasher Opekkhay", "Single, 2021")]),
           ("Eden's Garden", [("Firey Dekha", "Original"), ("Khushir Jagoron", "Original, official lyric video")])]
    releases = "".join(f'<div class="release" data-reveal><h3>{e(g)}</h3>' + "".join(f"<div><b>{e(t)}</b><span>{e(s)}</span></div>" for t, s in items) + "</div>" for g, items in rel)

    PLAY = '<span class="play" aria-hidden="true"><svg width="22" height="22" viewBox="0 0 24 24"><path d="M8 5v14l11-7z" fill="#FFFFFF"/></svg></span>'

    def yt(vid, thumb, who, title, big=False):
        src = asset(thumb, M, who + " " + title + " youtube thumbnail")
        return (f'<a class="yt{" big" if big else ""}" href="https://www.youtube.com/watch?v={vid}" target="_blank" rel="noopener" data-yt="{vid}" aria-label="Play {ea(who + ": " + title)}" data-reveal>'
                f'<span class="frame">{img(src, who + ", " + title + " (YouTube)")}{PLAY}</span>'
                f'<span><span class="who">{e(who)} · YouTube</span><span class="what">{e(title)}</span></span></a>')

    def sp(aid, k, name):
        src = asset(k, M, name + " spotify artist")
        return (f'<a class="sp" href="https://open.spotify.com/artist/{aid}" target="_blank" rel="noopener" data-spotify="{aid}" aria-label="{ea(name)} on Spotify" data-reveal>'
                f'{img(src, name + " on Spotify")}<span class="meta"><b>{e(name)}</b><small>Artist on Spotify</small>'
                f'<span class="go"><svg width="12" height="12" viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z" fill="#04140A"/></svg>Play on Spotify</span></span></a>')

    gallery = bento(4, 180, [(bimg("stage1", "Romeo on stage from behind, crowd lights", M, "stage crowd lights", "center"), 2, 2),
                             (bimg("stage2", "Romeo playing guitar in a studio", M, "studio guitar", "center"), 1, 2, None, "tall"),
                             (bimg("stage6", "Full-length shot with green guitar", M, "full length green guitar", "center"), 1, 2, None, "tall"),
                             (bimg("stage4", "Still from a music video", M, "music video still", "center"), 2, 1),
                             (bimg("stage5", "Wide stage shot with crowd lights", M, "wide stage shot", "center"), 2, 1)], 12)
    body = f'''
<section class="hero mhero" aria-labelledby="music-h1">
<div class="glow glow--b" aria-hidden="true" style="left: -160px; top: -200px; bottom: auto; width: 620px; height: 620px"></div>
<div class="wrap hero-grid">
<div class="hero-copy">
<p class="chip" data-enter style="--d: 0">Off the clock</p>
<h1 id="music-h1" data-split>Guitarist, lyricist and <span class="accent">producer.</span></h1>
<p class="hero-sub" data-enter style="--d: 480">15+ years on guitar. Three active bands, session work, and music for film and TV.</p>
<div class="hero-ctas" data-enter style="--d: 600">{btn("Listen on Spotify", "https://open.spotify.com/artist/1W4HbIZa9wnuJLYxVIrBnH", "primary")}{btn("Watch on YouTube", "https://www.youtube.com/@RomeoRozario", "outline")}</div>
</div>
<div class="hero-photo" data-enter style="--d: 200">{img(hero, "Romeo playing a green electric guitar on stage under blue lights", eager=True)}</div>
</div>
</section>

<section class="sec" aria-labelledby="bands-h" style="padding-top: 96px">
<div class="wrap">
<h2 class="h2" id="bands-h" data-reveal>Bands</h2>
{feature}
<div class="band-grid" data-stagger>{cards}</div>
</div>
</section>

<section class="sec tint-surf" aria-labelledby="releases-h">
<div class="wrap">
<h2 class="h2" id="releases-h" data-reveal>Releases</h2>
<div class="releases" data-stagger>{releases}</div>
</div>
</section>

<section class="sec" aria-labelledby="listen-h">
<div class="wrap">
<h2 class="h2" id="listen-h" data-reveal>Listen and watch</h2>
<div class="listen-top">
<figure class="teaser" data-reveal>
<video controls muted loop playsinline preload="none" data-autoplay poster="{asset("782f5331aed48cdb0c96f0d1729def76", "videos/music")}" aria-label="DOPAMINE, Good Job music video teaser"><source src="{asset("d43faf535f8090ea636bc1cd599cf8d0", "videos/music")}" type="video/mp4"></video>
<figcaption><span>DOPAMINE</span><b>Good Job: music video teaser</b></figcaption>
</figure>
{yt("wslgKDZzSB8", "d641734c143efbe6856ea656cad48051", "DOPAMINE", "1% (One Percent): official music video", big=True)}
</div>
<div class="yt-grid" data-stagger>
{yt("sIsgmyx2dKk", "9b23b015caf0037f39e95929543f2a98", "Buffering", "Chondrobhuk: official music video")}
{yt("linqTmcE7bM", "5ba9ec74f1b5f86e397d175dc9c3a684", "Buffering x Masha Islam", "Tumi Heena: official video")}
{yt("LtJmssK_YFg", "6137c40935573c0e7145aa0d4c53a557", "Buffering", "Jana Ki Chhilo?: official music video")}
{yt("JM12hbbHE4k", "a4d189031c00d4f813ca34e9eedf7dbd", "Eden's Garden", "Khushir Jagoron: official lyric video")}
</div>
<div style="display: flex; flex-direction: column; gap: 14px">
{eyebrow("On Spotify")}
<div class="sp-grid" data-stagger>
{sp("2oKoiTsvNHWxOm9rPYB5w9", "2e8e9489ca189f35ef460f7a40495d89", "DOPAMINE")}
{sp("1W4HbIZa9wnuJLYxVIrBnH", "59eb218ce9e64fa6cf2afc44d2e15532", "Buffering")}
{sp("4ZJ4DO6XzIDmISJ4YAYuky", "ef0659038bbdbc4d636129e4cb043bdb", "Eden's Garden")}
</div>
</div>
</div>
</section>

<section class="sec" aria-labelledby="session-h" style="padding-top: 0">
<div class="wrap">
<div class="beyond" data-reveal="scale">
<h2 class="h2" id="session-h">Beyond the band</h2>
<p>I produce, play session guitar, and mix and master tracks. I've played on a movie score, TVCs and jingles, and taught guitar to 20+ students.</p>
<ul aria-label="Services">{"".join(f"<li>{t}</li>" for t in ["Music production", "Session guitar", "Mix and master", "Film score", "TVCs and jingles", "Guitar lessons"])}</ul>
</div>
</div>
</section>

<section class="sec" aria-labelledby="gallery-h" style="padding-top: 0">
<div class="wrap">
<h2 class="h2" id="gallery-h" data-reveal>On stage</h2>
{gallery}
</div>
</section>

{cta_band("Need a guitarist or producer?", "Gigs, sessions, production and lessons.", ("Get in touch", "mailto:" + S.EMAIL), ("Watch on YouTube", "https://www.youtube.com/@RomeoRozario"), "booking-h")}
'''
    url = "https://romeorozario.com/music.html"
    groups = [{"@type": "MusicGroup", "name": b[0], "genre": b[1].split(",")[0], "sameAs": [u for t, u in b[5]],
               "member": {"@type": "OrganizationRole", "member": {"@id": "https://romeorozario.com/#person"}, "roleName": "Guitarist"}} for b in bands]
    extra = ld({"@context": "https://schema.org", "@type": "ProfilePage", "name": "Music: Romeo Nicholas Rozario", "url": url,
                "mainEntity": {"@id": "https://romeorozario.com/#person"}, "about": groups}) + ld(crumbs("Music", url))
    S.page("music.html", "Music: Guitarist, Lyricist and Producer | Romeo Nicholas Rozario",
           "Romeo Nicholas Rozario plays guitar in DOPAMINE, Buffering and Eden's Garden. 15+ years on guitar, session work, production, and music for film and TV.",
           "music", body, og_image="https://romeorozario.com" + hero, extra_head=extra)


# ===========================================================================
# QUALIFICATIONS
# ===========================================================================
def build_qualifications():
    Q = "images/certificates"

    def cert(k, alt):
        return f'<div class="fit cert">' + img(asset(CERT[k], Q, k + " certificate"), alt, zoom=True) + "</div>"

    def ctext(big, small, note, cls):
        return f'<div class="panel-text"><b class="{cls}">{e(big)}</b><strong>{e(small)}</strong><span>{e(note)}</span></div>'

    def edu(y, deg, school, place, grade, chips, big=False):
        ch = "".join(f"<li>{e(c)}</li>" for c in chips)
        return (f'<article class="edu{" big" if big else ""}" data-reveal><p class="yr">{e(y)}</p><h3>{e(deg)}</h3><p class="school">{e(school)}</p>'
                f'<p class="place">{e(place)} <span aria-hidden="true">·</span> {e(grade)}</p>' + (f"<ul>{ch}</ul>" if chips else "") + "</article>")

    EDU = G["EDU"]
    stats = [("M.S.S. & B.S.S.", "Economics, SUST", ""), ("12", "Certifications", "c-link"), ("7.5", "IELTS band score", "c-orange"), ("4", "From Google and HubSpot", "")]
    body = f'''
<section class="hero" aria-labelledby="q-h1">
<div class="glow glow--a" aria-hidden="true"></div>
<div class="wrap hero-grid q-grid">
<div class="hero-copy">
<p class="chip" data-enter style="--d: 0">Background</p>
<h1 id="q-h1" data-split>Education and <span class="accent">certifications.</span></h1>
<p class="hero-sub" data-enter style="--d: 480">An economist by training, a marketer by trade. Two economics degrees from SUST, plus certifications from Google, HubSpot and more.</p>
<div class="hero-ctas" data-enter style="--d: 600">{btn("Download CV", S.CV, "primary", extra_attr=" download")}{btn("Get in touch", "#contact", "outline")}</div>
</div>
<dl class="qstats" data-stagger>{"".join(f'<div data-reveal><dt>{e(l)}</dt><dd class="{c}">{e(v)}</dd></div>' for v, l, c in stats)}</dl>
</div>
</section>

<section class="sec" aria-labelledby="edu-h">
<div class="wrap">
<div class="sec-head" data-reveal>{eyebrow("01 / Education")}<h2 class="h2" id="edu-h">Where I studied</h2></div>
<div class="edu-grid" data-stagger>{edu(*EDU[0], big=True)}{edu(*EDU[1], big=True)}{edu(*EDU[2])}{edu(*EDU[3])}</div>
</div>
</section>

<section class="sec tint-sky" aria-labelledby="cert-h">
<div class="wrap">
<div class="sec-head" data-reveal>{eyebrow("02 / Marketing certifications")}<h2 class="h2" id="cert-h">Certified in the work I do</h2></div>
{bento(12, 118, [
        (cert("google", "Google certificate: Foundations of Digital Marketing and E-commerce"), 6, 3, "Google: Foundations of Digital Marketing and E-commerce", "tall"),
        (cert("claude", "Claude Marketing 101 certificate"), 6, 3, "GrowthPair: Claude Marketing 101", "tall"),
        (cert("hubspot_dm", "HubSpot Academy Digital Marketing Certified"), 3, 2, "HubSpot: Digital Marketing"),
        (cert("hubspot_da", "HubSpot Academy Digital Advertising Certified"), 3, 2, "HubSpot: Digital Advertising"),
        (cert("hubspot_cm", "HubSpot Academy Content Marketing Certified"), 3, 2, "HubSpot: Content Marketing"),
        (cert("hubspot_sm", "HubSpot Academy Social Media Certified"), 3, 2, "HubSpot: Social Media Marketing"),
        (cert("talentpop", "TalentPop certificate of completion"), 6, 2, "TalentPop: Growth Assistant (Marketing)"),
        (ctext("Ads", "Google Ads and Microsoft Ads", "Certifications on Udemy", "c-link"), 6, 2, "Udemy", "short")])}
</div>
</section>

<section class="sec" aria-labelledby="more-h">
<div class="wrap">
<div class="sec-head" data-reveal>{eyebrow("03 / Language, leadership and community")}<h2 class="h2" id="more-h">Beyond marketing</h2></div>
{bento(12, 118, [
        (cert("olympiad", "English Olympiad leadership certificate"), 4, 4, "English Olympiad: Leadership Certificate", "tall"),
        (ctext("7.5", "IELTS band score", "British Council", "c-orange"), 4, 2, "British Council: IELTS", "short"),
        (ctext("JAAGO", "Certified Volunteer", "JAAGO Foundation", "c-link"), 4, 2, "JAAGO Foundation", "short"),
        (cert("cypan", "Commonwealth Youth Peace Ambassadors Network certificate"), 8, 2, "CYPAN: Inclusion, Interfaith and Sustaining Peace")])}
</div>
</section>

{cta_band("Want the full picture?", "My CV has every role, result and credential in one place.", ("Download CV", S.CV), ("Get in touch", "mailto:" + S.EMAIL), "q-cta-h")}
'''
    url = "https://romeorozario.com/education.html"
    creds = [{"@type": "EducationalOccupationalCredential", "name": d, "credentialCategory": "degree",
              "recognizedBy": {"@type": "CollegeOrUniversity", "name": s}} for y, d, s, p, g, c in EDU[:2]]
    extra = ld({"@context": "https://schema.org", "@type": "ProfilePage", "name": "Education and certifications: Romeo Nicholas Rozario", "url": url,
                "mainEntity": {"@type": "Person", "@id": "https://romeorozario.com/#person", "name": "Romeo Nicholas Rozario", "hasCredential": creds,
                               "alumniOf": {"@type": "CollegeOrUniversity", "name": "Shahjalal University of Science and Technology"}}}) + ld(crumbs("Qualifications", url))
    S.page("education.html", "Education and Certifications | Romeo Nicholas Rozario",
           "Romeo Nicholas Rozario holds M.S.S. and B.S.S. degrees in Economics from SUST, plus 12 certifications from Google, HubSpot, GrowthPair and more. IELTS 7.5.",
           "qualifications", body, og_image="https://romeorozario.com" + asset(CERT["google"], Q, "google certificate"), extra_head=extra)


if __name__ == "__main__":
    build_portfolio(); print("portfolio.html")
    build_blogs(); print("blog.html")
    build_music(); print("music.html")
    build_qualifications(); print("education.html")
