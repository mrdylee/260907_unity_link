"""Run on ESS_Paired_Doors.blend; preserve baked GLB geometry and textures."""
import bpy, json, math, struct, sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / 'public/models/ess-container.glb'
source = Path(sys.argv[sys.argv.index('--') + 1]) if '--' in sys.argv else path
raw = source.read_bytes()
length = struct.unpack_from('<I', raw, 12)[0]
doc = json.loads(raw[20:20 + length])
nodes = doc['nodes']
by_name = {n['name']: i for i, n in enumerate(nodes)}
panel = nodes[by_name['E_Panel_Detailed']]
switch = nodes[by_name['Network_Switch_IE3500']]
expansion_children = [i for i in switch['children'] if nodes[i]['name'].startswith(('Expansion_', 'IEM3500_'))]
assert expansion_children, 'Run against the original paired-door model'
expansion = {'name': 'Extended_Switch', 'children': expansion_children}
panel['children'].append(len(nodes))
nodes.append(expansion)
switch['children'] = [i for i in switch['children'] if i not in expansion_children]
ext = bpy.data.objects.new('Extended_Switch', None)
bpy.context.collection.objects.link(ext)
ext.parent = bpy.data.objects['E_Panel_Detailed']
for index in expansion_children:
    node = nodes[index]
    node['translation'][2] += .172
    obj = bpy.data.objects[node['name']]
    obj.parent = ext
    obj.location.y -= .172

# Looking at the left wall, increasing X runs left to right.
layout = {'Extended_Switch': (-2.96, 1.05, -.28, 90),
          'Network_Switch_IE3500': (-2.74, 1.05, -.28, 90),
          'eBSC_Controller': (-2.51, 1.05, -.28, 90),
          'LCS_Controller': (-2.72, 1.45, .86, -90)}
for name, (x, y, z, angle) in layout.items():
    node = expansion if name == 'Extended_Switch' else nodes[by_name[name]]
    position = [x - panel['translation'][0], y - panel['translation'][1], z - panel['translation'][2]]
    a = math.radians(angle)
    node.update(translation=position, rotation=[0, math.sin(a / 2), 0, math.cos(a / 2)], scale=[1, 1, 1])
    obj = bpy.data.objects[name]
    obj.location = (position[0], -position[2], position[1])
    obj.rotation_mode = 'XYZ'
    obj.rotation_euler = (0, 0, a)
    obj.scale = (1, 1, 1)
bpy.context.view_layer.update()
out = root / 'Blender/ESS_Panel_Layout'
out.mkdir(exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out / 'ESS_Panel_Layout.blend'))
payload = json.dumps(doc, separators=(',', ':')).encode()
payload += b' ' * (-len(payload) % 4)
tail = raw[20 + length:]
path.write_bytes(struct.pack('<III', 0x46546c67, 2, 20 + len(payload) + len(tail)) + struct.pack('<II', len(payload), 0x4e4f534a) + payload + tail)
print('PANEL_LAYOUT_EXPORTED', layout)
