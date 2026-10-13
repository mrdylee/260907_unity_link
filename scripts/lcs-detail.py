"""Rebuild the right-wall LCS from the user photo; Ethernet exits downward."""
import bpy,sys,math
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'scripts'))
from detail_export import DetailGLB
path=root/'public/models/ess-container.glb';model=DetailGLB(path)
doc,nodes,lookup=model.doc,model.nodes,model.lookup
assert 'LCS_Face_Print' not in lookup,'Use the pre-LCS-detail Blender and GLB pair'
parent=bpy.data.objects['LCS_Controller'];controller=nodes[lookup[parent.name]]
removed=set()
def collect(index):
    removed.add(index)
    for child in nodes[index].get('children',[]):collect(child)
for index in controller['children']:collect(index)
for obj in list(parent.children_recursive):bpy.data.objects.remove(obj,do_unlink=True)
controller['children']=[]
# The narrower housing still touches the original white wall with its rear face.
wall=nodes[lookup['Fixed_Louver_Panel']];panel=nodes[lookup['E_Panel_Detailed']]
controller['translation'][2]=wall['translation'][2]-wall['scale'][2]/2-panel['translation'][2]-.020
parent.location.y=-controller['translation'][2]
png=root/'public/textures/lcs-face.png'
doc['images'].append({'name':'LCS photographed faceplate markings','bufferView':model.buffer(png.read_bytes()),'mimeType':'image/png'})
doc['textures'].append({'source':len(doc['images'])-1})
print_material=len(doc['materials'])
doc['materials'].append({'name':'LCS_Face_Print','pbrMetallicRoughness':{'baseColorTexture':{'index':len(doc['textures'])-1},'metallicFactor':0,'roughnessFactor':.72}})
mat=bpy.data.materials.new('LCS_Face_Print');mat.use_nodes=True
shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Roughness'].default_value=.72
image=mat.node_tree.nodes.new('ShaderNodeTexImage');image.image=bpy.data.images.load(str(png));image.image.pack()
mat.node_tree.links.new(image.outputs['Color'],shader.inputs['Base Color']);model.materials[print_material]=mat
def mesh(name,vertices,faces):
    data=bpy.data.meshes.new(name);data.from_pydata([(x,-z,y) for x,y,z in vertices],[],faces);data.update()
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);return obj
def box(name,u,y,depth,width,height,thickness,material=6):
    return model.box(name,(-depth,y,u),(thickness,height,width),material,parent)
def blocks(name,parts,material):
    vertices=[];faces=[]
    for u,y,d,w,h,t in parts:
        base=len(vertices)
        vertices.extend((-d+a*t,y+b*h,u+c*w) for a,b,c in [(-.5,-.5,-.5),(.5,-.5,-.5),(.5,.5,-.5),(-.5,.5,-.5),(-.5,-.5,.5),(.5,-.5,.5),(.5,.5,.5),(-.5,.5,.5)])
        faces.extend(tuple(base+i for i in face) for face in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(3,7,6,2),(0,4,7,3),(1,2,6,5)])
    return model.attach(mesh(name,vertices,faces),name,(0,0,0),material,parent)
housing=box('LCS_Black_Housing',0,0,0,.50,.25,.04)
# Apply dimensions before beveling so the front corners and shallow sidewalls stay rounded.
bpy.context.view_layer.objects.active=housing;housing.select_set(True);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
bevel=housing.modifiers.new('Rounded LCS enclosure corners','BEVEL');bevel.width=.004;bevel.segments=3
nodes[lookup[housing.name]]['scale']=[1,1,1];nodes[lookup[housing.name]]['mesh']=model.mesh(housing,6)
obj=mesh('LCS_Face_Print',[(-.0204,-.119,-.244),(-.0204,-.119,.244),(-.0204,.119,.244),(-.0204,.119,-.244)],[(0,1,2,3)])
layer=obj.data.uv_layers.new()
for i,uv in enumerate([(0,0),(1,0),(1,1),(0,1)]):layer.data[i].uv=uv
model.attach(obj,obj.name,(0,0,0),print_material,parent)
# Four unequal terminal banks along each edge, matching the photographed divisions.
banks=[('Top',.095,[(.315,.198,12),(.571,.210,12),(.747,.138,8),(.900,.154,8)]),('Bottom',-.093,[(.361,.128,8),(.585,.206,12),(.761,.138,8),(.915,.150,8)])]
openings=[];contacts=[];separators=[]
for row,y,groups in banks:
    for number,(center,width,count) in enumerate(groups,1):
        u=(center-.5)*.488;w=width*.488
        box(f'LCS_{row}_Terminal_Recess_{number}',u,y,.025,w+.005,.030,.010,1)
        box(f'LCS_{row}_Terminal_Bank_{number}',u,y,.032,w,.013,.014,9)
        for pin in range(count):
            px=u+(pin-(count-1)/2)*w/count
            openings.append((px,y+(.010 if row=='Top' else -.010),.032,w/count*.72,.008,.008))
            contacts.append((px,y,.040,w/count*.46,.004,.002))
            separators.append((px-w/count*.48,y,.041,.0006,.012,.001))
blocks('LCS_Terminal_Openings',openings,1)
blocks('LCS_Terminal_Contacts',contacts,3)
blocks('LCS_Terminal_Dividers',separators,9)
def cylinder(name,u,y,depth,radius,thickness,material):
    bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=radius,depth=thickness)
    obj=bpy.context.object;obj.rotation_euler=(0,math.pi/2,0)
    return model.attach(obj,name,(-depth,y,u),material,parent)
for number,(u,y) in enumerate([(-.237,.110),(.237,.110),(-.237,-.110),(.237,-.110)],1):
    cylinder(f'LCS_Mount_Recess_{number}',u,y,.022,.013,.006,1)
    cylinder(f'LCS_Mount_Screw_{number}',u,y,.026,.007,.003,3)
blocks('LCS_Screw_Crosses',[(u,y,.028,w,h,.001) for u in [-.237,.237] for y in [-.110,.110] for w,h in [(.008,.0015),(.0015,.008)]],1)
cylinder('LCS_Upper_Recess',-.165,.100,.022,.010,.004,1)
# The Ethernet jack is in the lower edge, not on the top or the front face.
box('LCS_LAN_Socket',-.147,-.123,.008,.028,.017,.022,3)
box('LCS_LAN_Opening',-.147,-.132,.008,.021,.002,.017,1)
box('LCS_LAN_Plug',-.147,-.139,.008,.019,.015,.015,6)
box('LCS_LAN_Boot',-.147,-.161,.008,.015,.030,.015,1)
blocks('LCS_LAN_Boot_Ribs',[(-.147,y,.008,.018,.002,.018) for y in [-.149,-.155,-.161,-.167,-.173]],6)
box('LCS_Power_Terminal',-.203,-.090,.032,.028,.012,.015,9)
blocks('LCS_Power_Contacts',[(-.211+i*.008,-.090,.041,.003,.004,.002) for i in range(3)],3)
def cable(name,points,material,radius):
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.resolution_u=12;data.bevel_depth=radius;data.bevel_resolution=2
    spline=data.splines.new('BEZIER');spline.bezier_points.add(len(points)-1)
    for point,(u,y,d) in zip(spline.bezier_points,points):
        point.co=(-d,-u,y);point.handle_left_type='AUTO';point.handle_right_type='AUTO'
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);model.attach(obj,name,(0,0,0),material,parent)
cable('LCS_LAN_Cable',[(-.147,-.176,.008),(-.147,-.222,.018),(-.125,-.310,.072),(-.170,-.455,.15),(-.215,-.510,.185)],6,.0035)
for name,offset,material in [('Red',0,5),('Black',.009,6)]:
    cable('LCS_Power_Wire_'+name,[(-.211+offset,-.096,.041),(-.220+offset,-.12,.058),(-.199+offset,-.18,.065),(-.180+offset,-.29,.075),(-.195+offset,-.46,.15),(-.209+offset,-.510,.185)],material,.0015)
bpy.context.view_layer.update()
out=root/'Blender/ESS_LCS_Detail';out.mkdir(exist_ok=True);bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'ESS_LCS_Detail.blend'))
# Remove the replaced LCS nodes; preserve all unrelated node indices through remapping.
assert not doc.get('animations') and not doc.get('skins')
remap={old:new for new,old in enumerate(i for i in range(len(nodes)) if i not in removed)}
doc['nodes']=[node for i,node in enumerate(nodes) if i not in removed]
for node in doc['nodes']:
    if 'children' in node:node['children']=[remap[i] for i in node['children'] if i not in removed]
for scene in doc['scenes']:scene['nodes']=[remap[i] for i in scene['nodes']]
model.save(path)
print('LCS_DETAIL_SAVED: shallow black case, eight terminal banks, bottom Ethernet, flush white-wall mounting')
