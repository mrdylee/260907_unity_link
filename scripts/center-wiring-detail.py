"""Photo-inspired central panel wiring; run once on ESS_Cisco_Network.blend."""
import bpy,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'scripts'))
from detail_export import DetailGLB
path=root/'public/models/ess-container.glb';model=DetailGLB(path)
nodes,lookup=model.nodes,model.lookup;panel=nodes[lookup['E_Panel_Detailed']]
assert 'Center_Wiring_Blue' not in lookup,'Use the pre-wiring detail model'
parent=bpy.data.objects['E_Panel_Detailed'];routes={}
def wire(color,points,radius=.0025):routes.setdefault(color,[]).append((points,radius))
modules=[nodes[i] for i in panel['children'] if nodes[i]['name'] in ['UPS','SMPS','Redundancy_Module'] or nodes[i]['name'] in ['Center_Middle_UPS_1261','Center_Middle_Redundancy_Module_1276','Center_Middle_SMPS_1291']]
for module in modules:
    obj=bpy.data.objects[module['name']]
    # Replace the straight power-lead stubs with continuous curved routes into the ducts.
    module['children']=[i for i in module['children'] if not nodes[i].get('children')]
    for child in list(obj.children):
        if child.type=='EMPTY' and child.children:
            for leaf in list(child.children):bpy.data.objects.remove(leaf,do_unlink=True)
            bpy.data.objects.remove(child,do_unlink=True)
    x,y,z=module['translation'];upper=y>1
    for sign,duct in [(1,1.29 if upper else .97),(-1,.97 if upper else .51)]:
        for offset,color in [(-.025,'Red'),(.025,'Black')]:
            start=(x-.035,y+sign*.113,z+offset)
            wire(color,[start,(x-.110,y+sign*.135,z+offset),(-.145,(y+sign*.135+duct)/2,z+offset+.013),(-.055,duct,z+offset+.013)])
        if not upper:
            for offset in (-.040,.040):
                wire('Blue',[(x-.040,y+sign*.110,z+offset),(-.155,y+sign*.155,z+offset),(-.170,y+sign*.180,z+offset+.036),(-.055,duct,z+offset+.036)],.0028)
    if not upper:
        points=[(x-.030,y-.110,z),(-.140,y-.156,z-.025),(-.150,.565,z-.035),(-.055,.51,z-.035)]
        wire('Earth',points,.0028);wire('Yellow',[(a-.0025,b,c) for a,b,c in points],.0012)
# Upper control terminals: separate red/black loops enter both adjacent ducts.
for n in [nodes[i] for i in panel['children'] if nodes[i]['name'].startswith('Center_Upper_Terminal_Block_')]:
    x,y,z=n['translation']
    for sign,duct in [(1,1.29),(-1,.97)]:
        for offset,color in [(-.017,'Red'),(.017,'Black')]:
            wire(color,[(x-.027,y+sign*.026,z+offset),(-.140,y+sign*.075,z+offset),(-.135,duct-sign*.025,z+offset+.020),(-.055,duct,z+offset+.020)],.0020)
# Dense blue service bundle follows the right-hand duct, as in the supplied photo.
for number in range(20):
    offset=number*.0027
    wire('Blue',[(-.055,1.29,.480+offset),(-.120,1.225,.550+offset),(-.150,1.045,.565+offset),(-.145,.840,.550+offset),(-.135,.625,.555+offset),(-.055,.51,.480+offset)],.0022)
# Lower breaker-to-terminal and terminal-to-bottom-duct leads fill the remaining gaps.
breakers=[nodes[i] for i in panel['children'] if nodes[i]['name']=='Circuit_Breaker']
for n in breakers:
    x,y,z=n['translation']
    wire('Blue',[(x-.040,y-.095,z),(-.180,y-.110,z),(-.160,.215,z),(-.110,.190,z)],.0020)
for n in [nodes[i] for i in panel['children'] if nodes[i]['name']=='Terminal_Block']:
    x,y,z=n['translation']
    wire('White',[(x-.027,y-.026,z),(-.155,y-.055,z),(-.055,.100,z)],.0020)
materials={'Red':5,'Black':1,'Blue':8,'White':2,'Earth':9,'Yellow':7}
for color,paths in routes.items():
    name='Center_Wiring_'+color;data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.resolution_u=5
    data.bevel_depth=.0025;data.bevel_resolution=1;data.use_fill_caps=True
    for points,radius in paths:
        spline=data.splines.new('BEZIER');spline.bezier_points.add(len(points)-1)
        for point,(x,y,z) in zip(spline.bezier_points,points):
            point.co=(x,-z,y);point.handle_left_type='AUTO';point.handle_right_type='AUTO';point.radius=radius/.0025
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj)
    model.attach(obj,name,(0,0,0),materials[color],parent)
    nodes[lookup[name]]['extras']={'visual_only':True,'cable_count':len(paths)}
bpy.context.view_layer.update();out=root/'Blender/ESS_Center_Wiring';out.mkdir(exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'ESS_Center_Wiring.blend'));model.save(path)
print('CENTER_WIRING_SAVED:',{color:len(paths) for color,paths in routes.items()},'six merged color meshes')
