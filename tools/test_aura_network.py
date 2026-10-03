#!/usr/bin/env python3
"""Verify AURA networking over one UART session and pinned local HTTPS.

Pairing codes, credentials, cookies, raw screenshots and OCR text stay in RAM,
apart from a temporary 0600 PNG deleted immediately after macOS Vision OCR.
The script temporarily replaces API widget 1 and restores its configuration.
Optional --ota uploads an application image and verifies its healthy restart.
No hardware operation occurs until main() is explicitly executed.
"""
import argparse
import hashlib
import http.client
import ipaddress
import json
import math
import os
import re
import ssl
import struct
import subprocess
import sys
import tempfile
import time
import zlib
from pathlib import Path

import serial


class CheckFailure(Exception):
    """Contains only a fixed, non-secret explanation."""


def require(condition, description):
    if not condition:
        raise CheckFailure(description)


def read_uart(port, seconds, marker=None, maximum=8192):
    captured = bytearray()
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        block = port.read(max(1, min(port.in_waiting, 16384)))
        if block:
            captured.extend(block)
            require(len(captured) <= maximum, "UART response exceeded its bounded size")
            if marker is not None and marker in captured:
                break
    return bytes(captured)


def uart_status(port):
    port.reset_input_buffer()
    port.write(b"status\n")
    raw = read_uart(port, 3, marker=b"\n", maximum=16384)
    match = re.search(rb"AURA_STATUS ([^\r\n]+)", raw)
    if not match:
        return None
    allowed = {"uptime", "heap", "min_heap", "psram", "wifi", "internet", "time", "weather", "air", "rates", "board"}
    result = {}
    for name, number in re.findall(rb"([a-z_]+)=(\d+)", match[1]):
        key = name.decode("ascii")
        if key in allowed:
            result[key] = int(number)
    return result


def screen_png(port, page=12):
    require(type(page) is int and 0 <= page <= 13, "Screenshot page is outside the supported interface")
    port.reset_input_buffer()
    port.write(("screen:" + str(page) + "\n").encode("ascii"))
    read_uart(port, 1, maximum=16384)
    port.write(b"screenshot\n")
    raw = read_uart(port, 60, marker=b"\nAURA_SCREEN_END\n", maximum=480 * 480 * 2 + 16384)
    match = re.search(rb"AURA_SCREEN (\d+) (\d+) (\d+) ([0-9a-f]{64})\r?\n", raw)
    require(match is not None, "Device did not provide a checked screenshot frame")
    width, height, size = map(int, match.groups()[:3])
    require(width == height == 480 and size == 480 * 480 * 2, "Unexpected screenshot dimensions or byte count")
    pixels = raw[match.end():match.end() + size]
    require(len(pixels) == size, "Screenshot transfer was truncated")
    require(raw[match.end() + size:].startswith(b"\nAURA_SCREEN_END"), "Screenshot framing was interrupted")
    require(hashlib.sha256(pixels).hexdigest().encode("ascii") == match[4], "Screenshot SHA-256 verification failed")
    rgb = bytearray()
    for y in range(height):
        rgb.append(0)
        for x in range(width):
            offset = 2 * (y * width + x)
            value = pixels[offset] | pixels[offset + 1] << 8
            rgb.extend((((value >> 11) & 31) * 255 // 31, ((value >> 5) & 63) * 255 // 63, (value & 31) * 255 // 31))

    def chunk(kind, payload):
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)

    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(rgb, 9)) + chunk(b"IEND", b"")


OCR_SWIFT = r'''import Foundation
import AppKit
import Vision
guard CommandLine.arguments.count == 2, let image = NSImage(contentsOfFile: CommandLine.arguments[1]),
      let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else { exit(2) }
let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.usesLanguageCorrection = false
request.recognitionLanguages = ["en-US"]
do {
  try VNImageRequestHandler(cgImage: cg).perform([request])
  let lines = (request.results ?? []).compactMap { $0.topCandidates(1).first?.string }
  let bytes = try JSONSerialization.data(withJSONObject: lines)
  FileHandle.standardOutput.write(bytes)
} catch { exit(3) }
'''


def private_pairing_ocr(png):
    require(sys.platform == "darwin", "Automatic private pairing OCR requires macOS Vision")
    with tempfile.TemporaryDirectory(prefix="aura-private-pair-") as directory:
        os.chmod(directory, 0o700)
        image = Path(directory) / "browser.png"
        source = Path(directory) / "recognize.swift"
        fd = os.open(image, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(png)
        fd = os.open(source, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as stream:
            stream.write(OCR_SWIFT)
        try:
            process = subprocess.run(["xcrun", "swift", str(source), str(image)], capture_output=True, timeout=120, check=False)
            require(process.returncode == 0, "macOS Vision OCR did not complete")
            lines = json.loads(process.stdout)
            require(isinstance(lines, list) and all(isinstance(item, str) for item in lines), "OCR returned an unexpected result")
        finally:
            image.unlink(missing_ok=True)
        joined = "\n".join(lines)
        addresses = set()
        for candidate in re.findall(r"(?:https?\s*:\s*//\s*)?\b(?:\d{1,3}\.){3}\d{1,3}\b", joined, flags=re.I):
            candidate = re.sub(r"^https?\s*:\s*//\s*", "", candidate, flags=re.I)
            try:
                address = ipaddress.IPv4Address(candidate)
                if address.is_private and not address.is_loopback and not address.is_link_local:
                    addresses.add(str(address))
            except ipaddress.AddressValueError:
                pass
        codes = {re.sub(r"\s", "", line) for line in lines if re.fullmatch(r"\s*\d{3}\s*\d{3}\s*", line)}
        require(len(addresses) == 1 and len(codes) == 1, "Private OCR could not uniquely read the local address and pairing code")
        return addresses.pop(), codes.pop()


class PinnedLocal:
    """Trust the first local leaf certificate, then require its exact SHA-256."""
    def __init__(self, address):
        self.address = address
        self.origin = "https://" + address
        self.pin = None
        self.cookie = ""
        self.csrf = ""
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_NONE
        self.context.minimum_version = ssl.TLSVersion.TLSv1_2

    def request(self, path, method="GET", data=None, body=None, bad_csrf=False, unauthenticated=False, timeout=20):
        require(path.startswith("/") and not path.startswith("//"), "Unexpected local request path")
        connection = http.client.HTTPSConnection(self.address, 443, context=self.context, timeout=timeout)
        try:
            connection.connect()
            fingerprint = hashlib.sha256(connection.sock.getpeercert(binary_form=True)).digest()
            if self.pin is None:
                self.pin = fingerprint
            require(fingerprint == self.pin, "Local device TLS certificate changed unexpectedly")
            headers = {"Accept": "application/json", "Origin": self.origin}
            if not unauthenticated and self.cookie:
                headers["Cookie"] = self.cookie
            if method != "GET":
                headers["X-Aura-CSRF"] = "invalid" if bad_csrf else self.csrf
                if body is not None:
                    headers["Content-Type"] = "application/octet-stream"
                else:
                    headers["Content-Type"] = "application/json"
                    body = json.dumps(data or {}, separators=(",", ":")).encode()
            connection.request(method, path, body=body, headers=headers)
            response = connection.getresponse()
            # The flash-resident 500-service companion is larger than status
            # JSON. Keep the larger bound specific to the browser document.
            response_limit = 1048576 if path == "/" and method == "GET" else 131072
            payload = response.read(response_limit + 1)
            require(len(payload) <= response_limit, "Local HTTPS response exceeded its size limit")
            cookie = response.getheader("Set-Cookie", "")
            if cookie:
                require("HttpOnly" in cookie and "Secure" in cookie and "SameSite=Strict" in cookie, "Pairing cookie lacks required protections")
                self.cookie = cookie.split(";", 1)[0]
            return response.status, payload
        finally:
            connection.close()

    def json(self, path, **options):
        status, payload = self.request(path, **options)
        try:
            value = json.loads(payload)
        except (ValueError, UnicodeError):
            raise CheckFailure("Local HTTPS JSON response was malformed") from None
        require(isinstance(value, dict), "Local HTTPS response was not a JSON object")
        return status, value


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def check_status(status, all_data=True):
    require(status.get("wifiConnected") is True and status.get("timeSynced") is True, "Router or synchronized time is unavailable")
    require(status.get("psramBytes", 0) >= 8 * 1024 * 1024 and status.get("freeHeap", 0) > 24000, "Device memory health is below the required threshold")
    if all_data:
        require(status.get("internetAvailable") is True, "Internet access has not been confirmed")
        require(all(status.get(key) is True for key in ("weatherValid", "airValid", "ratesValid")), "A public data source has not returned a valid reading")
        require(all(finite(status.get(key)) for key in ("temperature", "feelsLike", "humidity", "wind", "aqi", "pm25", "eurRon", "eurUsd")), "A displayed reading is not finite")
        require(0 <= status["humidity"] <= 100 and status["wind"] >= 0 and status["aqi"] >= 0 and status["pm25"] >= 0 and status["eurRon"] > 0 and status["eurUsd"] > 0, "A public reading is outside its supported range")
        require(all(isinstance(status.get(key), int) and status[key] >= 0 for key in ("weatherAgeMinutes", "airAgeMinutes")), "A public reading has no confirmed data age")
        require(re.fullmatch(r"\d{4}-\d{2}-\d{2}", status.get("rateDate", "")) is not None, "Reference rates lack their publication date")
    require("adminCode" not in status and "password" not in status, "Status response unexpectedly contains sensitive fields")


def export_has_secrets(value):
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = re.sub("[^a-z]", "", key.lower())
            if any(part in normalized for part in ("password", "pairingcode", "admincode", "privatekey", "cookie", "csrf", "sessiontoken")):
                return True
            if export_has_secrets(item):
                return True
    if isinstance(value, list):
        return any(export_has_secrets(item) for item in value)
    return False


def wait_http(client, predicate, seconds, port=None):
    deadline = time.monotonic() + seconds
    last = None
    while time.monotonic() < deadline:
        try:
            code, last = client.json("/api/status")
            if code == 200 and predicate(last):
                return last
        except CheckFailure:
            raise
        except (OSError, ssl.SSLError, http.client.HTTPException):
            pass
        if port is not None and port.in_waiting:
            port.read(min(port.in_waiting, 16384))
        time.sleep(2)
    raise CheckFailure("Timed out waiting for device data or a configuration round-trip")


def ota_restart(client, port, image, timeout):
    binary = image.read_bytes()
    require(1024 <= len(binary) <= 5 * 1024 * 1024 and binary[0] == 0xE9, "OTA file is not a bounded application image")
    require(len(binary) >= 36 and struct.unpack_from("<H", binary, 12)[0] == 9 and struct.unpack_from("<I", binary, 32)[0] == 0xABCD5432, "OTA file is not an ESP32-S3 application image")
    port.reset_input_buffer()
    code, result = client.json("/api/ota", method="POST", body=binary, timeout=180)
    require(code == 200 and result.get("verified") is True, "OTA did not verify and activate the image")
    deadline = time.monotonic() + min(timeout, 90)
    raw = bytearray()
    while time.monotonic() < deadline:
        if port.in_waiting:
            raw.extend(port.read(min(port.in_waiting, 4096)))
            require(len(raw) < 131072, "OTA boot output exceeded its limit")
            require(not any(marker in raw for marker in (b"Guru Meditation", b"Backtrace:", b"PANIC", b"Brownout", b"AURA_FATAL")), "OTA restart reported a crash marker")
            if b"AURA_READY" in raw and b"AURA_HEALTH startup=passed" in raw:
                return
        time.sleep(.1)
    raise CheckFailure("OTA restart did not pass startup health within its deadline")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", required=True)
    parser.add_argument("--timeout", type=int, default=240, help="Network/data deadline in seconds")
    parser.add_argument("--ota", type=Path, help="Optional AURA application .bin; updates the inactive slot")
    parser.add_argument("--summary", type=Path, help="Optional non-secret JSON result file; must not exist")
    args = parser.parse_args()
    if not 60 <= args.timeout <= 600:
        parser.error("timeout must be 60..600 seconds")
    if args.ota and not args.ota.is_file():
        parser.error("OTA application file does not exist")
    if args.summary and args.summary.exists():
        parser.error("summary output already exists")
    summary = {"product": "AURA Desk", "checks": [], "passed": False, "ota_requested": args.ota is not None}
    port = serial.Serial(port=None, baudrate=115200, timeout=.2, exclusive=True)
    port.dtr = False
    port.rts = False
    port.port = args.port
    original_widget = None
    client = None
    failure = None
    try:
        port.open()
        # Opening this WCH driver may pulse EN despite released control lines.
        initial_boot=read_uart(port, 9, maximum=131072)
        require(not any(marker in initial_boot for marker in (b"Guru Meditation", b"Backtrace:", b"PANIC", b"Brownout", b"AURA_FATAL")), "Initial startup reported a crash marker")
        deadline = time.monotonic() + args.timeout
        status = None
        while time.monotonic() < deadline:
            status = uart_status(port)
            if status and status.get("wifi") == 1 and status.get("time") == 1:
                break
            time.sleep(2)
        require(status is not None and status.get("wifi") == 1 and status.get("time") == 1, "Router connection or synchronized time was not established")
        require(status.get("board") == 1 and status.get("psram", 0) >= 8 * 1024 * 1024, "UART board/memory checks failed")
        summary["checks"].append("UART router, clock, display and memory")
        address, pairing_code = private_pairing_ocr(screen_png(port))
        client = PinnedLocal(address)
        summary["ip"] = address
        code, html = client.request("/")
        require(code == 200 and b"AURA" in html and b"Pair this browser" in html, "HTTPS browser shell is unavailable")
        code, _ = client.json("/api/status", unauthenticated=True)
        require(code == 401, "Unauthenticated status was not rejected")
        code, pairing = client.json("/api/pair", method="POST", data={"code": pairing_code}, unauthenticated=True)
        pairing_code = ""
        require(code == 200 and pairing.get("paired") is True and isinstance(pairing.get("csrf"), str), "Device pairing did not succeed")
        client.csrf = pairing["csrf"]
        summary["checks"].append("Pinned HTTPS, browser shell, authentication and secure cookie")
        code, _ = client.json("/api/refresh", method="POST", data={}, bad_csrf=True)
        require(code == 403, "Invalid CSRF token was not rejected")
        summary["checks"].append("CSRF rejection")
        value = wait_http(client, lambda item: all(item.get(key) is True for key in ("weatherValid", "airValid", "ratesValid", "internetAvailable")), args.timeout, port)
        check_status(value)
        summary["checks"].append("Internet, weather, air quality, reference rates and data ages")
        code, exported = client.json("/api/export")
        require(code == 200 and not export_has_secrets(exported), "Settings export failed or contained sensitive fields")
        summary["checks"].append("Configuration export excludes sensitive fields")
        configs = value.get("widgetConfig", [])
        require(isinstance(configs, list) and len(configs) == 2 and isinstance(configs[0], dict), "Saved widget configurations are unavailable")
        require(all(isinstance(config, dict) for config in configs), "Widget configuration has an unsupported shape")
        selected = next((index for index, config in enumerate(configs) if not config.get("enabled", False)), 0)
        previous = configs[selected]
        summary["widget_index"] = selected
        summary["restoration_mode"] = "previous-config" if previous else "disabled-defaults"
        original_widget = {"index": selected, "label": "API widget " + str(selected + 1), "url": "", "field": "", "unit": "", "interval": 1800, "enabled": False}
        original_widget.update({key: previous[key] for key in original_widget if key != "index" and key in previous})
        test_widget = {"index": selected, "label": "Network check", "url": "https://api.open-meteo.com/v1/forecast?latitude=44.4268&longitude=26.1025&current=relative_humidity_2m", "field": "current.relative_humidity_2m", "unit": "%", "interval": 300, "enabled": True}
        code, _ = client.json("/api/widget", method="POST", data=test_widget)
        require(code == 202, "Widget configuration was not accepted")
        result = wait_http(client, lambda item: len(item.get("widgets", [])) == 2 and item["widgets"][selected].get("label") == "Network check" and item["widgets"][selected].get("valid") is True, args.timeout, port)
        reading = result["widgets"][selected]
        try:
            humidity = float(reading.get("value", ""))
        except (ValueError, TypeError):
            raise CheckFailure("Widget did not display a numeric public reading") from None
        require(math.isfinite(humidity) and 0 <= humidity <= 100 and reading.get("ageMinutes", -1) >= 0, "Widget reading or age was invalid")
        summary["checks"].append("Public JSON widget configuration and real reading")
        code, _ = client.json("/api/widget", method="POST", data=original_widget)
        require(code == 202, "Original widget settings could not be restored")
        expected = {key: val for key, val in original_widget.items() if key != "index"}
        wait_http(client, lambda item: len(item.get("widgetConfig", [])) == 2 and item["widgetConfig"][selected] == expected, 45, port)
        original_widget = None
        summary["checks"].append("Original widget configuration restored")
        if args.ota:
            ota_restart(client, port, args.ota, args.timeout)
            summary["checks"].append("OTA image verification and healthy restart")
        summary["passed"] = True
    except CheckFailure as error:
        failure = str(error)
    except Exception:
        # Never include exception representations: URLs/headers/OCR can be secret.
        failure = "Network verification encountered a transport, OCR, or device error"
    finally:
        if original_widget is not None and client is not None:
            try:
                code, _ = client.json("/api/widget", method="POST", data=original_widget)
                require(code == 202, "Original widget configuration could not be restored")
                expected = {key: val for key, val in original_widget.items() if key != "index"}
                selected = original_widget["index"]
                wait_http(client, lambda item: len(item.get("widgetConfig", [])) == 2 and item["widgetConfig"][selected] == expected, 45, port)
                summary["cleanup_restore_verified"] = True
            except Exception:
                summary["cleanup_restore_verified"] = False
                failure = "Verification stopped and original widget restoration requires checking"
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
