import os
import re

GEN_FILE = r"c:\Users\hario\Downloads\CardioVision-AI\.gemini\generate_components_viewer.py"

with open(GEN_FILE, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update HTML controls panel: Add Tissue Appearance section right above or below Coronary Color Mode
old_coronary_section = """  <!-- Coronary Visualization Modes -->
  <div class="section" style="border-top:none; padding-top:0; margin-top:0;">
    <h2>Coronary Color Mode</h2>
    <div class="preset-row">
      <button class="btn-preset active" id="modeAnatomy">Anatomy Mode</button>
      <button class="btn-preset" id="modeRisk">Risk Overlay</button>
    </div>"""

new_sections = """  <!-- Coronary Visualization Modes -->
  <div class="section" style="border-top:none; padding-top:0; margin-top:0;">
    <h2>Coronary Color Mode</h2>
    <div class="preset-row">
      <button class="btn-preset active" id="modeAnatomy">Anatomy Mode</button>
      <button class="btn-preset" id="modeRisk">Risk Overlay</button>
    </div>"""

tissue_appearance_section = """
  <!-- Tissue Appearance Style (Independent Control) -->
  <div class="section" style="border-top:none; padding-top:0; margin-top:0;">
    <h2>Tissue Appearance</h2>
    <div class="preset-row">
      <button class="btn-preset active" id="styleClinical">Clinical Colors</button>
      <button class="btn-preset" id="styleRealistic">Realistic Tissue</button>
    </div>
  </div>"""

if old_coronary_section in content and "id=\"styleClinical\"" not in content:
    content = content.replace(old_coronary_section, old_coronary_section + "\n" + tissue_appearance_section)
    print("Added Tissue Appearance section to HTML controls panel")
else:
    print("Tissue Appearance section check:", "Already present" if "id=\"styleClinical\"" in content else "Target not found")

# 2. Update JavaScript module imports: add BufferGeometryUtils
old_imports = """<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';"""

new_imports = """<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
import * as BufferGeometryUtils from 'three/addons/utils/BufferGeometryUtils.js';"""

if old_imports in content:
    content = content.replace(old_imports, new_imports)
    print("Added BufferGeometryUtils import")

# 3. Add Procedural Texture Generator & Mesh Smoothing functions
procedural_texture_code = """
// ---------------------------------------------------------------------------
// Procedural Anatomical Tissue Micro-Texture Generator
// ---------------------------------------------------------------------------
// Generates fine myocardial fiber striations and subtle pericardial moisture
// roughness without external texture assets or heavy memory footprint.
function generateTissueTextures() {
  const size = 512;
  const nCanvas = document.createElement('canvas');
  nCanvas.width = size;
  nCanvas.height = size;
  const nCtx = nCanvas.getContext('2d');
  const nImg = nCtx.createImageData(size, size);
  const nData = nImg.data;

  const rCanvas = document.createElement('canvas');
  rCanvas.width = size;
  rCanvas.height = size;
  const rCtx = rCanvas.getContext('2d');
  const rImg = rCtx.createImageData(size, size);
  const rData = rImg.data;

  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const idx = (y * size + x) * 4;
      
      // Multi-frequency directional fiber striation pattern
      const f1 = Math.sin((x * 1.4 + y * 0.9) * 0.14) * Math.cos((y * 1.4 - x * 0.7) * 0.16);
      const f2 = Math.sin((x + y * 0.6) * 0.38) * 0.45;
      const f3 = (Math.sin(x * 2.2) * Math.cos(y * 2.2)) * 0.20;
      const grain = (Math.sin(x * 12.3 + y * 17.1) + Math.cos(x * 21.7 - y * 9.5)) * 0.12;
      const h = f1 * 0.45 + f2 * 0.30 + f3 * 0.15 + grain;

      // Normal slope computation (subtle micro-relief centered around RGB 128, 128, 246)
      const dx = (Math.cos((x * 1.4 + y * 0.9) * 0.14) * 0.14 + grain * 0.08) * 28;
      const dy = (Math.sin((y * 1.4 - x * 0.7) * 0.16) * 0.16 + grain * 0.08) * 28;
      
      const nx = Math.max(0, Math.min(255, Math.round(128 + dx)));
      const ny = Math.max(0, Math.min(255, Math.round(128 + dy)));
      const nz = 246; // Dominant positive Z normal for gentle micro-relief

      nData[idx] = nx;
      nData[idx + 1] = ny;
      nData[idx + 2] = nz;
      nData[idx + 3] = 255;

      // Roughness map: organic living tissue variance (values ~105 to 140 -> 0.41 to 0.55)
      const rVal = Math.max(0, Math.min(255, Math.round(115 + (h * 26))));
      rData[idx] = rVal;
      rData[idx + 1] = rVal;
      rData[idx + 2] = rVal;
      rData[idx + 3] = 255;
    }
  }

  nCtx.putImageData(nImg, 0, 0);
  rCtx.putImageData(rImg, 0, 0);

  const normalTex = new THREE.CanvasTexture(nCanvas);
  normalTex.wrapS = THREE.RepeatWrapping;
  normalTex.wrapT = THREE.RepeatWrapping;
  normalTex.repeat.set(6, 6);

  const roughnessTex = new THREE.CanvasTexture(rCanvas);
  roughnessTex.wrapS = THREE.RepeatWrapping;
  roughnessTex.wrapT = THREE.RepeatWrapping;
  roughnessTex.repeat.set(6, 6);

  return { normalTex, roughnessTex };
}

const { normalTex: tissueNormalMap, roughnessTex: tissueRoughnessMap } = generateTissueTextures();

// ---------------------------------------------------------------------------
// Mesh Normal Smoothing & Cylindrical UV Architecture
// ---------------------------------------------------------------------------
// Welds shared vertices on non-indexed OBJ meshes to eliminate polygon faceting
// without altering anatomical geometry, and computes smooth vertex normals.
function prepareSmoothGeometry(geom) {
  if (!geom || !geom.attributes.position) return geom;
  
  // 1. Ensure cylindrical/anatomical UV coordinates for procedural texture mapping
  if (!geom.attributes.uv) {
    geom.computeBoundingBox();
    const bbox = geom.boundingBox;
    const sizeZ = Math.max(bbox.max.z - bbox.min.z, 0.001);
    const midX = (bbox.min.x + bbox.max.x) * 0.5;
    const midY = (bbox.min.y + bbox.max.y) * 0.5;
    const pos = geom.attributes.position;
    const count = pos.count;
    const uvs = new Float32Array(count * 2);

    for (let i = 0; i < count; i++) {
      const x = pos.getX(i);
      const y = pos.getY(i);
      const z = pos.getZ(i);
      const angle = Math.atan2(y - midY, x - midX);
      uvs[i * 2] = (angle + Math.PI) / (2 * Math.PI);
      uvs[i * 2 + 1] = (z - bbox.min.z) / sizeZ;
    }
    geom.setAttribute('uv', new THREE.BufferAttribute(uvs, 2));
  }

  // 2. Weld shared vertices and compute smooth vertex normals
  try {
    if (BufferGeometryUtils && typeof BufferGeometryUtils.mergeVertices === 'function') {
      const merged = BufferGeometryUtils.mergeVertices(geom, 1e-4);
      merged.computeVertexNormals();
      return merged;
    }
  } catch (err) {
    console.warn('Mesh normal smoothing fallback:', err);
  }
  
  if (!geom.attributes.normal) {
    geom.computeVertexNormals();
  }
  return geom;
}
"""

# Insert procedural_texture_code right before Dynamic Coronary Risk Coloring Architecture
old_marker = "// ---------------------------------------------------------------------------\n// Dynamic Coronary Risk Coloring Architecture"
if old_marker in content and "prepareSmoothGeometry" not in content:
    content = content.replace(old_marker, procedural_texture_code + "\n" + old_marker)
    print("Added procedural texture generator and smooth geometry function")

# 4. Replace palettes and applyCoronaryMode with full dual-mode architecture
old_modes_and_palettes = """// ---------------------------------------------------------------------------
// Dynamic Coronary Risk Coloring Architecture (Track A Clinical Specification)
// ---------------------------------------------------------------------------
let currentVisualizationMode = 'anatomy'; // 'anatomy' (default) | 'risk'

// Continuous Visual Color Gradient:
// Green (0% - #10b981) -> Amber (50% - #f59e0b) -> Red (100% - #ef4444)
function getRiskGradientColor(probability) {
  let p = Number(probability || 0);
  if (p <= 1.0 && p > 0.0) p *= 100.0;
  p = Math.max(0, Math.min(100, p));

  const t = p / 100.0;
  let r, g, b;
  if (t <= 0.5) {
    const u = t / 0.5;
    r = Math.round(16 + u * (245 - 16));
    g = Math.round(185 + u * (158 - 185));
    b = Math.round(129 + u * (11 - 129));
  } else {
    const u = (t - 0.5) / 0.5;
    r = Math.round(245 + u * (239 - 245));
    g = Math.round(158 + u * (68 - 158));
    b = Math.round(11 + u * (68 - 11));
  }

  const hexR = r.toString(16).padStart(2, '0');
  const hexG = g.toString(16).padStart(2, '0');
  const hexB = b.toString(16).padStart(2, '0');
  return `#${hexR}${hexG}${hexB}`;
}

function updateRiskLegendDisplay() {
  const ladVal = Number(cardioData.LAD.risk || 0);
  const lcxVal = Number(cardioData.LCX.risk || 0);
  const rcaVal = Number(cardioData.RCA.risk || 0);

  const ladColor = getRiskGradientColor(ladVal);
  const lcxColor = getRiskGradientColor(lcxVal);
  const rcaColor = getRiskGradientColor(rcaVal);

  const dotLad = document.querySelector('#legendDotLAD');
  const valLad = document.querySelector('#legendValLAD');
  if (dotLad) dotLad.style.background = ladColor;
  if (valLad) valLad.textContent = isPredicted ? `${ladVal.toFixed(1)}%` : '--';

  const dotLcx = document.querySelector('#legendDotLCX');
  const valLcx = document.querySelector('#legendValLCX');
  if (dotLcx) dotLcx.style.background = lcxColor;
  if (valLcx) valLcx.textContent = isPredicted ? `${lcxVal.toFixed(1)}%` : '--';

  const dotRca = document.querySelector('#legendDotRCA');
  const valRca = document.querySelector('#legendValRCA');
  if (dotRca) dotRca.style.background = rcaColor;
  if (valRca) valRca.textContent = isPredicted ? `${rcaVal.toFixed(1)}%` : '--';
}

function applyCoronaryMode(mode) {
  currentVisualizationMode = (mode === 'risk') ? 'risk' : 'anatomy';

  const modeAnatomyBtn = document.querySelector('#modeAnatomy');
  const modeRiskBtn = document.querySelector('#modeRisk');
  const riskLegendEl = document.querySelector('#riskLegend');

  if (currentVisualizationMode === 'anatomy') {
    if (modeAnatomyBtn) modeAnatomyBtn.classList.add('active');
    if (modeRiskBtn) modeRiskBtn.classList.remove('active');
    if (riskLegendEl) riskLegendEl.style.display = 'none';

    // Restore original anatomical colors
    if (materials['lad']) materials['lad'].color.set(colorMap['lad']);
    if (materials['lad_branches']) materials['lad_branches'].color.set(colorMap['lad_branches']);
    if (materials['lcx']) materials['lcx'].color.set(colorMap['lcx']);
    if (materials['lcx_branches']) materials['lcx_branches'].color.set(colorMap['lcx_branches']);
    if (materials['rca']) materials['rca'].color.set(colorMap['rca']);
    if (materials['rca_branches']) materials['rca_branches'].color.set(colorMap['rca_branches']);
  } else {
    if (modeRiskBtn) modeRiskBtn.classList.add('active');
    if (modeAnatomyBtn) modeAnatomyBtn.classList.remove('active');
    if (riskLegendEl) riskLegendEl.style.display = 'block';

    // Apply continuous probability risk colors strictly to LAD, LCX, RCA
    const ladColor = getRiskGradientColor(cardioData.LAD.risk);
    const lcxColor = getRiskGradientColor(cardioData.LCX.risk);
    const rcaColor = getRiskGradientColor(cardioData.RCA.risk);

    if (materials['lad']) materials['lad'].color.set(ladColor);
    if (materials['lad_branches']) materials['lad_branches'].color.set(ladColor);
    if (materials['lcx']) materials['lcx'].color.set(lcxColor);
    if (materials['lcx_branches']) materials['lcx_branches'].color.set(lcxColor);
    if (materials['rca']) materials['rca'].color.set(rcaColor);
    if (materials['rca_branches']) materials['rca_branches'].color.set(rcaColor);
  }

  updateRiskLegendDisplay();

  // If meshes are currently highlighted in purple, update their _originalSharedMaterial
  // so when deselected, they restore the active mode's color!
  for (const m of selectedClonedMeshes) {
    if (m && m._originalSharedMaterial && m.userData && m.userData.group) {
      const g = m.userData.group;
      if (materials[g]) {
        m._originalSharedMaterial.color.copy(materials[g].color);
      }
    }
  }

  if (!currentlySelectedMesh) {
    updateArteryHighlighting();
  }
}

// Complete 106 Mesh Manifest
const entries = ENTRIES_PLACEHOLDER;

// Color Palette
const colorMap = {
  ventricles: '#b85b63',
  internal_myocardium: '#a84c55',
  atria: '#cf7d85',
  great_vessels: '#d4a39b',
  valves: '#eee5d8',
  cardiac_veins: '#2e7da9',
  conduction_system: '#f6c445',
  left_coronary_stem: '#e6d6c2',
  lad: '#2a86ef',
  lad_branches: '#4da1ff',
  lcx: '#0fb77d',
  lcx_branches: '#38d7a1',
  rca: '#ff9900',
  rca_branches: '#ffb74d'
};"""

new_modes_and_palettes = """// ---------------------------------------------------------------------------
// Dynamic Coronary Risk & Realistic Tissue Architecture
// ---------------------------------------------------------------------------
let currentVisualizationMode = 'anatomy'; // 'anatomy' (default) | 'risk'
let currentAppearanceStyle = 'clinical';  // 'clinical' (default) | 'realistic'

// Continuous Visual Color Gradient:
// Green (0% - #10b981) -> Amber (50% - #f59e0b) -> Red (100% - #ef4444)
function getRiskGradientColor(probability) {
  let p = Number(probability || 0);
  if (p <= 1.0 && p > 0.0) p *= 100.0;
  p = Math.max(0, Math.min(100, p));

  const t = p / 100.0;
  let r, g, b;
  if (t <= 0.5) {
    const u = t / 0.5;
    r = Math.round(16 + u * (245 - 16));
    g = Math.round(185 + u * (158 - 185));
    b = Math.round(129 + u * (11 - 129));
  } else {
    const u = (t - 0.5) / 0.5;
    r = Math.round(245 + u * (239 - 245));
    g = Math.round(158 + u * (68 - 158));
    b = Math.round(11 + u * (68 - 11));
  }

  const hexR = r.toString(16).padStart(2, '0');
  const hexG = g.toString(16).padStart(2, '0');
  const hexB = b.toString(16).padStart(2, '0');
  return `#${hexR}${hexG}${hexB}`;
}

// Complete 106 Mesh Manifest
const entries = ENTRIES_PLACEHOLDER;

// Dual Palettes: Clinical Identifiable vs Realistic Anatomical Shading
const paletteClinical = {
  ventricles: '#a3424c',         // Refined deep healthy myocardium
  internal_myocardium: '#8e2a33',// Trabecular / papillary depth
  atria: '#ba5862',              // Thin atrial wall myocardium
  great_vessels: '#caa095',      // Aorta & pulmonary trunk fibro-elastic adventitia
  valves: '#eee5d8',             // Fibrous annular rings & cusps
  cardiac_veins: '#2a7da3',      // Identifiable venous blue
  conduction_system: '#f5c542',  // Conduction bundles
  left_coronary_stem: '#e6d6c2', // Neutral reference bone-white
  lad: '#2a86ef',                // Identifiable LAD royal blue
  lad_branches: '#4da1ff',       // LAD diagonals/septals
  lcx: '#0fb77d',                // Identifiable LCX emerald green
  lcx_branches: '#38d7a1',       // LCX marginals
  rca: '#ff9900',                // Identifiable RCA amber orange
  rca_branches: '#ffb74d'        // RCA acute marginals
};

const paletteRealistic = {
  ventricles: '#82242c',         // Natural human myocardial red/burgundy
  internal_myocardium: '#741f26',// Endocardial / papillary depth
  atria: '#96343d',              // Natural atrial tissue
  great_vessels: '#b8897c',      // Ascending aorta fibro-muscular wall
  valves: '#e5dcce',             // Cardiac valve connective tissue
  cardiac_veins: '#243b56',      // Deep deoxygenated coronary venous blue
  conduction_system: '#d69e2e',  // Subendocardial Purkinje / nodal tissue
  left_coronary_stem: '#e6d6c2', // Neutral reference stem (preserved!)
  lad: '#a32630',                // Oxygenated arterial crimson
  lad_branches: '#b2333d',       // Arterial branch crimson
  lcx: '#9e242e',                // Arterial circumflex crimson
  lcx_branches: '#ad303a',       // Circumflex branch crimson
  rca: '#9c252f',                // Arterial right coronary crimson
  rca_branches: '#ab2f39'        // Marginal arterial crimson
};

// colorMap reference for backwards compatibility
const colorMap = paletteClinical;

function updateRiskLegendDisplay() {
  const ladVal = Number(cardioData.LAD.risk || 0);
  const lcxVal = Number(cardioData.LCX.risk || 0);
  const rcaVal = Number(cardioData.RCA.risk || 0);

  const ladColor = getRiskGradientColor(ladVal);
  const lcxColor = getRiskGradientColor(lcxVal);
  const rcaColor = getRiskGradientColor(rcaVal);

  const dotLad = document.querySelector('#legendDotLAD');
  const valLad = document.querySelector('#legendValLAD');
  if (dotLad) dotLad.style.background = ladColor;
  if (valLad) valLad.textContent = isPredicted ? `${ladVal.toFixed(1)}%` : '--';

  const dotLcx = document.querySelector('#legendDotLCX');
  const valLcx = document.querySelector('#legendValLCX');
  if (dotLcx) dotLcx.style.background = lcxColor;
  if (valLcx) valLcx.textContent = isPredicted ? `${lcxVal.toFixed(1)}%` : '--';

  const dotRca = document.querySelector('#legendDotRCA');
  const valRca = document.querySelector('#legendValRCA');
  if (dotRca) dotRca.style.background = rcaColor;
  if (valRca) valRca.textContent = isPredicted ? `${rcaVal.toFixed(1)}%` : '--';
}

function updateCategoryDotColors(palette) {
  for (const [grp, col] of Object.entries(palette)) {
    const input = document.querySelector(`[data-group="${grp}"]`);
    if (input) {
      const parent = input.closest('label');
      if (parent) {
        const dot = parent.querySelector('.dot');
        if (dot) {
          if (currentVisualizationMode === 'risk' && (grp === 'lad' || grp === 'lad_branches' || grp === 'lcx' || grp === 'lcx_branches' || grp === 'rca' || grp === 'rca_branches')) {
            if (grp.startsWith('lad')) dot.style.background = getRiskGradientColor(cardioData.LAD.risk);
            else if (grp.startsWith('lcx')) dot.style.background = getRiskGradientColor(cardioData.LCX.risk);
            else if (grp.startsWith('rca')) dot.style.background = getRiskGradientColor(cardioData.RCA.risk);
          } else {
            dot.style.background = col;
          }
        }
      }
    }
  }
}

function applyVisualizationState() {
  const isRisk = (currentVisualizationMode === 'risk');
  const isRealistic = (currentAppearanceStyle === 'realistic');

  const modeAnatomyBtn = document.querySelector('#modeAnatomy');
  const modeRiskBtn = document.querySelector('#modeRisk');
  const styleClinicalBtn = document.querySelector('#styleClinical');
  const styleRealisticBtn = document.querySelector('#styleRealistic');
  const riskLegendEl = document.querySelector('#riskLegend');

  if (modeAnatomyBtn) modeAnatomyBtn.classList.toggle('active', !isRisk);
  if (modeRiskBtn) modeRiskBtn.classList.toggle('active', isRisk);
  if (styleClinicalBtn) styleClinicalBtn.classList.toggle('active', !isRealistic);
  if (styleRealisticBtn) styleRealisticBtn.classList.toggle('active', isRealistic);

  if (riskLegendEl) {
    riskLegendEl.style.display = isRisk ? 'block' : 'none';
  }

  const activePalette = isRealistic ? paletteRealistic : paletteClinical;

  // 1. Non-coronary tissues
  for (const grp of heartGroups) {
    if (materials[grp] && activePalette[grp]) {
      materials[grp].color.set(activePalette[grp]);
    }
  }

  // Left coronary stem always remains neutral reference bone-white
  if (materials['left_coronary_stem']) {
    materials['left_coronary_stem'].color.set(activePalette['left_coronary_stem'] || '#e6d6c2');
  }

  // 2. Coronary vessels (LAD, LCX, RCA and branches)
  if (isRisk) {
    // Risk Overlay Mode: ALWAYS color LAD, LCX, RCA according to model-predicted continuous gradient
    const ladColor = getRiskGradientColor(cardioData.LAD.risk);
    const lcxColor = getRiskGradientColor(cardioData.LCX.risk);
    const rcaColor = getRiskGradientColor(cardioData.RCA.risk);

    if (materials['lad']) materials['lad'].color.set(ladColor);
    if (materials['lad_branches']) materials['lad_branches'].color.set(ladColor);
    if (materials['lcx']) materials['lcx'].color.set(lcxColor);
    if (materials['lcx_branches']) materials['lcx_branches'].color.set(lcxColor);
    if (materials['rca']) materials['rca'].color.set(rcaColor);
    if (materials['rca_branches']) materials['rca_branches'].color.set(rcaColor);
  } else {
    // Anatomy Mode: Use active appearance palette (identifiable vs natural arterial crimson)
    if (materials['lad']) materials['lad'].color.set(activePalette['lad']);
    if (materials['lad_branches']) materials['lad_branches'].color.set(activePalette['lad_branches']);
    if (materials['lcx']) materials['lcx'].color.set(activePalette['lcx']);
    if (materials['lcx_branches']) materials['lcx_branches'].color.set(activePalette['lcx_branches']);
    if (materials['rca']) materials['rca'].color.set(activePalette['rca']);
    if (materials['rca_branches']) materials['rca_branches'].color.set(activePalette['rca_branches']);
  }

  // 3. Update myocardial textures and roughness
  for (const grp of ['ventricles', 'internal_myocardium', 'atria']) {
    if (materials[grp]) {
      materials[grp].normalMap = tissueNormalMap;
      materials[grp].roughnessMap = tissueRoughnessMap;
      materials[grp].normalScale.set(0.22, 0.22);
      materials[grp].roughness = isRealistic ? 0.44 : 0.48;
      materials[grp].metalness = isRealistic ? 0.05 : 0.08;
      materials[grp].needsUpdate = true;
    }
  }
  if (materials['great_vessels']) {
    materials['great_vessels'].normalMap = tissueNormalMap;
    materials['great_vessels'].normalScale.set(0.12, 0.12);
    materials['great_vessels'].roughness = isRealistic ? 0.40 : 0.46;
    materials['great_vessels'].needsUpdate = true;
  }
  for (const grp of arteryGroups) {
    if (materials[grp]) {
      materials[grp].roughness = 0.28;
      materials[grp].metalness = 0.12;
      materials[grp].needsUpdate = true;
    }
  }

  updateCategoryDotColors(activePalette);
  updateRiskLegendDisplay();

  // If meshes are currently highlighted in purple, update their _originalSharedMaterial
  for (const m of selectedClonedMeshes) {
    if (m && m._originalSharedMaterial && m.userData && m.userData.group) {
      const g = m.userData.group;
      if (materials[g]) {
        m._originalSharedMaterial.color.copy(materials[g].color);
      }
    }
  }

  if (!currentlySelectedMesh) {
    updateArteryHighlighting();
  }
}

function applyCoronaryMode(mode) {
  currentVisualizationMode = (mode === 'risk') ? 'risk' : 'anatomy';
  applyVisualizationState();
}

function setAppearanceStyle(style) {
  currentAppearanceStyle = (style === 'realistic') ? 'realistic' : 'clinical';
  applyVisualizationState();
}"""

if old_modes_and_palettes in content:
    content = content.replace(old_modes_and_palettes, new_modes_and_palettes)
    print("Replaced palettes and mode architecture")
else:
    print("Warning: old_modes_and_palettes not found directly!")

# 5. Replace Lighting setup and toneMapping
old_lighting = """renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.35;

const scene = new THREE.Scene();
scene.background = new THREE.Color('#071325');

// In BodyParts3D dataset, Z is the superior/inferior anatomical axis:
const camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.01, 1000);
camera.up.set(0, 0, 1);

// OrbitControls Configuration
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.enableZoom = true;
// Normalized zoomSpeed: 2.4 with DPR compensation gives a natural, responsive ~12% zoom per wheel notch
controls.zoomSpeed = 2.4 * Math.max(1, (window.devicePixelRatio | 0));
controls.enableRotate = true;
controls.enablePan = true;
controls.screenSpacePanning = true;
controls.minDistance = 2.6;
controls.maxDistance = 35.0;

// High-fidelity Anatomical Lighting matching clinical orientation
const hemiLight = new THREE.HemisphereLight(0xffffff, 0x182436, 1.85);
scene.add(hemiLight);

const keyLight = new THREE.DirectionalLight(0xffffff, 2.4);
keyLight.position.set(-3.5, -6.5, 6.0);
scene.add(keyLight);

const fillLight = new THREE.DirectionalLight(0xbdd4f5, 1.4);
fillLight.position.set(5.0, 4.5, 2.5);
scene.add(fillLight);

const backLight = new THREE.DirectionalLight(0x82a5d4, 1.2);
backLight.position.set(0.0, 6.0, -4.0);
scene.add(backLight);"""

new_lighting = """renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.08;

const scene = new THREE.Scene();
scene.background = new THREE.Color('#071325');

// In BodyParts3D dataset, Z is the superior/inferior anatomical axis:
const camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.01, 1000);
camera.up.set(0, 0, 1);

// OrbitControls Configuration
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.enableZoom = true;
controls.zoomSpeed = 2.4 * Math.max(1, (window.devicePixelRatio | 0));
controls.enableRotate = true;
controls.enablePan = true;
controls.screenSpacePanning = true;
controls.minDistance = 2.6;
controls.maxDistance = 35.0;

// Professional Medical Studio Lighting
// 1. Soft Ambient Illumination (clean clinical neutral dome, subtle deep cavity ground)
const hemiLight = new THREE.HemisphereLight(0xf4f7fa, 0x141f2e, 0.75);
scene.add(hemiLight);

// 2. Directional Key Light (surgical key illumination from anterior-superior-left)
const keyLight = new THREE.DirectionalLight(0xfff6eb, 1.85);
keyLight.position.set(-3.8, -6.2, 5.5);
scene.add(keyLight);

// 3. Directional Fill Light (cool diffuse fill from lateral right to lift deep shadow contrast)
const fillLight = new THREE.DirectionalLight(0xd8e6f8, 0.75);
fillLight.position.set(5.2, 3.8, 2.2);
scene.add(fillLight);

// 4. Directional Rim / Kicker Light (crisp anatomical contour definition from posterior-superior)
const rimLight = new THREE.DirectionalLight(0x99bdf2, 1.25);
rimLight.position.set(0.0, 6.2, -4.2);
scene.add(rimLight);

// 5. Subtle Inferior Bounce Light (soft diaphragmatic bounce)
const bounceLight = new THREE.DirectionalLight(0x2a384c, 0.40);
bounceLight.position.set(0.0, -2.0, -5.5);
scene.add(bounceLight);"""

if old_lighting in content:
    content = content.replace(old_lighting, new_lighting)
    print("Replaced lighting and tone mapping with professional medical studio lighting")
else:
    print("Warning: old_lighting not found directly!")

# 6. Materials loop update
old_mat_loop = """// Build Materials
const materials = {};
for (const [grp, col] of Object.entries(colorMap)) {
  const isHeart = heartGroups.has(grp);
  const isArtery = arteryGroups.has(grp);
  const isConduction = (grp === 'conduction_system');

  materials[grp] = new THREE.MeshStandardMaterial({
    color: new THREE.Color(col),
    roughness: isArtery ? 0.25 : isConduction ? 0.3 : 0.48,
    metalness: isArtery ? 0.15 : isConduction ? 0.2 : 0.08,
    transparent: true,
    opacity: 1.0,
    side: THREE.DoubleSide,
    depthWrite: true,
    emissive: new THREE.Color('#000000'),
    emissiveIntensity: 0.7
  });
}"""

new_mat_loop = """// Build High-Quality Anatomical Materials
const materials = {};
for (const [grp, col] of Object.entries(paletteClinical)) {
  const isHeart = heartGroups.has(grp);
  const isArtery = arteryGroups.has(grp);
  const isVein = (grp === 'cardiac_veins');
  const isConduction = (grp === 'conduction_system');
  const isMyocardium = (grp === 'ventricles' || grp === 'internal_myocardium' || grp === 'atria');

  materials[grp] = new THREE.MeshStandardMaterial({
    color: new THREE.Color(col),
    roughness: isArtery ? 0.28 : isVein ? 0.32 : isConduction ? 0.35 : isMyocardium ? 0.46 : 0.50,
    metalness: isArtery ? 0.12 : isVein ? 0.10 : isConduction ? 0.15 : 0.05,
    transparent: true,
    opacity: 1.0,
    side: THREE.DoubleSide,
    depthWrite: true,
    emissive: new THREE.Color('#000000'),
    emissiveIntensity: 0.5,
    normalMap: isMyocardium ? tissueNormalMap : (grp === 'great_vessels' ? tissueNormalMap : null),
    normalScale: isMyocardium ? new THREE.Vector2(0.22, 0.22) : new THREE.Vector2(0.12, 0.12),
    roughnessMap: isMyocardium ? tissueRoughnessMap : null
  });
}"""

if old_mat_loop in content:
    content = content.replace(old_mat_loop, new_mat_loop)
    print("Replaced materials loop with micro-texture and adventitia sheen")
else:
    print("Warning: old_mat_loop not found directly!")

# 7. Update loadMeshWithRetry to use prepareSmoothGeometry
old_load_mesh = """      obj.traverse((child) => {
        if (child.isMesh) {
          child.material = materials[entry.group];
          child.userData = { ...entry };
          
          if (child.geometry && !child.geometry.attributes.normal) {
            child.geometry.computeVertexNormals();
          }
          child.renderOrder = isArtery ? 15 : isVein ? 10 : isConduction ? 12 : 1;
        }
      });"""

new_load_mesh = """      obj.traverse((child) => {
        if (child.isMesh) {
          if (child.geometry) {
            child.geometry = prepareSmoothGeometry(child.geometry);
          }
          child.material = materials[entry.group];
          child.userData = { ...entry };
          child.renderOrder = isArtery ? 15 : isVein ? 10 : isConduction ? 12 : 1;
        }
      });"""

if old_load_mesh in content:
    content = content.replace(old_load_mesh, new_load_mesh)
    print("Updated loadMeshWithRetry with prepareSmoothGeometry")
else:
    print("Warning: old_load_mesh not found directly!")

# 8. Update selectMesh color resolution:
old_select_col = """  const grp = obj.userData.group;
  const isCoronaryVessel = (grp === 'lad' || grp === 'lad_branches' || grp === 'lcx' || grp === 'lcx_branches' || grp === 'rca' || grp === 'rca_branches');
  const activeColor = (currentVisualizationMode === 'risk' && isCoronaryVessel && materials[grp])
    ? '#' + materials[grp].color.getHexString()
    : (colorMap[grp] || '#fff');
  const col = activeColor;"""

new_select_col = """  const grp = obj.userData.group;
  const isCoronaryVessel = (grp === 'lad' || grp === 'lad_branches' || grp === 'lcx' || grp === 'lcx_branches' || grp === 'rca' || grp === 'rca_branches');
  const activePalette = (currentAppearanceStyle === 'realistic') ? paletteRealistic : paletteClinical;
  const activeColor = (currentVisualizationMode === 'risk' && isCoronaryVessel && materials[grp])
    ? '#' + materials[grp].color.getHexString()
    : (activePalette[grp] || (materials[grp] ? '#' + materials[grp].color.getHexString() : '#fff'));
  const col = activeColor;"""

if old_select_col in content:
    content = content.replace(old_select_col, new_select_col)
    print("Updated selectMesh color resolution")
else:
    print("Warning: old_select_col not found directly!")

# 9. Update window.CardioVision3D and postMessage
old_api_marker = """  setVisualizationMode: applyCoronaryMode,
  getVisualizationMode: () => currentVisualizationMode,"""

new_api_marker = """  setVisualizationMode: applyCoronaryMode,
  getVisualizationMode: () => currentVisualizationMode,
  setAppearanceStyle: setAppearanceStyle,
  getAppearanceStyle: () => currentAppearanceStyle,"""

if old_api_marker in content:
    content = content.replace(old_api_marker, new_api_marker)
    print("Added appearance style methods to CardioVision3D")

old_postmsg_marker = """  } else if (ev.data.type === 'SET_VISUALIZATION_MODE') {
    if (ev.data.mode) applyCoronaryMode(ev.data.mode);"""

new_postmsg_marker = """  } else if (ev.data.type === 'SET_VISUALIZATION_MODE') {
    if (ev.data.mode) applyCoronaryMode(ev.data.mode);
  } else if (ev.data.type === 'SET_APPEARANCE_STYLE') {
    if (ev.data.style) setAppearanceStyle(ev.data.style);"""

if old_postmsg_marker in content:
    content = content.replace(old_postmsg_marker, new_postmsg_marker)
    print("Added SET_APPEARANCE_STYLE handler to postMessage")

# Add button listeners for #styleClinical and #styleRealistic
old_btn_listeners = """const btnModeRisk = document.querySelector('#modeRisk');
if (btnModeRisk) {
  btnModeRisk.addEventListener('click', () => applyCoronaryMode('risk'));
}"""

new_btn_listeners = """const btnModeRisk = document.querySelector('#modeRisk');
if (btnModeRisk) {
  btnModeRisk.addEventListener('click', () => applyCoronaryMode('risk'));
}

const btnStyleClinical = document.querySelector('#styleClinical');
if (btnStyleClinical) {
  btnStyleClinical.addEventListener('click', () => setAppearanceStyle('clinical'));
}
const btnStyleRealistic = document.querySelector('#styleRealistic');
if (btnStyleRealistic) {
  btnStyleRealistic.addEventListener('click', () => setAppearanceStyle('realistic'));
}"""

if old_btn_listeners in content:
    content = content.replace(old_btn_listeners, new_btn_listeners)
    print("Added button listeners for styleClinical and styleRealistic")

with open(GEN_FILE, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Successfully updated {GEN_FILE}")
