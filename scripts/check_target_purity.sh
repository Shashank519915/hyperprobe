#!/usr/bin/env bash
# Target purity check — ensures calculator code stays free of observability hooks.
# Stub in PR-01: passes when target/ is absent. Stricter rules added in PR-03 (task 2.6).

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${ROOT}/target"

echo "check_target_purity: scanning ${TARGET}"

if [[ ! -d "${TARGET}" ]]; then
  echo "check_target_purity: target/ not present yet — stub pass (PR-01)"
  exit 0
fi

# --- enforced once target/ exists (expanded in task 2.6) ---

if grep -R --include='*.py' -E '(^|[[:space:]])import[[:space:]]+agent|from[[:space:]]+agent' "${TARGET}" 2>/dev/null; then
  echo "FAIL: target/ must not import agent"
  exit 1
fi

if grep -R --include='*.py' -E '^[[:space:]]*(import logging|from logging|import agent|print\()' "${TARGET}" 2>/dev/null; then
  echo "FAIL: target/ must not use logging, agent imports, or print"
  exit 1
fi

echo "check_target_purity: OK"
exit 0
