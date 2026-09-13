#!/usr/bin/env python3
"""Offline, filename-only project inventory. Never reads file contents."""
import argparse
import json
import os
from pathlib import Path
import stat

EXCLUDED = {".git", "node_modules", ".venv", "venv", "vendor", "__pycache__", ".guard-raillm"}
MARKERS = {
    "package.json": "javascript", "pyproject.toml": "python", "requirements.txt": "python",
    "go.mod": "go", "Cargo.toml": "rust", "pom.xml": "java", "composer.json": "php",
    "Gemfile": "ruby", "Dockerfile": "container", "firebase.json": "firebase",
    "firestore.rules": "firebase-rules", "schema.prisma": "prisma",
}


def inventory(root, max_entries=20000):
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Project root must be a directory")
    result = {"schema_version": 1, "kind": "filename-inventory", "content_read": False,
              "network_used": False, "entries_seen": 0, "markers": [], "env_paths": [],
              "security_paths": [], "skipped": [], "errors": [], "truncated": False,
              "limitations": ["Not a vulnerability or secret scan", "No Git history inspected",
                              "Excluded directories and links are not inspected",
                              "Filenames may themselves be sensitive; review before sharing"]}
    pending = [root]
    while pending:
        directory = pending.pop()
        try:
            with os.scandir(directory) as entries:
                for entry in entries:
                    if result["entries_seen"] >= max_entries:
                        result["truncated"] = True
                        return result
                    result["entries_seen"] += 1
                    relative = Path(entry.path).relative_to(root).as_posix()
                    try:
                        info = entry.stat(follow_symlinks=False)
                        reparse = getattr(info, "st_file_attributes", 0) & 0x400
                        if stat.S_ISLNK(info.st_mode) or reparse:
                            result["skipped"].append({"path": relative, "reason": "link-or-reparse-point"})
                        elif stat.S_ISDIR(info.st_mode):
                            if entry.name in EXCLUDED:
                                result["skipped"].append({"path": relative, "reason": "excluded-directory"})
                            else:
                                pending.append(Path(entry.path))
                        elif stat.S_ISREG(info.st_mode):
                            if entry.name in MARKERS:
                                result["markers"].append({"path": relative, "type": MARKERS[entry.name]})
                            if entry.name == ".env" or entry.name.startswith(".env.") or entry.name.endswith(".env"):
                                result["env_paths"].append(relative)
                            if (relative.startswith(".github/workflows/") or entry.name.endswith((".tf", ".rules", ".sql"))
                                    or entry.name in {".gitignore", ".dockerignore", "docker-compose.yml", "compose.yaml"}):
                                result["security_paths"].append(relative)
                        else:
                            result["skipped"].append({"path": relative, "reason": "non-regular-file"})
                    except OSError:
                        result["errors"].append({"path": relative, "reason": "metadata-unavailable"})
        except OSError:
            result["errors"].append({"path": directory.relative_to(root).as_posix(), "reason": "directory-unreadable"})
    for key in ("env_paths", "security_paths"):
        result[key].sort()
    for key in ("markers", "skipped", "errors"):
        result[key].sort(key=lambda value: value["path"])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--max-entries", type=int, default=20000)
    args = parser.parse_args()
    if args.max_entries < 1:
        parser.error("--max-entries must be positive")
    try:
        result = inventory(args.root, args.max_entries)
    except (OSError, ValueError):
        parser.exit(2, "Cannot inventory project directory.\n")
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 2 if result["errors"] or result["truncated"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
