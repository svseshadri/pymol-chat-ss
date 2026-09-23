# Chat with PyMOL

Chat with PyMOL embeds a natural-language assistant in the PyMOL Qt interface. It can inspect the current molecular scene, fetch public PDB structures, and perform constrained PyMOL operations from typed requests.

This repository supports:

- Linux source installations using conda-forge PyMOL
- Remote Linux sessions using X11 forwarding or a remote desktop
- macOS source installations and the packaged macOS launcher
- API-key storage that persists across restarts
- A command log showing generated PyMOL code, results, and errors

![Chat with PyMOL controlling a human hemoglobin structure](docs/images/chat-with-pymol.png)

## Quick start on Linux

The recommended installation uses Conda or Miniconda:

```bash
git clone https://github.com/RomeroLab/pymol-chat.git
cd pymol-chat
conda env create -f environment.yml
conda activate pymol-chat
./run.sh
```

If this checkout already has the environment created, only the last three commands are needed:

```bash
cd ~/pymol-chat
conda activate pymol-chat
./run.sh
```

The launcher finds the active environment's `pymol` executable. To use a specific executable, set `PYMOL_BIN`:

```bash
PYMOL_BIN=/path/to/pymol ./run.sh
```

### Remote Linux over SSH

PyMOL is a graphical application. Start a new SSH connection with trusted X11 forwarding from the computer where the window should appear:

```bash
ssh -Y username@remote-host
```

Check the forwarded display before launching:

```bash
echo "$DISPLAY"
xdpyinfo >/dev/null && echo "X11 forwarding works"
```

`DISPLAY` should contain a value such as `localhost:10.0`. Then activate the environment and run the plugin:

```bash
cd ~/pymol-chat
conda activate pymol-chat
./run.sh
```

The local computer needs an X server:

- Linux normally provides one with the desktop session.
- macOS requires XQuartz to be running before the SSH connection is created.
- Windows can use MobaXterm, VcXsrv, or WSLg.

X11 forwarding must be requested for every new SSH session. Do not set `DISPLAY` manually. For smoother molecular rendering, a VNC or other remote-desktop session is usually faster than X11 forwarding.

## API key

An OpenAI API key with API billing enabled is required. On first launch, paste the key into the API Key Settings dialog.

Keys saved by the dialog are stored as follows:

| Platform | Storage |
| --- | --- |
| macOS | Login Keychain |
| Linux | `~/.pymol-chat/openai_api_key`, mode `0600` |

The saved key takes priority over `OPENAI_API_KEY` and a local `.env` file. It is never displayed again or stored in PyMOL session files.

Alternative configuration:

```bash
export OPENAI_API_KEY="your-key-here"
./run.sh
```

Or create a private development file:

```bash
cp .env.example .env
```

Edit `.env` and replace the placeholder. The file is ignored by Git and must never be committed.

## First test

Use this prompt to exercise structure retrieval, selections, representations, coloring, and camera control:

```text
Fetch PDB 1YY9, display the complex as a cartoon, color EGFR cyan and cetuximab orange, highlight EGFR residues within 4 angstroms of cetuximab as red sticks, and orient the view around the binding interface.
```

Open **... -> Show Command Log** to inspect generated commands and errors. The log is especially useful when a request changes the scene but returns an incomplete summary.

## Using the assistant

Open a structure with PyMOL's normal controls or ask the assistant to fetch a public PDB entry. Example requests:

- `Show the protein as a cartoon and color each chain differently.`
- `Select residues within 4 angstroms of the ligand.`
- `Download 2HHB and show the heme groups as sticks.`
- `Make a publication-style view and orient around the active site.`

The assistant can use one constrained local tool that executes PyMOL Python. Requests allow at most three command rounds, including structural queries and repair attempts. Larger tasks may require a follow-up request.

Simple visual changes can use a prepared confirmation immediately after successful execution. Measurements, scientific interpretation, errors, and complex operations receive an additional model review before the final reply.

### Voice features

Voice input and spoken replies are primarily supported by the packaged macOS build. Spoken replies use the Marin voice and incur additional API usage. Turn **... -> Spoken Replies** off when Qt audio is unavailable, which is common on remote Linux systems. The written assistant remains fully usable.

## macOS installation

For the packaged application:

1. Install a Qt-based PyMOL 2.x release in `/Applications/PyMOL.app`.
2. Download `Chat-with-PyMOL-macOS.dmg` from the upstream project's latest release.
3. Open the DMG and drag **Chat with PyMOL** into **Applications**.
4. Launch **Chat with PyMOL**, then enter an API key when prompted.
5. Allow microphone access if voice input is needed.

The packaged launcher is Developer ID-signed and notarized. See [docs/INSTALL.md](docs/INSTALL.md) for the complete macOS guide.

A source checkout can also be launched with:

```bash
PYMOL_APP=/Applications/PyMOL.app ./run.sh
```

## Configuration

| Variable | Purpose | Default |
| --- | --- | --- |
| `OPENAI_API_KEY` | API credential fallback | None |
| `OPENAI_MODEL` | Responses API model | `gpt-5.6-sol` |
| `OPENAI_TRANSCRIBE_MODEL` | Voice transcription model | `gpt-4o-mini-transcribe` |
| `OPENAI_REASONING_EFFORT` | Model reasoning effort | `medium` |
| `PYMOL_CHAT_WORKDIR` | Private captures/downloads directory | `~/.pymol-chat` |
| `PYMOL_BIN` | Linux/Unix PyMOL executable | First `pymol` on `PATH` |
| `PYMOL_APP` | macOS application bundle | `/Applications/PyMOL.app` |

Use `OPENAI_REASONING_EFFORT=low` for potentially faster responses at the cost of some performance on complex requests.

## Troubleshooting

### PyMOL was not found on PATH

Activate the environment first:

```bash
conda activate pymol-chat
./run.sh
```

Confirm the executable is present:

```bash
command -v pymol
```

### Qt could not connect to display

The current shell has no usable graphical display. On a remote machine, disconnect and create a fresh `ssh -Y` session after starting the local X server. Verify with `xdpyinfo` before launching.

### The window has stripes or renders slowly

The startup log may report Mesa `llvmpipe`, which is software rendering over the forwarded display. Use a remote desktop/VNC session for better OpenGL behavior. This is separate from the chat plugin.

### The assistant remains on Working

Current code marshals live PyMOL operations to Qt's main thread to avoid worker-thread lockups. Quit any instance started before updating the code and launch it again. If a new request still stalls, open **... -> Show Command Log** and retain the generated commands before restarting.

### No final summary appears

The scene may still have changed. Open **... -> Show Command Log** and inspect the latest command and result before repeating an operation.

### Audio output does not support Marin playback

Disable **... -> Spoken Replies**. This does not affect text replies or molecular operations.

### API key problems

Open **... -> API Key Settings** to replace the saved key. On Linux, verify private permissions without printing the secret:

```bash
stat -c '%a %U %n' ~/.pymol-chat/openai_api_key
```

The expected mode is `600`.

## Development

Create or update the reproducible environment:

```bash
conda env create -f environment.yml
conda activate pymol-chat
```

Run all tests without opening a visible window:

```bash
QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests -v
```

No third-party packages beyond the PyMOL environment are listed in `requirements.txt`; the OpenAI client uses Python's standard library.

Build the universal macOS launcher and DMG:

```bash
./build_dmg.sh
```

The artifact is written to `outputs/Chat-with-PyMOL-macOS.dmg`.

## Project structure

| Path | Responsibility |
| --- | --- |
| `launch_plugin.py` | Registers and opens the PyMOL plugin |
| `run.sh` | Cross-platform source launcher |
| `pymol_chat/ui.py` | Qt dock, background tasks, and main-thread PyMOL bridge |
| `pymol_chat/agent.py` | Responses API tool loop and conversation state |
| `pymol_chat/api_client.py` | Dependency-free OpenAI HTTP client |
| `pymol_chat/executor.py` | Constrained live PyMOL execution |
| `pymol_chat/config.py` | Environment and application directories |
| `pymol_chat/keychain.py` | macOS Keychain and Linux private-file credentials |
| `pymol_chat/audio.py` | Voice capture and transcription |
| `pymol_chat/speech.py` | Spoken-reply streaming |
| `tests/` | Unit and Qt integration tests |
| `packaging/` | macOS launcher metadata and sources |
| `voice_helper/` | Native macOS microphone helper |

## Privacy and security

- Prompt text, compact scene metadata, generated commands, and command results are sent to OpenAI.
- Results can include residue identities, sequences, coordinates, distances, and other molecular information queried from a local structure.
- Local structure files and viewport screenshots are not uploaded by the plugin.
- Voice recordings are sent to OpenAI for transcription when voice input is used.
- Reply text is sent for speech generation when spoken replies are enabled.
- Public structures fetched through PyMOL are stored under `~/.pymol-chat/downloads` by default.
- Generated Python is checked to block common shell, filesystem, networking, and unsafe PyMOL command paths.
- These checks reduce risk but are not an operating-system sandbox. Save important PyMOL sessions before destructive requests.
- Do not use confidential molecular data unless sending the described metadata to OpenAI is permitted.

## Git repository

This directory is a complete Git repository and retains the upstream project history for attribution and future comparison. The Linux compatibility, credential storage, and threading fixes are committed locally. No API keys, downloaded structures, sessions, build artifacts, or `.env` files are tracked.

## License

Chat with PyMOL is released under the [MIT License](LICENSE).
