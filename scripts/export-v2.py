"""Build web GLB from the verified Blender MCP → Unity export. Requires Pillow."""
import io, json, re, struct
from pathlib import Path
from PIL import Image, ImageChops
ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT/'Blender/UnityTransfer/model.json').read_text())
g = {'asset': {'version':'2.0','generator':'ESS verified Blender v2 export'},'scene':0,'scenes':[{'nodes':[0]}], 'nodes':[], 'meshes':[], 'materials':[], 'textures':[], 'images':[], 'samplers':[{'magFilter':9729,'minFilter':9987,'wrapS':10497,'wrapT':10497}], 'accessors':[], 'bufferViews':[], 'buffers':[]}
binary = bytearray()
def view(raw, target=None):
    binary.extend(b'\0' * (-len(binary)%4)); v={'buffer':0,'byteOffset':len(binary),'byteLength':len(raw)}
    if target:v['target']=target
    binary.extend(raw);g['bufferViews'].append(v);return len(g['bufferViews'])-1

def accessor(values, width, kind='f', bounds=False):
    a={'bufferView':view(struct.pack('<'+kind*len(values),*values),34963 if kind=='I' else 34962),'componentType':5125 if kind=='I' else 5126,'count':len(values)//width,'type':{1:'SCALAR',2:'VEC2',3:'VEC3'}[width]}
    if bounds:a.update(min=[min(values[i::width]) for i in range(width)],max=[max(values[i::width]) for i in range(width)])
    g['accessors'].append(a);return len(g['accessors'])-1

def image(raw):
    g['images'].append({'bufferView':view(raw),'mimeType':'image/png'})
    g['textures'].append({'sampler':0,'source':len(g['images'])-1});return {'index':len(g['textures'])-1}

def clean(name):return re.sub(r'\.\d{3}$','',name)
for m in data['materials']:
    pbr={'baseColorFactor':m['color'],'metallicFactor':m['metallic'],'roughnessFactor':m['roughness']}
    mat={'name':clean(m['name']),'pbrMetallicRoughness':pbr}
    if m['role']:
        base=ROOT/'UnityProject/Assets/ESS_Blender_v2/Textures'/m['role']
        mat['normalTexture']=image(Path(str(base)+'_Normal.png').read_bytes())
        mask=Image.open(str(base)+'_MetallicSmoothness.png').convert('RGBA');r,_,_,a=mask.split()
        out=Image.merge('RGB',(Image.new('L',mask.size,255),ImageChops.invert(a),r));buf=io.BytesIO();out.save(buf,format='PNG')
        pbr.update(metallicFactor=1,roughnessFactor=1,metallicRoughnessTexture=image(buf.getvalue()))
    g['materials'].append(mat)
for n in data['nodes']:
    x,y,z=n['position'];qx,qy,qz,qw=n['rotation']
    node={'name':clean(n['name']),'translation':[x,y,-z],'rotation':[-qx,-qy,qz,qw],'scale':n['scale']}
    if n['mesh']>=0:
        m=data['meshes'][n['mesh']];v=m['vertices'];normal=m['normals'];uv=m['uv'];tri=m['triangles']
        attrs={'POSITION':accessor([(-a if i%3==2 else a) for i,a in enumerate(v)],3,bounds=True),'NORMAL':accessor([(-a if i%3==2 else a) for i,a in enumerate(normal)],3),'TEXCOORD_0':accessor([(1-a if i%2 else a) for i,a in enumerate(uv)],2)}
        indices=[tri[k+j] for k in range(0,len(tri),3) for j in (0,2,1)]
        g['meshes'].append({'primitives':[{'attributes':attrs,'indices':accessor(indices,1,'I'),'material':n['material']}]});node['mesh']=len(g['meshes'])-1
    g['nodes'].append(node)
for i,n in enumerate(data['nodes']):
    if n['parent']>=0:g['nodes'][n['parent']].setdefault('children',[]).append(i)
g['buffers']=[{'byteLength':len(binary)}]
js=json.dumps(g,separators=(',',':')).encode();js+=b' '*(-len(js)%4);binary+=b'\0'*(-len(binary)%4)
result=struct.pack('<III',0x46546c67,2,12+8+len(js)+8+len(binary))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(binary),0x004e4942)+binary
(ROOT/'public/models/ess-container.glb').write_bytes(result)
p=ROOT/'public/models/manifest.json';manifest=json.loads(p.read_text());manifest.update(materials=len(g['materials']),uniqueGeometries=len(g['meshes']),modelVersion='Blender realistic materials v2',embeddedTextures=len(g['textures']))
for door in manifest['doors']:
    if door['name'].startswith('Door_Hinge_'):door['openDegrees']=105
p.write_text(json.dumps(manifest,indent=2)+'\n')
print(f'GLB: {len(g["nodes"])} nodes, {len(g["meshes"])} meshes, {len(g["materials"])} materials, {len(g["textures"])} textures, {len(result)} bytes')
