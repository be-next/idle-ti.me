#!/usr/bin/env bash
set -euo pipefail

# Sync awesome-performance-engineering markdown files from GitHub
# and transform them into Zola-compatible pages.

REPO="be-next/awesome-performance-engineering"
BRANCH="main"
BASE_URL="https://raw.githubusercontent.com/${REPO}/${BRANCH}"
GITHUB_REPO_URL="https://github.com/${REPO}"

CONTENT_DIR="content/awesome-performance-engineering"

download() {
  curl -sSfL "${BASE_URL}/$1"
}

mkdir -p "${CONTENT_DIR}/observability-tools"
mkdir -p "${CONTENT_DIR}/performance-testing-tools"

# --- README.md -> _index.md (section index) ---
echo "Transforming README.md..."
content=$(download "README.md")

# Remove H1 with awesome badge
content=$(echo "$content" | sed '/^# .*\[!\[Awesome\]/d')
# Remove CI badges
content=$(echo "$content" | sed '/^\[!\[Lint Markdown\]/d')
content=$(echo "$content" | sed '/^\[!\[Check Links\]/d')
# Remove leading blank lines
content=$(echo "$content" | sed '/./,$!d')

# Transform internal links
content=$(echo "$content" | sed 's|(awesome-observability-tools\.md)|(@/awesome-performance-engineering/observability-tools/index.md)|g')
content=$(echo "$content" | sed 's|(awesome-performance-testing-tools\.md)|(@/awesome-performance-engineering/performance-testing-tools/index.md)|g')
content=$(echo "$content" | sed "s|(CONTRIBUTING\.md)|(${GITHUB_REPO_URL}/blob/main/CONTRIBUTING.md)|g")

cat > "${CONTENT_DIR}/_index.md" << 'FRONTMATTER'
+++
title = "Awesome Performance Engineering"
sort_by = "weight"
template = "section.html"
insert_anchor_links = "left"
description = "A curated, opinionated collection of tools and resources dedicated to Performance Engineering — covering Observability and Performance Testing."

[extra]
show_reading_time = false
copy_button = true
+++

FRONTMATTER
echo "$content" >> "${CONTENT_DIR}/_index.md"

# --- awesome-observability-tools.md -> observability-tools/index.md ---
echo "Transforming awesome-observability-tools.md..."
content=$(download "awesome-observability-tools.md")

# Remove H1 with awesome badge
content=$(echo "$content" | sed '/^# .*\[!\[Awesome\]/d')
# Remove leading blank lines
content=$(echo "$content" | sed '/./,$!d')
# Transform CONTRIBUTING.md link
content=$(echo "$content" | sed "s|(CONTRIBUTING\.md)|(${GITHUB_REPO_URL}/blob/main/CONTRIBUTING.md)|g")

cat > "${CONTENT_DIR}/observability-tools/index.md" << 'FRONTMATTER'
+++
title = "Awesome Observability Tools"
description = "A curated, opinionated list of tools and resources dedicated to Observability as an engineering capability — from kernel-level tracing to full-stack platforms."
weight = 10
date = 2026-02-10
updated = 2026-02-10
toc = true

[taxonomies]
tags = ["observability", "performance-engineering", "awesome-list"]

[extra]
copy_button = true
giscus = false
show_reading_time = false
+++

FRONTMATTER
echo "$content" >> "${CONTENT_DIR}/observability-tools/index.md"

# --- awesome-performance-testing-tools.md -> performance-testing-tools/index.md ---
echo "Transforming awesome-performance-testing-tools.md..."
content=$(download "awesome-performance-testing-tools.md")

# Remove H1 with awesome badge
content=$(echo "$content" | sed '/^# .*\[!\[Awesome\]/d')
# Remove leading blank lines
content=$(echo "$content" | sed '/./,$!d')
# Transform README.md -> Zola section link (anchors not supported on _index.md)
content=$(echo "$content" | sed 's|(README\.md\(#[^)]*\))|(@/awesome-performance-engineering/_index.md)|g')
content=$(echo "$content" | sed 's|(README\.md)|(@/awesome-performance-engineering/_index.md)|g')
# Transform CONTRIBUTING.md link
content=$(echo "$content" | sed "s|(CONTRIBUTING\.md)|(${GITHUB_REPO_URL}/blob/main/CONTRIBUTING.md)|g")

# Fix GitHub-style anchors to match Zola slugification
# & in headings: GitHub produces --, Zola collapses to single -
content=$(echo "$content" | sed 's|#chaos-engineering--fault-injection|#chaos-engineering-fault-injection|g')
content=$(echo "$content" | sed 's|#network-simulation--traffic-shaping|#network-simulation-traffic-shaping|g')
content=$(echo "$content" | sed 's|#commercial--saas-platforms|#commercial-saas-platforms|g')
# Emoji in headings: GitHub keeps a leading -, Zola strips it
content=$(echo "$content" | sed 's|_index.md#-performance|_index.md#performance|g')

cat > "${CONTENT_DIR}/performance-testing-tools/index.md" << 'FRONTMATTER'
+++
title = "Awesome Performance Testing Tools"
description = "A curated, opinionated list of tools and resources dedicated to Performance Testing as a continuous engineering practice — from workload design to results analysis."
weight = 20
date = 2026-02-10
updated = 2026-02-10
toc = true

[taxonomies]
tags = ["performance-testing", "performance-engineering", "awesome-list"]

[extra]
copy_button = true
giscus = false
show_reading_time = false
+++

FRONTMATTER
echo "$content" >> "${CONTENT_DIR}/performance-testing-tools/index.md"

echo "Sync complete. Files written to ${CONTENT_DIR}/"
