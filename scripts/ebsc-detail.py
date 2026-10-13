"""Run once on ESS_Vent_Layout.blend with its GLB; retain baked PBR data."""
import bpy, json, struct, math, sys
from pathlib import Path
from mathutils import Vector, Quaternion

root=Path(__file__).resolve().parents[1]
path=root/'public/models/ess-container.glb'
source=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else path
raw=source.read_bytes();length=struct.unpack_from('<I',raw,12)[0]
doc=json.loads(raw[20:20+length]);nodes=doc['nodes']
lookup={n['name']:i for i,n in enumerate(nodes)}
assert 'eBSC_USB' not in lookup, 'Use the model before eBSC detailing'
bin_length=struct.unpack_from('<I',raw,20+length)[0]
binary=bytearray(raw[28+length:28+length+bin_length])
ebsc=bpy.data.objects['eBSC_Controller'];ebsc_node=nodes[lookup['eBSC_Controller']]
material_objects={i:bpy.data.materials.get(m['name']) for i,m in enumerate(doc['materials'])}

def buffer(data,target=None):
    binary.extend(b'\0'*(-len(binary)%4));offset=len(binary);binary.extend(data)
    view={'buffer':0,'byteOffset':offset,'byteLength':len(data)}
    if target:view['target']=target
    doc['bufferViews'].append(view)
    return len(doc['bufferViews'])-1

def accessor(values,kind,components):
    view=buffer(struct.pack('<'+'f'*len(values),*values),34962)
    item={'bufferView':view,'componentType':5126,'count':len(values)//components,'type':kind}
    if kind=='VEC3':
        item['min']=[min(values[i::components]) for i in range(components)]
        item['max']=[max(values[i::components]) for i in range(components)]
    doc['accessors'].append(item)
    return len(doc['accessors'])-1

def mesh(obj,material):
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    data=evaluated.to_mesh();data.calc_loop_triangles()
    positions=[];normals=[];uv=[]
    for triangle in data.loop_triangles:
        for index in triangle.loops:
            p=data.vertices[data.loops[index].vertex_index].co
            n=data.corner_normals[index].vector
            positions.extend((p.x,p.z,-p.y));normals.extend((n.x,n.z,-n.y))
            if data.uv_layers.active:
                value=data.uv_layers.active.data[index].uv;uv.extend((value.x,1-value.y))
    attributes={'POSITION':accessor(positions,'VEC3',3),'NORMAL':accessor(normals,'VEC3',3)}
    if uv:attributes['TEXCOORD_0']=accessor(uv,'VEC2',2)
    doc['meshes'].append({'name':obj.name,'primitives':[{'attributes':attributes,'material':material}]})
    evaluated.to_mesh_clear()
    return len(doc['meshes'])-1

def attach(obj,name,position,material,parent=ebsc):
    obj.name=name;obj.parent=parent;obj.location=(position[0],-position[2],position[1])
    obj.data.materials.clear();obj.data.materials.append(material_objects[material])
    bpy.context.view_layer.update()
    q=obj.rotation_quaternion if obj.rotation_mode=='QUATERNION' else obj.rotation_euler.to_quaternion()
    node={'name':name,'mesh':mesh(obj,material),'translation':list(position),
          'rotation':[q.x,q.z,-q.y,q.w],'scale':[obj.scale.x,obj.scale.z,obj.scale.y]}
    parent_node=nodes[lookup[parent.name]]
    parent_node.setdefault('children',[]).append(len(nodes));lookup[name]=len(nodes);nodes.append(node)
    return obj

def box(name,position,size,material,parent=ebsc):
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj=bpy.context.object;obj.scale=(size[0],size[2],size[1])
    return attach(obj,name,position,material,parent)

# A single printed face carries the small text instead of letter meshes.
png=root/'public/textures/ebsc-face.png'
doc.setdefault('images',[]).append({'name':'eBSC face print','bufferView':buffer(png.read_bytes()),'mimeType':'image/png'})
doc.setdefault('textures',[]).append({'source':len(doc['images'])-1})
print_material=len(doc['materials'])
doc['materials'].append({'name':'eBSC_Face_Print','pbrMetallicRoughness':{'baseColorTexture':{'index':len(doc['textures'])-1},'metallicFactor':0,'roughnessFactor':.42}})
mat=bpy.data.materials.new('eBSC_Face_Print');mat.use_nodes=True
shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Roughness'].default_value=.42
texture=mat.node_tree.nodes.new('ShaderNodeTexImage');texture.image=bpy.data.images.load(str(png));texture.image.pack()
mat.node_tree.links.new(texture.outputs['Color'],shader.inputs['Base Color']);material_objects[print_material]=mat

housing=bpy.data.objects['eBSC_Housing'];housing.data=housing.data.copy();housing.scale.y=.08
bevel=housing.modifiers.new('Soft metal case edges','BEVEL');bevel.width=.008;bevel.segments=2
bpy.context.view_layer.update()
nodes[lookup['eBSC_Housing']]['scale']=[housing.scale.x,housing.scale.z,housing.scale.y]
nodes[lookup['eBSC_Housing']]['mesh']=mesh(housing,6)
face=bpy.data.meshes.new('eBSC printed face')
face.from_pydata([(-.0715,.038,-.158),(-.0715,-.038,-.158),(-.0715,-.038,.158),(-.0715,.038,.158)],[],[(0,1,2,3)])
layer=face.uv_layers.new();
for index,uv in enumerate([(0,0),(1,0),(1,1),(0,1)]):layer.data[index].uv=uv
obj=bpy.data.objects.new('eBSC_Face_Print',face);bpy.context.collection.objects.link(obj)
attach(obj,'eBSC_Face_Print',(0,0,0),print_material)

for number,z,material in [(1,-.007,9),(2,.003,7),(3,.013,5)]:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=1)
    obj=bpy.context.object;obj.scale=(.0018,.0026,.0026)
    attach(obj,f'eBSC_LED_{number}',(-.0745,.104,z),material)

# User requested both USB and UART openings as rectangular USB 2.0 sockets.
for name,y in [('USB',.084),('UART',.052)]:
    box(f'eBSC_{name}',(-.075,y,.008),(.007,.013,.026),3)
    box(f'eBSC_{name}_Opening',(-.079,y,.008),(.0015,.009,.022),1)
    box(f'eBSC_{name}_Tongue',(-.080,y-.0015,.008),(.001,.002,.018),2)
for number,y,z in [(1,.149,-.030),(2,.149,.030),(3,-.151,-.030),(4,-.151,.030)]:
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.0018,depth=.0014)
    obj=bpy.context.object;obj.rotation_euler=(0,math.pi/2,0)
    attach(obj,f'eBSC_Case_Screw_{number}',(-.073,y,z),3)

for number in range(1,5):
    name=f'eBSC_LAN_{number}';node=nodes[lookup[name]];port=bpy.data.objects[name]
    node['translation']=[-.074,.015-(number-1)*.043,.008]
    port.location=(node['translation'][0],-node['translation'][2],node['translation'][1])
    for index in node['children']:
        child=nodes[index]
        original=Vector((child['translation'][0],-child['translation'][2],child['translation'][1]))
        obj=min(port.children,key=lambda o:(o.location-original).length)
        socket=child['name']=='RJ45_Socket'
        child['scale']=[.013,.022 if socket else .028,.023 if socket else .029]
        obj.scale=(child['scale'][0],child['scale'][2],child['scale'][1])
        if socket:
            child['translation'][0]=-.003;child['scale'][0]=.003
            obj.location.x=-.003;obj.scale.x=.003
            obj.data=obj.data.copy();obj.data.materials.clear();obj.data.materials.append(material_objects[1])
            doc['meshes'][child['mesh']]['primitives'][0]['material']=1
        else:
            # An actual open metal rim, with a recessed black socket behind it.
            vertices=[]
            for x in (-.5,.5):
                for half_y,half_z in ((.5,.5),(.39,.40)):
                    vertices.extend((x,-z,y) for y,z in [(-half_y,-half_z),(-half_y,half_z),(half_y,half_z),(half_y,-half_z)])
            faces=[]
            for c in range(4):
                n=(c+1)%4
                faces.extend([(c,n,4+n,4+c),(8+c,12+c,12+n,8+n),(c,8+c,8+n,n),(4+c,4+n,12+n,12+c)])
            data=bpy.data.meshes.new('Open RJ45 metal rim');data.from_pydata(vertices,[],faces)
            obj.data=data;obj.data.materials.append(material_objects[3])
            child['mesh']=mesh(obj,3)
    vertices=[];faces=[]
    for pin in range(8):
        z=(pin-3.5)*.0024;base=len(vertices)
        vertices.extend((-.0055,-horizontal,vertical) for vertical,horizontal in [(.002,z-.0006),(.002,z+.0006),(.009,z+.0006),(.009,z-.0006)])
        faces.append((base,base+1,base+2,base+3))
    data=bpy.data.meshes.new('Eight RJ45 contacts');data.from_pydata(vertices,[],faces)
    obj=bpy.data.objects.new(f'eBSC_LAN_Contacts_{number}',data);bpy.context.collection.objects.link(obj)
    attach(obj,f'eBSC_LAN_Contacts_{number}',(0,0,0),7,port)
    if number<=2:
        # Ribbed yellow strain relief and a white sleeve on connected LAN ports.
        profile=[(-.006,.024),(-.020,.024),(-.023,.020),(-.026,.022),(-.029,.018),(-.032,.020),(-.035,.016),(-.038,.018),(-.047,.009)]
        vertices=[(x,-z,y) for x,width in profile for y,z in [(-width/2,-width/2),(-width/2,width/2),(width/2,width/2),(width/2,-width/2)]]
        faces=[(0,3,2,1),(len(vertices)-4,len(vertices)-3,len(vertices)-2,len(vertices)-1)]
        faces.extend((r*4+c,r*4+(c+1)%4,(r+1)*4+(c+1)%4,(r+1)*4+c) for r in range(len(profile)-1) for c in range(4))
        data=bpy.data.meshes.new('Ribbed RJ45 boot');data.from_pydata(vertices,[],faces)
        obj=bpy.data.objects.new(f'eBSC_RJ45_Boot_{number}',data);bpy.context.collection.objects.link(obj)
        attach(obj,f'eBSC_RJ45_Boot_{number}',(0,0,0),7,port)
        box(f'eBSC_Cable_Sleeve_{number}',(-.049,0,0),(.013,.011,.011),2,port)

# Move both existing links with their ports; keep endpoints exactly connected.
def point(parent,name):
    q=parent['rotation']
    return Vector(parent['translation'])+Quaternion((q[3],q[0],q[1],q[2]))@Vector(nodes[lookup[name]]['translation'])
switch=nodes[lookup['Network_Switch_IE3500']]
for number in (1,2):
    link=nodes[lookup[f'Switch_eBSC_Link_{number}']]
    start=point(ebsc_node,link['extras']['from']);end=point(switch,link['extras']['to'])
    front=start.z+.09+number*.025
    points=[start,Vector((start.x,start.y,front)),Vector((end.x,end.y,front)),end]
    for index,(a,b) in zip(link['children'],zip(points,points[1:])):
        node=nodes[index];middle=(a+b)/2;delta=b-a;q=Vector((0,1,0)).rotation_difference(delta.normalized())
        node.update(translation=list(middle),rotation=[q.x,q.y,q.z,q.w],scale=[.007,delta.length/2,.007])
        obj=bpy.data.objects[node['name']]
        obj.location=(middle.x,-middle.z,middle.y);obj.rotation_mode='QUATERNION'
        obj.rotation_quaternion=Vector((0,0,1)).rotation_difference(Vector((delta.x,-delta.z,delta.y)).normalized())
        # These source cylinders have baked radius and length rather than unit geometry.
        obj.data=obj.data.copy()
        size=max(v.co.z for v in obj.data.vertices)-min(v.co.z for v in obj.data.vertices)
        obj.scale=(1,1,1)
        for vertex in obj.data.vertices:vertex.co.z*=delta.length/size

bpy.context.view_layer.update()
out=root/'Blender/ESS_eBSC_Detail';out.mkdir(exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'ESS_eBSC_Detail.blend'))
doc['buffers'][0]['byteLength']=len(binary)
binary.extend(b'\0'*(-len(binary)%4))
payload=json.dumps(doc,separators=(',',':')).encode();payload+=b' '*(-len(payload)%4)
path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(payload)+len(binary))+struct.pack('<II',len(payload),0x4e4f534a)+payload+struct.pack('<II',len(binary),0x004e4942)+binary)
print('eBSC_DETAIL_SAVED: LEDs, USB/UART rectangles, face print and two RJ45 boots')
