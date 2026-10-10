"""Add four bottom-edge vent pivots to Blender and the baked web model."""
import bpy,json,struct
from pathlib import Path
root=Path(__file__).resolve().parents[1]
path=root/'public/models/ess-container.glb'
raw=path.read_bytes();length=struct.unpack_from('<I',raw,12)[0]
doc=json.loads(raw[20:20+length]);nodes=doc['nodes']
assert not any(n['name'].startswith('Vent_Hinge_') for n in nodes)
for number,door_name,vent_name in [(1,'Door_Hinge_01','Upper_Exhaust_Vent'),(2,'Door_Hinge_05','Upper_Exhaust_Vent'),(3,'Door_Hinge_01','Lower_Intake_Damper'),(4,'Door_Hinge_05','Lower_Intake_Damper')]:
    door=next(n for n in nodes if n['name']==door_name)
    index=next(i for i in door['children'] if nodes[i]['name']==vent_name)
    vent=nodes[index]
    # Existing cover geometry is centered at the vent origin.
    bottom=min(nodes[c]['translation'][1]-nodes[c]['scale'][1]/2 for c in vent['children'])
    position=list(vent['translation']);position[1]+=bottom
    hinge={'name':f'Vent_Hinge_{number:02d}','translation':position,'children':[index], 'extras':{'ventId':number,'pairedVentId':5-number,'openDegrees':45}}
    door['children'][door['children'].index(index)]=len(nodes);nodes.append(hinge)
    vent['translation']=[0,-bottom,0]
    parent=bpy.data.objects[door_name]
    obj=next(o for o in parent.children if o.name.startswith(vent_name))
    pivot=bpy.data.objects.new(hinge['name'],None);bpy.context.collection.objects.link(pivot)
    pivot.parent=parent;pivot.location=(position[0],-position[2],position[1])
    obj.parent=pivot;obj.location=(0,0,-bottom)
    pivot['open_degrees']=45;pivot['paired_vent_id']=5-number
bpy.context.view_layer.update()
out=root/'Blender/ESS_Vent_Doors';out.mkdir(exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'ESS_Vent_Doors.blend'))
payload=json.dumps(doc,separators=(',',':')).encode();payload+=b' '*(-len(payload)%4);tail=raw[20+length:]
path.write_bytes(struct.pack('<III',0x46546c67,2,20+len(payload)+len(tail))+struct.pack('<II',len(payload),0x4e4f534a)+payload+tail)
