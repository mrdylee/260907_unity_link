"""Small Blender-to-GLB mesh writer for the photo-detail scripts."""
import bpy,json,struct

class DetailGLB:
    def __init__(self,path):
        raw=path.read_bytes();length=struct.unpack_from('<I',raw,12)[0]
        self.doc=json.loads(raw[20:20+length]);self.nodes=self.doc['nodes']
        self.lookup={n['name']:i for i,n in enumerate(self.nodes)}
        size=struct.unpack_from('<I',raw,20+length)[0]
        self.binary=bytearray(raw[28+length:28+length+size])
        self.materials={i:bpy.data.materials.get(m['name']) for i,m in enumerate(self.doc['materials'])}
    def buffer(self,data,target=None):
        self.binary.extend(b'\0'*(-len(self.binary)%4));offset=len(self.binary);self.binary.extend(data)
        view={'buffer':0,'byteOffset':offset,'byteLength':len(data)}
        if target:view['target']=target
        self.doc['bufferViews'].append(view)
        return len(self.doc['bufferViews'])-1
    def accessor(self,values,kind,components):
        view=self.buffer(struct.pack('<'+'f'*len(values),*values),34962)
        item={'bufferView':view,'componentType':5126,'count':len(values)//components,'type':kind}
        if kind=='VEC3':
            item['min']=[min(values[i::components]) for i in range(components)]
            item['max']=[max(values[i::components]) for i in range(components)]
        self.doc['accessors'].append(item)
        return len(self.doc['accessors'])-1
    def mesh(self,obj,material):
        bpy.context.view_layer.update()
        evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());data=evaluated.to_mesh();data.calc_loop_triangles()
        positions=[];normals=[];uv=[]
        for triangle in data.loop_triangles:
            for index in triangle.loops:
                p=data.vertices[data.loops[index].vertex_index].co;n=data.corner_normals[index].vector
                positions.extend((p.x,p.z,-p.y));normals.extend((n.x,n.z,-n.y))
                if data.uv_layers.active:
                    value=data.uv_layers.active.data[index].uv;uv.extend((value.x,1-value.y))
        attributes={'POSITION':self.accessor(positions,'VEC3',3),'NORMAL':self.accessor(normals,'VEC3',3)}
        if uv:attributes['TEXCOORD_0']=self.accessor(uv,'VEC2',2)
        self.doc['meshes'].append({'name':obj.name,'primitives':[{'attributes':attributes,'material':material}]})
        evaluated.to_mesh_clear()
        return len(self.doc['meshes'])-1
    def attach(self,obj,name,position,material,parent):
        obj.name=name;obj.parent=parent;obj.location=(position[0],-position[2],position[1])
        obj.data.materials.clear();obj.data.materials.append(self.materials[material])
        q=obj.rotation_quaternion if obj.rotation_mode=='QUATERNION' else obj.rotation_euler.to_quaternion()
        node={'name':name,'mesh':self.mesh(obj,material),'translation':list(position),
              'rotation':[q.x,q.z,-q.y,q.w],'scale':[obj.scale.x,obj.scale.z,obj.scale.y]}
        self.nodes[self.lookup[parent.name]].setdefault('children',[]).append(len(self.nodes))
        self.lookup[name]=len(self.nodes);self.nodes.append(node)
        return obj
    def box(self,name,position,size,material,parent):
        bpy.ops.mesh.primitive_cube_add(size=1)
        obj=bpy.context.object;obj.scale=(size[0],size[2],size[1])
        return self.attach(obj,name,position,material,parent)
    def save(self,path):
        self.doc['buffers'][0]['byteLength']=len(self.binary);self.binary.extend(b'\0'*(-len(self.binary)%4))
        payload=json.dumps(self.doc,separators=(',',':')).encode();payload+=b' '*(-len(payload)%4)
        path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(payload)+len(self.binary))+struct.pack('<II',len(payload),0x4e4f534a)+payload+struct.pack('<II',len(self.binary),0x004e4942)+self.binary)
