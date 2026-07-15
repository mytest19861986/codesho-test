#!/usr/bin/env python
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "backend" / "modules"
ALLOWED_DEPENDENCIES = {
    "identity": set(),
    "platform_event": set(),
    "platform_tenant": {"identity"},
}


def imported_module(node: ast.Import | ast.ImportFrom) -> str | None:
    names = [alias.name for alias in node.names] if isinstance(node, ast.Import) else [node.module or ""]
    for name in names:
        parts = name.split(".")
        if len(parts) >= 2 and parts[0] == "modules":
            return parts[1]
    return None


def main() -> int:
    violations: list[str] = []
    for path in ROOT.glob("*/*.py"):
        owner = path.parent.name
        allowed = ALLOWED_DEPENDENCIES.get(owner, set())
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                dependency = imported_module(node)
                if dependency and dependency != owner and dependency not in allowed:
                    violations.append(f"{path.relative_to(ROOT)} -> {dependency}")
    if violations:
        print("Disallowed module dependencies:")
        print("\n".join(sorted(violations)))
        return 1
    print("Module boundaries are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
