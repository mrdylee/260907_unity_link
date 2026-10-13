"""Connect the LCS signal terminal rows to the central panel ducts with smooth curves."""
import bpy,sys
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'scripts'))
from detail_export import DetailGLB
path=root/'public/models/ess-container.glb';model=DetailGLB(path)
nodes,lookup=model.nodes,model.lookup
assert 'LCS_Top_Signal_Wires' not in lookup,'Use the pre-wiring LCS-detail Blender/GLB pair'
parent=bpy.data.objects['E_Panel_Detailed'];lcs=bpy.data.objects['LCS_Controller']
bpy.context.view_layer.update();transform=parent.matrix_world.inverted() @ lcs.matrix_world
ducts=sorted([nodes[i] for i in nodes[lookup[parent.name]]['children'] if nodes[i]['name'].startswith('Horizontal_Wiring_Duct')],key=lambda n:n['translation'][1])
def panel_point(point):
    p=transform @ Vector((point.x,-point.z,point.y))
    return Vector((p.x,p.z,-p.y))
def curve(name,paths,radius,material,curve_parent):
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.resolution_u=10
    data.bevel_depth=radius;data.bevel_resolution=1;data.use_fill_caps=True
    for points in paths:
        spline=data.splines.new('BEZIER');spline.bezier_points.add(len(points)-1)
        for point,(x,y,z) in zip(spline.bezier_points,points):
            point.co=(x,-z,y);point.handle_left_type='AUTO';point.handle_right_type='AUTO'
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj)
    model.attach(obj,name,(0,0,0),material,curve_parent)
for row,counts,sign,duct in [('Top',[12,12,8,8],1,ducts[-1]),('Bottom',[8,12,8,8],-1,ducts[1])]:
    paths=[];ferrules=[];routes=[]
    for number,count in enumerate(counts,1):
        bank=nodes[lookup[f'LCS_{row}_Terminal_Bank_{number}']]
        for pin in range(count):
            start=Vector(bank['translation']);start.y+=sign*.010
            start.z+=(pin-(count-1)/2)*bank['scale'][2]/count
            start=panel_point(start);index=len(paths)
            departure=start+Vector((0,sign*.036,-.004))
            # Two spaced rows enter the free right-hand end of each duct.
            end=Vector((-.040,duct['translation'][1]+(-.010 if index<20 else .010),.630-(index%20)*.0031))
            arc=Vector((start.x+.010,start.y+sign*(.090+index*.001),start.z-.045))
            approach=Vector((-.165,end.y+sign*(.043+index*.0006),end.z+.060))
            paths.append([start,departure,arc,approach,Vector((-.100,end.y,end.z)),end])
            ferrules.append([start,start+(departure-start).normalized()*.010])
            routes.append({'from':bank['name'],'opening':pin+1,'start':list(start),'departure':list(departure),'end':list(end)})
    name=f'LCS_{row}_Signal_Wires'
    group=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(group);group.parent=parent
    lookup[name]=len(nodes);nodes[lookup[parent.name]]['children'].append(lookup[name])
    nodes.append({'name':name,'children':[],'extras':{'visual_only':True,'routes':routes,'duct_height':duct['translation'][1]}})
    curve(f'{name}_Red',paths[::2],.00125,5,group)
    curve(f'{name}_Black',paths[1::2],.00125,6,group)
    curve(f'LCS_{row}_Signal_Ferrules',ferrules,.0016,3,parent)
bpy.context.view_layer.update();out=root/'Blender/ESS_LCS_Wiring';out.mkdir(exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'ESS_LCS_Wiring.blend'));model.save(path)
print('LCS_SIGNAL_WIRING_SAVED: 40 upper and 36 lower alternating red/black smooth wires, six merged meshes, original materials retained')
