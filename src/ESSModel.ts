import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

/** Exported glTF uses right-handed coordinates; angle signs differ from Unity. */
const DOORS = [...Array.from({ length: 6 }, (_, i) => ({ name: `Door_Hinge_${String(i + 1).padStart(2, '0')}`, angle: 105 })),
  { name: 'Front_Left_Hinge', angle: 100 }, { name: 'Front_Right_Hinge', angle: -100 }];

export class ESSModel {
  readonly root: THREE.Group;
  private readonly doors: { node: THREE.Object3D; target: THREE.Quaternion; angle: number }[];
  private readonly closed = new THREE.Quaternion();
  private constructor(root: THREE.Group) {
    this.root = root;
    this.doors = DOORS.map(({ name, angle }) => {
      const node = root.getObjectByName(name);
      if (!node) throw new Error(`Missing door: ${name}`);
      return { node, angle, target: node.quaternion.clone() };
    });
  }
  static async load(url: string): Promise<ESSModel> {
    const { scene } = await new GLTFLoader().loadAsync(url);
    return new ESSModel(scene);
  }
  setDoor(name: string, open: boolean): void {
    const door = this.doors.find(d => d.node.name === name);
    if (!door) throw new Error(`Unknown door: ${name}`);
    door.target.setFromAxisAngle(THREE.Object3D.DEFAULT_UP, open ? THREE.MathUtils.degToRad(door.angle) : 0);
  }
  setAll(open: boolean): void { for (const door of this.doors) this.setDoor(door.node.name, open); }
  toggleObject(object: THREE.Object3D): string | null {
    for (let current: THREE.Object3D | null = object; current; current = current.parent) {
      const door = this.doors.find(d => d.node === current);
      if (door) { this.setDoor(door.node.name, door.target.angleTo(this.closed) < .01); return door.node.name; }
    }
    return null;
  }
  update(deltaSeconds: number): void {
    for (const door of this.doors) door.node.quaternion.rotateTowards(door.target, THREE.MathUtils.degToRad(140) * Math.min(deltaSeconds, .1));
  }
  dispose(): void {
    const geometries = new Set<THREE.BufferGeometry>(); const materials = new Set<THREE.Material>();
    this.root.traverse(object => { if (object instanceof THREE.Mesh) { geometries.add(object.geometry); for (const material of [object.material].flat()) materials.add(material); } });
    geometries.forEach(g => g.dispose()); materials.forEach(m => m.dispose()); this.root.removeFromParent();
  }
}
