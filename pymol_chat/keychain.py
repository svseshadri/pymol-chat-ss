"""Store an API key using the platform's available credential storage."""

from __future__ import annotations

import getpass
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from .config import APP_DIR


SERVICE = "org.openai.pymol-chat"
ACCOUNT = getpass.getuser()
SECURITY = "/usr/bin/security"
KEY_FILE = APP_DIR / "openai_api_key"


def storage_name() -> str:
    return "macOS Keychain" if sys.platform == "darwin" else "private local file"


def storage_description() -> str:
    if sys.platform == "darwin":
        return "the macOS login Keychain"
    return f"{KEY_FILE} with access limited to your user account"


def read_api_key() -> str:
    if sys.platform != "darwin":
        try:
            return KEY_FILE.read_text(encoding="utf-8").strip()
        except OSError:
            return ""

    try:
        result = subprocess.run(
            [SECURITY, "find-generic-password", "-a", ACCOUNT, "-s", SERVICE, "-w"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def save_api_key(value: str) -> None:
    key = value.strip()
    if not key:
        raise ValueError("Enter an API key before saving.")

    if sys.platform != "darwin":
        temporary_path: Path | None = None
        try:
            APP_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
            descriptor, name = tempfile.mkstemp(prefix=".openai_api_key.", dir=APP_DIR)
            temporary_path = Path(name)
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(key + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.chmod(temporary_path, 0o600)
            os.replace(temporary_path, KEY_FILE)
            temporary_path = None
            return
        except OSError as exc:
            raise RuntimeError(f"Could not save the API key in {storage_name()}.") from exc
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    try:
        result = subprocess.run(
            [
                SECURITY,
                "add-generic-password",
                "-U",
                "-a",
                ACCOUNT,
                "-s",
                SERVICE,
                "-w",
                key,
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise RuntimeError("Could not save the API key in macOS Keychain.") from exc
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Could not save the API key in macOS Keychain.")


def delete_api_key() -> None:
    if sys.platform != "darwin":
        try:
            KEY_FILE.unlink(missing_ok=True)
        except OSError as exc:
            raise RuntimeError(f"Could not remove the API key from {storage_name()}.") from exc
        return

    subprocess.run(
        [SECURITY, "delete-generic-password", "-a", ACCOUNT, "-s", SERVICE],
        check=False,
        capture_output=True,
        timeout=5,
    )
