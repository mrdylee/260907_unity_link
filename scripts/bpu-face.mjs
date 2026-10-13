import {createCanvas} from '@napi-rs/canvas';
import {writeFile} from 'node:fs/promises';
const canvas=createCanvas(1024,336),ctx=canvas.getContext('2d');
ctx.fillStyle='#1d2329';ctx.fillRect(0,0,1024,336);
const x=v=>(v/.95+.5)*1024,y=v=>(.155-v)/.31*336;
function text(value,px,py,size=21){ctx.fillStyle='#f0f2ef';ctx.font=`${size}px Arial`;ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(value,x(px),y(py));}
text('BTM (−)',-.385,.117,19);text('TOP (+)',.385,.117,19);
text('POWER SW',.215,.113,27);text('OFF',.182,.023,20);text('ON',.253,.023,20);
text('(+) CONTROL (−)',-.200,-.032,16);text('DC 24V',-.200,-.052,19);
ctx.fillStyle='#dd3934';ctx.fillRect(x(-.455),y(.152),110,22);
ctx.fillStyle='#fff';ctx.font='bold 15px Arial';ctx.textAlign='left';ctx.fillText('CAUTION',x(-.452)+8,y(.142));
ctx.fillStyle='#f5cc39';ctx.beginPath();ctx.moveTo(x(-.434),y(.127));ctx.lineTo(x(-.449),y(.098));ctx.lineTo(x(-.419),y(.098));ctx.closePath();ctx.fill();
ctx.fillStyle='#14191d';ctx.font='bold 24px Arial';ctx.fillText('ϟ',x(-.443),y(.104));
await writeFile(new URL('../public/textures/bpu-face.png',import.meta.url),canvas.toBuffer('image/png'));
console.log('BPU front labels created');
