from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, Mock

from start_jarvis import prepare


class LauncherTests(unittest.TestCase):
    def test_existing_configuration_preserved_and_repeat_start_skips_pip(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            python = root / ".venv" / "Scripts" / "python.exe"
            python.parent.mkdir(parents=True)
            python.touch()
            (root / "requirements.txt").write_text("streamlit>=1.66,<2\n")
            (root / ".env").write_text("PRIVATE=value\n")
            with patch("start_jarvis.subprocess.run", return_value=Mock(returncode=0)) as install:
                self.assertEqual(prepare(root), python)
                install.assert_called_once()
                self.assertIn("--no-index", install.call_args.args[0])
                prepare(root)
                install.assert_called_once()
            self.assertEqual((root / ".env").read_text(), "PRIVATE=value\n")

    def test_failed_install_is_not_marked_ready(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            python = root / ".venv" / "Scripts" / "python.exe"
            python.parent.mkdir(parents=True)
            python.touch()
            (root / "requirements.txt").write_text("streamlit>=1.66,<2\n")
            with patch("start_jarvis.subprocess.run", side_effect=[Mock(returncode=1), OSError("offline")]):
                with self.assertRaises(OSError):
                    prepare(root)
            self.assertFalse((root / ".venv" / "jarvis-requirements.sha256").exists())
