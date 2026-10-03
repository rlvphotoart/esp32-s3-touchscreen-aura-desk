#!/usr/bin/env python3
"""Generate the 500-service browser catalog and additional scalar reading examples.

Reads public JSON and licence files only. No network, device or ignored research
files are needed. --check rejects a stale generated adjacent C++ string literal.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DELIMITER = "AURASVC"
BEGIN = "/* AURA_API_SERVICES_BEGIN */"
END = "/* AURA_API_SERVICES_END */"
SERVICE_RUNTIME_KEYS = (
    "id", "name", "provider", "category", "use_case", "docs_url", "auth", "auth_code",
    "access", "formats", "current_firmware_fit", "fit_code", "evidence_status",
    "evidence_code", "notes", "reading_ids",
)
READING_RUNTIME_KEYS = (
    "name", "category", "label", "url", "field", "unit", "interval", "hint", "docs",
    "provider", "locationBased", "serviceId",
)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def load_document(relative):
    def bad_number(value):
        raise ValueError(f"Non-finite JSON number: {value}")
    return json.loads((ROOT / relative).read_text(), object_pairs_hook=unique_object,
                      parse_constant=bad_number)


def safe_docs_url(value):
    if not isinstance(value, str) or any(ord(c) < 32 for c in value):
        return False
    try:
        parsed = urlsplit(value)
        return parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username and not parsed.password
    except ValueError:
        return False


def runtime_documents():
    document = load_document("docs/PUBLIC_API_SERVICES.json")
    readings = load_document("docs/PUBLIC_API_SERVICE_READINGS.json")
    old_document = load_document("docs/PUBLIC_API_CATALOG.json")
    if document.get("schema_version") != 1 or document.get("count") != 500:
        raise ValueError("Exactly 500 service records with schema_version 1 are required")
    services = document["services"]
    if len(services) != 500 or len({row["id"] for row in services}) != 500:
        raise ValueError("Service record identifiers must be unique")
    if len({row["name"].casefold() for row in services}) != 500:
        raise ValueError("Service names must be unique")
    for count_field, field in (("auth_counts", "auth_code"), ("fit_counts", "fit_code"),
                               ("evidence_counts", "evidence_code")):
        if document[count_field] != dict(Counter(row[field] for row in services)):
            raise ValueError(f"Inconsistent service {count_field}")
    if document["category_count"] != len({row["category"] for row in services}):
        raise ValueError("Inconsistent category count")
    if not re.fullmatch(r"[0-9a-f]{64}", document["source_frozen_sha256"]):
        raise ValueError("Frozen review digest must be SHA-256")
    for source in document["source_directories"]:
        if not safe_docs_url(source["url"]) or source["license"] != "MIT":
            raise ValueError("Invalid discovery provenance")
        relative = Path(source["license_file"])
        if relative.is_absolute() or ".." in relative.parts or relative.parts[:2] != ("third_party", "catalog-discovery"):
            raise ValueError("Discovery licence path leaves its public directory")
        if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != source["license_sha256"]:
            raise ValueError("Discovery licence differs from its recorded digest")
    ids = {row["id"] for row in services}
    old_readings = {row["id"]: row for row in old_document["presets"]}
    if len(old_readings) != 100 or old_document["count"] != 100:
        raise ValueError("Original 100 reading examples must be retained")
    if readings.get("schema_version") != 1 or readings["count"] != len(readings["profiles"]):
        raise ValueError("Additional profile schema/count mismatch")
    new_readings = {row["id"]: row for row in readings["profiles"]}
    if len(new_readings) != readings["count"] or set(new_readings) & set(old_readings):
        raise ValueError("Reading identifiers must be unique across both catalogs")
    for row in new_readings.values():
        if not re.fullmatch(r"svc_[a-z0-9_]+", row["id"]) or row["serviceId"] not in ids:
            raise ValueError("New reading identifier or service association is invalid")
        for key, maximum in (("label", 27), ("url", 200), ("field", 80), ("unit", 15)):
            value = row[key]
            if not isinstance(value, str) or len(value.encode()) > maximum or any(ord(c) < 32 for c in value):
                raise ValueError(f"Reading {key} exceeds firmware limits")
        if not row["label"] or not safe_docs_url(row["url"]) or urlsplit(row["url"]).fragment:
            raise ValueError("Reading label/URL is invalid")
        if not re.fullmatch(r"[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*", row["field"]):
            raise ValueError("Reading dot path is invalid")
        if type(row["interval"]) is not int or not 300 <= row["interval"] <= 86400:
            raise ValueError("Reading interval exceeds firmware limits")
        if row["locationBased"] is not False or row["deviceTested"] is not False:
            raise ValueError("Desktop-derived profile cannot imply device testing or saved-city substitution")
        evidence = row["verification"]
        if evidence["httpStatus"] != 200 or not 0 < evidence["bytes"] <= 32768 or not 0 < evidence["scalarBytes"] <= 47:
            raise ValueError("Reading verification exceeds firmware bounds")
        if evidence["scalarType"] not in ("string", "number", "boolean"):
            raise ValueError("Reading verification must select a scalar")
        if not evidence["tlsVerified"] or evidence["redirectsFollowed"] or evidence["authenticationUsed"] or not evidence["scalarPathValidated"]:
            raise ValueError("Reading has insufficient direct anonymous HTTPS evidence")
        if not re.fullmatch(r"[0-9a-f]{64}", evidence["responseSha256"]):
            raise ValueError("Reading response digest is invalid")
    mappings = document["reading_mappings"]
    if len(mappings) != 100 or {m["reading_id"] for m in mappings} != set(old_readings):
        raise ValueError("Each original reading needs one mapping or an explicit legacy association")
    old_owners = {}
    for mapping in mappings:
        sid = mapping["service_id"]
        if sid is not None and sid not in ids:
            raise ValueError("Original reading association points to an absent service")
        if mapping["status"] != ("catalog_service" if sid else "legacy_retained"):
            raise ValueError("Original reading mapping status disagrees with its association")
        old_owners[mapping["reading_id"]] = sid
    owners = {**old_owners, **{key: row["serviceId"] for key, row in new_readings.items()}}
    for service in services:
        if not all(key in service for key in SERVICE_RUNTIME_KEYS):
            raise ValueError("Service runtime metadata is incomplete")
        if not safe_docs_url(service["docs_url"]) or not safe_docs_url(service["source_url"]):
            raise ValueError("Service documentation/source URL is invalid")
        if service["ready_preset"] is not False or service["device_tested"] is not False:
            raise ValueError("Service discovery must not imply all integrations are tested")
        expected = [key for key, owner in owners.items() if owner == service["id"]]
        if len(service["reading_ids"]) != len(set(service["reading_ids"])) or set(service["reading_ids"]) != set(expected):
            raise ValueError("Service reading associations are incomplete or incorrect")
    if document["reading_profile_count"] != len(owners):
        raise ValueError("Total reading count disagrees with profile catalogs")
    if document["mapped_reading_count"] != sum(owner is not None for owner in owners.values()):
        raise ValueError("Mapped reading count disagrees with associations")
    if document["legacy_reading_count"] != sum(owner is None for owner in owners.values()):
        raise ValueError("Legacy reading count disagrees with associations")
    runtime_services = [{key: service[key] for key in SERVICE_RUNTIME_KEYS} for service in services]
    runtime_readings = {key: {field: row[field] for field in READING_RUNTIME_KEYS}
                        for key, row in new_readings.items()}
    return runtime_services, runtime_readings


def compact(value):
    # Escape HTML-sensitive delimiters while preserving decoded data exactly.
    text = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    text = text.replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    if ")" + DELIMITER + '"' in text or "</script" in text.lower():
        raise ValueError("Generated data could terminate a source/script container")
    return text


def expected_include():
    services, readings = runtime_documents()
    script = (BEGIN + "\nconst API_SERVICES=" + compact(services) + ";\n"
              + "const SERVICE_READINGS=" + compact(readings) + ";\n" + END + "\n")
    return ('/* Generated by tools/generate_api_services.py; do not edit. */\n'
            + 'R"' + DELIMITER + '(\n' + script + ')' + DELIMITER + '"\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = ROOT / "firmware/AuraDesk/api_services.js.inc"
    try:
        result = expected_include()
    except (KeyError, TypeError, ValueError, OSError) as error:
        parser.error(str(error))
    if args.check:
        if not path.exists() or path.read_text() != result:
            parser.error("Generated services include is stale; run tools/generate_api_services.py")
        print("PASS: exactly 500 service records and additional readings match the public catalogs")
    elif not path.exists() or path.read_text() != result:
        path.write_text(result)
        print("Generated exactly 500 service records and additional scalar readings")
    else:
        print("Service catalog already current")


if __name__ == "__main__":
    main()
