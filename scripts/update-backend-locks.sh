#!/usr/bin/env bash
set -euo pipefail

readonly EXPECTED_PYTHON="3.12.13"
readonly ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly BACKEND_DIR="${ROOT_DIR}/backend"
readonly PYTHON_BIN="${PYTHON_BIN:-python3}"

if [[ "$(${PYTHON_BIN} -c 'import platform, sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} {platform.system()} {platform.machine()}")')" != "${EXPECTED_PYTHON} Linux x86_64" ]]; then
  echo "Task74B lock generation requires CPython ${EXPECTED_PYTHON} on Linux/x86_64." >&2
  exit 1
fi

cd "${BACKEND_DIR}"
export PIP_DISABLE_PIP_VERSION_CHECK=1
export PIP_ONLY_BINARY=:all:

"${PYTHON_BIN}" -m ensurepip --upgrade
"${PYTHON_BIN}" -m pip install --require-hashes --no-deps -r requirements/lock-tools.txt

compile_lock() {
  "${PYTHON_BIN}" -m piptools compile --allow-unsafe --generate-hashes --strip-extras "$@" pyproject.toml
}

compile_lock --output-file requirements/runtime.txt
compile_lock --extra dev --output-file requirements/dev.txt
compile_lock --extra lock --output-file requirements/lock-tools.txt

if [[ "${1:-}" == "--check" ]]; then
  git -C "${ROOT_DIR}" diff --exit-code -- backend/requirements
fi
