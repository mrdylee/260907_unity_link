import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { ESSModel } from './ESSModel';
import { formatRackLabel } from './telemetry';
import { setupDiagnostics } from './diagnostics';
import './style.css';

document.querySelector('#app')!.innerHTML = `<main><header><div><span class="eyebrow">ENERGY STORAGE SYSTEM</span><h1>ESS 컨테이너 · 6대</h1><p>Blender v2 재질 · 인터랙티브 3D 목업</p></div><span class="badge">6 CONTAINERS · 36 RACKS</span></header><section id="viewport"><canvas></canvas><div id="loading">모델 불러오는 중…</div><div id="rack-markers"></div><div id="container-markers"></div><aside id="telemetry"><div class="telemetry-head"><div><span class="eyebrow">MODBUS TCP</span><h2>ESS 진단 정보</h2></div><span class="simulation">SIMULATION</span></div><p class="connection">● 장비 미연결 · 예시 데이터</p><div id="rack-cards"></div><h3 class="equipment-title">제어기 진단</h3><div id="equipment-cards"></div></aside><div class="view-tools"><button id="zoom-in" aria-label="확대">＋</button><button id="zoom-out" aria-label="축소">−</button><button id="fullscreen" aria-label="전체화면">⛶</button></div><div class="hint">드래그 회전 · 휠 확대 · 우클릭 이동 · 문 클릭</div></section><footer><div class="group"><button id="open">전체 열기</button><button id="close">전체 닫기</button></div><div class="group"><button id="home">6대 전체 보기</button><label class="container-picker">컨테이너 <select id="container-select" aria-label="컨테이너 선택"><option value="0">ESS 01</option><option value="1">ESS 02</option><option value="2">ESS 03</option><option value="3">ESS 04</option><option value="4">ESS 05</option><option value="5">ESS 06</option></select></label><button id="racks">배터리 랙</button><button id="panel">내부 패널</button><button id="ebsc">eBSC</button></div><span id="status" role="status">준비 중</span></footer></main>`;
const canvas = document.querySelector('canvas')!;
const viewport = document.querySelector<HTMLElement>('#viewport')!;
const status = document.querySelector<HTMLElement>('#status')!;
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.25;
const scene = new THREE.Scene(); scene.background = new THREE.Color('#18232e');
const environment = new RoomEnvironment();
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(environment).texture;
environment.dispose(); pmrem.dispose();
scene.add(new THREE.HemisphereLight(0xe8f4ff, 0x657075, 2.6));
for (const [x,y,z,power] of [[-5,8,6,3.2],[5,3,-5,1.8],[-6,3,-1,2]]) {const light = new THREE.DirectionalLight(0xffffff,power);light.position.set(x,y,z);scene.add(light);}
const camera = new THREE.PerspectiveCamera(40, 1, .01, 100);
const controls = new OrbitControls(camera, canvas); controls.enableDamping = true; controls.minDistance = .22; controls.maxDistance = 80; controls.maxPolarAngle = Math.PI*.95;
function view(position: THREE.Vector3, target: THREE.Vector3): void { const offset=model?.root.position ?? new THREE.Vector3(); camera.position.copy(position).add(offset); controls.target.copy(target).add(offset); controls.update(); }
function home(): void { models.forEach(item=>item.root.visible=true);document.querySelector<HTMLElement>("#container-markers")!.style.display="block";camera.position.set(-18,20,27); controls.target.set(0,0.8,0); controls.update(); document.querySelector<HTMLElement>("#rack-markers")!.style.display="none"; status.textContent="컨테이너 6대 · 3열 × 2행 · 컨테이너를 선택해 상세 보기"; }
new ResizeObserver(() => {const {width,height}=viewport.getBoundingClientRect();renderer.setSize(width,height,false);camera.aspect=width/height;camera.updateProjectionMatrix();}).observe(viewport);
let model: ESSModel | undefined;
const models: ESSModel[] = [];
const containerMarkers: { element: HTMLButtonElement; anchor: THREE.Vector3 }[] = [];
const sceneMarkers: { element: HTMLButtonElement; anchor: THREE.Vector3 }[] = [];
function createRackMarkers():void {
 const layer=document.querySelector<HTMLElement>('#rack-markers')!;layer.replaceChildren();sceneMarkers.length=0;const racks=model?.root.getObjectByName('Internal_Battery_Racks');if(!racks)return;
 racks.children.forEach((rack,index)=>{const box=new THREE.Box3().setFromObject(rack);const anchor=new THREE.Vector3((box.min.x+box.max.x)/2,box.max.y+.16,(box.min.z+box.max.z)/2);const element=document.createElement('button');element.className='rack-marker';element.dataset.rack=String(index+1);element.textContent=formatRackLabel(index+1);layer.append(element);sceneMarkers.push({element,anchor});});
 for(const [id,nodeName] of [['LCS','LCS_Controller'],['eBSC','eBSC_Controller']] as const){const node=model?.root.getObjectByName(nodeName);if(!node)continue;const box=new THREE.Box3().setFromObject(node);const anchor=new THREE.Vector3((box.min.x+box.max.x)/2,(box.min.y+box.max.y)/2,(box.min.z+box.max.z)/2);const element=document.createElement('button');element.className='rack-marker equipment-marker';element.dataset.equipment=id;element.textContent=id;layer.append(element);sceneMarkers.push({element,anchor});}
}
function showSelectedMarkers():void {models.forEach(item=>item.root.visible=item===model);document.querySelector<HTMLElement>('#container-markers')!.style.display='none';document.querySelector<HTMLElement>('#rack-markers')!.style.display='block';}
function selectContainer(index:number):void {
 model=models[index];if(!model)return;
 document.querySelector<HTMLSelectElement>('#container-select')!.value=String(index);
 document.dispatchEvent(new Event('containerchange'));
 createRackMarkers();showSelectedMarkers();
 view(new THREE.Vector3(-7.8,5.3,10.2),new THREE.Vector3(.45,1.3,0));
 document.querySelector('#telemetry h2')!.textContent=`ESS ${String(index+1).padStart(2,'0')} 진단 정보`;
 status.textContent=`ESS ${String(index+1).padStart(2,'0')} · 랙 양문 1–2 / 3–4 / 5–6`;
}
document.querySelector('#container-select')!.addEventListener('change',event=>selectContainer(Number((event.target as HTMLSelectElement).value)));
void setupDiagnostics();
document.addEventListener('rackfocus', event => {
 const rackId=(event as CustomEvent<number>).detail;
 const rack=model?.root.getObjectByName('Internal_Battery_Racks')?.children[rackId-1];
 if(!model||!rack)return;
 showSelectedMarkers();
 const first=rackId%2?rackId:rackId-1;
 for(const id of [first,first+1])model.setDoor(`Door_Hinge_${String(id).padStart(2,'0')}`,true);
 const box=new THREE.Box3().setFromObject(rack);
 const target=box.getCenter(new THREE.Vector3());
 const size=box.getSize(new THREE.Vector3());
 const distance=Math.max(size.y,size.x/camera.aspect)/(2*Math.tan(THREE.MathUtils.degToRad(camera.fov/2)))*1.55;
 camera.position.copy(target).add(new THREE.Vector3(0,.15,distance));
 controls.target.copy(target);controls.update();
 status.textContent=`ESS ${models.indexOf(model)+1} · ${formatRackLabel(rackId)} 확대 · 배터리 랙 버튼으로 복귀`;
});
const raycaster = new THREE.Raycaster(); let down = new THREE.Vector2();
canvas.addEventListener('pointerdown', event => {down.set(event.clientX,event.clientY);});
canvas.addEventListener('pointerup', event => {
 if (event.button !== 0 || !model || down.distanceTo(new THREE.Vector2(event.clientX,event.clientY))>5) return;
 const rect=canvas.getBoundingClientRect();raycaster.setFromCamera(new THREE.Vector2((event.clientX-rect.left)/rect.width*2-1,-(event.clientY-rect.top)/rect.height*2+1),camera);
 const hit=raycaster.intersectObjects(models.filter(item=>item.root.visible).map(item=>item.root),true)[0]; if(hit){ const owner=models.find(item=>{let node:THREE.Object3D|null=hit.object;while(node){if(node===item.root)return true;node=node.parent;}return false;}); if(owner && document.querySelector<HTMLElement>('#container-markers')!.style.display!=='none'){selectContainer(models.indexOf(owner));return;} const name=owner?.toggleObject(hit.object);if(name)status.textContent=`ESS ${models.indexOf(owner!)+1} · ${name.startsWith('Door_Hinge')?'랙 양문 조작':'장비실 문 조작'}`;}
});
function on(id:string, action:()=>void):void{document.getElementById(id)!.addEventListener('click',action);}
on('open',()=>{models.forEach(item=>item.setAll(true));status.textContent='컨테이너 6대 모든 문 열기';});
on('close',()=>{models.forEach(item=>item.setAll(false));status.textContent='컨테이너 6대 모든 문 닫기';});
on('home',home);
function zoom(factor:number):void{const offset=camera.position.clone().sub(controls.target);offset.setLength(THREE.MathUtils.clamp(offset.length()*factor,controls.minDistance,controls.maxDistance));camera.position.copy(controls.target).add(offset);controls.update();}
on('zoom-in',()=>zoom(.8));on('zoom-out',()=>zoom(1.25));
on('fullscreen',()=>{if(document.fullscreenElement)void document.exitFullscreen();else void document.documentElement.requestFullscreen().catch(()=>{status.textContent='이 브라우저에서는 전체화면을 사용할 수 없습니다.';});});
on('racks',()=>{showSelectedMarkers();model?.setAll(true);view(new THREE.Vector3(2.5,3.8,9.5),new THREE.Vector3(0,1.35,0));status.textContent='랙 6개 · 각 7팩';});
on('panel',()=>{showSelectedMarkers();model?.setAll(true);view(new THREE.Vector3(-6.4,1.8,.3),new THREE.Vector3(-2.5,1.12,.3));status.textContent='내부 장비와 문 안쪽 FACP';});
on('ebsc',()=>{if(!model)return;showSelectedMarkers();model.setAll(true);const node=model.root.getObjectByName('eBSC_Controller')!;const target=node.getWorldPosition(new THREE.Vector3());camera.position.copy(target).add(new THREE.Vector3(-1.1,.06,0));controls.target.copy(target);controls.update();status.textContent='eBSC · LAN 포트 4개';});
let previous=performance.now();renderer.setAnimationLoop(time=>{const dt=(time-previous)/1000;previous=time;models.forEach(item=>item.update(dt));controls.update();renderer.render(scene,camera);const {width,height}=viewport.getBoundingClientRect();for(const marker of [...sceneMarkers,...containerMarkers]){const point=marker.anchor.clone().project(camera);marker.element.hidden=point.z < -1 || point.z > 1;marker.element.style.transform=`translate(${(point.x*.5+.5)*width}px,${(-point.y*.5+.5)*height}px) translate(-50%,-50%)`;}});
async function loadModel():Promise<void>{
try {model=await ESSModel.load('./models/ess-container.glb');for(let index=0;index<6;index++){const instance=index===0?model:model.clone();instance.root.position.set((index%3-1)*8.5,0,(Math.floor(index/3)-.5)*7);instance.root.name=`ESS_${index+1}`;models.push(instance);scene.add(instance.root);instance.root.updateMatrixWorld(true);const element=document.createElement('button');element.className='container-marker';element.textContent=`ESS ${String(index+1).padStart(2,'0')}`;element.addEventListener('click',()=>selectContainer(index));document.querySelector('#container-markers')!.append(element);containerMarkers.push({element,anchor:instance.root.position.clone().add(new THREE.Vector3(0,3.5,0))});}createRackMarkers();document.getElementById('loading')!.remove();home();}
catch(error){document.getElementById('loading')!.textContent='모델을 불러오지 못했습니다. 서버 주소로 접속했는지 확인하세요.';console.error(error);}

}
void loadModel();
