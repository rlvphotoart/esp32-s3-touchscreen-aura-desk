#!/usr/bin/env python3
"""Check the public preset catalog and its exact embedded browser payload offline.

These checks validate recorded endpoint evidence, firmware input limits, and
source/catalog agreement. They do not make HTTP requests or prove future API
availability. Use --self-test to exercise the checker with synthetic fixtures.
"""

import argparse
import copy
import ipaddress
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlsplit


ROOT = Path(__file__).resolve().parent.parent
RUNTIME_KEYS = (
    "name", "category", "label", "url", "field", "unit", "interval", "hint",
    "docs", "provider", "locationBased",
)
BEGIN = "/* AURA_API_CATALOG_BEGIN */"
END = "/* AURA_API_CATALOG_END */"
SCALAR_TYPES = {
    "number": "number", "integer": "number", "int": "number", "float": "number",
    "double": "number", "string": "string", "boolean": "boolean", "bool": "boolean",
}
AUTH_QUERY_KEYS = {
    "apikey", "key", "token", "accesstoken", "authtoken", "auth", "authorization",
    "password", "passwd", "secret", "clientsecret", "subscriptionkey", "bearer",
}


class CatalogError(ValueError):
    """An actionable catalog-contract failure."""


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise CatalogError("JSON contains a duplicate object key")
        result[key] = value
    return result


def invalid_constant(_value):
    raise CatalogError("JSON contains a non-finite numeric constant")


def json_decoder():
    return json.JSONDecoder(object_pairs_hook=unique_pairs, parse_constant=invalid_constant)


class Checks:
    def __init__(self):
        self.count = 0

    def require(self, condition, message):
        self.count += 1
        if not condition:
            raise CatalogError(message)


def clean_text(value):
    return isinstance(value, str) and bool(value.strip()) and all(ord(c) >= 32 for c in value)


def public_https_url(value, checks, context, allow_fragment=False):
    checks.require(isinstance(value, str), context + ": URL must be text")
    checks.require(all(32 < ord(c) < 127 for c in value) and "\\" not in value,
                   context + ": URL must use printable ASCII without backslashes")
    try:
        parsed = urlsplit(value)
        host = parsed.hostname
        port = parsed.port
    except ValueError as exc:
        raise CatalogError(context + ": malformed URL authority") from exc
    checks.require(parsed.scheme == "https" and bool(host) and port in (None, 443),
                   context + ": public HTTPS on port 443 is required")
    checks.require(parsed.username is None and parsed.password is None and "@" not in parsed.netloc,
                   context + ": credentials are unsupported")
    checks.require(allow_fragment or not parsed.fragment, context + ": URL fragments are unsupported")
    checks.require("%" not in host and not host.endswith(".") and "." in host,
                   context + ": invalid public hostname")
    lowered = host.lower()
    checks.require(lowered != "localhost" and not lowered.endswith(
        (".localhost", ".local", ".internal", ".lan", ".home")),
        context + ": local hostnames are unsupported")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    checks.require(address is None or address.is_global, context + ": private IP addresses are unsupported")
    checks.require(address is None or address.version == 4, context + ": literal IPv6 is unsupported")
    for key, val in parse_qsl(parsed.query, keep_blank_values=True):
        normalized = re.sub(r"[^a-z0-9]", "", key.lower())
        checks.require(normalized not in AUTH_QUERY_KEYS,
                       context + ": API keys or authentication query parameters are unsupported")
        checks.require(all(ord(c) >= 32 for c in key + val),
                       context + ": encoded control characters are unsupported")
    checks.require(all(ord(c) >= 32 for c in unquote(parsed.path)),
                   context + ": encoded path controls are unsupported")
    return parsed


def expand_urls(item, checks, context):
    url = item["url"]
    checks.require(isinstance(item["locationBased"], bool), context + ": locationBased must be a boolean")
    placeholders = re.findall(r"\{([^{}]+)\}", url)
    checks.require("{" not in re.sub(r"\{[^{}]+\}", "", url)
                   and "}" not in re.sub(r"\{[^{}]+\}", "", url),
                   context + ": malformed coordinate template")
    if item["locationBased"]:
        checks.require(sorted(placeholders) == ["latitude", "longitude"],
                       context + ": a saved-city preset needs each supported coordinate template once")
        return [url.replace("{latitude}", lat).replace("{longitude}", lon)
                for lat, lon in (("-90.0000", "-180.0000"), ("90.0000", "180.0000"), ("0.0000", "0.0000"))]
    checks.require(not placeholders, context + ": fixed presets cannot contain coordinate templates")
    return [url]


def validate_evidence(item, checks, context):
    evidence = item.get("verification")
    checks.require(isinstance(evidence, dict), context + ": verification metadata is required")
    checks.require(type(evidence.get("httpStatus")) is int and evidence["httpStatus"] == 200,
                   context + ": recorded first HTTP response must be 200")
    size = evidence.get("bytes")
    checks.require(type(size) is int and 0 < size <= 32768,
                   context + ": recorded body must fit the 32768-byte device limit")
    checks.require(isinstance(evidence.get("scalarType"), str), context + ": scalar type must be text")
    scalar_type = SCALAR_TYPES.get(evidence["scalarType"])
    checks.require(scalar_type is not None, context + ": evidence must identify a supported scalar type")
    timestamp = evidence.get("checkedAt")
    checks.require(isinstance(timestamp, str), context + ": UTC check time is required")
    try:
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CatalogError(context + ": check time must be ISO 8601") from exc
    checks.require(parsed.tzinfo is not None and parsed.utcoffset().total_seconds() == 0,
                   context + ": check time must be in UTC")
    for key in ("redirected", "followedRedirects"):
        if key in evidence:
            checks.require(evidence[key] is False, context + ": redirected responses cannot qualify")
    if "redirectCount" in evidence:
        checks.require(type(evidence["redirectCount"]) is int and evidence["redirectCount"] == 0,
                       context + ": redirected responses cannot qualify")
    if "firstHttpStatus" in evidence:
        checks.require(type(evidence["firstHttpStatus"]) is int and evidence["firstHttpStatus"] == 200,
                       context + ": first HTTP response cannot be a redirect")
    if "requestedUrl" in evidence and "finalUrl" in evidence:
        checks.require(evidence["requestedUrl"] == evidence["finalUrl"],
                       context + ": verification URL changed through a redirect")
    for key in ("valueLength", "valueBytes", "stringBytes", "stringLength"):
        if key in evidence:
            length = evidence[key]
            checks.require(type(length) is int and 0 < length <= 47,
                           context + ": recorded scalar length exceeds the 47-byte display limit")
    if "value" in evidence:
        value = evidence["value"]
        actual_type = ("boolean" if isinstance(value, bool) else "number" if type(value) in (int, float)
                       else "string" if isinstance(value, str) else None)
        checks.require(actual_type == scalar_type, context + ": recorded value is null, composite, or mistyped")
        if actual_type == "string":
            checks.require(clean_text(value) and len(value.encode("utf-8")) <= 47,
                           context + ": recorded text cannot fit the display")
        elif actual_type == "number":
            numeric_text = json.dumps(value)
            checks.require(len(numeric_text.encode("utf-8")) <= 47 and math.isfinite(value),
                           context + ": recorded number cannot fit the display")


def validate_catalog(catalog):
    checks = Checks()
    checks.require(isinstance(catalog, dict), "Catalog root must be an object")
    checks.require(type(catalog.get("schema_version")) is int and catalog["schema_version"] == 1,
                   "Catalog schema_version must be integer 1")
    checks.require(type(catalog.get("count")) is int and catalog["count"] == 100,
                   "Catalog count must be integer 100")
    items = catalog.get("presets")
    checks.require(isinstance(items, list) and len(items) == 100, "Catalog must contain exactly 100 presets")
    ids, choices, runtime = set(), set(), {}
    for index, item in enumerate(items):
        context = "Preset " + str(index + 1)
        checks.require(isinstance(item, dict), context + ": preset must be an object")
        identifier = item.get("id")
        checks.require(isinstance(identifier, str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", identifier) is not None,
                       context + ": identifier must be an ASCII JavaScript-safe name")
        checks.require(identifier not in ("__proto__", "constructor", "prototype"), context + ": unsafe object identifier")
        checks.require(identifier not in ids, context + ": duplicate identifier")
        ids.add(identifier)
        checks.require(all(key in item for key in RUNTIME_KEYS), context + ": runtime fields are incomplete")
        for key in ("name", "category", "label", "url", "field", "hint", "docs", "provider"):
            checks.require(clean_text(item[key]), context + ": " + key + " must be nonempty text without controls")
        checks.require(isinstance(item["unit"], str) and all(ord(c) >= 32 for c in item["unit"]),
                       context + ": unit must be text without controls")
        for key, maximum in (("label", 27), ("unit", 15), ("url", 200), ("field", 80)):
            checks.require(len(item[key].encode("utf-8")) <= maximum,
                           context + ": " + key + " exceeds the firmware byte limit")
        checks.require(re.fullmatch(r"[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*", item["field"]) is not None,
                       context + ": field must be a supported ASCII dot path")
        checks.require(type(item["interval"]) is int and 300 <= item["interval"] <= 86400,
                       context + ": refresh interval must be a whole number from 300 to 86400 seconds")
        choice = (item["url"], item["field"])
        checks.require(choice not in choices, context + ": duplicate endpoint and field data choice")
        choices.add(choice)
        public_https_url(item["docs"], checks, context + " documentation", allow_fragment=True)
        for url in expand_urls(item, checks, context):
            checks.require(len(url.encode("utf-8")) <= 200,
                           context + ": expanded saved-city URL exceeds the firmware limit")
            public_https_url(url, checks, context)
            options = {key: item[key] for key in ("label", "field", "unit", "interval")}
            options.update(url=url, enabled=True)
            checks.require(len(json.dumps(options, ensure_ascii=False, separators=(",", ":")).encode("utf-8")) <= 512,
                           context + ": generated widget configuration exceeds the 512-byte limit")
        validate_evidence(item, checks, context)
        runtime[identifier] = {key: item[key] for key in RUNTIME_KEYS}
    return runtime, checks.count


def extract_runtime(source):
    if source.count(BEGIN) != 1 or source.count(END) != 1:
        raise CatalogError("Embedded source needs exactly one pair of catalog markers")
    start = source.index(BEGIN) + len(BEGIN)
    finish = source.index(END)
    if finish <= start:
        raise CatalogError("Embedded catalog markers are out of order")
    block = source[start:finish].strip()
    match = re.match(r"const\s+WIDGET_EXAMPLES\s*=\s*", block)
    if not match:
        raise CatalogError("Catalog block must declare const WIDGET_EXAMPLES")
    try:
        payload, end = json_decoder().raw_decode(block[match.end():])
    except json.JSONDecodeError as exc:
        raise CatalogError("Embedded catalog must contain strict JSON") from exc
    if block[match.end() + end:].strip() != ";":
        raise CatalogError("Catalog block contains extra code after its JSON declaration")
    if not isinstance(payload, dict):
        raise CatalogError("Embedded WIDGET_EXAMPLES must be an object keyed by preset ID")
    return payload


def check_source(catalog, source):
    expected, count = validate_catalog(catalog)
    actual = extract_runtime(source)
    if json.dumps(actual, ensure_ascii=False, sort_keys=True) != json.dumps(expected, ensure_ascii=False, sort_keys=True):
        if set(actual) != set(expected):
            raise CatalogError("Embedded catalog identifiers differ from the 100 canonical presets")
        raise CatalogError("Embedded catalog values differ from canonical runtime fields")
    return count + 1


def self_test():
    def fixture():
        presets = [dict(id="example_" + str(i), name="Synthetic choice " + str(i), category="Fixtures",
                        label="Example " + str(i), url="https://example.org/data/" + str(i) + ".json",
                        field="data.0.value", unit="", interval=1800, hint="Offline synthetic scalar fixture.",
                        docs="https://example.org/docs", provider="Synthetic", locationBased=False,
                        verification=dict(httpStatus=200, bytes=123, scalarType="number", checkedAt="2026-10-03T18:00:00Z"))
                   for i in range(100)]
        presets[0].update(url="https://example.org/weather?latitude={latitude}&longitude={longitude}", locationBased=True)
        return dict(schema_version=1, count=100, presets=presets)

    def source(catalog):
        runtime = {item["id"]: {key: item[key] for key in RUNTIME_KEYS} for item in catalog["presets"]}
        return BEGIN + "\nconst WIDGET_EXAMPLES=" + json.dumps(runtime, separators=(",", ":")) + ";\n" + END

    good = fixture()
    assertions = check_source(good, source(good))
    mutations = [
        lambda c: c.update(count=True),
        lambda c: c.update(schema_version="1"),
        lambda c: c["presets"].pop(),
        lambda c: c["presets"][1].update(id=c["presets"][0]["id"]),
        lambda c: c["presets"][1].update(id="constructor"),
        lambda c: c["presets"][2].update(url=c["presets"][1]["url"], field=c["presets"][1]["field"]),
        lambda c: c["presets"][1].update(url="http://example.org/data.json"),
        lambda c: c["presets"][1].update(url="https://user:password@example.org/data.json"),
        lambda c: c["presets"][1].update(url="https://example.org:444/data.json"),
        lambda c: c["presets"][1].update(url="https://192.168.1.1/data.json"),
        lambda c: c["presets"][1].update(url="https://device.local/data.json"),
        lambda c: c["presets"][1].update(url="https://example.org/data.json?api%5Fkey=fixture"),
        lambda c: c["presets"][1].update(url="https://example.org/data.json?token=fixture"),
        lambda c: c["presets"][1].update(url="https://example.org/data.json#value"),
        lambda c: c["presets"][1].update(url="https://example.org/data.json?name=%0A"),
        lambda c: c["presets"][1].update(label="é" * 14),
        lambda c: c["presets"][1].update(unit="µ" * 8),
        lambda c: c["presets"][1].update(field="a" * 81),
        lambda c: c["presets"][1].update(field="data..value"),
        lambda c: c["presets"][1].update(field="data[0].value"),
        lambda c: c["presets"][1].update(interval=1800.0),
        lambda c: c["presets"][1].update(interval=True),
        lambda c: c["presets"][1].update(interval=299),
        lambda c: c["presets"][1].update(interval=86401),
        lambda c: c["presets"][0].update(url="https://example.org/?latitude={latitude}"),
        lambda c: c["presets"][0].update(url="https://example.org/?latitude={latitude}&longitude={unknown}"),
        lambda c: c["presets"][0].update(locationBased="true"),
        lambda c: c["presets"][0].update(locationBased=False),
        lambda c: c["presets"][1].update(docs="http://example.org/docs"),
        lambda c: c["presets"][1].update(hint=""),
        lambda c: c["presets"][1]["verification"].update(httpStatus=302),
        lambda c: c["presets"][1]["verification"].update(bytes=32769),
        lambda c: c["presets"][1]["verification"].update(bytes=True),
        lambda c: c["presets"][1]["verification"].update(scalarType="object"),
        lambda c: c["presets"][1]["verification"].update(scalarType=[]),
        lambda c: c["presets"][1]["verification"].update(checkedAt="2026-10-03T18:00:00"),
        lambda c: c["presets"][1]["verification"].update(redirected=True),
        lambda c: c["presets"][1]["verification"].update(firstHttpStatus=301),
        lambda c: c["presets"][1]["verification"].update(redirectCount=1),
        lambda c: c["presets"][1]["verification"].update(requestedUrl="https://example.org/one", finalUrl="https://example.org/two"),
        lambda c: c["presets"][1]["verification"].update(valueLength=48),
        lambda c: c["presets"][1]["verification"].update(value=None),
        lambda c: c["presets"][1]["verification"].update(value=float("inf")),
        lambda c: c["presets"][1]["verification"].update(scalarType="string", value="x" * 48),
        lambda c: c["presets"][1]["verification"].update(scalarType="string", value="control\n"),
    ]
    for mutate in mutations:
        bad = copy.deepcopy(good)
        mutate(bad)
        try:
            check_source(bad, source(bad))
        except CatalogError:
            assertions += 1
        else:
            raise CatalogError("Self-test did not reject a deliberately invalid catalog")
    altered = source(good).replace('"label":"Example 1"', '"label":"Stale label"', 1)
    bad_sources = (
        altered, source(good).replace(END, ""),
        source(good).replace(";\n" + END, ";\nWIDGET_EXAMPLES={};\n" + END),
        source(good).replace('"interval":1800', '"interval":1800.0', 1),
        source(good).replace('"locationBased":true', '"locationBased":1', 1),
        source(good).replace('"label":"Example 1"', '"label":"Example 1","label":"Example 1"', 1),
        source(good).replace('"interval":1800', '"interval":NaN', 1),
    )
    for bad_source in bad_sources:
        try:
            check_source(good, bad_source)
        except CatalogError:
            assertions += 1
        else:
            raise CatalogError("Self-test did not reject generated runtime drift")
    for value, scalar_type in ((0, "number"), (False, "bool"), ("0", "string"), ("é" * 23 + "x", "string")):
        accepted = copy.deepcopy(good)
        accepted["presets"][1]["verification"].update(value=value, scalarType=scalar_type)
        check_source(accepted, source(accepted))
        assertions += 1
    anchored_docs = copy.deepcopy(good)
    anchored_docs["presets"][1]["docs"] = "https://example.org/docs#scalar-fields"
    check_source(anchored_docs, source(anchored_docs))
    assertions += 1
    return assertions, len(mutations) + len(bad_sources)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=ROOT / "docs/PUBLIC_API_CATALOG.json")
    parser.add_argument("--source", type=Path, default=ROOT / "firmware/AuraDesk/web_service.cpp")
    parser.add_argument("--self-test", action="store_true", help="Use synthetic fixtures; do not read repository catalog files")
    args = parser.parse_args()
    try:
        if args.self_test:
            assertions, rejected = self_test()
            print(f"PASS: catalog checker self-test; {rejected} invalid/drift cases rejected and valid scalar boundaries accepted ({assertions} assertions)")
        else:
            count = check_source(json_decoder().decode(args.catalog.read_text()), args.source.read_text())
            print(f"PASS: exactly 100 unique public API data choices; recorded evidence and firmware limits valid; embedded catalog matches ({count} offline assertions)")
    except (CatalogError, OSError, json.JSONDecodeError, UnicodeError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
