#!/usr/bin/env python3
"""Copy the local skill to an explicit skills directory; never overwrite."""
import argparse
from pathlib import Path
import shutil


def install(destination):
    source = Path(__file__).resolve().parents[1] / "skills" / "guard-raillm"
    destination = Path(destination).expanduser().resolve()
    target = destination / "guard-raillm"
    if target.is_relative_to(source.resolve()):
        raise ValueError("Destination cannot be inside the source skill")
    if target.exists() or target.is_symlink():
        raise ValueError("Target already exists; review and manage the existing installation manually")
    for path in source.rglob("*"):
        if path.is_symlink() or getattr(path.lstat(), "st_file_attributes", 0) & 0x400:
            raise ValueError("Source contains a link or reparse point; refusing installation")
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copyfile(source.parents[1] / "LICENSE", target / "LICENSE")
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", type=Path, required=True, help="Parent skills directory, not the skill folder")
    args = parser.parse_args()
    try:
        target = install(args.dest)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Installation failed: {exc}\n")
    print(f"Installed: {target}")


if __name__ == "__main__":
    main()
