import hashlib
from pathlib import Path
import unittest
import zipfile

from test_helpers import ROOT, module

packager = module("packager", ROOT / "scripts/package.py")


class PackageTests(unittest.TestCase):
    def test_reproducible_complete_archive(self):
        archive = packager.build()
        first = hashlib.sha256(archive.read_bytes()).digest()
        packager.build()
        self.assertEqual(first, hashlib.sha256(archive.read_bytes()).digest())
        with zipfile.ZipFile(archive) as bundle:
            self.assertIsNone(bundle.testzip())
            names = bundle.namelist()
            self.assertIn("guard-raillm/SKILL.md", names)
            self.assertIn("guard-raillm/LICENSE", names)
            self.assertIn("guard-raillm/references/reporting.md", names)
            self.assertFalse(any("__pycache__" in name or ".." in Path(name).parts for name in names))


if __name__ == "__main__":
    unittest.main()
