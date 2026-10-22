import * as THREE from 'three';

/** Three opposite-facing pairs: rows 1/2 form the four-unit group, row 3 the two-unit group. */
export function arrangeContainers(roots: THREE.Object3D[]): THREE.Box3 {
  const gap = .5 * .3048;
  const depth = new THREE.Box3().setFromObject(roots[0]).getSize(new THREE.Vector3()).z;
  const rows = [-depth - 3, -1, depth + 3];
  const bounds = new THREE.Box3();
  roots.forEach((root, index) => {
    root.position.set(0, 0, 0);
    root.rotation.set(0, index % 2 ? Math.PI : 0, 0);
    root.updateWorldMatrix(true, true);
    const body = new THREE.Box3().setFromObject(root);
    root.position.set(index % 2 ? gap / 2 - body.min.x : -gap / 2 - body.max.x,
      0, rows[Math.floor(index / 2)] - body.getCenter(new THREE.Vector3()).z);
    root.updateWorldMatrix(true, true);
    bounds.union(new THREE.Box3().setFromObject(root));
  });
  return bounds;
}
