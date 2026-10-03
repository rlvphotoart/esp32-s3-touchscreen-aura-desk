# ESP32 inspection environment — original setup audit

**2026-10-03 update:** This document retains the initial inspection-tool audit. AURA Desk 1.0.0 has since been built and installed using isolated Arduino CLI, pinned Arduino-ESP32 3.1.1, its matching official high-performance SDK, `DebugLevel=none`, and two 5 MiB app slots. Serial app-only updates require a fresh verified full backup; no eFuse changes were made. Use the [current build guide](FIRMWARE_BUILD.md), [user manual](AURA_DESK.md), and [release validation](RELEASE_VALIDATION.md) for AURA setup, behavior, and recorded tests.

The initial audit was verified on 3 October 2026 on an Apple Silicon Mac (`arm64`). Its scope was to inspect the connected device and assess backup feasibility. Firmware replacement and compilation were deferred at that point, before the owner's subsequent authorization and AURA implementation.

The device discovery identified an **ESP32-S3, revision 0.2, with 8 MB embedded PSRAM (AP3v3)**. This identifies the chip family; the board model, flash configuration, pin assignments, peripherals, and firmware requirements still need to be established before choosing a firmware project or build configuration.

## Initial inspection-tool inventory

The initial audit checked normal shell PATH, Homebrew packages, standard application locations, and the usual `~/.espressif`, `~/esp`, `~/.platformio`, and Arduino data directories. A custom installation outside those locations may exist.

| Tool | Verified executable or location | Version / state |
| --- | --- | --- |
| Homebrew | `/opt/homebrew/bin/brew` | 7.0.7 |
| Default Python | `/opt/homebrew/bin/python3` | 3.14.7 |
| Default pip | `/opt/homebrew/bin/pip3` | 26.2.1 for Python 3.14 |
| Python.org Python 3.11 | `/usr/local/bin/python3.11` | 3.11.9; pip 25.3 |
| Python.org Python 3.13 | `/usr/local/bin/python3.13` | 3.13.9; pip 25.3 |
| Apple system Python | `/usr/bin/python3` | 3.9.6 |
| Git | `/usr/bin/git` | 2.54.0 (Apple Git-157) |
| Active Xcode developer directory | `/Applications/Xcode-beta.app/Contents/Developer` | Confirmed with `xcode-select -p` |
| Workspace Python | `/absolute/path/to/ESP32/.venv/bin/python` | 3.11.9 |
| Workspace esptool | `.venv`, Python package | 5.4.0 |
| Workspace pyserial | `.venv`, Python package | 3.5 |
| ESP-IDF / `idf.py` | Normal PATH and standard locations | Not found; not installed by this investigation |
| Espressif Installation Manager (`eim`) | Normal PATH | Not found |
| PlatformIO / `pio` | Normal PATH and standard locations | Not found |
| Arduino CLI / Arduino app | Normal PATH and app locations | Not found |
| CMake / Ninja | Normal PATH and Homebrew inventory | Not found |
| Espressif GCC toolchains | Normal PATH | `riscv32-esp-elf-gcc`, `xtensa-esp-elf-gcc`, and `xtensa-esp32-elf-gcc` not found |

Before the workspace environment was created, esptool, pyserial, and PlatformIO were absent from the checked Python 3.11, 3.13, and 3.14 environments. The inspection tools now live only in the workspace virtual environment.

## Reuse the existing environment

Run commands from the workspace root. Activation is optional when using the explicit interpreter path:

```sh
cd '/absolute/path/to/ESP32'
.venv/bin/python --version
.venv/bin/python -m esptool version
.venv/bin/python -m pip check
```

These version and dependency checks do not open a serial connection. Commands that access a serial port, enter the bootloader, or reset the board are separate device operations and are outside this setup check.

For an interactive terminal session, activate the environment with:

```sh
source .venv/bin/activate
```

Use `deactivate` when finished. No persistent shell configuration changes are needed.

## Reproduce the inspection tools

The full set of pinned package versions is in `requirements-tools.lock` at the workspace root. In a fresh checkout or directory without an existing `.venv`, use the verified Python 3.11 interpreter:

```sh
cd '/absolute/path/to/ESP32'
/usr/local/bin/python3.11 -m venv .venv
.venv/bin/python -m pip install --requirement requirements-tools.lock
.venv/bin/python -m pip check
.venv/bin/python -m esptool version
```

On another machine, substitute a verified Python 3.11 interpreter path. Keep the lock file with the project. It pins direct and transitive package versions; it does not pin the Python runtime or include package artifact hashes.

The current esptool documentation requires Python 3.10 or newer and recommends an isolated virtual environment. The existing Python.org 3.11.9 interpreter satisfies that requirement; the Apple system Python 3.9.6 does not. [Espressif: esptool installation and dependencies](https://docs.espressif.com/projects/esptool/en/latest/esp32/installation.html)

## Historical native ESP-IDF recommendation

Native ESP-IDF compilation was not performed during the initial investigation. No ESP-IDF SDK, compiler, CMake, or Ninja installation was added in that phase. This inspection `.venv` supplies device tools; AURA's later Arduino build dependencies are isolated under `.toolchains/` and documented in [FIRMWARE_BUILD.md](FIRMWARE_BUILD.md).

As checked on 3 October 2026, Espressif's stable getting-started documentation identifies **ESP-IDF v6.1**. For v6.0 and newer, its macOS guide recommends the **Espressif Installation Manager (EIM)**. This is the preferred starting point for a new native ESP-IDF setup after the device and application requirements are known. [Espressif: stable ESP-IDF getting started](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/get-started/index.html), [Espressif: ESP-IDF installation on macOS](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/get-started/macos-setup.html)

Before starting that phase:

1. Establish the exact board, flash parameters, peripheral wiring, intended application, and dependencies.
2. Select an ESP-IDF release compatible with those requirements and pin its exact release tag. Do not automatically migrate an existing firmware project to the newest SDK.
3. Install the selected release through EIM and preserve its generated `eim_config.toml` to reproduce the installation.
4. Use the SDK's managed Python environment and tool versions. Keep this standalone inspection `.venv` separate from the SDK environment.
5. Build a project for `esp32s3`, inspect the resulting flash layout and configuration, and validate it before considering any device write.

EIM supports explicit ESP-IDF version selection and reusable installation configuration. Espressif also advises updating esptool supplied by an SDK through that SDK rather than independently replacing it. [Espressif: macOS setup and version selection](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/get-started/macos-setup.html), [Espressif: updating esptool as part of a framework](https://docs.espressif.com/projects/esptool/en/latest/esp32/installation.html#as-a-part-of-sdk-framework)

No EIM installation or SDK installation commands have been executed or scheduled by this setup document.
