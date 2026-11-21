# idle-ti.me website

![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/be-next/idle-ti.me?logo=github)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/be-next/idle-ti.me/publish.yml?label=build%20%26%20publish)

Source of [idle-ti.me](https://idle-ti.me) — articles, curated tools and projects on performance engineering and observability. The site is built with [Zola](https://www.getzola.org) and the [tabi](https://welpo.github.io/tabi) theme, and served from Amazon S3 through CloudFront.

## Stack

| | |
|---|---|
| Generator | Zola 0.23.6, pinned in CI |
| Theme | tabi v5, as a git submodule in `themes/tabi`, kept up to date by Dependabot |
| Hosting | private Amazon S3 bucket behind CloudFront, DNS in Route 53 |
| CI/CD | GitHub Actions: build on every pull request, build and deploy on every push to `main` |
| Comments, analytics | giscus, Umami |

## Local development

```bash
git clone --recurse-submodules https://github.com/be-next/idle-ti.me.git
cd idle-ti.me
zola serve --drafts   # http://127.0.0.1:1111
zola build            # production build into ./public
```

Use Zola 0.23.6 locally as well: tabi v5 relies on Tera 2 components, which older versions of Zola cannot parse. If the repository was cloned without its submodules, run `git submodule update --init --recursive`.

## Repository layout

| Path | Contents |
|---|---|
| `content/` | Markdown sources: `blog/` (one folder per post, `index.md` plus `img/`), `projects/`, `pages/` (about, library, copyright), `awesome-performance-engineering/` |
| `templates/components/` | Site components: `number_card`, `capability_card`, `timeline`… |
| `sass/custom.scss` | Site-specific styles on top of tabi |
| `static/syntax-dual.css` | Light and dark code highlighting, see [below](#code-highlighting) |
| `scripts/sync-awesome-lists.sh` | Regenerates the tools page from [awesome-performance-engineering](https://github.com/be-next/awesome-performance-engineering) |
| `.github/workflows/` | `validate.yml` (pull request build), `publish.yml` (deploy), `sync-awesome-lists.yml` |

## Writing content with Zola 0.23

Zola 0.23 moved to Tera 2, which changes two things when writing Markdown:

- **Shortcodes are now components.** Block form: `{% <references> %} … {% </references> %}`. Inline form: `{{< number_card value="8" label="industries" />}}` — arguments are separated by spaces, not commas.
- **`{{ … }}` and `{% … %}` are parsed inside fenced code blocks too.** Wrap any sample that contains them — a GitHub Actions `${{ secrets.X }}`, Jinja, JSX — in `{% raw %}` / `{% endraw %}`.

The tools page, `content/awesome-performance-engineering/_index.md`, is generated: change the source repository or the sync script, never the file itself.

## Deployment

On every push to `main`, `publish.yml`:

1. builds the site with `zola build`;
2. syncs the static assets to S3 with `Cache-Control: public, max-age=31536000`;
3. syncs the content (HTML, XML, JSON, TXT) with `Cache-Control: public, max-age=0, s-maxage=31536000, must-revalidate`: browsers revalidate on every visit, while CloudFront keeps the pages at the edge;
4. invalidates `/*` on CloudFront, which is what purges that edge-cached content.

Both syncs use `--delete`, so a file that leaves the build leaves the bucket too. S3 versioning keeps every overwritten or deleted object for 5 days.

The CloudFront side is configured in AWS, not in this repository:

- a CloudFront Function on viewer requests appends `index.html` to directory URLs;
- a custom error response turns the 403 that S3 returns for a missing key into `/404.html` with a 404 status;
- a cache policy honours the origin `Cache-Control`, keys on Zola's `?h=` cache-busting hash, and serves Brotli;
- a response headers policy adds HSTS, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` and `Permissions-Policy`;
- HTTP/3 and IPv6 are enabled, and Route 53 holds A and AAAA aliases plus a CAA record for ACM.

The article [Zola: How to deploy a website using S3 Bucket and CloudFront](https://idle-ti.me/blog/zola-aws/) explains each of these choices and gives the configurations to reproduce them.

Repository secrets used by the workflows: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET`, `CLOUDFRONT_DISTRIBUTION_ID`, and `PUSH_TOKEN` for the tools-page sync.

### Code highlighting

`config.toml` sets a light (`github-light`) and a dark (`catppuccin-frappe`) highlighting theme. Zola generates one stylesheet per theme and tabi loads both unconditionally, so the dark palette would win everywhere. `static/syntax-dual.css`, loaded last, scopes each palette to its own theme and follows tabi's theme switcher. Regenerate it after changing either theme: the procedure is in its header.

## License

Unless otherwise noted, the content of the site is available under [CC BY-SA 4.0](https://idle-ti.me/copyright/).
