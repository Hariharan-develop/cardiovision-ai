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
            await asyncio.sleep(0.8)
            shot = await cdp_call("Page.captureScreenshot", {"format": "png"})
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
        print("Page brought to front.", flush=True)

        # Switch to 3D Visualization navItem
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

        # Wait for heart assembly to finish loading inside viewerIframe
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
        # TEST 1: Blue Cardiac Vein Selection
        # ---------------------------------------------------------------------
        print("\n================== TEST 1: BLUE CARDIAC VEIN SELECTION ==================", flush=True)
        t1_eval = await cdp_call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;

                    // Locate a blue cardiac vein mesh
                    let veinMesh = null;
                    vWin.root.traverse(c => {
                        if (c.isMesh && c.userData && c.userData.group === 'cardiac_veins' && !veinMesh) {
                            veinMesh = c;
                        }
                    });

                    if (veinMesh) {
                        vWin.selectMesh(veinMesh);
                    }

                    const originalSharedColor = '#' + vWin.materials['cardiac_veins'].color.getHexString();
                    const clonedMeshColor = veinMesh ? '#' + veinMesh.material.color.getHexString() : null;
                    const clonedMeshEmissive = veinMesh ? '#' + veinMesh.material.emissive.getHexString() : null;
                    const clonedEmissiveIntensity = veinMesh ? veinMesh.material.emissiveIntensity : null;
                    const isMaterialCloned = veinMesh ? (veinMesh.material !== vWin.materials['cardiac_veins']) : false;

                    return {
                        label: veinMesh ? veinMesh.userData.label : null,
                        group: veinMesh ? veinMesh.userData.group : null,
                        originalSharedColor,
                        clonedMeshColor,
                        clonedMeshEmissive,
                        clonedEmissiveIntensity,
                        isMaterialCloned,
                        activeOutlineCount: vWin.getActiveOutlineMeshes ? vWin.getActiveOutlineMeshes().length : 0,
                        selectedClonedCount: vWin.getSelectedClonedMeshes ? vWin.getSelectedClonedMeshes().length : 0,
                        inspectorTitle: vWin.document.querySelector('#detail strong') ? vWin.document.querySelector('#detail strong').textContent : ''
                    };
                })()
            """,
            "returnByValue": True
        })
        t1 = t1_eval.get("result", {}).get("value", {})
        print(json.dumps(t1, indent=2), flush=True)
        await capture("cardiovision_blue_vein_purple_glow.png")

        # ---------------------------------------------------------------------
        # TEST 2: Pink Heart Wall (Myocardium) Selection
        # ---------------------------------------------------------------------
        print("\n================== TEST 2: PINK HEART WALL SELECTION ==================", flush=True)
        t2_eval = await cdp_call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;

                    // Locate a ventricle mesh
                    let ventMesh = null;
                    vWin.root.traverse(c => {
                        if (c.isMesh && c.userData && c.userData.group === 'ventricles' && !ventMesh) {
                            ventMesh = c;
                        }
                    });

                    // First find previous vein mesh to verify its restoration
                    let veinMesh = null;
                    vWin.root.traverse(c => {
                        if (c.isMesh && c.userData && c.userData.group === 'cardiac_veins' && !veinMesh) {
                            veinMesh = c;
                        }
                    });

                    if (ventMesh) {
                        vWin.selectMesh(ventMesh);
                    }

                    // Vein should now be restored to shared material
                    const veinMaterialRestored = veinMesh ? (veinMesh.material === vWin.materials['cardiac_veins']) : false;
                    const veinCurrentColor = veinMesh ? '#' + veinMesh.material.color.getHexString() : null;

                    const ventOriginalSharedColor = '#' + vWin.materials['ventricles'].color.getHexString();
                    const ventClonedColor = ventMesh ? '#' + ventMesh.material.color.getHexString() : null;
                    const ventClonedEmissive = ventMesh ? '#' + ventMesh.material.emissive.getHexString() : null;
                    const ventEmissiveIntensity = ventMesh ? ventMesh.material.emissiveIntensity : null;
                    const isVentCloned = ventMesh ? (ventMesh.material !== vWin.materials['ventricles']) : false;

                    return {
                        ventLabel: ventMesh ? ventMesh.userData.label : null,
                        ventGroup: ventMesh ? ventMesh.userData.group : null,
                        veinMaterialRestored,
                        veinCurrentColor,
                        ventOriginalSharedColor,
                        ventClonedColor,
                        ventClonedEmissive,
                        ventEmissiveIntensity,
                        isVentCloned,
                        activeOutlineCount: vWin.getActiveOutlineMeshes ? vWin.getActiveOutlineMeshes().length : 0,
                        selectedClonedCount: vWin.getSelectedClonedMeshes ? vWin.getSelectedClonedMeshes().length : 0,
                        inspectorTitle: vWin.document.querySelector('#detail strong') ? vWin.document.querySelector('#detail strong').textContent : ''
                    };
                })()
            """,
            "returnByValue": True
        })
        t2 = t2_eval.get("result", {}).get("value", {})
        print(json.dumps(t2, indent=2), flush=True)
        await capture("cardiovision_pink_wall_purple_glow.png")

        # ---------------------------------------------------------------------
        # TEST 3: Orange RCA Selection (Trunk and Branches together)
        # ---------------------------------------------------------------------
        print("\n================== TEST 3: ORANGE RCA TERRITORY SELECTION ==================", flush=True)
        t3_eval = await cdp_call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;

                    vWin.focusVesselGroup('rca');

                    const rcaMeshes = [];
                    vWin.root.traverse(c => {
                        if (c.isMesh && (c.userData.group === 'rca' || c.userData.group === 'rca_branches')) {
                            rcaMeshes.push(c);
                        }
                    });

                    const allRcaPurple = rcaMeshes.every(m => '#' + m.material.color.getHexString() === '#b026ff' && '#' + m.material.emissive.getHexString() === '#b026ff');
                    const ladMat = vWin.materials['lad'];
                    const lcxMat = vWin.materials['lcx'];
                    const veinMat = vWin.materials['cardiac_veins'];

                    return {
                        selectedArterySystem: vWin.getSelectedArterySystem ? vWin.getSelectedArterySystem() : null,
                        rcaMeshCount: rcaMeshes.length,
                        allRcaPurple,
                        ladOpacityDimmed: ladMat.opacity === 0.4,
                        lcxOpacityDimmed: lcxMat.opacity === 0.4,
                        veinOpacityDimmed: veinMat.opacity === 0.4,
                        activeOutlineCount: vWin.getActiveOutlineMeshes ? vWin.getActiveOutlineMeshes().length : 0,
                        selectedClonedCount: vWin.getSelectedClonedMeshes ? vWin.getSelectedClonedMeshes().length : 0,
                        inspectorTitle: vWin.document.querySelector('#detail strong') ? vWin.document.querySelector('#detail strong').textContent : ''
                    };
                })()
            """,
            "returnByValue": True
        })
        t3 = t3_eval.get("result", {}).get("value", {})
        print(json.dumps(t3, indent=2), flush=True)
        await capture("cardiovision_orange_rca_purple_glow.png")

        # ---------------------------------------------------------------------
        # TEST 4: Blue LAD Selection (Trunk and Branches together)
        # ---------------------------------------------------------------------
        print("\n================== TEST 4: BLUE LAD TERRITORY SELECTION ==================", flush=True)
        t4_eval = await cdp_call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;

                    vWin.focusVesselGroup('lad');

                    const ladMeshes = [];
                    vWin.root.traverse(c => {
                        if (c.isMesh && (c.userData.group === 'lad' || c.userData.group === 'lad_branches')) {
                            ladMeshes.push(c);
                        }
                    });

                    const allLadPurple = ladMeshes.every(m => '#' + m.material.color.getHexString() === '#b026ff' && '#' + m.material.emissive.getHexString() === '#b026ff');
                    const rcaMat = vWin.materials['rca'];
                    const lcxMat = vWin.materials['lcx'];

                    return {
                        selectedArterySystem: vWin.getSelectedArterySystem ? vWin.getSelectedArterySystem() : null,
                        ladMeshCount: ladMeshes.length,
                        allLadPurple,
                        rcaOpacityDimmed: rcaMat.opacity === 0.4,
                        lcxOpacityDimmed: lcxMat.opacity === 0.4,
                        activeOutlineCount: vWin.getActiveOutlineMeshes ? vWin.getActiveOutlineMeshes().length : 0,
                        selectedClonedCount: vWin.getSelectedClonedMeshes ? vWin.getSelectedClonedMeshes().length : 0,
                        inspectorTitle: vWin.document.querySelector('#detail strong') ? vWin.document.querySelector('#detail strong').textContent : ''
                    };
                })()
            """,
            "returnByValue": True
        })
        t4 = t4_eval.get("result", {}).get("value", {})
        print(json.dumps(t4, indent=2), flush=True)
        await capture("cardiovision_lad_purple_glow.png")

        # ---------------------------------------------------------------------
        # TEST 5: Clean Deselection / Reset
        # ---------------------------------------------------------------------
        print("\n================== TEST 5: CLEAN DESELECTION / RESET ==================", flush=True)
        t5_eval = await cdp_call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;

                    vWin.selectMesh(null);

                    let anyClonedLeft = false;
                    vWin.root.traverse(c => {
                        if (c.isMesh && c.material !== vWin.materials[c.userData.group]) {
                            anyClonedLeft = true;
                        }
                    });

                    const ladMat = vWin.materials['lad'];
                    const lcxMat = vWin.materials['lcx'];
                    const rcaMat = vWin.materials['rca'];
                    const veinMat = vWin.materials['cardiac_veins'];

                    return {
                        selectedArterySystem: vWin.getSelectedArterySystem ? vWin.getSelectedArterySystem() : null,
                        currentlySelectedMesh: vWin.getCurrentlySelectedMesh ? vWin.getCurrentlySelectedMesh() : null,
                        anyClonedLeft,
                        ladOpacity: ladMat.opacity,
                        lcxOpacity: lcxMat.opacity,
                        rcaOpacity: rcaMat.opacity,
                        veinOpacity: veinMat.opacity,
                        activeOutlineCount: vWin.getActiveOutlineMeshes ? vWin.getActiveOutlineMeshes().length : 0,
                        selectedClonedCount: vWin.getSelectedClonedMeshes ? vWin.getSelectedClonedMeshes().length : 0
                    };
                })()
            """,
            "returnByValue": True
        })
        t5 = t5_eval.get("result", {}).get("value", {})
        print(json.dumps(t5, indent=2), flush=True)
        await capture("cardiovision_clean_deselection.png")

        print("\n>>> ALL TESTS COMPLETE AND SCREENSHOTS CAPTURED! <<<", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
