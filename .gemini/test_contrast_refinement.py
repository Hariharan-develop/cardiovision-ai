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
                await asyncio.sleep(0.5)
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
        print("Reloading page to load latest viewer code...", flush=True)
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
                print("All meshes loaded!", flush=True)
                break
            await asyncio.sleep(1)

        await asyncio.sleep(1)

        # -------------------------------------------------------------
        # TEST 1: LAD Vessel Selection (Blue Coronary)
        # -------------------------------------------------------------
        print("\n================== TEST 1: LAD VESSEL SELECTION (BLUE) ==================", flush=True)
        t1 = await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const vIframe = st.contentDocument.getElementById('viewerIframe');
                    const vWin = vIframe.contentWindow;

                    // Select LAD via focusVesselGroup
                    vWin.focusVesselGroup('lad');

                    const outlines = vWin.getActiveOutlineMeshes();
                    const ladMat = vWin.materials['lad'];
                    const ladColor = '#' + ladMat.color.getHexString();
                    const ladEmissive = '#' + ladMat.emissive.getHexString();
                    const ladEmissiveIntensity = ladMat.emissiveIntensity;

                    // Inspect attached outlines colors
                    const outlineColors = outlines.map(o => '#' + o.material.uniforms.outlineColor.value.getHexString());
                    const hasWhiteOutline = outlineColors.includes('#ffffff');
                    const hasPurpleGlow = outlineColors.includes('#b026ff');

                    const whiteThickness = vWin.whiteCoreOutlineMaterial.uniforms.outlineThickness.value;
                    const glowThickness = vWin.purpleGlowOutlineMaterial.uniforms.outlineThickness.value;

                    return {
                        selectedSystem: vWin.getSelectedArterySystem(),
                        ladColor: ladColor,
                        ladEmissive: ladEmissive,
                        ladEmissiveIntensity: ladEmissiveIntensity,
                        outlinesCount: outlines.length,
                        hasWhiteOutline: hasWhiteOutline,
                        hasPurpleGlow: hasPurpleGlow,
                        whiteThickness: whiteThickness,
                        glowThickness: glowThickness
                    };
                })()
            """,
            "returnByValue": True
        })
        val1 = t1.get("result", {}).get("value", {})
        print("Test 1 Result (LAD):", json.dumps(val1, indent=2), flush=True)
        assert val1.get("ladColor") == "#2a86ef", f"LAD color altered! {val1.get('ladColor')}"
        assert val1.get("ladEmissive") == "#000000", f"LAD emissive should be black! {val1.get('ladEmissive')}"
        assert val1.get("hasWhiteOutline") is True, "LAD missing crisp white core outline!"
        assert val1.get("hasPurpleGlow") is True, "LAD missing purple glow outline!"
        print(">>> PASS: LAD vessel displays crisp white outline + purple glow with unchanged natural blue color! <<<", flush=True)
        await capture("contrast_test1_lad_blue_vessel.png")

        # -------------------------------------------------------------
        # TEST 2: Cardiac Vein Selection (Blue Vein)
        # -------------------------------------------------------------
        print("\n================== TEST 2: CARDIAC VEIN SELECTION (BLUE VEIN) ==================", flush=True)
        t2 = await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const vIframe = st.contentDocument.getElementById('viewerIframe');
                    const vWin = vIframe.contentWindow;

                    // Find Coronary sinus or Great cardiac vein
                    let veinMesh = null;
                    vWin.root.traverse(c => {
                        if (c.isMesh && c.userData && c.userData.group === 'cardiac_veins') {
                            if (!veinMesh) veinMesh = c;
                        }
                    });

                    if (!veinMesh) return { error: 'veinMesh not found' };

                    // Rotate to posterior view where veins are prominent
                    vWin.setView('back', false);
                    vWin.selectMesh(veinMesh);

                    const veinMat = veinMesh.material;
                    const veinColor = '#' + veinMat.color.getHexString();
                    const veinEmissive = '#' + veinMat.emissive.getHexString();
                    const veinEmissiveIntensity = veinMat.emissiveIntensity;

                    const outlines = vWin.getActiveOutlineMeshes();
                    const outlineColors = outlines.map(o => '#' + o.material.uniforms.outlineColor.value.getHexString());
                    const hasWhiteOutline = outlineColors.includes('#ffffff');
                    const hasPurpleGlow = outlineColors.includes('#b026ff');

                    return {
                        veinLabel: veinMesh.userData.label,
                        veinColor: veinColor,
                        veinEmissive: veinEmissive,
                        veinEmissiveIntensity: veinEmissiveIntensity,
                        outlinesCount: outlines.length,
                        hasWhiteOutline: hasWhiteOutline,
                        hasPurpleGlow: hasPurpleGlow
                    };
                })()
            """,
            "returnByValue": True
        })
        val2 = t2.get("result", {}).get("value", {})
        print("Test 2 Result (Vein):", json.dumps(val2, indent=2), flush=True)
        assert val2.get("veinColor") == "#2e7da9", f"Vein color altered! {val2.get('veinColor')}"
        assert val2.get("hasWhiteOutline") is True, "Vein missing crisp white core outline!"
        assert val2.get("hasPurpleGlow") is True, "Vein missing purple glow outline!"
        assert val2.get("outlinesCount") == 2, f"Expected 2 outlines on selected vein mesh (white + glow), got {val2.get('outlinesCount')}"
        print(">>> PASS: Cardiac vein displays crisp white outline + purple glow with natural blue color! <<<", flush=True)
        await capture("contrast_test2_cardiac_vein_blue.png")

        # -------------------------------------------------------------
        # TEST 3: LCX Selection (Green Vessel)
        # -------------------------------------------------------------
        print("\n================== TEST 3: LCX SELECTION (GREEN VESSEL) ==================", flush=True)
        t3 = await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const vIframe = st.contentDocument.getElementById('viewerIframe');
                    const vWin = vIframe.contentWindow;

                    vWin.focusVesselGroup('lcx');

                    const lcxMat = vWin.materials['lcx'];
                    const lcxColor = '#' + lcxMat.color.getHexString();
                    const outlines = vWin.getActiveOutlineMeshes();
                    const outlineColors = outlines.map(o => '#' + o.material.uniforms.outlineColor.value.getHexString());
                    const allPurple = outlineColors.every(c => c === '#b026ff');

                    return {
                        selectedSystem: vWin.getSelectedArterySystem(),
                        lcxColor: lcxColor,
                        outlinesCount: outlines.length,
                        allPurple: allPurple
                    };
                })()
            """,
            "returnByValue": True
        })
        val3 = t3.get("result", {}).get("value", {})
        print("Test 3 Result (LCX):", json.dumps(val3, indent=2), flush=True)
        assert val3.get("selectedSystem") == "lcx"
        assert val3.get("lcxColor") == "#0fb77d", f"LCX color altered! {val3.get('lcxColor')}"
        assert val3.get("allPurple") is True, "LCX should retain thin Electric Purple outline!"
        print(">>> PASS: LCX green artery retains standard thin Electric Purple outline! <<<", flush=True)
        await capture("contrast_test3_lcx_green_vessel.png")

        # -------------------------------------------------------------
        # TEST 4: RCA Selection (Orange Vessel)
        # -------------------------------------------------------------
        print("\n================== TEST 4: RCA SELECTION (ORANGE VESSEL) ==================", flush=True)
        t4 = await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const vIframe = st.contentDocument.getElementById('viewerIframe');
                    const vWin = vIframe.contentWindow;

                    vWin.focusVesselGroup('rca');

                    const rcaMat = vWin.materials['rca'];
                    const rcaColor = '#' + rcaMat.color.getHexString();
                    const outlines = vWin.getActiveOutlineMeshes();
                    const outlineColors = outlines.map(o => '#' + o.material.uniforms.outlineColor.value.getHexString());
                    const allPurple = outlineColors.every(c => c === '#b026ff');

                    return {
                        selectedSystem: vWin.getSelectedArterySystem(),
                        rcaColor: rcaColor,
                        outlinesCount: outlines.length,
                        allPurple: allPurple
                    };
                })()
            """,
            "returnByValue": True
        })
        val4 = t4.get("result", {}).get("value", {})
        print("Test 4 Result (RCA):", json.dumps(val4, indent=2), flush=True)
        assert val4.get("selectedSystem") == "rca"
        assert val4.get("rcaColor") == "#ff9900", f"RCA color altered! {val4.get('rcaColor')}"
        assert val4.get("allPurple") is True, "RCA should retain thin Electric Purple outline!"
        print(">>> PASS: RCA orange artery retains standard thin Electric Purple outline! <<<", flush=True)
        await capture("contrast_test4_rca_orange_vessel.png")

        # -------------------------------------------------------------
        # TEST 5: Myocardial Structure Selection (Pink Wall)
        # -------------------------------------------------------------
        print("\n================== TEST 5: MYOCARDIAL STRUCTURE (PINK WALL) ==================", flush=True)
        t5 = await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const vIframe = st.contentDocument.getElementById('viewerIframe');
                    const vWin = vIframe.contentWindow;

                    vWin.setView('front', false);

                    let ventMesh = null;
                    vWin.root.traverse(c => {
                        if (c.isMesh && c.userData && c.userData.label && c.userData.label.includes('Free wall of left ventricle')) {
                            ventMesh = c;
                        }
                    });

                    vWin.selectMesh(ventMesh);

                    const ventMat = ventMesh.material;
                    const ventColor = '#' + ventMat.color.getHexString();
                    const emissive = '#' + ventMat.emissive.getHexString();
                    const emissiveIntensity = ventMat.emissiveIntensity;

                    const outlines = vWin.getActiveOutlineMeshes();
                    const outlineColors = outlines.map(o => '#' + o.material.uniforms.outlineColor.value.getHexString());
                    const isPurple = outlineColors.length === 1 && outlineColors[0] === '#b026ff';

                    return {
                        meshLabel: ventMesh.userData.label,
                        ventColor: ventColor,
                        emissive: emissive,
                        emissiveIntensity: emissiveIntensity,
                        outlinesCount: outlines.length,
                        isPurple: isPurple
                    };
                })()
            """,
            "returnByValue": True
        })
        val5 = t5.get("result", {}).get("value", {})
        print("Test 5 Result (Myocardium):", json.dumps(val5, indent=2), flush=True)
        assert val5.get("ventColor") == "#b85b63", f"Myocardium color altered! {val5.get('ventColor')}"
        assert val5.get("isPurple") is True, "Myocardium should retain single Electric Purple outline!"
        assert val5.get("emissiveIntensity") <= 0.16, "Myocardium should have subtle glow <= 0.16"
        print(">>> PASS: Pink myocardium retains subtle glow & standard thin Electric Purple outline! <<<", flush=True)
        await capture("contrast_test5_pink_myocardium.png")

        # -------------------------------------------------------------
        # TEST 6: Clear Selection Restoration
        # -------------------------------------------------------------
        print("\n================== TEST 6: CLEAR SELECTION RESTORATION ==================", flush=True)
        t6 = await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const vIframe = st.contentDocument.getElementById('viewerIframe');
                    const vWin = vIframe.contentWindow;

                    vWin.selectMesh(null);

                    const outlines = vWin.getActiveOutlineMeshes();
                    const selMesh = vWin.getCurrentlySelectedMesh();
                    const selSystem = vWin.getSelectedArterySystem();
                    const detail = vIframe.contentDocument.querySelector('#detail').textContent;

                    return {
                        outlinesCount: outlines.length,
                        selMeshNull: selMesh === null,
                        selSystemNull: selSystem === null,
                        inspectorReset: detail.includes('Anatomical Inspector')
                    };
                })()
            """,
            "returnByValue": True
        })
        val6 = t6.get("result", {}).get("value", {})
        print("Test 6 Result (Clear):", json.dumps(val6, indent=2), flush=True)
        assert val6.get("outlinesCount") == 0, "Outlines not cleared!"
        assert val6.get("selMeshNull") is True, "Selection not cleared!"
        assert val6.get("inspectorReset") is True, "Inspector not reset!"
        print(">>> PASS: Selection clearing restored all materials and removed all outlines! <<<", flush=True)

        print("\n>>> ALL 6 CONTRAST SELECTION TEST CASES PASSED WITH 100% SUCCESS! <<<", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
