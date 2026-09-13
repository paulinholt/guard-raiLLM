import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


inv = module("inventory", ROOT / "skills/guard-raillm/scripts/inventory.py")
installer = module("installer", ROOT / "scripts/install.py")


class InventoryTests(unittest.TestCase):
    def test_names_only_and_exclusions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            secret = "synthetic-sensitive-content-do-not-output"
            (root / ".env").write_text(secret)
            (root / "package.json").write_text("this is not executable JSON")
            (root / "node_modules").mkdir()
            (root / "node_modules/.env").write_text(secret)
            result = inv.inventory(root)
            self.assertNotIn(secret, json.dumps(result))
            self.assertEqual(result["env_paths"], [".env"])
            self.assertEqual(result["markers"], [{"path": "package.json", "type": "javascript"}])
            self.assertTrue(result["skipped"])

    def test_external_link_not_followed(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            (Path(outside) / ".env").write_text("synthetic")
            try:
                (Path(tmp) / "escape").symlink_to(outside, target_is_directory=True)
            except OSError:
                self.skipTest("OS does not permit symlink creation")
            result = inv.inventory(tmp)
            self.assertEqual(result["env_paths"], [])
            self.assertEqual(result["skipped"][0]["reason"], "link-or-reparse-point")

    def test_truncation_is_nonpassing(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ("a", "b", "c"):
                (Path(tmp) / name).touch()
            run = subprocess.run([sys.executable, str(ROOT / "skills/guard-raillm/scripts/inventory.py"),
                                  tmp, "--max-entries", "1"], capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertTrue(json.loads(run.stdout)["truncated"])

    def test_invalid_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                inv.inventory(Path(tmp) / "missing")


class InstallerTests(unittest.TestCase):
    def test_install_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = installer.install(Path(tmp) / "skills")
            self.assertTrue((target / "SKILL.md").is_file())
            self.assertTrue((target / "references/data.md").is_file())
            self.assertTrue((target / "LICENSE").is_file())
            (target / "SKILL.md").write_text("user customization")
            with self.assertRaises(ValueError):
                installer.install(Path(tmp) / "skills")
            self.assertEqual((target / "SKILL.md").read_text(), "user customization")

    def test_refuse_recursive_destination(self):
        with self.assertRaises(ValueError):
            installer.install(ROOT / "skills/guard-raillm/nested")


if __name__ == "__main__":
    unittest.main()
