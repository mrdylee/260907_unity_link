"""Remove only the six yellow door plaques from the aligned Blender and web models."""
import bpy,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'scripts'))
from detail_export import DetailGLB
path=root/'public/models/ess-container.glb';model=DetailGLB(path)
for number in range(1,7):
    name=f'Door_Hinge_{number:02d}'
    door=model.nodes[model.lookup[name]]
    plaques=[i for i in door['children'] if model.nodes[i]['name']=='Door_Warning_Plate']
    assert len(plaques)==1,f'{name}: expected one warning plate'
    door['children'].remove(plaques[0])
    objects=[obj for obj in bpy.data.objects[name].children if obj.name.startswith('Door_Warning_Plate')]
    assert len(objects)==1,f'{name}: expected one Blender warning plate'
    bpy.data.objects.remove(objects[0],do_unlink=True)
assert not any(obj.name.startswith('Door_Warning_Plate') for obj in bpy.data.objects)
out=root/'Blender/ESS_Clean_Doors';out.mkdir(exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'ESS_Clean_Doors.blend'));model.save(path)
print('REMOVED: six door warning plates; hinges and remaining hardware retained')
