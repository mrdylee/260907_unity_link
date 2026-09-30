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
