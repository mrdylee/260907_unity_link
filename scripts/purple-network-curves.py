"""Run once on the LCS-wiring Blender/GLB pair to round the purple network cables."""
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
for number in range(1,7):
    name=f'RBMS_{number}_Cable';group=nodes[lookup[name]];parent=bpy.data.objects[name]
    assert len(group['children'])==3,'Use the pre-curve LCS-wiring Blender/GLB pair'
    first,last=(nodes[group['children'][i]] for i in (0,-1))
    start,end=endpoint(first,-1),endpoint(last,1)
    outgoing=(endpoint(first,1)-start).normalized();incoming=(end-endpoint(last,-1)).normalized()
    points=[start,start+outgoing*.065,end-incoming*.040,end]
    handles=[(outgoing,.065/3,.065/3),(outgoing,.065/3,.150),
             (incoming,.200,.040/3),(incoming,.040/3,.040/3)]
    data=bpy.data.curves.new(f'{name}_Smooth','CURVE');data.dimensions='3D';data.resolution_u=24
    data.bevel_depth=.007;data.bevel_resolution=2;data.use_fill_caps=True
    spline=data.splines.new('BEZIER');spline.bezier_points.add(3)
    for point,position,(direction,left,right) in zip(spline.bezier_points,points,handles):
        point.co=blender(position);point.handle_left_type='FREE';point.handle_right_type='FREE'
        point.handle_left=blender(position-direction*left);point.handle_right=blender(position+direction*right)
    # Remove only the former straight segments; keep the cable group and port metadata.
    for obj in list(parent.children):bpy.data.objects.remove(obj,do_unlink=True)
    group['children']=[]
    obj=bpy.data.objects.new(f'{name}_Smooth',data);bpy.context.collection.objects.link(obj)
    model.attach(obj,obj.name,(0,0,0),10,parent)
bpy.context.view_layer.update();out=root/'Blender/ESS_Network_Curves';out.mkdir(exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'ESS_Network_Curves.blend'));model.save(path)
print('PURPLE_CURVES_SAVED: six smooth cables, original ports/duct endpoints/color/radius retained')
