"""Run with Blender -b source.blend --python scripts/paired-doors.py.
Mirror the even leaves about their center so handles meet and hinges sit outside.
Keep the existing baked PBR payload, transferring Blender-edited hinge transforms.
"""
import bpy, json, struct
from pathlib import Path

root = Path(__file__).resolve().parents[1]
changes = {}
for number in (2, 4, 6):
    door = bpy.data.objects[f'Door_Hinge_{number:02d}']
    # Door leaf center is x=.585 in the unscaled hinge coordinate system.
    door.location.x += 1.17 * door.scale.x
    door.scale.x *= -1
    changes[door.name] = {'translation': [door.location.x, door.location.z, -door.location.y],
                          'scale': [door.scale.x, door.scale.z, door.scale.y]}
for number in range(1, 7):
    bpy.data.objects[f'Door_Hinge_{number:02d}']['open_degrees'] = -105 if number % 2 else 105
bpy.context.view_layer.update()
out = root / 'Blender/ESS_Paired_Doors'
out.mkdir(exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out / 'ESS_Paired_Doors.blend'))
path = root / 'public/models/ess-container.glb'
raw = path.read_bytes()
length = struct.unpack_from('<I', raw, 12)[0]
document = json.loads(raw[20:20+length])
for node in document['nodes']:
    if node.get('name') in changes:
        node.update(changes[node['name']])
document['asset']['generator'] = 'Blender paired-door hinge revision with preserved baked PBR textures'
payload = json.dumps(document, separators=(',', ':')).encode()
payload += b' ' * (-len(payload) % 4)
tail = raw[20+length:]
path.write_bytes(struct.pack('<III', 0x46546c67, 2, 20+len(payload)+len(tail)) + struct.pack('<II',len(payload),0x4e4f534a) + payload + tail)
(out / 'hinges.json').write_text(json.dumps(changes, indent=2))
print('PAIRED_DOORS_EXPORTED', json.dumps(changes))
