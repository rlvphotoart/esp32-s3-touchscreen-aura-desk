#!/usr/bin/env python3
"""Package AURA Desk from an explicit public allowlist, after release validation.

This command never opens the device or invokes a compiler. It refuses incomplete
release evidence and verifies the finished ZIP against the exact source bytes.
SHA-256 sums establish integrity; this package has no publisher signature.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path, PurePosixPath
import stat
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent.parent
VERSION = re.search(r'^#define AURA_VERSION "([0-9]+\.[0-9]+\.[0-9]+)"$', (ROOT/'firmware/AuraDesk/firmware_version.h').read_text(), re.M)[1]
RELEASE = f"releases/aura-desk-{VERSION}"
MANIFEST = f"{RELEASE}/release-manifest.json"
SUMS = f"{RELEASE}/SHA256SUMS"
FORBIDDEN = {"backups", "logs", ".toolchains", ".venv", "build", ".git", "__pycache__"}

REQUIRED = [
    ".gitignore", "README.md", "CHANGELOG.md", "ORIGINAL_CODE_RIGHTS.md", "requirements-tools.lock",
    "docs/AURA_DESK.md", "docs/FIRMWARE_BUILD.md", "docs/UI_QA.md",
    "docs/RELEASE_VALIDATION.md", "docs/TOOLCHAIN_LOCK.json", "docs/PUBLIC_API_CATALOG.json", "docs/PUBLIC_API_CATALOG.md", "docs/API_CATALOG_VALIDATION.md", "docs/API_CATALOG_VALIDATION.json",
    "firmware/ui_preview/render.cpp", "tools/render_ui.py",
    'third_party/licenses/Apache-2.0.txt',
    'third_party/licenses/ArduinoJson-MIT.txt',
    'third_party/licenses/CC0-1.0.txt',
    'third_party/licenses/Espressif-radio-binaries-LICENSE.txt',
    'third_party/licenses/FONT_PROVENANCE.json',
    'third_party/licenses/FontAwesome-5.9.0-LICENSE.txt',
    'third_party/licenses/FreeRTOS-MIT.txt',
    'third_party/licenses/GCC-GPL-3.0.txt',
    'third_party/licenses/GCC-Runtime-Exception-3.1.txt',
    'third_party/licenses/GPL-2.0.txt',
    'third_party/licenses/IDF-newlib-COPYING.txt',
    'third_party/licenses/LGPL-2.1.txt',
    'third_party/licenses/LVGL-MIT.txt',
    'third_party/licenses/Montserrat-7.200-OFL.txt',
    'third_party/licenses/PROVENANCE.json',
    'third_party/licenses/SIL-OFL-1.1.txt',
    'third_party/licenses/WPA-supplicant-COPYING.txt',
    'third_party/licenses/cJSON-MIT.txt',
    'third_party/licenses/esp-littlefs-MIT.txt',
    'third_party/licenses/http-parser-MIT.txt',
    'third_party/licenses/littlefs-BSD-3-Clause.txt',
    'third_party/licenses/lwIP-COPYING.txt',
    'third_party/licenses/mbedTLS-3.6.2-LICENSE.txt',
    'third_party/licenses/toolchain-newlib-COPYING.txt',

    *[f"{RELEASE}/{name}" for name in (
        "AuraDesk.ino.bin", "AuraDesk.ino.bootloader.bin", "AuraDesk.ino.partitions.bin",
        "AuraDesk.ino.merged.bin", "AuraDesk.ino.elf", "build-layout.json", "TOOLCHAIN_LOCK.json")],
    *[f"firmware/AuraDesk/{name}" for name in (
        "AuraDesk.ino", "firmware_version.h", "app_model.h", "app_service.cpp", "app_service.h",
        "esp_panel_board_supported_conf.h", "lv_conf.h", "lvgl_v8_port.cpp",
        "lvgl_v8_port.h", "partitions.csv", "ui.cpp", "ui.h", "web_service.cpp", "web_service.h")],
    *[f"scripts/{name}" for name in (
        "backup_flash.sh", "build.sh", "common.sh", "detect_device.sh", "flash.sh",
        "monitor.sh", "restore_original.sh", "verify_backup.sh")],
    *[f"tools/{name}" for name in (
        "aura_console.py", "backup_device.py", "capture_serial.py", "capture_release_screens.py", "device_inventory.py",
        "export_backup.py", "flash_aura.py", "read_efuses.py", "reset_and_capture.py",
        "restore_original.py", "screen_to_png.py", "test_aura_boot.py", "test_aura_network.py",
        "verify_backup.py", "verify_aura_ota.py", "upload_aura_update.py", "test_always_on.py", "test_navigation_device.py", "test_widgets.py", "test_widget_browser.py", "test_http_response_policy.py", "test_api_device.py", "test_api_catalog.py", "generate_api_catalog.py", "package_release.py", "vendor/gen_esp32part.py", "vendor/PROVENANCE.json")],
]
# Additional public reference documents are explicit, not a wildcard over docs/.
OPTIONAL = [
    f"{RELEASE}/AuraDesk.ino.map",
    *[f"docs/{name}" for name in (
        "BACKUP.md", "CAPABILITIES.md", "FLASH_LAYOUT.md", "GPIO_MAP.md", "HARDWARE.md",
        "ORIGINAL_FIRMWARE.md", "RECOVERY.md", "RESEARCH.md", "SECURITY.md", "SETUP.md",
        "TEST_PLAN.md", "DEVELOPMENT.md", "ENGINEERING_REPORT.md", "hardware_profile.json", "RELEASE_VALIDATION_1.0.0.md", "RELEASE_VALIDATION_1.0.0.json", "RELEASE_VALIDATION_1.0.1.md", "RELEASE_VALIDATION_1.0.1.json", "RELEASE_VALIDATION_1.0.2.md", "RELEASE_VALIDATION_1.0.2.json", "BROWSER_API_VALIDATION.md", "BROWSER_API_VALIDATION.json", "RELEASE_VALIDATION_1.0.3.md", "RELEASE_VALIDATION_1.0.3.json")],
    "artifacts/ui-preview/home_offline.png", "artifacts/ui-preview/weather_offline.png",
    "artifacts/ui-preview/tools_offline.png", "artifacts/ui-preview/settings_offline.png",
    "artifacts/ui-preview/settings_always_on_offline.png",
]
VALIDATION_JSON = (
    "docs/RELEASE_VALIDATION.json", "docs/release_validation.json",
    f"{RELEASE}/release-validation.json",
)
PRIVATE_KEYS = {
    "password", "pass", "passphrase", "psk", "secret", "token", "access_token",
    "refresh_token", "admincode", "admin_code", "pairingcode", "pairing_code",
    "privatekey", "private_key", "credential", "credentials", "ssid", "certificate",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def allowed(relative: str) -> Path:
    name = PurePosixPath(relative)
    if name.is_absolute() or ".." in name.parts or any(part in FORBIDDEN for part in name.parts):
        raise ValueError(f"Forbidden package path: {relative}")
    if any(part.startswith(".env") or part == ".DS_Store" for part in name.parts):
        raise ValueError(f"Private environment path refused: {relative}")
    if "_fixture" in name.name or "password" in name.name.lower() or "pairing" in name.name.lower():
        raise ValueError(f"Private or synthetic capture refused: {relative}")
    path = ROOT / relative
    if path.resolve().is_relative_to(ROOT.resolve()) is False:
        raise ValueError(f"Package path leaves workspace: {relative}")
    current = path
    while current != ROOT:
        if current.is_symlink():
            raise ValueError(f"Symlink refused: {relative}")
        current = current.parent
    return path


def sanitized_checks(value):
    """Retain validation conclusions without identity or authentication material."""
    if isinstance(value, dict):
        return {key: sanitized_checks(item) for key, item in value.items()
                if str(key).lower().replace("-", "_") not in PRIVATE_KEYS}
    if isinstance(value, list):
        return [sanitized_checks(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        if isinstance(value, str) and any(marker in value for marker in (
            "-----BEGIN PRIVATE KEY", "-----BEGIN RSA PRIVATE KEY", "-----BEGIN EC PRIVATE KEY",
            "-----BEGIN CERTIFICATE", "Bearer ")):
            raise ValueError("Validation checks contain authentication material; publish a conclusions-only JSON")
        return value
    raise ValueError("Unsupported validation JSON value")


def inputs() -> tuple[dict[str, bytes], dict]:
    missing = [name for name in REQUIRED if not allowed(name).is_file()]
    notices = next((name for name in ("THIRD_PARTY_NOTICES.md", "THIRD_PARTY_NOTICES")
                    if allowed(name).is_file()), None)
    if notices is None:
        missing.append("THIRD_PARTY_NOTICES.md or THIRD_PARTY_NOTICES")
    # Public previews contain only offline default states. Private device/pairing
    # captures stay outside the package; live conclusions are in validation JSON.
    if not allowed("artifacts/ui-preview/home_offline.png").is_file():
        missing.append("artifacts/ui-preview/home_offline.png")
    if missing:
        raise ValueError("Release is incomplete; missing: " + ", ".join(missing))
    names = set(REQUIRED + [notices])
    names.update(name for name in OPTIONAL if allowed(name).is_file())
    payload = {name: allowed(name).read_bytes() for name in sorted(names)}
    for name in names:
        if name.endswith(".png") and not payload[name].startswith(b"\x89PNG\r\n\x1a\n"):
            raise ValueError(f"Invalid PNG device capture: {name}")
    validation = {
        "report": "docs/RELEASE_VALIDATION.md",
        "report_sha256": digest(payload["docs/RELEASE_VALIDATION.md"]),
        "checks": None,
    }
    evidence = next((name for name in VALIDATION_JSON if allowed(name).is_file()), None)
    if evidence:
        raw = json.loads(allowed(evidence).read_text(encoding="utf-8"))
        checks = raw.get("checks", raw.get("results", {})) if isinstance(raw, dict) else raw
        validation["checks"] = sanitized_checks(checks)
        validation["check_source"] = evidence
        validation["check_source_sha256"] = digest(allowed(evidence).read_bytes())
        if sanitized_checks(raw)!=raw:
            raise ValueError("Validation JSON contains private fields; provide a public conclusions-only record")
        payload[evidence]=allowed(evidence).read_bytes()
    layout = json.loads(payload[f"{RELEASE}/build-layout.json"])
    merged_name = f"{RELEASE}/AuraDesk.ino.merged.bin"
    merged = payload[merged_name]
    if len(merged) != 16 * 1024 * 1024 or layout.get("chip") != "esp32s3":
        raise ValueError("Release is not the expected ESP32-S3 / 16 MiB image")
    for region in layout["regions"]:
        name = f"{RELEASE}/{region['file']}"
        if name not in payload:
            raise ValueError(f"Unlisted firmware region: {name}")
        data = payload[name]
        offset = int(region["offset"], 0) if isinstance(region["offset"], str) else region["offset"]
        if len(data) != region["bytes"] or digest(data) != region["sha256"]:
            raise ValueError(f"Firmware differs from build-layout: {name}")
        if offset < 0 or merged[offset:offset + len(data)] != data:
            raise ValueError(f"Merged image differs at region: {name}")
    record = layout["merged_image"]
    if record["file"] != Path(merged_name).name or len(merged) != record["bytes"] or digest(merged) != record["sha256"]:
        raise ValueError("Merged image hash/length does not match build-layout")
    # A source edit after the exported application demands a new target build.
    application_mtime = allowed(f"{RELEASE}/AuraDesk.ino.bin").stat().st_mtime_ns
    if any(allowed(name).stat().st_mtime_ns > application_mtime
           for name in names if name.startswith("firmware/AuraDesk/")):
        raise ValueError("Firmware source is newer than the exported application; rebuild before packaging")
    return payload, validation


def verify_archive(path: Path, payload: dict[str, bytes], manifest: dict) -> None:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != set(payload):
            raise ValueError("Archive contains duplicate, missing or unexpected members")
        if archive.testzip() is not None:
            raise ValueError("Archive CRC verification failed")
        for name in names:
            allowed(name)
            if archive.read(name) != payload[name]:
                raise ValueError(f"Archive byte verification failed: {name}")
        for record in manifest["files"]:
            data = archive.read(record["path"])
            if len(data) != record["bytes"] or digest(data) != record["sha256"]:
                raise ValueError(f"Archive manifest verification failed: {record['path']}")
        for name, expected in manifest["source_sha256"].items():
            if digest(archive.read(name)) != expected:
                raise ValueError(f"Archive source hash failed: {name}")
        for line in archive.read(SUMS).decode("utf-8").splitlines():
            expected, name = line.split("  ", 1)
            if digest(archive.read(name)) != expected:
                raise ValueError(f"Archive SHA256SUMS verification failed: {name}")


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".pending", dir=path.parent)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def package(output: Path) -> dict:
    payload, validation = inputs()
    manifest = {
        "schema_version": 1, "product": "AURA Desk", "interface": "Horizon",
        "version": VERSION, "release_date": "2026-10-03",
        "board": "Jingcai / Guition ESP32-4848S040C_I_Y_3", "target": "esp32s3",
        "flash_size_bytes": 16 * 1024 * 1024,
        "application_sha256": digest(payload[f"{RELEASE}/AuraDesk.ino.bin"]),
        "merged_sha256": digest(payload[f"{RELEASE}/AuraDesk.ino.merged.bin"]),
        "files": [{"path": name, "bytes": len(data), "sha256": digest(data)} for name, data in payload.items()],
        "source_sha256": {name: digest(data) for name, data in payload.items()
                          if name.startswith(("firmware/", "scripts/", "tools/"))},
        "validation": validation,
        "publisher_signature": {"signed": False, "note": "SHA-256 hashes verify integrity; they are not publisher signatures."},
        "privacy": "Owner backups, logs, credentials, toolchains, environments and pairing/credential captures are excluded.",
        "generated_files": [MANIFEST, SUMS],
    }
    original = dict(payload)
    manifest_data = (json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    payload[MANIFEST] = manifest_data
    sums_data = "".join(f"{digest(data)}  {name}\n" for name, data in sorted(payload.items())).encode("utf-8")
    payload[SUMS] = sums_data
    output.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=output.name + ".", suffix=".pending", dir=output.parent)
    os.close(handle)
    staged = Path(temporary)
    try:
        with zipfile.ZipFile(staged, "w", zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=True) as archive:
            for name, data in sorted(payload.items()):
                info = zipfile.ZipInfo(name, date_time=(2026, 10, 3, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                executable = name.endswith(".sh") or (name in original and allowed(name).stat().st_mode & stat.S_IXUSR)
                info.external_attr = ((stat.S_IFREG | (0o755 if executable else 0o644)) << 16)
                archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        verify_archive(staged, payload, manifest)
        for name, data in original.items():
            if allowed(name).read_bytes() != data:
                raise ValueError(f"Source changed while packaging: {name}")
        atomic_write(allowed(MANIFEST), manifest_data)
        atomic_write(allowed(SUMS), sums_data)
        os.replace(staged, output)
        archive_sha = digest(output.read_bytes())
        atomic_write(Path(str(output) + ".sha256"), f"{archive_sha}  {output.name}\n".encode("utf-8"))
        return {"archive": str(output), "sha256": archive_sha, "members": len(payload),
                "application_sha256": manifest["application_sha256"], "merged_sha256": manifest["merged_sha256"],
                "byte_verification": "passed", "manifest_verification": "passed", "private_path_check": "passed"}
    finally:
        staged.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / f"releases/AURA-Desk-{VERSION}.zip")
    args = parser.parse_args()
    try:
        print(json.dumps(package(args.output.resolve()), indent=2))
    except (OSError, ValueError, KeyError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        parser.exit(1, f"Package refused: {exc}\n")


if __name__ == "__main__":
    main()
