"""Align rack-door pivots with their barrel axes, preserving every closed mesh pose.
Run with Blender -b Blender/ESS_Touching_Racks/ESS_Touching_Racks.blend --python this-file.
"""
import bpy, sys
from pathlib import Path
from mathutils import Matrix, Quaternion, Vector

root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'scripts'))
from detail_export import DetailGLB
path=root/'public/models/ess-container.glb';model=DetailGLB(path)

def matrix(node):
    x,y,z,w=node.get('rotation',[0,0,0,1])
    return Matrix.LocRotScale(Vector(node.get('translation',[0,0,0])),Quaternion((w,x,y,z)),Vector(node.get('scale',[1,1,1])))

def unchanged(before,after):
    assert max(abs(before[i][j]-after[i][j]) for i in range(4) for j in range(4))<1e-6,'Closed geometry moved'

for number in range(1,7):
    name=f'Door_Hinge_{number:02d}';door=bpy.data.objects[name]
    barrels=[obj for obj in door.children if obj.name.startswith('Hinge_Barrel')]
    assert len(barrels)==3
    offset=Vector((barrels[0].location.x,barrels[0].location.y,0))
    assert all((Vector((obj.location.x,obj.location.y,0))-offset).length<1e-6 for obj in barrels)
    bpy.context.view_layer.update()
    before={obj:obj.matrix_world.copy() for obj in door.children_recursive}
    door.location+=door.matrix_basis.to_3x3()@offset
    for obj in door.children:obj.location-=offset
    bpy.context.view_layer.update()
    for obj,pose in before.items():unchanged(pose,obj.matrix_world)

    node=model.nodes[model.lookup[name]]
    children=[model.nodes[i] for i in node['children']]
    barrels=[child for child in children if child['name'].startswith('Hinge_Barrel')]
    assert len(barrels)==3
    center=barrels[0]['translation'];shift=Vector((center[0],0,center[2]))
    assert all(abs(child['translation'][0]-shift.x)+abs(child['translation'][2]-shift.z)<1e-6 for child in barrels)
    before=[matrix(node)@matrix(child) for child in children]
    node['translation']=list(Vector(node['translation'])+matrix(node).to_3x3()@shift)
    for child in children:child['translation']=list(Vector(child.get('translation',[0,0,0]))-shift)
    for child,pose in zip(children,before):unchanged(pose,matrix(node)@matrix(child))
    print(f'{name}: pivot aligned by {tuple(round(v,6) for v in shift)}; closed geometry retained')

out=root/'Blender/ESS_Aligned_Door_Hinges';out.mkdir(exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'ESS_Aligned_Door_Hinges.blend'))
model.save(path)
