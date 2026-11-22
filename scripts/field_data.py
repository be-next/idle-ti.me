#!/usr/bin/env python3
"""Turn CloudFront's access logs into the field data of the /performance/ page.

CloudFront delivers its access logs (standard logging v2, JSON) to the
idle-ti-me-logs bucket, which keeps them 35 days. They hold no IP address,
user agent, referrer, cookie or query string: those fields are left out of the
delivery. publish.yml syncs the bucket to logs/ and runs this script, which
writes content/pages/performance/field.json with two parts:

- edge: how CloudFront served the pages (HTML), per point of presence (PoP):
  requests, cache hit ratio, time to first byte measured at the edge;
- field: the Web Vitals that readers' browsers sent through static/js/rum.js
  (/rum/ beacons, answered by a CloudFront Function): 75th percentile and
  good / needs improvement / poor shares, as Google's CrUX reports them.

Window: the last 28 days, as in CrUX. Like performance_data.py, the output is
not committed; the page shows a notice where data is missing or too thin.

Stdlib only.
Usage: python3 scripts/field_data.py [logs_dir] [output]
       (defaults: logs  content/pages/performance/field.json)
"""

import gzip
import json
import math
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
WINDOW_DAYS = 28
# Fewer samples than this and a percentile says more about chance than about
# the site: the page shows "not enough data" instead.
MIN_SAMPLES = 20

# Web Vitals thresholds: [good up to, poor above], from web-vitals.
THRESHOLDS = {
    "lcp": (2500, 4000),
    "inp": (200, 500),
    "cls": (0.1, 0.25),
    "fcp": (1800, 3000),
    "ttfb": (800, 1800),
}
# Sanity bounds: beacons are unauthenticated, anything outside is dropped.
BOUNDS = {"lcp": 60000, "inp": 60000, "cls": 10, "fcp": 60000, "ttfb": 60000}
NAVIGATION_TYPES = {"navigate", "reload", "back-forward", "back-forward-cache", "prerender", "restore"}

# CloudFront names its PoPs after the nearest airport (IATA code).
CITIES = {
    "AKL": "Auckland", "AMS": "Amsterdam", "ARN": "Stockholm", "ATH": "Athens",
    "ATL": "Atlanta", "BAH": "Bahrain", "BCN": "Barcelona", "BER": "Berlin",
    "BKK": "Bangkok", "BLR": "Bengaluru", "BNE": "Brisbane", "BOG": "Bogotá",
    "BOM": "Mumbai", "BOS": "Boston", "BRU": "Brussels", "BUD": "Budapest",
    "CAI": "Cairo", "CCU": "Kolkata", "CDG": "Paris", "CGK": "Jakarta",
    "CMH": "Columbus", "CPH": "Copenhagen", "CPT": "Cape Town", "DEL": "New Delhi",
    "DEN": "Denver", "DFW": "Dallas", "DOH": "Doha", "DUB": "Dublin",
    "DUS": "Düsseldorf", "DXB": "Dubai", "EWR": "Newark", "EZE": "Buenos Aires",
    "FCO": "Rome", "FJR": "Fujairah", "FRA": "Frankfurt", "GIG": "Rio de Janeiro",
    "GRU": "São Paulo", "HAM": "Hamburg", "HAN": "Hanoi", "HEL": "Helsinki",
    "HIO": "Hillsboro", "HKG": "Hong Kong", "HYD": "Hyderabad", "IAD": "Ashburn",
    "IAH": "Houston", "ICN": "Seoul", "IST": "Istanbul", "JAX": "Jacksonville",
    "JED": "Jeddah", "JFK": "New York", "JNB": "Johannesburg", "KIX": "Osaka",
    "KUL": "Kuala Lumpur", "LAX": "Los Angeles", "LHR": "London", "LIM": "Lima",
    "LIS": "Lisbon", "LOS": "Lagos", "MAA": "Chennai", "MAD": "Madrid",
    "MAN": "Manchester", "MCI": "Kansas City", "MCT": "Muscat", "MEL": "Melbourne",
    "MEX": "Mexico City", "MIA": "Miami", "MNL": "Manila", "MRS": "Marseille",
    "MSP": "Minneapolis", "MUC": "Munich", "MXP": "Milan", "NBO": "Nairobi",
    "NRT": "Tokyo", "ORD": "Chicago", "OSL": "Oslo", "OTP": "Bucharest",
    "PDX": "Portland", "PER": "Perth", "PHL": "Philadelphia", "PHX": "Phoenix",
    "PMO": "Palermo", "PNQ": "Pune", "PRG": "Prague", "QRO": "Querétaro",
    "SCL": "Santiago", "SEA": "Seattle", "SFO": "San Francisco", "SGN": "Ho Chi Minh City",
    "SIN": "Singapore", "SLC": "Salt Lake City", "SOF": "Sofia", "SYD": "Sydney",
    "TLV": "Tel Aviv", "TPE": "Taipei", "TXL": "Berlin", "VIE": "Vienna",
    "WAW": "Warsaw", "YTO": "Toronto", "YUL": "Montréal", "YVR": "Vancouver",
    "ZAG": "Zagreb", "ZRH": "Zurich",
}


def records(logs_dir):
    """Every log record under logs_dir: gzipped or not, JSON lines or array."""
    for path in sorted(Path(logs_dir).rglob("*")):
        if not path.is_file():
            continue
        raw = path.read_bytes()
        if raw[:2] == b"\x1f\x8b":
            raw = gzip.decompress(raw)
        text = raw.decode("utf-8", "replace").strip()
        if not text:
            continue
        if text.startswith("["):
            yield from json.loads(text)
            continue
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("{"):
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue


def number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def percentile(values, p):
    """Nearest-rank percentile: a value that was actually observed."""
    ordered = sorted(values)
    return ordered[max(0, math.ceil(p / 100 * len(ordered)) - 1)]


def decode(value):
    """Undo URL encoding, however many times the path went through it."""
    for _ in range(3):
        decoded = unquote(value)
        if decoded == value:
            break
        value = decoded
    return value


def beacon(stem):
    """The fields of a /rum/1/ beacon, or None if it doesn't parse."""
    body = stem[len("/rum/1/"):]
    if ";" not in body:
        body = decode(body)  # separators logged encoded
    fields = {}
    for part in body.split(";"):
        key, sep, value = part.partition("=")
        if sep:
            fields[key] = decode(value)
    if not fields.get("p", "").startswith("/") or fields.get("n") not in NAVIGATION_TYPES:
        return None
    metrics = {}
    for name, bound in BOUNDS.items():
        value = number(fields.get(name))
        if value is not None and 0 <= value <= bound:
            metrics[name] = value
    return {"page": fields["p"], "device": fields.get("d"), "metrics": metrics} if metrics else None


def edge_summary(pages):
    def stats(group):
        ttfb = [r["ttfb_ms"] for r in group]
        return {
            "requests": len(group),
            "hit_ratio": round(sum(r["hit"] for r in group) / len(group), 3),
            "ttfb_p50_ms": round(percentile(ttfb, 50), 1),
            "ttfb_p95_ms": round(percentile(ttfb, 95), 1),
        }

    if len(pages) < MIN_SAMPLES:
        return {"page_requests": len(pages)}
    by_pop = {}
    for r in pages:
        by_pop.setdefault(r["pop"], []).append(r)
    pops, other = [], []
    for code, group in sorted(by_pop.items(), key=lambda item: -len(item[1])):
        if len(group) >= MIN_SAMPLES:
            pops.append({"code": code, "city": CITIES.get(code, code), **stats(group)})
        else:
            other.extend(group)
    misses = [r["origin_ms"] for r in pages if not r["hit"] and r["origin_ms"] is not None]
    overall = stats(pages)
    summary = {"page_requests": overall.pop("requests"), **overall, "pops": pops,
               "other_pops": {"count": len(by_pop) - len(pops), "requests": len(other)}}
    if len(misses) >= MIN_SAMPLES:
        summary["origin_p50_ms"] = round(percentile(misses, 50), 1)
    return summary


def field_summary(beacons):
    metrics = {}
    for name, (good, poor) in THRESHOLDS.items():
        values = [b["metrics"][name] for b in beacons if name in b["metrics"]]
        entry = {"n": len(values), "thresholds": [good, poor]}
        if len(values) >= MIN_SAMPLES:
            entry.update({
                "p75": round(percentile(values, 75), 3 if name == "cls" else 0),
                "good": round(sum(v <= good for v in values) / len(values), 3),
                "needs_improvement": round(sum(good < v <= poor for v in values) / len(values), 3),
                "poor": round(sum(v > poor for v in values) / len(values), 3),
            })
        metrics[name] = entry
    # Each page view sends TTFB once, in its first beacon.
    views = [b for b in beacons if "ttfb" in b["metrics"]]
    mobile = sum(b["device"] == "m" for b in views)
    return {
        "page_views": len(views),
        "mobile_share": round(mobile / len(views), 3) if views else None,
        "metrics": metrics,
    }


def main():
    logs_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "logs"
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "content/pages/performance/field.json"

    now = time.time()
    start = now - WINDOW_DAYS * 86400
    pages, beacons, requests, http3 = [], [], 0, 0
    first = now  # oldest record in the window: logging may be younger than it
    for record in records(logs_dir) if logs_dir.is_dir() else []:
        timestamp = number(record.get("timestamp"))
        if timestamp is None or not start <= timestamp <= now:
            continue
        first = min(first, timestamp)
        stem = record.get("cs-uri-stem") or ""
        status = record.get("sc-status")
        if stem.startswith("/rum/"):
            if str(status) == "204" and stem.startswith("/rum/1/"):
                parsed = beacon(stem)
                if parsed:
                    beacons.append(parsed)
            continue
        requests += 1
        http3 += record.get("cs-protocol-version") == "HTTP/3.0"
        ttfb = number(record.get("time-to-first-byte"))
        if (record.get("cs-method") == "GET" and str(status) in ("200", "304")
                and (record.get("sc-content-type") or "").startswith("text/html")
                and ttfb is not None):
            origin = number(record.get("origin-fbl"))
            pages.append({
                "pop": (record.get("x-edge-location") or "?")[:3],
                "hit": record.get("x-edge-result-type") == "Hit",
                "ttfb_ms": ttfb * 1000,
                "origin_ms": origin * 1000 if origin is not None else None,
            })

    def day(seconds):
        return datetime.fromtimestamp(seconds, timezone.utc).strftime("%Y-%m-%d")

    data = {
        "window_days": WINDOW_DAYS,
        "from": day(first),
        "to": day(now),
        "min_samples": MIN_SAMPLES,
        "edge": {**edge_summary(pages),
                 "http3_share": round(http3 / requests, 3) if requests else None},
        "field": field_summary(beacons),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    # Counts only: workflow logs are public, log file names carry the account ID.
    print(f"field.json: {len(pages)} page requests, {len(beacons)} beacons, {WINDOW_DAYS} days")


if __name__ == "__main__":
    main()
