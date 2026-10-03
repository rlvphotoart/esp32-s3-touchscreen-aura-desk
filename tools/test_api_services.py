#!/usr/bin/env python3
"""Validate the 500-service browser catalog and its bounded reading profiles.

These offline checks enforce metadata/evidence contracts, safe public links,
exact generated source agreement, and the production C++ widget input path.
They neither contact providers nor establish availability on the ESP32. The
research directory and private device material are not required or accessed.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

from test_api_catalog import (CatalogError, Checks, RUNTIME_KEYS, clean_text,
                              json_decoder, public_https_url, validate_evidence)

ROOT = Path(__file__).resolve().parents[1]
SERVICE_KEYS = (
    "id", "name", "provider", "category", "use_case", "docs_url", "auth",
    "auth_code", "access", "formats", "current_firmware_fit", "fit_code",
    "evidence_status", "evidence_code", "notes", "reading_ids",
)
PROFILE_KEYS = RUNTIME_KEYS + ("serviceId",)
AUTH_CODES = {"no_key_reported", "no_key_confirmed", "optional_key", "unknown", "requires_key"}
FIT_CODES = {"review_required", "direct_candidate", "adapter"}
EVIDENCE_CODES = {"directory_only", "provider_docs_reviewed"}


def strict_json(text):
    try:
        value, stop = json_decoder().raw_decode(text.lstrip())
    except json.JSONDecodeError as error:
        raise CatalogError("Catalog data is not strict JSON") from error
    if text.lstrip()[stop:].strip():
        raise CatalogError("Catalog data contains extra text after JSON")
    return value


def load_json(path):
    return strict_json(path.read_text(encoding="utf-8"))


def require_text(value, checks, context):
    checks.require(clean_text(value) and "\x7f" not in value,
                   context + ": nonempty text without controls is required")


def validate_services(catalog, legacy, profiles):
    checks = Checks()
    checks.require(isinstance(catalog, dict), "Service catalog root must be an object")
    checks.require(type(catalog.get("schema_version")) is int and catalog["schema_version"] == 1,
                   "Service schema must be integer 1")
    services = catalog.get("services")
    checks.require(type(catalog.get("count")) is int and catalog["count"] == 500,
                   "Service count must be integer 500")
    checks.require(isinstance(services, list) and len(services) == 500,
                   "Exactly 500 service records are required")
    legacy_by_id = {item["id"]: item for item in legacy["presets"]}
    profile_by_id = {item["id"]: item for item in profiles["profiles"]}
    checks.require(len(legacy_by_id) == 100, "Original 100 reading IDs must be preserved")
    checks.require(not set(legacy_by_id) & set(profile_by_id), "New profile IDs cannot shadow original readings")
    readings = {**legacy_by_id, **profile_by_id}
    ids, names, documentation, associations = set(), set(), set(), {}
    runtime = []
    for number, item in enumerate(services, 1):
        context = "Service " + str(number)
        checks.require(isinstance(item, dict), context + ": service must be an object")
        checks.require(all(key in item for key in SERVICE_KEYS), context + ": runtime metadata is incomplete")
        identifier = item["id"]
        checks.require(isinstance(identifier, str) and re.fullmatch(r"[a-z0-9][a-z0-9-]*", identifier),
                       context + ": ID must be a stable lowercase identifier")
        checks.require(identifier not in ids, context + ": duplicate service ID")
        ids.add(identifier)
        for key in SERVICE_KEYS:
            if key != "reading_ids":
                require_text(item[key], checks, context + " " + key)
        name = item["name"].strip().casefold()
        checks.require(name not in names, context + ": duplicate service name")
        names.add(name)
        parsed = public_https_url(item["docs_url"], checks, context + " documentation", allow_fragment=True)
        doc_identity = (parsed.netloc.lower(), parsed.path.rstrip("/"), parsed.query, parsed.fragment)
        checks.require(doc_identity not in documentation, context + ": duplicate documentation identity")
        documentation.add(doc_identity)
        public_https_url(item.get("source_url"), checks, context + " evidence source", allow_fragment=True)
        checks.require(item["auth_code"] in AUTH_CODES, context + ": unknown authentication code")
        checks.require(item["fit_code"] in FIT_CODES, context + ": unknown device-fit code")
        checks.require(item["evidence_code"] in EVIDENCE_CODES, context + ": unknown evidence code")
        if item["auth_code"] == "no_key_confirmed":
            checks.require(item["evidence_code"] == "provider_docs_reviewed",
                           context + ": anonymous access cannot be confirmed by a directory claim alone")
        checks.require(item.get("ready_preset") is False and item.get("device_tested") is False,
                       context + ": discovery records must not claim a verified or device-tested preset")
        reading_ids = item["reading_ids"]
        checks.require(isinstance(reading_ids, list) and all(isinstance(value, str) for value in reading_ids),
                       context + ": reading_ids must be a string array")
        checks.require(len(reading_ids) == len(set(reading_ids)), context + ": duplicate reading association")
        for reading_id in reading_ids:
            checks.require(reading_id in readings, context + ": reading association is unresolved")
            checks.require(reading_id not in associations, context + ": a reading has multiple service owners")
            associations[reading_id] = identifier
        runtime.append({key: item[key] for key in SERVICE_KEYS})
    checks.require(type(catalog.get("category_count")) is int
                   and catalog["category_count"] == len({item["category"] for item in services}),
                   "Recorded category count differs from service records")
    for key, field in (("auth_counts", "auth_code"), ("fit_counts", "fit_code"),
                       ("evidence_counts", "evidence_code")):
        checks.require(catalog.get(key) == dict(Counter(item[field] for item in services)),
                       "Recorded " + key + " differs from service records")
    mappings = catalog.get("reading_mappings")
    checks.require(isinstance(mappings, list) and len(mappings) == 100,
                   "Every original reading requires an explicit service or retained-legacy mapping")
    mapped = set()
    for mapping in mappings:
        checks.require(isinstance(mapping, dict), "Legacy reading mapping must be an object")
        reading_id, service_id = mapping.get("reading_id"), mapping.get("service_id")
        checks.require(reading_id in legacy_by_id and reading_id not in mapped,
                       "Legacy mapping has an unresolved or repeated reading")
        mapped.add(reading_id)
        checks.require(mapping.get("provider") == legacy_by_id[reading_id]["provider"],
                       "Legacy mapping provider differs from preserved reading attribution")
        if service_id is None:
            checks.require(mapping.get("status") == "legacy_retained" and reading_id not in associations,
                           "Unmapped original reading must be retained without a false service association")
        else:
            checks.require(service_id in ids and mapping.get("status") == "catalog_service"
                           and associations.get(reading_id) == service_id,
                           "Original reading-to-service mapping differs from runtime association")
    checks.require(mapped == set(legacy_by_id), "Original reading mapping is incomplete")
    for reading_id, profile in profile_by_id.items():
        checks.require(associations.get(reading_id) == profile.get("serviceId"),
                       "New reading must be associated with its documented service")
    checks.require(catalog.get("reading_profile_count") == len(readings),
                   "Total reading count differs from the original and new profiles")
    checks.require(catalog.get("mapped_reading_count") == len(associations),
                   "Mapped reading count differs from service associations")
    checks.require(catalog.get("legacy_reading_count") == len(readings) - len(associations),
                   "Retained-legacy reading count differs from service associations")
    checks.require(isinstance(catalog.get("source_frozen_sha256"), str)
                   and re.fullmatch(r"[0-9a-f]{64}", catalog["source_frozen_sha256"]),
                   "Frozen research snapshot identity is missing")
    return runtime, checks.count


def validate_profiles(document, catalog):
    checks = Checks()
    checks.require(isinstance(document, dict), "Reading profile root must be an object")
    checks.require(type(document.get("schema_version")) is int and document["schema_version"] == 1,
                   "Reading profile schema must be integer 1")
    profiles = document.get("profiles")
    checks.require(isinstance(profiles, list) and profiles, "At least one bounded reading profile is required")
    checks.require(type(document.get("count")) is int and document["count"] == len(profiles),
                   "Reading profile count differs from records")
    checks.require(document.get("source_service_catalog") == "docs/PUBLIC_API_SERVICES.json",
                   "Reading profile service-catalog reference is incorrect")
    services = {item["id"]: item for item in catalog["services"]}
    ids, choices, runtime = set(), set(), {}
    for number, item in enumerate(profiles, 1):
        context = "Reading profile " + str(number)
        checks.require(isinstance(item, dict) and all(key in item for key in PROFILE_KEYS),
                       context + ": runtime fields are incomplete")
        identifier = item["id"]
        checks.require(isinstance(identifier, str) and re.fullmatch(r"svc_[A-Za-z0-9_]+", identifier),
                       context + ": ID must be a namespaced JavaScript-safe identifier")
        checks.require(identifier not in ids, context + ": duplicate reading profile ID")
        ids.add(identifier)
        service_id = item["serviceId"]
        checks.require(isinstance(service_id, str) and service_id in services,
                       context + ": service association is unresolved")
        checks.require(item.get("deviceTested") is False,
                       context + ": desktop evidence cannot claim device verification")
        checks.require(item["locationBased"] is False,
                       context + ": new profiles require a fully resolved public example endpoint")
        for key in ("name", "category", "label", "url", "field", "hint", "docs", "provider"):
            require_text(item[key], checks, context + " " + key)
        checks.require(isinstance(item["unit"], str) and all(ord(char) >= 32 and ord(char) != 127 for char in item["unit"]),
                       context + ": unit must be text without controls")
        for key, bound in (("label", 27), ("url", 200), ("field", 80), ("unit", 15)):
            checks.require(len(item[key].encode("utf-8")) <= bound,
                           context + ": " + key + " exceeds the firmware byte limit")
        checks.require(re.fullmatch(r"[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*", item["field"]),
                       context + ": unsupported scalar field path")
        checks.require(type(item["interval"]) is int and 300 <= item["interval"] <= 86400,
                       context + ": interval must be whole seconds in the supported range")
        public_https_url(item["url"], checks, context + " endpoint")
        public_https_url(item["docs"], checks, context + " documentation", allow_fragment=True)
        choice = (item["url"], item["field"])
        checks.require(choice not in choices, context + ": duplicate new endpoint/field reading")
        choices.add(choice)
        options = {key: item[key] for key in ("label", "url", "field", "unit", "interval")}
        options["enabled"] = True
        checks.require(len(json.dumps(options, ensure_ascii=False, separators=(",", ":")).encode()) <= 512,
                       context + ": widget configuration exceeds the request bound")
        validate_evidence(item, checks, context)
        evidence = item["verification"]
        checks.require(evidence.get("tlsVerified") is True and evidence.get("redirectsFollowed") is False
                       and evidence.get("authenticationUsed") is False
                       and evidence.get("scalarPathValidated") is True,
                       context + ": verified TLS, first response, anonymous access and scalar-path evidence required")
        checks.require(isinstance(evidence.get("responseSha256"), str)
                       and re.fullmatch(r"[0-9a-f]{64}", evidence["responseSha256"]),
                       context + ": response body hash is required")
        length = evidence.get("scalarBytes")
        checks.require(type(length) is int and 0 < length <= 47,
                       context + ": selected scalar byte length must fit the device display")
        runtime[identifier] = {key: item[key] for key in PROFILE_KEYS}
    return runtime, checks.count


def extract_runtime(include):
    checks = Checks()
    checks.require("</script" not in include.lower(), "Generated include can terminate its browser script")
    match = re.search(r'R"([A-Za-z0-9_]+)\((.*?)\)\1"', include, re.S)
    checks.require(match is not None, "Generated include needs one C++ raw string")
    delimiter, script = match.group(1), match.group(2)
    checks.require(len(re.findall(r'R"[A-Za-z0-9_]+\(', include)) == 1,
                   "Generated include must have exactly one C++ raw string")
    checks.require(")" + delimiter + '"' not in script,
                   "Generated data can terminate its C++ raw string")
    outside = include[:match.start()] + include[match.end():]
    outside = re.sub(r"/\*.*?\*/|//[^\n]*", "", outside, flags=re.S)
    checks.require(not outside.strip(), "Generated include contains unexpected C++ outside its raw string")
    begin, end = "/* AURA_API_SERVICES_BEGIN */", "/* AURA_API_SERVICES_END */"
    script = script.strip()
    checks.require(script.count(begin) == 1 and script.count(end) == 1
                   and script.startswith(begin) and script.endswith(end),
                   "Generated browser data needs one ordered service-marker pair")
    script = script[len(begin):-len(end)]
    checks.require("<" not in script and "\u2028" not in script and "\u2029" not in script,
                   "Generated service data must escape HTML and script line delimiters")
    cursor, payload = 0, {}
    for name in ("API_SERVICES", "SERVICE_READINGS"):
        declaration = re.match(r"\s*const\s+" + name + r"\s*=\s*", script[cursor:])
        checks.require(declaration is not None, "Generated include must declare " + name + " in order")
        cursor += declaration.end()
        try:
            value, consumed = json_decoder().raw_decode(script[cursor:])
        except json.JSONDecodeError as error:
            raise CatalogError("Generated " + name + " must contain strict JSON data") from error
        cursor += consumed
        ending = re.match(r"\s*;", script[cursor:])
        checks.require(ending is not None, "Generated declaration must end after its JSON value")
        cursor += ending.end()
        payload[name] = value
    checks.require(not script[cursor:].strip(), "Generated include contains extra browser code")
    checks.require(isinstance(payload["API_SERVICES"], list), "API_SERVICES must be an array")
    checks.require(isinstance(payload["SERVICE_READINGS"], dict), "SERVICE_READINGS must be an object")
    return payload, checks.count


def validate_licenses(catalog):
    checks = Checks()
    sources = catalog.get("source_directories")
    checks.require(isinstance(sources, list) and len(sources) == 2,
                   "Both original discovery directory sources must be attributed")
    for source in sources:
        checks.require(isinstance(source, dict) and source.get("license") == "MIT",
                       "Discovery source license provenance is incomplete")
        public_https_url(source.get("url"), checks, "Discovery source", allow_fragment=True)
        require_text(source.get("name"), checks, "Discovery source name")
        checks.require(re.fullmatch(r"[0-9a-f]{64}", str(source.get("snapshot_sha256", ""))),
                       "Discovery README snapshot hash is incomplete")
        filename = source.get("license_file")
        checks.require(isinstance(filename, str) and filename.startswith("third_party/catalog-discovery/")
                       and Path(filename).parent.as_posix() == "third_party/catalog-discovery",
                       "Discovery license must name an explicitly retained catalog notice")
        path = ROOT / filename
        checks.require(path.is_file() and not path.is_symlink(), "Discovery license text is missing")
        notice = path.read_text()
        checks.require("MIT License" in notice and "Copyright (c)" in notice
                       and "The above copyright notice and this permission notice" in notice
                       and "SOFTWARE IS PROVIDED" in notice,
                       "Discovery license must retain the complete original notice")
        checks.require(source.get("license_sha256") == hashlib.sha256(path.read_bytes()).hexdigest(),
                       "Discovery license bytes differ from recorded provenance")
    provenance = load_json(ROOT / "third_party/catalog-discovery/PROVENANCE.json")
    checks.require(provenance.get("schema_version") == 1 and provenance.get("sources") == sources,
                   "Retained license provenance differs from the canonical discovery sources")
    return checks.count


def check_source(catalog, profiles, legacy, include):
    expected_profiles, count = validate_profiles(profiles, catalog)
    expected_services, additional = validate_services(catalog, legacy, profiles)
    count += additional
    actual, additional = extract_runtime(include)
    count += additional
    if actual["API_SERVICES"] != expected_services:
        raise CatalogError("Embedded service metadata differs from the 500 canonical records")
    if actual["SERVICE_READINGS"] != expected_profiles:
        raise CatalogError("Embedded reading profiles differ from the canonical bounded records")
    return count + 2


def backend_check(profiles, compiler):
    """Exercise new profile configurations through actual production functions."""
    from test_widgets import HOST_PREFIX, extract_function
    backend = (ROOT / "firmware/AuraDesk/app_service.cpp").read_text()
    web = (ROOT / "firmware/AuraDesk/web_service.cpp").read_text()
    functions = [extract_function(web, name) for name in ("publicApiUrl", "widgetHandler")]
    for name in ("publicWidgetUrl", "validWidgetPath", "validateWidgetOptions", "configureWidget",
                 "app_validate_widget_config"):
        functions.append(extract_function(backend, name))
    tests = [r'''unsigned assertions=0;
void check(bool valid,const char *name){assertions++;if(!valid){std::fprintf(stderr,"FAIL: %s\n",name);std::exit(1);}}
int main(){''']
    for profile in profiles["profiles"]:
        options = {key: profile[key] for key in ("label", "url", "field", "unit", "interval")}
        options["enabled"] = True
        encoded = json.dumps(options, ensure_ascii=False, separators=(",", ":"))
        # A quoted JSON string avoids C++ raw delimiter injection in this host
        # harness. Byte-accurate UTF-8 is retained by the compiler's source file.
        literal = json.dumps(encoded, ensure_ascii=False)
        for slot in (0, 1):
            tests.append('{const char *encoded=' + literal + ';char problem[96]={};'
                         'check(app_validate_widget_config(encoded,problem,sizeof(problem)),"New profile fits production backend bounds");'
                         'JsonDocument request;check(!deserializeJson(request,encoded),"New profile configuration parses");'
                         'request["index"]=' + str(slot) + ';httpd_req_t r;serializeJson(request,r.body);'
                         'unsigned previous=dispatchCount;widgetHandler(&r);'
                         'check(r.status==202&&dispatchCount==previous+1,"New profile is accepted by production HTTP handler");'
                         'check(dispatchedSlot=="' + str(slot) + '","New profile dispatch selects the requested slot");'
                         'check(configureWidget(' + str(slot) + ',encoded),"New profile persists in requested production slot");}')
    tests.append(r'''std::printf("PASS: %u new-profile production C++ assertions (offline platform stubs; no device or provider traffic)\n",assertions);}''')
    with tempfile.TemporaryDirectory(prefix="aura-services-host-") as directory:
        source, binary = Path(directory) / "services.cpp", Path(directory) / "services"
        source.write_text(HOST_PREFIX + "\n\n".join(functions) + "\n".join(tests))
        source.chmod(0o600)
        result = subprocess.run([compiler, "-std=c++17", "-O1", "-Wall", "-Wextra",
                                 "-I" + str(ROOT / ".toolchains/arduino/user/libraries/ArduinoJson/src"),
                                 "-I" + str(ROOT / "firmware/AuraDesk"), str(source), "-o", str(binary)],
                                capture_output=True, text=True)
        if result.returncode:
            raise CatalogError((result.stdout + result.stderr).replace(str(ROOT), "<workspace>")
                               .replace(directory, "<temporary>"))
        result = subprocess.run([str(binary)], capture_output=True, text=True)
        if result.returncode:
            raise CatalogError(result.stderr or "New-profile production backend checks failed")
        print(result.stdout, end="")


def self_test(catalog, profiles, legacy, include):
    """Mutate real contracts to prove that misleading/unsafe data is rejected."""
    assertions = 0
    def reject(c= catalog, p= profiles, l= legacy, i= include):
        nonlocal assertions
        try:
            check_source(c, p, l, i)
        except (CatalogError, TypeError, KeyError):
            assertions += 1
            return
        raise CatalogError("Checker self-test accepted a malformed catalog fixture")
    for mutate in (
        lambda d: d.update(count=499),
        lambda d: d["services"].pop(),
        lambda d: d["services"][1].update(id=d["services"][0]["id"]),
        lambda d: d["services"][1].update(name=d["services"][0]["name"]),
        lambda d: d["services"][0].update(docs_url="javascript:alert(1)"),
        lambda d: d["services"][0].update(docs_url="https://u:p@example.org/docs"),
        lambda d: d["services"][0].update(source_url="https://127.0.0.1/docs"),
        lambda d: d["services"][0].update(ready_preset=True),
        lambda d: d["services"][0].update(device_tested=True),
        lambda d: d["services"][0].update(reading_ids=["unresolved_reading"]),
        lambda d: d["services"][0].update(auth_code="no_key_confirmed", evidence_code="directory_only"),
        lambda d: d.update(category_count=499),
        lambda d: d.update(auth_counts={}),
        lambda d: d["reading_mappings"].pop(),
    ):
        changed = copy.deepcopy(catalog); mutate(changed); reject(c=changed)
    for mutate in (
        lambda d: d.update(count=0),
        lambda d: d["profiles"][0].update(id="bitcoin"),
        lambda d: d["profiles"][0].update(serviceId="unknown-service"),
        lambda d: d["profiles"][0].update(url="https://example.org/data?api_key=fixture"),
        lambda d: d["profiles"][0].update(url="http://example.org/data"),
        lambda d: d["profiles"][0].update(label="é" * 14),
        lambda d: d["profiles"][0].update(field="current..value"),
        lambda d: d["profiles"][0].update(interval=299),
        lambda d: d["profiles"][0].update(deviceTested=True),
        lambda d: d["profiles"][0]["verification"].update(httpStatus=302),
        lambda d: d["profiles"][0]["verification"].update(bytes=32769),
        lambda d: d["profiles"][0]["verification"].update(scalarBytes=48),
        lambda d: d["profiles"][0]["verification"].update(tlsVerified=False),
        lambda d: d["profiles"][0]["verification"].update(authenticationUsed=True),
        lambda d: d["profiles"][0]["verification"].update(redirectsFollowed=True),
        lambda d: d["profiles"][0]["verification"].update(responseSha256="missing"),
    ):
        changed = copy.deepcopy(profiles); mutate(changed); reject(p=changed)
    for injected in (include + "\nalert(1);", include.replace("const API_SERVICES=", "const OTHER="),
                     include + "\n</ScRiPt>", include.replace("const SERVICE_READINGS=", "alert(1);const SERVICE_READINGS="),
                     include.replace('"Amazing Endemic Species"', '"<img src=x onerror=alert(1)>"', 1)):
        reject(i=injected)
    for invalid in ('{"a":1,"a":2}', '{"a":NaN}', '{}{}'):
        try:
            strict_json(invalid)
        except CatalogError:
            assertions += 1
        else:
            raise CatalogError("Strict JSON self-test accepted malformed data")
    print("PASS: " + str(assertions) + " malformed evidence/link/mapping/source fixtures rejected")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--backend", action="store_true", help="Run new profiles through actual production C++ functions")
    parser.add_argument("--compiler", default="clang++")
    args = parser.parse_args()
    catalog = load_json(ROOT / "docs/PUBLIC_API_SERVICES.json")
    profiles = load_json(ROOT / "docs/PUBLIC_API_SERVICE_READINGS.json")
    legacy = load_json(ROOT / "docs/PUBLIC_API_CATALOG.json")
    include = (ROOT / "firmware/AuraDesk/api_services.js.inc").read_text()
    count = check_source(catalog, profiles, legacy, include) + validate_licenses(catalog)
    print("PASS: " + str(count) + " service/evidence/source checks; exactly 500 services and "
          + str(profiles["count"]) + " bounded profiles (offline validation)")
    if args.self_test:
        self_test(catalog, profiles, legacy, include)
    if args.backend:
        backend_check(profiles, args.compiler)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (CatalogError, OSError, KeyError, TypeError, RuntimeError) as error:
        print("FAIL: " + str(error), file=sys.stderr)
        raise SystemExit(1)
