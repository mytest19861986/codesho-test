#!/usr/bin/env python3
"""Fail closed when a supported backend install path can resolve dependencies."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCKS = (
    (ROOT / "backend" / "requirements.lock", True),
    (ROOT / "backend" / "requirements-dev.lock", True),
    (ROOT / "backend" / "requirements" / "lock-tools.txt", False),
)
CONSUMERS = {
    ROOT / "backend" / "Dockerfile": (
        "pip install --require-hashes --only-binary=:all: --no-deps -r requirements.lock",
        "pip install --no-deps --no-build-isolation .",
    ),
    ROOT / ".github" / "workflows" / "ci.yml": (
        "pip install --require-hashes --only-binary=:all: --no-deps -r requirements-dev.lock",
        "pip install --no-deps --no-build-isolation -e .",
    ),
    ROOT / ".github" / "workflows" / "compose-smoke.yml": (
        "pip install --require-hashes --only-binary=:all: --no-deps -r requirements-dev.lock",
        "pip install --no-deps --no-build-isolation -e .",
    ),
}
PINNED_REQUIREMENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*==[^\s\\]+ \\")


def validate_lock(lock: Path, *, require_binary_directive: bool) -> list[str]:
    errors: list[str] = []
    lines = lock.read_text(encoding="utf-8").splitlines()
    if require_binary_directive and "--only-binary :all:" not in lines:
        errors.append(f"{lock.relative_to(ROOT)} must require binary-only installs")
    for index, line in enumerate(lines):
        if not PINNED_REQUIREMENT.match(line):
            continue
        group = "\n".join(lines[index + 1 :])
        next_requirement = PINNED_REQUIREMENT.search(group)
        segment = group[: next_requirement.start()] if next_requirement else group
        if "--hash=sha256:" not in segment:
            errors.append(f"{lock.relative_to(ROOT)}:{index + 1} is missing a hash")
    return errors


def validate_consumers() -> list[str]:
    errors: list[str] = []
    for consumer, required in CONSUMERS.items():
        text = consumer.read_text(encoding="utf-8")
        for command in required:
            if command not in text:
                errors.append(f"{consumer.relative_to(ROOT)} is missing: {command}")
        if "pip install -e '.[dev]'" in text or "pip install ." in text:
            errors.append(f"{consumer.relative_to(ROOT)} still permits unconstrained project resolution")
    return errors


def main() -> int:
    errors: list[str] = []
    for lock, require_binary_directive in LOCKS:
        if not lock.is_file():
            errors.append(f"missing lock: {lock.relative_to(ROOT)}")
        else:
            errors.extend(validate_lock(lock, require_binary_directive=require_binary_directive))
    errors.extend(validate_consumers())
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Python dependency lock governance: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
