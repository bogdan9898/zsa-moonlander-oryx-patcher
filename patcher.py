#!/usr/bin/env python3
"""
Moonlander Oryx patch + compile script
Usage: python moonlander_patch.py <path-to-oryx-zip>

Expects os_detection.patch to be in the same directory as this script.
"""

import sys
import shutil
import tempfile
import zipfile
import subprocess
from pathlib import Path

PATCH_FILE = str(Path(__file__).parent / "zsa_moonlander_macos.patch")
QMK_DIR    = "/home/bogdan/Desktop/qmk_firmware"
KEYMAP_DIR = f"{QMK_DIR}/keyboards/zsa/moonlander/keymaps/macos_keymap"
KEYBOARD   = "zsa/moonlander/revb"
KEYMAP_NAME = "macos_keymap"

def info(msg):    print(f"[info]  {msg}")
def success(msg): print(f"[ok]    {msg}")
def error(msg):   print(f"[error] {msg}"); sys.exit(1)


def extract_zip(zip_path, target_dir):
    info(f"Extracting {zip_path}...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(target_dir)


def setup_keymap_dir(tmp_dir):
    oryx_source = f"{tmp_dir}/zsa_moonlander_mission-control_source"

    # Apply patch to the extracted source
    info("Applying patch...")
    result = subprocess.run(
        [
            "patch",
            "--strip=5",
            "--directory", oryx_source,
            "--input", PATCH_FILE,
            "--forward",
            "--reject-file=-",
        ],
    )
    if result.returncode != 0:
        error("patch failed. Your Oryx layout may have changed too much from the original diff.")
    success("Patch applied")

    # Handle existing keymap dir
    if Path(KEYMAP_DIR).exists():
        answer = input(f"\n'{KEYMAP_DIR}' already exists. Delete it? [y/N]: ").strip().lower()
        if answer in ("y", "yes"):
            shutil.rmtree(KEYMAP_DIR)
        else:
            sys.exit(1)

    info(f"Copying files to {KEYMAP_DIR}...")
    shutil.copytree(oryx_source, KEYMAP_DIR)
    success("Keymap directory ready")


def cleanup_bin_files():
    bin_files = list(Path(QMK_DIR).glob("*.bin"))
    if bin_files:
        info(f"Removing {len(bin_files)} old .bin file(s)...")
        for f in bin_files:
            f.unlink()
            info(f"  deleted {f.name}")
        success("Old .bin files removed")


def compile_keymap():
    cleanup_bin_files()
    info("Compiling keymap (this may take a minute)...")
    result = subprocess.run(
        ["qmk", "compile", "-kb", KEYBOARD, "-km", KEYMAP_NAME],
        cwd=QMK_DIR,
    )
    if result.returncode != 0:
        error("Compilation failed. Check the output above for details.")
    success("Done! Flash the .bin from the qmk_firmware root with Keymapp.")


def main():
    if len(sys.argv) != 2:
        error(f"Usage: python {sys.argv[0]} <path-to-oryx-zip>")

    zip_path = sys.argv[1]

    if not Path(zip_path).is_file():
        error(f"File not found: {zip_path}")

    if not Path(QMK_DIR).exists():
        clone_repo_cmd = "git clone https://github.com/zsa/qmk_firmware && cd qmk_firmware && git submodule update --init --recursive"
        error(f"'{QMK_DIR}' directory is missing; please clone the repo and try again:\n    {clone_repo_cmd}")

    with tempfile.TemporaryDirectory() as tmp_dir:
        extract_zip(zip_path, tmp_dir)
        setup_keymap_dir(tmp_dir)

    compile_keymap()


if __name__ == "__main__":
    main()
