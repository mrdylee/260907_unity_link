import { createCanvas } from '@napi-rs/canvas';
import { mkdir, writeFile } from 'node:fs/promises';
const canvas=createCanvas(512,2048),ctx=canvas.getContext('2d');
ctx.fillStyle='#182027';ctx.fillRect(0,0,512,2048);
function text(value,z,y,size,bold=false,color='#f4f5f5',align='center'){
 ctx.font=`${bold?'bold ':''}${size}px Arial`;ctx.fillStyle=color;ctx.textAlign=align;ctx.textBaseline='middle';
 ctx.fillText(value,(z+.04)/.08*512,(.16-y)/.32*2048);
}
ctx.fillStyle='#a70d38';ctx.beginPath();ctx.arc(44,70,22,0,Math.PI*2);ctx.fill();
text('LG',-.0331,.149,17,true);
text('LG Energy Solution',.006,.149,26,true);
text('JF3 eBSC',0,.135,41,true);
text('LED',.003,.123,20,true);
[-.007,.003,.013].forEach((z,i)=>text(String(i+1),z,.114,18));
text('USB',-.030,.084,22,true);
text('UART',-.030,.052,22,true);
for(let number=1;number<=4;number++)text(`LAN${number}`,-.030,.015-(number-1)*.043,23,true);
ctx.fillStyle='#f2f3f3';ctx.fillRect(93,1910,326,84);
text('JF3 eBSC',0,-.145,26,true,'#26333c');
await mkdir(new URL('../public/textures/',import.meta.url),{recursive:true});
await writeFile(new URL('../public/textures/ebsc-face.png',import.meta.url),canvas.toBuffer('image/png'));
console.log('eBSC face print created');
