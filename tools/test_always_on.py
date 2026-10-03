#!/usr/bin/env python3
"""Verify persistent display policy and the actual three-minute idle threshold.

Run explicitly against an installed AURA Desk display-policy firmware. One exclusive UART
session is used throughout. Pairing screenshots, local addresses, codes, TLS
pins, cookies and response bodies stay private; only checked numeric display
state is emitted. Reboots use the normal application command and preserve
flash/settings. The device is left on Home with always-on enabled and its
original brightness. --idle-only skips reboot persistence checks while retaining
the actual inactivity/backlight checks. --self-test checks parser boundaries
without hardware.
"""
import argparse
import http.client
import json
import os
import re
import ssl
import time
from pathlib import Path

import serial

from test_aura_network import (
    CheckFailure, PinnedLocal, export_has_secrets, private_pairing_ocr,
    read_uart, require, screen_png,
)


NUMERIC_FIELDS = {
    "uptime", "heap", "min_heap", "psram", "wifi", "internet", "time",
    "weather", "air", "rates", "board", "always_on", "backlight",
    "idle_ms", "dimmed",
}
DISPLAY_FIELDS = {"always_on", "backlight", "idle_ms", "dimmed"}
CRASH_MARKERS = (b"Guru Meditation", b"Backtrace:", b"PANIC", b"Brownout", b"AURA_FATAL")
IDLE_THRESHOLD_MS = 180000


def parse_uart_status(raw):
    """Return a strict non-secret whitelist from the last complete status line."""
    matches = list(re.finditer(rb"(?m)^AURA_STATUS ([^\r\n]*)\r?\n", raw))
    if not matches:
        return None
    result = {}
    for field in matches[-1][1].split():
        name, separator, value = field.partition(b"=")
        if not separator:
            continue
        try:
            key = name.decode("ascii")
        except UnicodeDecodeError:
            continue
        if key not in NUMERIC_FIELDS and key != "version":
            continue
        require(key not in result, "UART status contains duplicate checked fields")
        if key == "version":
            require(re.fullmatch(rb"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", value) is not None,
                    "UART firmware version has an unsupported form")
            result[key] = value.decode("ascii")
        else:
            require(re.fullmatch(rb"[0-9]{1,10}", value) is not None,
                    "UART status contains an invalid checked number")
            number = int(value)
            require(number <= 0xFFFFFFFF, "UART checked number exceeds its range")
            result[key] = number
    return result


def uart_status(port):
    port.reset_input_buffer()
    port.write(b"status\n")
    raw = bytearray()
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        block = port.read(max(1, min(port.in_waiting, 4096)))
        if block:
            raw.extend(block)
            require(len(raw) <= 16384, "UART status response exceeded its bound")
            require(not any(marker in raw for marker in CRASH_MARKERS), "Device reported a crash marker")
            value = parse_uart_status(raw)
            if value is not None:
                return value
    return None


def require_display_status(value, expected_version):
    require(value is not None and value.get("version") == expected_version,
            "Expected display-policy firmware is not running")
    require(DISPLAY_FIELDS <= value.keys(), "UART display diagnostics are incomplete")
    require(value["always_on"] in (0, 1) and value["dimmed"] in (0, 1),
            "Display policy flags have an unsupported value")
    require(10 <= value["backlight"] <= 100, "Applied backlight is outside its supported range")
    require(value.get("board") == 1 and value.get("psram", 0) >= 8 * 1024 * 1024,
            "Device display or physical memory health failed")


def emit(event, status=None, **numbers):
    record = {"event": event}
    if status is not None:
        record.update({key: status[key] for key in ("always_on", "backlight", "idle_ms", "dimmed", "uptime") if key in status})
    record.update(numbers)
    print(json.dumps(record, separators=(",", ":")), flush=True)


def wait_uart(port, predicate, seconds, expected_version):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        value = uart_status(port)
        if value is not None:
            require_display_status(value, expected_version)
            if predicate(value):
                return value
        time.sleep(1)
    raise CheckFailure("Timed out waiting for checked display state")


def pair_private(port, timeout, expected_version, previous_pin=None, on_stage=None):
    def step(name):
        if on_stage is not None:
            on_stage(name)

    step("wait_router")
    wait_uart(port, lambda value: value.get("wifi") == 1, timeout, expected_version)
    step("capture_private_screen")
    png = screen_png(port)
    step("private_ocr")
    address, code = private_pairing_ocr(png)
    png = None
    client = PinnedLocal(address)
    if previous_pin is not None:
        client.pin = previous_pin
    # Association is observable before the HTTPS server finishes restarting.
    # Retry transport failures with this same RAM-only address/code and pin;
    # certificate, authorization and checked protocol failures remain fatal.
    step("https_pair")
    deadline = time.monotonic() + min(timeout, 90)
    attempt = 0
    while time.monotonic() < deadline:
        attempt += 1
        try:
            status, response = client.json("/api/pair", method="POST", data={"code": code},
                                           unauthenticated=True,
                                           timeout=min(12, max(1, deadline-time.monotonic())))
        except ssl.SSLCertVerificationError:
            raise
        except (OSError, ssl.SSLError, http.client.HTTPException) as error:
            emit("private_pairing_transport_retry", attempt=attempt,
                 exception_type=type(error).__name__)
            if time.monotonic() >= deadline:
                raise
            time.sleep(min(2, max(0, deadline-time.monotonic())))
            continue
        require(status == 200 and response.get("paired") is True and isinstance(response.get("csrf"), str),
                "Private local browser pairing failed")
        code = ""
        client.csrf = response["csrf"]
        return client
    raise CheckFailure("Local HTTPS pairing did not become available within its deadline")


def display_http(client, expected, brightness, expected_version):
    code, value = client.json("/api/status")
    require(code == 200, "Authenticated display status is unavailable")
    require(value.get("firmware") == "AURA Desk " + expected_version,
            "HTTPS status reports an unexpected firmware version")
    require(type(value.get("alwaysOnDisplay")) is bool,
            "HTTPS status lacks a boolean always-on setting")
    require(value["alwaysOnDisplay"] is expected and value.get("brightness") == brightness,
            "HTTPS display settings have not round-tripped")
    code, exported = client.json("/api/export")
    require(code == 200 and not export_has_secrets(exported),
            "Settings export failed or contains sensitive fields")
    require(type(exported.get("alwaysOnDisplay")) is bool and exported["alwaysOnDisplay"] is expected
            and exported.get("brightness") == brightness,
            "Exported display policy differs from checked status")


def set_policy(client, port, enabled, brightness, expected_version):
    code, response = client.json("/api/settings", method="POST", data={"alwaysOnDisplay": enabled})
    require(code == 202 and response.get("accepted") is True, "Display-only settings were not accepted")
    value = wait_uart(port, lambda item: item["always_on"] == int(enabled), 60, expected_version)
    display_http(client, enabled, brightness, expected_version)
    return value


def wait_before_reboot(client, port, timeout):
    # The public-source worker owns NVS and may be inside a bounded HTTPS fetch.
    # Await its next quiet interval, then allow at least five seconds. The normal
    # reboot command also follows the policy write in the same ordered queue.
    deadline = time.monotonic() + timeout
    quiet_since = None
    while time.monotonic() < deadline:
        code, value = client.json("/api/status")
        require(code == 200, "Status became unavailable before the persistence check")
        now = time.monotonic()
        if value.get("fetching") is False:
            if quiet_since is None:
                quiet_since = now
            if now - quiet_since >= 5:
                return
        else:
            quiet_since = None
        if port.in_waiting:
            port.read(min(port.in_waiting, 16384))
        time.sleep(1)
    raise CheckFailure("Device service did not reach a quiet interval for persistence verification")


def reboot_healthy(port, expected_policy, expected_version, timeout):
    # Reboot follows SetAlwaysOn in the service command queue, so its NVS write
    # completes before restart even when a public data request is in progress.
    port.reset_input_buffer()
    port.write(b"reboot:confirm\n")
    raw = bytearray()
    deadline = time.monotonic() + min(timeout, 120)
    while time.monotonic() < deadline:
        block = port.read(max(1, min(port.in_waiting, 4096)))
        if block:
            raw.extend(block)
            require(len(raw) <= 131072, "Restart output exceeded its bounded size")
            require(not any(marker in raw for marker in CRASH_MARKERS), "Display-policy restart reported a crash marker")
            if b"AURA_READY" in raw and b"AURA_HEALTH startup=passed" in raw:
                value = wait_uart(port, lambda item: item["always_on"] == int(expected_policy), 15, expected_version)
                require(raw.count(b"ESP-ROM:esp32s3-20210327") == 1, "Expected one healthy application restart")
                return value
    raise CheckFailure("Display-policy restart did not pass startup health")


def self_test():
    checked = parse_uart_status(b"noise\nAURA_STATUS version=1.0.1 always_on=1 backlight=80 idle_ms=180005 dimmed=0 board=1 psram=8388608 password=secret ip=192.0.2.8\n")
    require(checked == {"version": "1.0.1", "always_on": 1, "backlight": 80, "idle_ms": 180005, "dimmed": 0, "board": 1, "psram": 8388608},
            "Parser whitelist self-test failed")
    require(parse_uart_status(b"AURA_STATUS version=1.0.1 always_on=1") is None,
            "Parser accepted a truncated frame")
    require(parse_uart_status(b"AURA_STATUS always_on=0\nAURA_STATUS always_on=1\n")["always_on"] == 1,
            "Parser did not select the last complete frame")
    for raw in (b"AURA_STATUS always_on=0 always_on=1\n", b"AURA_STATUS backlight=-1\n",
                b"AURA_STATUS idle_ms=4294967296\n", b"AURA_STATUS version=1.0.1extra\n"):
        try:
            parse_uart_status(raw)
        except CheckFailure:
            continue
        raise CheckFailure("Parser accepted malformed checked status")
    emit("parser_self_test_passed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port")
    parser.add_argument("--timeout", type=int, default=240, help="Router/idle deadlines in seconds, 200..600")
    parser.add_argument("--expected-version", default="1.0.3")
    parser.add_argument("--summary", type=Path, help="Optional non-secret result JSON; must not exist")
    parser.add_argument("--idle-only", action="store_true",
                        help="Skip reboot persistence phases; verify real inactivity and both backlight modes")
    parser.add_argument("--self-test", action="store_true", help="Run parser checks without opening hardware")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if not args.port:
        parser.error("--port is required for device checks")
    if not 200 <= args.timeout <= 600:
        parser.error("timeout must be 200..600 seconds")
    if re.fullmatch(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", args.expected_version) is None:
        parser.error("expected firmware version must be three dotted numbers")
    if args.summary and args.summary.exists():
        parser.error("summary output already exists")
    summary = {"product": "AURA Desk", "firmware": args.expected_version, "passed": False,
               "idle_threshold_ms": IDLE_THRESHOLD_MS, "checks": [], "device_states": {},
               "mode": "idle-only" if args.idle_only else "full",
               "persistence_reboots_skipped": args.idle_only,
               "skipped_checks": (["Automatic dim policy persists across reboot",
                                    "Always-on policy persists across reboot"] if args.idle_only else [])}
    port = serial.Serial(port=None, baudrate=115200, timeout=.2, exclusive=True)
    port.dtr = False
    port.rts = False
    port.port = args.port
    client = None
    brightness = None
    original_brightness = None
    failure = None
    failure_type = None
    failure_stage = None
    stage = "open_uart"

    def set_stage(name):
        nonlocal stage
        stage = name
        emit("validation_stage", stage=name)

    def pair_at(name, pin=None):
        return pair_private(port, args.timeout, args.expected_version, pin,
                            on_stage=lambda step: set_stage(name + "/" + step))

    try:
        set_stage("open_uart")
        port.open()
        set_stage("initial_startup")
        startup = read_uart(port, 9, maximum=131072)
        require(not any(marker in startup for marker in CRASH_MARKERS), "Initial startup reported a crash marker")
        set_stage("initial_router")
        wait_uart(port, lambda item: item.get("wifi") == 1, args.timeout, args.expected_version)
        emit("private_pairing_started")
        client = pair_at("initial_pairing")
        set_stage("read_original_display_settings")
        code, current = client.json("/api/status")
        require(code == 200 and isinstance(current.get("brightness"), int) and 10 <= current["brightness"] <= 100,
                "Original display brightness is unavailable")
        original_brightness = current["brightness"]
        brightness = 20 if original_brightness == 10 else original_brightness
        require(type(current.get("alwaysOnDisplay")) is bool, "Always-on setting is unavailable")
        summary["original_brightness"] = original_brightness
        summary["test_brightness"] = brightness
        if brightness != original_brightness:
            set_stage("temporary_test_brightness")
            # At the 10% minimum, automatic dim has no lower physical level.
            # Temporarily use 20% to exercise both paths and restore 10% below.
            code, reply = client.json("/api/settings", method="POST", data={"brightness": brightness})
            require(code == 202 and reply.get("accepted") is True,
                    "Temporary display test brightness was not accepted")
            deadline = time.monotonic() + 60
            while time.monotonic() < deadline:
                code, adjusted = client.json("/api/status")
                if code == 200 and adjusted.get("brightness") == brightness:
                    break
                time.sleep(1)
            else:
                raise CheckFailure("Temporary display test brightness was not applied")
            emit("temporary_brightness_above_dim_floor", test_brightness=brightness,
                 original_brightness=original_brightness)

        # Reject a string before changing policy; a typed boolean is part of the
        # browser/API contract rather than relying on permissive JSON coercion.
        set_stage("reject_non_boolean_setting")
        code, _ = client.json("/api/settings", method="POST", data={"alwaysOnDisplay": "true"})
        require(code == 400, "Display settings accepted a non-boolean always-on value")
        summary["checks"].append("Settings reject non-boolean display policy")

        if not args.idle_only:
            set_stage("set_automatic_dim")
            set_policy(client, port, False, brightness, args.expected_version)
            set_stage("wait_automatic_dim_persistence")
            wait_before_reboot(client, port, args.timeout)
            set_stage("reboot_automatic_dim")
            value = reboot_healthy(port, False, args.expected_version, args.timeout)
            emit("automatic_dim_policy_survived_restart", value)
            pin = client.pin
            client = None
            client = pair_at("pair_after_automatic_dim_reboot", pin)
            set_stage("check_automatic_dim_export_after_reboot")
            display_http(client, False, brightness, args.expected_version)
            summary["checks"].append("Automatic dim setting persists across healthy restart and settings export")

            set_stage("set_always_on")
            set_policy(client, port, True, brightness, args.expected_version)
            set_stage("wait_always_on_persistence")
            wait_before_reboot(client, port, args.timeout)
            set_stage("reboot_always_on")
            value = reboot_healthy(port, True, args.expected_version, args.timeout)
            emit("always_on_policy_survived_restart", value)
            pin = client.pin
            client = None
            client = pair_at("pair_after_always_on_reboot", pin)
            set_stage("check_always_on_export_after_reboot")
            display_http(client, True, brightness, args.expected_version)
            summary["checks"].append("Always-on setting persists across healthy restart and settings export")
        else:
            set_stage("idle_only_enable_always_on")
            set_policy(client, port, True, brightness, args.expected_version)
            wait_uart(port, lambda item: item["always_on"] == 1 and item["dimmed"] == 0
                      and item["backlight"] == brightness, 60, args.expected_version)
            summary["checks"].append("Always-on status and settings export round-trip before idle check")
            emit("persistence_phases_skipped_by_idle_only")
        port.write(b"screen:0\n")
        port.flush()

        # UART/HTTP reads must not manufacture touch activity. We wait for the
        # firmware's real LVGL idle counter, never shorten the three-minute timer.
        set_stage("wait_actual_three_minute_idle")
        deadline = time.monotonic() + args.timeout
        last_report = 0
        value = None
        while time.monotonic() < deadline:
            value = uart_status(port)
            require_display_status(value, args.expected_version)
            require(value["always_on"] == 1, "Always-on display unexpectedly became disabled")
            require(value["backlight"] == brightness and value["dimmed"] == 0,
                    "Always-on display dimmed before or during the idle check")
            if time.monotonic() - last_report >= 20:
                emit("waiting_for_actual_idle_threshold", value)
                last_report = time.monotonic()
            if value["idle_ms"] > IDLE_THRESHOLD_MS + 1500:
                break
            time.sleep(2)
        require(value is not None and value["idle_ms"] > IDLE_THRESHOLD_MS + 1500,
                "Actual touch inactivity did not exceed the display dim threshold")
        summary["device_states"]["always_on_after_idle"] = {key: value[key] for key in DISPLAY_FIELDS}
        summary["checks"].append("Always-on retains selected physical backlight beyond three minutes of actual touch inactivity")
        emit("always_on_after_actual_idle_passed", value)

        idle_before = value["idle_ms"]
        set_stage("disable_always_on_while_idle")
        set_policy(client, port, False, brightness, args.expected_version)
        dimmed_brightness = max(10, brightness // 5)
        value = wait_uart(port, lambda item: item["dimmed"] == 1 and item["backlight"] == dimmed_brightness,
                          60, args.expected_version)
        require(value["idle_ms"] >= idle_before and value["always_on"] == 0,
                "Display toggle unexpectedly reset the touch inactivity counter")
        summary["device_states"]["automatic_dim_after_idle"] = {key: value[key] for key in DISPLAY_FIELDS}
        summary["checks"].append("Disabling always-on while idle applies the existing dim level without touch")
        emit("automatic_dim_after_actual_idle_passed", value)

        idle_before = value["idle_ms"]
        set_stage("restore_always_on_without_touch")
        set_policy(client, port, True, brightness, args.expected_version)
        value = wait_uart(port, lambda item: item["dimmed"] == 0 and item["backlight"] == brightness,
                          60, args.expected_version)
        require(value["idle_ms"] >= idle_before and value["always_on"] == 1,
                "Restoring always-on unexpectedly reset the touch inactivity counter")
        summary["device_states"]["always_on_restored_without_touch"] = {key: value[key] for key in DISPLAY_FIELDS}
        summary["checks"].append("Enabling always-on restores selected backlight without touch")
        emit("selected_brightness_restored_passed", value)
        summary["passed"] = True
    except CheckFailure as error:
        failure = str(error)
        failure_type = type(error).__name__
        failure_stage = stage
    except Exception as error:
        # Transport and OCR exception strings may include URLs or private input.
        failure = "Display verification encountered a transport, OCR, or device error"
        failure_type = type(error).__name__
        failure_stage = stage
    finally:
        if original_brightness is not None:
            try:
                if client is None:
                    client = pair_at("cleanup_pairing")
                set_stage("cleanup_restore_original_brightness_and_always_on")
                # Restore the selected brightness as well if an external edit
                # or partial verification changed it during this session.
                code, reply = client.json("/api/settings", method="POST",
                                          data={"alwaysOnDisplay": True, "brightness": original_brightness})
                require(code == 202 and reply.get("accepted") is True,
                        "Final display configuration was not accepted")
                deadline = time.monotonic() + 60
                while time.monotonic() < deadline:
                    code, restored = client.json("/api/status")
                    if code == 200 and restored.get("brightness") == original_brightness and restored.get("alwaysOnDisplay") is True:
                        break
                    time.sleep(1)
                else:
                    raise CheckFailure("Original brightness could not be restored")
                set_policy(client, port, True, original_brightness, args.expected_version)
                set_stage("cleanup_wait_persistence")
                wait_before_reboot(client, port, args.timeout)
                summary["cleanup_always_on_enabled"] = True
            except Exception as error:
                summary["cleanup_always_on_enabled"] = False
                summary["cleanup_failure"] = "Enabling always-on and restoring original brightness requires checking"
                summary["cleanup_failure_stage"] = stage
                summary["cleanup_exception_type"] = type(error).__name__
                if failure is None:
                    failure = "Display checks completed but final display restoration requires checking"
                    failure_type = type(error).__name__
                    failure_stage = stage
        if port.is_open:
            try:
                port.write(b"screen:0\n")
                port.flush()
            except Exception:
                pass
            port.close()
        if failure:
            summary["passed"] = False
            summary["failure"] = failure
            summary["failure_stage"] = failure_stage
            summary["exception_type"] = failure_type
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
