#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")/.."

uv run robot \
  --include smoke \
  --outputdir reports/smoke \
  tests