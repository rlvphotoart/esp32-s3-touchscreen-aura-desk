#!/usr/bin/env python3
"""Check real-device Browser re-entry, private pairing and display preservation.

Serial page navigation is the tested scope; no physical or synthetic touches
are injected. Pairing screenshots, addresses, codes, cookies, certificate pins
and authenticated bodies remain private in RAM (the existing macOS OCR helper
uses a temporary 0600 image that it deletes). Only fixed descriptions, checked
booleans and numeric display state are reported. No settings, flash or eFuses
are written. Leave the device on Home after the check. --self-test is offline.
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

from test_always_on import CRASH_MARKERS, parse_uart_status, uart_status, wait_uart
from test_aura_network import (
    CheckFailure, PinnedLocal, export_has_secrets, private_pairing_ocr,
    read_uart, require, screen_png,
)


def progress(stage, attempt=None, exception_type=None):
    record = {"stage": stage}
    if attempt is not None:
        record["attempt"] = attempt
    if exception_type is not None:
        record["exception_type"] = exception_type
    print(json.dumps(record, separators=(",", ":")), flush=True)


def pair_in_memory(address, pairing_code, timeout, previous_pin=None):
    """Retry only transport failures; keep the same code/address and TLS pin."""
    client = PinnedLocal(address)
    if previous_pin is not None:
        client.pin = previous_pin
    deadline = time.monotonic() + min(timeout, 90)
    attempt = 0
    while time.monotonic() < deadline:
        attempt += 1
        try:
            status, result = client.json("/api/pair", method="POST",
                                         data={"code": pairing_code}, unauthenticated=True,
                                         timeout=min(12, max(1, deadline-time.monotonic())))
        except ssl.SSLCertVerificationError:
            raise
        except (OSError, ssl.SSLError, http.client.HTTPException) as error:
            progress("private_pair_transport_retry", attempt, type(error).__name__)
            if time.monotonic() >= deadline:
                raise
            time.sleep(min(2, max(0, deadline-time.monotonic())))
            continue
        require(status == 200 and result.get("paired") is True and isinstance(result.get("csrf"), str),
                "Private Browser pairing was not accepted")
        client.csrf = result["csrf"]
        return client
    raise CheckFailure("Local Browser pairing did not become available before its deadline")


def read_only_json(client, path, retry_stats=None, timeout=45):
    """Retry bounded transport failures for authenticated GETs, never validation."""
    require(path in ("/api/status", "/api/export"),
            "Navigation verifier requested an unsupported read-only endpoint")
    operation = "status" if path == "/api/status" else "export"
    deadline = time.monotonic() + timeout
    attempt = 0
    while time.monotonic() < deadline:
        attempt += 1
        try:
            return client.json(path, timeout=min(12, max(1, deadline-time.monotonic())))
        except ssl.SSLCertVerificationError:
            raise
        except (OSError, ssl.SSLError, http.client.HTTPException) as error:
            if retry_stats is not None:
                retry_stats["read_only_transport_retries"] += 1
                retry_stats["last_read_only_retry_exception_type"] = type(error).__name__
            progress("authenticated_" + operation + "_transport_retry", attempt, type(error).__name__)
            if time.monotonic() >= deadline:
                raise
            time.sleep(min(2, max(0, deadline-time.monotonic())))
    raise CheckFailure("Authenticated read-only transport did not recover within its deadline")


def read_display_configuration(client, expected_version, retry_stats=None):
    code, value = read_only_json(client, "/api/status", retry_stats)
    require(code == 200, "Authenticated device status is unavailable")
    require(value.get("firmware") == "AURA Desk " + expected_version,
            "Authenticated status has an unexpected firmware version")
    require(type(value.get("alwaysOnDisplay")) is bool,
            "Authenticated status lacks a boolean display policy")
    require(type(value.get("brightness")) is int and 10 <= value["brightness"] <= 100,
            "Authenticated status lacks supported selected brightness")
    require("adminCode" not in value and "password" not in value,
            "Authenticated status unexpectedly contains sensitive device fields")
    return value["alwaysOnDisplay"], value["brightness"]


def navigate_serial(port, page):
    require(page in (0, 3), "Navigation check requested an unsupported intermediate page")
    port.reset_input_buffer()
    port.write(("screen:" + str(page) + "\n").encode("ascii"))
    port.flush()
    raw = read_uart(port, 1, maximum=16384)
    require(not any(marker in raw for marker in CRASH_MARKERS),
            "Serial page navigation reported a crash marker")
    require(b"AURA_ERROR" not in raw, "Serial page navigation was rejected")


def self_test():
    value = parse_uart_status(b"AURA_STATUS version=1.0.2 board=1 psram=8388608 always_on=1 backlight=78 idle_ms=12 dimmed=0 password=private ip=192.0.2.23\n")
    require(value["version"] == "1.0.2" and value["always_on"] == 1,
            "Navigation UART parser self-test failed")
    require("password" not in value and "ip" not in value,
            "UART parser leaked an unchecked field")
    require(export_has_secrets({"settings": {"password": "private"}}),
            "Export sensitive-field guard failed")
    require(not export_has_secrets({"alwaysOnDisplay": True, "brightness": 78}),
            "Export guard rejected valid display settings")
    progress("offline_self_test_passed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port")
    parser.add_argument("--expected-version", default="1.0.4")
    parser.add_argument("--timeout", type=int, default=240, help="Router/readiness deadline, 60..600 seconds")
    parser.add_argument("--summary", type=Path, help="Optional non-secret JSON result; must not exist")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if not args.port:
        parser.error("--port is required for actual device checks")
    if not 60 <= args.timeout <= 600:
        parser.error("timeout must be 60..600 seconds")
    if re.fullmatch(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", args.expected_version) is None:
        parser.error("expected firmware version must be three dotted numbers")
    if args.summary and args.summary.exists():
        parser.error("summary output already exists")
    summary = {"product": "AURA Desk", "firmware": args.expected_version, "passed": False,
               "serial_page_navigation_tested": True, "physical_touch_tested": False,
               "settings_writes": False, "flash_writes": False, "efuse_writes": False,
               "read_only_transport_retries": 0, "checks": []}
    port = serial.Serial(port=None, baudrate=115200, timeout=.2, exclusive=True)
    port.dtr = False
    port.rts = False
    port.port = args.port
    stage = "open_uart"
    failure = None
    original_policy = None
    original_brightness = None

    def set_stage(name):
        nonlocal stage
        stage = name
        progress(name)

    try:
        set_stage("open_uart")
        port.open()
        set_stage("initial_startup")
        initial = read_uart(port, 9, maximum=131072)
        require(not any(marker in initial for marker in CRASH_MARKERS),
                "Initial device startup reported a crash marker")
        set_stage("wait_router_and_display_status")
        first_uart = wait_uart(port, lambda item: item.get("wifi") == 1,
                               args.timeout, args.expected_version)
        original_uart_policy = bool(first_uart["always_on"])
        summary["checks"].append("Expected firmware, physical PSRAM, display diagnostics and router connection")

        set_stage("capture_first_browser_screen")
        first_png = screen_png(port)
        set_stage("private_ocr_first_browser_screen")
        address_first, code_first = private_pairing_ocr(first_png)
        first_png = None
        set_stage("pair_first_browser_entry")
        client = pair_in_memory(address_first, code_first, args.timeout)
        set_stage("read_original_display_configuration")
        original_policy, original_brightness = read_display_configuration(client, args.expected_version, summary)
        require(original_policy == original_uart_policy,
                "Display policy changed during the first Browser entry")
        if original_uart_policy:
            require(first_uart["backlight"] == original_brightness,
                    "Selected brightness changed during the first Browser entry")
        summary["selected_always_on"] = original_policy
        summary["selected_brightness"] = original_brightness

        set_stage("serial_browser_close_to_settings")
        navigate_serial(port, 3)
        set_stage("serial_settings_to_home")
        navigate_serial(port, 0)
        set_stage("capture_reopened_browser_screen")
        second_png = screen_png(port)
        set_stage("private_ocr_reopened_browser_screen")
        address_second, code_second = private_pairing_ocr(second_png)
        second_png = None
        require(address_second == address_first, "Local Browser address changed during page re-entry")
        require(code_second == code_first, "Browser pairing code changed during page re-entry within one boot")
        summary["browser_address_stable_within_boot"] = True
        summary["browser_code_stable_within_boot"] = True
        summary["checks"].append("Checked Browser screenshots retain current pairing details after serial Settings/Home re-entry")

        set_stage("pair_reopened_browser_with_pinned_certificate")
        second_client = pair_in_memory(address_second, code_second, args.timeout, client.pin)
        code_first = code_second = ""
        address_first = address_second = ""
        set_stage("verify_authenticated_status_after_reentry")
        policy, brightness = read_display_configuration(second_client, args.expected_version, summary)
        require(policy == original_policy and brightness == original_brightness,
                "Browser page re-entry changed selected display settings")
        summary["always_on_preserved"] = True
        summary["brightness_preserved"] = True
        summary["https_pairing_verified"] = True
        summary["checks"].append("Reopened Browser pairs over the same pinned TLS certificate and returns correct authenticated firmware/settings")

        set_stage("verify_export_excludes_sensitive_fields")
        status, exported = read_only_json(second_client, "/api/export", summary)
        require(status == 200 and not export_has_secrets(exported),
                "Settings export failed or contains sensitive fields")
        require(exported.get("alwaysOnDisplay") is original_policy
                and exported.get("brightness") == original_brightness,
                "Settings export differs from preserved display configuration")
        summary["checks"].append("Export excludes sensitive fields and retains selected display policy and brightness")
        set_stage("verify_final_uart_display_state")
        last_uart = uart_status(port)
        require(last_uart is not None and last_uart.get("version") == args.expected_version
                and bool(last_uart.get("always_on")) == original_policy,
                "Final UART display status differs from the initial policy")
        summary["passed"] = True
    except CheckFailure as error:
        failure = str(error)
        summary["failure_stage"] = stage
        summary["exception_type"] = type(error).__name__
    except Exception as error:
        failure = "Navigation verification encountered a transport, OCR, or device error"
        summary["failure_stage"] = stage
        summary["exception_type"] = type(error).__name__
    finally:
        if port.is_open:
            try:
                navigate_serial(port, 0)
                summary["home_navigation_command_sent"] = True
            except Exception as error:
                summary["home_navigation_command_sent"] = False
                summary["cleanup_exception_type"] = type(error).__name__
                if failure is None:
                    failure = "Final serial navigation to Home could not be verified"
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
