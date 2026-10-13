import {createCanvas} from '@napi-rs/canvas';
import {readFile,writeFile} from 'node:fs/promises';
const raw=await readFile(new URL('../public/models/ess-container.glb',import.meta.url));
const {nodes}=JSON.parse(raw.subarray(20,20+raw.readUInt32LE(12)).toString());
const canvas=createCanvas(1024,832),ctx=canvas.getContext('2d');
ctx.fillStyle='#24292d';ctx.fillRect(0,0,1024,832);
let seed=3500;for(let i=0;i<14000;i++){seed=(seed*1664525+1013904223)>>>0;const x=seed%1024;seed=(seed*1664525+1013904223)>>>0;ctx.fillStyle=i%2?'#2c3135':'#1e2428';ctx.fillRect(x,seed%832,1,1);}
function panel(offset,width){
 const x=z=>offset+(z/width+.5)*512,y=v=>(.155-v)/.31*832;
 const text=(value,z,v,size=16,align='center')=>{ctx.fillStyle='#e8edef';ctx.font=`bold ${size}px Arial`;ctx.textAlign=align;ctx.textBaseline='middle';ctx.fillText(value,x(z),y(v));};
 const led=(z,v,color)=>{ctx.fillStyle=color;ctx.beginPath();ctx.arc(x(z),y(v),4,0,Math.PI*2);ctx.fill();};
 const logo=(z,v)=>{for(let i=0;i<9;i++){ctx.fillStyle='#e8edef';ctx.fillRect(x(z)+(i-4)*5,y(v)-[3,9,17,9,5,9,17,9,3][i],2,[3,9,17,9,5,9,17,9,3][i]);}text('cisco',z,v-.007,27);};
 return {x,y,text,led,logo};
}
const ext=panel(0,.178),main=panel(512,.19);
ext.logo(.055,.142);ext.text('IEM-3500',-.024,.138,18);
ext.text('14T2S',-.024,.127,14);ext.text('14 GE + 2 SFP',0,-.149,12);
for(let number=1;number<=14;number++){
 const n=nodes.find(n=>n.name===`Expansion_RJ45_2_${number}`),z=n.translation[2],y=n.translation[1];
 ext.text(String(number),z-.023,y,14);ext.led(z+.021,y+.007,'#68ac86');
}
ext.text('15',-.057,-.130,14);ext.text('16',.007,-.130,14);
main.logo(.063,.142);main.text('IE 3500',.063,.125,17);
const rows=[.120,.088,.056,.024,-.024,-.056,-.088,-.120];
rows.forEach((y,i)=>{main.text(`1/${i+4}`, -.014,y-.004,12);main.led(-.014,y+.007,'#829d89');});
for(let i=0;i<3;i++)main.text(`1/${i+1}`,-.029,.040-i*.040,12);
main.text('CONSOLE',-.064,.128,11);main.text('SFP',-.052,.067,12);
main.text('DC-A',.040,.094,12);main.text('DC-B',.040,.034,12);
main.text('+',.088,.104,17);main.text('−',.088,.084,17);
main.text('+',.088,.044,17);main.text('−',.088,.024,17);
main.text('DC   A   B',.061,.007,12);[.049,.061,.073].forEach(z=>main.led(z,-.001,'#718a73'));
main.text('SYS',.047,-.027,11);main.text('ALM',.074,-.027,11);main.led(.048,-.036,'#87bda3');main.led(.074,-.036,'#bca368');
main.text('USB / SD',-.049,-.114,14);main.text('SERIAL LABEL',-.082,-.114,10);
main.text('8T3S',-.072,-.146,16);main.text('ALARM',.043,-.067,11);
ctx.strokeStyle='#d6dfe2';ctx.lineWidth=2;ctx.beginPath();ctx.arc(main.x(.084),main.y(-.143),10,0,Math.PI*2);ctx.stroke();main.text('⏚',.084,-.143,19);
await writeFile(new URL('../public/textures/cisco-face.png',import.meta.url),canvas.toBuffer('image/png'));
console.log('Cisco front print atlas created');
