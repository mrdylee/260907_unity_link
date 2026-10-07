"""Repair pink cable parenting and port endpoints on ESS_Panel_Network."""
import bpy, json, struct
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
path=root/'public/models/ess-container.glb'
raw=path.read_bytes(); length=struct.unpack_from('<I',raw,12)[0]
doc=json.loads(raw[20:20+length]); nodes=doc['nodes']
lookup={n['name']:i for i,n in enumerate(nodes)}
switch=nodes[lookup['Network_Switch_IE3500']]
extension=nodes[lookup['Extended_Switch']]
for number in range(1,7):
    index=lookup[f'RBMS_{number}_Cable']; cable=nodes[index]
    assert index in switch['children'], 'Use the pre-repair model'
    switch['children'].remove(index); extension['children'].append(index)
    obj=bpy.data.objects[cable['name']]
    obj.parent=bpy.data.objects['Extended_Switch']
    first=nodes[cable['children'][0]]
    old=Vector((first['translation'][0],-first['translation'][2],first['translation'][1]))
    first_obj=min(obj.children,key=lambda child:(child.location-old).length)
    for child in cable['children']:nodes[child]['translation'][2]+=.172
    for child in obj.children:child.location.y-=.172
    port=nodes[lookup[f'Expansion_RJ45_2_{number}']]
    a=Vector(port['translation']); b=Vector((-.17,a.y,a.z))
    middle=(a+b)/2; delta=b-a
    q=Vector((0,1,0)).rotation_difference(delta.normalized())
    first.update(translation=list(middle),rotation=[q.x,q.y,q.z,q.w],scale=[.007,delta.length/2,.007])
    first_obj.location=(middle.x,-middle.z,middle.y)
    first_obj.scale=(.007,.007,delta.length/2)
    first_obj.rotation_mode='QUATERNION'
    first_obj.rotation_quaternion=Vector((0,0,1)).rotation_difference(Vector((delta.x,-delta.z,delta.y)).normalized())
    cable['extras']={'port':port['name']}
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(root/'Blender/ESS_Panel_Network/ESS_Panel_Network.blend'))
payload=json.dumps(doc,separators=(',',':')).encode();payload+=b' '*(-len(payload)%4);tail=raw[20+length:]
path.write_bytes(struct.pack('<III',0x46546c67,2,20+len(payload)+len(tail))+struct.pack('<II',len(payload),0x4e4f534a)+payload+tail)
