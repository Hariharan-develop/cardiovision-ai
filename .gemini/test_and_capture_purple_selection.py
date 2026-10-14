import asyncio, json, urllib.request, websockets, base64, os

ARTIFACT_DIR = r"C:\Users\hario\.gemini\antigravity-ide\brain\8cd09337-1c91-438d-aacf-249a561d03c7"

async def cdp_call(ws, method, params=None):
    msg_id = getattr(cdp_call, "counter", 1) + 1
    cdp_call.counter = msg_id
    payload = {"id": msg_id, "method": method, "params": params or {}}
    await ws.send(json.dumps(payload))
    while True:
        res = json.loads(await ws.recv())
        if res.get("id") == msg_id:
            return res

async def main():
    pages = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json/list").read().decode())
    target = next((p for p in pages if "CardioVision" in p.get("title", "")), pages[0])
    ws_url = target["webSocketDebuggerUrl"]
    print("Connecting to target:", target.get("title"), "at", ws_url)

    async with websockets.connect(ws_url, max_size=20_000_000) as ws:
        # Reload to ensure latest components/heart_viewer.html is loaded
        print("Reloading page...")
        await cdp_call(ws, "Page.reload")
        await asyncio.sleep(4)

        # Bring to front
        await cdp_call(ws, "Page.bringToFront")

        # Check if 3D Visualization tab is selected in Streamlit or dashboard
        tab_eval = await cdp_call(ws, "Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    if (stFrame) {
                        const doc = stFrame.contentDocument || stFrame.contentWindow.document;
                        // Click 3D tab if available
                        const tab3d = doc.querySelector('[data-view-tab="3d"]') || doc.querySelector('#tab-3d') || Array.from(doc.querySelectorAll('button, a, div')).find(el => el.textContent.includes('3D Visualization') || el.textContent.includes('3D Heart'));
                        if (tab3d) tab3d.click();
                        return { foundTabInFrame: !!tab3d };
                    }
                    return { foundTabInFrame: false };
                })()
            """,
            "returnByValue": True
        })
        print("Tab eval:", tab_eval.get("result", {}).get("result", {}).get("value"))
        await asyncio.sleep(2)

        # Wait for all 106 meshes to load in the 3D heart viewer
        print("Waiting for meshes to finish loading...")
        for attempt in range(40):
            status = await cdp_call(ws, "Runtime.evaluate", {
                "expression": """
                    (() => {
                        const stFrame = document.querySelector('.stIFrame');
                        if (!stFrame) return { status: 'no_stFrame' };
                        const vIframe = stFrame.contentDocument.getElementById('viewerIframe');
                        if (!vIframe) return { status: 'no_viewerIframe' };
                        const vWin = vIframe.contentWindow;
                        const vDoc = vIframe.contentDocument;
                        const statusEl = vDoc.querySelector('#loadStatus');
                        const statusText = statusEl ? statusEl.textContent : '';
                        const meshesCount = vWin.root ? vWin.root.children.length : 0;
                        return {
                            statusText,
                            meshesCount,
                            hasCV3D: !!vWin.CardioVision3D,
                            hasLoadedAll: statusText.includes('Complete heart loaded') || meshesCount >= 106
                        };
                    })()
                """,
                "returnByValue": True
            })
            val = status.get("result", {}).get("result", {}).get("value", {})
            safe_status = str(val).encode('ascii', 'replace').decode('ascii')
            print(f"[{attempt}] Status: {safe_status}")
            if val.get("hasLoadedAll"):
                print("All meshes loaded successfully!")
                break
            await asyncio.sleep(1)

        await asyncio.sleep(1)

        # Function to capture screenshot
        async def capture(filename):
            shot = await cdp_call(ws, "Page.captureScreenshot", {"format": "png"})
            raw_data = shot.get("result", {}).get("data") or shot.get("data")
            out_file = os.path.join(ARTIFACT_DIR, filename)
            with open(out_file, "wb") as f:
                f.write(base64.b64decode(raw_data))
            print(f"Screenshot saved: {out_file}")
            return out_file

        # TEST 1: Select LAD (Trunk and Branches)
        print("\n--- Testing LAD Selection ---")
        lad_test = await cdp_call(ws, "Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    vWin.focusVesselGroup('lad');
                    
                    // Inspect state
                    const ladMat = vWin.materials['lad'];
                    const ladBranchMat = vWin.materials['lad_branches'];
                    const lcxMat = vWin.materials['lcx'];
                    const rcaMat = vWin.materials['rca'];
                    const veinMat = vWin.materials['cardiac_veins'];
                    
                    return {
                        selectedArterySystem: vWin.getSelectedArterySystem ? vWin.getSelectedArterySystem() : null,
                        ladEmissive: '#' + ladMat.emissive.getHexString(),
                        ladBranchEmissive: '#' + ladBranchMat.emissive.getHexString(),
                        ladColor: '#' + ladMat.color.getHexString(),
                        ladBranchColor: '#' + ladBranchMat.color.getHexString(),
                        ladOpacity: ladMat.opacity,
                        lcxOpacity: lcxMat.opacity,
                        rcaOpacity: rcaMat.opacity,
                        veinOpacity: veinMat.opacity,
                        outlineMeshCount: vWin.getActiveOutlineMeshes ? vWin.getActiveOutlineMeshes().length : 0,
                        detailName: vWin.document.querySelector('#detail strong') ? vWin.document.querySelector('#detail strong').textContent : ''
                    };
                })()
            """,
            "returnByValue": True
        })
        print("LAD Test Result:", json.dumps(lad_test.get("result", {}).get("result", {}).get("value"), indent=2))
        await asyncio.sleep(0.5)
        await capture("lad_selection_electric_purple.png")

        # TEST 2: Select LCX (Trunk and Branches)
        print("\n--- Testing LCX Selection ---")
        lcx_test = await cdp_call(ws, "Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    vWin.focusVesselGroup('lcx');
                    
                    const ladMat = vWin.materials['lad'];
                    const lcxMat = vWin.materials['lcx'];
                    const lcxBranchMat = vWin.materials['lcx_branches'];
                    const rcaMat = vWin.materials['rca'];
                    
                    return {
                        selectedArterySystem: vWin.getSelectedArterySystem ? vWin.getSelectedArterySystem() : null,
                        lcxEmissive: '#' + lcxMat.emissive.getHexString(),
                        lcxBranchEmissive: '#' + lcxBranchMat.emissive.getHexString(),
                        lcxColor: '#' + lcxMat.color.getHexString(),
                        lcxBranchColor: '#' + lcxBranchMat.color.getHexString(),
                        lcxOpacity: lcxMat.opacity,
                        ladOpacity: ladMat.opacity,
                        rcaOpacity: rcaMat.opacity,
                        outlineMeshCount: vWin.getActiveOutlineMeshes ? vWin.getActiveOutlineMeshes().length : 0,
                        detailName: vWin.document.querySelector('#detail strong') ? vWin.document.querySelector('#detail strong').textContent : ''
                    };
                })()
            """,
            "returnByValue": True
        })
        print("LCX Test Result:", json.dumps(lcx_test.get("result", {}).get("result", {}).get("value"), indent=2))
        await asyncio.sleep(0.5)
        await capture("lcx_selection_electric_purple.png")

        # TEST 3: Select RCA (Trunk and Branches)
        print("\n--- Testing RCA Selection ---")
        rca_test = await cdp_call(ws, "Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    vWin.focusVesselGroup('rca');
                    
                    const ladMat = vWin.materials['lad'];
                    const lcxMat = vWin.materials['lcx'];
                    const rcaMat = vWin.materials['rca'];
                    const rcaBranchMat = vWin.materials['rca_branches'];
                    
                    return {
                        selectedArterySystem: vWin.getSelectedArterySystem ? vWin.getSelectedArterySystem() : null,
                        rcaEmissive: '#' + rcaMat.emissive.getHexString(),
                        rcaBranchEmissive: '#' + rcaBranchMat.emissive.getHexString(),
                        rcaColor: '#' + rcaMat.color.getHexString(),
                        rcaBranchColor: '#' + rcaBranchMat.color.getHexString(),
                        rcaOpacity: rcaMat.opacity,
                        ladOpacity: ladMat.opacity,
                        lcxOpacity: lcxMat.opacity,
                        outlineMeshCount: vWin.getActiveOutlineMeshes ? vWin.getActiveOutlineMeshes().length : 0,
                        detailName: vWin.document.querySelector('#detail strong') ? vWin.document.querySelector('#detail strong').textContent : ''
                    };
                })()
            """,
            "returnByValue": True
        })
        print("RCA Test Result:", json.dumps(rca_test.get("result", {}).get("result", {}).get("value"), indent=2))
        await asyncio.sleep(0.5)
        await capture("rca_selection_electric_purple.png")

        # TEST 4: Select Myocardial Structure (e.g., Left Ventricle Wall)
        print("\n--- Testing Myocardial Structure Selection ---")
        myo_test = await cdp_call(ws, "Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    
                    // Find a ventricle mesh
                    let lvMesh = null;
                    vWin.root.traverse(c => {
                        if (c.isMesh && c.userData && c.userData.group === 'ventricles' && !lvMesh) {
                            lvMesh = c;
                        }
                    });
                    
                    if (lvMesh) {
                        vWin.selectMesh(lvMesh);
                    }
                    
                    const ladMat = vWin.materials['lad'];
                    const lcxMat = vWin.materials['lcx'];
                    const rcaMat = vWin.materials['rca'];
                    
                    return {
                        selectedName: lvMesh ? lvMesh.userData.label : null,
                        selectedGroup: lvMesh ? lvMesh.userData.group : null,
                        meshEmissive: lvMesh ? '#' + lvMesh.material.emissive.getHexString() : null,
                        meshColor: lvMesh ? '#' + lvMesh.material.color.getHexString() : null,
                        sharedVentricleEmissive: '#' + vWin.materials['ventricles'].emissive.getHexString(),
                        ladOpacity: ladMat.opacity,
                        lcxOpacity: lcxMat.opacity,
                        rcaOpacity: rcaMat.opacity,
                        outlineMeshCount: vWin.getActiveOutlineMeshes ? vWin.getActiveOutlineMeshes().length : 0,
                        detailName: vWin.document.querySelector('#detail strong') ? vWin.document.querySelector('#detail strong').textContent : ''
                    };
                })()
            """,
            "returnByValue": True
        })
        print("Myocardium Test Result:", json.dumps(myo_test.get("result", {}).get("result", {}).get("value"), indent=2))
        await asyncio.sleep(0.5)
        await capture("myocardium_selection_electric_purple.png")

        # TEST 5: Deselection / Background Click (Clean Reset)
        print("\n--- Testing Deselection / Clean Reset ---")
        reset_test = await cdp_call(ws, "Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    vWin.selectMesh(null);
                    
                    const ladMat = vWin.materials['lad'];
                    const lcxMat = vWin.materials['lcx'];
                    const rcaMat = vWin.materials['rca'];
                    
                    return {
                        currentlySelectedMesh: vWin.getCurrentlySelectedMesh ? vWin.getCurrentlySelectedMesh() : null,
                        selectedArterySystem: vWin.getSelectedArterySystem ? vWin.getSelectedArterySystem() : null,
                        ladOpacity: ladMat.opacity,
                        lcxOpacity: lcxMat.opacity,
                        rcaOpacity: rcaMat.opacity,
                        outlineMeshCount: vWin.getActiveOutlineMeshes ? vWin.getActiveOutlineMeshes().length : 0,
                        detailName: vWin.document.querySelector('#detail strong') ? vWin.document.querySelector('#detail strong').textContent : ''
                    };
                })()
            """,
            "returnByValue": True
        })
        print("Reset Test Result:", json.dumps(reset_test.get("result", {}).get("result", {}).get("value"), indent=2))
        await asyncio.sleep(0.5)
        await capture("deselection_clean_reset.png")

        # TEST 6: Pulsing Glow Verification over time
        print("\n--- Testing Pulsing Glow Modulation ---")
        pulse_test = await cdp_call(ws, "Runtime.evaluate", {
            "expression": """
                (async () => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    vWin.focusVesselGroup('lad');
                    
                    const samples = [];
                    for (let i = 0; i < 5; i++) {
                        await new Promise(r => setTimeout(r, 120));
                        samples.push({
                            outlineOpacity: vWin.outlineMaterial.uniforms.outlineOpacity.value,
                            outlineThickness: vWin.outlineMaterial.uniforms.outlineThickness.value,
                            ladEmissiveIntensity: vWin.materials['lad'].emissiveIntensity
                        });
                    }
                    return samples;
                })()
            """,
            "awaitPromise": True,
            "returnByValue": True
        })
        print("Pulse Samples:", json.dumps(pulse_test.get("result", {}).get("result", {}).get("value"), indent=2))

if __name__ == "__main__":
    asyncio.run(main())
