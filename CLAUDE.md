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

There are no tests, linters, or formatters configured in this repo. CI just runs `zola build` on PRs (`validate.yml`).

## Architecture

### Theme as submodule
`themes/tabi` is a **git submodule** pointing at `welpo/tabi`. CI checks out with `submodules: recursive`. Dependabot opens daily PRs to bump the submodule SHA. Don't edit files under `themes/tabi/` — they're upstream. Site-level overrides go in `templates/`, `sass/custom.scss`, or `static/`.

### Content layout
Zola's content tree directly maps to URLs:

- `content/blog/<slug>/index.md` — each post is a folder with co-located images under `img/`. Use the page-bundle pattern (folder + `index.md`), not `<slug>.md`.
- `content/projects/` — uses `cards.html` template (see `_index.md`).
- `content/awesome-performance-engineering/_index.md` — **auto-generated**, do not edit by hand. See "Awesome list sync" below.
- `content/pages/` — flat pages (`about/`, `copyright/`).
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
- `sass/custom.scss` → compiled by Zola to `custom.css` (site-specific overrides on top of tabi).
- `static/syntax-dual.css` → dual-theme code highlighting; generated from the giallo sheets, see above.
- `static/custom_subset.css` → font subset (referenced by `custom_subset = true` in config) to avoid Firefox FOUT.

### Tabi-specific config knobs (in `config.toml`)
The `[extra]` section drives most theme behavior: `skin = "lowcontrast_orange"`, `theme_switcher`, `quick_navigation_buttons`, `katex`, the `menu`/`footer_menu`/`socials` arrays, giscus comments (repo `be-next/idle-ti.me-comments`), and umami analytics. Per-page settings in `[extra]` of a post's front matter override config-level values (tabi's settings hierarchy: page > section > config).

CSP is **disabled** (`enable_csp = false`) but the `allowed_domains` array is kept current in case it's re-enabled.

## Awesome list sync (the only "build step" beyond `zola build`)

`content/awesome-performance-engineering/_index.md` is generated by `scripts/sync-awesome-lists.sh`, which:

1. Pulls `README.md` from `be-next/awesome-performance-engineering` (the source repo).
2. Strips the H1 + Awesome badge.
3. Rewrites relative links/images to absolute GitHub URLs.
4. **Patches anchor slugs** — GitHub's slugifier collapses `&` to `--`, Zola collapses it to `-`. The script has a long block of `sed` rules mapping each `--` anchor to `-` (e.g. `#metrics-collection--time-series-storage` → `#metrics-collection-time-series-storage`). When new section headings containing `&` are added upstream, **add a matching sed line** or the in-page TOC links will 404.
5. Prepends Zola front matter and injects badge/star-link blocks before `## Contents`.

The script is triggered by `.github/workflows/sync-awesome-lists.yml` on `repository_dispatch` (event type `awesome-lists-updated`, fired by the source repo) or manual `workflow_dispatch`. It commits and pushes only if the diff under `content/awesome-performance-engineering/` is non-empty.

The sync also `rm -rf`s legacy `observability-tools/` and `performance-testing-tools/` subdirs from the pre-2026-04 multi-file era — do not re-create those paths as content. Their old URLs stay alive as redirects through the `aliases` line of the generated front matter; keep it in the script.

## Deployment pipeline (`publish.yml`)

On push to `main`:
1. `zola build` (with submodules).
2. `aws s3 sync --delete` static assets (CSS/JS/fonts/images) with `Cache-Control: public, max-age=31536000`.
3. `aws s3 sync --delete` content (HTML/XML/JSON/TXT) with `Cache-Control: public, max-age=0, s-maxage=31536000, must-revalidate`.
4. `aws cloudfront create-invalidation --paths "/*"` — counts as one path for billing.

The two-pass `s3 sync` is intentional. Assets get a long browser cache. Content is never cached by browsers (`max-age=0`) but is cached at the edge for a year (`s-maxage`), so HTML is served from the nearest PoP instead of the us-east-1 origin. **The invalidation in step 4 is what purges that edge-cached HTML** — don't collapse the steps, and never ship content without it. `--delete` is scoped by each pass's filters, so neither pass deletes the other's files; S3 versioning keeps deleted or overwritten objects for 5 days.

### CloudFront and DNS configuration (lives in AWS, not in this repo)
Distribution `E2N14H6KQ7G4WH`: origin is the S3 bucket `idle-ti.me` through an OAI, HTTP/2 and HTTP/3, and a viewer-request CloudFront Function `Rewrite_URL` that appends `index.html` to directory URLs. The default behaviour uses:

- **Cache policy `idle-ti-me-static-site`** — honours the origin `Cache-Control` (min TTL 0, max 1 year). The cache key is the path plus the `h` query string only: that is Zola's cache-busting hash (`main.css?h=…`). Before this policy CloudFront ignored the hash and could hand stale CSS to a fresh URL, which browsers then kept for a year. Gzip and Brotli are enabled here — legacy cache settings only ever served gzip.
- **Response headers policy `idle-ti-me-security-headers`** — HSTS (1 year, no subdomains, no preload), `nosniff`, `X-Frame-Options: SAMEORIGIN`, `Referrer-Policy`, `Permissions-Policy`; strips the S3 `Server` header.
- **Custom error response** — S3 answers 403 for a missing key; CloudFront turns it into `/404.html` with status 404.

Route 53 has A and AAAA aliases to the distribution, and a CAA record (`0 issue "amazon.com"`). Any CAA change must keep an Amazon value, or ACM certificate renewal fails.

Region is `us-east-1`. Required GitHub secrets: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET`, `CLOUDFRONT_DISTRIBUTION_ID`, `PUSH_TOKEN` (used by the awesome-list sync workflow to push back).

## Conventions worth knowing

- **Commits**: Dependabot PRs use `⬆️ deps:` prefix; auto-sync uses `sync: …`. Recent human commits are short imperative lines, sometimes with gitmoji shortcodes (`:arrow_up:` etc.). Match the existing style. **Never add `Co-Authored-By` trailers** (or any other co-author attribution) to commits in this repository — keep the authorship clean.
- **Images in posts**: place under `content/blog/<slug>/img/` and reference relatively (`img/foo.webp`) or absolutely (`/blog/<slug>/img/foo.webp`). `.webp` is preferred.
- **Dates in front matter**: `date = YYYY-MM-DD` (unquoted), `updated = "YYYY-MM-DD"` (quoted). Keep this asymmetry — tabi parses both.
