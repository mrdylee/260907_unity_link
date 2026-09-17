using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;
using UnityEditor;
using UnityEditor.SceneManagement;

public class ESSBlenderImporter
{
    [Serializable] public class Node { public string name; public int parent; public float[] position,rotation,scale; public int mesh,material; }
    [Serializable] public class MeshData { public float[] vertices,normals,uv; public int[] triangles; }
    [Serializable] public class Mat { public string name,role; public float[] color; public float metallic,roughness; }
    [Serializable] public class Model { public Node[] nodes; public MeshData[] meshes; public Mat[] materials; }
    const string Folder="Assets/ESS_Blender_v2";
    Vector3 V(float[] a) { return new Vector3(a[0],a[1],a[2]); }
    Vector3[] Vectors(float[] a) { var r=new Vector3[a.Length/3]; for(int i=0;i<r.Length;i++)r[i]=new Vector3(a[i*3],a[i*3+1],a[i*3+2]);return r; }
    string Clean(string s) { return s.Replace(".001", "").Replace("|","_").Replace("/","_"); }
    Texture2D Texture(string role,string suffix,bool normal)
    {
        string path=Folder+"/Textures/"+role+suffix+".png";
        var importer=(TextureImporter)AssetImporter.GetAtPath(path);
        importer.textureType=normal?TextureImporterType.NormalMap:TextureImporterType.Default;
        importer.sRGBTexture=false;importer.wrapMode=TextureWrapMode.Repeat;importer.filterMode=FilterMode.Trilinear;
        importer.textureCompression=TextureImporterCompression.Uncompressed;importer.maxTextureSize=1024;
        importer.alphaSource=TextureImporterAlphaSource.FromInput;importer.mipmapEnabled=true;
        importer.SaveAndReimport();
        return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
    }
    void Light(string name,Vector3 position,float intensity,Color color)
    {
        var go=new GameObject(name);var light=go.AddComponent<Light>();light.type=LightType.Directional;
        go.transform.position=position;go.transform.LookAt(new Vector3(0,1.4f,0));light.intensity=intensity;light.color=color;
        light.shadows=LightShadows.Soft;
    }
    [MenuItem("Tools/ESS/Import Blender v2")]
    public static void Import() { new ESSBlenderImporter().Run(); }
    private void Run()
    {
        if(Application.dataPath!="/Users/james_black/work/project/ess_unity_project/Assets"||Application.isPlaying)throw new Exception("Wrong project or Play Mode");
        for(int i=0;i<SceneManager.sceneCount;i++)if(SceneManager.GetSceneAt(i).isDirty)throw new Exception("Preserve unsaved scene before import");
        if(AssetDatabase.LoadAssetAtPath<GameObject>(Folder+"/ESS_Blender_v2.prefab")!=null)throw new Exception("Import already exists; do not overwrite");
        var data=Newtonsoft.Json.JsonConvert.DeserializeObject<Model>(File.ReadAllText("Blender/UnityTransfer/model.json"));
        Directory.CreateDirectory(Folder+"/Materials");Directory.CreateDirectory(Folder+"/Meshes");AssetDatabase.Refresh();
        Debug.Log("DATA nodes="+(data.nodes==null?-1:data.nodes.Length)+" mats="+(data.materials==null?-1:data.materials.Length)+" meshes="+(data.meshes==null?-1:data.meshes.Length));
        var materials=new Material[data.materials.Length];
        for(int i=0;i<materials.Length;i++)
        {
            var d=data.materials[i];Debug.Log("MAT "+i+" name="+d.name+" color="+(d.color==null?-1:d.color.Length));var m=new Material(Shader.Find("Universal Render Pipeline/Lit"));m.name=Clean(d.name);
            m.SetColor("_BaseColor",new Color(d.color[0],d.color[1],d.color[2],1).gamma);
            m.SetFloat("_Metallic",d.metallic);m.SetFloat("_Smoothness",1-d.roughness);
            if(!string.IsNullOrEmpty(d.role))
            {
                m.SetTexture("_BumpMap",Texture(d.role,"_Normal",true));m.SetFloat("_BumpScale",1);
                m.SetTexture("_MetallicGlossMap",Texture(d.role,"_MetallicSmoothness",false));m.SetFloat("_Smoothness",1);
                m.EnableKeyword("_NORMALMAP");m.EnableKeyword("_METALLICSPECGLOSSMAP");
            }
            AssetDatabase.CreateAsset(m,Folder+"/Materials/"+i.ToString("D2")+"_"+Clean(d.name)+".mat");materials[i]=m;
        }
        var meshes=new UnityEngine.Mesh[data.meshes.Length];
        AssetDatabase.StartAssetEditing();
        try
        {
            for(int i=0;i<meshes.Length;i++)
            {
                var d=data.meshes[i];var m=new UnityEngine.Mesh();m.name="ESS_Mesh_"+i.ToString("D4");
                m.indexFormat=IndexFormat.UInt32;m.vertices=Vectors(d.vertices);m.normals=Vectors(d.normals);
                var uv=new Vector2[d.uv.Length/2];for(int k=0;k<uv.Length;k++)uv[k]=new Vector2(d.uv[k*2],d.uv[k*2+1]);m.uv=uv;
                m.triangles=d.triangles;m.RecalculateBounds();m.RecalculateTangents();
                AssetDatabase.CreateAsset(m,Folder+"/Meshes/"+m.name+".asset");meshes[i]=m;
            }
        }
        finally { AssetDatabase.StopAssetEditing(); }
        var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
        var objects=new GameObject[data.nodes.Length];
        for(int i=0;i<objects.Length;i++)
        {
            var n=data.nodes[i];var go=new GameObject(Clean(n.name));objects[i]=go;
            if(n.parent>=0)go.transform.SetParent(objects[n.parent].transform,false);
            go.transform.localPosition=V(n.position);go.transform.localScale=V(n.scale);
            go.transform.localRotation=new Quaternion(n.rotation[0],n.rotation[1],n.rotation[2],n.rotation[3]);
            if(n.mesh>=0){go.AddComponent<MeshFilter>().sharedMesh=meshes[n.mesh];go.AddComponent<MeshRenderer>().sharedMaterial=materials[n.material];}
        }
        var root=objects[0];root.name="ESS_Blender_v2";Undo.RegisterCreatedObjectUndo(root,"Import ESS Blender v2");
        var camGo=new GameObject("Main Camera");camGo.tag="MainCamera";var cam=camGo.AddComponent<Camera>();
        camGo.transform.position=new Vector3(-9,7.2f,-11);camGo.transform.LookAt(new Vector3(0,1.35f,0));cam.orthographic=true;cam.orthographicSize=3.5f;
        cam.nearClipPlane=.05f;cam.farClipPlane=100;cam.backgroundColor=new Color(.16f,.18f,.21f);cam.clearFlags=CameraClearFlags.SolidColor;
        camGo.AddComponent<AudioListener>();
        var hinges=new Transform[8];var angles=new float[8];
        for(int i=0;i<6;i++){hinges[i]=objects.Single(o=>o.name=="Door_Hinge_"+(i+1).ToString("D2")).transform;angles[i]=-105;}
        hinges[6]=objects.Single(o=>o.name=="Front_Left_Hinge").transform;angles[6]=-100;
        hinges[7]=objects.Single(o=>o.name=="Front_Right_Hinge").transform;angles[7]=100;
        foreach(var hinge in hinges)
        {
            var panel=hinge.GetComponentsInChildren<MeshFilter>().Where(f=>f.name.StartsWith("Door_Leaf")).FirstOrDefault();
            if(panel==null)panel=hinge.GetComponentsInChildren<MeshFilter>().OrderByDescending(f=>f.sharedMesh.bounds.size.sqrMagnitude).First();
            var collider=panel.gameObject.AddComponent<BoxCollider>();collider.center=panel.sharedMesh.bounds.center;collider.size=panel.sharedMesh.bounds.size;
        }
        var controller=root.AddComponent<ESSDoorController>();var serialized=new SerializedObject(controller);
        var hs=serialized.FindProperty("hinges");var ag=serialized.FindProperty("openAngles");hs.arraySize=8;ag.arraySize=8;
        for(int i=0;i<8;i++){hs.GetArrayElementAtIndex(i).objectReferenceValue=hinges[i];ag.GetArrayElementAtIndex(i).floatValue=angles[i];}
        serialized.FindProperty("viewCamera").objectReferenceValue=cam;serialized.ApplyModifiedPropertiesWithoutUndo();
        PrefabUtility.SaveAsPrefabAsset(root,Folder+"/ESS_Blender_v2.prefab");
        var floor=GameObject.CreatePrimitive(PrimitiveType.Plane);floor.name="Display Ground";floor.transform.position=new Vector3(0,-.055f,0);floor.transform.localScale=new Vector3(3,1,3);
        var ground=new Material(Shader.Find("Universal Render Pipeline/Lit"));ground.name="Display_Ground";ground.SetColor("_BaseColor",new Color(.28f,.30f,.32f));ground.SetFloat("_Smoothness",.15f);
        AssetDatabase.CreateAsset(ground,Folder+"/Materials/Display_Ground.mat");floor.GetComponent<Renderer>().sharedMaterial=ground;
        Light("Key",new Vector3(-3,6,-4),1.8f,new Color(1,.97f,.92f));Light("Fill",new Vector3(4,5,3),.7f,new Color(.85f,.92f,1));
        RenderSettings.ambientMode=AmbientMode.Trilight;RenderSettings.ambientSkyColor=new Color(.5f,.55f,.6f);RenderSettings.ambientEquatorColor=new Color(.24f,.26f,.28f);RenderSettings.ambientGroundColor=new Color(.12f,.13f,.14f);
        var sky=new Material(Shader.Find("Skybox/Procedural"));sky.name="Display_Sky";sky.SetFloat("_Exposure",.7f);AssetDatabase.CreateAsset(sky,Folder+"/Materials/Display_Sky.mat");RenderSettings.skybox=sky;
        var probeGo=new GameObject("Material Reflection Probe");var probe=probeGo.AddComponent<ReflectionProbe>();probe.mode=ReflectionProbeMode.Realtime;probe.refreshMode=ReflectionProbeRefreshMode.OnAwake;
        probe.size=new Vector3(15,8,12);probe.transform.position=new Vector3(0,1.5f,0);probe.resolution=128;
        EditorSceneManager.SaveScene(scene,Folder+"/ESS_Blender_v2_Demo.unity");AssetDatabase.SaveAssets();
        Selection.activeGameObject=root;
        if(SceneView.lastActiveSceneView!=null){SceneView.lastActiveSceneView.LookAt(new Vector3(0,1.4f,0),camGo.transform.rotation,7,false,true);SceneView.lastActiveSceneView.sceneLighting=true;SceneView.lastActiveSceneView.Repaint();}
        var bounds=root.GetComponentsInChildren<Renderer>().First().bounds;foreach(var renderer in root.GetComponentsInChildren<Renderer>())bounds.Encapsulate(renderer.bounds);
        Debug.Log("Imported "+objects.Length+" nodes / "+meshes.Length+" meshes / "+materials.Length+" URP materials. BOUNDS="+bounds+" HINGES="+hinges.Length);
        File.WriteAllText("Blender/UnityTransfer/unity_import_report.json",JsonUtility.ToJson(new Report {project=Application.dataPath,scene=scene.path,nodes=objects.Length,meshes=meshes.Length,materials=materials.Length,doors=hinges.Length,boundsCenter=bounds.center,boundsSize=bounds.size},true));
    }
    [Serializable] public class Report {public string project,scene;public int nodes,meshes,materials,doors;public Vector3 boundsCenter,boundsSize;}
}
