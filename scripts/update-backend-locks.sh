#!/bin/sh
# Run inside the approved CPython 3.12.13 Linux/amd64 Bookworm tool container.
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
backend_dir="$repo_root/backend"
output_dir="${OUTPUT_DIR:-$backend_dir}"

mkdir -p "$output_dir"
pip-compile --all-build-deps --allow-unsafe --generate-hashes --strip-extras --no-header --no-annotate \
  --pip-args='--only-binary=:all:' \
  --output-file "$output_dir/requirements.lock" "$backend_dir/pyproject.toml"
pip-compile --all-build-deps --allow-unsafe --extra=dev --generate-hashes --strip-extras --no-header --no-annotate \
  --pip-args='--only-binary=:all:' \
  --output-file "$output_dir/requirements-dev.lock" "$backend_dir/pyproject.toml"
