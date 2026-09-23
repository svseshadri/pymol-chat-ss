"""Credential storage tests using fake API keys and temporary paths."""

import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pymol_chat import keychain


class LocalCredentialStorageTests(unittest.TestCase):
    def test_local_key_round_trip_uses_private_permissions(self):
        with tempfile.TemporaryDirectory() as directory:
            app_dir = Path(directory) / "app"
            key_file = app_dir / "openai_api_key"
            with (
                patch.object(keychain.sys, "platform", "linux"),
                patch.object(keychain, "APP_DIR", app_dir),
                patch.object(keychain, "KEY_FILE", key_file),
            ):
                keychain.save_api_key("  sk-test-local-credential  ")

                self.assertEqual(keychain.read_api_key(), "sk-test-local-credential")
                self.assertEqual(stat.S_IMODE(key_file.stat().st_mode), 0o600)

                keychain.delete_api_key()
                self.assertEqual(keychain.read_api_key(), "")

    def test_empty_key_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Enter an API key"):
            keychain.save_api_key("   ")


if __name__ == "__main__":
    unittest.main()
