"""Remove the two enclosure jambs obstructing the outer paired rack-door openings."""
import bpy,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'scripts'))
from detail_export import DetailGLB
path=root/'public/models/ess-container.glb';model=DetailGLB(path)
enclosure=model.nodes[model.lookup['Enclosure']]
for name in ('Door_Jamb_1','Door_Jamb_3'):
    index=model.lookup[name]
    assert index in enclosure['children'],f'{name} must be an enclosure jamb'
    enclosure['children'].remove(index)
    bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
for number in range(1,7):
    rack=bpy.data.objects[f'Battery_Rack_{number:02d}']
    assert len([obj for obj in rack.children if obj.name.startswith('Rack_Upright')])==4
out=root/'Blender/ESS_Clear_Rack_Openings';out.mkdir(exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'ESS_Clear_Rack_Openings.blend'));model.save(path)
print('RACK_OPENINGS_CLEARED: Door_Jamb_1 and Door_Jamb_3 removed; all rack uprights retained')
