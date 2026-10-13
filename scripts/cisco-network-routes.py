"""Run once on ESS_Cisco_Detail.blend and its matching pre-routing GLB."""
import bpy,sys
from pathlib import Path
from mathutils import Vector,Quaternion,Matrix
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'scripts'))
from detail_export import DetailGLB
path=root/'public/models/ess-container.glb'
source=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else path
model=DetailGLB(source);nodes,lookup=model.nodes,model.lookup
main=nodes[lookup['Network_Switch_IE3500']];ext=nodes[lookup['Extended_Switch']]
assert lookup['RBMS_1_Cable'] in ext['children'],'Use the pre-routing Cisco detail model'
def rotation(node):
    q=node['rotation'];return Quaternion((q[3],q[0],q[1],q[2]))
def world(parent,point):return Vector(parent['translation'])+rotation(parent)@Vector(point)
def local(parent,point):return rotation(parent).inverted()@(point-Vector(parent['translation']))
def reparent(name,before,after):
    index=lookup[name];nodes[lookup[before]]['children'].remove(index);nodes[lookup[after]].setdefault('children',[]).append(index)
    obj=bpy.data.objects[name];obj.parent=bpy.data.objects[after];obj.matrix_parent_inverse=Matrix.Identity(4)
def segments(group,points):
    for index,(a,b) in zip(group['children'],zip(points,points[1:])):
        n=nodes[index];delta=b-a;middle=(a+b)/2;q=Vector((0,1,0)).rotation_difference(delta.normalized())
        n.update(translation=list(middle),rotation=[q.x,q.y,q.z,q.w],scale=[.007,delta.length/2,.007])
        obj=bpy.data.objects[n['name']];obj.data=obj.data.copy()
        depth=max(v.co.z for v in obj.data.vertices)-min(v.co.z for v in obj.data.vertices)
        for v in obj.data.vertices:v.co.x*=obj.scale.x;v.co.y*=obj.scale.y;v.co.z*=delta.length/depth
        obj.scale=(1,1,1);obj.location=(middle.x,-middle.z,middle.y);obj.rotation_mode='QUATERNION'
        obj.rotation_quaternion=Vector((0,0,1)).rotation_difference(Vector((delta.x,-delta.z,delta.y)).normalized())
purple_ports=['Main_SFP_1_1','Main_SFP_1_2','Main_RJ45_1_4','Main_RJ45_1_5','Main_RJ45_1_6','Main_RJ45_1_11']
for number,target in enumerate(purple_ports,1):
    group=nodes[lookup[f'RBMS_{number}_Cable']]
    z=-.45+(number-1)*.036
    # Enter the top control-panel duct above the red/black wiring, on the eBSC side.
    bend=local(main,Vector((-.170,1.355,z)));end=local(main,Vector((-.055,1.305,z)))
    start=Vector(nodes[lookup[target]]['translation'])
    points=[start,Vector((-.170,start.y,start.z)),bend,end]
    reparent(group['name'],'Extended_Switch','Network_Switch_IE3500');group['extras'].update(port=target,route='upper-control-duct')
    bpy.data.objects[group['name']]['port']=target
    segments(group,points)
    for name in (f'RBMS_RJ45_Plug_{number}',f'RBMS_Strain_Relief_{number}'):
        reparent(name,f'Expansion_RJ45_2_{number}',target)
    if number<=2:
        model.box(f'IE3500_SFP_Copper_Module_{number}',(-.007,0,0),(.014,.030,.023),3,bpy.data.objects[target])
ebsc=nodes[lookup['eBSC_Controller']]
for number,target,parent in [(1,'Expansion_RJ45_2_9',ext),(2,'Main_RJ45_1_7',main)]:
    group=nodes[lookup[f'Switch_eBSC_Link_{number}']];group['extras']['to']=target
    bpy.data.objects[group['name']]['to']=target
    start=world(ebsc,nodes[lookup[group['extras']['from']]]['translation']);end=world(parent,nodes[lookup[target]]['translation'])
    front=start.z+.09+number*.025
    segments(group,[start,Vector((start.x,start.y,front)),Vector((end.x,end.y,front)),end])
    old=f'Main_RJ45_Plug_{number+3}';reparent(old,f'Main_RJ45_1_{number+3}',target)
    name=f'Switch_eBSC_RJ45_Plug_{number}';nodes[lookup[old]]['name']=name;bpy.data.objects[old].name=name
bpy.context.view_layer.update();out=root/'Blender/ESS_Cisco_Network';out.mkdir(exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'ESS_Cisco_Network.blend'));model.save(path)
print('CISCO_NETWORK_SAVED: six purple links on main IE3500, one eBSC link on each switch')
