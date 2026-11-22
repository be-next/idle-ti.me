+++
title = "Zola: How to deploy a website using S3 Bucket and CloudFront"
date = 2024-03-11
updated = "2026-11-21"
draft = false
toc = true

description = "Deploying a Zola website on an S3 bucket via CloudFront raises a few traps the official guide doesn't cover: sub-pages that don't resolve, 403s instead of 404s, and a cache that is either stale or slow. Here are the configurations I use to make it work, fast and secure — revised after auditing my own setup two years later."

[taxonomies]
tags = ["Zola", "AWS", "S3 bucket", "CloudFront", "static website"]

[extra]
giscus = true
copy_button = true
+++

{% <admonition type="info" title="Revised in November 2026"> %}
Two years after the first version, I audited this setup and found that it worked — just not as well as I thought. HTML was never cached at the edge, CloudFront ignored Zola's cache-busting hash, the distribution served neither Brotli, nor HTTP/3, nor a single security header, and the deploy relied on an access key created in 2024. Sections 2 and 3 are rewritten — section 3 also corrects advice the 2024 version got wrong — and section 4 is new.
{% </admonition> %}

## When RTFM isn't Enough 😉

As we all do, the first thing I did to deploy my Zola website using an S3 bucket and CloudFront was to follow the [Zola documentation](https://www.getzola.org/documentation/deployment/aws-s3/). And... once deployed, I found that the site didn't work as well as expected.

I was faced with the following problems:

1. When I try to access a sub-page, CloudFront doesn't serve its `index.html` file. To solve this, I had to create a CloudFront Function (it could have been a Lambda@Edge) that rewrites the URL to point to the `index.html` file.
2. The `404.html` error page is never displayed. When I try to access a non-existent page, I get a 403 error instead. To solve this, I had to configure a custom **error response** in the CloudFront distribution.
3. Updates don't show up, because CloudFront keeps serving its cached copies. The GitHub Action given in the Zola documentation invalidates the whole CloudFront cache on each deploy, which fixes freshness — but, as I found out later, a cache that is both fresh *and* fast takes a little more care.

In this article, I share the method I used to solve these problems. Let me know if there are simpler or more effective methods!

## 1. Redirecting to the file: CloudFront Function

When we access a sub-page of the website, CloudFront doesn't serve its `index.html` file. And if you've configured the `404.html` error page as described below, you'll get a 404 error instead of the expected page.
CloudFront has a *default root object* setting, but as its name suggests, it only applies to the root of the website! Fortunately, CloudFront also provides CloudFront Functions, which can rewrite URLs on the fly.
To create a CloudFront Function that rewrites requests to the right `index.html` file, you can follow the example provided by AWS:

- [Add index.html to request URLs that don't include a file name](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/example-function-add-index.html)
- [GitHub repository](https://github.com/aws-samples/amazon-cloudfront-functions/tree/main/url-rewrite-single-page-apps)

This example provides the following code:

```javascript, linenos
function handler(event) {
    var request = event.request;
    var uri = request.uri;

    // Check whether the URI is missing a file name.
    if (uri.endsWith('/')) {
        request.uri += 'index.html';
    }
    // Check whether the URI is missing a file extension.
    else if (!uri.includes('.')) {
        request.uri += '/index.html';
    }
    return request;
}
```

Once you've created and published this function, associate it (I've called it `Rewrite_URL`) with the `Default (*)` behaviour of the CloudFront distribution, on the *viewer request* event:
[![CloudFront function](/blog/zola-aws/img/function_associations.png)](/blog/zola-aws/img/function_associations.png)

A multilingual site needs nothing more. The first version of this article guessed that each language would need its own function and behaviour; it doesn't. Zola writes translated pages under a language prefix[^1], with the same `index.html` layout, which the function above already handles.

## 2. The Case of the Misleading Errors: 404 vs 403

### Problem statement

When accessing non-existent pages or resources on a static website generated with Zola and hosted on an Amazon S3 bucket served through CloudFront, we get a 403 Forbidden error instead of the expected 404 Not Found. This happens even though CloudFront can read every existing object. The S3 bucket has public access blocked, so that CloudFront is the only entry point for users.

### Underlying cause

The 403 comes from S3 itself. When a client asks for a key that doesn't exist, S3 answers 404 only if that client is allowed to list the bucket (`s3:ListBucket`); otherwise it answers 403 Access Denied, so as not to reveal which keys exist[^2]. CloudFront is only allowed `s3:GetObject` — as it should be — so every missing page comes back as a 403.

### Solution: Configuring CloudFront and S3 for Correct Error Handling

#### Restrict the bucket to CloudFront

The bucket blocks all public access: only CloudFront may read it. When I first set this up, following the AWS guide [Use an Amazon CloudFront distribution to serve a static website](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/getting-started-cloudfront-overview.html), I used an OAI (Origin Access Identity). AWS now labels OAI as legacy and recommends Origin Access Control (OAC)[^3], which I've switched to. With OAC, CloudFront signs its requests to S3, and the bucket policy grants read access to the CloudFront service — for your distribution only:

```json, linenos
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowCloudFrontOAC",
            "Effect": "Allow",
            "Principal": { "Service": "cloudfront.amazonaws.com" },
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::yourbucketname/*",
            "Condition": {
                "StringEquals": {
                    "AWS:SourceArn": "arn:aws:cloudfront::YOUR_ACCOUNT_ID:distribution/YOUR_DISTRIBUTION_ID"
                }
            }
        }
    ]
}
```

Replace `yourbucketname`, `YOUR_ACCOUNT_ID` and `YOUR_DISTRIBUTION_ID` with your own values, and select the OAC on the distribution's S3 origin.

To migrate an existing distribution without downtime, let the bucket policy allow both the OAI and the OAC, switch the origin to the OAC, check that objects not yet in the cache still load, then remove the OAI statement and delete the OAI.

#### Configure a custom error response in CloudFront

To return a proper 404, we configure a custom error response in CloudFront:

1. Open the CloudFront distribution for your website.
2. Go to the **Error pages** tab.
3. Choose **Create custom error response**.
4. **HTTP error code**: 403: Forbidden.
5. **Error caching minimum TTL**: a short value — I use 10 seconds.
6. **Customize error response**: Yes.
7. **Response page path**: `/404.html`.
8. **HTTP Response code**: 404: Not Found.
9. Choose **Create custom error response**.

There is no need to configure a response for the 404 code itself: as we have seen, S3 never returns one here. A missing page triggers a 403, which CloudFront now turns into a 404 served with your error page. Granting `s3:ListBucket` would make S3 return 404 directly, but I prefer to keep CloudFront's permissions to the strict minimum.

## 3. Caching: fresh *and* fast

By default, CloudFront keeps a response from S3 for 24 hours when nothing tells it otherwise[^4], so an update to the bucket doesn't show up right away. The first version of this article stopped at the obvious cure — invalidate the whole cache on every deploy — and that does keep the site fresh. But when I audited the setup two years later, I found it slow exactly where it mattered, and subtly wrong in one corner. Here is the setup I run today.

### Two kinds of files, two `Cache-Control` headers

The deploy uploads files in two passes, with different headers. Assets are kept for a year, by browsers and CloudFront alike. Content is revalidated by browsers on every visit, but kept by CloudFront at the edge:

| Files | `Cache-Control` |
|---|---|
| CSS, JS, fonts, images | `public, max-age=31536000` |
| HTML, XML, JSON, TXT | `public, max-age=0,`<br>`s-maxage=31536000, must-revalidate` |

The second line is the one I got wrong. My content was uploaded with `max-age=0` alone, and CloudFront applied it to itself too: every HTML request went back to the S3 origin in `us-east-1` to revalidate (`x-cache: RefreshHit`), for a time to first byte of about 300 ms from Paris. `s-maxage` is the directive meant for shared caches: CloudFront follows it, capped by the maximum TTL of its cache policy, while browsers keep following `max-age`[^5]. The HTML now comes from the nearest edge location (`x-cache: Hit`, about 40 ms).

Caching HTML for a year at the edge sounds reckless. It's safe here because every deploy invalidates `/*` (see the workflow below): the invalidation is no longer a convenience, it's what keeps the edge cache correct.

### Let Zola's cache-busting hash through

Assets cached for a year raise the opposite question: how does a browser ever get a new stylesheet? Zola answers it. `get_url(..., cachebust=true)` appends a hash of the file to its URL, `?h=<sha256>`[^6], and tabi uses it for its CSS and JavaScript: a new stylesheet means a new URL.

But CloudFront only honours that if the query string is part of its cache key — and mine wasn't. With the legacy cache settings, my distribution kept only a `versionId` parameter in the key (more on that below) and dropped `h`: `main.css?h=anything` returned the cached file. In the seconds between uploading new HTML and the end of the invalidation, a visitor could get the old stylesheet under the new URL — and their browser would keep it for a year.

The fix is a cache policy that keeps `h` in the key. It is also the only way to get Brotli compression, which CloudFront doesn't support with legacy cache settings[^7]:

```json, linenos
{
  "Name": "idle-ti-me-static-site",
  "Comment": "Honours origin Cache-Control. Cache key = path + ?h= (Zola cache-busting hash). Gzip + Brotli.",
  "DefaultTTL": 86400,
  "MaxTTL": 31536000,
  "MinTTL": 0,
  "ParametersInCacheKeyAndForwardedToOrigin": {
    "EnableAcceptEncodingGzip": true,
    "EnableAcceptEncodingBrotli": true,
    "HeadersConfig": { "HeaderBehavior": "none" },
    "CookiesConfig": { "CookieBehavior": "none" },
    "QueryStringsConfig": {
      "QueryStringBehavior": "whitelist",
      "QueryStrings": { "Quantity": 1, "Items": ["h"] }
    }
  }
}
```

Create it with `aws cloudfront create-cache-policy --cache-policy-config file://cache-policy.json`, then select it on the `Default (*)` behaviour. The managed *CachingOptimized* policy would not do: it leaves every query string out of the key.

### The deployment workflow

Here is the GitHub Action I use today. Compared with the one suggested in the Zola documentation, it uploads in two passes to set the two `Cache-Control` headers above, it adds `--delete`, and it holds no AWS key:

{% raw %}
```yaml, linenos
name: Build and Publish to AWS
on:
  push:
    branches:
      - main

# No long-lived AWS keys: the job requests a short-lived OIDC token from GitHub
# and exchanges it for credentials of an IAM role that only this repository's
# main branch can assume (trust policy on the `sub` claim).
permissions:
  id-token: write
  contents: read

jobs:
  run:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive
      - uses: taiki-e/install-action@v2
        with:
          tool: zola@0.23.6
      - name: Build
        run: zola build

      # Pinned by commit SHA: this action handles the AWS credentials.
      # Dependabot (github-actions ecosystem) keeps the pin up to date.
      - name: Configure AWS credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@e1253824e5c10ff9df46874f81ed3ec929e19cfd # v6.3.0
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: us-east-1

      # Static assets: long cache (1 year) — CSS, JS, fonts, images.
      # --delete removes assets that left the build; filters scope it to this
      # pass's extensions, so the content pass below is untouched.
      - name: Deploy static assets
        run: |
          aws s3 sync public/ s3://${{ secrets.S3_BUCKET }}/ --delete \
            --exclude "*" \
            --include "*.css" --include "*.js" \
            --include "*.woff" --include "*.woff2" --include "*.ttf" --include "*.eot" \
            --include "*.png" --include "*.jpg" --include "*.jpeg" \
            --include "*.webp" --include "*.avif" --include "*.svg" \
            --include "*.gif" --include "*.ico" \
            --cache-control "public, max-age=31536000"

      # Content pages — HTML, XML, JSON, TXT. Browsers always revalidate
      # (max-age=0); CloudFront keeps them at the edge (s-maxage=1y) until the
      # invalidation below purges them. Without s-maxage every HTML request went
      # back to the us-east-1 origin: ~300 ms TTFB from Europe instead of ~50 ms.
      - name: Deploy content
        run: |
          aws s3 sync public/ s3://${{ secrets.S3_BUCKET }}/ --delete \
            --exclude "*" \
            --include "*.html" --include "*.xml" --include "*.xsl" \
            --include "*.json" --include "*.txt" \
            --cache-control "public, max-age=0, s-maxage=31536000, must-revalidate"

      # Invalidate all CloudFront edges so new content + headers take effect.
      # This is also what purges the edge-cached HTML: never deploy without it.
      # "/*" counts as a single invalidation path for billing (first 1000/month free).
      - name: Invalidate CloudFront cache
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ secrets.CLOUDFRONT_DISTRIBUTION_ID }} \
            --paths "/*"
```
{% endraw %}

There are no AWS credentials in the repository. GitHub issues the job a short-lived OIDC token (`permissions: id-token: write`), and `aws-actions/configure-aws-credentials` exchanges it for temporary credentials of an IAM role[^8]. The role's trust policy only accepts this repository's `main` branch — `repo:be-next/idle-ti.me:ref:refs/heads/main` — so a pull request or another branch cannot deploy, and its permissions cover the site's bucket and invalidations on its distribution, nothing more. The access key that sat in the repository secrets since 2024 is gone. Since this action handles the credentials, it is pinned by commit SHA rather than by tag.

Without `--delete`, `aws s3 sync` never removes anything: files that leave the build stay online forever. I found eleven of them, including two pages retired seven months earlier and still answering 200. With `--delete`, files in the bucket that are no longer in the build are removed — and since files excluded by the filters are excluded from deletion too[^9], each pass only cleans up its own file types. If a retired URL deserves to survive, Zola's `aliases` front-matter field generates a redirect page in its place.

To invalidate by hand, run `aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"`. The `/*` wildcard counts as a single path for billing.

### S3 versioning: a safety net, not cache busting

The 2024 version of this article suggested enabling S3 versioning and adding a `versionId` query string to the cache key, "to update resources without invalidating the whole cache". I was wrong. For that to do anything, the URLs in the pages would have to carry a `versionId`, and nothing in a Zola site ever generates one: the setting sat in my distribution for more than two years without any effect. The mechanism that actually works is Zola's `?h=` hash, above.

Versioning is still worth keeping, for another reason: it lets you roll back a bad deploy. A lifecycle rule keeps its cost negligible. Mine deletes non-current versions after 5 days, and removes the delete markers they leave behind — which `--delete` now produces at every cleanup.

## 4. Five settings that cost nothing

These settings were off, or incomplete, on my 2024 distribution:

- **HTTP/3**: in the distribution settings, add HTTP/3 to the supported HTTP versions. Browsers discover it through the `alt-svc` response header and switch to it on the following requests.
- **Brotli**: comes with the cache policy above.
- **Security headers**: a *response headers policy* adds them to every response[^10]. Mine sets HSTS for one year — without `includeSubDomains` or `preload`, which are harder to take back — plus `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, a `Referrer-Policy` and a `Permissions-Policy`. It also removes the `Server: AmazonS3` header sent by the origin.
- **IPv6**: my distribution had IPv6 enabled, but nothing pointed to it — the domain had an `A` alias record and no `AAAA`. Create both.
- **CAA**: a DNS record listing the certificate authorities allowed to issue certificates for your domain. With ACM, `0 issue "amazon.com"` is enough[^11]. Keep an Amazon value in it, or ACM can no longer renew your certificate.

Before and after this revision, measured from Paris:

| Aspect | Before | After |
|---|---|---|
| HTML time to first byte | 311–360 ms (`RefreshHit`) | 32–54 ms (`Hit`) |
| Compression | gzip | Brotli |
| Protocol | HTTP/2 | HTTP/3 |
| Security headers | none | 5, and no `Server: AmazonS3` |
| Cache-busting hash | ignored | part of the cache key |
| Deploy credentials | access key from 2024 | short-lived, through OIDC |
| Bucket access | OAI (legacy) | OAC |

## Overkill? Certainly, but worth the journey

Let's be honest — deploying a simple blog using CloudFront is probably like using a sledgehammer to crack a nut. The dozen or so readers of my blog (hi sweety!) would have been perfectly happy with a simple static hosting solution. But hey, who am I to deny myself the pleasure of diving into AWS services under the pretense of "proper infrastructure"?

For the record, the sledgehammer costs nothing to swing: at this blog's traffic, CloudFront stays inside its free tier and S3 costs well under a dollar a year. The real bill is the domain name and the Route 53 hosted zone.

In all seriousness, while this setup might be oversized for my current needs, exploring CloudFront's capabilities beyond basic configuration has been an enlightening journey — and, two years on, a humbling one: a setup can work for years and still be quietly wrong.

If you've found yourself on a similar over-engineered adventure, or if you have any questions or suggestions, feel free to share your experiences in the comments below.

---
[^1]: Zola documentation, [Multilingual sites](https://www.getzola.org/documentation/content/multilingual/): "Zola outputs the translated content with a base URL of `{base_url}/{code}/`."

[^2]: Amazon S3 API Reference, [GetObject](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObject.html): "If you have the `s3:ListBucket` permission on the bucket, Amazon S3 returns an HTTP status code `404 Not Found` error. If you don't have the `s3:ListBucket` permission, Amazon S3 returns an HTTP status code `403 Access Denied` error."

[^3]: Amazon CloudFront Developer Guide, [Restrict access to an Amazon S3 origin](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html): "We recommend that you use OAC instead."

[^4]: AWS re:Post, [Push updated Amazon S3 content from CloudFront](https://repost.aws/knowledge-center/cloudfront-serving-outdated-content-s3): "By default, CloudFront caches a response from Amazon S3 for 24 hours (Default TTL of 86,400 seconds)."

[^5]: Amazon CloudFront Developer Guide, [how long content stays in the cache](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Expiration.html): "CloudFront caches the object for the lesser of the value of the Cache-Control: s-maxage directive" and the maximum TTL of the cache policy.

[^6]: Zola documentation, [Templates — `get_url`](https://www.getzola.org/documentation/templates/overview/): "a cachebust of the format `?h=<sha256>` at the end of a URL by passing `cachebust=true`".

[^7]: Amazon CloudFront Developer Guide, [Serve compressed files](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/ServingCompressedFiles.html): "You must use cache policies to use Brotli compression. Brotli doesn't support legacy cache settings."

[^8]: GitHub Docs, [Configuring OpenID Connect in Amazon Web Services](https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services): OIDC lets workflows access AWS "without needing to store the AWS credentials as long-lived GitHub secrets".

[^9]: AWS CLI Command Reference, [`s3 sync`](https://docs.aws.amazon.com/cli/latest/reference/s3/sync.html): "Files that exist in the destination but not in the source are deleted during sync. Note that files excluded by filters are excluded from deletion."

[^10]: Amazon CloudFront Developer Guide, [adding HTTP headers to CloudFront responses](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/adding-response-headers.html).

[^11]: AWS Certificate Manager User Guide, [CAA records](https://docs.aws.amazon.com/acm/latest/userguide/setup-caa.html): any one of `amazon.com`, `amazontrust.com`, `awstrust.com` or `amazonaws.com`.
