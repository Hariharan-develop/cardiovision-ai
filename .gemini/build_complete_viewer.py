import json, os

with open(r'c:\Users\hario\Downloads\CardioVision-AI\.gemini\curated_entries.json', 'r', encoding='utf-8') as f:
    entries = json.load(f)

print(f"Loaded {len(entries)} curated entries.")

viewer_html = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>CardioVision AI | Complete 3D Anatomical Heart Inspector</title>
<style>
  :root { color-scheme: dark; font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, sans-serif; }
  * { box-sizing: border-box; }
  body { margin: 0; background: #08182d; color: #eaf2ff; overflow: hidden; }
  #canvas { width: 100vw; height: 100vh; display: block; }
  
  /* Left Controls Panel */
  .panel {
    position: absolute;
    top: 16px;
    left: 16px;
    z-index: 10;
    width: min(340px, calc(100vw - 32px));
    max-height: calc(100vh - 32px);
    overflow-y: auto;
    padding: 16px 18px;
    border: 1px solid #2d4c70;
    border-radius: 14px;
    background: #0f233be8;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.45);
  }
  .panel::-webkit-scrollbar { width: 6px; }
  .panel::-webkit-scrollbar-thumb { background: #355376; border-radius: 3px; }

  h1 { font-size: 17px; font-weight: 750; margin: 0 0 3px; color: #ffffff; letter-spacing: -0.2px; }
  .subtitle { color: #8eb3dc; font-size: 11.5px; margin: 0 0 12px; line-height: 1.4; }
  
  #status {
    font-size: 11.5px;
    font-weight: 600;
    color: #cfe3fd;
    padding: 8px 12px;
    border-radius: 7px;
    background: #16365a;
    border: 1px solid #2a527c;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .spinner {
    width: 12px;
    height: 12px;
    border: 2px solid #548cd1;
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    display: inline-block;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  .preset-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-bottom: 12px;
  }
  .btn-preset {
    padding: 8px 10px;
    border-radius: 7px;
    border: 1px solid #3b6594;
    background: #173d66;
    color: #eaf2ff;
    font-size: 11.5px;
    font-weight: 650;
    cursor: pointer;
    transition: all 0.15s ease;
    text-align: center;
  }
  .btn-preset:hover { background: #225388; border-color: #5387c2; }
  .btn-preset.active { background: #1c62ad; border-color: #69a7ef; box-shadow: 0 0 10px rgba(42, 134, 239, 0.35); }

  .view-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 5px;
    margin: 8px 0 12px;
  }
  .btn-view {
    padding: 5px 6px;
    border-radius: 5px;
    border: 1px solid #2d4c70;
    background: #142e4c;
    color: #cbe0f8;
    font-size: 10.5px;
    font-weight: 600;
    cursor: pointer;
    text-align: center;
  }
  .btn-view:hover { background: #1f456e; border-color: #4a75a3; color: #fff; }

  .section { border-top: 1px solid #233e5c; padding-top: 11px; margin-top: 11px; }
  .section h2 {
    font-size: 11px;
    font-weight: 750;
    color: #7fa8d5;
    letter-spacing: .06em;
    text-transform: uppercase;
    margin: 0 0 8px;
  }
  
  label.toggle {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    margin: 6px 0;
    cursor: pointer;
    color: #dbe8f7;
    user-select: none;
  }
  label.toggle:hover { color: #ffffff; }
  label.toggle input { accent-color: #2a86ef; width: 15px; height: 15px; cursor: pointer; }
  .dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; flex: none; }
  .count-badge { font-size: 10px; color: #7fa8d5; margin-left: auto; background: #0c1c2e; padding: 1px 6px; border-radius: 10px; }

  input[type="range"] {
    width: 100%;
    accent-color: #2a86ef;
    margin-top: 5px;
    cursor: pointer;
  }
  .range-meta { display: flex; justify-content: space-between; font-size: 11px; color: #8eb3dc; }

  /* Top Right Inspection Card */
  #detail {
    position: absolute;
    top: 16px;
    right: 16px;
    max-width: min(340px, calc(100vw - 390px));
    padding: 14px 16px;
    background: #0f233be8;
    border: 1px solid #2d4c70;
    border-radius: 12px;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    font-size: 12px;
    line-height: 1.45;
  }
  #detail strong { display: block; font-size: 13px; color: #ffffff; margin-bottom: 3px; }
  #detail .sublabel { color: #64b5f6; font-weight: 600; font-size: 11.5px; margin-bottom: 2px; }
  #detail .filename { font-family: monospace; font-size: 10.5px; color: #9bbcdb; word-break: break-all; }

  .footer-note {
    position: absolute;
    bottom: 12px;
    right: 16px;
    max-width: 460px;
    color: #8daacb;
    font-size: 10.5px;
    text-align: right;
    pointer-events: none;
    text-shadow: 0 1px 4px #000;
  }

  @media (max-width: 760px) {
    .panel { max-height: 52vh; width: calc(100vw - 24px); left: 12px; top: 12px; }
    #detail { top: auto; bottom: 65px; right: 12px; max-width: calc(100vw - 24px); }
  }
</style>
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
  }
}
</script>
</head>
<body>

<div class="panel">
  <h1>CardioVision AI · 3D Heart</h1>
  <p class="subtitle">Anatomical BodyParts3D Assembly &amp; Multi-Vessel Coronary Model</p>
  
  <div id="status"><span class="spinner"></span> Initializing meshes...</div>

  <!-- Presets -->
  <div class="preset-row">
    <button class="btn-preset active" id="presetComplete">Complete Heart</button>
    <button class="btn-preset" id="presetCoronary">Coronary Focus</button>
  </div>

  <!-- Camera Views -->
  <div class="section" style="margin-top:0; padding-top:4px; border-top:none;">
    <h2>Anatomical Camera Views</h2>
    <div class="view-grid">
      <button class="btn-view" data-view="front">Anterior (Front)</button>
      <button class="btn-view" data-view="back">Posterior (Back)</button>
      <button class="btn-view" data-view="left">Left Lateral</button>
      <button class="btn-view" data-view="right">Right Lateral</button>
      <button class="btn-view" data-view="top">Base (Top)</button>
      <button class="btn-view" data-view="bottom">Apex (Bottom)</button>
    </div>
    <button class="btn-view" id="btnReset" style="width:100%; padding:6px;">Reset Camera (Perspective)</button>
  </div>

  <!-- Heart Muscle & Internal Anatomy -->
  <div class="section">
    <h2>Heart Anatomy &amp; Walls</h2>
    <label class="toggle"><input type="checkbox" data-group="ventricles" checked /><span class="dot" style="background:#b95c64"></span> Ventricles &amp; Septa <span class="count-badge">7</span></label>
    <label class="toggle"><input type="checkbox" data-group="atria" checked /><span class="dot" style="background:#c87a80"></span> Atria &amp; Auricles <span class="count-badge">11</span></label>
    <label class="toggle"><input type="checkbox" data-group="great_vessels" checked /><span class="dot" style="background:#cba099"></span> Great Vessels (Aorta &amp; PT) <span class="count-badge">3</span></label>
    <label class="toggle"><input type="checkbox" data-group="valves" checked /><span class="dot" style="background:#ede4d8"></span> Cardiac Valves &amp; Annuli <span class="count-badge">14</span></label>
    <label class="toggle"><input type="checkbox" data-group="cardiac_veins" /><span class="dot" style="background:#388bb8"></span> Cardiac Veins &amp; Sinus <span class="count-badge">5</span></label>
    
    <div style="margin-top:10px;">
      <div class="range-meta"><span>Myocardium Opacity</span><span id="opacityLabel">100%</span></div>
      <input type="range" id="opacity" min="15" max="100" value="100" step="5" />
    </div>
  </div>

  <!-- Coronary Arteries -->
  <div class="section">
    <h2>Coronary Arteries (Target Models)</h2>
    <label class="toggle"><input type="checkbox" data-group="left_coronary_stem" checked /><span class="dot" style="background:#e3d2bb"></span> Left Coronary Stem (LM) <span class="count-badge">1</span></label>
    <label class="toggle"><input type="checkbox" data-group="lad" checked /><span class="dot" style="background:#2a86ef"></span> LAD Trunk (Anterior Descending) <span class="count-badge">3</span></label>
    <label class="toggle"><input type="checkbox" data-group="lad_branches" checked /><span class="dot" style="background:#4da1ff"></span> LAD Branches (Diagonals &amp; Septals) <span class="count-badge">6</span></label>
    <label class="toggle"><input type="checkbox" data-group="lcx" checked /><span class="dot" style="background:#0fb77d"></span> LCX Trunk (Circumflex) <span class="count-badge">2</span></label>
    <label class="toggle"><input type="checkbox" data-group="lcx_branches" checked /><span class="dot" style="background:#38d7a1"></span> LCX Branches (Marginals &amp; Post) <span class="count-badge">3</span></label>
    <label class="toggle"><input type="checkbox" data-group="rca" checked /><span class="dot" style="background:#ff9900"></span> RCA Trunk (Right Coronary) <span class="count-badge">3</span></label>
    <label class="toggle"><input type="checkbox" data-group="rca_branches" checked /><span class="dot" style="background:#ffb74d"></span> RCA Branches (Marginal, SA, AV) <span class="count-badge">7</span></label>
  </div>
</div>

<div id="detail">
  <strong>Anatomical Inspector</strong>
  <span style="color:#8eb3dc;">Click any coronary artery or myocardial structure to identify its anatomical name and details.</span>
</div>

<canvas id="canvas"></canvas>

<div class="footer-note">
  BodyParts3D / Anatomography Postnatal Heart Dataset (BP51782) · Research &amp; Educational Visualization.
</div>

<script type="module">
import * as THREE from 'three';
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const entries = """ + json.dumps(entries, indent=2) + """;

// Color definitions matching clinical standards & user requirements
const colorMap = {
  ventricles: '#b95c64',        // Deep myocardial muscle
  atria: '#c87a80',             // Atrial wall tissue
  great_vessels: '#cba099',     // Aorta and pulmonary trunk
  valves: '#ede4d8',            // Fibrous valve cusps & annuli
  left_coronary_stem: '#e3d2bb',// Left Main trunk
  lad: '#2a86ef',               // LAD Blue (#2a86ef)
  lad_branches: '#4da1ff',      // LAD branches
  lcx: '#0fb77d',               // LCX Green (#0fb77d)
  lcx_branches: '#38d7a1',      // LCX branches
  rca: '#ff9900',               // RCA Orange (#ff9900)
  rca_branches: '#ffb74d',      // RCA branches
  cardiac_veins: '#388bb8'      // Venous system
};

const heartGroups = new Set(['ventricles', 'atria', 'great_vessels', 'valves']);
const arteryGroups = new Set(['left_coronary_stem', 'lad', 'lad_branches', 'lcx', 'lcx_branches', 'rca', 'rca_branches']);

// Scene setup
const scene = new THREE.Scene();
scene.background = new THREE.Color('#08182d');

const camera = new THREE.PerspectiveCamera(40, innerWidth / innerHeight, 0.01, 1000);
// BodyParts3D coordinates use Z as superior/inferior anatomical axis:
camera.up.set(0, 0, 1);

const renderer = new THREE.WebGLRenderer({
  canvas: document.querySelector('#canvas'),
  antialias: true,
  alpha: false,
  powerPreference: 'high-performance'
});
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.35;

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.minDistance = 2.0;
controls.maxDistance = 25.0;

// High-fidelity anatomical lighting
const hemiLight = new THREE.HemisphereLight(0xf0f6ff, 0x1f2b3e, 1.8);
scene.add(hemiLight);

const keyLight = new THREE.DirectionalLight(0xffffff, 2.6);
keyLight.position.set(-3.5, -6.5, 6.0);
scene.add(keyLight);

const fillLight = new THREE.DirectionalLight(0xbdd4f5, 1.4);
fillLight.position.set(5.0, 4.5, 2.5);
scene.add(fillLight);

const backLight = new THREE.DirectionalLight(0x82a5d4, 1.2);
backLight.position.set(0.0, 6.0, -4.0);
scene.add(backLight);

const root = new THREE.Group();
scene.add(root);

// Materials cache
const materials = {};
const objectsByGroup = new Map();

for (const group of Object.keys(colorMap)) {
  const isArtery = arteryGroups.has(group);
  const isVein = (group === 'cardiac_veins');
  
  materials[group] = new THREE.MeshStandardMaterial({
    color: colorMap[group],
    roughness: isArtery ? 0.38 : isVein ? 0.45 : 0.62,
    metalness: isArtery ? 0.08 : 0.03,
    side: isArtery || isVein ? THREE.FrontSide : THREE.DoubleSide,
    transparent: false,
    opacity: 1.0,
    depthWrite: true,
    polygonOffset: isArtery || isVein,
    polygonOffsetFactor: isArtery ? -1.8 : -1.0,
    polygonOffsetUnits: isArtery ? -4.0 : -2.0
  });
  objectsByGroup.set(group, []);
}

// Camera Presets
const defaultCamPos = new THREE.Vector3(0, -7.5, 2.0);
function setView(viewName) {
  controls.target.set(0, 0, 0);
  switch (viewName) {
    case 'front':  // Anterior
      camera.position.set(0, -8.0, 0.4);
      break;
    case 'back':   // Posterior
      camera.position.set(0, 8.0, 0.4);
      break;
    case 'left':   // Left lateral (LV / LA)
      camera.position.set(8.0, 0, 0.4);
      break;
    case 'right':  // Right lateral (RV / RA)
      camera.position.set(-8.0, 0, 0.4);
      break;
    case 'top':    // Superior (Base / Great vessels)
      camera.position.set(0, -0.2, 8.0);
      break;
    case 'bottom': // Inferior (Apex)
      camera.position.set(0, -0.2, -8.0);
      break;
    default:       // Perspective reset
      camera.position.copy(defaultCamPos);
      break;
  }
  camera.lookAt(0, 0, 0);
  controls.update();
}

function refreshVisibility() {
  for (const [group, objs] of objectsByGroup.entries()) {
    const input = document.querySelector(`[data-group="${group}"]`);
    const isVisible = Boolean(input?.checked);
    for (const obj of objs) {
      obj.visible = isVisible;
      obj.traverse(child => {
        if (child.isMesh) child.visible = isVisible;
      });
    }
  }

  if (currentlySelectedChild && currentlySelectedChild.userData) {
    const selGroup = currentlySelectedChild.userData.group;
    const input = document.querySelector(`[data-group="${selGroup}"]`);
    if (input && !input.checked) {
      selectMesh(null);
    }
  }
}

function setHeartOpacity(val) {
  const op = val / 100;
  for (const group of heartGroups) {
    const mat = materials[group];
    mat.opacity = op;
    mat.transparent = op < 1.0;
    mat.depthWrite = (op >= 0.95);
    mat.needsUpdate = true;
  }
  document.querySelector('#opacityLabel').textContent = `${val}%`;
}

function applyPreset(preset) {
  const completeBtn = document.querySelector('#presetComplete');
  const coronaryBtn = document.querySelector('#presetCoronary');

  if (preset === 'complete') {
    completeBtn.classList.add('active');
    coronaryBtn.classList.remove('active');
    
    // All heart structures ON
    for (const g of heartGroups) {
      const input = document.querySelector(`[data-group="${g}"]`);
      if (input) input.checked = true;
    }
    // All coronary arteries ON
    for (const g of arteryGroups) {
      const input = document.querySelector(`[data-group="${g}"]`);
      if (input) input.checked = true;
    }
    document.querySelector('#opacity').value = 100;
    setHeartOpacity(100);
  } else if (preset === 'coronary') {
    coronaryBtn.classList.add('active');
    completeBtn.classList.remove('active');
    
    // Coronary focus: All arteries ON
    for (const g of arteryGroups) {
      const input = document.querySelector(`[data-group="${g}"]`);
      if (input) input.checked = true;
    }
    // Heart anatomy ON but translucent ghost (30%)
    for (const g of heartGroups) {
      const input = document.querySelector(`[data-group="${g}"]`);
      if (input) input.checked = true;
    }
    document.querySelector('#opacity').value = 30;
    setHeartOpacity(30);
  }
  refreshVisibility();
}

function selectMesh(obj) {
  for (const mat of Object.values(materials)) mat.emissive.set('#000000');
  const detail = document.querySelector('#detail');
  
  if (!obj || !obj.userData) {
    detail.innerHTML = '<strong>Anatomical Inspector</strong><span style="color:#8eb3dc;">Click any coronary artery or myocardial structure to identify its anatomical name and details.</span>';
    return;
  }

  const grp = obj.userData.group;
  if (materials[grp]) {
    materials[grp].emissive.set('#3a3a3a');
  }

  const col = colorMap[grp] || '#fff';
  detail.innerHTML = `
    <div style="display:flex;align-items:center;gap:7px;margin-bottom:3px;">
      <span class="dot" style="background:${col};width:11px;height:11px;"></span>
      <strong style="margin:0;">${obj.userData.label || obj.userData.id}</strong>
    </div>
    <div class="sublabel">${grp.toUpperCase().replace(/_/g, ' ')} (${obj.userData.id})</div>
    <div class="filename">${obj.userData.filename}</div>
  `;
}

// Concurrency-controlled OBJ Loader
const loader = new OBJLoader();
const loaded = [];
let failures = 0;

async function loadMeshWithRetry(entry, maxRetries = 2) {
  const path = './models/' + encodeURIComponent(entry.filename);
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const obj = await loader.loadAsync(path);
      obj.userData = { ...entry };
      
      const isArtery = arteryGroups.has(entry.group);
      const isVein = (entry.group === 'cardiac_veins');
      
      obj.traverse((child) => {
        if (child.isMesh) {
          child.material = materials[entry.group];
          child.userData = { ...entry };
          // Enable smooth normal computation for realistic shading without faceted artifacts
          if (child.geometry) {
            child.geometry.computeVertexNormals();
          }
          child.renderOrder = isArtery ? 10 : isVein ? 8 : 1;
        }
      });
      return obj;
    } catch (e) {
      if (attempt === maxRetries) throw e;
      await new Promise(r => setTimeout(r, 200 * (attempt + 1)));
    }
  }
}

async function loadAllMeshes() {
  const statusEl = document.querySelector('#status');
  const CONCURRENCY = 6;
  let nextIdx = 0;
  let completed = 0;

  async function worker() {
    while (nextIdx < entries.length) {
      const idx = nextIdx++;
      const entry = entries[idx];
      try {
        const obj = await loadMeshWithRetry(entry);
        root.add(obj);
        objectsByGroup.get(entry.group).push(obj);
        loaded.push(obj);
      } catch (err) {
        failures++;
        console.error('Failed to load', entry.filename, err);
      } finally {
        completed++;
        statusEl.innerHTML = `<span class="spinner"></span> Loading ${completed}/${entries.length} meshes (${Math.round(completed/entries.length*100)}%)...`;
      }
    }
  }

  const workers = Array.from({ length: CONCURRENCY }, () => worker());
  await Promise.all(workers);

  // Apply one shared transform to the complete heart assembly
  if (loaded.length) {
    const bounds = new THREE.Box3().setFromObject(root);
    const center = bounds.getCenter(new THREE.Vector3());
    const size = bounds.getSize(new THREE.Vector3());
    const maxDimension = Math.max(size.x, size.y, size.z);
    if (maxDimension > 0 && Number.isFinite(maxDimension)) {
      const scale = 4.2 / maxDimension;
      root.scale.setScalar(scale);
      root.position.copy(center).multiplyScalar(-scale);
    }
  }

  refreshVisibility();
  setView('front');

  if (failures === 0) {
    statusEl.innerHTML = `<span style="color:#4ade80;">✓</span> Complete heart loaded (${loaded.length}/${entries.length} meshes)`;
  } else {
    statusEl.innerHTML = `<span style="color:#fbbf24;">⚠</span> ${loaded.length}/${entries.length} loaded · ${failures} failed`;
  }
}

// Event Listeners
for (const input of document.querySelectorAll('[data-group]')) {
  input.addEventListener('change', refreshVisibility);
}

document.querySelector('#opacity').addEventListener('input', e => setHeartOpacity(Number(e.target.value)));
document.querySelector('#presetComplete').addEventListener('click', () => applyPreset('complete'));
document.querySelector('#presetCoronary').addEventListener('click', () => applyPreset('coronary'));

document.querySelector('#btnReset').addEventListener('click', () => setView('reset'));
for (const btn of document.querySelectorAll('[data-view]')) {
  btn.addEventListener('click', () => setView(btn.dataset.view));
}

// Raycasting for interactive selection
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
let pointerDownPos = null;

renderer.domElement.addEventListener('pointerdown', e => {
  pointerDownPos = [e.clientX, e.clientY];
});

function isMeshEligibleForRaycast(mesh) {
  if (!mesh || !mesh.isMesh) return false;
  let curr = mesh;
  while (curr) {
    if (curr.visible === false) return false;
    curr = curr.parent;
  }
  const grp = mesh.userData ? mesh.userData.group : null;
  if (grp) {
    const input = document.querySelector(`[data-group="${grp}"]`);
    if (input && !input.checked) return false;
  }
  const isOuterMyocardium = (grp === 'ventricles' || grp === 'atria' || grp === 'great_vessels');
  const coronaryBtn = document.querySelector('#presetCoronary');
  const isCoronaryPresetActive = coronaryBtn && coronaryBtn.classList.contains('active');
  const currentOpacity = (materials[grp] && materials[grp].opacity !== undefined) ? materials[grp].opacity : 1.0;
  if (isOuterMyocardium && (isCoronaryPresetActive || currentOpacity < 0.50)) {
    return false;
  }
  if (mesh.material && mesh.material.opacity !== undefined && mesh.material.opacity <= 0.02) {
    return false;
  }
  return true;
}

function getSelectableMeshes() {
  const selectables = [];
  root.traverse(child => {
    if (isMeshEligibleForRaycast(child)) {
      selectables.push(child);
    }
  });
  return selectables;
}

renderer.domElement.addEventListener('pointerup', e => {
  if (!pointerDownPos || Math.hypot(e.clientX - pointerDownPos[0], e.clientY - pointerDownPos[1]) > 5) return;
  const rect = renderer.domElement.getBoundingClientRect();
  pointer.x = (e.clientX - rect.left) / rect.width * 2 - 1;
  pointer.y = -(e.clientY - rect.top) / rect.height * 2 + 1;
  raycaster.setFromCamera(pointer, camera);
  
  const selectableMeshes = getSelectableMeshes();
  const hits = raycaster.intersectObjects(selectableMeshes, false);
  let targetHit = null;
  for (const hit of hits) {
    if (isMeshEligibleForRaycast(hit.object)) {
      targetHit = hit;
      break;
    }
  }
  if (targetHit) {
    selectMesh(targetHit.object);
  } else {
    selectMesh(null);
  }
});

window.addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}
animate();
loadAllMeshes();
</script>
</body>
</html>
"""

# Write to both locations
dest1 = r'C:\Users\hario\Downloads\CardioVision_BodyParts3D_ThreeJS_Preview\CardioVision_3D_Preview\viewer.html'
dest2 = r'c:\Users\hario\Downloads\CardioVision-AI\3d-test\viewer.html'

with open(dest1, 'w', encoding='utf-8') as f:
    f.write(viewer_html)
print(f"Updated {dest1} ({len(viewer_html)} bytes)")

with open(dest2, 'w', encoding='utf-8') as f:
    f.write(viewer_html)
print(f"Updated {dest2} ({len(viewer_html)} bytes)")
