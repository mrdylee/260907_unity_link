import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { ESSModel } from './ESSModel';
import { formatRackLabel, SampleTelemetryProvider, type EquipmentTelemetry, type RackTelemetry } from './telemetry';
import './style.css';

document.querySelector('#app')!.innerHTML = `<main><header><div><span class="eyebrow">ENERGY STORAGE SYSTEM</span><h1>ESS 컨테이너</h1><p>Blender v2 재질 · 인터랙티브 3D 목업</p></div><span class="badge">6 RACKS · 42 PACKS</span></header><section id="viewport"><canvas></canvas><div id="loading">모델 불러오는 중…</div><div id="rack-markers"></div><aside id="telemetry"><div class="telemetry-head"><div><span class="eyebrow">MODBUS TCP</span><h2>ESS 진단 정보</h2></div><span class="simulation">SIMULATION</span></div><p class="connection">● 장비 미연결 · 예시 데이터</p><div id="rack-cards"></div><h3 class="equipment-title">제어기 진단</h3><div id="equipment-cards"></div></aside><div class="view-tools"><button id="zoom-in" aria-label="확대">＋</button><button id="zoom-out" aria-label="축소">−</button><button id="fullscreen" aria-label="전체화면">⛶</button></div><div class="hint">드래그 회전 · 휠 확대 · 우클릭 이동 · 문 클릭</div></section><footer><div class="group"><button id="open">전체 열기</button><button id="close">전체 닫기</button></div><div class="group"><button id="home">전체 보기</button><button id="racks">배터리 랙</button><button id="panel">내부 패널</button><button id="ebsc">eBSC</button></div><span id="status" role="status">준비 중</span></footer></main>`;
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
const controls = new OrbitControls(camera, canvas); controls.enableDamping = true; controls.minDistance = .22; controls.maxDistance = 22; controls.maxPolarAngle = Math.PI*.95;
function view(position: THREE.Vector3, target: THREE.Vector3): void { camera.position.copy(position); controls.target.copy(target); controls.update(); }
function home(): void {view(new THREE.Vector3(-7.8,5.3,10.2),new THREE.Vector3(.45,1.3,0));status.textContent="전체 보기 · 드래그로 회전";}
home();
new ResizeObserver(() => {const {width,height}=viewport.getBoundingClientRect();renderer.setSize(width,height,false);camera.aspect=width/height;camera.updateProjectionMatrix();}).observe(viewport);
let model: ESSModel | undefined;
let rackHighlight: THREE.Box3Helper | undefined;
const sceneMarkers: { element: HTMLButtonElement; anchor: THREE.Vector3 }[] = [];
const telemetryProvider = new SampleTelemetryProvider();
function selectRack(rackId:number):void {
 document.querySelectorAll('.equipment-card,.equipment-marker').forEach(item=>item.classList.remove('selected'));
 document.querySelectorAll('.rack-card,.rack-marker').forEach(item=>item.classList.toggle('selected',item.getAttribute('data-rack')===String(rackId)));
 model?.setAll(true);const racks=model?.root.getObjectByName('Internal_Battery_Racks');const rack=racks?.children[rackId-1];
 if(rack){
   if(rackHighlight){scene.remove(rackHighlight);rackHighlight.geometry.dispose();(rackHighlight.material as THREE.Material).dispose();}
   rackHighlight=new THREE.Box3Helper(new THREE.Box3().setFromObject(rack),0x49e2d6);scene.add(rackHighlight);
   view(new THREE.Vector3(3.2,4.6,12),new THREE.Vector3(.45,1.35,0));
 }
 status.textContent=`${formatRackLabel(rackId)} 진단 정보 · 모의 데이터`;
}
function createRackMarkers():void {
 const layer=document.querySelector<HTMLElement>('#rack-markers')!;const racks=model?.root.getObjectByName('Internal_Battery_Racks');if(!racks)return;
 racks.children.forEach((rack,index)=>{const box=new THREE.Box3().setFromObject(rack);const anchor=new THREE.Vector3((box.min.x+box.max.x)/2,box.max.y+.16,(box.min.z+box.max.z)/2);const element=document.createElement('button');element.className='rack-marker';element.dataset.rack=String(index+1);element.textContent=formatRackLabel(index+1);element.addEventListener('click',()=>selectRack(index+1));layer.append(element);sceneMarkers.push({element,anchor});});
 for(const [id,nodeName] of [['LCS','LCS_Controller'],['eBSC','eBSC_Controller']] as const){const node=model?.root.getObjectByName(nodeName);if(!node)continue;const box=new THREE.Box3().setFromObject(node);const anchor=new THREE.Vector3((box.min.x+box.max.x)/2,(box.min.y+box.max.y)/2,(box.min.z+box.max.z)/2);const element=document.createElement('button');element.className='rack-marker equipment-marker';element.dataset.equipment=id;element.textContent=id;element.addEventListener('click',()=>selectEquipment(id));layer.append(element);sceneMarkers.push({element,anchor});}
}
function selectEquipment(id:'LCS'|'eBSC'):void {
 document.querySelectorAll('.rack-card,.rack-marker').forEach(item=>item.classList.remove('selected'));
 if(rackHighlight){scene.remove(rackHighlight);rackHighlight.geometry.dispose();(rackHighlight.material as THREE.Material).dispose();rackHighlight=undefined;}
 document.querySelectorAll('.equipment-card,.equipment-marker').forEach(item=>item.classList.toggle('selected',item.getAttribute('data-equipment')===id));
 model?.setAll(true);const node=model?.root.getObjectByName(id==='LCS'?'LCS_Controller':'eBSC_Controller');if(node){rackHighlight=new THREE.Box3Helper(new THREE.Box3().setFromObject(node),0xf3c866);scene.add(rackHighlight);const target=node.getWorldPosition(new THREE.Vector3());view(target.clone().add(new THREE.Vector3(-1.25,.15,.15)),target);}
 status.textContent=`${id}${id==='eBSC'?' · LAN 포트 4개':''} 진단 정보 · 모의 데이터`;
}
function renderTelemetry(snapshot: RackTelemetry[]): void {
 const cards=document.querySelector<HTMLElement>('#rack-cards')!;
 cards.innerHTML=snapshot.map(rack=>`<button class="rack-card ${rack.status}" data-rack="${rack.rackId}"><span class="rack-title"><b>${formatRackLabel(rack.rackId)}</b><i>${rack.status==='warning'?'경고':'정상'}</i></span><span class="rack-values"><strong>${rack.temperatureC.toFixed(1)}<small> °C</small></strong><span>${rack.voltageV.toFixed(1)} V</span><span>SOC ${rack.socPercent}%</span></span><span class="diagnostic"><code>${rack.diagnosticCode}</code>${rack.diagnosticMessage}</span></button>`).join('');
 cards.querySelectorAll<HTMLButtonElement>('.rack-card').forEach(card=>card.addEventListener('click',()=>selectRack(Number(card.dataset.rack))));
}
void telemetryProvider.read().then(renderTelemetry);
function renderEquipment(snapshot:EquipmentTelemetry[]):void {
 const cards=document.querySelector<HTMLElement>('#equipment-cards')!;cards.innerHTML=snapshot.map(item=>`<button class="equipment-card" data-equipment="${item.id}"><span><b>${item.id}</b><i>${item.communication}</i></span><small>${item.mode}</small><code>${item.diagnosticCode}</code><em>${item.diagnosticMessage}</em></button>`).join('');cards.querySelectorAll<HTMLButtonElement>('.equipment-card').forEach(card=>card.addEventListener('click',()=>selectEquipment(card.dataset.equipment as 'LCS'|'eBSC')));
}
void telemetryProvider.readEquipment().then(renderEquipment);
const raycaster = new THREE.Raycaster(); let down = new THREE.Vector2();
canvas.addEventListener('pointerdown', event => {down.set(event.clientX,event.clientY);});
canvas.addEventListener('pointerup', event => {
 if (event.button !== 0 || !model || down.distanceTo(new THREE.Vector2(event.clientX,event.clientY))>5) return;
 const rect=canvas.getBoundingClientRect();raycaster.setFromCamera(new THREE.Vector2((event.clientX-rect.left)/rect.width*2-1,-(event.clientY-rect.top)/rect.height*2+1),camera);
 const hit=raycaster.intersectObject(model.root,true)[0]; if(hit){const name=model.toggleObject(hit.object);if(name)status.textContent=name.startsWith('Door_Hinge')?'배터리실 문 조작':'장비실 문 조작';}
});
function on(id:string, action:()=>void):void{document.getElementById(id)!.addEventListener('click',action);}
on('open',()=>{model?.setAll(true);status.textContent='모든 문 열기';});
on('close',()=>{model?.setAll(false);status.textContent='모든 문 닫기';});
on('home',()=>{document.querySelectorAll('.selected').forEach(item=>item.classList.remove('selected'));if(rackHighlight){scene.remove(rackHighlight);rackHighlight.geometry.dispose();(rackHighlight.material as THREE.Material).dispose();rackHighlight=undefined;}home();});
function zoom(factor:number):void{const offset=camera.position.clone().sub(controls.target);offset.setLength(THREE.MathUtils.clamp(offset.length()*factor,controls.minDistance,controls.maxDistance));camera.position.copy(controls.target).add(offset);controls.update();}
on('zoom-in',()=>zoom(.8));on('zoom-out',()=>zoom(1.25));
on('fullscreen',()=>{if(document.fullscreenElement)void document.exitFullscreen();else void document.documentElement.requestFullscreen().catch(()=>{status.textContent='이 브라우저에서는 전체화면을 사용할 수 없습니다.';});});
on('racks',()=>{model?.setAll(true);view(new THREE.Vector3(2.5,3.8,9.5),new THREE.Vector3(0,1.35,0));status.textContent='랙 6개 · 각 7팩';});
on('panel',()=>{model?.setAll(true);view(new THREE.Vector3(-6.4,1.8,.3),new THREE.Vector3(-2.5,1.12,.3));status.textContent='내부 장비와 문 안쪽 FACP';});
on('ebsc',()=>{if(!model)return;model.setAll(true);const node=model.root.getObjectByName('eBSC_Controller')!;const target=node.getWorldPosition(new THREE.Vector3());view(target.clone().add(new THREE.Vector3(-1.1,.06,0)),target);status.textContent='eBSC · LAN 포트 4개';});
let previous=performance.now();renderer.setAnimationLoop(time=>{const dt=(time-previous)/1000;previous=time;model?.update(dt);controls.update();renderer.render(scene,camera);const {width,height}=viewport.getBoundingClientRect();for(const marker of sceneMarkers){const point=marker.anchor.clone().project(camera);marker.element.hidden=point.z < -1 || point.z > 1;marker.element.style.transform=`translate(${(point.x*.5+.5)*width}px,${(-point.y*.5+.5)*height}px) translate(-50%,-50%)`;}});
async function loadModel():Promise<void>{
try {model=await ESSModel.load('./models/ess-container.glb');scene.add(model.root);model.root.updateMatrixWorld(true);createRackMarkers();document.getElementById('loading')!.remove();status.textContent='준비 완료 · 문을 클릭하세요';}
catch(error){document.getElementById('loading')!.textContent='모델을 불러오지 못했습니다. 서버 주소로 접속했는지 확인하세요.';console.error(error);}

}
void loadModel();
