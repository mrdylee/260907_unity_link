"""Rotate IE3500 180 degrees in its front plane; reconnect both eBSC links."""
import bpy,json,struct,math
from pathlib import Path
from mathutils import Vector,Quaternion
root=Path(__file__).resolve().parents[1]
path=root/'public/models/ess-container.glb'
raw=path.read_bytes();length=struct.unpack_from('<I',raw,12)[0]
doc=json.loads(raw[20:20+length]);nodes=doc['nodes'];lookup={n['name']:i for i,n in enumerate(nodes)}
switch=nodes[lookup['Network_Switch_IE3500']]
assert 'front_rotation_degrees' not in switch.get('extras',{}), 'Use the model before switch rotation'
q=switch['rotation'];rotation=Quaternion((q[3],q[0],q[1],q[2]))@Quaternion((1,0,0),math.pi)
switch['rotation']=[rotation.x,rotation.y,rotation.z,rotation.w]
switch.setdefault('extras',{})['front_rotation_degrees']=180
obj=bpy.data.objects['Network_Switch_IE3500'];obj.rotation_mode='QUATERNION'
obj.rotation_quaternion=Quaternion((rotation.w,rotation.x,-rotation.z,rotation.y))
obj['front_rotation_degrees']=180
def point(parent,name):
    q=parent['rotation']
    return Vector(parent['translation'])+Quaternion((q[3],q[0],q[1],q[2]))@Vector(nodes[lookup[name]]['translation'])
ebsc=nodes[lookup['eBSC_Controller']]
for number in (1,2):
    link=nodes[lookup[f'Switch_eBSC_Link_{number}']]
    start=point(ebsc,link['extras']['from']);end=point(switch,link['extras']['to'])
    front=start.z+.09+number*.025
    points=[start,Vector((start.x,start.y,front)),Vector((end.x,end.y,front)),end]
    for index,(a,b) in zip(link['children'],zip(points,points[1:])):
        node=nodes[index];middle=(a+b)/2;delta=b-a;q=Vector((0,1,0)).rotation_difference(delta.normalized())
        node.update(translation=list(middle),rotation=[q.x,q.y,q.z,q.w],scale=[.007,delta.length/2,.007])
        obj=bpy.data.objects[node['name']];obj.data=obj.data.copy()
        size=max(v.co.z for v in obj.data.vertices)-min(v.co.z for v in obj.data.vertices)
        for vertex in obj.data.vertices:vertex.co.z*=delta.length/size
        obj.location=(middle.x,-middle.z,middle.y);obj.scale=(1,1,1);obj.rotation_mode='QUATERNION'
        obj.rotation_quaternion=Vector((0,0,1)).rotation_difference(Vector((delta.x,-delta.z,delta.y)).normalized())
bpy.context.view_layer.update()
out=root/'Blender/ESS_IE3500_Orientation';out.mkdir(exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'ESS_IE3500_Orientation.blend'))
payload=json.dumps(doc,separators=(',',':')).encode();payload+=b' '*(-len(payload)%4);tail=raw[20+length:]
path.write_bytes(struct.pack('<III',0x46546c67,2,20+len(payload)+len(tail))+struct.pack('<II',len(payload),0x4e4f534a)+payload+tail)
print('IE3500_ROTATED: eight copper ports right, three SFP ports left, both links connected')
