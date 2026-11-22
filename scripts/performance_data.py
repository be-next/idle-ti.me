#!/usr/bin/env python3
"""Turn Lighthouse CI results into the data behind the /performance/ page.

`lhci collect` leaves one report per run in .lighthouseci/lhr-*.json. This
script takes, for each page, the median of every figure across its runs, adds
the budget from lighthouserc.json and the measurement conditions, and writes
content/pages/performance/data.json. The page's `performance_report` component
renders it, and Zola publishes the file next to the page (/performance/data.json).

publish.yml runs it on the build it is about to deploy, so the page always
describes the site as deployed. The file is not committed: a build without it
renders the page with a "no measurement" notice instead of the figures.

Stdlib only.
Usage: python3 scripts/performance_data.py [reports_dir] [output]
       (defaults: .lighthouseci  content/pages/performance/data.json)
"""

import html
import json
import os
import re
import statistics
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
REPO_URL = "https://github.com/be-next/idle-ti.me"

# Transfer size breakdown kept on the page, in Lighthouse's resource types.
RESOURCE_TYPES = ["document", "stylesheet", "script", "font", "image", "other"]
METRICS = {
    "fcp_ms": "first-contentful-paint",
    "lcp_ms": "largest-contentful-paint",
    "tbt_ms": "total-blocking-time",
    "si_ms": "speed-index",
}


def median(values, digits=0):
    value = statistics.median(values)
    # `or 0`: a CLS of 0.0 is printed "0", not "0.0".
    return (round(value, digits) or 0) if digits else int(round(value))


def page_title(path):
    """The page's <title>, from the build Lighthouse measured (public/)."""
    index = ROOT / "public" / path.lstrip("/") / "index.html"
    if path == "/":
        return "Home"
    try:
        match = re.search(r"<title>([^<]*)</title>", index.read_text(encoding="utf-8"))
    except OSError:
        match = None
    if not match:
        return path
    # tabi titles read "idle-ti.me • <page title>".
    return html.unescape(match.group(1)).split(" • ", 1)[-1].strip()


def budget(config):
    assertions = config["ci"]["assert"]["assertions"]

    def limit(name, key):
        rule = assertions.get(name)
        return rule[1][key] if rule else None

    scores = {
        category.replace("-", "_"): round(limit(f"categories:{category}", "minScore") * 100)
        for category in ["performance", "accessibility", "best-practices", "seo"]
        if limit(f"categories:{category}", "minScore") is not None
    }
    return {
        "scores": scores,
        "lcp_ms": limit("largest-contentful-paint", "maxNumericValue"),
        "cls": limit("cumulative-layout-shift", "maxNumericValue"),
        "tbt_ms": limit("total-blocking-time", "maxNumericValue"),
        "font_bytes": limit("resource-summary:font:size", "maxNumericValue"),
    }


def commit():
    sha = os.environ.get("GITHUB_SHA")
    if not sha:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True
        )
        sha = result.stdout.strip()
    return sha[:7] if sha else None


def main():
    reports_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / ".lighthouseci"
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "content/pages/performance/data.json"

    config = json.loads((ROOT / "lighthouserc.json").read_text())
    runs = {}
    for report in sorted(reports_dir.glob("lhr-*.json")):
        lhr = json.loads(report.read_text())
        runs.setdefault(lhr["requestedUrl"], []).append(lhr)
    if not runs:
        sys.exit(f"No Lighthouse reports (lhr-*.json) in {reports_dir}")

    # Keep the page order of lighthouserc.json.
    order = config["ci"]["collect"]["url"]
    urls = sorted(runs, key=lambda url: order.index(url) if url in order else len(order))
    limits = budget(config)

    pages = []
    for url in urls:
        lhrs = runs[url]
        path = urlparse(url).path or "/"
        page = {
            "path": path,
            "title": page_title(path),
            "scores": {
                key.replace("-", "_"): median([lhr["categories"][key]["score"] * 100 for lhr in lhrs])
                for key in ["performance", "accessibility", "best-practices", "seo"]
            },
        }
        for field, audit in METRICS.items():
            page[field] = median([lhr["audits"][audit]["numericValue"] for lhr in lhrs])
        page["cls"] = median([lhr["audits"]["cumulative-layout-shift"]["numericValue"] for lhr in lhrs], 3)

        sizes = {}
        for lhr in lhrs:
            for item in lhr["audits"]["resource-summary"]["details"]["items"]:
                sizes.setdefault(item["resourceType"], []).append(
                    (item["transferSize"], item["requestCount"])
                )
        page["bytes"] = {kind: median([size for size, _ in sizes.get(kind, [(0, 0)])])
                         for kind in RESOURCE_TYPES + ["total"]}
        page["requests"] = median([count for _, count in sizes["total"]])

        over = []
        for category, minimum in limits["scores"].items():
            if page["scores"][category] < minimum:
                over.append(category)
        for field in ["lcp_ms", "cls", "tbt_ms"]:
            if limits[field] is not None and page[field] > limits[field]:
                over.append(field)
        if limits["font_bytes"] is not None and page["bytes"]["font"] > limits["font_bytes"]:
            over.append("font_bytes")
        page["over_budget"] = over
        pages.append(page)

    first = runs[urls[0]][0]
    settings = first["configSettings"]
    throttling = settings["throttling"]
    fetched = min(lhr["fetchTime"] for lhrs in runs.values() for lhr in lhrs)
    sha = commit()
    in_ci = os.environ.get("GITHUB_ACTIONS") == "true"

    data = {
        "measured_at": fetched,
        "measured_on": fetched[:10],
        "commit": sha,
        "commit_url": f"{REPO_URL}/commit/{sha}" if sha and in_ci else None,
        "runner": "GitHub Actions" if in_ci else "local",
        "lighthouse_version": first["lighthouseVersion"],
        "runs_per_page": min(len(lhrs) for lhrs in runs.values()),
        "conditions": {
            "form_factor": settings["formFactor"],
            "throttling_method": settings["throttlingMethod"],
            "rtt_ms": throttling["rttMs"],
            "throughput_mbps": round(throttling["throughputKbps"] / 1000, 1),
            "cpu_slowdown": throttling["cpuSlowdownMultiplier"],
            "viewport": f'{settings["screenEmulation"]["width"]}×{settings["screenEmulation"]["height"]}',
        },
        "excluded": [
            pattern.strip("*")
            for pattern in config["ci"]["collect"]["settings"].get("blockedUrlPatterns", [])
        ],
        "budget": limits,
        "pages": pages,
        # Each figure at its worst page: what the budget is held against.
        "worst": {
            "performance": min(page["scores"]["performance"] for page in pages),
            "accessibility": min(page["scores"]["accessibility"] for page in pages),
            "lcp_ms": max(page["lcp_ms"] for page in pages),
            "cls": max(page["cls"] for page in pages),
            "tbt_ms": max(page["tbt_ms"] for page in pages),
            "total_bytes": max(page["bytes"]["total"] for page in pages),
        },
        "over_budget": any(page["over_budget"] for page in pages),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{output.relative_to(ROOT) if output.is_relative_to(ROOT) else output}: "
          f"{len(pages)} pages, {sum(len(lhrs) for lhrs in runs.values())} runs")


if __name__ == "__main__":
    main()
