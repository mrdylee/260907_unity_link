"""Recess adjacent rack-door rims 15mm in a GLB; leaves binary mesh/texture data intact.

Run after exporting the Blender source: python3 scripts/recess-door-rims.py [model.glb]
"""
import json
import struct
import sys
from pathlib import Path

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / 'public/models/ess-container.glb'
raw = path.read_bytes()
magic, version, _ = struct.unpack_from('<III', raw)
length, kind = struct.unpack_from('<II', raw, 12)
assert magic == 0x46546C67 and version == 2 and kind == 0x4E4F534A
doc = json.loads(raw[20:20 + length])
nodes = doc['nodes']
rims = [nodes[child] for door in nodes if door.get('name') in
        [f'Door_Hinge_{number:02d}' for number in (2, 3, 4, 5)]
        for child in door['children'] if nodes[child]['name'].startswith('Door_Edge')]
assert len(rims) == 16
changed = 0
for rim in rims:
    z = rim['translation'][2]
    if abs(z - .043) < 1e-6:
        rim['translation'][2] -= .015
        changed += 1
    else:
        assert abs(z - .028) < 1e-6, f"Unexpected rim depth: {rim['name']} {z}"
if changed:
    payload = json.dumps(doc, separators=(',', ':')).encode()
    payload += b' ' * (-len(payload) % 4)
    remainder = raw[20 + length:]
    path.write_bytes(struct.pack('<III', magic, version, 20 + len(payload) + len(remainder))
                     + struct.pack('<II', len(payload), kind) + payload + remainder)
print(f'{path.name}: recessed {changed}/16 rims; binary mesh and texture chunks preserved')
