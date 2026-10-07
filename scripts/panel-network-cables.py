"""Run once on ESS_Panel_Center.blend and the matching web GLB."""
import bpy, json, struct
from pathlib import Path
from mathutils import Vector, Quaternion

root = Path(__file__).resolve().parents[1]
path = root / 'public/models/ess-container.glb'
raw = path.read_bytes()
length = struct.unpack_from('<I', raw, 12)[0]
doc = json.loads(raw[20:20+length])
nodes = doc['nodes']
lookup = {n['name']: i for i,n in enumerate(nodes)}
assert 'Switch_eBSC_Link_1' not in lookup, 'Use the pre-cabling source model'
panel = nodes[lookup['E_Panel_Detailed']]
ebsc = nodes[lookup['eBSC_Controller']]
switch = nodes[lookup['Network_Switch_IE3500']]
old_cables = [i for i in ebsc['children'] if nodes[i]['name'] == 'eBSC_LAN_Cable']
template_mesh = nodes[nodes[old_cables[0]]['children'][0]]['mesh']
blender_ebsc = bpy.data.objects['eBSC_Controller']
old_objects = [o for o in blender_ebsc.children if o.name.startswith('eBSC_LAN_Cable')]
material = old_objects[0].children[0].data.materials[0]
for cable in old_objects:
    for child in list(cable.children):
        bpy.data.objects.remove(child, do_unlink=True)
    bpy.data.objects.remove(cable, do_unlink=True)
ebsc['children'] = [i for i in ebsc['children'] if i not in old_cables]

# Raise the entire left row by 15 cm: bottom clears the middle duct,
# top remains below the upper power bank.
for name in ['Extended_Switch', 'Network_Switch_IE3500', 'eBSC_Controller']:
    nodes[lookup[name]]['translation'][1] += .15
    bpy.data.objects[name].location.z += .15

def port_position(parent, name):
    node = nodes[lookup[name]]
    q = parent['rotation']
    return Vector(parent['translation']) + Quaternion((q[3],q[0],q[1],q[2])) @ Vector(node['translation'])

for number, switch_port in [(1,'Main_RJ45_1_4'),(2,'Main_RJ45_1_5')]:
    start = port_position(ebsc, f'eBSC_LAN_{number}')
    end = port_position(switch, switch_port)
    # Separate forward service loops keep both links distinguishable.
    front = start.z + .09 + number*.025
    points = [start, Vector((start.x,start.y,front)), Vector((end.x,end.y,front)), end]
    name = f'Switch_eBSC_Link_{number}'
    group = {'name': name, 'children': [], 'extras': {'from':f'eBSC_LAN_{number}', 'to':switch_port}}
    panel['children'].append(len(nodes)); nodes.append(group)
    parent = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(parent)
    parent.parent = bpy.data.objects['E_Panel_Detailed']
    parent['from'], parent['to'] = f'eBSC_LAN_{number}', switch_port
    for index,(a,b) in enumerate(zip(points,points[1:])):
        middle=(a+b)/2; delta=b-a
        q=Vector((0,1,0)).rotation_difference(delta.normalized())
        group['children'].append(len(nodes))
        nodes.append({'name':f'{name}_Segment_{index}', 'mesh':template_mesh,
                      'translation':list(middle), 'rotation':[q.x,q.y,q.z,q.w],
                      'scale':[.007,delta.length/2,.007]})
        # glTF Y-up -> Blender Z-up.
        ba=Vector((a.x,-a.z,a.y)); bb=Vector((b.x,-b.z,b.y))
        bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=.0035, depth=(bb-ba).length)
        obj=bpy.context.object; obj.name=f'{name}_Segment_{index}'; obj.parent=parent
        obj.location=(ba+bb)/2; obj.rotation_mode='QUATERNION'
        obj.rotation_quaternion=Vector((0,0,1)).rotation_difference((bb-ba).normalized())
        obj.data.materials.append(material)
bpy.context.view_layer.update()
out=root/'Blender/ESS_Panel_Network'; out.mkdir(exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'ESS_Panel_Network.blend'))
payload=json.dumps(doc,separators=(',',':')).encode(); payload+=b' '*(-len(payload)%4)
tail=raw[20+length:]
path.write_bytes(struct.pack('<III',0x46546c67,2,20+len(payload)+len(tail))+struct.pack('<II',len(payload),0x4e4f534a)+payload+tail)
