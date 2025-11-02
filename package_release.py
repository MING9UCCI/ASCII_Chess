#!/usr/bin/env python3
"""Utility script to bundle ASCII Chess into a standalone executable."""

from __future__ import annotations

import argparse
import importlib.util
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENGINE_ROOT = ROOT / "engines" / "stockfish"
DIST_DIR = ROOT / "dist"
BUILD_DIR = ROOT / "build"
SPEC_FILE = ROOT / "ascii_chess.spec"


def ensure_pyinstaller() -> None:
    if importlib.util.find_spec("PyInstaller") is None:
        raise RuntimeError(
            "PyInstaller is not installed. Install it with `python -m pip install pyinstaller`."
        )


def build(include_engine: bool) -> None:
    ensure_pyinstaller()

    add_data_entries = [
        f"{ROOT / 'ascii_chess' / 'fonts' / 'menlo-regular.ttf'}{os.pathsep}ascii_chess/fonts",
        f"{ROOT / 'engines' / 'README.md'}{os.pathsep}engines",
    ]

    if include_engine:
        if not ENGINE_ROOT.exists():
            raise RuntimeError("Stockfish not found under engines/stockfish/. Download and place it there first.")
        add_data_entries.append(f"{ENGINE_ROOT}{os.pathsep}engines/stockfish")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--name",
        "ascii_chess",
    ]

    for entry in add_data_entries:
        cmd.extend(["--add-data", entry])

    cmd.append(str(ROOT / "main.py"))

    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd)

    print("\nDone! Executable created in the dist/ directory.")
    if platform.system() == "Windows":
        print("  -> dist\\ascii_chess.exe")
    elif platform.system() == "Darwin":
        print("  -> dist/ascii_chess")
    else:
        print("  -> dist/ascii_chess (Linux binary)")


def clean() -> None:
    for path in (DIST_DIR, BUILD_DIR, SPEC_FILE):
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build standalone ASCII Chess executable.")
    parser.add_argument("--with-engine", action="store_true", help="Bundle engines/stockfish contents")
    parser.add_argument("--clean", action="store_true", help="Remove previous dist/build/spec first")
    args = parser.parse_args()

    if args.clean:
        clean()

    if args.with_engine and not ENGINE_ROOT.exists():
        print("ERROR: engines/stockfish/ not found. Prepare the engine before bundling.", file=sys.stderr)
        sys.exit(1)

    try:
        build(include_engine=args.with_engine)
    except Exception as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
