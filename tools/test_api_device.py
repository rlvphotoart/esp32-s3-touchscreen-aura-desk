#!/usr/bin/env python3
"""Read-only verification of both configured API readings on real LCD frames.

The identity-checked ROM connection and firmware console share one UART handle.
Only a volatile RAM reader is loaded; flash, eFuses and settings are not written.
Pairing, addresses, configuration, raw frames and OCR results stay in RAM except
for a temporary 0600 PNG/source that macOS Vision deletes. Reports contain fixed
descriptions, booleans and numeric diagnostics. Physical touch is not simulated.
Requires AURA_EXPECTED_MAC to contain the operator's verified device identity.
"""
import argparse
import contextlib
import io
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import time
import unicodedata
from pathlib import Path

from backup_device import connect, require_expected_mac
from test_always_on import CRASH_MARKERS, uart_status, wait_uart
from test_aura_network import CheckFailure, private_pairing_ocr, read_uart, require, screen_png
from test_navigation_device import navigate_serial, pair_in_memory, read_only_json


OCR_REGIONS_SWIFT = r'''import Foundation
import AppKit
import Vision
guard CommandLine.arguments.count == 3,
      let image = NSImage(contentsOfFile: CommandLine.arguments[1]),
      let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil),
      let page = Int(CommandLine.arguments[2]) else { exit(2) }
let rects: [(Double, Double, Double, Double)] = page == 0
  ? [(20,364,214,48),(246,364,214,48)]
  : [(20,111,440,132),(20,257,440,132)]
var groups: [[String]] = []
do {
  for (x,y,w,h) in rects {
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = false
    request.recognitionLanguages = ["en-US"]
    request.regionOfInterest = CGRect(x:x/480,y:(480-y-h)/480,width:w/480,height:h/480)
    try VNImageRequestHandler(cgImage:cg).perform([request])
    groups.append((request.results ?? []).compactMap { $0.topCandidates(1).first?.string })
  }
  FileHandle.standardOutput.write(try JSONSerialization.data(withJSONObject:groups))
} catch { exit(3) }
'''


def private_regions_ocr(png, page):
    require(sys.platform == "darwin" and page in (0, 13), "Regional private OCR requires macOS and a supported data page")
    with tempfile.TemporaryDirectory(prefix="aura-private-api-") as directory:
        os.chmod(directory, 0o700)
        image = Path(directory) / "frame.png"
        source = Path(directory) / "recognize.swift"
        for path, data in ((image, png), (source, OCR_REGIONS_SWIFT.encode())):
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
        try:
            completed = subprocess.run(["xcrun", "swift", str(source), str(image), str(page)],
                                       capture_output=True, timeout=120, check=False)
            require(completed.returncode == 0, "Regional macOS Vision OCR did not complete")
            groups = json.loads(completed.stdout)
            require(isinstance(groups, list) and len(groups) == 2
                    and all(isinstance(group, list) and all(isinstance(line, str) for line in group) for group in groups),
                    "Regional OCR returned an unsupported shape")
            return groups
        finally:
            image.unlink(missing_ok=True)


def normalized(value):
    return "".join(char for char in unicodedata.normalize("NFKC", value).casefold()
                   if not char.isspace())


def home_value(value):
    """Mirror only the documented Home presentation, not provider selection."""
    if len(value.encode()) > 12 and any(char in value for char in ".eE"):
        try:
            number = float(value)
        except ValueError:
            return value
        if math.isfinite(number):
            return format(number, ".2f" if 1 <= abs(number) < 100000000 else ".5g")
    return value


def display_preserved(status, expected_brightness):
    require(status.get("alwaysOnDisplay") is True and status.get("brightness") == expected_brightness,
            "Selected always-on mode or brightness differs from the verification baseline")


def status_checked(client, version, brightness, summary):
    code, status = read_only_json(client, "/api/status", summary)
    require(code == 200 and status.get("firmware") == "AURA Desk " + version,
            "Authenticated device status does not match the expected firmware")
    require("adminCode" not in status and "password" not in status,
            "Authenticated device status unexpectedly contains sensitive fields")
    display_preserved(status, brightness)
    return status


def two_live_widgets(status, require_fresh=False):
    widgets = status.get("widgets")
    configs = status.get("widgetConfig")
    require(isinstance(widgets, list) and len(widgets) == 2 and isinstance(configs, list) and len(configs) == 2,
            "Both saved widget configurations are unavailable")
    for widget, config in zip(widgets, configs):
        require(isinstance(widget, dict) and isinstance(config, dict) and config.get("enabled") is True
                and widget.get("enabled") is True, "Both API widgets must already be saved and enabled")
        require(isinstance(config.get("url"), str) and config["url"].startswith("https://")
                and isinstance(config.get("field"), str) and config["field"],
                "Saved public widget address or field is unavailable")
        require(widget.get("valid") is True and widget.get("fetching") is False
                and type(widget.get("ageMinutes")) is int
                and widget["ageMinutes"] >= 0,
                "A widget has no verified public API reading with a completed update and known age")
        if require_fresh:
            require(not widget.get("error") and widget.get("httpStatus") == 200,
                    "A widget's latest refresh did not complete successfully")
        require(all(isinstance(widget.get(key), str) for key in ("label", "value", "unit"))
                and widget["label"] and widget["value"], "A widget display label or scalar value is unavailable")
    return widgets


def region_matches(lines, widget, page):
    label = normalized(widget["label"])
    value = home_value(widget["value"]) if page == 0 else widget["value"]
    combined = value + (" " + widget["unit"] if widget["unit"] else "")
    normalized_lines = [normalized(line) for line in lines]
    # Each OCR group is bounded to its own widget card, so a matching value from
    # the other slot cannot satisfy this check. Require the value+unit in one
    # recognized line; age numbers elsewhere cannot masquerade as the reading.
    pattern = r"(?<![\w.+-])" + re.escape(normalized(combined)) + r"(?![\w.+-])"
    return any(label in line for line in normalized_lines) and any(re.search(pattern, line) is not None for line in normalized_lines)


def self_test():
    fixture = {"label": "Price fixture", "value": "123456.78901234", "unit": "USD"}
    require(home_value(fixture["value"]) == "123456.79", "Home numeric compaction self-test failed")
    require(region_matches(["Price fixture", "123456.79 USD"], fixture, 0), "Home reading matching self-test failed")
    require(region_matches(["Price fixture", "123456.78901234 USD"], fixture, 13), "Details scalar matching self-test failed")
    require(not region_matches(["Price fixture", "123456.78 USD"], fixture, 0), "OCR matcher accepted the wrong reading")
    require(not region_matches(["Another widget", "123456.79 USD"], fixture, 0), "OCR matcher accepted the wrong label")
    zero = {"label": "Humidity", "value": "0", "unit": "%"}
    require(region_matches(["Humidity", "0 %", "Updated 1 min ago"], zero, 0), "Numeric zero was incorrectly treated as empty")
    require(not region_matches(["Humidity", "50 %", "Updated 0 min ago"], zero, 0), "Age digits were mistaken for a reading")
    print(json.dumps({"event": "offline_api_matching_self_test_passed"}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port")
    parser.add_argument("--expected-version", default="1.0.3")
    parser.add_argument("--expected-brightness", type=int, default=80)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--require-fresh", action="store_true", help="Require both latest refreshes to have no error and HTTP 200")
    parser.add_argument("--pairing-preview", type=Path,
                        help="Optional temporary 0600 pairing PNG in a 0700 directory outside the repository; operator deletes after use")
    parser.add_argument("--home-preview", type=Path,
                        help="Optional checked Home PNG in a 0700 directory outside the repository; operator deletes or explicitly shares")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if not args.port:
        parser.error("--port is required for actual device verification")
    if not 60 <= args.timeout <= 600 or not 10 <= args.expected_brightness <= 100:
        parser.error("timeout must be 60..600 seconds and brightness 10..100")
    if not re.fullmatch(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", args.expected_version):
        parser.error("expected version must be three dotted numbers")
    if args.summary and args.summary.exists():
        parser.error("summary output already exists")
    for requested_preview in (args.pairing_preview, args.home_preview):
        if requested_preview is None:
            continue
        preview = requested_preview.resolve()
        root = Path(__file__).resolve().parents[1]
        if preview == root or root in preview.parents or preview.exists() or preview.is_symlink():
            parser.error("preview must be a fresh file outside the repository")
        if not preview.parent.is_dir() or preview.parent.stat().st_mode & 0o077:
            parser.error("preview directory must already exist with owner-only permissions")
    if args.pairing_preview and args.home_preview and args.pairing_preview.resolve() == args.home_preview.resolve():
        parser.error("pairing and Home previews require different paths")
    summary = {"product": "AURA Desk", "firmware": args.expected_version, "passed": False,
               "read_only_transport_retries": 0, "settings_writes": False,
               "flash_writes": False, "efuse_writes": False, "physical_touch_tested": False,
               "latest_refresh_success_required": args.require_fresh,
               "checks": []}
    stage = "verify_identity"
    port = None
    failure = None

    def progress(name):
        nonlocal stage
        stage = name
        print(json.dumps({"stage": name}), flush=True)

    try:
        require_expected_mac()
        progress("verify_rom_identity_and_reset")
        # Keep chip/MAC/security/ROM diagnostics private. connect() validates the
        # operator's identity, chip, JEDEC flash and security before RAM reader.
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            esp, _ = connect(args.port, 115200)
            port = esp._port
            port.exclusive = True
            port.timeout = .2
            port.dtr = False
            port.rts = False
            esp.hard_reset()
            port.dtr = False
            port.rts = False
        summary["identity_verified"] = True
        progress("verify_healthy_firmware_startup")
        boot = read_uart(port, 9, maximum=131072)
        require(b"AURA_READY" in boot and b"AURA_HEALTH startup=passed" in boot
                and not any(marker in boot for marker in CRASH_MARKERS),
                "Expected firmware did not pass display/startup health")
        # Bound the wait for router connection and the operator-supplied
        # display baseline; a different saved brightness must not be accepted.
        initial = wait_uart(port, lambda item: item.get("wifi") == 1
                            and item.get("always_on") == 1
                            and item.get("backlight") == args.expected_brightness,
                            args.timeout, args.expected_version)
        require(initial["always_on"] == 1 and initial["backlight"] == args.expected_brightness,
                "Initial applied display mode differs from the expected baseline")
        summary["checks"].append("ROM identity, physical PSRAM, firmware version and healthy display startup")
        progress("capture_private_pairing_screen")
        pairing_png = screen_png(port)
        if args.pairing_preview:
            fd = os.open(args.pairing_preview, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "wb") as stream:
                stream.write(pairing_png)
            summary["temporary_pairing_preview_written"] = True
        address, code = private_pairing_ocr(pairing_png)
        pairing_png = None
        progress("pair_pinned_local_https")
        client = pair_in_memory(address, code, args.timeout)
        address = code = ""
        progress("wait_for_both_saved_live_api_readings")
        deadline = time.monotonic() + args.timeout
        while True:
            status = status_checked(client, args.expected_version, args.expected_brightness, summary)
            if (isinstance(status.get("widgets"), list) and len(status["widgets"]) == 2
                    and all(widget.get("valid") is True and widget.get("fetching") is False
                            and (not args.require_fresh or (not widget.get("error") and widget.get("httpStatus") == 200))
                            for widget in status["widgets"])):
                two_live_widgets(status, args.require_fresh)
                break
            require(time.monotonic() < deadline, "Both saved widgets did not produce successful live API readings")
            time.sleep(2)
        original_configs = status["widgetConfig"]
        summary["checks"].append("Both existing enabled widgets have verified public API readings with known age and recorded refresh state")

        for page, name in ((0, "home"), (13, "api_details")):
            progress("capture_checked_" + name + "_framebuffer")
            before = status_checked(client, args.expected_version, args.expected_brightness, summary)
            before_widgets = two_live_widgets(before, args.require_fresh)
            frame = screen_png(port, page=page)
            if page == 0 and args.home_preview:
                fd = os.open(args.home_preview, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                with os.fdopen(fd, "wb") as stream:
                    stream.write(frame)
                summary["checked_home_preview_written"] = True
            progress("private_regional_ocr_" + name)
            groups = private_regions_ocr(frame, page)
            frame = None
            after = status_checked(client, args.expected_version, args.expected_brightness, summary)
            after_widgets = two_live_widgets(after, args.require_fresh)
            require(before["widgetConfig"] == original_configs and after["widgetConfig"] == original_configs,
                    "Saved widget configuration changed during screen verification")
            for slot in range(2):
                require(region_matches(groups[slot], before_widgets[slot], page)
                        or region_matches(groups[slot], after_widgets[slot], page),
                        "A widget label/current reading/unit could not be confirmed in its own framebuffer region")
            summary[name + "_both_labels_values_units_verified"] = True
            summary["checks"].append("Checked " + name + " framebuffer independently matches both configured labels, values and units")
        progress("verify_preserved_display_settings_and_home")
        final = status_checked(client, args.expected_version, args.expected_brightness, summary)
        require(final["widgetConfig"] == original_configs, "Saved widget settings changed after page navigation")
        last_uart = wait_uart(port, lambda item: item.get("always_on") == 1
                              and item.get("backlight") == args.expected_brightness,
                              30, args.expected_version)
        require(last_uart is not None and last_uart.get("version") == args.expected_version
                and last_uart.get("always_on") == 1 and last_uart.get("backlight") == args.expected_brightness,
                "Applied display settings changed during API screen navigation")
        summary["selected_brightness"] = args.expected_brightness
        summary["always_on_preserved"] = True
        summary["brightness_preserved"] = True
        summary["widget_refresh_states"] = [
            {"slot": slot, "verified_reading_valid": widget.get("valid") is True,
             "latest_refresh_http_status": widget.get("httpStatus"),
             "latest_refresh_error_present": bool(widget.get("error")),
             "reading_age_minutes": widget.get("ageMinutes")}
            for slot, widget in enumerate(two_live_widgets(final, args.require_fresh))
        ]
        summary["checks"].append("API configuration, always-on mode and selected/applied brightness remain unchanged")
        summary["passed"] = True
    except CheckFailure as error:
        failure = str(error)
        summary["failure_stage"] = stage
        summary["exception_type"] = type(error).__name__
    except Exception as error:
        failure = "Device API verification encountered an identity, transport, OCR or device error"
        summary["failure_stage"] = stage
        summary["exception_type"] = type(error).__name__
    finally:
        if port is not None and port.is_open:
            try:
                navigate_serial(port, 0)
                summary["home_navigation_command_sent"] = True
            except Exception as error:
                summary["home_navigation_command_sent"] = False
                summary["cleanup_exception_type"] = type(error).__name__
                if failure is None:
                    failure = "Final Home navigation could not be confirmed"
                    summary["failure_stage"] = "cleanup_home"
                    summary["exception_type"] = type(error).__name__
            port.close()
        if failure:
            summary["passed"] = False
            summary["failure"] = failure
        if args.summary:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(args.summary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "w") as stream:
                json.dump(summary, stream, indent=2)
                stream.write("\n")
        print(json.dumps(summary, separators=(",", ":")), flush=True)
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
