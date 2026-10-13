"""Run on ESS_Vent_Doors.blend: diagonal covers on doors 1/2 and 5/6."""
import bpy, json, struct, sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / 'public/models/ess-container.glb'
source = Path(sys.argv[sys.argv.index('--') + 1]) if '--' in sys.argv else path
raw = source.read_bytes()
length = struct.unpack_from('<I', raw, 12)[0]
doc = json.loads(raw[20:20 + length])
nodes = doc['nodes']
old = {int(n['name'][-2:]): i for i, n in enumerate(nodes) if n['name'].startswith('Vent_Hinge_')}
assert set(old) == {1, 2, 3, 4}, 'Requires the previous four-cover model'
objects = {number: bpy.data.objects[f'Vent_Hinge_{number:02d}'] for number in old}

layout = [(1, old[3], objects[3]), (2, old[1], objects[1]),
          (5, old[4], objects[4]), (6, old[2], objects[2])]
for index in old.values():
    parent = next(n for n in nodes if index in n.get('children', []))
    parent['children'].remove(index)
for obj in objects.values():
    obj.name = 'Previous_' + obj.name

for number, index, obj in layout:
    name = f'Vent_Hinge_{number:02d}'
    door_name = f'Door_Hinge_{number:02d}'
    node = nodes[index]
    node['name'] = name
    node['rotation'] = [0, 0, 0, 1]
    node['extras'] = {'ventId': number, 'pairedVentId': number + 1 if number % 2 else number - 1, 'openDegrees': 45}
    next(n for n in nodes if n['name'] == door_name)['children'].append(index)
    obj.name = name
    obj.parent = bpy.data.objects[door_name]
    x, y, z = node['translation']
    obj.location = (x, -z, y)
    obj.rotation_euler = (0, 0, 0)
    obj['open_degrees'] = 45
    obj['paired_vent_id'] = node['extras']['pairedVentId']

bpy.context.view_layer.update()
for number in range(1, 7):
    door = bpy.data.objects[f'Door_Hinge_{number:02d}']
    vents = [obj for obj in door.children if obj.name.startswith('Vent_Hinge_')]
    assert len(vents) == (0 if number in (3, 4) else 1)
    if vents:
        assert vents[0].location.z < .5 if number % 2 else vents[0].location.z > 1.5

out = root / 'Blender/ESS_Vent_Layout'
out.mkdir(exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(out / 'ESS_Vent_Layout.blend'))
payload = json.dumps(doc, separators=(',', ':')).encode()
payload += b' ' * (-len(payload) % 4)
tail = raw[20 + length:]
path.write_bytes(struct.pack('<III', 0x46546c67, 2, 20 + len(payload) + len(tail)) + struct.pack('<II', len(payload), 0x4e4f534a) + payload + tail)
print('VENT_LAYOUT_SAVED: four covers on doors 1/2 and 5/6; middle doors clear')
