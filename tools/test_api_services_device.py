#!/usr/bin/env python3
"""Verify new scalar profiles on the ESP32, then restore both saved widgets.

Only profile IDs, request outcomes and numeric health diagnostics are recorded.
Identity, pairing, TLS pins, cookies and saved configurations remain in RAM.
This performs authorized temporary settings writes; it does not write firmware
or eFuses. Physical display matching is handled by test_api_device.py.
"""
import argparse
import contextlib
import io
import json
import os
from pathlib import Path
import time

from backup_device import connect, require_expected_mac
from test_always_on import CRASH_MARKERS, uart_status, wait_uart
from test_aura_network import CheckFailure, private_pairing_ocr, read_uart, require, screen_png
from test_navigation_device import pair_in_memory, read_only_json

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", required=True)
    parser.add_argument("--expected-version", required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--profile-timeout", type=int, default=90)
    parser.add_argument("--profile", action="append", help="Restrict a diagnostic run to these profile IDs")
    parser.add_argument("--uart-log", type=Path, help="Private UART diagnostics; may contain device details")
    args = parser.parse_args()
    require(20 <= args.profile_timeout <= 180, "Profile deadline is outside its bound")
    require(not args.summary.exists(), "Summary already exists")
    require_expected_mac()
    profiles = json.loads((ROOT / "docs/PUBLIC_API_SERVICE_READINGS.json").read_text())["profiles"]
    total_profiles = len(profiles)
    if args.profile:
        requested = set(args.profile)
        require(requested <= {x["id"] for x in profiles}, "Unknown profile ID")
        profiles = [x for x in profiles if x["id"] in requested]
    results = {"firmware": args.expected_version, "passed": False, "profiles": [],
               "read_only_transport_retries": 0, "settings_temporarily_written": False,
               "firmware_writes": False, "efuse_writes": False, "physical_touch_tested": False}
    port = client = original = baseline = uart_log = None
    failure = None
    try:
        if args.uart_log:
            fd = os.open(args.uart_log, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            uart_log = os.fdopen(fd, "wb")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            esp, _ = connect(args.port, 115200)
            port = esp._port
            port.exclusive = True
            port.timeout = .2
            port.dtr = port.rts = False
            esp.hard_reset()
            port.dtr = port.rts = False
        boot = read_uart(port, 9, maximum=131072)
        if uart_log:
            uart_log.write(boot)
        require(b"AURA_READY" in boot and b"AURA_HEALTH startup=passed" in boot
                and not any(marker in boot for marker in CRASH_MARKERS), "Device startup failed")
        wait_uart(port, lambda x: x.get("wifi") == 1 and x.get("time") == 1, 180, args.expected_version)
        address, code = private_pairing_ocr(screen_png(port))
        client = pair_in_memory(address, code, 90)
        address = code = ""
        http, baseline = read_only_json(client, "/api/status", results)
        require(http == 200 and baseline.get("firmware") == "AURA Desk " + args.expected_version,
                "Installed firmware differs")
        original = baseline.get("widgetConfig")
        require(isinstance(original, list) and len(original) == 2
                and all(isinstance(x, dict) for x in original), "Saved widget configuration is unavailable")
        minimum_heap = baseline["minimumHeap"]
        for profile in profiles:
            payload = {key: profile[key] for key in ["label", "url", "field", "unit", "interval"]}
            payload.update(index=0, enabled=True)
            http, _ = client.json("/api/widget", method="POST", data=payload)
            require(http == 202, "A new profile configuration was rejected")
            results["settings_temporarily_written"] = True
            deadline = time.monotonic() + args.profile_timeout
            outcome = None
            while time.monotonic() < deadline:
                http, status = read_only_json(client, "/api/status", results)
                require(http == 200 and status.get("firmware") == "AURA Desk " + args.expected_version,
                        "Device status differs during profile checks")
                require(status.get("freeHeap", 0) > 24000 and status.get("psramBytes", 0) >= 8388608,
                        "Device memory health fell below its threshold")
                minimum_heap = min(minimum_heap, status["minimumHeap"])
                widget = status["widgets"][0]
                expected_config = {key: value for key, value in payload.items() if key != "index"}
                if status["widgetConfig"][0] == expected_config and not widget.get("fetching"):
                    if widget.get("valid") and not widget.get("error") and widget.get("httpStatus") == 200:
                        value = widget.get("value", "")
                        require(isinstance(value, str) and 0 < len(value.encode()) <= 47,
                                "Device scalar is outside display bounds")
                        outcome = {"id": profile["id"], "service_id": profile["serviceId"],
                                   "passed": True, "http_status": 200, "scalar_bytes": len(value.encode())}
                        break
                    if widget.get("error"):
                        outcome = {"id": profile["id"], "service_id": profile["serviceId"],
                                   "passed": False, "http_status": widget.get("httpStatus", 0),
                                   "device_error": widget["error"]}
                        break
                if port.in_waiting:
                    raw = port.read(min(port.in_waiting, 16384))
                    if uart_log:
                        uart_log.write(raw)
                    require(not any(marker in raw for marker in CRASH_MARKERS), "Device reported a crash")
                time.sleep(1)
            if outcome is None:
                outcome = {"id": profile["id"], "service_id": profile["serviceId"],
                           "passed": False, "deadline_exceeded": True}
            results["profiles"].append(outcome)
            print(json.dumps({"profile": outcome["id"], "passed": outcome["passed"],
                              "completed": len(results["profiles"]), "total": len(profiles)}), flush=True)
        results["minimum_heap_observed_bytes"] = minimum_heap
        results["selected_profiles_checked"] = len(results["profiles"]) == len(profiles)
        results["all_profiles_checked"] = len(results["profiles"]) == total_profiles
        require(all(x["passed"] for x in results["profiles"]), "One or more live profiles failed")
        results["passed"] = True
    except CheckFailure as error:
        failure = str(error)
    except Exception:
        failure = "Live profile verification encountered a transport or device error"
    finally:
        if client is not None and original is not None:
            try:
                for index, config in enumerate(original):
                    http, _ = client.json("/api/widget", method="POST", data={"index": index, **config})
                    require(http == 202, "Saved widget restoration was rejected")
                deadline = time.monotonic() + 90
                while True:
                    http, status = read_only_json(client, "/api/status", results)
                    if http == 200 and status["widgetConfig"] == original:
                        require(status["brightness"] == baseline["brightness"]
                                and status["alwaysOnDisplay"] == baseline["alwaysOnDisplay"],
                                "Display policy changed during profile tests")
                        results["saved_widgets_restored"] = True
                        results["display_settings_preserved"] = True
                        break
                    require(time.monotonic() < deadline, "Saved widget restoration did not complete")
                    time.sleep(1)
            except Exception:
                results["saved_widgets_restored"] = False
                results["passed"] = False
                failure = "Saved widget restoration requires checking"
        if port is not None:
            if uart_log and port.in_waiting:
                uart_log.write(port.read(min(port.in_waiting, 131072)))
            port.write(b"screen:0\n")
            port.flush()
            port.close()
        if uart_log:
            uart_log.close()
        if failure:
            results["failure"] = failure
        fd = os.open(args.summary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as out:
            json.dump(results, out, indent=2)
            out.write("\n")
    print(json.dumps({"passed": results["passed"], "checked": len(results["profiles"]),
                      "restored": results.get("saved_widgets_restored", False)}), flush=True)
    return 0 if results["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
