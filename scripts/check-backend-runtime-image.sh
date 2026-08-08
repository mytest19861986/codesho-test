#!/usr/bin/env sh
set -eu

image=${1:?usage: check-backend-runtime-image.sh IMAGE}

docker run --rm --entrypoint sh "$image" -c '
set -eu
fail_if_present() {
    label=$1
    shift
    if "$@" >/dev/null 2>&1; then
        printf "FAIL: %s is present or usable\\n" "$label" >&2
        exit 1
    fi
}

test "$(id -u)" -ne 0
test "$(id -un)" = codesho
test -f /app/manage.py
command -v gunicorn >/dev/null
fail_if_present pip command -v pip
fail_if_present pip3 command -v pip3
fail_if_present "python -m pip" python -m pip --version
fail_if_present "python3 -m pip" python3 -m pip --version
fail_if_present "pip import" python -c "import pip"
fail_if_present "setuptools import" python -c "import setuptools"
fail_if_present "wheel import" python -c "import wheel"
fail_if_present "piptools import" python -c "import piptools"
fail_if_present "pip_audit import" python -c "import pip_audit"
fail_if_present "build import" python -c "import build"
fail_if_present "ensurepip import" python -c "import ensurepip"
fail_if_present curl command -v curl
fail_if_present wget command -v wget
fail_if_present git command -v git
fail_if_present ruff command -v ruff
fail_if_present mypy command -v mypy
fail_if_present "pytest import" python -c "import pytest"
fail_if_present "coverage import" python -c "import coverage"
python -c "import django, gunicorn"
'
