# zsa-moonlander-oryx-patcher
Applies a custom QMK patch to a ZSA Oryx source export and compiles it for the Moonlander keyboard.

The patch automatically swaps `Alt`/`GUI` on linux/linux based on OS-detection — no manual layer switching needed.

## Requirements

- Python 3.10+
- `patch` binary (pre-installed on most Linux/macOS systems)
- QMK CLI
- ZSA's QMK firmware fork, which you are responsible for cloning yourself:

```bash
git clone https://github.com/zsa/qmk_firmware
cd qmk_firmware
git submodule update --init --recursive
```

## Usage

1. Download your layout source from Oryx (the **Source Code** button, not the firmware)
2. Place `os_detection.patch` in the same directory as the script
3. Run:

```bash
python patcher.py <path-to-oryx-zip>
```

4. Flash the resulting `.bin` from your `qmk_firmware` folder using Keymapp or the qmk cli
