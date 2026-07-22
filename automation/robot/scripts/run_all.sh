#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")/.."

uv run robot \
  --outputdir reports/all \
  tests