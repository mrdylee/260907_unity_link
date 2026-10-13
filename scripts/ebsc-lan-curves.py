"""Run once on the network-curves Blender/GLB pair to round the two eBSC LAN cables."""
import bpy,sys
from pathlib import Path
from mathutils import Vector,Quaternion
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'scripts'))
from detail_export import DetailGLB
path=root/'public/models/ess-container.glb';model=DetailGLB(path)
nodes,lookup=model.nodes,model.lookup
def endpoint(node,sign):
    q=node['rotation'];rotation=Quaternion((q[3],q[0],q[1],q[2]))
    return Vector(node['translation'])+rotation@Vector((0,sign*node['scale'][1],0))
def blender(point):return (point.x,-point.z,point.y)
for number in (1,2):
    name=f'Switch_eBSC_Link_{number}';group=nodes[lookup[name]];parent=bpy.data.objects[name]
    assert len(group['children'])==3,'Use the pre-LAN-curve network-curves Blender/GLB pair'
    first,last=(nodes[group['children'][i]] for i in (0,-1))
    start,end=endpoint(first,-1),endpoint(last,1)
    outgoing=(endpoint(first,1)-start).normalized();incoming=(end-endpoint(last,-1)).normalized()
    span=(end-start).length;across=(end-start).normalized()
    middle=(start+end)/2+outgoing*(.155+number*.015)+Vector((0,-span*.18,0))
    points=[start,start+outgoing*.055,middle,end-incoming*.055,end]
    handles=[(outgoing,.055/3,.055/3),(outgoing,.055/3,.100),
             (across,span*.20,span*.20),(incoming,.100,.055/3),(incoming,.055/3,.055/3)]
    data=bpy.data.curves.new(f'{name}_Smooth','CURVE');data.dimensions='3D';data.resolution_u=24
    data.bevel_depth=first['scale'][0];data.bevel_resolution=2;data.use_fill_caps=True
    spline=data.splines.new('BEZIER');spline.bezier_points.add(4)
    for point,position,(direction,left,right) in zip(spline.bezier_points,points,handles):
        point.co=blender(position);point.handle_left_type='FREE';point.handle_right_type='FREE'
        point.handle_left=blender(position-direction*left);point.handle_right=blender(position+direction*right)
    material=model.doc['meshes'][first['mesh']]['primitives'][0]['material']
    for obj in list(parent.children):bpy.data.objects.remove(obj,do_unlink=True)
    group['children']=[]
    obj=bpy.data.objects.new(f'{name}_Smooth',data);bpy.context.collection.objects.link(obj)
    model.attach(obj,obj.name,(0,0,0),material,parent)
bpy.context.view_layer.update();out=root/'Blender/ESS_LAN_Curves';out.mkdir(exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'ESS_LAN_Curves.blend'));model.save(path)
print('EBSC_LAN_CURVES_SAVED: two smooth white cables, original ports/connectors/radius retained')
