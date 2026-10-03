#!/usr/bin/env python3
"""Compile real LVGL/UI for host visual checks, without ESP32 hardware access."""
from pathlib import Path
import concurrent.futures
import subprocess
import sys

root=Path(__file__).resolve().parent.parent
library=root/'.toolchains/arduino/user/libraries/lvgl'
build=root/'build/ui-preview'
output=root/'artifacts/ui-preview'
build.mkdir(parents=True,exist_ok=True)
output.mkdir(parents=True,exist_ok=True)
includes=['-I'+str(library),'-I'+str(root/'firmware/AuraDesk'),'-DLV_CONF_INCLUDE_SIMPLE=1']
def compile_one(source):
    obj=build/(str(source.relative_to(library)).replace('/','_')+'.o')
    if not obj.exists() or obj.stat().st_mtime<max(source.stat().st_mtime,(root/'firmware/AuraDesk/lv_conf.h').stat().st_mtime):
        subprocess.run(['clang','-O1','-w',*includes,'-c',str(source),'-o',str(obj)],check=True)
    return obj
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    objects=list(pool.map(compile_one,sorted((library/'src').rglob('*.c'))))
binary=build/'render-ui'
subprocess.run(['clang++','-std=c++17','-O1',*includes,str(root/'firmware/ui_preview/render.cpp'),str(root/'firmware/AuraDesk/ui.cpp'),*[str(p) for p in objects],'-o',str(binary)],check=True)
subprocess.run([str(binary),str(output)],check=True)
subprocess.run([str(binary),str(output),'--fixture'],check=True)
for ppm in sorted(output.glob('*.ppm')):
    subprocess.run(['sips','-s','format','png',str(ppm),'--out',str(ppm.with_suffix('.png'))],check=True,stdout=subprocess.DEVNULL)
    ppm.unlink()
print(f'Actual LVGL screenshots: {output}')
