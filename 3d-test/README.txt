CardioVision AI — BodyParts3D Three.js Anatomical Mesh Preview

WHAT IS INCLUDED
- 39 curated OBJ meshes extracted from your uploaded BodyParts3D archive.
- viewer.html: an independent interactive Three.js inspector.
- mesh_manifest.csv: original filenames and anatomical group mappings.

RUN (WINDOWS)
1. Extract this ZIP to a folder (for example CardioVision_3D_Preview).
2. Open Command Prompt in the folder containing viewer.html.
3. Run: python -m http.server 8000
4. Open: http://localhost:8000/viewer.html
5. An internet connection is required to load Three.js from jsDelivr.

IMPORTANT
- These are separate anatomical surfaces, NOT a complete external heart mesh.
- The core vessel trunk segments are continuous at their endpoints based on a numerical nearest-vertex check.
- Colors distinguish LAD, LCX and RCA; they DO NOT indicate disease or anatomical narrowing.
- No predictions are included in this preview. Integration with the actual ML backend is a separate step.
- Meshes are kept in their original coordinate system. The viewer applies one common centering/scaling transform.
- The Z axis is set as up for the BodyParts3D anatomical coordinate system.
- Do not combine this preview with another heart mesh unless you verify its anatomical alignment.
- Research visualization only, not medical imaging or a diagnostic device.

ANATOMICAL RESOURCE
BodyParts3D / Anatomography: https://lifesciencedb.jp/bp3d/
Check and comply with the license and attribution requirements for the source dataset before publishing or redistributing.
