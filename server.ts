import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { dirname, resolve, extname, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
const root = resolve(dirname(fileURLToPath(import.meta.url)), 'dist');
const port = Number(process.env.PORT || 3000);
const host = process.env.HOST || '127.0.0.1';
const mime: Record<string, string> = { '.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.glb':'model/gltf-binary','.json':'application/json','.png':'image/png','.svg':'image/svg+xml' };
const server = createServer(async (request, response) => {
  if (request.method !== 'GET' && request.method !== 'HEAD') { response.writeHead(405).end(); return; }
  try {
    const pathname = decodeURIComponent(new URL(request.url || '/', 'http://localhost').pathname);
    const file = resolve(root, '.' + (pathname === '/' ? '/index.html' : pathname));
    if (!file.startsWith(root + sep)) { response.writeHead(403).end(); return; }
    const info = await stat(file);
    if (!info.isFile()) { response.writeHead(404).end(); return; }
    response.writeHead(200, {'Content-Type':mime[extname(file)] || 'application/octet-stream','Content-Length':info.size,'X-Content-Type-Options':'nosniff'});
    response.end(request.method === 'HEAD' ? undefined : await readFile(file));
  } catch { response.writeHead(404).end('Not found'); }
});
server.on('error', error => { console.error(error.message); process.exitCode = 1; });
server.listen(port, host, () => console.log(`ESS viewer: http://${host}:${port}`));
