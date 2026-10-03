#!/usr/bin/env python3
"""Exercise fail-closed release evidence gates without packaging or device access.

Uses temporary synthetic reports and artifact bytes. It checks the production
gate and its real inputs() wiring; it cannot prove that a report's claims are true.
An optional conclusions-only summary is created with private file permissions.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
from unittest.mock import patch

import package_release as policy


def fixtures():
    payload = {
        f"{policy.RELEASE}/AuraDesk.ino.bin": b"synthetic application fixture",
        f"{policy.RELEASE}/AuraDesk.ino.merged.bin": b"synthetic factory fixture",
        "docs/PUBLIC_API_SERVICES.json": b'{"synthetic": "service source"}',
        "docs/PUBLIC_API_SERVICE_READINGS.json": b'{"synthetic": "reading source"}',
        "firmware/AuraDesk/api_services.js.inc": b"synthetic generated source",
    }
    reports = {name: {
        "schema_version": 1, "product": "AURA Desk", "version": policy.VERSION,
        "status": "validated", "passed": True, "release_ready": True,
        "checks": {gate: {"passed": True} for gate in gates},
    } for name, gates in policy.REPORT_CHECKS.items()}
    release = reports[policy.RELEASE_REPORT]
    for key, filename in (("application", "AuraDesk.ino.bin"), ("factory_image", "AuraDesk.ino.merged.bin")):
        value = payload[f"{policy.RELEASE}/{filename}"]
        release[key] = {"file": filename, "bytes": len(value), "sha256": policy.digest(value)}
    reports[policy.API_SERVICES_REPORT]["source_sha256"] = {
        name: policy.digest(value) for name, value in payload.items() if not name.startswith("releases/")
    }
    return payload, reports


def encoded(payload, reports):
    result = dict(payload)
    result.update({name: json.dumps(value).encode() for name, value in reports.items()})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--current-reports", action="store_true", help="Also require current public reports to pass")
    parser.add_argument("--summary", type=Path, help="Create a new private conclusions-only summary")
    args = parser.parse_args()
    if args.summary and args.summary.exists():
        parser.error("Summary already exists")
    payload, reports = fixtures()
    checked = rejected = 0

    def accepts(data):
        nonlocal checked
        policy.validate_release_reports(data)
        checked += 1

    def refuses(data, label, expected=None):
        nonlocal checked, rejected
        try:
            policy.validate_release_reports(data)
        except ValueError as error:
            if expected and expected not in str(error):
                raise AssertionError(f"Wrong rejection for {label}") from error
            checked += 1
            rejected += 1
        else:
            raise AssertionError(f"Incomplete evidence accepted: {label}")

    accepts(encoded(payload, reports))
    historical = deepcopy(reports)
    historical[policy.API_SERVICES_REPORT]["checks"]["initial_failed_attempt"] = {
        "passed": False, "status": "historical_failure", "checked": 22, "successful": 21,
    }
    accepts(encoded(payload, historical))

    for name, gates in policy.REPORT_CHECKS.items():
        base = encoded(payload, reports)
        missing = dict(base)
        del missing[name]
        refuses(missing, "missing current report", "missing")
        for replacement in ([], None):
            bad = dict(base)
            bad[name] = json.dumps(replacement).encode()
            refuses(bad, "invalid report object", "schema")
        for key, values in {
            "schema_version": [None, True, 2],
            "product": [None, "Other product"],
            "version": [None, "0.0.0"],
            "passed": [False, None, "true", 1],
            "release_ready": [False, None, "true", 1],
            "status": [None, "pending", "draft", "failed"],
            "checks": [None, []],
        }.items():
            for value in values:
                changed = deepcopy(reports)
                changed[name][key] = value
                refuses(encoded(payload, changed), "invalid current report field " + key)
        for gate in gates:
            for value in (None, {"passed": False}, {"passed": None}):
                changed = deepcopy(reports)
                changed[name]["checks"][gate] = value
                refuses(encoded(payload, changed), "unfinished final gate " + gate, "Final validation gate")
        for field in ("token", "password", "ssid"):
            changed = deepcopy(reports)
            changed[name][field] = "synthetic secret fixture"
            refuses(encoded(payload, changed), "private report field", "private")
        changed = deepcopy(reports)
        changed[name]["notes"] = "Bearer synthetic-secret-fixture"
        refuses(encoded(payload, changed), "embedded authentication marker", "authentication")
        bad = dict(base)
        body = json.dumps(reports[name])
        bad[name] = (body[:-1] + ',"passed":true}').encode()
        refuses(bad, "ambiguous duplicate JSON key", "Invalid current-release validation JSON")
        bad[name] = (body[:-1] + ',"invalid":NaN}').encode()
        refuses(bad, "nonfinite JSON", "Invalid current-release validation JSON")
        bad[name] = b'{"invalid UTF8": "\xff"}'
        refuses(bad, "invalid UTF8", "Invalid current-release validation JSON")

    for key in ("application", "factory_image"):
        for field, value in (("file", "different.bin"), ("bytes", 1), ("bytes", True), ("sha256", "0" * 64)):
            changed = deepcopy(reports)
            changed[policy.RELEASE_REPORT][key][field] = value
            refuses(encoded(payload, changed), "firmware record does not bind bytes", "does not match")
        changed = deepcopy(reports)
        del changed[policy.RELEASE_REPORT][key]
        refuses(encoded(payload, changed), "missing validated firmware record", "missing")
    for name in reports[policy.API_SERVICES_REPORT]["source_sha256"]:
        changed_payload = dict(payload)
        changed_payload[name] += b"changed after validation"
        refuses(encoded(changed_payload, reports), "stale validated catalog source", "does not match")
        changed = deepcopy(reports)
        del changed[policy.API_SERVICES_REPORT]["source_sha256"][name]
        refuses(encoded(payload, changed), "missing catalog source digest", "does not match")
    changed = deepcopy(reports)
    changed[policy.API_SERVICES_REPORT]["source_sha256"] = None
    refuses(encoded(payload, changed), "missing validated catalog digest map", "does not match")

    # Exercise the real entry point: a gate that exists but is never called would
    # still fail these fixtures. The temporary 16 MiB image is never installed.
    integrated_payload = dict(payload)
    app_name = f"{policy.RELEASE}/AuraDesk.ino.bin"
    merged_name = f"{policy.RELEASE}/AuraDesk.ino.merged.bin"
    application = integrated_payload[app_name]
    merged = bytearray(16 * 1024 * 1024)
    merged[0x20000:0x20000 + len(application)] = application
    integrated_payload[merged_name] = bytes(merged)
    layout_name = f"{policy.RELEASE}/build-layout.json"
    integrated_payload[layout_name] = json.dumps({
        "chip": "esp32s3", "regions": [{"file": "AuraDesk.ino.bin", "offset": "0x20000",
            "bytes": len(application), "sha256": policy.digest(application)}],
        "merged_image": {"file": "AuraDesk.ino.merged.bin", "bytes": len(merged),
            "sha256": policy.digest(merged)},
    }).encode()
    integrated_reports = deepcopy(reports)
    integrated_reports[policy.RELEASE_REPORT]["factory_image"].update(
        bytes=len(merged), sha256=policy.digest(merged))
    integrated_payload = encoded(integrated_payload, integrated_reports)
    integrated_payload.update({"docs/RELEASE_VALIDATION.md": b"Synthetic complete report fixture",
        "THIRD_PARTY_NOTICES.md": b"Synthetic notice fixture",
        "artifacts/ui-preview/home_offline.png": b"\x89PNG\r\n\x1a\n"})
    with tempfile.TemporaryDirectory(prefix="aura-package-gate-") as temporary:
        root = Path(temporary)
        for name, value in integrated_payload.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(value)
        os.utime(root / app_name, ns=(2_000_000_000_000_000_000, 2_000_000_000_000_000_000))
        with patch.object(policy, "ROOT", root), patch.object(policy, "REQUIRED", list(integrated_payload)), patch.object(policy, "OPTIONAL", []):
            prepared, conclusion = policy.inputs()
            assert conclusion["release_ready"] is True and conclusion["version"] == policy.VERSION
            assert conclusion["check_source"] == policy.RELEASE_REPORT
            assert conclusion["api_services_source"] == policy.API_SERVICES_REPORT
            assert prepared[app_name] == application
            checked += 1
            changed = deepcopy(integrated_reports)
            changed[policy.API_SERVICES_REPORT]["release_ready"] = False
            (root / policy.API_SERVICES_REPORT).write_bytes(json.dumps(changed[policy.API_SERVICES_REPORT]).encode())
            try:
                policy.inputs()
            except ValueError as error:
                assert policy.API_SERVICES_REPORT in str(error) and "incomplete" in str(error)
                checked += 1
                rejected += 1
            else:
                raise AssertionError("Actual inputs() bypasses the API-services evidence gate")

    current_passed = None
    if args.current_reports:
        names = [policy.RELEASE_REPORT, policy.API_SERVICES_REPORT,
                 app_name, merged_name, "docs/PUBLIC_API_SERVICES.json",
                 "docs/PUBLIC_API_SERVICE_READINGS.json", "firmware/AuraDesk/api_services.js.inc"]
        policy.validate_release_reports({name: policy.allowed(name).read_bytes() for name in names})
        current_passed = True
        checked += 1
    summary = {"passed": True, "checks": checked, "negative_fixtures_rejected": rejected,
        "historical_failed_attempt_retention_tested": True, "actual_inputs_wiring_tested": True,
        "exact_firmware_and_catalog_binding_tested": True, "current_public_reports_passed": current_passed,
        "device_access": False, "firmware_writes": False, "packaging_writes": False,
        "scope": "Offline evidence refusal and binding checks; synthetic artifacts only. No hardware or provider claims are inferred."}
    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(args.summary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as stream:
            json.dump(summary, stream, indent=2)
            stream.write("\n")
    print(f"PASS: {checked} package evidence checks; {rejected} incomplete, stale, ambiguous or private fixtures rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
