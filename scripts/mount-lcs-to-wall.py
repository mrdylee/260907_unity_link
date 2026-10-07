"""Mount LCS housing flush with the white side panel, in Blender and GLB."""
import bpy, json, struct
from pathlib import Path
root=Path(__file__).resolve().parents[1]
path=root/'public/models/ess-container.glb'
raw=path.read_bytes(); length=struct.unpack_from('<I',raw,12)[0]
doc=json.loads(raw[20:20+length]); nodes={n['name']:n for n in doc['nodes']}
wall=nodes['Fixed_Louver_Panel']
housing=nodes['LCS_Black_Housing']
panel=nodes['E_Panel_Detailed']
# Wall's inside surface and LCS rear surface meet without penetration.
wall_inside=wall['translation'][2]-wall['scale'][2]/2
center=wall_inside-housing['scale'][0]/2
nodes['LCS_Controller']['translation'][2]=center-panel['translation'][2]
bpy.data.objects['LCS_Controller'].location.y=-(center-panel['translation'][2])
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(root/'Blender/ESS_Panel_Network/ESS_Panel_Network.blend'))
payload=json.dumps(doc,separators=(',',':')).encode();payload+=b' '*(-len(payload)%4);tail=raw[20+length:]
path.write_bytes(struct.pack('<III',0x46546c67,2,20+len(payload)+len(tail))+struct.pack('<II',len(payload),0x4e4f534a)+payload+tail)
