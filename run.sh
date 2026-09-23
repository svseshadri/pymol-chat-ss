#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYSTEM_NAME="$(uname -s)"

if [[ "$SYSTEM_NAME" == "Darwin" ]]; then
  PYMOL_APP="${PYMOL_APP:-/Applications/PyMOL.app}"

  if [[ ! -x "$PYMOL_APP/Contents/bin/pymol" ]]; then
    echo "PyMOL was not found at $PYMOL_APP" >&2
    echo "Set PYMOL_APP to the application location and try again." >&2
    exit 1
  fi

  if command -v xcrun >/dev/null 2>&1; then
    "$PROJECT_DIR/voice_helper/build.sh"
  else
    echo "Warning: Xcode Command Line Tools are unavailable; voice input will be disabled." >&2
  fi

  exec "$PYMOL_APP/Contents/bin/pymol" -r "$PROJECT_DIR/launch_plugin.py" "$@"
else
  if [[ -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
    echo "No graphical display is available." >&2
    echo "For a remote session, reconnect with SSH X11 forwarding (for example: ssh -Y host)." >&2
    exit 1
  fi

  PYMOL_BIN="${PYMOL_BIN:-}"
  if [[ -z "$PYMOL_BIN" ]]; then
    if command -v pymol >/dev/null 2>&1; then
      PYMOL_BIN="$(command -v pymol)"
    else
      echo "PyMOL was not found on PATH." >&2
      echo "Activate an environment with PyMOL or set PYMOL_BIN to the pymol executable." >&2
      exit 1
    fi
  fi

  if [[ ! -x "$PYMOL_BIN" ]]; then
    echo "PyMOL is not executable at $PYMOL_BIN" >&2
    exit 1
  fi

  exec "$PYMOL_BIN" -r "$PROJECT_DIR/launch_plugin.py" "$@"
fi
