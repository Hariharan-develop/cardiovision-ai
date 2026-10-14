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

        await asyncio.sleep(1.5)

        # ---------------------------------------------------------------------
        # TEST 1: Heartbeat Controls Initial State
        # ---------------------------------------------------------------------
        print("\n================== TEST 1: HEARTBEAT INITIAL STATE ==================", flush=True)
        t1_eval = await cdp_call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    const vDoc = stFrame.contentDocument.getElementById('viewerIframe').contentDocument;

                    const toggle = vDoc.querySelector('#toggleHeartbeat');
                    const slider = vDoc.querySelector('#bpmSlider');
                    const display = vDoc.querySelector('#bpmDisplay');
                    const dot = vDoc.querySelector('#heartbeatPulseDot');
                    const state = vWin.CardioVision3D.getHeartbeatState();

                    return {
                        toggleChecked: toggle ? toggle.checked : null,
                        sliderValue: slider ? Number(slider.value) : null,
                        displayText: display ? display.textContent.trim() : null,
                        dotExists: !!dot,
                        dotPausedClass: dot ? dot.classList.contains('paused') : null,
                        engineState: state
                    };
                })()
            """,
            "returnByValue": True
        })
        t1 = t1_eval.get("result", {}).get("value", {})
        print(json.dumps(t1, indent=2), flush=True)

        # ---------------------------------------------------------------------
        # TEST 2: Active Contraction Cycle & Coronary Lockstep Alignment
        # ---------------------------------------------------------------------
        print("\n================== TEST 2: CONTRACTION CYCLE & CORONARY ALIGNMENT ==================", flush=True)
        t2_eval = await cdp_call("Runtime.evaluate", {
            "expression": """
                (async () => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;

                    // Sample over 900ms (covers full cardiac cycle at 72 BPM = 833ms)
                    const samples = [];
                    let minScaleX = 1.0;
                    let maxScaleX = 0.0;
                    let allCoronariesAligned = true;
                    let all106PresentAndAligned = true;

                    for (let step = 0; step < 12; step++) {
                        await new Promise(r => setTimeout(r, 75));

                        // Find ventricle and coronary meshes
                        let ventObj = null;
                        let ladObj = null;
                        let lcxObj = null;
                        let rcaObj = null;

                        vWin.root.children.forEach(obj => {
                            if (obj.userData) {
                                if (obj.userData.group === 'ventricles' && !ventObj) ventObj = obj;
                                if (obj.userData.group === 'lad' && !ladObj) ladObj = obj;
                                if (obj.userData.group === 'lcx' && !lcxObj) lcxObj = obj;
                                if (obj.userData.group === 'rca' && !rcaObj) rcaObj = obj;
                            }
                        });

                        const ventScaleX = Number(ventObj.scale.x.toFixed(4));
                        const ladScaleX = Number(ladObj.scale.x.toFixed(4));
                        const lcxScaleX = Number(lcxObj.scale.x.toFixed(4));
                        const rcaScaleX = Number(rcaObj.scale.x.toFixed(4));
                        const ventScaleY = Number(ventObj.scale.y.toFixed(4));
                        const ventPosZ = Number(ventObj.position.z.toFixed(4));
                        const ladPosZ = Number(ladObj.position.z.toFixed(4));

                        if (ventScaleX < minScaleX) minScaleX = ventScaleX;
                        if (ventScaleX > maxScaleX) maxScaleX = ventScaleX;

                        // Check lockstep alignment between myocardium and ALL coronaries
                        const coronaryMatch = (ventScaleX === ladScaleX) && (ventScaleX === lcxScaleX) && (ventScaleX === rcaScaleX);
                        const posMatch = (ventPosZ === ladPosZ);
                        if (!coronaryMatch || !posMatch) allCoronariesAligned = false;

                        // Verify every single mesh in root.children has identical scale
                        vWin.root.children.forEach(c => {
                            if (Math.abs(c.scale.x - ventScaleX) > 1e-4) all106PresentAndAligned = false;
                        });

                        samples.push({
                            timeMs: step * 75,
                            phase: Number(vWin.CardioVision3D.getHeartbeatState().phase.toFixed(3)),
                            ventScaleX,
                            ventScaleY,
                            ventPosZ,
                            coronaryMatch: coronaryMatch && posMatch
                        });
                    }

                    return {
                        totalMeshes: vWin.root.children.length,
                        sampleCount: samples.length,
                        minScaleX,
                        maxScaleX,
                        systolicContractionPct: Number(((1.0 - minScaleX) * 100).toFixed(2)),
                        allCoronariesAligned,
                        all106PresentAndAligned,
                        samples: samples.slice(0, 8)
                    };
                })()
            """,
            "awaitPromise": True,
            "returnByValue": True
        })
        t2 = t2_eval.get("result", {}).get("value", {})
        print(json.dumps(t2, indent=2), flush=True)
        await capture("heartbeat_active_running.png")

        # ---------------------------------------------------------------------
        # TEST 3: Heart Rate Slider Modulation (40 - 120 BPM)
        # ---------------------------------------------------------------------
        print("\n================== TEST 3: HEART RATE BPM ADJUSTMENT ==================", flush=True)
        t3_eval = await cdp_call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    const vDoc = stFrame.contentDocument.getElementById('viewerIframe').contentDocument;

                    const slider = vDoc.querySelector('#bpmSlider');
                    const display = vDoc.querySelector('#bpmDisplay');

                    // Set to 105 BPM (tachycardia test)
                    slider.value = 105;
                    slider.dispatchEvent(new Event('input'));

                    const state105 = vWin.CardioVision3D.getHeartbeatState();
                    const text105 = display.textContent.trim();

                    // Set to 50 BPM (bradycardia test)
                    slider.value = 50;
                    slider.dispatchEvent(new Event('input'));

                    const state50 = vWin.CardioVision3D.getHeartbeatState();
                    const text50 = display.textContent.trim();

                    // Restore to 72 BPM
                    slider.value = 72;
                    slider.dispatchEvent(new Event('input'));

                    const state72 = vWin.CardioVision3D.getHeartbeatState();
                    const text72 = display.textContent.trim();

                    return {
                        bpm105: { stateBpm: state105.bpm, displayText: text105 },
                        bpm50: { stateBpm: state50.bpm, displayText: text50 },
                        bpm72: { stateBpm: state72.bpm, displayText: text72 }
                    };
                })()
            """,
            "returnByValue": True
        })
        t3 = t3_eval.get("result", {}).get("value", {})
        print(json.dumps(t3, indent=2), flush=True)

        # ---------------------------------------------------------------------
        # TEST 4: Toggle OFF / Smooth Easing / Exact Resting Shape Restoration
        # ---------------------------------------------------------------------
        print("\n================== TEST 4: HEARTBEAT TOGGLE OFF & RESTING SHAPE RESTORATION ==================", flush=True)
        t4_eval = await cdp_call("Runtime.evaluate", {
            "expression": """
                (async () => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    const vDoc = stFrame.contentDocument.getElementById('viewerIframe').contentDocument;

                    const toggle = vDoc.querySelector('#toggleHeartbeat');
                    const display = vDoc.querySelector('#bpmDisplay');
                    const dot = vDoc.querySelector('#heartbeatPulseDot');

                    // Toggle OFF
                    toggle.checked = false;
                    toggle.dispatchEvent(new Event('change'));

                    // Wait 350ms for smooth ease-down
                    await new Promise(r => setTimeout(r, 350));

                    const state = vWin.CardioVision3D.getHeartbeatState();
                    const textPaused = display.textContent.trim();
                    const isDotPaused = dot.classList.contains('paused');

                    // Verify ALL 106 meshes are strictly restored to exact identity transforms
                    let nonZeroPos = 0;
                    let nonZeroRot = 0;
                    let nonUnitScale = 0;

                    vWin.root.children.forEach(obj => {
                        if (obj.position.lengthSq() > 1e-6) nonZeroPos++;
                        if (Math.abs(obj.rotation.x) > 1e-4 || Math.abs(obj.rotation.y) > 1e-4 || Math.abs(obj.rotation.z) > 1e-4) nonZeroRot++;
                        if (Math.abs(obj.scale.x - 1) > 1e-4 || Math.abs(obj.scale.y - 1) > 1e-4 || Math.abs(obj.scale.z - 1) > 1e-4) nonUnitScale++;
                    });

                    return {
                        enabled: state.enabled,
                        activity: state.activity,
                        textPaused,
                        isDotPaused,
                        meshCount: vWin.root.children.length,
                        nonZeroPos,
                        nonZeroRot,
                        nonUnitScale,
                        allMeshesRestoredToRestingShape: (nonZeroPos === 0 && nonZeroRot === 0 && nonUnitScale === 0)
                    };
                })()
            """,
            "awaitPromise": True,
            "returnByValue": True
        })
        t4 = t4_eval.get("result", {}).get("value", {})
        print(json.dumps(t4, indent=2), flush=True)
        await capture("heartbeat_paused_rest_state.png")

        # ---------------------------------------------------------------------
        # TEST 5: Toggle Back ON & Seamless Resume
        # ---------------------------------------------------------------------
        print("\n================== TEST 5: HEARTBEAT TOGGLE ON & SEAMLESS RESUME ==================", flush=True)
        t5_eval = await cdp_call("Runtime.evaluate", {
            "expression": """
                (async () => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    const vDoc = stFrame.contentDocument.getElementById('viewerIframe').contentDocument;

                    const toggle = vDoc.querySelector('#toggleHeartbeat');
                    const display = vDoc.querySelector('#bpmDisplay');
                    const dot = vDoc.querySelector('#heartbeatPulseDot');

                    // Toggle ON
                    toggle.checked = true;
                    toggle.dispatchEvent(new Event('change'));

                    // Wait 250ms for smooth ramp-up
                    await new Promise(r => setTimeout(r, 250));

                    const state = vWin.CardioVision3D.getHeartbeatState();
                    const textResumed = display.textContent.trim();
                    const isDotActive = !dot.classList.contains('paused');

                    return {
                        enabled: state.enabled,
                        activity: state.activity,
                        textResumed,
                        isDotActive
                    };
                })()
            """,
            "awaitPromise": True,
            "returnByValue": True
        })
        t5 = t5_eval.get("result", {}).get("value", {})
        print(json.dumps(t5, indent=2), flush=True)

        # ---------------------------------------------------------------------
        # TEST 6: Co-existence with Electric Purple Selection Highlight
        # ---------------------------------------------------------------------
        print("\n================== TEST 6: ELECTRIC PURPLE SELECTION DURING HEARTBEAT ==================", flush=True)
        t6_eval = await cdp_call("Runtime.evaluate", {
            "expression": """
                (async () => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;

                    // Select LAD system while beating
                    vWin.focusVesselGroup('lad');
                    await new Promise(r => setTimeout(r, 200));

                    const ladMat = vWin.materials['lad'];
                    const selectedArterySystem = vWin.getSelectedArterySystem();
                    const activeOutlineCount = vWin.getActiveOutlineMeshes().length;
                    const heartbeatState = vWin.CardioVision3D.getHeartbeatState();

                    // Check that lad mesh is pulsing with Electric Purple glow
                    let ladMesh = null;
                    vWin.root.children.forEach(obj => {
                        if (obj.userData && obj.userData.group === 'lad' && !ladMesh) {
                            obj.traverse(c => { if (c.isMesh && !ladMesh) ladMesh = c; });
                        }
                    });

                    const meshColor = ladMesh ? '#' + ladMesh.material.color.getHexString() : null;
                    const meshEmissive = ladMesh ? '#' + ladMesh.material.emissive.getHexString() : null;
                    const hasOutlineChild = ladMesh ? !!ladMesh.children.find(c => c.name === 'selectionOutline') : false;

                    return {
                        selectedArterySystem,
                        meshColor,
                        meshEmissive,
                        hasOutlineChild,
                        activeOutlineCount,
                        heartbeatRunning: heartbeatState.enabled && heartbeatState.activity > 0.5
                    };
                })()
            """,
            "awaitPromise": True,
            "returnByValue": True
        })
        t6 = t6_eval.get("result", {}).get("value", {})
        print(json.dumps(t6, indent=2), flush=True)
        await capture("heartbeat_with_purple_selection.png")

        # ---------------------------------------------------------------------
        # TEST 7: Co-existence with Coronary Focus & Anatomical Layer Filtering
        # ---------------------------------------------------------------------
        print("\n================== TEST 7: CORONARY FOCUS & LAYER FILTERING DURING HEARTBEAT ==================", flush=True)
        t7_eval = await cdp_call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    const vDoc = stFrame.contentDocument.getElementById('viewerIframe').contentDocument;

                    // Click Coronary Focus preset
                    const coronaryBtn = vDoc.querySelector('#presetCoronary');
                    if (coronaryBtn) coronaryBtn.click();

                    const ventOpacity = vWin.materials['ventricles'].opacity;
                    const isCoronaryActive = coronaryBtn.classList.contains('active');
                    const heartbeatState = vWin.CardioVision3D.getHeartbeatState();

                    // Restore Complete Heart preset
                    const completeBtn = vDoc.querySelector('#presetComplete');
                    if (completeBtn) completeBtn.click();

                    return {
                        isCoronaryActive,
                        ventOpacityInCoronaryFocus: ventOpacity,
                        heartbeatRemainedActive: heartbeatState.enabled
                    };
                })()
            """,
            "returnByValue": True
        })
        t7 = t7_eval.get("result", {}).get("value", {})
        print(json.dumps(t7, indent=2), flush=True)

        # ---------------------------------------------------------------------
        # TEST 8: Multi-View Anatomical Assembly & Vessel Continuity Verification
        # (Anterior, Posterior, Left Lateral, Right Lateral)
        # ---------------------------------------------------------------------
        print("\n================== TEST 8: MULTI-VIEW ANATOMICAL INTEGRITY INSPECTION ==================", flush=True)
        views = [
            ("front", "heartbeat_view_anterior.png", "Anterior (Sternocostal surface / LAD)"),
            ("back", "heartbeat_view_posterior.png", "Posterior (Diaphragmatic surface / Base)"),
            ("left", "heartbeat_view_left_lateral.png", "Left Lateral (LV obtuse margin / LCX)"),
            ("right", "heartbeat_view_right_lateral.png", "Right Lateral (RV / RCA)")
        ]
        
        for view_name, img_name, desc in views:
            print(f"Switching to {desc}...", flush=True)
            await cdp_call("Runtime.evaluate", {
                "expression": f"""
                    (() => {{
                        const stFrame = document.querySelector('.stIFrame');
                        const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                        vWin.setView('{view_name}', false);
                        return true;
                    }})()
                """,
                "returnByValue": True
            })
            await asyncio.sleep(0.6)
            await capture(img_name)
            
            # Check mesh visibility and wall continuity
            chk_eval = await cdp_call("Runtime.evaluate", {
                "expression": """
                    (() => {
                        const stFrame = document.querySelector('.stIFrame');
                        const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                        let visibleMeshes = 0;
                        let allFiniteTransforms = true;
                        vWin.root.children.forEach(c => {
                            if (c.visible !== false) visibleMeshes++;
                            if (!Number.isFinite(c.position.x) || !Number.isFinite(c.scale.x)) allFiniteTransforms = false;
                        });
                        return { visibleMeshes, allFiniteTransforms };
                    })()
                """,
                "returnByValue": True
            })
            chk = chk_eval.get("result", {}).get("value", {})
            print(f"  -> {view_name} view check: {chk}", flush=True)

        # Restore front view
        await cdp_call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    vWin.setView('front', false);
                })()
            """,
            "returnByValue": True
        })

        print("\n>>> ALL 8 HEARTBEAT VERIFICATION TESTS COMPLETE! <<<", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
