#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLI="$ROOT/.toolchains/bin/arduino-cli"
CONFIG="$ROOT/.toolchains/arduino-cli.yaml"
SKETCH="$ROOT/firmware/AuraDesk"
BUILD="$ROOT/build/AuraDesk"
VERSION="$(sed -n 's/^#define AURA_VERSION "\([0-9.]*\)"$/\1/p' "$SKETCH/firmware_version.h")"
if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo 'Invalid firmware version header.' >&2
    exit 1
fi
OUTPUT="$ROOT/releases/aura-desk-$VERSION"
"$ROOT/.venv/bin/python" "$ROOT/tools/generate_api_catalog.py" --check
"$ROOT/.venv/bin/python" "$ROOT/tools/test_api_catalog.py"
"$ROOT/.venv/bin/python" "$ROOT/tools/generate_api_services.py" --check
"$ROOT/.venv/bin/python" "$ROOT/tools/test_api_services.py"
"$ROOT/.venv/bin/python" "$ROOT/tools/test_https_tls_policy.py"
FQBN='esp32:esp32:esp32s3:PSRAM=opi,FlashMode=dio,FlashSize=16M,CPUFreq=240,LoopCore=1,EventsCore=1,USBMode=hwcdc,CDCOnBoot=default,MSCOnBoot=default,DFUOnBoot=default,UploadMode=default,PartitionScheme=custom,UploadSpeed=115200,DebugLevel=none,EraseFlash=none'
if [[ ! -x "$CLI" || ! -f "$CONFIG" ]]; then
    echo 'Pinned local Arduino toolchain missing. See docs/FIRMWARE_BUILD.md.' >&2
    exit 1
fi
if [[ ! -f "$SKETCH/AuraDesk.ino" || ! -f "$SKETCH/partitions.csv" || ! -f "$SKETCH/esp_panel_board_supported_conf.h" ]]; then
    echo 'Firmware source or board configuration is incomplete.' >&2
    exit 1
fi
SDKCONFIG="$ROOT/.toolchains/arduino/data/packages/esp32/tools/esp32-arduino-libs/idf-release_v5.3-cfea4f7c-v1/esp32s3/dio_opi/include/sdkconfig.h"
if [[ ! -f "$SDKCONFIG" ]] || ! /usr/bin/grep -q '^#define CONFIG_SPIRAM_XIP_FROM_PSRAM 1$' "$SDKCONFIG"; then
    echo 'Matching high-performance SDK with XIP from PSRAM is required.' >&2
    exit 1
fi
PYTHON="$ROOT/.venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then
    echo 'Pinned inspection Python/esptool environment missing.' >&2
    exit 1
fi
mkdir -p "$BUILD" "$OUTPUT"
"$CLI" --config-file "$CONFIG" compile --jobs 4 \
    --fqbn "$FQBN" \
    --build-property 'compiler.optimization_flags=-O2' \
    --build-property "compiler.c.extra_flags=-DLV_CONF_INCLUDE_SIMPLE -DLV_LVGL_H_INCLUDE_SIMPLE -ffile-prefix-map=$ROOT=. -fdebug-prefix-map=$ROOT=." \
    --build-property "compiler.cpp.extra_flags=-DLV_CONF_INCLUDE_SIMPLE -DLV_LVGL_H_INCLUDE_SIMPLE -DNETWORK_EVENTS_MUTEX -ffile-prefix-map=$ROOT=. -fdebug-prefix-map=$ROOT=." \
    --build-path "$BUILD" --output-dir "$OUTPUT" "$SKETCH"
# Arduino3.1.1 hardcodes app0x10000 and boot_app0xE000 in its merged export.
# Our custom layout starts ota_0 at0x20000. Replace that export explicitly.
"$PYTHON" - "$ROOT" "$BUILD" "$OUTPUT" <<'PYCODE'
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys
from esptool.bin_image import ESP32S3FirmwareImage
root,build,output=map(Path,sys.argv[1:])
flash_size=16*1024*1024
for directory in (build,output):
    (directory/'AuraDesk.ino.merged.bin').unlink(missing_ok=True)
spec=importlib.util.spec_from_file_location('aura_partition',root/'tools/vendor/gen_esp32part.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
module.offset_part_table=0x8000
binary_table=output/'AuraDesk.ino.partitions.bin'
table=module.PartitionTable.from_binary(binary_table.read_bytes())
table.verify();table.verify_size_fits(flash_size)
source_table=module.PartitionTable.from_csv((root/'firmware/AuraDesk/partitions.csv').read_text())
source_table.verify();source_table.verify_size_fits(flash_size)
if table.to_binary()!=source_table.to_binary():
    raise SystemExit('Compiled partition table differs from source CSV')
ota0=table.find_by_name('ota_0');ota1=table.find_by_name('ota_1')
if not ota0 or not ota1 or ota0.type!=0 or ota1.type!=0 or ota0.offset!=0x20000:
    raise SystemExit('Expected dual OTA layout with first app at0x20000')
regions=[(0,output/'AuraDesk.ino.bootloader.bin'),(0x8000,binary_table),(ota0.offset,output/'AuraDesk.ino.bin')]
previous_end=0
manifest=[]
expected=bytearray(b'\xff'*flash_size)
for offset,path in regions:
    data=path.read_bytes()
    if not data or offset<previous_end or offset+len(data)>flash_size:
        raise SystemExit('Flash region is empty, overlapping, or outside16MiB')
    if offset==0 and len(data)>0x8000:
        raise SystemExit('Bootloader overlaps partition sector')
    if offset==0x8000 and len(data)>0x1000:
        raise SystemExit('Partition table exceeds its sector')
    if offset==ota0.offset and (len(data)>ota0.size or len(data)>ota1.size):
        raise SystemExit('Application does not fit both OTA slots')
    if offset!=0x8000:
        with path.open('rb') as source: image=ESP32S3FirmwareImage(source)
        if image.chip_id!=9 or image.checksum!=image.calculate_checksum():
            raise SystemExit('Invalid ESP32-S3 image header/checksum: '+path.name)
        if image.append_digest and image.stored_digest!=image.calc_digest:
            raise SystemExit('Invalid appended image digest: '+path.name)
    expected[offset:offset+len(data)]=data
    previous_end=offset+len(data)
    manifest.append({'file':path.name,'offset':hex(offset),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
merged=output/'AuraDesk.ino.merged.bin'
cmd=[sys.executable,'-m','esptool','--chip','esp32s3','merge-bin','--output',str(merged),'--pad-to-size','16MB','--flash-mode','keep','--flash-freq','keep','--flash-size','keep']
for offset,path in regions:cmd.extend([hex(offset),str(path)])
subprocess.run(cmd,check=True)
actual=merged.read_bytes()
if actual!=expected:
    merged.unlink(missing_ok=True)
    raise SystemExit('Merged image differs from validated regions and erased padding')
layout={'chip':'esp32s3','flash_size_bytes':flash_size,'application_offset':hex(ota0.offset),'regions':manifest,'merged_image':{'file':merged.name,'bytes':len(actual),'sha256':hashlib.sha256(actual).hexdigest()},'otadata':'Intentionally erased; bootloader selects first OTA slot','warning':'Do not use Arduino CLI upload. Custom layout requires explicit offsets.'}
(output/'build-layout.json').write_text(json.dumps(layout,indent=2)+'\n')
print('Custom merged image validated:16MiB, application at0x20000; no boot_app0 written.')
PYCODE
# Linker maps contain linker input filenames, independent of compiler prefix maps.
"$PYTHON" - "$ROOT" "$OUTPUT" <<'PUBLIC_PATHS'
from pathlib import Path
import sys
root,output=map(Path,sys.argv[1:])
map_file=output/'AuraDesk.ino.map'
if map_file.exists():
    map_file.write_text(map_file.read_text().replace(str(root),'.'))
for path in output.iterdir():
    if path.suffix in ('.bin','.elf','.map') and str(Path.home()).encode() in path.read_bytes():
        raise SystemExit('Private home path remains in release artifact: '+path.name)
print('Public artifact path audit passed.')
PUBLIC_PATHS
cp "$ROOT/docs/TOOLCHAIN_LOCK.json" "$OUTPUT/TOOLCHAIN_LOCK.json"
echo "Firmware artifacts: $OUTPUT"
