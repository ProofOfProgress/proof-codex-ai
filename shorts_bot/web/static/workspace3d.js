/**
 * Shared 3D workspace — owner + agent see creature/camera moves in real time.
 * Coordinates: stored in Blender space (Y forward, Z up); Three.js display converts.
 */
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/controls/OrbitControls.js';
import { TransformControls } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/controls/TransformControls.js';
import { GLTFLoader } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/loaders/GLTFLoader.js';

function apiHeaders(extra = {}) {
  const h = { ...extra };
  if (window.__API_TOKEN__) h.Authorization = `Bearer ${window.__API_TOKEN__}`;
  return h;
}

/** Blender (x,y,z) → Three.js */
export function blenderToThree([x, y, z]) {
  return new THREE.Vector3(x, z, -y);
}

/** Three.js → Blender */
export function threeToBlender(v) {
  return [v.x, -v.z, v.y];
}

function eulerThreeToBlender(euler) {
  return [euler.x, euler.z, -euler.y];
}

function eulerBlenderToThree([x, y, z]) {
  return new THREE.Euler(x, z, -y, 'XYZ');
}

export function initWorkspace({ draftId, creatureUrl }) {
  const wrap = document.getElementById('canvas-wrap');
  const statusEl = document.getElementById('status');
  let ws = null;
  let layout = null;
  let remoteDrag = false;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0a0c12);
  scene.fog = new THREE.Fog(0x0a0c12, 8, 45);

  const camera = new THREE.PerspectiveCamera(50, 1, 0.1, 200);
  camera.position.set(0, 2.5, 12);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  wrap.appendChild(renderer.domElement);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(0, 1.2, -6);
  controls.update();

  // Night lighting
  scene.add(new THREE.AmbientLight(0x223344, 0.45));
  const street = new THREE.PointLight(0xffaa66, 2.2, 30);
  street.position.set(4, 5.2, 6);
  scene.add(street);
  const fill = new THREE.DirectionalLight(0x6688aa, 0.35);
  fill.position.set(-3, 8, 4);
  scene.add(fill);

  // Ground + gas station proxy (matches build_and_render layout)
  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(80, 80),
    new THREE.MeshStandardMaterial({ color: 0x0c0c10, roughness: 0.95 }),
  );
  ground.rotation.x = -Math.PI / 2;
  scene.add(ground);

  const pumpMat = new THREE.MeshStandardMaterial({ color: 0x1a1a20, roughness: 0.85 });
  const glowMat = new THREE.MeshStandardMaterial({
    color: 0xff7722,
    emissive: 0xff5500,
    emissiveIntensity: 0.8,
  });
  for (const x of [-3.5, 3.5]) {
    const pump = new THREE.Mesh(new THREE.BoxGeometry(0.6, 2.4, 0.5), pumpMat);
    pump.position.copy(blenderToThree([x, -8, 1.2]));
    scene.add(pump);
    const glow = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.08, 0.25), glowMat);
    glow.position.copy(blenderToThree([x, -8, 2.35]));
    scene.add(glow);
  }

  const creaturePivot = new THREE.Group();
  creaturePivot.name = 'creature';
  scene.add(creaturePivot);

  const shotCamera = new THREE.Group();
  shotCamera.name = 'shotCamera';
  const camHelper = new THREE.Mesh(
    new THREE.BoxGeometry(0.35, 0.22, 0.5),
    new THREE.MeshStandardMaterial({ color: 0x4488ff, transparent: true, opacity: 0.7 }),
  );
  shotCamera.add(camHelper);
  const camArrow = new THREE.ArrowHelper(
    new THREE.Vector3(0, 0, -1),
    new THREE.Vector3(0, 0, 0),
    0.8,
    0x66aaff,
  );
  shotCamera.add(camArrow);
  scene.add(shotCamera);

  const transform = new TransformControls(camera, renderer.domElement);
  transform.setSpace('world');
  scene.add(transform);

  transform.addEventListener('dragging-changed', (e) => {
    controls.enabled = !e.value;
    if (!e.value && !remoteDrag) broadcastTransform();
  });
  transform.addEventListener('objectChange', () => {
    if (!remoteDrag) broadcastTransform(true);
  });

  let selectTarget = creaturePivot;
  transform.attach(creaturePivot);

  function applyLayout(data) {
    layout = data;
    const c = data.creature || {};
    const loc = c.location || [0, -7.5, 0];
    creaturePivot.position.copy(blenderToThree(loc));
    if (c.rotation) creaturePivot.rotation.copy(eulerBlenderToThree(c.rotation));
    if (c.scale) creaturePivot.scale.set(c.scale[0], c.scale[2] ?? c.scale[1], c.scale[1] ?? c.scale[2]);

    const cam = data.camera || {};
    const cloc = cam.location || [0, 2, 1.65];
    shotCamera.position.copy(blenderToThree(cloc));
    if (cam.rotation) shotCamera.rotation.copy(eulerBlenderToThree(cam.rotation));
  }

  function layoutFromScene() {
    return {
      creature: {
        location: threeToBlender(creaturePivot.position),
        rotation: eulerThreeToBlender(creaturePivot.rotation),
        scale: [creaturePivot.scale.x, creaturePivot.scale.z, creaturePivot.scale.y],
      },
      camera: {
        location: threeToBlender(shotCamera.position),
        rotation: eulerThreeToBlender(shotCamera.rotation),
        lens: (layout && layout.camera && layout.camera.lens) || 24,
      },
    };
  }

  function broadcastTransform(live = false) {
    const patch = layoutFromScene();
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: live ? 'transform_live' : 'transform', ...patch }));
    }
  }

  async function saveLayout() {
    statusEl.textContent = 'Saving…';
    const body = layoutFromScene();
    const res = await fetch(`/api/workspace/draft/${draftId}/scene`, {
      method: 'PUT',
      headers: apiHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      statusEl.textContent = 'Save failed';
      return;
    }
    layout = await res.json();
    statusEl.textContent = 'Saved — render will use this layout';
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'saved', layout }));
    }
  }

  function connectWs() {
    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    let url = `${proto}://${location.host}/ws/workspace/${draftId}`;
    if (window.__API_TOKEN__) url += `?token=${encodeURIComponent(window.__API_TOKEN__)}`;
    ws = new WebSocket(url);
    ws.onopen = () => { statusEl.textContent = 'Live — shared workspace'; };
    ws.onclose = () => {
      statusEl.textContent = 'Disconnected — reconnecting…';
      setTimeout(connectWs, 2000);
    };
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg.type === 'layout' || msg.type === 'saved') {
          remoteDrag = true;
          applyLayout(msg.layout);
          remoteDrag = false;
        } else if (msg.type === 'transform' || msg.type === 'transform_live') {
          remoteDrag = true;
          if (msg.creature) {
            const c = msg.creature;
            if (c.location) creaturePivot.position.copy(blenderToThree(c.location));
            if (c.rotation) creaturePivot.rotation.copy(eulerBlenderToThree(c.rotation));
            if (c.scale) creaturePivot.scale.set(c.scale[0], c.scale[2], c.scale[1]);
          }
          if (msg.camera) {
            const cam = msg.camera;
            if (cam.location) shotCamera.position.copy(blenderToThree(cam.location));
            if (cam.rotation) shotCamera.rotation.copy(eulerBlenderToThree(cam.rotation));
          }
          remoteDrag = false;
        }
      } catch (_) { /* ignore */ }
    };
  }

  document.getElementById('btn-select-creature').onclick = () => {
    selectTarget = creaturePivot;
    transform.attach(creaturePivot);
    document.getElementById('btn-select-creature').classList.add('active');
    document.getElementById('btn-select-camera').classList.remove('active');
  };
  document.getElementById('btn-select-camera').onclick = () => {
    selectTarget = shotCamera;
    transform.attach(shotCamera);
    document.getElementById('btn-select-camera').classList.add('active');
    document.getElementById('btn-select-creature').classList.remove('active');
  };
  document.getElementById('btn-reset').onclick = async () => {
    const res = await fetch(`/api/workspace/draft/${draftId}/scene/default`);
    if (res.ok) applyLayout(await res.json());
  };
  document.getElementById('btn-save').onclick = saveLayout;

  const loader = new GLTFLoader();
  loader.load(
    creatureUrl,
    (gltf) => {
      const model = gltf.scene;
      model.traverse((o) => {
        if (o.isMesh) {
          o.castShadow = true;
          o.material = o.material.clone();
          if (o.material.color) o.material.color.multiplyScalar(0.55);
        }
      });
      const box = new THREE.Box3().setFromObject(model);
      const h = box.max.y - box.min.y || 2;
      model.scale.setScalar(2.45 / h);
      model.position.y = -box.min.y * (2.45 / h);
      creaturePivot.add(model);
      if (layout) applyLayout(layout);
    },
    undefined,
    () => { statusEl.textContent = 'Creature model loading… (proxy still draggable)'; },
  );

  fetch(`/api/workspace/draft/${draftId}/scene`)
    .then((r) => r.json())
    .then((data) => { layout = data; applyLayout(data); })
    .catch(() => {});

  connectWs();

  function resize() {
    const w = wrap.clientWidth;
    const h = wrap.clientHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  }
  window.addEventListener('resize', resize);
  resize();

  function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
  }
  animate();
}
