#!/usr/bin/env python3
"""Draw the social media cards (og:image) for idle-ti.me.

config.toml sets `social_media_card = "social_card.png"`. tabi looks for that
file next to the page first, then in the parent folder, then in static/. So:

- every page bundle (content/**/index.md) gets content/<path>/social_card.png,
  drawn from its title, description, date and tags. Pages that set their own
  URL with `path =` (about, library, copyright) get theirs in static/ instead,
  at the same content path: tabi builds the og:image URL from the content path
  (/pages/about/…), while Zola publishes the page's files under its `path`
  (/about/…), so a colocated card would be announced at a 404;
- static/social_card.png is the site-wide card, used by sections (home, blog,
  tags...) and by any page without its own.

Cards are 1200x630 PNG, the size LinkedIn, Mastodon, Bluesky and X expect, in
the colours of the site's dark theme, set in the fonts the site itself uses.

Run it after adding a post or changing a title or description. Drafts and
pages git doesn't track yet are skipped. Existing cards are redrawn.

Requires: pip install fonttools brotli pillow
Usage:    python3 scripts/social_cards.py
"""

import io
import subprocess
import tomllib
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "themes/tabi/static/fonts"
CARD_NAME = "social_card.png"

W, H = 1200, 630
MARGIN = 80
BACKGROUND = "#1f1f1f"  # tabi dark theme
ORANGE = "#ec984f"  # accessible_orange, dark theme
TITLE = "#eceeef"
TEXT = "#b0b0b0"


def load_font(name, size, axes):
    """Load a woff2 variable font at the given axis values (Pillow needs TTF)."""
    font = TTFont(FONTS / name)
    font.flavor = None
    buf = io.BytesIO()
    font.save(buf)
    buf.seek(0)
    pil = ImageFont.truetype(buf, size)
    order = [a.axisTag for a in font["fvar"].axes]
    pil.set_variation_by_axes([axes[tag] for tag in order])
    return pil


def serif(size, weight=600):
    return load_font("SourceSerif4Variable-Roman.ttf.woff2", size, {"wght": weight, "opsz": 60})


def sans(size, weight=400):
    return load_font("Inter4.woff2", size, {"wght": weight, "opsz": 32})


def wrap(draw, text, font, width, max_lines):
    """Greedy word wrap; the last line ends with an ellipsis if text is cut."""
    words, lines, line = text.split(), [], ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if draw.textlength(candidate, font=font) <= width:
            line = candidate
        else:
            lines.append(line)
            line = word
    lines.append(line)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while draw.textlength(last + "…", font=font) > width:
            last = last.rsplit(" ", 1)[0]
        lines[-1] = last.rstrip(",;:—–-") + "…"
    return lines


def draw_card(title, description, footer, out):
    img = Image.new("RGB", (W, H), BACKGROUND)
    draw = ImageDraw.Draw(img)
    width = W - 2 * MARGIN

    draw.text((MARGIN, 64), "idle-ti.me", font=sans(36, 600), fill=ORANGE)

    # Largest title size that fits in three lines.
    for size in (76, 68, 60, 54):
        title_font = serif(size)
        lines = wrap(draw, title, title_font, width, 3)
        if not lines[-1].endswith("…"):
            break
    y = 150
    for line in lines:
        draw.text((MARGIN, y), line, font=title_font, fill=TITLE)
        y += int(size * 1.18)

    # Description: as many lines as fit above the footer.
    if description:
        desc_font = sans(30)
        y += 30
        room = (H - 130 - y) // 42
        for line in wrap(draw, description, desc_font, width, max(room, 0)) if room > 0 else []:
            draw.text((MARGIN, y), line, font=desc_font, fill=TEXT)
            y += 42

    if footer:
        draw.text((MARGIN, H - 92), footer, font=sans(26), fill=TEXT)
    draw.rectangle([0, H - 12, W, H], fill=ORANGE)

    img.save(out, optimize=True)


def front_matter(path):
    text = path.read_text(encoding="utf-8")
    return tomllib.loads(text.split("+++")[1])


def tracked(path):
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(path)],
        cwd=ROOT, capture_output=True,
    )
    return result.returncode == 0


def main():
    # Site card: the description's first clause is the headline
    # ("Performance engineering & observability — articles, ...").
    config = tomllib.loads((ROOT / "config.toml").read_text())
    headline, _, rest = config.get("description", "").partition(" — ")
    draw_card(
        headline or config["title"],
        rest[:1].upper() + rest[1:],
        "",
        ROOT / "static" / CARD_NAME,
    )
    print(f"static/{CARD_NAME}")

    for page in sorted((ROOT / "content").rglob("index.md")):
        rel = page.relative_to(ROOT)
        fm = front_matter(page)
        if fm.get("draft"):
            continue
        if not tracked(page):
            print(f"skipped (not tracked by git): {rel}")
            continue
        parts = []
        if fm.get("date"):
            parts.append(fm["date"].strftime("%-d %B %Y"))
        tags = fm.get("taxonomies", {}).get("tags", [])
        if tags:
            parts.append(" · ".join(tags[:3]))
        if fm.get("path"):
            out = ROOT / "static" / page.parent.relative_to(ROOT / "content") / CARD_NAME
            out.parent.mkdir(parents=True, exist_ok=True)
        else:
            out = page.parent / CARD_NAME
        draw_card(fm["title"], fm.get("description", ""), "   —   ".join(parts), out)
        print(out.relative_to(ROOT))


if __name__ == "__main__":
    main()
