from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_supported_python_install_paths_are_hash_locked() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check-python-locks.py")],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "PASS" in result.stdout
