# mac-beat-sync
A small macOS utility that reads audio (system or input) and uses it to control a Mac keyboard's backlight brightness and a simple visual output. The project captures audio, computes a brightness/intensity value, and drives a CLI-based keyboard brightness tool while displaying progress bars for raw and smoothed values.

## Features
- Capture audio (via a virtual device like BlackHole or a physical input)
- Compute loudness and beat/onset intensity
- Smooth and gamma-correct brightness output
- Drive a CLI tool to set keyboard brightness (configurable)

## Requirements
- macOS
- Python 3.9+ (project uses simple stdlib + small dependencies)
- Python packages: `sounddevice`, `numpy`, `pyyaml`, `tqdm`

- External CLI dependency: `mac-brightnessctl` (used by default via `driver.CLI_TOOL`).
   - Install with Homebrew (tap + install):
      ```bash
      brew tap rakalex/mac-brightnessctl
      brew install mac-brightnessctl
      ```
   - After installing, ensure the path in `config.yaml` (`driver.CLI_TOOL`) points to the installed binary (commonly `/opt/homebrew/bin/mac-brightnessctl` on Apple Silicon/Homebrew default).

Install Python packages (recommend using a virtualenv):

```bash
python -m pip install -r requirements.txt
```

## Installation (BlackHole and Audio routing)
- Install BlackHole (virtual audio device) if you need to capture system output. Common install via Homebrew:

```bash
# 2-channel BlackHole (common choice)
brew install blackhole-2ch
```

- Create a Multi-Output Device in Audio MIDI Setup that includes BlackHole and your physical output so you can still hear sound while routing a copy to BlackHole. Enable drift correction on BlackHole. Set the Multi-Output Device as the system output.

Refer to macOS Audio MIDI Setup for details — the app itself does not modify macOS audio settings.

- Install `mac-brightnessctl` from https://github.com/rakalex/mac-brightnessctl
```bash
brew tap rakalex/mac-brightnessctl
brew install mac-brightnessctl
```

## Usage
1. Ensure your system audio is routed to a device that the app can capture (BlackHole Multi-Output, or physical input).
2. Run the app from the project root:

```bash
python main.py
```

The app will try to auto-detect a device named `BlackHole` (case-insensitive). If not found, it will prompt for an input device index. You can list devices with the snippet in the Configuration section.

When running, the app prints two progress bars:
- Raw Brightness: instantaneous estimate
- Smoothed Output: EMA- smoothed, gamma-corrected output applied to the keyboard

Interrupt with Ctrl+C to exit; the app will reset the keyboard to a default brightness before closing.

## Configuration
All runtime configuration is read from `config.yaml` in the project root. Below are the available keys, their defaults (from the shipped `config.yaml`), and a brief description.

audio:
- SAMPLE_RATE (default: 44100)
   - Audio sampling rate in Hz. Must match your audio device/sample rate for best results.

- BLOCK_SIZE (default: 1024)
   - Number of frames per audio block processed. Affects latency and FFT resolution.

- SMOOTHING (default: 0.05)
   - Exponential moving average smoothing factor for the smoothed brightness (higher = slower changes).

- WINDOW_SECONDS (default: 0.3)
   - Length of the rolling window (in seconds) used for averaging RMS history and short-term stats.

- UPDATE_INTERVAL (default: 0.2)
   - Minimum wall-clock seconds between keyboard update calls (rate limiting to avoid excessive CLI calls).

- GAMMA (default: 1.1)
   - Gamma correction applied to perceptual brightness. Values >1 reduce perceived brightness of low values.

- WEIGHT_RMS (default: 0.2)
   - Weight applied to normalized RMS energy when combining features into a single intensity.

- WEIGHT_BEAT (default: 0.8)
   - Weight applied to beat/onset intensity when combining features.

driver:
- CLI_TOOL (default: "/opt/homebrew/bin/mac-brightnessctl")
   - Path to the external CLI tool used to set keyboard brightness. The app calls this tool with a single numeric argument (0–1). Replace with your installed utility or script.

Example `config.yaml` (defaults shipped with repo):

```yaml
audio:
   SAMPLE_RATE: 44100
   BLOCK_SIZE: 1024
   SMOOTHING: 0.95
   WINDOW_SECONDS: 0.3
   UPDATE_INTERVAL: 0.2
   GAMMA: 1.1
   WEIGHT_RMS: 0.2
   WEIGHT_BEAT: 0.8
driver:
   CLI_TOOL: "/opt/homebrew/bin/mac-brightnessctl"
```

Edit values in `config.yaml` and restart the app to apply changes.

### How to find device indices
If the app prompts for an input device index or you want to confirm device names, run:

```bash
python -c "import sounddevice as sd; print(sd.query_devices())"
```

Look for a device whose `name` contains `BlackHole` (if you installed it). Note the index and enter it when prompted.

## Troubleshooting & Notes
- If you hear no audio after switching system output to a Multi-Output Device, verify that the physical output is checked and set as the master clock in Audio MIDI Setup.
- If BlackHole doesn't appear after installation, log out or reboot.
- Keep `SAMPLE_RATE` consistent between Audio MIDI Setup and `config.yaml` for best audio fidelity.

## Contributing
Pull requests welcome. Small, focused changes and documentation improvements are preferred.

---

