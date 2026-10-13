"""Widen paired racks inward until their frames meet without changing the pair's outer edges."""
import bpy,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'scripts'))
from detail_export import DetailGLB
path=root/'public/models/ess-container.glb';model=DetailGLB(path)
def bounds(rack):
    base=next(model.nodes[i] for i in rack['children'] if model.nodes[i]['name']=='Rack_Base')
    position=model.doc['meshes'][base['mesh']]['primitives'][0]['attributes']['POSITION']
    geometry=model.doc['accessors'][position]
    return tuple(base['translation'][0]+geometry[key][0]*base['scale'][0] for key in ('min','max'))
for number in (1,3,5):
    left,right=(model.nodes[model.lookup[f'Battery_Rack_{i:02d}']] for i in (number,number+1))
    a,b=bounds(left);c,d=bounds(right)
    outer_left=left['translation'][0]+a*left['scale'][0]
    outer_right=right['translation'][0]+d*right['scale'][0]
    seam=(left['translation'][0]+b*left['scale'][0]+right['translation'][0]+c*right['scale'][0])/2
    for rack,low,high,lo,hi in [(left,outer_left,seam,a,b),(right,seam,outer_right,c,d)]:
        rack['scale'][0]=(high-low)/(hi-lo);rack['translation'][0]=low-lo*rack['scale'][0]
        obj=bpy.data.objects[rack['name']];obj.scale.x=rack['scale'][0];obj.location.x=rack['translation'][0]
    print(f'RACK_PAIR_{number}_{number+1}: seam={seam:.6f}, outer edges retained')
bpy.context.view_layer.update();out=root/'Blender/ESS_Touching_Racks';out.mkdir(exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'ESS_Touching_Racks.blend'));model.save(path)
