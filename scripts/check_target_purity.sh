#!/usr/bin/env bash
# Target purity check — calculator code must stay free of observability hooks (R3).
# Implementation: scripts/target_purity_check.py (this wrapper keeps CI/bash entrypoint).

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python "${ROOT}/scripts/target_purity_check.py" "$@"
