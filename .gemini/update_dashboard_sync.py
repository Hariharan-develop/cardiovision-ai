with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Title in view-viewer3d
old_title = """        <div>
          <h2>Interactive 3D Anatomical Heart &amp; Coronary Stenosis Viewer</h2>
          <p>WebGL Three.js spatial visualization with real-time model-derived coronary artery color mapping.</p>
        </div>"""

new_title = """        <div>
          <h2>Interactive 3D Coronary Anatomy</h2>
          <p>WebGL Three.js 106-mesh anatomical assembly with live multi-vessel prediction telemetry and vascular isolation.</p>
        </div>"""

if old_title in text:
    text = text.replace(old_title, new_title, 1)
    print("Updated title!")
else:
    print("Title already updated or not found.")

# 2. Update switchNav and add sync3DViewerState
old_nav = """  syncPatientDetails();
  if (viewId === 'patient') {
    renderPatientInfoScreen();
  }
}"""

new_nav = """  syncPatientDetails();
  if (viewId === 'patient') {
    renderPatientInfoScreen();
  }
  if (viewId === 'viewer3d') {
    sync3DViewerState();
  }
}

function sync3DViewerState() {
  try {
    const viewer = document.getElementById('viewerIframe') || document.getElementById('heartViewerFrame');
    if (!viewer || !viewer.contentWindow) return;
    const st = sessionStorage.getItem('cardiovision_state');
    if (st === 'awaiting') {
      if (viewer.contentWindow.CardioVision3D && viewer.contentWindow.CardioVision3D.reset) {
        viewer.contentWindow.CardioVision3D.reset();
      }
      viewer.contentWindow.postMessage({ type: 'RESET_CARDIO_DATA' }, '*');
    } else {
      const lastPred = sessionStorage.getItem('cardiovision_last_prediction');
      if (lastPred) {
        const d = JSON.parse(lastPred);
        const updatePayload = {
          CAD: { risk: Number(d.cad_risk || 0), label: String(d.cad_label || 'CAD') },
          LAD: { risk: Number(d.lad_risk || 0), label: String(d.lad_label || 'Stenotic') },
          LCX: { risk: Number(d.lcx_risk || 0), label: String(d.lcx_label || 'Stenotic') },
          RCA: { risk: Number(d.rca_risk || 0), label: String(d.rca_label || 'Stenotic') }
        };
        if (viewer.contentWindow.CardioVision3D && viewer.contentWindow.CardioVision3D.updateProbabilities) {
          viewer.contentWindow.CardioVision3D.updateProbabilities(updatePayload);
        }
        viewer.contentWindow.postMessage({ type: 'UPDATE_CARDIO_DATA', data: updatePayload }, '*');
      }
    }
  } catch(e) {}
}"""

if old_nav in text:
    text = text.replace(old_nav, new_nav, 1)
    print("Updated switchNav!")
else:
    print("switchNav already updated or not found.")

# 3. Update clearPredictionResults 3D section to call CardioVision3D.reset()
idx = text.find('// 6. Clear 3D prediction highlights')
if idx != -1:
    end_idx = text.find('} catch(e) {}', idx) + len('} catch(e) {}')
    old_clear_block = text[idx:end_idx]
    new_clear_block = """// 6. Clear 3D prediction highlights
  try {
    const viewer = document.getElementById('viewerIframe') || document.getElementById('heartViewerFrame');
    if (viewer && viewer.contentWindow) {
      if (viewer.contentWindow.CardioVision3D && viewer.contentWindow.CardioVision3D.reset) {
        viewer.contentWindow.CardioVision3D.reset();
      } else if (viewer.contentWindow.CardioVision3D && viewer.contentWindow.CardioVision3D.updateProbabilities) {
        viewer.contentWindow.CardioVision3D.updateProbabilities({
          CAD: { risk: 0, label: 'Awaiting' },
          LAD: { risk: 0, label: 'Awaiting' },
          LCX: { risk: 0, label: 'Awaiting' },
          RCA: { risk: 0, label: 'Awaiting' }
        });
      }
      viewer.contentWindow.postMessage({
        type: 'RESET_CARDIO_DATA'
      }, '*');
    }
  } catch(e) {}"""
    text = text[:idx] + new_clear_block + text[end_idx:]
    print("Updated clearPredictionResults!")

# 4. Attach iframe load listener in DOMContentLoaded
old_load = "  syncPatientDetails();"
new_load = """  syncPatientDetails();
  const vFrame = document.getElementById('viewerIframe');
  if (vFrame) {
    vFrame.addEventListener('load', function() {
      setTimeout(sync3DViewerState, 50);
    });
  }"""

if old_load in text:
    text = text.replace(old_load, new_load, 1)
    print("Updated DOMContentLoaded!")

with open('cardiovision_exact_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("cardiovision_exact_dashboard.html written successfully!")
