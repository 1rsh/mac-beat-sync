#!/usr/bin/env python3
"""CLI wrapper exposing runtime overrides for config and making the tool installable.

This script parses optional arguments that map to keys in `config.yaml` and then
launches the main app. It uses `utils.set_config_overrides` to apply runtime
overrides before the rest of the app loads the config.
"""
from __future__ import annotations

import argparse

from mac_beat_sync.utils.utils import set_config_overrides


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="mac-beat-sync")

    # Device selection
    p.add_argument("--device-index", type=int, help="Input device index to use (overrides auto-detection)")

    # Audio config
    p.add_argument("--sample-rate", type=int, dest="SAMPLE_RATE", help="Audio sample rate (Hz)")
    p.add_argument("--block-size", type=int, dest="BLOCK_SIZE", help="Audio block size (frames)")
    p.add_argument("--smoothing", type=float, dest="SMOOTHING", help="EMA smoothing factor (0-1)")
    p.add_argument("--window-seconds", type=float, dest="WINDOW_SECONDS", help="Rolling window length in seconds")
    p.add_argument("--update-interval", type=float, dest="UPDATE_INTERVAL", help="Minimum seconds between keyboard updates")
    p.add_argument("--gamma", type=float, dest="GAMMA", help="Gamma correction applied to brightness")
    p.add_argument("--weight-rms", type=float, dest="WEIGHT_RMS", help="Weight for RMS energy in combined intensity")
    p.add_argument("--weight-beat", type=float, dest="WEIGHT_BEAT", help="Weight for beat/onset intensity")

    # Driver config
    p.add_argument("--cli-tool", type=str, dest="CLI_TOOL", help="Path to CLI tool used to set keyboard brightness")

    return p.parse_args()


def build_overrides_from_args(args: argparse.Namespace) -> dict:
    overrides: dict = {}

    # audio group
    audio_keys = [
        "SAMPLE_RATE",
        "BLOCK_SIZE",
        "SMOOTHING",
        "WINDOW_SECONDS",
        "UPDATE_INTERVAL",
        "GAMMA",
        "WEIGHT_RMS",
        "WEIGHT_BEAT",
    ]

    audio_overrides = {}
    for k in audio_keys:
        v = getattr(args, k, None)
        if v is not None:
            audio_overrides[k] = v

    if audio_overrides:
        overrides["audio"] = audio_overrides

    # driver group
    if getattr(args, "CLI_TOOL", None) is not None:
        overrides.setdefault("driver", {})["CLI_TOOL"] = args.CLI_TOOL

    return overrides


def main():
    args = parse_args()
    overrides = build_overrides_from_args(args)

    if overrides:
        set_config_overrides(overrides)

    # Import main lazily so that modules read the overridden config
    from .main import main as app_main

    app_main(device_index=args.device_index)


if __name__ == "__main__":
    main()
