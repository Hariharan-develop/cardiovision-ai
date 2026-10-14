import json, re

with open('.gemini/final_heart_entries.json') as f:
    entries = json.load(f)

# Sort entries cleanly by group, then by id
group_order = [
    'ventricles', 'internal_myocardium', 'atria', 'great_vessels', 'valves', 
    'conduction_system', 'cardiac_veins', 'left_coronary_stem', 
    'lad', 'lad_branches', 'lcx', 'lcx_branches', 'rca', 'rca_branches'
]
group_order_map = {g: i for i, g in enumerate(group_order)}
entries.sort(key=lambda x: (group_order_map.get(x['group'], 99), x['id']))

# Calculate counts per group
counts = {}
for e in entries:
    counts[e['group']] = counts.get(e['group'], 0) + 1

print(f"Total entries: {len(entries)}")
for g in group_order:
    print(f"  {g}: {counts.get(g, 0)}")

# Generate full updated viewer.html
html_template = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>CardioVision AI | Complete 3D Anatomical Heart Inspector</title>
<style>
  :root { color-scheme: dark; font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, sans-serif; }
  * { box-sizing: border-box; }
  body { margin: 0; background: #071526; color: #eaf2ff; overflow: hidden; }
  #canvas { width: 100vw; height: 100vh; display: block; }
  
  /* Left Controls Panel */
  .panel {
    position: absolute;
    top: 16px;
    left: 16px;
    z-index: 10;
    width: min(350px, calc(100vw - 32px));
    max-height: calc(100vh - 32px);
    overflow-y: auto;
    padding: 16px 18px;
    border: 1px solid #233e5c;
    border-radius: 14px;
    background: #0d1e34ea;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.55);
  }
  .panel::-webkit-scrollbar { width: 5px; }
  .panel::-webkit-scrollbar-thumb { background: #2f4d70; border-radius: 3px; }

  h1 { font-size: 16.5px; font-weight: 750; margin: 0 0 2px; color: #ffffff; letter-spacing: -0.2px; }
  .subtitle { color: #8eb3dc; font-size: 11px; margin: 0 0 11px; line-height: 1.35; }
  
  #status {
    font-size: 11.5px;
    font-weight: 600;
    color: #cfe3fd;
    padding: 7px 11px;
    border-radius: 7px;
    background: #142e4d;
    border: 1px solid #24466c;
    margin-bottom: 11px;
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
    gap: 7px;
    margin-bottom: 11px;
  }
  .btn-preset {
    padding: 7px 9px;
    border-radius: 7px;
    border: 1px solid #35577f;
    background: #143457;
    color: #eaf2ff;
    font-size: 11px;
    font-weight: 650;
    cursor: pointer;
    transition: all 0.15s ease;
    text-align: center;
  }
  .btn-preset:hover { background: #1c4777; border-color: #4f7cb5; }
  .btn-preset.active { background: #1a5ea8; border-color: #639fe6; box-shadow: 0 0 10px rgba(42, 134, 239, 0.35); }

  .view-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 5px;
    margin: 6px 0 10px;
  }
  .btn-view {
    padding: 5px 6px;
    border-radius: 5px;
    border: 1px solid #284465;
    background: #11263e;
    color: #cbe0f8;
    font-size: 10px;
    font-weight: 600;
    cursor: pointer;
    text-align: center;
    transition: all 0.12s;
  }
  .btn-view:hover { background: #1c3d62; border-color: #426993; color: #fff; }

  .section { border-top: 1px solid #1c324a; padding-top: 10px; margin-top: 10px; }
  h2 { font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.7px; color: #7fa4cd; margin: 0 0 7px; }

  .toggle {
    display: flex;
    align-items: center;
    gap: 7px;
    padding: 3.5px 0;
    font-size: 11px;
    color: #dbe8fa;
    cursor: pointer;
    user-select: none;
  }
  .toggle:hover { color: #ffffff; }
  .toggle input[type="checkbox"] {
    accent-color: #2a86ef;
    cursor: pointer;
    width: 13px;
    height: 13px;
    margin: 0;
  }
  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
  }
  .count-badge {
    margin-left: auto;
    font-size: 9.5px;
    background: #152d47;
    border: 1px solid #213f62;
    padding: 1px 5px;
    border-radius: 4px;
    color: #9abedc;
    font-weight: 600;
  }

  .range-meta {
    display: flex;
    justify-content: space-between;
    font-size: 10.5px;
    color: #9cbddf;
    margin-bottom: 4px;
    font-weight: 550;
  }
  input[type="range"] {
    width: 100%;
    accent-color: #2a86ef;
    margin: 0;
    height: 4px;
  }

  /* Right Anatomical Inspector Card */
  #detail {
    position: absolute;
    top: 16px;
    right: 16px;
    z-index: 10;
    width: min(340px, calc(100vw - 32px));
    padding: 14px 16px;
    border: 1px solid #233e5c;
    border-radius: 12px;
    background: #0d1e34ea;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.55);
    font-size: 11.5px;
    line-height: 1.45;
  }
  #detail strong { display: block; font-size: 13px; color: #fff; margin-bottom: 3px; }
  #detail .sublabel { color: #8eb3dc; font-size: 10px; font-weight: 650; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px; }
  #detail .filename { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 9.5px; color: #7fa4cd; word-break: break-all; background: #13273e; padding: 4px 6px; border-radius: 5px; border: 1px solid #1e3a5a; }

  .footer-note {
    position: absolute;
    bottom: 12px;
    right: 16px;
    font-size: 10px;
    color: #607e9e;
    z-index: 5;
    pointer-events: none;
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
  <div class="subtitle">Complete Anatomical BodyParts3D Assembly &amp; Multi-Vessel Coronary Model</div>

  <div id="status"><span class="spinner"></span> Initializing cardiac meshes...</div>

  <div class="preset-row">
    <button class="btn-preset active" id="presetComplete">Complete Heart</button>
    <button class="btn-preset" id="presetCoronary">Coronary Focus</button>
  </div>

  <div class="section" style="border-top:none; padding-top:0; margin-top:0;">
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
    <label class="toggle"><input type="checkbox" data-group="ventricles" checked /><span class="dot" style="background:#b85b63"></span> Ventricles &amp; Septa <span class="count-badge">COUNT_VENTRICLES</span></label>
    <label class="toggle"><input type="checkbox" data-group="atria" checked /><span class="dot" style="background:#cf7d85"></span> Atria &amp; Auricles <span class="count-badge">COUNT_ATRIA</span></label>
    <label class="toggle"><input type="checkbox" data-group="great_vessels" checked /><span class="dot" style="background:#d4a39b"></span> Great Vessels (Aorta &amp; PT) <span class="count-badge">COUNT_VESSELS</span></label>
    <label class="toggle"><input type="checkbox" data-group="valves" checked /><span class="dot" style="background:#eee5d8"></span> Cardiac Valves &amp; Annuli <span class="count-badge">COUNT_VALVES</span></label>
    <label class="toggle"><input type="checkbox" data-group="internal_myocardium" checked /><span class="dot" style="background:#a84c55"></span> Papillary Muscles &amp; Trabeculae <span class="count-badge">COUNT_INTERNAL</span></label>
    <label class="toggle"><input type="checkbox" data-group="cardiac_veins" checked /><span class="dot" style="background:#2e7da9"></span> Cardiac Veins &amp; Sinus <span class="count-badge">COUNT_VEINS</span></label>
    <label class="toggle"><input type="checkbox" data-group="conduction_system" checked /><span class="dot" style="background:#f6c445"></span> Conduction System (SA/AV/His) <span class="count-badge">COUNT_CONDUCTION</span></label>
    
    <div style="margin-top:10px;">
      <div class="range-meta"><span>Myocardium Opacity</span><span id="opacityLabel">100%</span></div>
      <input type="range" id="opacity" min="15" max="100" value="100" step="5" />
    </div>
  </div>

  <!-- Coronary Arteries -->
  <div class="section">
    <h2>Coronary Arteries (Target Models)</h2>
    <label class="toggle"><input type="checkbox" data-group="left_coronary_stem" checked /><span class="dot" style="background:#e6d6c2"></span> Left Coronary Stem (LM) <span class="count-badge">COUNT_LM</span></label>
    <label class="toggle"><input type="checkbox" data-group="lad" checked /><span class="dot" style="background:#2a86ef"></span> LAD Trunk (Anterior Descending) <span class="count-badge">COUNT_LAD</span></label>
    <label class="toggle"><input type="checkbox" data-group="lad_branches" checked /><span class="dot" style="background:#4da1ff"></span> LAD Branches (Diagonals &amp; Septals) <span class="count-badge">COUNT_LAD_BR</span></label>
    <label class="toggle"><input type="checkbox" data-group="lcx" checked /><span class="dot" style="background:#0fb77d"></span> LCX Trunk (Circumflex) <span class="count-badge">COUNT_LCX</span></label>
    <label class="toggle"><input type="checkbox" data-group="lcx_branches" checked /><span class="dot" style="background:#38d7a1"></span> LCX Branches (Marginals &amp; Post) <span class="count-badge">COUNT_LCX_BR</span></label>
    <label class="toggle"><input type="checkbox" data-group="rca" checked /><span class="dot" style="background:#ff9900"></span> RCA Trunk (Right Coronary) <span class="count-badge">COUNT_RCA</span></label>
    <label class="toggle"><input type="checkbox" data-group="rca_branches" checked /><span class="dot" style="background:#ffb74d"></span> RCA Branches (Marginal, SA, AV) <span class="count-badge">COUNT_RCA_BR</span></label>
  </div>
</div>

<div id="detail">
  <strong>Anatomical Inspector</strong>
  <span style="color:#8eb3dc;">Click any coronary artery, myocardial wall or internal structure to inspect its anatomical identity and provenance.</span>
</div>

<canvas id="canvas"></canvas>

<div class="footer-note">
  BodyParts3D / Anatomography Postnatal Heart Dataset (BP51782) · Complete Verified Assembly.
</div>

<script type="module">
import * as THREE from 'three';
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const entries = ENTRIES_PLACEHOLDER;

// Clinical & Anatomical Color Definitions
const colorMap = {
  ventricles: '#b85b63',          // Myocardial muscle tissue
  internal_myocardium: '#a84c55', // Deep papillary muscles and trabeculae
  atria: '#cf7d85',               // Thinner atrial wall muscle
  great_vessels: '#d4a39b',       // Aortic root & pulmonary trunk
  valves: '#eee5d8',              // Fibrous cusps, annuli and trigones
  conduction_system: '#f6c445',   // Conduction nodes and bundle branches (Gold/amber)
  cardiac_veins: '#2e7da9',       // Venous system & coronary sinus
  left_coronary_stem: '#e6d6c2',  // Left Main stem
  lad: '#2a86ef',                 // LAD Blue (#2a86ef)
  lad_branches: '#4da1ff',        // LAD Diagonals & Septals
  lcx: '#0fb77d',                 // LCX Green (#0fb77d)
  lcx_branches: '#38d7a1',        // LCX Marginals & Post
  rca: '#ff9900',                 // RCA Orange (#ff9900)
  rca_branches: '#ffb74d'         // RCA Branches
};

const heartGroups = new Set(['ventricles', 'internal_myocardium', 'atria', 'great_vessels', 'valves', 'conduction_system', 'cardiac_veins']);
const arteryGroups = new Set(['left_coronary_stem', 'lad', 'lad_branches', 'lcx', 'lcx_branches', 'rca', 'rca_branches']);

// Scene setup
const scene = new THREE.Scene();
scene.background = new THREE.Color('#071526');

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

// High-fidelity anatomical illumination
const hemiLight = new THREE.HemisphereLight(0xf2f7ff, 0x182436, 1.85);
scene.add(hemiLight);

const keyLight = new THREE.DirectionalLight(0xffffff, 2.6);
keyLight.position.set(-3.5, -6.5, 6.0);
scene.add(keyLight);

const fillLight = new THREE.DirectionalLight(0xbdd4f5, 1.45);
fillLight.position.set(5.0, 4.5, 2.5);
scene.add(fillLight);

const backLight = new THREE.DirectionalLight(0x82a5d4, 1.25);
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
  const isConduction = (group === 'conduction_system');
  
  materials[group] = new THREE.MeshStandardMaterial({
    color: colorMap[group],
    roughness: isArtery ? 0.35 : isVein ? 0.42 : isConduction ? 0.35 : 0.58,
    metalness: isArtery ? 0.08 : isVein ? 0.06 : isConduction ? 0.15 : 0.04,
    side: isArtery || isVein ? THREE.FrontSide : THREE.DoubleSide,
    transparent: false,
    opacity: 1.0,
    depthWrite: true,
    polygonOffset: isArtery || isVein,
    polygonOffsetFactor: isArtery ? -2.5 : -1.2,
    polygonOffsetUnits: isArtery ? -5.0 : -2.5
  });
  objectsByGroup.set(group, []);
}

// Camera Presets
const defaultCamPos = new THREE.Vector3(0, -7.5, 1.8);
function setView(viewName) {
  controls.target.set(0, 0, 0);
  switch (viewName) {
    case 'front':  // Anterior
      camera.position.set(0, -8.0, 0.4);
      break;
    case 'back':   // Posterior
      camera.position.set(0, 8.0, 0.4);
      break;
    case 'left':   // Left lateral (LV / LCX / OM1)
      camera.position.set(8.0, 0, 0.4);
      break;
    case 'right':  // Right lateral (RV / RA / RCA)
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
    for (const obj of objs) obj.visible = isVisible;
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
    
    // Coronary focus: All arteries ON at full opacity
    for (const g of arteryGroups) {
      const input = document.querySelector(`[data-group="${g}"]`);
      if (input) input.checked = true;
    }
    // Heart anatomy ON but translucent ghost (25%) so arteries stand out in full 3D context
    for (const g of heartGroups) {
      const input = document.querySelector(`[data-group="${g}"]`);
      if (input) input.checked = true;
    }
    document.querySelector('#opacity').value = 25;
    setHeartOpacity(25);
  }
  refreshVisibility();
}

function selectMesh(obj) {
  for (const mat of Object.values(materials)) mat.emissive.set('#000000');
  const detail = document.querySelector('#detail');
  
  if (!obj || !obj.userData) {
    detail.innerHTML = '<strong>Anatomical Inspector</strong><span style="color:#8eb3dc;">Click any coronary artery, myocardial wall or internal structure to inspect its anatomical identity and provenance.</span>';
    return;
  }

  const grp = obj.userData.group;
  if (materials[grp]) {
    materials[grp].emissive.set('#3a3a3a');
  }

  const col = colorMap[grp] || '#fff';
  detail.innerHTML = `
    <div style="display:flex;align-items:center;gap:7px;margin-bottom:3px;">
      <span class="dot" style="background:${col};width:10px;height:10px;"></span>
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
      const isConduction = (entry.group === 'conduction_system');
      
      obj.traverse((child) => {
        if (child.isMesh) {
          child.material = materials[entry.group];
          child.userData = { ...entry };
          
          // Preserve high-fidelity smooth vertex normals from BodyParts3D OBJ meshes
          // Only compute if normals were not present in the OBJ file
          if (child.geometry && !child.geometry.attributes.normal) {
            child.geometry.computeVertexNormals();
          }
          child.renderOrder = isArtery ? 15 : isVein ? 10 : isConduction ? 12 : 1;
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
  const CONCURRENCY = 8;
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

renderer.domElement.addEventListener('pointerup', e => {
  if (!pointerDownPos || Math.hypot(e.clientX - pointerDownPos[0], e.clientY - pointerDownPos[1]) > 5) return;
  const rect = renderer.domElement.getBoundingClientRect();
  pointer.x = (e.clientX - rect.left) / rect.width * 2 - 1;
  pointer.y = -(e.clientY - rect.top) / rect.height * 2 + 1;
  raycaster.setFromCamera(pointer, camera);
  
  const visibleMeshes = [];
  root.traverse(child => {
    if (child.isMesh && child.visible) visibleMeshes.push(child);
  });
  
  const hits = raycaster.intersectObjects(visibleMeshes, false);
  if (hits.length > 0) {
    selectMesh(hits[0].object);
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
'''

# Replace placeholders
replacements = {
    'ENTRIES_PLACEHOLDER': json.dumps(entries, indent=2),
    'COUNT_VENTRICLES': str(counts.get('ventricles', 0)),
    'COUNT_ATRIA': str(counts.get('atria', 0)),
    'COUNT_VESSELS': str(counts.get('great_vessels', 0)),
    'COUNT_VALVES': str(counts.get('valves', 0)),
    'COUNT_INTERNAL': str(counts.get('internal_myocardium', 0)),
    'COUNT_VEINS': str(counts.get('cardiac_veins', 0)),
    'COUNT_CONDUCTION': str(counts.get('conduction_system', 0)),
    'COUNT_LM': str(counts.get('left_coronary_stem', 0)),
    'COUNT_LAD': str(counts.get('lad', 0)),
    'COUNT_LAD_BR': str(counts.get('lad_branches', 0)),
    'COUNT_LCX': str(counts.get('lcx', 0)),
    'COUNT_LCX_BR': str(counts.get('lcx_branches', 0)),
    'COUNT_RCA': str(counts.get('rca', 0)),
    'COUNT_RCA_BR': str(counts.get('rca_branches', 0)),
}

for k, v in replacements.items():
    html_template = html_template.replace(k, v)

with open('3d-test/viewer.html', 'w', encoding='utf-8') as out:
    out.write(html_template)

print("Successfully written 3d-test/viewer.html!")
