#!/usr/bin/env bash
set -euo pipefail

# Measure the site with Lighthouse CI on the pages listed in lighthouserc.json
# (3 runs each, reports in .lighthouseci/). Used by validate.yml on pull
# requests and by publish.yml on each deploy; runs locally too (needs Node and
# Chrome). Follow with `npx @lhci/cli@0.16.0 assert` to check the budget, or
# `python3 scripts/performance_data.py` to feed the /performance/ page.
#
# Leaves public/ as a measurement build (127.0.0.1 URLs, .gz copies):
# rebuild with `zola build` before deploying or browsing it.

# Built against the local server's address, or the pages' absolute URLs would
# load their assets from production.
zola build --base-url http://127.0.0.1:8080

# CloudFront serves text files compressed; measure them the same way.
# http-server --gzip (lighthouserc.json) serves these .gz copies, it doesn't
# compress by itself.
find public -type f \( -name '*.html' -o -name '*.css' -o -name '*.js' \
  -o -name '*.svg' -o -name '*.json' -o -name '*.xml' -o -name '*.txt' \) \
  -exec gzip -9 --keep {} +

npx --yes @lhci/cli@0.16.0 collect
