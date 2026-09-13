#!/usr/bin/env python3
"""Build a deterministic ZIP of the skill and its license, plus SHA-256."""
import hashlib
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def build():
    source = ROOT / "skills/guard-raillm"
    output = ROOT / "dist"
    output.mkdir(exist_ok=True)
    archive = output / "guard-raillm-0.1.0.zip"
    files = []
    for path in sorted(source.rglob("*")):
        if path.is_symlink() or getattr(path.lstat(), "st_file_attributes", 0) & 0x400:
            raise ValueError("Refusing to package links/reparse points")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
            files.append((path, "guard-raillm/" + path.relative_to(source).as_posix()))
    files.append((ROOT / "LICENSE", "guard-raillm/LICENSE"))
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path, name in sorted(files, key=lambda item: item[1]):
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, path.read_bytes())
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    (output / "SHA256SUMS").write_text(f"{checksum}  {archive.name}\n", encoding="ascii")
    print(f"Created {archive.name}: {len(files)} files; SHA-256 {checksum}")
    return archive


if __name__ == "__main__":
    build()
