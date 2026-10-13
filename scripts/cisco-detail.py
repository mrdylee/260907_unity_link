"""Photo-guided IE3500 + IEM3500 joined assembly, preserving all baked PBR."""
import bpy,sys,math
from pathlib import Path
from mathutils import Vector,Quaternion
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'scripts'))
from detail_export import DetailGLB
path=root/'public/models/ess-container.glb';model=DetailGLB(path)
doc,nodes,lookup=model.doc,model.nodes,model.lookup
assert 'IE3500_Face_Print' not in lookup, 'Use the pre-detail switch assembly'
main=nodes[lookup['Network_Switch_IE3500']];ext=nodes[lookup['Extended_Switch']]
nodes[lookup['IEM3500_Expansion']]['scale'][2]=.178
bpy.data.objects['IEM3500_Expansion'].scale.y=.178
ext['translation'][0]=main['translation'][0]-(.19+.178)/2-.0015
bpy.data.objects['Extended_Switch'].location.x=ext['translation'][0]

def object_mesh(name,vertices,faces):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update()
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);return obj
def blocks(name,parts,material,parent,sign):
    vertices=[];faces=[]
    for depth,y,z,dx,dy,dz in parts:
        base=len(vertices)
        vertices.extend((-depth+x,-(sign*z+horizontal),sign*y+vertical) for x,vertical,horizontal in [(-dx/2,-dy/2,-dz/2),(dx/2,-dy/2,-dz/2),(dx/2,dy/2,-dz/2),(-dx/2,dy/2,-dz/2),(-dx/2,-dy/2,dz/2),(dx/2,-dy/2,dz/2),(dx/2,dy/2,dz/2),(-dx/2,dy/2,dz/2)])
        faces.extend(tuple(base+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(3,7,6,2),(0,4,7,3),(1,2,6,5)])
    return model.attach(object_mesh(name,vertices,faces),name,(0,0,0),material,parent)
def box(name,depth,y,z,size,material,parent,sign):
    return model.box(name,(-depth,sign*y,sign*z),size,material,parent)
def ring_data():
    vertices=[]
    for x in (-.5,.5):
        for hy,hz in ((.5,.5),(.40,.39)):
            vertices.extend((x,-z,y) for y,z in [(-hy,-hz),(-hy,hz),(hy,hz),(hy,-hz)])
    faces=[]
    for c in range(4):
        n=(c+1)%4;faces.extend([(c,n,4+n,4+c),(8+c,12+c,12+n,8+n),(c,8+c,8+n,n),(4+c,4+n,12+n,12+c)])
    return vertices,faces
def port(name,y,z,parent,sign,sfp=False):
    node=nodes[lookup[name]];obj=bpy.data.objects[name]
    node['translation']=[-.074,sign*y,sign*z];obj.location=(-.074,-sign*z,sign*y)
    for index in node['children']:
        child=nodes[index];old=Vector((child['translation'][0],-child['translation'][2],child['translation'][1]))
        leaf=min(obj.children,key=lambda o:(o.location-old).length)
        rim=child['name']=='Yellow_Port_Border'
        if rim:
            verts,faces=ring_data();leaf.data=object_mesh('Socket rim geometry',verts,faces).data
            temporary=bpy.data.objects.get('Socket rim geometry');bpy.data.objects.remove(temporary,do_unlink=True)
            child['scale']=[.009,.035 if sfp else .030,.026 if sfp else .031]
            leaf.scale=(child['scale'][0],child['scale'][2],child['scale'][1]);child['mesh']=model.mesh(leaf,3)
            leaf.data.materials.clear();leaf.data.materials.append(model.materials[3])
        else:
            child['translation'][0]=-.002;child['scale']=[.003,.028 if sfp else .024,.020 if sfp else .025]
            leaf.location.x=-.002;leaf.scale=(child['scale'][0],child['scale'][2],child['scale'][1])
            leaf.data=leaf.data.copy();leaf.data.materials.clear();leaf.data.materials.append(model.materials[1]);doc['meshes'][child['mesh']]['primitives'][0]['material']=1
    return obj,node
main_obj=bpy.data.objects['Network_Switch_IE3500'];ext_obj=bpy.data.objects['Extended_Switch']
rows=[.120,.088,.056,.024,-.024,-.056,-.088,-.120]
for number,y in enumerate(rows,4):port(f'Main_RJ45_1_{number}',y,.014,main_obj,-1)
for number in range(1,4):port(f'Main_SFP_1_{number}',.040-(number-1)*.040,-.052,main_obj,-1,True)
for number in range(1,15):
    n=nodes[lookup[f'Expansion_RJ45_2_{number}']];port(n['name'],n['translation'][1],n['translation'][2],ext_obj,1)
for number,z in [(15,-.032),(16,.032)]:port(f'Expansion_SFP_2_{number}',-.130,z,ext_obj,1,True)

png=root/'public/textures/cisco-face.png'
doc['images'].append({'name':'Cisco face print','bufferView':model.buffer(png.read_bytes()),'mimeType':'image/png'});doc['textures'].append({'source':len(doc['images'])-1})
material=len(doc['materials']);doc['materials'].append({'name':'Cisco_Face_Print','pbrMetallicRoughness':{'baseColorTexture':{'index':len(doc['textures'])-1},'metallicFactor':0,'roughnessFactor':.46}})
mat=bpy.data.materials.new('Cisco_Face_Print');mat.use_nodes=True
image=mat.node_tree.nodes.new('ShaderNodeTexImage');image.image=bpy.data.images.load(str(png));image.image.pack()
mat.node_tree.links.new(image.outputs['Color'],mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color']);model.materials[material]=mat
for prefix,body,parent,width,sign,u in [('IE3500','IE3500_Main',main_obj,.19,-1,.5),('IEM3500','IEM3500_Expansion',ext_obj,.178,1,0)]:
    housing=bpy.data.objects[body];housing.data=housing.data.copy();bevel=housing.modifiers.new('Rounded metal chassis','BEVEL');bevel.width=.01;bevel.segments=2
    nodes[lookup[body]]['mesh']=model.mesh(housing,6)
    obj=object_mesh(prefix+'_Face_Print',[(-.0718,(width-.004)/2,-.153),(-.0718,-(width-.004)/2,-.153),(-.0718,-(width-.004)/2,.153),(-.0718,(width-.004)/2,.153)],[(0,1,2,3)])
    layer=obj.data.uv_layers.new();uvs=[(u,0),(u+.5,0),(u+.5,1),(u,1)] if sign==1 else [(u+.5,1),(u,1),(u,0),(u+.5,0)]
    for i,uv in enumerate(uvs):layer.data[i].uv=uv
    model.attach(obj,prefix+'_Face_Print',(0,0,0),material,parent)
    fins=[(-.030+i*.009,y,0,.004,.008,width-.008) for i in range(11) for y in (-.153,.153)]
    blocks(prefix+'_Heatsink',fins,6,parent,sign)
    screws=[(.076,y,z,.003,.005,.005) for y in (-.145,.145) for z in (-width/2+.008,width/2-.008)]
    blocks(prefix+'_Mount_Screws',screws,3,parent,sign)
    contacts=[]
    for child in nodes[lookup[parent.name]]['children']:
        n=nodes[child]
        if 'RJ45' not in n['name'] or n['name'].endswith('Plug'):continue
        if not n['name'].startswith(('Main_RJ45_','Expansion_RJ45_')):continue
        for pin in range(8):contacts.append((.078,sign*n['translation'][1]+.005,sign*n['translation'][2]+(pin-3.5)*.0025,.001,.005,.001))
    blocks(prefix+'_RJ45_Contacts',contacts,7,parent,sign)
# Shared yellow outlines: two copper groups, one three-slot SFP group.
for name,y,z,height,width in [('Copper_Upper',.072,.014,.132,.041),('Copper_Lower',-.072,.014,.132,.041),('SFP_Group',0,-.052,.122,.032)]:
    parts=[(.076,y-height/2,z,.002,.002,width),(.076,y+height/2,z,.002,.002,width),(.076,y,z-width/2,.002,height,.002),(.076,y,z+width/2,.002,height,.002)]
    blocks('IE3500_'+name,parts,7,main_obj,-1)
box('IE3500_Console',.078,.103,-.067,(.006,.025,.025),3,main_obj,-1)
box('IE3500_Console_Opening',.082,.103,-.067,(.002,.019,.019),1,main_obj,-1)
box('IE3500_USB_Cover',.076,-.099,-.046,(.007,.082,.030),6,main_obj,-1)
obj=object_mesh('IE3500_USB_Cover_Print',[(-.080,-z,-y) for y,z in [(-.125,-.061),(-.125,-.037),(-.104,-.037),(-.104,-.061)]],[(0,1,2,3)])
layer=obj.data.uv_layers.new()
for i,(y,z) in enumerate([(-.125,-.061),(-.125,-.037),(-.104,-.037),(-.104,-.061)]):layer.data[i].uv=(.5+(z/.19+.5)*.5,(y+.155)/.31)
model.attach(obj,'IE3500_USB_Cover_Print',(0,0,0),material,main_obj)
box('IE3500_Console_Cover',.074,.111,-.037,(.005,.067,.020),6,main_obj,-1)
parts=[(.080,y,.065,.018,.038,.026) for y in (.094,.034)]+[(.082,-.099,.064,.018,.073,.019)]
blocks('IE3500_Power_Alarm_Terminals',parts,6,main_obj,-1)
parts=[(.091,y+dy,.065,.003,.006,.009) for y in (.094,.034) for dy in (-.013,0,.013)]+[(.093,-.074-i*.010,.064,.003,.003,.005) for i in range(6)]
blocks('IE3500_Terminal_Contacts',parts,3,main_obj,-1)
box('IE3500_Ground_Strap',.078,-.101,.084,(.006,.054,.012),3,main_obj,-1)
for name,y in [('Top',.140),('Bottom',-.140)]:box('Cisco_Coupling_'+name,-.025,y,-.095,(.020,.015,.024),3,main_obj,-1)
for number in range(1,7):
    parent=bpy.data.objects[f'Expansion_RJ45_2_{number}']
    model.box(f'RBMS_RJ45_Plug_{number}',(-.014,0,0),(.026,.018,.018),2,parent)
    model.box(f'RBMS_Strain_Relief_{number}',(-.030,0,0),(.009,.011,.011),10,parent)
for number in (4,5):model.box(f'Main_RJ45_Plug_{number}',(-.014,0,0),(.026,.018,.018),7,bpy.data.objects[f'Main_RJ45_1_{number}'])

def point(parent,name):
    q=parent['rotation'];return Vector(parent['translation'])+Quaternion((q[3],q[0],q[1],q[2]))@Vector(nodes[lookup[name]]['translation'])
ebsc=nodes[lookup['eBSC_Controller']]
for number in (1,2):
    link=nodes[lookup[f'Switch_eBSC_Link_{number}']];start=point(ebsc,link['extras']['from']);end=point(main,link['extras']['to']);front=start.z+.09+number*.025
    points=[start,Vector((start.x,start.y,front)),Vector((end.x,end.y,front)),end]
    for index,(a,b) in zip(link['children'],zip(points,points[1:])):
        n=nodes[index];middle=(a+b)/2;delta=b-a;q=Vector((0,1,0)).rotation_difference(delta.normalized())
        n.update(translation=list(middle),rotation=[q.x,q.y,q.z,q.w],scale=[.007,delta.length/2,.007])
        obj=bpy.data.objects[n['name']];obj.data=obj.data.copy();size=max(v.co.z for v in obj.data.vertices)-min(v.co.z for v in obj.data.vertices)
        for v in obj.data.vertices:v.co.z*=delta.length/size
        obj.location=(middle.x,-middle.z,middle.y);obj.scale=(1,1,1);obj.rotation_mode='QUATERNION';obj.rotation_quaternion=Vector((0,0,1)).rotation_difference(Vector((delta.x,-delta.z,delta.y)).normalized())
bpy.context.view_layer.update();out=root/'Blender/ESS_Cisco_Detail';out.mkdir(exist_ok=True);bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'ESS_Cisco_Detail.blend'));model.save(path)
print('CISCO_DETAIL_SAVED: joined cases, front labels, socket contacts, plugs, fins and terminals')
