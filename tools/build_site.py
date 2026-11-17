"""Build the static pages of romeorozario.com from shared parts.

Usage: python3 -I build_site.py /home/user/romeorozario.com
"""
import html, json, os, sys

ROOT = sys.argv[1]
e = lambda s: html.escape(s, quote=False)
ea = lambda s: html.escape(s, quote=True)

PAGES = dict(home="/", portfolio="/portfolio.html", blogs="/blog.html", music="/music.html", qualifications="/education.html")
CV = "/Romeo%20Rozario%20CV%202026.pdf"
EMAIL = "hello@romeorozario.com"

ARR = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" '
       'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>')
SUN = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">'
       '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>')
MOON = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>')

CONTACTS = [("Email", EMAIL, "mailto:" + EMAIL),
            ("LinkedIn", "romeo-rozario", "https://www.linkedin.com/in/romeo-rozario/"),
            ("X", "@allaboutromeo", "https://x.com/allaboutromeo"),
            ("Instagram", "@romeonicholasrozario", "https://www.instagram.com/romeonicholasrozario"),
            ("Facebook", "romeonicholasrozario", "https://www.facebook.com/romeonicholasrozario"),
            ("Discord", "Send me a message", "https://discord.com/users/473758414372077578"),
            ("YouTube", "@RomeoRozario", "https://www.youtube.com/@RomeoRozario"),
            ("Muck Rack", "muckrack.com/romeo-rozario", "https://muckrack.com/romeo-rozario/portfolio"),
            ("Dribbble", "romeonicholasrozario", "https://dribbble.com/romeonicholasrozario"),
            ("Behance", "romeonicholasrozario", "https://www.behance.net/romeonicholasrozario")]


def ext(url):
    return url.startswith("http")


def a_attrs(url):
    return ' target="_blank" rel="noopener"' if ext(url) else ""


def btn(label, href, kind="primary", size="", magnetic=True, extra_attr=""):
    cls = f"btn btn--{kind}" + (f" btn--{size}" if size else "")
    return (f'<a class="{cls}" href="{href}"{a_attrs(href)}{" data-magnetic" if magnetic else ""}{extra_attr}>'
            f'{e(label)}{ARR}</a>')


# ---------------------------------------------------------------------------
# Shared head, header and footer
# ---------------------------------------------------------------------------
def head(title, desc, canonical, og_image, extra_head=""):
    return f'''<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>
  /* Set theme and the js flag before first paint, so there is no flash. */
  (function () {{
    var d = document.documentElement, t = null;
    d.classList.add("js");
    try {{ t = localStorage.getItem("theme"); }} catch (e) {{}}
    if (t !== "light" && t !== "dark") t = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    d.setAttribute("data-theme", t);
  }})();
</script>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-9D5DWVD4LX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-9D5DWVD4LX');
</script>
<title>{e(title)}</title>
<meta name="description" content="{ea(desc)}">
<meta name="author" content="Romeo Nicholas Rozario">
<meta name="google-site-verification" content="MgLc2EPak2qLwboO3UE4iZnTQsgrsQIcB6ugvh7PEeg">
<meta name="theme-color" content="#F6F7FB">
<link rel="canonical" href="{canonical}">
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="icon" type="image/png" sizes="512x512" href="/apple-touch-icon.png">
<link rel="apple-touch-icon" sizes="512x512" href="/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{ea(title)}">
<meta property="og:description" content="{ea(desc)}">
<meta property="og:image" content="{og_image}">
<meta property="og:site_name" content="Romeo Nicholas Rozario">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@allaboutromeo">
<meta name="twitter:title" content="{ea(title)}">
<meta name="twitter:description" content="{ea(desc)}">
<meta name="twitter:image" content="{og_image}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&amp;family=Geist:wght@400;500;600;700&amp;family=Geist+Mono:wght@400;500&amp;display=swap">
<link rel="stylesheet" href="/css/site.css">
{extra_head}</head>'''


def header(active):
    items = [("About Me", "home"), ("My Portfolio", "portfolio"), ("Blogs", "blogs"), ("Music", "music"),
             ("Qualifications", "qualifications"), ("Contact", None)]
    links = "\n".join(
        f'<a href="{PAGES[k] if k else "/#contact"}"{" aria-current=\"page\"" if k == active else ""}>{l}</a>' for l, k in items)
    return f'''<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
<div class="wrap header-row">
<a class="brand" href="/" aria-label="Romeo Rozario, home"><span class="brand-mark" aria-hidden="true">RR</span><span class="brand-name">Romeo Rozario</span></a>
<nav class="nav-links" id="site-nav" aria-label="Primary">
{links}
</nav>
<div class="header-actions">
<button type="button" class="theme-toggle" data-theme-toggle aria-label="Switch to dark mode" aria-pressed="false"><span class="t-sun">{SUN}</span><span class="t-moon">{MOON}</span></button>
<a class="btn btn--primary btn--sm" href="{CV}" download data-magnetic>Download CV</a>
<button type="button" class="menu-toggle" aria-controls="site-nav" aria-expanded="false" aria-label="Menu"><i></i></button>
</div>
</div>
<span class="progress" aria-hidden="true"></span>
</header>'''


def footer():
    pages = [("About Me", PAGES["home"]), ("My Portfolio", PAGES["portfolio"]), ("Blogs", PAGES["blogs"]),
             ("Music", PAGES["music"]), ("Qualifications", PAGES["qualifications"]), ("Contact", "/#contact")]
    pl = "\n".join(f'<a href="{h}">{l}</a>' for l, h in pages)
    cl = "\n".join(f'<a href="{u}"{a_attrs(u)}>{l}</a>' for l, _, u in CONTACTS)
    return f'''<footer class="site-footer">
<div class="wrap">
<div class="footer-top">
<div style="display: flex; flex-direction: column; gap: 10px; max-width: 360px">
<span class="name">Romeo Rozario</span>
<span class="tag">Content strategy and growth marketing.</span>
</div>
<nav class="footer-nav" aria-label="Footer">
{pl}
</nav>
</div>
<div class="footer-social">
{cl}
</div>
<p class="copyright">© <span data-year>2026</span> romeorozario.com</p>
</div>
</footer>'''


def page(path, title, desc, active, body, og_image="https://romeorozario.com/images/site/hero-portrait.webp", canonical=None, extra_head=""):
    canonical = canonical or ("https://romeorozario.com" + ("/" if path == "index.html" else "/" + path))
    out = (head(title, desc, canonical, og_image, extra_head) + "\n<body>\n" + header(active)
           + '\n<main id="main">\n' + body + "\n</main>\n" + footer()
           + '\n<script src="/js/site.js" defer></script>\n</body>\n</html>\n')
    with open(os.path.join(ROOT, path), "w") as f:
        f.write(out)
    return out


# ---------------------------------------------------------------------------
# HOME
# ---------------------------------------------------------------------------
IMG = "/images/site/"
LG = "/images/brand-logos/"
LOGOS = [("E-Warmup", "ewarmup.webp", 26), ("Serpely", "serpely.webp", 36), ("Care Skills Training", "careskills.webp", 38),
         ("WellDev", "welldev.webp", 26), ("WP Manage Ninja", "wpmn.webp", 34), ("WPMet", "wpmet.webp", 28), ("WPCenter", "wpcenter.webp", 24),
         ("InnoTix", "innotix.webp", 32), ("trueAct", "trueact.webp", 24), ("Rhätische Bahn", "rhb.webp", 24),
         ("Essential Safety Training", "essential.webp", 38), ("fluentCRM", "fluentcrm.webp", 28), ("Fluent Forms", "fluentforms.webp", 28),
         ("GetGenie", "getgenie.webp", 32), ("SendCopy", "sendcopy.webp", 22), ("Pink Mail", "pink-mail-navy.png", 24),
         ("AffiliateX", "affiliatex.webp", 28), ("Lantern Sol", "lantern-sol.webp", 28), ("Heritage", "heritage.webp", 46),
         ("JPK Landscaping", "jpk-landscaping.png", 50)]
LOGO_FILE = {n: f for n, f, h in LOGOS}


def logo_wall():
    rows = [LOGOS[0:7], LOGOS[7:14], LOGOS[14:20]]
    out = []
    for r in rows:
        lis = "".join(f'<li data-reveal="fade"><img src="{LG}{f}" alt="{ea(n)}" loading="lazy" decoding="async" style="--h: {h}px"></li>' for n, f, h in r)
        out.append(f'<ul class="logo-row" data-stagger>{lis}</ul>')
    return '<div class="logo-wall">' + "".join(out) + "</div>"


def start_card(href, title, text, cta, pill, src, pos, bg):
    return (f'<a class="start-card start-card--{bg}" href="{href}" data-reveal>'
            f'<img src="{src}" alt="" loading="lazy" decoding="async" style="object-position: {pos}">'
            f'<span class="t"><b>{e(title)}</b><span>{e(text)}</span></span>'
            f'<span class="pill pill--{pill}">{e(cta)}{ARR}</span></a>')


def work_card(span, bg, shots, label, title, desc, stats, chips, href, shot_h):
    if len(shots) == 2:
        media = (f'<div class="shot-pair" style="height: {shot_h}px">'
                 + "".join(f'<div class="shot"><img src="{s}" alt="{ea(a)}" loading="lazy" decoding="async" data-zoom></div>' for s, a, p in shots)
                 + "</div>")
    else:
        s, a, p = shots[0]
        media = f'<div class="shot" style="height: {shot_h}px"><img src="{s}" alt="{ea(a)}" loading="lazy" decoding="async" data-zoom style="object-position: {p}"></div>'
    st = "".join(f"<div><b>{e(v)}</b><span>{e(l)}</span></div>" for v, l in stats)
    ch = "".join(f"<span>{e(c)}</span>" for c in chips)
    return (f'<article class="work-card span-{span} work-card--{bg}" data-reveal>{media}'
            f'<p class="label">{e(label)}</p><h3>{e(title)}</h3>'
            + (f'<p class="desc">{e(desc)}</p>' if desc else "")
            + (f'<div class="chips">{ch}</div>' if ch else "")
            + (f'<div class="wstats">{st}</div>' if st else "")
            + f'<div class="more">{btn("View the work", href, "ghost", "sm", magnetic=False)}</div></article>')


def svc_card(t, d, c, sid):
    color = "var(--orange)" if c == "o" else "var(--cobalt)"
    return (f'<a class="svc" href="{PAGES["portfolio"]}#{sid}" style="--c: {color}" data-reveal>'
            f'<h3>{e(t)}</h3><p>{e(d)}</p><span class="go">See the work {ARR}</span></a>')


EXP = [("01", "E-Warmup", "E-Warmup", "Content and Social Media Manager", "Content that converts for email deliverability SaaS.",
        "Product marketing, SEO content, landing pages and the editorial calendar for an email deliverability and warmup platform. Feb 2026 to present.",
        [("5,000+", "Happy businesses"), ("50+", "Articles written"), ("2x", "ROAS achieved")], ["#1 Project of the Day, Open Launch", "Featured on Product Hunt"], "https://e-warmup.com"),
       ("02", "Serpely", "CieloOps", "Marketing Project Coordinator", "Building the SEO tool for the AI era.",
        "Serpely is an agentic SEO platform built for GEO, AEO and AI citation optimization. I lead full marketing: positioning, content, product storytelling and growth strategy.",
        [], [], "https://serpely.com"),
       ("03", "Care Skills Training", "Care Skills Training UK", "Marketing Team Lead", "360 marketing across web, social, email and paid.",
        "Led full marketing across SEO, content, paid media and email for a UK healthcare training provider. Ran Google, Microsoft and Meta campaigns.",
        [("2M+", "Search impressions"), ("30K+", "Monthly traffic"), ("2,000+", "Email leads"), ("100+", "Blogs published"), ("3x", "ROAS achieved")], [], "https://careskillstraining.org"),
       ("04", "WellDev", "WellDev AG", "Content Marketing Specialist", "International content strategy across three products.",
        "Content strategy for Welltravel, InnoTix and trueAct. Collaborated with teams across Switzerland, Austria, Germany and North America.",
        [("50K+", "LinkedIn followers"), ("15K+", "Newsletter subscribers")], [], "https://welldev.io"),
       ("05", "WP Manage Ninja", "WPManageNinja (AuthLab)", "Digital Marketing Strategist", "Content and product marketing for a WordPress plugin suite used across thousands of sites.",
        "", [], ["Paymattic", "AzonPress", "Fluent Forms"], "https://wpmanageninja.com"),
       ("06", "WPMet", "WPMet (XpeedStudio)", "Creative Content Writer", "SEO content, ad copy and social strategy across a WordPress and AI product portfolio.",
        "", [], ["GetGenie AI", "ShopEngine", "ElementsKit"], "https://wpmet.com")]


def exp_card(num, logo, company, role, headline, desc, stats, chips, url):
    st = "".join(f"<div><b>{e(v)}</b><span>{e(l)}</span></div>" for v, l in stats)
    ch = "".join(f"<span>{e(c)}</span>" for c in chips)
    return (f'<li class="exp-card" data-reveal><div class="exp-top"><div class="plate"><img src="{LG}{LOGO_FILE[logo]}" alt="{ea(logo)} logo" loading="lazy" decoding="async"></div>'
            f'<span class="num">{num}</span></div>'
            f'<p class="role">{e(company)} · {e(role)}</p><h3>{e(headline)}</h3>'
            + (f'<p class="desc">{e(desc)}</p>' if desc else "")
            + (f'<div class="estats">{st}</div>' if st else "")
            + (f'<div class="chips">{ch}</div>' if ch else "")
            + f'<div class="more">{btn("Visit site", url, "ghost", "sm", magnetic=False)}</div></li>')


POSTS = [("E-Warmup", "Oct 29, 2026", "Email Deliverability Updates News: 5 Key Q4 2026 Changes",
          "https://e-warmup.com/blog/email-deliverability-updates-news-q4-2026/", "/images/blog-covers/ewarmup-deliverability-updates-q4-2026.webp"),
         ("Serpely", "Oct 17, 2026", "7 SEO Mistakes That Are Making You Invisible to AI Search in 2027",
          "https://serpely.com/blog/seo-mistakes-ai-search-visibility", "/images/blog-covers/serpely-seo-mistakes-ai-search.webp"),
         ("E-Warmup", "Oct 18, 2026", "Best Email Warmup Tools in 2027: 7 Compared and Ranked",
          "https://e-warmup.com/blog/best-email-warmup-tool/", "/images/blog-covers/ewarmup-best-email-warmup-tools.webp")]


def post_card(pub, date, title, url, img):
    return (f'<a class="post" href="{url}" target="_blank" rel="noopener" data-reveal>'
            f'<span class="cover"><img src="{img}" alt="" loading="lazy" decoding="async" width="800" height="450"></span>'
            f'<span class="meta">{e(pub)}<span>, {e(date)}</span></span><span class="title">{e(title)}</span></a>')


def stat(label, value, count, suffix, cls=""):
    return (f'<div data-reveal><dt>{e(label)}</dt><dd class="{cls}" data-count="{count}" data-suffix="{ea(suffix)}">{e(value)}</dd></div>')


def build_home():
    services = [
        ("Content strategy", "Editorial plans, content calendars and briefs built around what your audience searches for.", "o", "seo"),
        ("SEO content writing", "SEO, GEO and AEO-ready blogs and landing pages for SaaS products, D2C brands and eLearning platforms. 200+ blogs written.", "c", "blogs"),
        ("Social media marketing", "Strategy, posts and carousels for LinkedIn, Instagram, Facebook and X. Grew a LinkedIn newsletter to 15K+ subscribers.", "o", "social"),
        ("Graphic design and motion", "Social posts, carousels, ad creatives and short motion graphics, designed in-house and sized for every feed.", "c", "social"),
        ("Paid media (PPC)", "Google, Microsoft and Meta campaigns, plus the ad copy and creatives that run in them.", "c", "ads"),
        ("UI/UX design and UX copy", "Working app dashboards and landing pages for software, with the interface and the words built together.", "o", "lp-web"),
        ("Product marketing", "Positioning and launches backed by competitor analysis, website audits in Semrush and Ahrefs, and hands-on product testing.", "c", "lp-web"),
        ("Email marketing", "Quality campaigns and newsletters, with email designs and HTML emails built in Mailchimp and MailerLite.", "o", "email"),
    ]
    P = PAGES["portfolio"]
    work = "\n".join([
        work_card(7, "peach", [(IMG + "ewarmup-landing-page.webp", "e-warmup.com landing page: Are your emails landing in spam? We can fix that.", "left top")],
                  "E-Warmup · Email deliverability SaaS", "Content and social that convert for an email deliverability SaaS",
                  "I lead content and social, from SEO articles and launch posts to product demo videos, lifecycle emails and paid campaigns.",
                  [("50+", "Articles written"), ("2x", "ROAS on paid campaigns")], ["SEO articles", "Social and carousels", "Motion", "Lifecycle email", "Paid ads"], P, 400),
        work_card(5, "sky", [("/images/ui-ux/serpely-dashboard-dark.webp", "Serpely app dashboard: Command Center with site health, organic performance and AI visibility", ""),
                             (IMG + "serpely-homepage.webp", "serpely.com homepage: Agentic SEO, built for the AI-first web", "")],
                  "Serpely · Agentic SEO tool", "Launching an agentic SEO tool for the AI search era", "",
                  [], ["App dashboard design", "Positioning", "Full website copy", "Go-to-market", "Product demo video"], P + "#lp-web", 170),
        work_card(5, "surf", [(IMG + "care-skills-search-console.webp", "Search Console performance for Care Skills Training: 253K impressions", "left top")],
                  "Care Skills Training · UK", "Full-funnel marketing for a healthcare training provider", "",
                  [("2M+", "Search impressions"), ("30K+", "Monthly traffic"), ("3x", "ROAS")], [], P + "#seo", 150),
        work_card(4, "surf", [("/images/blog-covers/welldev-saas-paas-iaas-faas.webp", "WellDev blog cover: Navigating the Cloud, SaaS vs PaaS vs IaaS vs FaaS", "left top")],
                  "WellDev AG · Switzerland", "Content strategy for a Swiss software firm", "",
                  [("50K+", "LinkedIn followers"), ("15K+", "Newsletter subscribers")], [], P + "#blogs", 150),
        work_card(4, "sky", [(IMG + "wpmanageninja-google-rank-1.webp", "Google results: WPManageNinja ranked #1 for conversion funnel optimization", "left top")],
                  "WPManageNinja · WordPress plugins", "Ranking #1 on Google with a single guide", "",
                  [("#1", "conversion funnel optimization"), ("61K", "Impressions")], [], P + "#blogs", 150),
        work_card(4, "peach", [("/images/ad-creatives/ewarmup-1111-sale-facebook-feed-ad.webp", "Facebook feed ad for the E-Warmup 11.11 Sale", "center 30%")],
                  "Paid media · Meta and Google", "Ad creatives and campaigns that pay back", "",
                  [("3x", "Best ROAS"), ("3", "Ad platforms run")], [], P + "#ads", 150),
    ])
    starts = "\n".join([
        start_card(P, "My portfolio", "Blogs, copy, ads, social, email and web design, with results.", "See the work", "ink",
                   "/images/ad-creatives/ewarmup-1111-sale-instagram-feed-ad.webp", "center 30%", "peach"),
        start_card(PAGES["blogs"], "Blogs", "Professional blogs for the teams I've worked with, plus a personal journal.", "Read blogs", "cobalt",
                   "/images/blog-covers/serpely-seo-mistakes-ai-search.webp", "left center", "sky"),
        start_card(PAGES["qualifications"], "Qualifications", "Economics degrees from SUST, plus Google, HubSpot and more.", "See credentials", "ink",
                   IMG + "google-certificate.webp", "center top", "plain"),
        start_card(PAGES["music"], "Off the clock", "Guitarist in three bands. Hear what I make after work.", "Hear my music", "orange",
                   IMG + "on-stage.webp", "center 35%", "plain"),
    ])
    contacts = "\n".join(f'<li><a href="{u}"{a_attrs(u)}><span>{l}</span><b>{e(h)}</b></a></li>' for l, h, u in CONTACTS)

    body = f'''
<section class="hero" aria-labelledby="hero-h">
<div class="glow glow--a" aria-hidden="true"></div>
<div class="glow glow--b" aria-hidden="true"></div>
<div class="wrap hero-grid">
<div class="hero-copy">
<p class="chip" data-enter style="--d: 0"><span class="dot" aria-hidden="true"></span>Content strategy and growth marketing</p>
<h1 id="hero-h" data-split>The one who makes brands <span class="accent">matter.</span></h1>
<p class="hero-sub" data-enter style="--d: 520">5+ years in digital marketing. I build content that ranks, campaigns that convert, and strategies that stick. I've done it for SaaS, WordPress, eLearning, eCommerce and D2C brands.</p>
<div class="hero-ctas" data-enter style="--d: 640">{btn("See my work", P, "primary")}{btn("Get in touch", "#contact", "outline")}</div>
</div>
<div class="hero-photo" data-enter style="--d: 200">
<img src="{IMG}hero-portrait.webp" alt="Romeo Rozario in a dark blazer and white turtleneck, arms crossed, in front of a blue and gold wall" width="1000" height="1000" fetchpriority="high" decoding="async">
</div>
</div>
</section>

<section class="stats" aria-label="Highlights">
<dl class="wrap" data-stagger>
{stat("In digital marketing", "5+ years", 5, "+ years")}
{stat("Blogs written", "200+", 200, "+", "c-link")}
{stat("Search impressions driven", "2M+", 2, "M+", "c-orange")}
{stat("Monthly organic traffic", "30K+", 30, "K+")}
</dl>
</section>

<section class="start" aria-labelledby="start-h">
<div class="wrap">
<h2 class="h2" id="start-h" data-reveal>Start here</h2>
<div class="start-grid" data-stagger>
{starts}
</div>
</div>
</section>

<section class="brands" aria-labelledby="brands-h">
<div class="wrap">
<p class="eyebrow" id="brands-h" data-reveal="fade">Teams I've worked with</p>
{logo_wall()}
</div>
</section>

<section class="work" id="work" aria-labelledby="work-h">
<div class="wrap">
<div class="section-head" data-reveal>
<div><p class="eyebrow" aria-hidden="true">Case studies</p><h2 class="h2" id="work-h">Selected work</h2></div>
{btn("See full portfolio", P, "primary", "sm")}
</div>
<div class="work-grid" data-stagger>
{work}
</div>
</div>
</section>

<section class="services" aria-labelledby="services-h">
<div class="wrap">
<h2 class="h2" id="services-h" data-reveal>What I do</h2>
<div class="svc-grid" data-stagger>
{"".join(svc_card(*s) for s in services)}
</div>
</div>
</section>

<section class="exp" aria-labelledby="exp-h">
<div class="wrap">
<div class="section-head" data-reveal>
<div><h2 class="h2" id="exp-h">Experience</h2><p class="lede">Six teams across Switzerland, the UK, Europe and Bangladesh.</p></div>
<a class="btn btn--primary btn--sm" href="{CV}" download data-magnetic>Download CV{ARR}</a>
</div>
<ol class="exp-grid" data-stagger>
{"".join(exp_card(*x) for x in EXP)}
</ol>
</div>
</section>

<section class="about" id="about" aria-labelledby="about-h">
<div class="wrap">
<div class="about-photo" data-reveal="scale"><img src="{IMG}about-cafe.webp" alt="Romeo working on a laptop at a cafe" loading="lazy" decoding="async" width="1260" height="1260"></div>
<div class="about-copy" data-stagger>
<h2 class="h2" id="about-h" data-reveal>An economist who found marketing</h2>
<p data-reveal>I studied economics at SUST and ended up writing landing pages and building growth funnels. It makes more sense than it sounds.</p>
<p data-reveal>I've worked with teams in the US, UK and Europe, across SaaS, eLearning, healthcare and eCommerce.</p>
<div class="ctas" data-reveal>{btn("Qualifications", PAGES["qualifications"], "ink")}{btn("Off the clock: my music", PAGES["music"], "ghost")}</div>
</div>
</div>
</section>

<section class="blogs" id="writing" aria-labelledby="writing-h">
<div class="wrap">
<div class="section-head" data-reveal>
<h2 class="h2" id="writing-h">Blogs</h2>
{btn("See all blogs", PAGES["blogs"], "primary", "sm")}
</div>
<div class="blog-grid" data-stagger>
{"".join(post_card(*p) for p in POSTS)}
</div>
</div>
</section>

<section class="contact" id="contact" aria-labelledby="contact-h">
<div class="wrap">
<div class="contact-panel" data-reveal="scale">
<div class="glow" aria-hidden="true"></div>
<h2 class="h2" id="contact-h">Want your brand found in search and AI answers?</h2>
<p>Email works best. You can also find me on any of these.</p>
<div>{btn("Get in touch", "mailto:" + EMAIL, "primary")}</div>
<ul class="contact-grid" aria-label="All the ways to reach me">
{contacts}
</ul>
</div>
</div>
</section>
'''
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Person", "@id": "https://romeorozario.com/#person", "name": "Romeo Nicholas Rozario", "url": "https://romeorozario.com/",
             "image": "https://romeorozario.com/images/site/hero-portrait.webp", "jobTitle": "Marketing Project Coordinator",
             "worksFor": [{"@type": "Organization", "name": "CieloOps", "url": "https://serpely.com"},
                          {"@type": "Organization", "name": "E-Warmup", "url": "https://e-warmup.com"}],
             "alumniOf": {"@type": "CollegeOrUniversity", "name": "Shahjalal University of Science and Technology"},
             "description": "Digital marketer with 5+ years across SEO, GEO, AEO, content strategy, paid media, social and email for SaaS and D2C brands.",
             "email": "mailto:" + EMAIL,
             "sameAs": [u for l, h, u in CONTACTS if ext(u)],
             "knowsAbout": ["SEO", "GEO", "AEO", "Content Strategy", "SaaS Marketing", "Paid Media", "Email Marketing", "Social Media Marketing", "UI/UX Copywriting"]},
            {"@type": "WebSite", "@id": "https://romeorozario.com/#website", "url": "https://romeorozario.com/", "name": "Romeo Nicholas Rozario",
             "publisher": {"@id": "https://romeorozario.com/#person"}},
        ]}
    extra = ('<link rel="preload" as="image" href="/images/site/hero-portrait.webp" fetchpriority="high">\n'
             '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False) + "</script>\n")
    page("index.html",
         "Romeo Nicholas Rozario: Digital Marketer for SaaS, SEO and AI Search",
         "Romeo Nicholas Rozario is a digital marketer with 5+ years in SEO, GEO, content strategy, paid media and social for SaaS brands like E-Warmup and Serpely.",
         "home", body, extra_head=extra)


if __name__ == "__main__":
    build_home()
    print("built index.html")
