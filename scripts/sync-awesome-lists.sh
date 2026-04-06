#!/usr/bin/env bash
set -euo pipefail

# Sync awesome-performance-engineering README from GitHub
# and transform it into a Zola-compatible page.
#
# Since the 2026-04 consolidation, the awesome list is a single README.md
# containing all tool entries (Observability + Performance Testing).

REPO="be-next/awesome-performance-engineering"
BRANCH="main"
BASE_URL="https://raw.githubusercontent.com/${REPO}/${BRANCH}"
GITHUB_REPO_URL="https://github.com/${REPO}"

CONTENT_DIR="content/awesome-performance-engineering"
TODAY=$(date -u +%Y-%m-%d)

download() {
  curl -sSfL "${BASE_URL}/$1"
}

mkdir -p "${CONTENT_DIR}"

# Remove legacy sub-pages from the multi-file era (if present)
rm -rf "${CONTENT_DIR}/observability-tools"
rm -rf "${CONTENT_DIR}/performance-testing-tools"

# --- README.md -> _index.md (single page with all content) ---
echo "Transforming README.md..."
content=$(download "README.md")

# Remove H1 with awesome badge
content=$(echo "$content" | sed '/^# .*\[!\[Awesome\]/d')
# Remove leading blank lines
content=$(echo "$content" | sed '/./,$!d')

# Transform CONTRIBUTING.md and code-of-conduct.md links to absolute GitHub URLs
content=$(echo "$content" | sed "s|(CONTRIBUTING\.md)|(${GITHUB_REPO_URL}/blob/main/CONTRIBUTING.md)|g")
content=$(echo "$content" | sed "s|(code-of-conduct\.md)|(${GITHUB_REPO_URL}/blob/main/code-of-conduct.md)|g")

# Transform relative image paths to absolute GitHub raw URLs
content=$(echo "$content" | sed "s|src=\"media/|src=\"${BASE_URL}/media/|g")

# Fix GitHub-style anchors to match Zola slugification
# & in headings: GitHub uses --, Zola collapses to single -
content=$(echo "$content" | sed 's|#metrics-collection--time-series-storage|#metrics-collection-time-series-storage|g')
content=$(echo "$content" | sed 's|#log-management--log-pipelines|#log-management-log-pipelines|g')
content=$(echo "$content" | sed 's|#visualization--dashboards|#visualization-dashboards|g')
content=$(echo "$content" | sed 's|#profiling--continuous-performance-analysis|#profiling-continuous-performance-analysis|g')
content=$(echo "$content" | sed 's|#alerting--incident-response|#alerting-incident-response|g')
content=$(echo "$content" | sed 's|#real-user-monitoring-rum--frontend-observability|#real-user-monitoring-rum-frontend-observability|g')
content=$(echo "$content" | sed 's|#load--stress-testing|#load-stress-testing|g')
content=$(echo "$content" | sed 's|#http-benchmarking--micro-benchmarking|#http-benchmarking-micro-benchmarking|g')
content=$(echo "$content" | sed 's|#api-testing--contract-testing|#api-testing-contract-testing|g')
content=$(echo "$content" | sed 's|#grpc--protocol-specific-testing|#grpc-protocol-specific-testing|g')
content=$(echo "$content" | sed 's|#browser--frontend-performance|#browser-frontend-performance|g')
content=$(echo "$content" | sed 's|#database-performance-testing--benchmarking|#database-performance-testing-benchmarking|g')
content=$(echo "$content" | sed 's|#system--infrastructure-benchmarking|#system-infrastructure-benchmarking|g')
content=$(echo "$content" | sed 's|#chaos-engineering--fault-injection|#chaos-engineering-fault-injection|g')
content=$(echo "$content" | sed 's|#network-simulation--traffic-shaping|#network-simulation-traffic-shaping|g')
content=$(echo "$content" | sed 's|#cicd-integration--performance-gates|#ci-cd-integration-performance-gates|g')
content=$(echo "$content" | sed 's|#results-analysis--reporting|#results-analysis-reporting|g')
content=$(echo "$content" | sed 's|#commercial--saas-platforms|#commercial-saas-platforms|g')
content=$(echo "$content" | sed 's|#tools--integrations|#tools-integrations|g')
content=$(echo "$content" | sed 's|#legacy--historical|#legacy-historical|g')

# Insert badges and GitHub link before content
BADGES="[![Lint Markdown](${GITHUB_REPO_URL}/actions/workflows/lint.yml/badge.svg)](${GITHUB_REPO_URL}/actions/workflows/lint.yml) [![Check Links](${GITHUB_REPO_URL}/actions/workflows/links.yml/badge.svg)](${GITHUB_REPO_URL}/actions/workflows/links.yml)"
GITHUB_LINK="[![GitHub repository](https://img.shields.io/badge/GitHub-Repository-181717?logo=github)](${GITHUB_REPO_URL}) [![GitHub stars](https://img.shields.io/github/stars/${REPO}?style=social)](${GITHUB_REPO_URL}/stargazers)"

cat > "${CONTENT_DIR}/_index.md" << 'FRONTMATTER'
+++
title = "Awesome Performance Engineering"
sort_by = "weight"
template = "section.html"
insert_anchor_links = "left"
description = "The discipline that ensures systems deliver fast, reliable, and cost-efficient experiences at any scale, combining observability and performance testing."

[extra]
show_reading_time = false
copy_button = true
+++

FRONTMATTER

# Inject badges and GitHub link together, just before ## Contents
echo "$content" | awk -v badges="${BADGES}" -v ghlink="${GITHUB_LINK}" \
  '/^## Contents$/ { print badges; print ""; print ghlink; print "" } { print }' \
  >> "${CONTENT_DIR}/_index.md"

echo "Sync complete. Single page written to ${CONTENT_DIR}/_index.md"
