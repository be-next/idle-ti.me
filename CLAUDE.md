# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

`idle-ti.me` is a static site built with [Zola](https://www.getzola.org) (Rust SSG) using the [tabi](https://welpo.github.io/tabi) theme. There is no JavaScript framework, no Node toolchain, no package.json — everything is Markdown, TOML config, SCSS/CSS, and a few shell scripts. The site is deployed to AWS (S3 + CloudFront) via GitHub Actions on every push to `main`.

The pinned Zola version is **0.23.6** (set in `.github/workflows/publish.yml` and `validate.yml`). Match this locally to avoid build divergence. Zola 0.23 replaced the template engine (Tera 2); tabi ≥ v5.0.0 is required, and tabi ≤ v4.2.0 no longer builds.

Two consequences of Tera 2 that bite when editing content:

- **Shortcodes are components.** They live in `templates/components/` (not `templates/shortcodes/`), declare typed parameters, and close by name: `{% component foo(bar: string) %} … {% endcomponent foo %}`. Call them as `{% <foo bar="x"> %} … {% </foo> %}` for block form, `{{< foo bar="x" />}}` for inline form. Note that arguments are space-separated, with no commas.
- **`{{ … }}` and `{% … %}` are now parsed inside fenced code blocks.** Any code sample containing template-like syntax (GitHub Actions `${{ secrets.X }}`, Jinja, Vue, JSX) must be wrapped in `{% raw %}` / `{% endraw %}` around the fence, or the build fails with `Variable … is not defined`. This is deliberate upstream — see [zola#3263](https://github.com/getzola/zola/issues/3263). `content/blog/zola-aws/index.md` is the current example.

## Common commands

```bash
# Local dev server, opens browser, includes drafts
zola serve --open --drafts

# Production-equivalent build (output goes to ./public, gitignored)
zola build

# Manually re-pull the awesome-performance-engineering content
bash scripts/sync-awesome-lists.sh

# After cloning, the tabi theme is a git submodule — required for builds
git submodule update --init --recursive
```

There are no tests, linters, or formatters configured in this repo. CI (`validate.yml`, on pull requests) runs `zola build`, then a Lighthouse CI budget; `publish.yml` runs the same measurement on every deploy (see "Front-end budget" below).

```bash
# Redraw social media cards after adding a post or changing a title/description
python3 scripts/social_cards.py
# Regenerate the font subsets after changing the site title or menu (checks coverage of public/)
zola build && python3 scripts/subset_fonts.py
# Both need: pip install fonttools brotli pillow

# The CI budget, locally (needs Node and Chrome; leaves a measurement build in public/)
bash scripts/measure.sh && npx @lhci/cli@0.16.0 assert
# Then, to see the /performance/ page with these figures under zola serve
python3 scripts/performance_data.py
# Field data from CloudFront's logs (needs read access to the idle-ti-me-logs bucket)
aws s3 sync s3://idle-ti-me-logs/ logs/ && python3 scripts/field_data.py logs/
```

## Architecture

### Theme as submodule
`themes/tabi` is a **git submodule** pointing at `welpo/tabi`. CI checks out with `submodules: recursive`. Dependabot opens weekly PRs (Mondays) to bump the submodule SHA, and groups the GitHub Actions updates in a second weekly PR. Don't edit files under `themes/tabi/` — they're upstream. Site-level overrides go in `templates/`, `sass/custom.scss`, or `static/`.

### Content layout
Zola's content tree directly maps to URLs:

- `content/blog/<slug>/index.md` — each post is a folder with co-located images under `img/`. Use the page-bundle pattern (folder + `index.md`), not `<slug>.md`.
- `content/projects/` — uses `cards.html` template (see `_index.md`).
- `content/awesome-performance-engineering/_index.md` — **auto-generated**, do not edit by hand. See "Awesome list sync" below.
- `content/pages/` — flat pages (`about/`, `library/`, `copyright/`, `performance/`), each with a custom `path =`.
- `content/pages/performance/` — the public performance page, in three parts: lab (`data.json`, Lighthouse, rendered by the `performance_report` component), edge and real readers (`field.json`, CloudFront logs, rendered by `field_report`). Both files are **generated on each deploy and gitignored** (see "Front-end budget" and "Field data"); each component shows a notice when its file is missing or its samples are too few.
- `content/archive/_index.md` — uses `archive.html` template for the full post list.
- `content/_index.md` — landing page (uses `section_path = "blog/_index.md"` to surface latest posts).

Front matter is TOML between `+++` fences. Posts conventionally include `[taxonomies]` (with `tags`) and `[extra]` (per-page tabi flags like `giscus` and `copy_button`). Footnote backlinks are native — `[markdown] bottom_footnotes = true` in `config.toml`; tabi's old `footnote_backlinks` flag no longer exists.

Drafts are kept inline (e.g. `content/blog/draft-02/`) with `draft = true` in front matter; they only appear under `zola serve --drafts`.

### Syntax highlighting (`syntax-dual.css` is load-bearing — do not drop it)
`config.toml` sets `[markdown.highlighting]` with `light_theme = "github-light"`, `dark_theme = "catppuccin-frappe"` and `style = "class"`. Zola generates two stylesheets **into the build output** (`public/giallo-light.css`, `public/giallo-dark.css`), with disjoint class prefixes: `.z-l-*` for light, `.z-d-*` for dark. Every token span carries classes from *both* palettes.

tabi v5 injects both files with **no `media` attribute** (`themes/tabi/templates/partials/header.html`), so the dark sheet — loaded second — wins everywhere, and neither sheet knows about tabi's `data-theme` switcher. Left alone, code blocks render dark on a light page, with the wrong colours.

`static/syntax-dual.css` fixes this. Loaded last via `extra.stylesheets`, it re-declares each palette scoped to its own theme at specificity (0,2,0) — `:root:not([data-theme='dark'])`, `[data-theme='dark']`, and a `prefers-color-scheme` block for readers who never toggled — and neutralises the opposite palette, which the raw sheets (0,1,0) cannot override. **Regenerate it from `giallo-{light,dark}.css` after changing either theme**; its own header comment carries the procedure.

Zola ≤ 0.22 wrote the giallo files into `static/` instead. The `static/giallo-*.css` line in `.gitignore` is kept as a guard: a leftover copy there shadows the generated one and silently breaks every code block.

### Custom styles
- `sass/custom.scss` → compiled by Zola to `custom.css` (site-specific overrides on top of tabi): underlined links in running text, 24 px header touch targets, `a code` colour, hidden empty `a.u-url`, view transitions.
- `sass/skins/accessible_orange.scss` → the site skin (`skin = "accessible_orange"`): tabi's `lowcontrast_orange` with light-theme `--primary-color: #c25400` (4.6:1 on white; upstream #f56a00 is 3.02:1), plus `--link-on-grey-color` (#a84900) for links on tabi's greys: inline code inside links (#e7e7e7) and striped table rows (#f0f0f0). Any new light-theme colour on white, #f0f0f0 or #e7e7e7 must keep 4.5:1.
- `static/syntax-dual.css` → dual-theme code highlighting; generated from the giallo sheets, see above.
- `static/custom_subset.css` → 'Inter Subset' header font (`custom_subset = true`), cut to the site title + menu by `scripts/subset_fonts.py`. Regenerate it when the title or menu changes.

### Fonts are subset (`static/fonts/` shadows the theme)
`static/fonts/Inter4.woff2` and `static/fonts/SourceSerif4Variable-Roman.ttf.woff2` are Latin subsets of tabi's files, generated by `scripts/subset_fonts.py` from `themes/tabi/static/fonts/`. Same file names, so Zola copies them over the theme's and tabi's `@font-face` rules pick them up. A character outside `UNICODES` in that script falls back to a system font: after adding content with unusual characters, run `zola build && python3 scripts/subset_fonts.py` — it lists any character used in `public/` that the subsets dropped. Re-run it if a tabi update changes the font files.

### Head extension, CSP, social cards
- `templates/tabi/extend_head.html` overrides tabi's empty extension point to inject: font preloads (Inter everywhere, Source Serif on `blog/` and `projects/` pages — without them the serif article measured 0.15 CLS on GitHub's Ubuntu runners, whose fallback fonts differ); Speculation Rules (`prefetch`, `moderate` eagerness — not `prerender`: prerendered pages run Umami and would count views nobody made); and the real-user metrics module `static/js/rum.js` (see "Field data").
- CSP is on (`enable_csp = true`) as a `<meta>` tag built by tabi from `allowed_domains`; tabi adds Umami and giscus domains itself. `'inline-speculation-rules'` in `script-src` is what lets the speculation rules through — no other inline script is allowed. Under `zola serve`, the livereload inline script is blocked (harmless, serve-only).
- `social_media_card = "social_card.png"` in config: tabi looks next to the page, then the parent folder, then `static/`. `scripts/social_cards.py` draws one per page bundle. Pages with a custom `path =` (about, library, copyright) get theirs under `static/pages/<name>/` instead: tabi builds their og:image URL from the content path while Zola publishes colocated files under `path`, so a colocated card would 404.

### Tabi-specific config knobs (in `config.toml`)
The `[extra]` section drives most theme behavior: `skin = "lowcontrast_orange"`, `theme_switcher`, `quick_navigation_buttons`, `katex`, the `menu`/`footer_menu`/`socials` arrays, giscus comments (repo `be-next/idle-ti.me-comments`), and umami analytics. Per-page settings in `[extra]` of a post's front matter override config-level values (tabi's settings hierarchy: page > section > config).

CSP is **enabled** — see "Head extension, CSP, social cards" above. A new third-party embed (script, iframe, font) needs its domain in `allowed_domains` or it is blocked.

## Awesome list sync (the only "build step" beyond `zola build`)

`content/awesome-performance-engineering/_index.md` is generated by `scripts/sync-awesome-lists.sh`, which:

1. Pulls `README.md` from `be-next/awesome-performance-engineering` (the source repo).
2. Strips the H1 + Awesome badge.
3. Rewrites relative links to absolute GitHub URLs, and **self-hosts the images** the README references under `media/` (the logo): downloaded flat next to `_index.md` (Zola publishes a section's own files, not its subfolders), with a `height` derived from the SVG viewBox so the page doesn't shift while the logo loads. From raw.githubusercontent.com the logo was the page's LCP and caused a 0.27 CLS — the Lighthouse budget fails on that page if it comes back.
4. **Patches anchor slugs** — GitHub's slugifier collapses `&` to `--`, Zola collapses it to `-`. The script has a long block of `sed` rules mapping each `--` anchor to `-` (e.g. `#metrics-collection--time-series-storage` → `#metrics-collection-time-series-storage`). When new section headings containing `&` are added upstream, **add a matching sed line** or the in-page TOC links will 404.
5. Prepends Zola front matter and injects badge/star-link blocks before `## Contents`.

The script is triggered by `.github/workflows/sync-awesome-lists.yml` on `repository_dispatch` (event type `awesome-lists-updated`, fired by the source repo) or manual `workflow_dispatch`. It commits and pushes only if the diff under `content/awesome-performance-engineering/` is non-empty.

The sync also `rm -rf`s legacy `observability-tools/` and `performance-testing-tools/` subdirs from the pre-2026-04 multi-file era — do not re-create those paths as content. Their old URLs stay alive as redirects through the `aliases` line of the generated front matter; keep it in the script.

## Deployment pipeline (`publish.yml`)

On push to `main`, daily at 05:17 UTC (refresh of the performance page) and on `workflow_dispatch`; `concurrency: publish` serialises runs:
1. `aws-actions/configure-aws-credentials` (pinned by SHA) exchanges a GitHub OIDC token for short-lived credentials of the IAM role `github-actions-idle-ti-me-deploy`. There are **no long-lived AWS keys** anywhere: the role's trust policy only accepts `repo:be-next/idle-ti.me:ref:refs/heads/main`, so pull requests and other branches can't deploy. Its inline policy `deploy-idle-ti-me` allows `ListBucket` on the bucket, `Get/Put/DeleteObject` on its objects, invalidations on this distribution, and read-only `ListBucket`/`GetObject` on the logs bucket `idle-ti-me-logs`. The workflow needs `permissions: id-token: write`. If the repository ever opts into GitHub's immutable OIDC subjects (`repo:owner@id/repo@id:…`), deploys will fail with `Not authorized to perform sts:AssumeRoleWithWebIdentity` until the trust policy's `sub` condition is updated to the new format.
2. Lighthouse measurement of the build about to ship (`scripts/measure.sh`), turned into `content/pages/performance/data.json` by `scripts/performance_data.py`. `continue-on-error`: a broken measurement never blocks a deploy.
3. `aws s3 sync s3://idle-ti-me-logs/ logs/` then `scripts/field_data.py` → `content/pages/performance/field.json`. Also `continue-on-error`. Keep it quiet (`--only-show-errors`, counts only): workflow logs are public and the log keys contain the AWS account ID.
4. `rm -rf public && zola build` (with submodules) — from scratch, because the measurement left a build with 127.0.0.1 URLs and `.gz` copies in `public/`.
5. `aws s3 sync --delete` static assets (CSS/JS/fonts/images) with `Cache-Control: public, max-age=31536000`.
6. `aws s3 sync --delete` content (HTML/XML/JSON/TXT) with `Cache-Control: public, max-age=0, s-maxage=31536000, must-revalidate`.
7. `aws cloudfront create-invalidation --paths "/*"` — counts as one path for billing. **The daily scheduled run invalidates `/performance/*` only**: the rest of its build is byte-identical to what the edges hold (same commit), and a daily full purge would make every reader's first page a cache miss.
8. `lhci assert` (the budget), after the deploy: a page over budget turns the run red without holding back the publication. A failed measurement or unreadable logs do too.

The two-pass `s3 sync` is intentional. Assets get a long browser cache. Content is never cached by browsers (`max-age=0`) but is cached at the edge for a year (`s-maxage`), so HTML is served from the nearest PoP instead of the us-east-1 origin. **The invalidation in step 7 is what purges that edge-cached HTML** — don't collapse the steps, and never ship content without it. `--delete` is scoped by each pass's filters, so neither pass deletes the other's files; S3 versioning keeps deleted or overwritten objects for 5 days.

### CloudFront and DNS configuration (lives in AWS, not in this repo)
Distribution `E2N14H6KQ7G4WH`: origin is the S3 bucket `idle-ti.me` through the Origin Access Control `idle-ti-me-s3` (the bucket policy grants `s3:GetObject` to `cloudfront.amazonaws.com`, conditioned on this distribution's ARN), HTTP/2 and HTTP/3, and a viewer-request CloudFront Function `Rewrite_URL` that appends `index.html` to directory URLs. The default behaviour uses:

- **Cache policy `idle-ti-me-static-site`** — honours the origin `Cache-Control` (min TTL 0, max 1 year). The cache key is the path plus the `h` query string only: that is Zola's cache-busting hash (`main.css?h=…`). Before this policy CloudFront ignored the hash and could hand stale CSS to a fresh URL, which browsers then kept for a year. Gzip and Brotli are enabled here — legacy cache settings only ever served gzip.
- **Response headers policy `idle-ti-me-security-headers`** — HSTS (1 year, no subdomains, no preload), `nosniff`, `X-Frame-Options: SAMEORIGIN`, `Referrer-Policy`, `Permissions-Policy`; strips the S3 `Server` header.
- **Custom error response** — S3 answers 403 for a missing key; CloudFront turns it into `/404.html` with status 404.

One extra cache behaviour, **`/rum/*`**: all HTTP methods (`sendBeacon` posts), `https-only`, managed policy `CachingDisabled`, and the viewer-request CloudFront Function `rum-beacon`, which answers every request with an empty `204` (`cache-control: no-store`) — nothing reaches the origin. Its whole code is that `return { statusCode: 204, … }`.

**Access logs**: CloudFront standard logging v2 (CloudWatch Logs delivery `idle-ti-me-access-logs` → destination `idle-ti-me-logs-s3`), JSON lines, gzipped, into the private bucket `idle-ti-me-logs` under `AWSLogs/<account>/CloudFront/yyyy/MM/dd/HH/`. Only 15 fields are delivered — `timestamp`, `x-edge-location`, `cs-method`, `cs-uri-stem`, `sc-status`, `sc-bytes`, `sc-content-type`, the three `x-edge-*result-type`, `time-to-first-byte`, `time-taken`, `origin-fbl`, `cs-protocol-version`, `cache-behavior-path-pattern`: **no IP address, user agent, referrer, cookie or query string**. Don't add them back: the performance page tells readers they aren't kept. A lifecycle rule deletes logs after 35 days (the field window is 28). Bucket policy: `delivery.logs.amazonaws.com` may `PutObject` (source account and delivery-source ARN conditions), plain HTTP denied.

Route 53 has A and AAAA aliases to the distribution, and a CAA record (`0 issue "amazon.com"`). Any CAA change must keep an Amazon value, or ACM certificate renewal fails.

Region is `us-east-1`. Required GitHub secrets: `AWS_ROLE_ARN` (the deploy role, kept as a secret so the AWS account ID stays out of this public repo), `S3_BUCKET`, `CLOUDFRONT_DISTRIBUTION_ID`, `PUSH_TOKEN` (used by the awesome-list sync workflow to push back).

## Front-end budget (`lighthouserc.json`)

`scripts/measure.sh` rebuilds with `--base-url http://127.0.0.1:8080` (otherwise absolute URLs load production assets), gzips text files like CloudFront, and runs `lhci collect` (served by `http-server --gzip`) on five pages, 3 runs each. `validate.yml` (pull requests) then runs `lhci assert`; `publish.yml` (main) feeds the reports to `scripts/performance_data.py` before building, and asserts after the deploy. The budget fails on: performance < 95, accessibility / best practices / SEO < 100, LCP > 2.5 s, CLS > 0.05, TBT > 100 ms, fonts > 225 KB. Umami and giscus are blocked during the runs (no fake page views, no third-party noise). Reports are uploaded as the `lighthouse-reports` artifact by both workflows.

The budget thresholds live only in `lighthouserc.json`: `performance_data.py` copies them into `data.json`, and the performance page prints its *Budget* rows from there. Adding a page to the `url` list adds it to the page's tables too (title read from the measured build's `<title>`). Known upstream gaps that keep some pages below 100 but are outside the budgeted pages: tabi's archive and tags templates have no `<main>` landmark.

## Field data (`scripts/field_data.py`, `static/js/rum.js`)

Both parts come from CloudFront's access logs (see "Access logs" above), over the last 28 days; under 20 samples, a figure is replaced by "not enough data".

- **Edge** — HTML requests (GET, 200/304, `text/html`): per PoP (first three letters of `x-edge-location`, an IATA code mapped to a city in the script), pages served, cache hit ratio (`x-edge-result-type == Hit`), `time-to-first-byte` p50/p95. That TTFB is measured by CloudFront from the request's arrival to the first byte sent: it shows cache effectiveness and origin latency (`origin-fbl` on misses, ~280 ms from Paris to us-east-1), not the reader's network. Bots and crawlers are included — the logs have no user agent to filter them.
- **Real readers** — `rum.js` (a module loaded on every page) uses web-vitals 6.2.3, vendored as `static/js/web-vitals-6.2.3.js` (version in the file name because static assets are cached a year; upgrade by adding the new file and changing the import). On `visibilitychange` → hidden or `pagehide`, it sends one beacon `/rum/1/p=<encoded path>;n=<navigationType>;d=<m|d>;lcp=…;inp=…;cls=…;fcp=…;ttfb=…` with `navigator.sendBeacon`. The data is in the **path**, not a query string, because query strings aren't logged. The beacon is sent only when `location.hostname === 'idle-ti.me'`; elsewhere (zola serve, Lighthouse CI) it is printed with `console.debug`. The script drops beacons that don't parse, have an unknown navigation type or values out of bounds (they are unauthenticated). Percentiles are nearest-rank; p75 and the good / needs improvement / poor shares use Google's thresholds, as CrUX does.

Changing the beacon format: bump the `/rum/1/` version segment and teach `field_data.py` both, until the old one has aged out of the 35-day logs.

## Conventions worth knowing

- **Commits**: Dependabot PRs use `⬆️ deps:` prefix; auto-sync uses `sync: …`. Recent human commits are short imperative lines, sometimes with gitmoji shortcodes (`:arrow_up:` etc.). Match the existing style. **Never add `Co-Authored-By` trailers** (or any other co-author attribution) to commits in this repository — keep the authorship clean.
- **Images in posts**: place under `content/blog/<slug>/img/` and reference relatively (`img/foo.webp`) or absolutely (`/blog/<slug>/img/foo.webp`). `.webp` is preferred.
- **Dates in front matter**: `date = YYYY-MM-DD` (unquoted), `updated = "YYYY-MM-DD"` (quoted). Keep this asymmetry — tabi parses both.
