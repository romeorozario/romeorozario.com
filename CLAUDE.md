# romeorozario.com

Personal site of Romeo Nicholas Rozario (digital marketer, guitarist). Plain static HTML, CSS and JavaScript. No framework, no build step: the HTML files are the source of truth, so edit them directly.

## Deploying

The live site deploys from the `main` branch. To publish a change: commit on a working branch, open a pull request into `main`, and merge it. The site is hosted on Cloudflare Pages, which redeploys automatically within a couple of minutes and posts a "Cloudflare Pages" check on each pull request.

Cloudflare Pages rejects any single file over 25 MiB and the whole deploy fails. Compress large videos (for example with ffmpeg) before committing them.

## Pages

Cloudflare Pages serves clean URLs: `/portfolio`, `/blog`, `/music`, `/education` (the `.html` versions 308-redirect there). Always link, canonicalize and list in `sitemap.xml` using the clean form.

| Page | File | Notes |
|---|---|---|
| About Me (home) | `index.html` | Hero, stats, Start here cards, logo wall, Selected work bento, What I do, Experience, About, latest Blogs, Contact |
| My Portfolio | `portfolio.html` | One page with a sticky "Jump to" nav. Sections in order: `#blogs`, `#social`, `#ads`, `#lp-web`, `#seo`, `#email` |
| Blogs | `blog.html` | Professional blogs in pages of 8 (`.pager-page` blocks), then the personal journal teaser |
| Music | `music.html` | Bands, releases, YouTube and Spotify (click-to-play), on-stage gallery |
| Qualifications | `education.html` | Degrees, certificates, beyond marketing |

Every page shares the same header, footer, `<head>` setup (theme script, Google tag G-9D5DWVD4LX, fonts) and loads `/css/site.css` and `/js/site.js`. If you change the header or footer, change it in all five files.

## Shared files

- `css/site.css`: design tokens at the top (`:root` for light, `[data-theme="dark"]` for dark), then home sections, then inner-page sections, then responsive rules (breakpoints 1180px, 1060px, 680px) and reduced-motion rules.
- `js/site.js`: theme toggle (circular reveal), hide-on-scroll header, mobile menu, headline word split (`data-split`), scroll reveals, count-up stats (`data-count`), magnetic buttons (`data-magnetic`), lightbox (`img[data-zoom]`), post slider (`data-slider`), blog pager (`data-pager`), jump-nav scrollspy (`data-jump`), YouTube and Spotify click-to-play (`data-yt`, `data-spotify`), autoplay-in-view videos (`video[data-autoplay]`).

## Conventions

- Desktop scale: above 1060px the whole site renders at `zoom: 0.9` (top of `css/site.css`), the same as 90% browser zoom. Any JS that turns a measured rect into a CSS length must divide by `Z()` in `js/site.js` (window scrolling does not need it).
- Phones (680px and below): two cards per row wherever a card fits (Start here, What I do, Experience, blogs, contact, portfolio blog cards, emails, bento grids, blog pager, bands, YouTube, Spotify, education). One per row only for wide content. An odd last bento tile spans the row. The phone rules sit in the "Phones: denser layout" block near the end of `css/site.css`.

- Rotating words: add `data-rotate="word|word|word"` to a span whose text is the first word (it stays in the HTML for SEO). Optional `data-rotate-every` and `data-rotate-start` in ms. The home headline cycles matter. > rank. > convert. > grow. > shine., about 1.4s per word (820ms hold plus a 0.6s swap). It pauses off-screen and stays still for reduced-motion visitors.
- Punchline: `.punch` under the hero headline is italic Unna, with `.king` in the cobalt-to-orange `--accent-grad` and an orange `.crown` that drops in. Home: "Growth happens with content. And content? Still king." Home page only.

- Brand: the header shows "Romeo Nicholas Rozario" in Unna (`--serif`) inside a pill, with "Rozario" in `--accent-grad` (`.grad`): a cobalt (#2F4BFF) to orange (#FF6B2C) gradient that glides to orange-to-blue on hover. "Nicholas" (`.mid`) hides on phones. The footer name uses the same style.

- Theme: every new visit opens in light mode. The toggle switches to dark, and that choice is kept in `sessionStorage` only, so it lasts while the visitor browses this session and resets to light next time. The pre-paint script in each page's `<head>` and `applyTheme` in `js/site.js` implement this; keep them in sync.

- Animation hooks are attributes: `data-reveal` (fade up on scroll; `="fade"` or `="scale"` variants), `data-stagger` on a parent to cascade its `data-reveal` children, `data-enter` with `style="--d: <ms>"` for hero entrance.
- Launch badges (`.launch-badges` > `a.lbadge img`) load from the platforms (Open Launch, Product Hunt). If one fails, `js/site.js` swaps in a text chip from the alt text, so write the alt as "E-Warmup: <badge text>". They appear on the home E-Warmup experience card and in the Portfolio "Launches I've marketed" strip; add new launches to both.
- Any image or video with `data-zoom` opens in the lightbox (videos play full size there).
- Landing pages and UI/UX uses a compact `.bento.gallery` (3 columns desktop, 2 tablet and phone). Keep tiles small: the lightbox shows the full size. `.feature` and `.wide` span 2 columns; `.wide-sm` spans the row only on tablet and phone, to avoid a lone tile.
- Buttons: `class="btn btn--primary|ink|ghost|outline|dark|line"` with the arrow SVG inside; add `data-magnetic` for the hover pull.
- Text content stays in the HTML (good for SEO and AI crawlers). Animations are progressive enhancement and respect `prefers-reduced-motion`.
- Images live in `images/` by type (`site`, `brand-logos`, `blog-covers`, `social-media-designs`, `ad-creatives`, `ui-ux`, `seo-analytics`, `email-designs`, `music`, `certificates`). Use `.webp`, include `width` and `height`, and `loading="lazy"` below the fold.
- Videos live in `videos/`. Pages use the compressed `*-web.mp4` versions with a poster image; the full-size originals are kept for reference only.
- Writing style: conversational, data-driven, no em dashes.
- Accent gradient: cobalt #2F4BFF to brand orange #FF6B2C only (`--accent-grad`, blended in oklab where supported). No purple or pink stops. Buttons stay solid.
- No decorative numbering ("01 /", "02", step counters) on labels, nav pills or cards. It reads as templated.
- When adding a page, add it to the nav and footer in every file and to `sitemap.xml`.

## SEO

- Each page has its own `<title>` (under 60 characters), meta description (150 to 160 characters), keywords, robots, canonical, Open Graph and Twitter tags, and structured data. Keep og:title, twitter:title, og:description and twitter:description matching the title and description.
- Use the full name "Romeo Nicholas Rozario" in titles and "Romeo Rozario" in descriptions or body copy, so both forms are indexed. The homepage Person schema lists both (`alternateName`).
- Target keywords: digital marketing specialist, content marketing, digital marketing, marketing specialist, SEO, GEO, AEO, SaaS marketing (home, portfolio, blogs); guitarist, musician, producer (music).
- External links open in a new tab with `target="_blank" rel="noopener"`.

## Checking changes

Serve the folder locally (`python3 -m http.server 8765`) and open the pages at desktop (1440px), tablet (768px) and phone (390px) widths, in light and dark mode. Paths are root-relative (`/css/site.css`), so open pages through the server, not as `file://`.
