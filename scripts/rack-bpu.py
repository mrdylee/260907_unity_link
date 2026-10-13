"""Photo-guided bottom BPU on each rack; preserve seven black packs per rack."""
import bpy,sys,math,copy
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'scripts'))
from detail_export import DetailGLB
path=root/'public/models/ess-container.glb';model=DetailGLB(path)
doc,nodes,lookup=model.doc,model.nodes,model.lookup
assert 'BPU_01' not in lookup,'Use the pre-BPU model'
black=doc['materials'][6]['pbrMetallicRoughness']
doc['materials'][11]['pbrMetallicRoughness'].update({key:copy.deepcopy(black[key]) for key in ['baseColorFactor','metallicFactor','roughnessFactor']})
doc['materials'][11]['pbrMetallicRoughness']['roughnessFactor']=.72
doc['materials'][11].setdefault('extensions',{})['KHR_materials_specular']={'specularFactor':.18}
if 'KHR_materials_specular' not in doc.setdefault('extensionsUsed',[]):doc['extensionsUsed'].append('KHR_materials_specular')
shader=model.materials[11].node_tree.nodes.get('Principled BSDF')
shader.inputs['Base Color'].default_value=black['baseColorFactor'];shader.inputs['Metallic'].default_value=black['metallicFactor'];shader.inputs['Roughness'].default_value=.72;shader.inputs['Specular IOR Level'].default_value=.09
for number in range(1,7):
    rack=nodes[lookup[f'Battery_Rack_{number:02}']]
    packs=[nodes[i] for i in rack['children'] if nodes[i]['name'].startswith('Battery_Module_')]
    packs.sort(key=lambda n:n['translation'][1]);assert len(packs)==7
    for slot,pack in enumerate(packs):
        pack['translation'][1]=.500+slot*.252;bpy.data.objects[pack['name']].location.z=pack['translation'][1]
        for child in pack['children']:
            n=nodes[child]
            if n['name']=='Module_Face':doc['meshes'][n['mesh']]['primitives'][0]['material']=11
        for face in bpy.data.objects[pack['name']].children:
            if face.name.startswith('Module_Face'):
                face.data=face.data.copy();face.data.materials.clear();face.data.materials.append(model.materials[11])
png=root/'public/textures/bpu-face.png'
doc['images'].append({'name':'BPU front labels','bufferView':model.buffer(png.read_bytes()),'mimeType':'image/png'});doc['textures'].append({'source':len(doc['images'])-1})
print_material=len(doc['materials']);doc['materials'].append({'name':'BPU_Face_Print','pbrMetallicRoughness':{'baseColorTexture':{'index':len(doc['textures'])-1},'metallicFactor':0,'roughnessFactor':.36}})
mat=bpy.data.materials.new('BPU_Face_Print');mat.use_nodes=True
image=mat.node_tree.nodes.new('ShaderNodeTexImage');image.image=bpy.data.images.load(str(png));image.image.pack()
mat.node_tree.links.new(image.outputs['Color'],mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color']);model.materials[print_material]=mat
clear_material=len(doc['materials']);doc['materials'].append({'name':'BPU_Clear_Cover','alphaMode':'BLEND','doubleSided':True,'pbrMetallicRoughness':{'baseColorFactor':[.70,.80,.88,.24],'metallicFactor':0,'roughnessFactor':.18}})
mat=bpy.data.materials.new('BPU_Clear_Cover');mat.use_nodes=True;mat.diffuse_color=(.70,.80,.88,.24)
shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(.70,.80,.88,.24);shader.inputs['Alpha'].default_value=.24;shader.inputs['Roughness'].default_value=.18
model.materials[clear_material]=mat
parent=bpy.data.objects.new('BPU_01',None);bpy.context.collection.objects.link(parent);parent.parent=bpy.data.objects['Battery_Rack_01'];parent.location=(0,0,.235);parent.scale=(1,1,.25/.31)
index=len(nodes);nodes[lookup['Battery_Rack_01']]['children'].append(index);lookup['BPU_01']=index
nodes.append({'name':'BPU_01','translation':[0,.235,0],'scale':[1,.25/.31,1],'children':[]})
def mesh_object(name,vertices,faces):
    data=bpy.data.meshes.new(name);data.from_pydata([(x,-z,y) for x,y,z in vertices],[],faces);data.update()
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);return obj
def box(label,position,size,material):return model.box('BPU_01_'+label,position,size,material,parent)
def blocks(label,parts,material):
    vertices=[];faces=[]
    for x,y,z,sx,sy,sz in parts:
        base=len(vertices);vertices.extend((x+a*sx,y+b*sy,z+c*sz) for a,b,c in [(-.5,-.5,-.5),(.5,-.5,-.5),(.5,.5,-.5),(-.5,.5,-.5),(-.5,-.5,.5),(.5,-.5,.5),(.5,.5,.5),(-.5,.5,.5)])
        faces.extend(tuple(base+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(3,7,6,2),(0,4,7,3),(1,2,6,5)])
    return model.attach(mesh_object('BPU_01_'+label,vertices,faces),'BPU_01_'+label,(0,0,0),material,parent)
box('Case',(0,0,0),(.94,.31,1.04),6)
obj=mesh_object('BPU_01_Face_Print',[(-.47,-.155,.560),(.47,-.155,.560),(.47,.155,.560),(-.47,.155,.560)],[(0,1,2,3)])
layer=obj.data.uv_layers.new()
for i,uv in enumerate([(0,0),(1,0),(1,1),(0,1)]):layer.data[i].uv=uv
model.attach(obj,'BPU_01_Face_Print',(0,0,0),print_material,parent)
box('Vent',(0,.141,.564),(.60,.015,.012),1)
blocks('Vent_Dividers',[(x,.141,.573,.006,.020,.008) for x in [-.24,-.16,-.08,0,.08,.16,.24]],6)
box('Control_24V',(-.200,.039,.588),(.145,.083,.045),12)
box('Control_Clear_Cover',(-.195,.039,.615),(.092,.074,.015),clear_material)
box('Power_Switch_Frame',(.215,.067,.585),(.106,.050,.032),1)
box('Power_Switch',(.215,.067,.607),(.084,.032,.018),5)
blocks('Switch_Marks',[(.192,.067,.618,.009,.012,.002),(.241,.067,.618,.014,.002,.002)],2)
# The rack narrows X; compensate the fan so it remains circular in the assembled rack.
fan_x=(.25/.31)/(2/3)
bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.055,depth=.014)
obj=bpy.context.object;obj.rotation_euler=(math.pi/2,0,0);obj.scale.x=fan_x
model.attach(obj,'BPU_01_Fan',(.030,.030,.581),1,parent)
data=bpy.data.curves.new('BPU_01_Fan_Guard','CURVE');data.dimensions='3D';data.bevel_depth=.0020;data.bevel_resolution=1
paths=[]
for radius in [.057,.041,.026]:paths.append([( .030+fan_x*radius*math.cos(i*math.tau/32),.030+radius*math.sin(i*math.tau/32),.595) for i in range(33)])
for sx,sy in [(-1,-1),(-1,1),(1,-1),(1,1)]:paths.append([(.030+fan_x*sx*.057,.030+sy*.057,.595),(.030+fan_x*sx*.018,.030+sy*.018,.595)])
for points in paths:
    spline=data.splines.new('POLY');spline.points.add(len(points)-1)
    for point,(x,y,z) in zip(spline.points,points):point.co=(x,-z,y,1)
obj=bpy.data.objects.new('BPU_01_Fan_Guard',data);bpy.context.collection.objects.link(obj);model.attach(obj,obj.name,(0,0,0),3,parent)
blocks('Fan_Blades',[(.030,.030,.591,.016,.016,.002)]+[(.030+sx*.027,.030+sy*.027,.591,.031,.012,.002) for sx,sy in [(-1,-1),(-1,1),(1,-1),(1,1)]],6)
blocks('Terminal_Base',[(x,-.015,.581,.182,.185,.040) for x in [-.383,.383]],1)
blocks('Terminal_Busbars',[(x,-.015,.612,.124,.094,.016) for x in [-.383,.383]],7)
blocks('Terminal_Covers',[(x,-.015,.637,.187,.205,.034) for x in [-.383,.383]],clear_material)
blocks('Cover_Ribs',[(x+offset,-.015,.659,.006,.185,.006) for x in [-.383,.383] for offset in [-.080,-.040,0,.040,.080]]+[(x,y,.659,.178,.006,.006) for x in [-.383,.383] for y in [-.101,-.070,.040,.071]],clear_material)
blocks('Terminal_Bolts',[(x,-.015,.665,.036,.036,.014) for x in [-.383,.383]],3)
box('LAN_Frame',(-.160,-.105,.580),(.065,.043,.025),3)
box('LAN',(-.160,-.105,.597),(.053,.031,.011),1)
blocks('LAN_Contacts',[(-.160+(i-3.5)*.005,-.099,.605,.002,.011,.002) for i in range(8)],7)
blocks('Signal_Port_Frames',[(x,-.105,.580,w,.041,.025) for x,w in [(.145,.091),(.236,.048)]],3)
blocks('Signal_Ports',[(x,-.105,.596,w,.029,.010) for x,w in [(.145,.077),(.236,.034)]],1)
blocks('Signal_Contacts',[(.145+(i-5.5)*.005,-.104,.603,.002,.012,.002) for i in range(12)]+[(.236+(i-2.5)*.004,-.104,.603,.0015,.012,.002) for i in range(6)],3)
blocks('Mount_Screws',[(x,y,.566,.009,.009,.006) for x in [-.455,.455] for y in [-.142,.142]]+[(-.200+off,.039,.628,.010,.010,.004) for off in [-.040,0,.040]],3)
def clone_node(index,number):
    node=copy.deepcopy(nodes[index]);node['name']=node['name'].replace('BPU_01',f'BPU_{number:02}')
    new=len(nodes);nodes.append(node)
    if 'children' in node:node['children']=[clone_node(child,number) for child in node['children']]
    return new
def clone_object(obj,rack,number):
    duplicate=obj.copy();duplicate.name=obj.name.replace('BPU_01',f'BPU_{number:02}');bpy.context.collection.objects.link(duplicate);duplicate.parent=rack
    for child in obj.children:clone_object(child,duplicate,number)
for number in range(2,7):
    nodes[lookup[f'Battery_Rack_{number:02}']]['children'].append(clone_node(index,number))
    clone_object(parent,bpy.data.objects[f'Battery_Rack_{number:02}'],number)
bpy.context.view_layer.update();out=root/'Blender/ESS_Rack_BPU';out.mkdir(exist_ok=True);bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'ESS_Rack_BPU.blend'));model.save(path)
print('RACK_BPU_SAVED: six racks each contain seven black packs and one bottom BPU')
