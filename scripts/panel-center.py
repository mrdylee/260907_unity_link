"""Run on ESS_Panel_Layout.blend and its matching GLB, once."""
import bpy, copy, json, struct
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / 'public/models/ess-container.glb'
raw = path.read_bytes()
length = struct.unpack_from('<I', raw, 12)[0]
doc = json.loads(raw[20:20 + length])
nodes = doc['nodes']
assert not any(n['name'].startswith('Center_Middle_') for n in nodes)
panel = next(n for n in nodes if n['name'] == 'E_Panel_Detailed')

def clone_node(index, prefix):
    node = copy.deepcopy(nodes[index])
    new_index = len(nodes)
    node['name'] = prefix + '_' + str(new_index)
    nodes.append(node)
    if 'children' in node:
        node['children'] = [clone_node(child, prefix) for child in node['children']]
    return new_index

def clone_object(obj, parent):
    children = list(obj.children)
    result = obj.copy()
    bpy.context.collection.objects.link(result)
    result.parent = parent
    for child in children:
        clone_object(child, result)
    return result

# Photo-inspired second power-supply bank, keeping the side controllers clear.
for name, z in [('UPS', .15), ('Redundancy_Module', .30), ('SMPS', .45)]:
    source_index = next(i for i,n in enumerate(nodes) if n['name'] == name)
    index = clone_node(source_index, 'Center_Middle_' + name)
    nodes[index]['translation'] = [-.02, .73, z]
    panel['children'].append(index)
    obj = clone_object(bpy.data.objects[name], bpy.data.objects['E_Panel_Detailed'])
    obj.name = nodes[index]['name']
    obj.location = (-.02, -z, .73)

# Supplement the top row with terminal blocks and green inserts.
for name in ['Terminal_Block', 'Terminal_Green_Insert']:
    source_index = next(i for i,n in enumerate(nodes) if n['name'] == name)
    for number,z in enumerate([.04,.14,.24,.34,.44,.54]):
        index = clone_node(source_index, 'Center_Upper_' + name)
        position = nodes[index]['translation']
        position[1], position[2] = 1.12,z
        panel['children'].append(index)
        obj = clone_object(bpy.data.objects[name], bpy.data.objects['E_Panel_Detailed'])
        obj.name = nodes[index]['name']
        obj.location = (position[0], -z, position[1])
bpy.context.view_layer.update()
out = root / 'Blender/ESS_Panel_Center'
out.mkdir(exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out / 'ESS_Panel_Center.blend'))
payload = json.dumps(doc, separators=(',', ':')).encode()
payload += b' ' * (-len(payload) % 4)
tail = raw[20 + length:]
path.write_bytes(struct.pack('<III',0x46546c67,2,20+len(payload)+len(tail)) + struct.pack('<II',len(payload),0x4e4f534a) + payload + tail)
