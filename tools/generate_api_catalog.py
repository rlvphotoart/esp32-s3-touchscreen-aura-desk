#!/usr/bin/env python3
"""Embed the reviewed public API catalog; --check refuses stale generated data.

No network or device access. The independent catalog checker enforces schema,
firmware limits and verification records before this generator is used.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEGIN = "/* AURA_API_CATALOG_BEGIN */"
END = "/* AURA_API_CATALOG_END */"
RUNTIME_KEYS = ("name", "category", "label", "url", "field", "unit", "interval",
                "hint", "docs", "provider", "locationBased")


def expected_block():
    document = json.loads((ROOT / "docs/PUBLIC_API_CATALOG.json").read_text())
    presets = document["presets"]
    if document["count"] != 100 or len(presets) != 100:
        raise ValueError("Exactly 100 reviewed public API presets are required")
    catalog = {item["id"]: {key: item[key] for key in RUNTIME_KEYS} for item in presets}
    if len(catalog) != 100:
        raise ValueError("Catalog identifiers must be unique")
    compact = json.dumps(catalog, ensure_ascii=False, separators=(",", ":"))
    # The data lives inside a C++ raw string and a browser script. Refuse data
    # that could terminate either container, even though it is a reviewed file.
    if ")AURA\"" in compact or "</script" in compact.lower():
        raise ValueError("Catalog text could terminate its source container")
    return BEGIN + "\nconst WIDGET_EXAMPLES=" + compact + ";\n" + END


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = ROOT / "firmware/AuraDesk/web_service.cpp"
    source = path.read_text()
    if source.count(BEGIN) != 1 or source.count(END) != 1:
        parser.error("Expected one catalog generation region")
    start = source.index(BEGIN)
    stop = source.index(END, start) + len(END)
    block = expected_block()
    if args.check:
        if source[start:stop] != block:
            parser.error("Embedded API catalog is stale; run this generator")
        print("PASS: exactly 100 embedded presets match the reviewed catalog")
    elif source[start:stop] != block:
        path.write_text(source[:start] + block + source[stop:])
        print("Embedded 100 reviewed public API presets")
    else:
        print("Catalog already current")


if __name__ == "__main__":
    main()
