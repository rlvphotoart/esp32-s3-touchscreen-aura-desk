#!/usr/bin/env python3
"""Verify local backup hashes without opening the device or changing files."""
import argparse,hashlib,json
from pathlib import Path

def checked_path(root, name):
    path=(root/name).resolve()
    if not path.is_relative_to(root):
        raise ValueError('Manifest path escapes backup directory')
    return path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory',type=Path)
    a=p.parse_args()
    root=a.directory.resolve()
    m=json.loads((root/'manifest.json').read_text())
    image=checked_path(root,'full_flash_original.bin')
    data=image.read_bytes()
    expected=m['full_flash_original.bin']
    if len(data)!=m['flash_size_bytes'] or len(data)!=expected['bytes']:
        raise ValueError('Full image size mismatch')
    if hashlib.sha256(data).hexdigest()!=expected['sha256']:
        raise ValueError('Full image SHA-256 mismatch')
    if not expected.get('device_md5_verified') or hashlib.md5(data).hexdigest()!=expected['md5']:
        raise ValueError('Device MD5 verification record/hash mismatch')
    for chunk in m['chunks']:
        offset=int(chunk['offset'],16); length=chunk['length']
        if hashlib.sha256(data[offset:offset+length]).hexdigest()!=chunk['sha256']:
            raise ValueError(f'Chunk hash mismatch at {offset:#x}')
    for name,entry in m.get('files',{}).items():
        path=checked_path(root,name)
        if path.stat().st_size!=entry['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest()!=entry['sha256']:
            raise ValueError(f'Artifact hash mismatch: {name}')
    print(f'PASS: {image}; {len(data):,} bytes; full image, chunk and artifact SHA-256 hashes match.')
    print('This is local integrity verification. The manifest also records the device-side MD5 comparison at acquisition.')

if __name__=='__main__':main()
