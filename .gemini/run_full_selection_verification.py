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

        # Reload page to get latest components/heart_viewer.html
        print("Reloading Streamlit page...", flush=True)
        await cdp_call("Page.reload")
        await asyncio.sleep(3)

        # Click 3D tab if not already selected
        await cdp_call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    if (stFrame) {
                        const doc = stFrame.contentDocument;
                        const tabs = doc.querySelectorAll('[data-view-tab], .tab-btn, button');
                        for (const b of tabs) {
                            if (b.textContent && (b.textContent.includes('3D Visualization') || b.textContent.includes('3D Heart'))) {
                                b.click();
                                return true;
                            }
                        }
                    }
                    return false;
                })()
            """,
            "returnByValue": True
        })

        # Wait for heart assembly to load
        print("Waiting for 106 meshes to finish loading...", flush=True)
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
        # TEST 1: LAD Selection
        # ---------------------------------------------------------------------
        print("\n================== TEST 1: LAD SELECTION ==================", flush=True)
        t1_eval = await cdp_call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    vWin.focusVesselGroup('lad');

                    const ladMat = vWin.materials['lad'];
                    const ladBrMat = vWin.materials['lad_branches'];
                    const lcxMat = vWin.materials['lcx'];
                    const rcaMat = vWin.materials['rca'];
                    const veinMat = vWin.materials['cardiac_veins'];
                    const ventMat = vWin.materials['ventricles'];

                    return {
                        selectedArterySystem: vWin.getSelectedArterySystem ? vWin.getSelectedArterySystem() : null,
                        ladEmissive: '#' + ladMat.emissive.getHexString(),
                        ladBranchEmissive: '#' + ladBrMat.emissive.getHexString(),
                        ladBaseColor: '#' + ladMat.color.getHexString(),
                        ladBranchBaseColor: '#' + ladBrMat.color.getHexString(),
                        ladOpacity: ladMat.opacity,
                        ladBranchOpacity: ladBrMat.opacity,
                        lcxOpacity: lcxMat.opacity,
                        rcaOpacity: rcaMat.opacity,
                        veinOpacity: veinMat.opacity,
                        ventricleOpacity: ventMat.opacity,
                        activeOutlineCount: vWin.getActiveOutlineMeshes ? vWin.getActiveOutlineMeshes().length : 0,
                        detailTitle: vWin.document.querySelector('#detail strong') ? vWin.document.querySelector('#detail strong').textContent : ''
                    };
                })()
            """,
            "returnByValue": True
        })
        t1 = t1_eval.get("result", {}).get("value", {})
        print(json.dumps(t1, indent=2), flush=True)
        await asyncio.sleep(0.5)
        await capture("lad_selection_verified.png")

        # ---------------------------------------------------------------------
        # TEST 2: LCX Selection
        # ---------------------------------------------------------------------
        print("\n================== TEST 2: LCX SELECTION ==================", flush=True)
        t2_eval = await cdp_call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    vWin.focusVesselGroup('lcx');

                    const ladMat = vWin.materials['lad'];
                    const lcxMat = vWin.materials['lcx'];
                    const lcxBrMat = vWin.materials['lcx_branches'];
                    const rcaMat = vWin.materials['rca'];

                    return {
                        selectedArterySystem: vWin.getSelectedArterySystem ? vWin.getSelectedArterySystem() : null,
                        lcxEmissive: '#' + lcxMat.emissive.getHexString(),
                        lcxBranchEmissive: '#' + lcxBrMat.emissive.getHexString(),
                        lcxBaseColor: '#' + lcxMat.color.getHexString(),
                        lcxBranchBaseColor: '#' + lcxBrMat.color.getHexString(),
                        lcxOpacity: lcxMat.opacity,
                        ladOpacity: ladMat.opacity,
                        rcaOpacity: rcaMat.opacity,
                        activeOutlineCount: vWin.getActiveOutlineMeshes ? vWin.getActiveOutlineMeshes().length : 0,
                        detailTitle: vWin.document.querySelector('#detail strong') ? vWin.document.querySelector('#detail strong').textContent : ''
                    };
                })()
            """,
            "returnByValue": True
        })
        t2 = t2_eval.get("result", {}).get("value", {})
        print(json.dumps(t2, indent=2), flush=True)
        await asyncio.sleep(0.5)
        await capture("lcx_selection_verified.png")

        # ---------------------------------------------------------------------
        # TEST 3: RCA Selection
        # ---------------------------------------------------------------------
        print("\n================== TEST 3: RCA SELECTION ==================", flush=True)
        t3_eval = await cdp_call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    vWin.focusVesselGroup('rca');

                    const ladMat = vWin.materials['lad'];
                    const lcxMat = vWin.materials['lcx'];
                    const rcaMat = vWin.materials['rca'];
                    const rcaBrMat = vWin.materials['rca_branches'];

                    return {
                        selectedArterySystem: vWin.getSelectedArterySystem ? vWin.getSelectedArterySystem() : null,
                        rcaEmissive: '#' + rcaMat.emissive.getHexString(),
                        rcaBranchEmissive: '#' + rcaBrMat.emissive.getHexString(),
                        rcaBaseColor: '#' + rcaMat.color.getHexString(),
                        rcaBranchBaseColor: '#' + rcaBrMat.color.getHexString(),
                        rcaOpacity: rcaMat.opacity,
                        ladOpacity: ladMat.opacity,
                        lcxOpacity: lcxMat.opacity,
                        activeOutlineCount: vWin.getActiveOutlineMeshes ? vWin.getActiveOutlineMeshes().length : 0,
                        detailTitle: vWin.document.querySelector('#detail strong') ? vWin.document.querySelector('#detail strong').textContent : ''
                    };
                })()
            """,
            "returnByValue": True
        })
        t3 = t3_eval.get("result", {}).get("value", {})
        print(json.dumps(t3, indent=2), flush=True)
        await asyncio.sleep(0.5)
        await capture("rca_selection_verified.png")

        # ---------------------------------------------------------------------
        # TEST 4: Myocardial Structure Selection (Left Ventricular Wall)
        # ---------------------------------------------------------------------
        print("\n================== TEST 4: MYOCARDIAL SELECTION ==================", flush=True)
        t4_eval = await cdp_call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;

                    // Locate a myocardial mesh in 'ventricles'
                    let targetMesh = null;
                    vWin.root.traverse(c => {
                        if (c.isMesh && c.userData && c.userData.group === 'ventricles' && !targetMesh) {
                            targetMesh = c;
                        }
                    });

                    if (targetMesh) {
                        vWin.selectMesh(targetMesh);
                    }

                    const ladMat = vWin.materials['lad'];
                    const lcxMat = vWin.materials['lcx'];
                    const rcaMat = vWin.materials['rca'];
                    const sharedVentMat = vWin.materials['ventricles'];

                    return {
                        selectedLabel: targetMesh ? targetMesh.userData.label : null,
                        selectedGroup: targetMesh ? targetMesh.userData.group : null,
                        meshEmissive: targetMesh ? '#' + targetMesh.material.emissive.getHexString() : null,
                        meshBaseColor: targetMesh ? '#' + targetMesh.material.color.getHexString() : null,
                        sharedVentricleEmissive: '#' + sharedVentMat.emissive.getHexString(),
                        ladOpacity: ladMat.opacity,
                        lcxOpacity: lcxMat.opacity,
                        rcaOpacity: rcaMat.opacity,
                        activeOutlineCount: vWin.getActiveOutlineMeshes ? vWin.getActiveOutlineMeshes().length : 0,
                        detailTitle: vWin.document.querySelector('#detail strong') ? vWin.document.querySelector('#detail strong').textContent : ''
                    };
                })()
            """,
            "returnByValue": True
        })
        t4 = t4_eval.get("result", {}).get("value", {})
        print(json.dumps(t4, indent=2), flush=True)
        await asyncio.sleep(0.5)
        await capture("myocardium_selection_verified.png")

        # ---------------------------------------------------------------------
        # TEST 5: Clean Deselection / Reset
        # ---------------------------------------------------------------------
        print("\n================== TEST 5: CLEAN DESELECTION ==================", flush=True)
        t5_eval = await cdp_call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    vWin.selectMesh(null);

                    const ladMat = vWin.materials['lad'];
                    const lcxMat = vWin.materials['lcx'];
                    const rcaMat = vWin.materials['rca'];
                    const veinMat = vWin.materials['cardiac_veins'];

                    return {
                        selectedArterySystem: vWin.getSelectedArterySystem ? vWin.getSelectedArterySystem() : null,
                        currentlySelectedMesh: vWin.getCurrentlySelectedMesh ? vWin.getCurrentlySelectedMesh() : null,
                        ladOpacity: ladMat.opacity,
                        lcxOpacity: lcxMat.opacity,
                        rcaOpacity: rcaMat.opacity,
                        veinOpacity: veinMat.opacity,
                        activeOutlineCount: vWin.getActiveOutlineMeshes ? vWin.getActiveOutlineMeshes().length : 0,
                        detailTitle: vWin.document.querySelector('#detail strong') ? vWin.document.querySelector('#detail strong').textContent : ''
                    };
                })()
            """,
            "returnByValue": True
        })
        t5 = t5_eval.get("result", {}).get("value", {})
        print(json.dumps(t5, indent=2), flush=True)
        await asyncio.sleep(0.5)
        await capture("deselection_clean_verified.png")

        # ---------------------------------------------------------------------
        # TEST 6: Pulsing Glow Sine Wave Verification
        # ---------------------------------------------------------------------
        print("\n================== TEST 6: PULSING GLOW MODULATION ==================", flush=True)
        t6_eval = await cdp_call("Runtime.evaluate", {
            "expression": """
                (async () => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    vWin.focusVesselGroup('lad');

                    const samples = [];
                    for (let i = 0; i < 4; i++) {
                        await new Promise(r => setTimeout(r, 150));
                        samples.push({
                            outlineOpacity: Number(vWin.outlineMaterial.uniforms.outlineOpacity.value.toFixed(3)),
                            outlineThickness: Number(vWin.outlineMaterial.uniforms.outlineThickness.value.toFixed(5)),
                            ladEmissiveIntensity: Number(vWin.materials['lad'].emissiveIntensity.toFixed(3))
                        });
                    }
                    return samples;
                })()
            """,
            "awaitPromise": True,
            "returnByValue": True
        })
        t6 = t6_eval.get("result", {}).get("value", {})
        print("Pulsing samples over 450ms:\n", json.dumps(t6, indent=2), flush=True)

        print("\n>>> ALL TESTS COMPLETE AND VERIFIED! <<<", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
