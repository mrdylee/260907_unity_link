import assert from 'node:assert/strict';
import * as THREE from 'three';
import { ESSModel } from '../src/ESSModel.ts';
// Decode embedded glTF images in Node; rendering is verified separately in the browser.
const { createCanvas, loadImage } = await import('@napi-rs/canvas');
globalThis.self = globalThis;
globalThis.createImageBitmap = async blob => { const img = await loadImage(Buffer.from(await blob.arrayBuffer())); const canvas = createCanvas(img.width,img.height); canvas.getContext('2d').drawImage(img,0,0); return canvas; };
// GLTFLoader emits browser progress events; supply their shape for the Node test.
globalThis.ProgressEvent = class { constructor(type, values) { this.type=type;Object.assign(this,values); } };
const model=await ESSModel.load(`${process.env.ESS_TEST_URL || 'http://127.0.0.1:3006'}/models/ess-container.glb`);
const root=model.root;
root.updateMatrixWorld(true);
const leftDevices=['Extended_Switch','Network_Switch_IE3500','eBSC_Controller'].map(name=>root.getObjectByName(name));
const rightDevice=root.getObjectByName('LCS_Controller');
const positions=leftDevices.map(node=>node.getWorldPosition(new THREE.Vector3()));
assert.ok(positions.every(p=>p.z<0),'Three devices are on the left internal face');
assert.ok(positions[0].x<positions[1].x && positions[1].x<positions[2].x,'Extended switch, switch, eBSC left-to-right');
assert.ok(rightDevice.getWorldPosition(new THREE.Vector3()).z>0,'LCS is on the right internal face');
for(const node of [...leftDevices,rightDevice]){
 const front=new THREE.Vector3(-1,0,0).applyQuaternion(node.getWorldQuaternion(new THREE.Quaternion()));
 assert.ok(node===rightDevice ? front.z<-.99 : front.z>.99,'Ports face into the service compartment');
}
const hvacBox=new THREE.Box3().setFromObject(root.getObjectByName('HVAC_Unit'));
for(const node of leftDevices)assert.ok(!new THREE.Box3().setFromObject(node).intersectsBox(hvacBox),'Equipment clears HVAC');
const panel=root.getObjectByName('E_Panel_Detailed');
for(let number=1;number<=6;number++){
 const cable=root.getObjectByName(`RBMS_${number}_Cable`);
 assert.equal(cable.parent.name,'Extended_Switch','Pink cable follows its expansion switch');
 const port=root.getObjectByName(`Expansion_RJ45_2_${number}`).getWorldPosition(new THREE.Vector3());
 assert.ok(cable.children[0].localToWorld(new THREE.Vector3(0,-1,0)).distanceTo(port)<1e-5,'Pink cable plugs into LAN port');
 for(let index=1;index<cable.children.length;index++){
  const previous=cable.children[index-1].localToWorld(new THREE.Vector3(0,1,0));
  const next=cable.children[index].localToWorld(new THREE.Vector3(0,-1,0));
  assert.ok(previous.distanceTo(next)<1e-5,'Pink cable segments remain joined');
 }
}
const links=panel.children.filter(node=>/^Switch_eBSC_Link_\d$/.test(node.name));
assert.equal(links.length,2,'Only two eBSC LAN connections');
assert.equal(root.getObjectByName('eBSC_Controller').children.filter(n=>n.name.startsWith('eBSC_LAN_Cable')).length,0,'No dangling old LAN cables');
for(const link of links){
 const from=root.getObjectByName(link.userData.from).getWorldPosition(new THREE.Vector3());
 const to=root.getObjectByName(link.userData.to).getWorldPosition(new THREE.Vector3());
 const first=link.children[0],last=link.children.at(-1);
 assert.ok(first.localToWorld(new THREE.Vector3(0,-1,0)).distanceTo(from)<1e-5,'Cable starts at eBSC port');
 assert.ok(last.localToWorld(new THREE.Vector3(0,1,0)).distanceTo(to)<1e-5,'Cable ends at switch port');
}
for(const device of leftDevices)for(const duct of panel.children.filter(n=>n.name.startsWith('Horizontal_Wiring_Duct'))){
 assert.ok(!new THREE.Box3().setFromObject(device).intersectsBox(new THREE.Box3().setFromObject(duct)),'Raised devices clear central shelves');
}
const materials=new Set();root.traverse(n=>{if(n.isMesh)materials.add(n.material);});assert.equal(materials.size,13);assert.equal([...materials].filter(m=>m.normalMap&&m.metalnessMap&&m.roughnessMap).length,4);
const racks=root.getObjectByName('Internal_Battery_Racks');assert.equal(racks.children.length,6);
let count=0;root.traverse(n=>{if(/^Battery_Module_\d/.test(n.name))count++;});assert.equal(count,42);
const side=root.getObjectByName('Side_Access_Doors');assert.equal(side.children.length,6);
const facp=root.getObjectByName('FACP_Inside_Door');assert.equal(facp.parent.name,'Front_Left_Hinge');
root.updateMatrixWorld(true);const rackPosition=racks.children[0].getWorldPosition(new THREE.Vector3());const facpClosed=facp.getWorldPosition(new THREE.Vector3());
model.setAll(true);for(let i=0;i<100;i++)model.update(1/60);root.updateMatrixWorld(true);
for(const door of side.children)assert.ok(door.quaternion.angleTo(new THREE.Quaternion().setFromAxisAngle(THREE.Object3D.DEFAULT_UP,THREE.MathUtils.degToRad(Number(door.name.slice(-2))%2 ? -105 : 105)))<1e-5);
assert.ok(facp.getWorldPosition(new THREE.Vector3()).distanceTo(facpClosed)>.1);
assert.ok(racks.children[0].getWorldPosition(new THREE.Vector3()).distanceTo(rackPosition)<1e-8);
model.setAll(false);for(let i=0;i<100;i++)model.update(1/60);
let picked;side.children[0].traverse(n=>{if(n instanceof THREE.Mesh&&!picked)picked=n;});assert.equal(model.toggleObject(picked),'Door_Hinge_01');for(let i=0;i<100;i++)model.update(1/60);
assert.ok(side.children[0].quaternion.angleTo(new THREE.Quaternion())>1);assert.ok(side.children[1].quaternion.angleTo(new THREE.Quaternion())>1);
assert.ok(side.children[2].quaternion.angleTo(new THREE.Quaternion())<1e-5);
assert.equal(model.toggleObject(racks),null);assert.throws(()=>model.setDoor('missing',true));
model.setAll(false);for(let i=0;i<100;i++)model.update(1/60);
const copies=Array.from({length:5},()=>model.clone());
assert.equal(new Set([root,...copies.map(item=>item.root)]).size,6);
for(const index of [0,2,4]){
 const left=side.children[index],right=side.children[index+1];
 assert.ok(left.scale.x>0 && right.scale.x<0);
 assert.ok(right.position.x>left.position.x);
 const closedLeft=new THREE.Box3().setFromObject(left).getCenter(new THREE.Vector3());
 const closedRight=new THREE.Box3().setFromObject(right).getCenter(new THREE.Vector3());
 model.toggleObject(right);for(let i=0;i<100;i++)model.update(1/60);root.updateMatrixWorld(true);
 const openLeft=new THREE.Box3().setFromObject(left).getCenter(new THREE.Vector3());
 const openRight=new THREE.Box3().setFromObject(right).getCenter(new THREE.Vector3());
 assert.ok(openLeft.z>closedLeft.z && openRight.z>closedRight.z,'Both leaves swing outwards');
 assert.ok(openLeft.x<closedLeft.x && openRight.x>closedRight.x,'Leaves separate away from the middle');
 for(const copy of copies)assert.ok(copy.root.getObjectByName(left.name).quaternion.angleTo(new THREE.Quaternion())<1e-5);
 model.toggleObject(left);for(let i=0;i<100;i++)model.update(1/60);
 assert.ok(left.quaternion.angleTo(new THREE.Quaternion())<1e-5 && right.quaternion.angleTo(new THREE.Quaternion())<1e-5);
}
model.dispose();
console.log('PASS: 6 racks / 42 packs / 8 door hierarchy, opening and closing, three outward door pairs, six independent containers, FACP follows hinge, racks stationary.');
