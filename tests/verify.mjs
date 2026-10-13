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
const ventNodes=[];root.traverse(n=>{if(n.name.startsWith('Vent_Hinge_'))ventNodes.push(n);});
assert.equal(ventNodes.length,4,'Four covers on the outer double doors');
const ventDoorNumbers=[1,2,5,6];
const vents=ventDoorNumbers.map(number=>root.getObjectByName(`Vent_Hinge_${String(number).padStart(2,'0')}`));
for(const number of [3,4]){
 const door=root.getObjectByName(`Door_Hinge_${String(number).padStart(2,'0')}`);
 assert.equal(door.children.filter(n=>n.name.startsWith('Vent_Hinge_')).length,0,'Middle doors have no vent covers');
}
for(let index=0;index<4;index++){
 const door=root.getObjectByName(`Door_Hinge_${String(ventDoorNumbers[index]).padStart(2,'0')}`);
 assert.equal(vents[index].parent,door,'Vent follows its numbered door');
 assert.equal(door.children.filter(n=>n.name.startsWith('Vent_Hinge_')).length,1,'No extra vent on a door');
 assert.ok(index%2 ? vents[index].position.y>1.5 : vents[index].position.y<.5,'Odd door vent below, even door vent above');
}
assert.equal(model.toggleVents(),true);
for(let step=0;step<100;step++)model.update(1/60);
assert.ok(vents.every(v=>Math.abs(v.quaternion.angleTo(new THREE.Quaternion())-Math.PI/4)<1e-5));
assert.equal(model.toggleVents(),false);
for(let step=0;step<100;step++)model.update(1/60);
assert.ok(vents.every(v=>v.quaternion.angleTo(new THREE.Quaternion())<1e-5));
for(let index=0;index<4;index++){
 let mesh;vents[index].traverse(n=>{if(n.isMesh&&!mesh)mesh=n;});
 const hingeBefore=vents[index].getWorldPosition(new THREE.Vector3());
 const topBefore=vents[index].localToWorld(new THREE.Vector3(0,.3,0));
 assert.equal(model.toggleObject(mesh),vents[index].name);
 for(let step=0;step<100;step++)model.update(1/60);
 root.updateMatrixWorld(true);
 const paired=index%2 ? index-1 : index+1;
 for(let j=0;j<4;j++)assert.ok(Math.abs(vents[j].quaternion.angleTo(new THREE.Quaternion())-((j===index||j===paired)?Math.PI/4:0))<1e-5,'Only the diagonal pair on the same double doors opens 45 degrees');
 assert.ok(vents[index].getWorldPosition(new THREE.Vector3()).distanceTo(hingeBefore)<1e-6,'Lower hinge stays fixed');
 const topAfter=vents[index].localToWorld(new THREE.Vector3(0,.3,0));
 assert.ok(topAfter.z>topBefore.z && topAfter.y<topBefore.y,'Cover top tilts outward and downward');
 assert.ok(vents[index].parent.quaternion.angleTo(new THREE.Quaternion())<1e-6,'Vent click leaves battery door closed');
 model.toggleObject(mesh);for(let step=0;step<100;step++)model.update(1/60);
 assert.ok(vents.every(v=>v.quaternion.angleTo(new THREE.Quaternion())<1e-5),'Second click closes the pair');
}
root.updateMatrixWorld(true);
const leftDevices=['Extended_Switch','Network_Switch_IE3500','eBSC_Controller'].map(name=>root.getObjectByName(name));
const rightDevice=root.getObjectByName('LCS_Controller');
const ebsc=root.getObjectByName('eBSC_Controller');
for(const name of ['eBSC_USB','eBSC_UART','eBSC_LED_1','eBSC_LED_2','eBSC_LED_3','eBSC_Face_Print'])assert.ok(root.getObjectByName(name),`Photo detail ${name} exists`);
assert.ok(root.getObjectByName('eBSC_LED_1').position.y>root.getObjectByName('eBSC_USB').position.y);
assert.ok(root.getObjectByName('eBSC_USB').position.y>root.getObjectByName('eBSC_UART').position.y);
assert.ok(root.getObjectByName('eBSC_UART').position.y>root.getObjectByName('eBSC_LAN_1').position.y);
for(let number=1;number<=4;number++){
 const port=root.getObjectByName(`eBSC_LAN_${number}`);
 assert.equal(port.parent,ebsc);
 assert.ok(port.children.some(n=>n.name===`eBSC_LAN_Contacts_${number}`),'LAN socket has visible contacts');
 if(number>1)assert.ok(root.getObjectByName(`eBSC_LAN_${number-1}`).position.y>port.position.y,'LAN ports run top to bottom');
 assert.equal(port.children.filter(n=>n.name.startsWith('eBSC_RJ45_Boot')).length,number<=2?1:0,'Only the two switch connections have plugs');
}
assert.ok(root.getObjectByName('eBSC_Face_Print').material.map,'Printed photo labels are a texture');
const lcsHousing=new THREE.Box3().setFromObject(root.getObjectByName('LCS_Black_Housing'));
const whiteWall=new THREE.Box3().setFromObject(root.getObjectByName('Fixed_Louver_Panel'));
assert.ok(Math.abs(lcsHousing.max.z-whiteWall.min.z)<1e-6,'LCS rear sits flush against white wall');
const lcsSize=lcsHousing.getSize(new THREE.Vector3());
assert.ok(lcsSize.z<.045 && lcsSize.x/lcsSize.y>1.9,'Photo LCS is a shallow landscape enclosure');
assert.ok(root.getObjectByName('LCS_Face_Print')?.material.map,'LCS keeps the photographed faceplate markings');
for(const row of ['Top','Bottom']){
 const banks=rightDevice.children.filter(n=>n.name.startsWith(`LCS_${row}_Terminal_Bank_`));
 assert.equal(banks.length,4,'Four separate terminal banks on each LCS edge');
 assert.ok(banks.every(n=>row==='Top' ? n.position.y>.08 : n.position.y<-.08));
}
const lcsPlug=root.getObjectByName('LCS_LAN_Plug'),lcsBoot=root.getObjectByName('LCS_LAN_Boot');
assert.ok(new THREE.Box3().setFromObject(lcsPlug).max.y<lcsHousing.min.y,'Ethernet plugs into the lower LCS edge');
const bootBox=new THREE.Box3().setFromObject(lcsBoot),lanBox=new THREE.Box3().setFromObject(root.getObjectByName('LCS_LAN_Cable'));
assert.ok(bootBox.intersectsBox(lanBox),'Black Ethernet cable meets the strain relief');
assert.ok(lanBox.min.y<bootBox.min.y-.2,'Ethernet cable routes downward from the LCS');
const lcsPanel=root.getObjectByName('E_Panel_Detailed');
const lcsDucts=lcsPanel.children.filter(n=>n.name.startsWith('Horizontal_Wiring_Duct')).sort((a,b)=>a.position.y-b.position.y);
for(const [row,counts,duct] of [['Top',[12,12,8,8],lcsDucts.at(-1)],['Bottom',[8,12,8,8],lcsDucts[1]]]){
 const harness=root.getObjectByName(`LCS_${row}_Signal_Wires`);
 assert.ok(harness,`${row} LCS terminals have a signal harness`);
 assert.equal(harness.userData.routes.length,counts.reduce((a,b)=>a+b,0),'Each modeled signal opening has a wire');
 const redWire=harness.getObjectByName(`LCS_${row}_Signal_Wires_Red`),blackWire=harness.getObjectByName(`LCS_${row}_Signal_Wires_Black`);
 assert.ok(redWire&&blackWire,'LCS signal wires use both red and black');
 assert.ok(redWire.material.color.r>redWire.material.color.g*2 && blackWire.material.color.r<.1,'Signal wire materials are red and black');
 const hasSurfaceAt=(mesh,point)=>{
  const vertices=mesh.geometry.attributes.position;
  for(let i=0;i<vertices.count;i++)if(new THREE.Vector3().fromBufferAttribute(vertices,i).distanceTo(point)<.0017)return true;
  return false;
 };
 let routeIndex=0;
 for(let bankIndex=0;bankIndex<4;bankIndex++){
  const bank=root.getObjectByName(`LCS_${row}_Terminal_Bank_${bankIndex+1}`),count=counts[bankIndex],sign=row==='Top'?1:-1;
  for(let pin=0;pin<count;pin++){
   const wire=routeIndex%2?blackWire:redWire,route=harness.userData.routes[routeIndex++];
   const start=rightDevice.localToWorld(new THREE.Vector3(bank.position.x,bank.position.y+sign*.010,bank.position.z+(pin-(count-1)/2)*bank.scale.z/count));
   const localStart=harness.worldToLocal(start.clone()),end=new THREE.Vector3(...route.end);
   assert.ok(localStart.distanceTo(new THREE.Vector3(...route.start))<1e-6,'Wire starts at its actual modeled terminal opening');
   assert.ok(hasSurfaceAt(wire,localStart)&&hasSurfaceAt(wire,end),'Alternating red/black cable geometry reaches both connection points');
   assert.ok(new THREE.Box3().setFromObject(duct).containsPoint(harness.localToWorld(end.clone())),'Signal wire terminates inside the assigned duct');
   assert.ok(sign*(route.departure[1]-route.start[1])>.02,'Top wires exit upward, bottom wires exit downward');
  }
 }
}
const positions=leftDevices.map(node=>node.getWorldPosition(new THREE.Vector3()));
const mainSwitch=leftDevices[1],mainX=positions[1].x;
const mainCopper=mainSwitch.children.filter(n=>n.name.startsWith('Main_RJ45_1_'));
const mainSfp=mainSwitch.children.filter(n=>n.name.startsWith('Main_SFP_1_'));
assert.equal(mainCopper.length,8);assert.equal(mainSfp.length,3);
assert.ok(mainCopper.every(n=>n.getWorldPosition(new THREE.Vector3()).x>mainX),'IE3500 copper ports sit on the right');
assert.ok(mainSfp.every(n=>n.getWorldPosition(new THREE.Vector3()).x<mainX),'IE3500 three SFP ports sit on the left');
const expansionCase=new THREE.Box3().setFromObject(root.getObjectByName('IEM3500_Expansion'));
const mainCase=new THREE.Box3().setFromObject(root.getObjectByName('IE3500_Main'));
const caseGap=mainCase.min.x-expansionCase.max.x;
assert.ok(caseGap>=0 && caseGap<.003,'Expansion module is attached beside the main case');
assert.ok((expansionCase.max.x-expansionCase.min.x)/(mainCase.max.x-mainCase.min.x)>.90,'Expansion case follows the reference width ratio');
for(const name of ['IE3500_Face_Print','IE3500_USB_Cover_Print','IEM3500_Face_Print','Cisco_Coupling_Top','Cisco_Coupling_Bottom','IE3500_Heatsink','IEM3500_Heatsink'])assert.ok(root.getObjectByName(name),`Cisco detail ${name} exists`);
assert.ok(root.getObjectByName('IE3500_Face_Print').material.map);
assert.ok(root.getObjectByName('IEM3500_Face_Print').material.map);
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
const purplePorts=['Main_SFP_1_1','Main_SFP_1_2','Main_RJ45_1_4','Main_RJ45_1_5','Main_RJ45_1_6','Main_RJ45_1_11'];
const upperDuct=panel.children.filter(n=>n.name.startsWith('Horizontal_Wiring_Duct')).sort((a,b)=>b.position.y-a.position.y)[0];
const upperDuctBox=new THREE.Box3().setFromObject(upperDuct);
for(let number=1;number<=6;number++){
 const cable=root.getObjectByName(`RBMS_${number}_Cable`);
 assert.equal(cable.parent.name,'Network_Switch_IE3500','Purple cable follows the main IE3500');
 assert.equal(cable.userData.port,purplePorts[number-1],'Purple cable uses the specified IE3500 port');
 const target=root.getObjectByName(cable.userData.port);
 const port=target.getWorldPosition(new THREE.Vector3());
 assert.ok(target.children.some(n=>n.name===`RBMS_RJ45_Plug_${number}`),'Purple connector is on its main switch port');
 assert.equal(root.getObjectByName(`Expansion_RJ45_2_${number}`).children.filter(n=>n.name.startsWith('RBMS_RJ45_Plug_')).length,0,'Expansion port has no leftover purple plug');
 assert.equal(cable.children.length,1,'Purple cable is one continuous curve instead of separate straight segments');
 const wire=cable.children[0],vertices=wire.geometry.attributes.position;
 const end=panel.localToWorld(new THREE.Vector3(-.055,1.305,-.45+(number-1)*.036));
 assert.ok(upperDuctBox.containsPoint(end),'Purple cable keeps its original top-duct endpoint');
 let portDistance=Infinity,endDistance=Infinity;
 for(let index=0;index<vertices.count;index++){
  const point=wire.localToWorld(new THREE.Vector3().fromBufferAttribute(vertices,index));
  portDistance=Math.min(portDistance,point.distanceTo(port));endDistance=Math.min(endDistance,point.distanceTo(end));
 }
 assert.ok(portDistance<.0071 && endDistance<.0071,'Exported curved cable surface reaches both original connection points');
 assert.ok(wire.material.color.r>wire.material.color.g && wire.material.color.b>wire.material.color.g,'Purple cable color is retained');
}
const links=panel.children.filter(node=>/^Switch_eBSC_Link_\d$/.test(node.name));
assert.equal(links.length,2,'Only two eBSC LAN connections');
assert.deepEqual(links.map(n=>n.userData.to),['Expansion_RJ45_2_9','Main_RJ45_1_7'],'One yellow connection goes to expansion port 9, one to a free main port');
assert.ok(links.every(n=>!purplePorts.includes(n.userData.to)),'Purple and eBSC links do not share a socket');
assert.equal(root.getObjectByName('eBSC_Controller').children.filter(n=>n.name.startsWith('eBSC_LAN_Cable')).length,0,'No dangling old LAN cables');
for(const link of links){
 const from=root.getObjectByName(link.userData.from).getWorldPosition(new THREE.Vector3());
 const to=root.getObjectByName(link.userData.to).getWorldPosition(new THREE.Vector3());
 assert.equal(link.children.length,1,'Each eBSC LAN cable is one continuous curved mesh');
 const wire=link.children[0],vertices=wire.geometry.attributes.position;
 let fromDistance=Infinity,toDistance=Infinity;
 for(let index=0;index<vertices.count;index++){
  const point=wire.localToWorld(new THREE.Vector3().fromBufferAttribute(vertices,index));
  fromDistance=Math.min(fromDistance,point.distanceTo(from));toDistance=Math.min(toDistance,point.distanceTo(to));
 }
 assert.ok(fromDistance<.0071 && toDistance<.0071,'Curved LAN cable reaches both the eBSC and assigned switch ports');
}
for(const name of ['IEM3500_Expansion','IE3500_Main','eBSC_Housing'])for(const duct of panel.children.filter(n=>n.name.startsWith('Horizontal_Wiring_Duct'))){
 assert.ok(!new THREE.Box3().setFromObject(root.getObjectByName(name)).intersectsBox(new THREE.Box3().setFromObject(duct)),'Raised device cases clear central shelves');
}
const materials=new Set();root.traverse(n=>{if(n.isMesh)materials.add(n.material);});assert.equal(materials.size,18);assert.equal([...materials].filter(m=>m.normalMap&&m.metalnessMap&&m.roughnessMap).length,4);
const racks=root.getObjectByName('Internal_Battery_Racks');assert.equal(racks.children.length,6);
for(const [index,rack] of racks.children.entries()){
 const packs=rack.children.filter(n=>/^Battery_Module_\d/.test(n.name));assert.equal(packs.length,7,'Each rack keeps seven packs');
 const bpus=rack.children.filter(n=>/^BPU_\d{2}$/.test(n.name));assert.equal(bpus.length,1,'Each rack has one BPU');
 const bpu=bpus[0],caseMesh=root.getObjectByName(`${bpu.name}_Case`),bpuBox=new THREE.Box3().setFromObject(caseMesh);
 const packBoxes=packs.map(n=>new THREE.Box3().setFromObject(n));
 assert.ok(packBoxes.every(box=>box.min.y>bpuBox.max.y),'BPU sits below every pack');
 const rackBase=new THREE.Box3().setFromObject(rack.children.find(n=>n.name.startsWith('Rack_Base'))),rackTop=new THREE.Box3().setFromObject(rack.children.find(n=>n.name.startsWith('Rack_Top')));
 assert.ok(bpuBox.min.y>rackBase.max.y && packBoxes.every(box=>box.max.y<rackTop.min.y),'BPU and packs fit between rack frame rails');
 assert.ok(caseMesh.material.color.r<.2 && caseMesh.material.color.g<.2 && caseMesh.material.color.b<.2,'BPU case is black');
 for(const pack of packs)for(const mesh of pack.children.filter(n=>n.name.startsWith('Module_Case')||n.name.startsWith('Module_Face'))){assert.ok(['r','g','b'].every(c=>Math.abs(mesh.material.color[c]-caseMesh.material.color[c])<1e-5),'Pack front and case match the black BPU');}
 for(const detail of ['Face_Print','Fan','Fan_Guard','Power_Switch','Control_24V','LAN','Signal_Ports','Terminal_Covers'])assert.ok(root.getObjectByName(`${bpu.name}_${detail}`),`BPU ${index+1} photo detail ${detail} exists`);
}
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
