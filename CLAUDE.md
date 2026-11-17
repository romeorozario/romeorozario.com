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

- Animation hooks are attributes: `data-reveal` (fade up on scroll; `="fade"` or `="scale"` variants), `data-stagger` on a parent to cascade its `data-reveal` children, `data-enter` with `style="--d: <ms>"` for hero entrance.
- Any image with `data-zoom` opens in the lightbox.
- Buttons: `class="btn btn--primary|ink|ghost|outline|dark|line"` with the arrow SVG inside; add `data-magnetic` for the hover pull.
- Text content stays in the HTML (good for SEO and AI crawlers). Animations are progressive enhancement and respect `prefers-reduced-motion`.
- Images live in `images/` by type (`site`, `brand-logos`, `blog-covers`, `social-media-designs`, `ad-creatives`, `ui-ux`, `seo-analytics`, `email-designs`, `music`, `certificates`). Use `.webp`, include `width` and `height`, and `loading="lazy"` below the fold.
- Videos live in `videos/`. Pages use the compressed `*-web.mp4` versions with a poster image; the full-size originals are kept for reference only.
- Writing style: conversational, data-driven, no em dashes.
- When adding a page, add it to the nav and footer in every file and to `sitemap.xml`.

## Checking changes

Serve the folder locally (`python3 -m http.server 8765`) and open the pages at desktop (1440px), tablet (768px) and phone (390px) widths, in light and dark mode. Paths are root-relative (`/css/site.css`), so open pages through the server, not as `file://`.
