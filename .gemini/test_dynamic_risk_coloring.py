import asyncio, json, urllib.request, websockets, base64, os, sys

ARTIFACT_DIR = r"C:\Users\hario\.gemini\antigravity-ide\brain\8cd09337-1c91-438d-aacf-249a561d03c7"

async def main():
    pages = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json/list").read().decode())
    st_pages = [p for p in pages if "8501" in p.get("url", "")]
    if not st_pages:
        st_pages = [p for p in pages if "CardioVision" in p.get("title", "")]
    target = st_pages[0]
    ws_url = target["webSocketDebuggerUrl"]
    print(f"Connecting to target [{target.get('id')}]: {target.get('title')}", flush=True)

    msg_counter = 0

    async with websockets.connect(ws_url, max_size=30_000_000) as ws:
        async def cdp_call(method, params=None):
            nonlocal msg_counter
            msg_counter += 1
            cid = msg_counter
            payload = {"id": cid, "method": method, "params": params or {}}
            await ws.send(json.dumps(payload))
            while True:
                raw = await ws.recv()
                msg = json.loads(raw)
                if msg.get("id") == cid:
                    return msg.get("result", {})

        async def capture(filename):
            await asyncio.sleep(0.3)
            await cdp_call("Emulation.setFocusEmulationEnabled", {"enabled": False})
            shot = await cdp_call("Page.captureScreenshot", {"format": "png"})
            await cdp_call("Emulation.setFocusEmulationEnabled", {"enabled": True})
            data = shot.get("data")
            if not data:
                print(f"ERROR: No data in screenshot response: {shot}", flush=True)
                return None
            out_file = os.path.join(ARTIFACT_DIR, filename)
            with open(out_file, "wb") as f:
                f.write(base64.b64decode(data))
            print(f"Screenshot successfully written: {out_file} ({len(data)} b64 bytes)", flush=True)
            return out_file

        await cdp_call("Page.bringToFront")
        await cdp_call("Emulation.setFocusEmulationEnabled", {"enabled": True})
        print("Page brought to front and focus emulation enabled.", flush=True)

        # Reload to load updated components/heart_viewer.html
        print("Reloading Streamlit page...", flush=True)
        await cdp_call("Page.reload")
        await asyncio.sleep(4)

        # Navigate to 3D Visualization tab
        print("Navigating to 3D Visualization tab...", flush=True)
        await cdp_call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const doc = stFrame ? stFrame.contentDocument : document;
                    const navItem = Array.from(doc.querySelectorAll('.navItem')).find(el => el.textContent && el.textContent.includes('3D Visualization'));
                    if (navItem) {
                        navItem.click();
                        return true;
                    }
                    return false;
                })()
            """,
            "returnByValue": True
        })
        await asyncio.sleep(2)

        # Wait for heart assembly to load inside viewerIframe
        print("Waiting for 106 meshes to load in 3D viewer...", flush=True)
        for i in range(35):
            eval_res = await cdp_call("Runtime.evaluate", {
                "expression": """
                    (() => {
                        const stFrame = document.querySelector('.stIFrame');
                        if (!stFrame) return { ok: false, reason: 'no stFrame' };
                        const vIframe = stFrame.contentDocument.getElementById('viewerIframe');
                        if (!vIframe) return { ok: false, reason: 'no viewerIframe' };
                        const vWin = vIframe.contentWindow;
                        const statusEl = vIframe.contentDocument.querySelector('#loadStatus');
                        const txt = statusEl ? statusEl.textContent : '';
                        const loadedCount = vWin.root ? vWin.root.children.length : 0;
                        const ready = txt.includes('Complete heart loaded') || loadedCount >= 106;
                        return { ok: true, ready, txt, loadedCount };
                    })()
                """,
                "returnByValue": True
            })
            val = eval_res.get("result", {}).get("value", {})
            safe_txt = str(val.get("txt", "")).encode("ascii", "replace").decode("ascii")
            print(f"[{i}] Loaded: {val.get('loadedCount')} - Status: {safe_txt}", flush=True)
            if val.get("ready"):
                print(">>> All 106 meshes fully loaded! <<<", flush=True)
                break
            await asyncio.sleep(1)

        await asyncio.sleep(1.0)

        # ---------------------------------------------------------------------
        # TEST 1: Initial Default Anatomy Mode State
        # ---------------------------------------------------------------------
        print("\n================== TEST 1: INITIAL ANATOMY MODE STATE ==================", flush=True)
        t1_eval = await cdp_call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    const vDoc = stFrame.contentDocument.getElementById('viewerIframe').contentDocument;

                    const modeAnatomy = vDoc.querySelector('#modeAnatomy');
                    const modeRisk = vDoc.querySelector('#modeRisk');
                    const legend = vDoc.querySelector('#riskLegend');

                    const ladColor = '#' + vWin.materials['lad'].color.getHexString();
                    const lcxColor = '#' + vWin.materials['lcx'].color.getHexString();
                    const rcaColor = '#' + vWin.materials['rca'].color.getHexString();
                    const veinColor = '#' + vWin.materials['cardiac_veins'].color.getHexString();
                    const stemColor = '#' + vWin.materials['left_coronary_stem'].color.getHexString();

                    return {
                        currentMode: vWin.CardioVision3D.getVisualizationMode(),
                        isAnatomyActive: modeAnatomy ? modeAnatomy.classList.contains('active') : false,
                        isRiskActive: modeRisk ? modeRisk.classList.contains('active') : false,
                        legendDisplay: legend ? legend.style.display : null,
                        ladColor,
                        lcxColor,
                        rcaColor,
                        veinColor,
                        stemColor
                    };
                })()
            """,
            "returnByValue": True
        })
        t1 = t1_eval.get("result", {}).get("value", {})
        print(json.dumps(t1, indent=2), flush=True)
        await capture("dynamic_coloring_01_initial_anatomy.png")

        # ---------------------------------------------------------------------
        # TEST 2: Illustrative Probabilities (LAD: 0.12, LCX: 0.54, RCA: 0.83)
        # ---------------------------------------------------------------------
        print("\n================== TEST 2: ILLUSTRATIVE PROBABILITIES (0.12, 0.54, 0.83) ==================", flush=True)
        t2_eval = await cdp_call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    const vDoc = stFrame.contentDocument.getElementById('viewerIframe').contentDocument;

                    // 1. Pass illustrative test probabilities (0.12, 0.54, 0.83)
                    vWin.CardioVision3D.updateProbabilities({
                        CAD: { risk: 75.0, label: 'CAD' },
                        LAD: { risk: 12.0, label: 'Normal' },
                        LCX: { risk: 54.0, label: 'Stenotic' },
                        RCA: { risk: 83.0, label: 'Stenotic' }
                    });

                    // 2. Switch to Risk Overlay Mode
                    const modeRiskBtn = vDoc.querySelector('#modeRisk');
                    if (modeRiskBtn) modeRiskBtn.click();

                    const mode = vWin.CardioVision3D.getVisualizationMode();
                    const legend = vDoc.querySelector('#riskLegend');

                    const ladColor = '#' + vWin.materials['lad'].color.getHexString();
                    const ladBranchColor = '#' + vWin.materials['lad_branches'].color.getHexString();
                    const lcxColor = '#' + vWin.materials['lcx'].color.getHexString();
                    const lcxBranchColor = '#' + vWin.materials['lcx_branches'].color.getHexString();
                    const rcaColor = '#' + vWin.materials['rca'].color.getHexString();
                    const rcaBranchColor = '#' + vWin.materials['rca_branches'].color.getHexString();

                    // Check uncolored non-targets
                    const veinColor = '#' + vWin.materials['cardiac_veins'].color.getHexString();
                    const stemColor = '#' + vWin.materials['left_coronary_stem'].color.getHexString();
                    const ventColor = '#' + vWin.materials['ventricles'].color.getHexString();

                    const valLad = vDoc.querySelector('#legendValLAD')?.textContent;
                    const valLcx = vDoc.querySelector('#legendValLCX')?.textContent;
                    const valRca = vDoc.querySelector('#legendValRCA')?.textContent;

                    return {
                        mode,
                        legendVisible: legend ? legend.style.display !== 'none' : false,
                        legendValues: { lad: valLad, lcx: valLcx, rca: valRca },
                        ladColor,
                        ladBranchColor,
                        lcxColor,
                        lcxBranchColor,
                        rcaColor,
                        rcaBranchColor,
                        veinColorUnchanged: veinColor === '#2e7da9',
                        stemColorUnchanged: stemColor === '#e6d6c2',
                        ventColorUnchanged: ventColor === '#b85b63'
                    };
                })()
            """,
            "returnByValue": True
        })
        t2 = t2_eval.get("result", {}).get("value", {})
        print(json.dumps(t2, indent=2), flush=True)
        await capture("dynamic_coloring_02_illustrative_risk_overlay.png")

        # ---------------------------------------------------------------------
        # TEST 3: Purple Selection & Deselection Restoration in Risk Mode
        # ---------------------------------------------------------------------
        print("\n================== TEST 3: PURPLE SELECTION & DESELECTION RESTORATION ==================", flush=True)
        t3_eval = await cdp_call("Runtime.evaluate", {
            "expression": """
                (async () => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    const vDoc = stFrame.contentDocument.getElementById('viewerIframe').contentDocument;

                    const expectedLadRiskColor = '#' + vWin.materials['lad'].color.getHexString();

                    // Step A: Select LAD while in Risk Overlay Mode
                    vWin.focusVesselGroup('lad');
                    await new Promise(r => setTimeout(r, 200));

                    let ladMesh = null;
                    vWin.root.children.forEach(obj => {
                        if (obj.userData && obj.userData.group === 'lad' && !ladMesh) {
                            obj.traverse(c => { if (c.isMesh && !ladMesh) ladMesh = c; });
                        }
                    });

                    const ladSelectedColor = ladMesh ? '#' + ladMesh.material.color.getHexString() : null;
                    const ladSelectedEmissive = ladMesh ? '#' + ladMesh.material.emissive.getHexString() : null;
                    const detailHtml = vDoc.querySelector('#detail')?.innerHTML || '';
                    const shows12Pct = detailHtml.includes('12.0%');

                    // Step B: Deselect LAD
                    vWin.CardioVision3D.clearSelectionHighlights();
                    await new Promise(r => setTimeout(r, 200));

                    // Confirm ladMesh material is restored to Risk Overlay color, NOT old anatomical blue!
                    const ladRestoredColor = ladMesh ? '#' + ladMesh.material.color.getHexString() : null;
                    const correctRiskRestored = (ladRestoredColor === expectedLadRiskColor);

                    // Step C: Test LCX selection and restoration
                    const expectedLcxRiskColor = '#' + vWin.materials['lcx'].color.getHexString();
                    vWin.focusVesselGroup('lcx');
                    await new Promise(r => setTimeout(r, 200));
                    let lcxMesh = null;
                    vWin.root.children.forEach(obj => {
                        if (obj.userData && obj.userData.group === 'lcx' && !lcxMesh) {
                            obj.traverse(c => { if (c.isMesh && !lcxMesh) lcxMesh = c; });
                        }
                    });
                    const lcxSelectedColor = lcxMesh ? '#' + lcxMesh.material.color.getHexString() : null;
                    vWin.CardioVision3D.clearSelectionHighlights();
                    await new Promise(r => setTimeout(r, 200));
                    const lcxRestoredColor = lcxMesh ? '#' + lcxMesh.material.color.getHexString() : null;

                    // Step D: Test RCA selection and restoration
                    const expectedRcaRiskColor = '#' + vWin.materials['rca'].color.getHexString();
                    vWin.focusVesselGroup('rca');
                    await new Promise(r => setTimeout(r, 200));
                    let rcaMesh = null;
                    vWin.root.children.forEach(obj => {
                        if (obj.userData && obj.userData.group === 'rca' && !rcaMesh) {
                            obj.traverse(c => { if (c.isMesh && !rcaMesh) rcaMesh = c; });
                        }
                    });
                    const rcaSelectedColor = rcaMesh ? '#' + rcaMesh.material.color.getHexString() : null;
                    vWin.CardioVision3D.clearSelectionHighlights();
                    await new Promise(r => setTimeout(r, 200));
                    const rcaRestoredColor = rcaMesh ? '#' + rcaMesh.material.color.getHexString() : null;

                    return {
                        ladSelectedInPurple: ladSelectedColor === '#b026ff',
                        ladSelectedEmissivePurple: ladSelectedEmissive === '#b026ff',
                        showsNumericalProbability: shows12Pct,
                        ladRestoredToRiskColor: correctRiskRestored,
                        ladRestoredColor,
                        expectedLadRiskColor,
                        lcxSelectedInPurple: lcxSelectedColor === '#b026ff',
                        lcxRestoredToRiskColor: lcxRestoredColor === expectedLcxRiskColor,
                        rcaSelectedInPurple: rcaSelectedColor === '#b026ff',
                        rcaRestoredToRiskColor: rcaRestoredColor === expectedRcaRiskColor
                    };
                })()
            """,
            "awaitPromise": True,
            "returnByValue": True
        })
        t3 = t3_eval.get("result", {}).get("value", {})
        print(json.dumps(t3, indent=2), flush=True)

        # Select LAD to capture purple selection screenshot
        await cdp_call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    vWin.focusVesselGroup('lad');
                })()
            """,
            "returnByValue": True
        })
        await capture("dynamic_coloring_03_purple_selected_lad.png")

        # Clear selection
        await cdp_call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    vWin.CardioVision3D.clearSelectionHighlights();
                })()
            """,
            "returnByValue": True
        })

        # ---------------------------------------------------------------------
        # TEST 4: Toggle Back to Anatomy Mode
        # ---------------------------------------------------------------------
        print("\n================== TEST 4: RESTORE ANATOMY MODE ==================", flush=True)
        t4_eval = await cdp_call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    const vDoc = stFrame.contentDocument.getElementById('viewerIframe').contentDocument;

                    const modeAnatomyBtn = vDoc.querySelector('#modeAnatomy');
                    if (modeAnatomyBtn) modeAnatomyBtn.click();

                    const mode = vWin.CardioVision3D.getVisualizationMode();
                    const legend = vDoc.querySelector('#riskLegend');

                    const ladColor = '#' + vWin.materials['lad'].color.getHexString();
                    const lcxColor = '#' + vWin.materials['lcx'].color.getHexString();
                    const rcaColor = '#' + vWin.materials['rca'].color.getHexString();

                    return {
                        mode,
                        legendHidden: legend ? legend.style.display === 'none' : true,
                        ladRestoredToAnatomicalBlue: ladColor === '#2a86ef',
                        lcxRestoredToAnatomicalGreen: lcxColor === '#0fb77d',
                        rcaRestoredToAnatomicalOrange: rcaColor === '#ff9900'
                    };
                })()
            """,
            "returnByValue": True
        })
        t4 = t4_eval.get("result", {}).get("value", {})
        print(json.dumps(t4, indent=2), flush=True)
        await capture("dynamic_coloring_04_restored_anatomy.png")

        # ---------------------------------------------------------------------
        # TEST 5: Real ML Model Predictions Integration (Triggered Live)
        # ---------------------------------------------------------------------
        print("\n================== TEST 5: REAL ML MODEL PREDICTIONS INTEGRATION ==================", flush=True)
        t5_eval = await cdp_call("Runtime.evaluate", {
            "expression": """
                (async () => {
                    const stFrame = document.querySelector('.stIFrame');
                    const doc = stFrame ? stFrame.contentDocument : document;
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    const vDoc = stFrame.contentDocument.getElementById('viewerIframe').contentDocument;

                    // Switch 3D viewer to Risk Overlay Mode
                    vDoc.querySelector('#modeRisk').click();

                    // Switch to Predict Risk tab in main dashboard
                    const navPredict = Array.from(doc.querySelectorAll('.navItem')).find(el => el.textContent && el.textContent.includes('Predict Risk'));
                    if (navPredict) navPredict.click();
                    await new Promise(r => setTimeout(r, 600));

                    // Click Predict button
                    const btnPredict = doc.querySelector('#btnPredict');
                    if (btnPredict) btnPredict.click();
                    await new Promise(r => setTimeout(r, 1200));

                    // Switch back to 3D Visualization tab
                    const nav3D = Array.from(doc.querySelectorAll('.navItem')).find(el => el.textContent && el.textContent.includes('3D Visualization'));
                    if (nav3D) nav3D.click();
                    await new Promise(r => setTimeout(r, 600));

                    // Read live probabilities from 3D viewer
                    const ladVal = vDoc.querySelector('#val-lad')?.textContent;
                    const lcxVal = vDoc.querySelector('#val-lcx')?.textContent;
                    const rcaVal = vDoc.querySelector('#val-rca')?.textContent;
                    const ladColor = '#' + vWin.materials['lad'].color.getHexString();
                    const lcxColor = '#' + vWin.materials['lcx'].color.getHexString();
                    const rcaColor = '#' + vWin.materials['rca'].color.getHexString();

                    return {
                        realPredictionsLoaded: ladVal !== '--' && lcxVal !== '--' && rcaVal !== '--',
                        liveTelemetry: { lad: ladVal, lcx: lcxVal, rca: rcaVal },
                        liveColors: { ladColor, lcxColor, rcaColor },
                        totalMeshesIntact: vWin.root.children.length === 106
                    };
                })()
            """,
            "awaitPromise": True,
            "returnByValue": True
        })
        t5 = t5_eval.get("result", {}).get("value", {})
        print(json.dumps(t5, indent=2), flush=True)
        await capture("dynamic_coloring_05_real_ml_predictions.png")

        # ---------------------------------------------------------------------
        # TEST 6: Multi-View Verification in Risk Mode (Anterior, Posterior, Left Lat, Right Lat)
        # ---------------------------------------------------------------------
        print("\n================== TEST 6: MULTI-VIEW INTEGRITY IN RISK OVERLAY MODE ==================", flush=True)
        views = [
            ("front", "dynamic_coloring_view_anterior.png", "Anterior"),
            ("back", "dynamic_coloring_view_posterior.png", "Posterior"),
            ("left", "dynamic_coloring_view_left_lat.png", "Left Lateral"),
            ("right", "dynamic_coloring_view_right_lat.png", "Right Lateral")
        ]
        for vname, imgname, vdesc in views:
            await cdp_call("Runtime.evaluate", {
                "expression": f"""
                    (() => {{
                        const stFrame = document.querySelector('.stIFrame');
                        const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                        vWin.setView('{vname}', false);
                    }})()
                """,
                "returnByValue": True
            })
            await asyncio.sleep(0.4)
            await capture(imgname)

        print("\n>>> ALL 6 DYNAMIC CORONARY RISK COLORING TESTS COMPLETE! <<<", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
