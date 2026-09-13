#!/usr/bin/env python3
"""Validate this repository's deliberately simple skill metadata and local links."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def validate():
    errors = []
    skill = ROOT / "skills/guard-raillm/SKILL.md"
    text = skill.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not match:
        errors.append("Missing frontmatter")
    else:
        fields = dict(re.findall(r"^([a-z-]+): (.+)$", match[1], re.M))
        if fields.get("name") != skill.parent.name:
            errors.append("Skill name must match its directory")
        if not 1 <= len(fields.get("description", "")) <= 1024:
            errors.append("Description missing or too long")
        if fields.get("license") != "MIT":
            errors.append("Unexpected license metadata")
    for path in ROOT.rglob("*.md"):
        if any(part in {".git", "dist", ".venv"} for part in path.relative_to(ROOT).parts):
            continue
        content = path.read_text(encoding="utf-8")
        for link in re.findall(r"\]\(([^\s)]+)\)", content):
            if "://" in link or link.startswith(("#", "mailto:")):
                continue
            target = (path.parent / link.split("#")[0]).resolve()
            if not target.is_relative_to(ROOT) or not target.exists():
                errors.append(f"Broken/outside local link in {path.relative_to(ROOT)}: {link}")
    for path in (ROOT / "skills/guard-raillm").rglob("*"):
        if path.is_symlink() or getattr(path.lstat(), "st_file_attributes", 0) & 0x400:
            errors.append("Skill contains a link/reparse point")
    for error in errors:
        print(error, file=sys.stderr)
    print(f"Validation: {len(errors)} error(s). This is structural validation, not a security audit.")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(validate())
