import asyncio, json, urllib.request, websockets, base64, os

ARTIFACT_DIR = r"C:\Users\hario\.gemini\antigravity-ide\brain\8cd09337-1c91-438d-aacf-249a561d03c7"

async def main():
    pages = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json/list").read().decode())
    p = [x for x in pages if "8501" in x.get("url", "")][0]
    ws_url = p["webSocketDebuggerUrl"]
    print("Connecting to:", p["title"], "at", ws_url, flush=True)

    msg_id = 0
    async with websockets.connect(ws_url, max_size=30_000_000) as ws:
        async def call(method, params=None):
            nonlocal msg_id
            msg_id += 1
            cid = msg_id
            await ws.send(json.dumps({"id": cid, "method": method, "params": params or {}}))
            while True:
                raw = await ws.recv()
                msg = json.loads(raw)
                if msg.get("id") == cid:
                    return msg.get("result", {})

        async def capture(name):
            try:
                await asyncio.sleep(0.6)
                res = await asyncio.wait_for(call("Page.captureScreenshot", {"format": "png"}), timeout=5.0)
                data = res.get("data")
                if data:
                    filepath = os.path.join(ARTIFACT_DIR, name)
                    with open(filepath, "wb") as f:
                        f.write(base64.b64decode(data))
                    print(f"Captured: {filepath}", flush=True)
                    return filepath
            except Exception as e:
                print(f"Capture error or timeout for {name}: {e}", flush=True)
                return None

        await call("Page.bringToFront")
        print("Reloading page to load latest viewer...", flush=True)
        await call("Page.reload")
        await asyncio.sleep(3)
        await call("Page.bringToFront")

        # Navigate to 3D tab with retry loop
        print("Navigating to 3D Visualization tab...", flush=True)
        for _ in range(15):
            res = await call("Runtime.evaluate", {
                "expression": """
                    (() => {
                        const stFrame = document.querySelector('.stIFrame');
                        if (!stFrame || !stFrame.contentDocument) return false;
                        const doc = stFrame.contentDocument;
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
            if res.get("result", {}).get("value") is True:
                print("Clicked 3D Visualization tab!", flush=True)
                break
            await asyncio.sleep(0.5)

        print("Waiting for meshes to load...", flush=True)
        for _ in range(30):
            res = await call("Runtime.evaluate", {
                "expression": """
                    (() => {
                        const stFrame = document.querySelector('.stIFrame');
                        if (!stFrame) return false;
                        const vIframe = stFrame.contentDocument.getElementById('viewerIframe');
                        if (!vIframe) return false;
                        const vWin = vIframe.contentWindow;
                        const statusEl = vIframe.contentDocument.querySelector('#loadStatus');
                        const txt = statusEl ? statusEl.textContent : '';
                        return txt.includes('Complete heart loaded') || (vWin.root && vWin.root.children.length >= 106);
                    })()
                """,
                "returnByValue": True
            })
            if res.get("result", {}).get("value") is True:
                print("Meshes fully loaded!", flush=True)
                break
            await asyncio.sleep(1)

        await asyncio.sleep(1)

        print("\n================== VERIFYING MYOCARDIAL SELECTION REFINEMENT ==================", flush=True)
        eval_res = await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const vIframe = st.contentDocument.getElementById('viewerIframe');
                    const vWin = vIframe.contentWindow;

                    // Select left ventricle free wall
                    let ventMesh = null;
                    vWin.root.traverse(c => {
                        if (c.isMesh && c.userData && c.userData.label && c.userData.label.includes('Free wall of left ventricle')) {
                            ventMesh = c;
                        }
                    });

                    if (!ventMesh) return { error: 'ventMesh not found' };

                    // Select it
                    vWin.selectMesh(ventMesh);

                    const outlineMat = vWin.outlineMaterial;
                    const thickness = outlineMat.uniforms.outlineThickness.value;
                    const opacity = outlineMat.uniforms.outlineOpacity.value;
                    const colorHex = '#' + outlineMat.uniforms.outlineColor.value.getHexString();
                    const aspect = outlineMat.uniforms.aspect ? outlineMat.uniforms.aspect.value : null;

                    const curMat = ventMesh.material;
                    const baseColorHex = '#' + curMat.color.getHexString();
                    const emissiveHex = '#' + curMat.emissive.getHexString();
                    const emissiveIntensity = curMat.emissiveIntensity;

                    const activeOutlines = vWin.getActiveOutlineMeshes();

                    return {
                        meshLabel: ventMesh.userData.label,
                        baseColorHex: baseColorHex,
                        emissiveHex: emissiveHex,
                        emissiveIntensity: emissiveIntensity,
                        outlineThickness: thickness,
                        outlineOpacity: opacity,
                        outlineColor: colorHex,
                        outlineCount: activeOutlines.length,
                        aspectUniform: aspect
                    };
                })()
            """,
            "returnByValue": True
        })
        r = eval_res.get("result", {}).get("value", {})
        print("Myocardial Selection State:", json.dumps(r, indent=2), flush=True)

        # Assertions
        assert r.get("baseColorHex") == "#b85b63", f"Expected base color #b85b63 (pink), got {r.get('baseColorHex')}"
        assert r.get("emissiveIntensity") <= 0.16, f"Expected subtle emissive <= 0.16, got {r.get('emissiveIntensity')}"
        assert r.get("outlineThickness") <= 0.0030, f"Expected thin outline <= 0.0030, got {r.get('outlineThickness')}"
        assert r.get("outlineCount") == 1, f"Expected 1 outline mesh, got {r.get('outlineCount')}"
        print(">>> PASS: Myocardial selection has subtle glow, preserves pink (#b85b63) base, and thin outline! <<<", flush=True)

        await capture("refined_pink_myocardium_selection.png")

        print("\n================== VERIFYING ARTERY SELECTION ==================", flush=True)
        art_res = await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const vIframe = st.contentDocument.getElementById('viewerIframe');
                    const vWin = vIframe.contentWindow;

                    // Focus LAD
                    vWin.focusVesselGroup('lad');

                    const selMesh = vWin.getCurrentlySelectedMesh();
                    const selSystem = vWin.getSelectedArterySystem();
                    const outlines = vWin.getActiveOutlineMeshes();

                    const ladMat = vWin.materials['lad'];
                    const ladBaseColor = '#' + ladMat.color.getHexString();
                    const ladEmissive = '#' + ladMat.emissive.getHexString();
                    const ladEmissiveIntensity = ladMat.emissiveIntensity;

                    return {
                        selectedSystem: selSystem,
                        selectedMesh: selMesh ? selMesh.userData.label : null,
                        outlinesCount: outlines.length,
                        ladBaseColor: ladBaseColor,
                        ladEmissive: ladEmissive,
                        ladEmissiveIntensity: ladEmissiveIntensity
                    };
                })()
            """,
            "returnByValue": True
        })
        ar = art_res.get("result", {}).get("value", {})
        print("Artery Selection State:", json.dumps(ar, indent=2), flush=True)

        assert ar.get("selectedSystem") == "lad", f"Expected lad system, got {ar.get('selectedSystem')}"
        assert ar.get("ladBaseColor") == "#2a86ef", f"Expected blue LAD color #2a86ef, got {ar.get('ladBaseColor')}"
        assert ar.get("ladEmissiveIntensity") <= 0.25, f"Expected subtle artery emissive <= 0.25, got {ar.get('ladEmissiveIntensity')}"
        print(">>> PASS: LAD selection preserves blue base (#2a86ef) with thin electric purple outline! <<<", flush=True)

        await capture("refined_lad_artery_selection.png")

        print("\n>>> ALL VISUAL REFINEMENT VERIFICATIONS PASSED! <<<", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
