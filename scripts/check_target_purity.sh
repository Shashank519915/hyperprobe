#!/usr/bin/env bash
# Target purity check — ensures calculator code stays free of observability hooks.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${ROOT}/target"

echo "check_target_purity: scanning ${TARGET}"

if [[ ! -d "${TARGET}" ]]; then
  echo "check_target_purity: target/ not present yet — stub pass (PR-01)"
  exit 0
fi

if grep -R --include='*.py' -E '(^|[[:space:]])import[[:space:]]+agent|from[[:space:]]+agent' "${TARGET}" 2>/dev/null; then
  echo "FAIL: target/ must not import agent"
  exit 1
fi

if grep -R --include='*.py' -E '^[[:space:]]*(import logging|from logging|print\()' "${TARGET}" 2>/dev/null; then
  echo "FAIL: target/ must not use logging or print"
  exit 1
fi

if grep -R --include='*.py' -E '(sys\.settrace|threading\.settrace|import trace|from trace|opentelemetry|OpenTelemetry)' "${TARGET}" 2>/dev/null; then
  echo "FAIL: target/ must not use tracing or instrumentation hooks"
  exit 1
fi

echo "check_target_purity: OK"
exit 0
