// Recover only the photographed faceplate markings; do not invent unreadable pin names.
import {createCanvas,loadImage} from '@napi-rs/canvas';
import {writeFile} from 'node:fs/promises';
const image=await loadImage(process.argv[2]);
const source=createCanvas(image.width,image.height),input=source.getContext('2d');
input.drawImage(image,0,0);
const pixels=input.getImageData(0,0,image.width,image.height).data;
const corners=[[203,-4],[472,112],[460,224],[187,150]],uv=[[0,0],[1,0],[1,1],[0,1]],matrix=[];
for(let i=0;i<4;i++){
 const [u,v]=uv[i],[x,y]=corners[i];
 matrix.push([u,v,1,0,0,0,-u*x,-v*x,x],[0,0,0,u,v,1,-u*y,-v*y,y]);
}
for(let i=0;i<8;i++){
 let pivot=i;for(let j=i+1;j<8;j++)if(Math.abs(matrix[j][i])>Math.abs(matrix[pivot][i]))pivot=j;
 [matrix[i],matrix[pivot]]=[matrix[pivot],matrix[i]];
 const divisor=matrix[i][i];for(let j=i;j<9;j++)matrix[i][j]/=divisor;
 for(let k=0;k<8;k++)if(k!==i){const factor=matrix[k][i];for(let j=i;j<9;j++)matrix[k][j]-=factor*matrix[i][j];}
}
const h=matrix.map(row=>row[8]),canvas=createCanvas(1200,600),ctx=canvas.getContext('2d'),result=ctx.createImageData(1200,600);
// These regions contain silkscreen and two stickers, not the separate 3D connectors.
const labels=[[260,123,235,130],[562,120,248,140],[818,130,360,135],[122,150,78,65],[130,357,75,58],[79,437,98,43],[185,470,88,49],[350,373,160,115],[575,335,245,144],[829,335,355,144]];
for(let py=0;py<600;py++)for(let px=0;px<1200;px++){
 const index=(py*1200+px)*4;
 let ink=0;
 if(labels.some(([x,y,w,h])=>px>=x&&px<x+w&&py>=y&&py<y+h)){
  const u=px/1199,v=py/599,d=h[6]*u+h[7]*v+1,x=(h[0]*u+h[1]*v+h[2])/d,y=(h[3]*u+h[4]*v+h[5])/d;
  const sx=Math.floor(x),sy=Math.floor(y),dx=x-sx,dy=y-sy,channels=[];
  for(let c=0;c<3;c++)channels.push(pixels[(sy*image.width+sx)*4+c]*(1-dx)*(1-dy)+pixels[(sy*image.width+sx+1)*4+c]*dx*(1-dy)+pixels[((sy+1)*image.width+sx)*4+c]*(1-dx)*dy+pixels[((sy+1)*image.width+sx+1)*4+c]*dx*dy);
  ink=Math.max(0,Math.min(1,(Math.min(...channels)-48)/160));
 }
 for(let c=0;c<3;c++)result.data[index+c]=[28,34,40][c]*(1-ink)+[224,232,233][c]*ink;
 result.data[index+3]=255;
}
ctx.putImageData(result,0,0);
await writeFile(new URL('../public/textures/lcs-face.png',import.meta.url),canvas.toBuffer('image/png'));
console.log('LCS photographed silkscreen texture created');
