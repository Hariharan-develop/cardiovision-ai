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
                await asyncio.sleep(0.4)
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
        print("Page brought to front.", flush=True)

        print("Reloading page to get latest viewer code...", flush=True)
        await call("Page.reload")
        await asyncio.sleep(3)
        await call("Page.bringToFront")

        # Ensure we are on 3D view
        await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const doc = stFrame ? stFrame.contentDocument : document;
                    const navItem = Array.from(doc.querySelectorAll('.navItem')).find(el => el.textContent && el.textContent.includes('3D Visualization'));
                    if (navItem) navItem.click();
                })()
            """
        })

        # Wait for all 106 meshes to finish loading
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
                print("All 106 meshes loaded!", flush=True)
                break
            await asyncio.sleep(1)

        await asyncio.sleep(1)

        # ---------------------------------------------------------------------
        # TEST CASE 1: Hide Atria & Auricles and Ventricles & Septa
        # ---------------------------------------------------------------------
        print("\n================== TEST 1: HIDE ATRIA & VENTRICLES ==================", flush=True)
        t1_res = await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const vDoc = st.contentDocument.getElementById('viewerIframe').contentDocument;
                    const vWin = st.contentDocument.getElementById('viewerIframe').contentWindow;

                    // Uncheck Ventricles & Septa and Atria & Auricles
                    const ventCheck = vDoc.querySelector('[data-group="ventricles"]');
                    const atriaCheck = vDoc.querySelector('[data-group="atria"]');
                    if (ventCheck) { ventCheck.checked = false; ventCheck.dispatchEvent(new Event('change')); }
                    if (atriaCheck) { atriaCheck.checked = false; atriaCheck.dispatchEvent(new Event('change')); }

                    // Check actual selectable meshes
                    const selectables = vWin.getSelectableMeshes();
                    const hasAtria = selectables.some(m => m.userData && m.userData.group === 'atria');
                    const hasVentricles = selectables.some(m => m.userData && m.userData.group === 'ventricles');

                    // Check specifically "Wall of right auricle proper"
                    let auricleMesh = null;
                    vWin.root.traverse(c => {
                        if (c.isMesh && c.userData && c.userData.label && c.userData.label.includes('right auricle')) {
                            auricleMesh = c;
                        }
                    });
                    const auricleEligible = auricleMesh ? vWin.isMeshEligibleForRaycast(auricleMesh) : false;

                    return {
                        hasAtriaInSelectables: hasAtria,
                        hasVentriclesInSelectables: hasVentricles,
                        totalSelectableCount: selectables.length,
                        auricleEligible: auricleEligible,
                        auricleVisible: auricleMesh ? auricleMesh.visible : false
                    };
                })()
            """,
            "returnByValue": True
        })
        t1_val = t1_res.get("result", {}).get("value", {})
        print("Test 1 Result:", json.dumps(t1_val, indent=2), flush=True)
        assert t1_val["hasAtriaInSelectables"] is False, "FAIL: Atria found in selectable meshes!"
        assert t1_val["hasVentriclesInSelectables"] is False, "FAIL: Ventricles found in selectable meshes!"
        assert t1_val["auricleEligible"] is False, "FAIL: Right auricle is still eligible for raycast!"
        print(">>> PASS: Atria & Ventricles are completely excluded from raycasting! <<<", flush=True)
        await capture("test1_atria_ventricles_hidden.png")

        # ---------------------------------------------------------------------
        # TEST CASE 2: Click Exposed Inner Structure (Papillary Muscle)
        # ---------------------------------------------------------------------
        print("\n================== TEST 2: SELECT EXPOSED PAPILLARY MUSCLE ==================", flush=True)
        t2_res = await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const vDoc = st.contentDocument.getElementById('viewerIframe').contentDocument;
                    const vWin = st.contentDocument.getElementById('viewerIframe').contentWindow;

                    // Find an exposed papillary muscle in internal_myocardium
                    let papMesh = null;
                    vWin.root.traverse(c => {
                        if (c.isMesh && c.userData && c.userData.group === 'internal_myocardium' && !papMesh) {
                            papMesh = c;
                        }
                    });

                    // Test raycast eligibility
                    const isEligible = vWin.isMeshEligibleForRaycast(papMesh);

                    // Select the exposed papillary muscle
                    if (papMesh) vWin.selectMesh(papMesh);

                    return {
                        meshLabel: papMesh ? papMesh.userData.label : null,
                        meshGroup: papMesh ? papMesh.userData.group : null,
                        isEligible: isEligible,
                        detailTitle: vDoc.querySelector('#detail strong') ? vDoc.querySelector('#detail strong').textContent : '',
                        detailSub: vDoc.querySelector('#detail .sublabel') ? vDoc.querySelector('#detail .sublabel').textContent : '',
                        emissive: papMesh ? '#' + papMesh.material.emissive.getHexString() : null,
                        outlinesCount: vWin.getActiveOutlineMeshes().length
                    };
                })()
            """,
            "returnByValue": True
        })
        t2_val = t2_res.get("result", {}).get("value", {})
        print("Test 2 Result:", json.dumps(t2_val, indent=2), flush=True)
        assert t2_val["isEligible"] is True, "FAIL: Papillary muscle should be eligible!"
        assert "right auricle" not in t2_val["detailTitle"].lower(), "FAIL: Auricle was selected instead of papillary muscle!"
        assert t2_val["emissive"] == "#b026ff", "FAIL: Electric purple emissive not applied!"
        assert t2_val["outlinesCount"] >= 1, "FAIL: Outline not added!"
        print(">>> PASS: Correct inner papillary muscle selected with Electric Purple highlight! <<<", flush=True)
        await capture("test2_exposed_papillary_selected.png")

        # ---------------------------------------------------------------------
        # TEST CASE 3: Enable ONLY Conduction System
        # ---------------------------------------------------------------------
        print("\n================== TEST 3: ENABLE ONLY CONDUCTION SYSTEM ==================", flush=True)
        t3_res = await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const vDoc = st.contentDocument.getElementById('viewerIframe').contentDocument;
                    const vWin = st.contentDocument.getElementById('viewerIframe').contentWindow;

                    // Uncheck all layers except conduction_system
                    vDoc.querySelectorAll('[data-group]').forEach(cb => {
                        cb.checked = (cb.dataset.group === 'conduction_system');
                        cb.dispatchEvent(new Event('change'));
                    });

                    const selectables = vWin.getSelectableMeshes();
                    const allAreConduction = selectables.every(m => m.userData && m.userData.group === 'conduction_system');

                    // Select an SA or AV node mesh
                    let saNode = null;
                    vWin.root.traverse(c => {
                        if (c.isMesh && c.userData && c.userData.group === 'conduction_system' && !saNode) {
                            saNode = c;
                        }
                    });
                    if (saNode) vWin.selectMesh(saNode);

                    return {
                        totalSelectables: selectables.length,
                        allAreConduction: allAreConduction,
                        selectedLabel: saNode ? saNode.userData.label : null,
                        detailTitle: vDoc.querySelector('#detail strong') ? vDoc.querySelector('#detail strong').textContent : '',
                        emissive: saNode ? '#' + saNode.material.emissive.getHexString() : null,
                        baseColor: saNode ? '#' + saNode.material.color.getHexString() : null,
                        outlinesCount: vWin.getActiveOutlineMeshes().length
                    };
                })()
            """,
            "returnByValue": True
        })
        t3_val = t3_res.get("result", {}).get("value", {})
        print("Test 3 Result:", json.dumps(t3_val, indent=2), flush=True)
        assert t3_val["allAreConduction"] is True, "FAIL: Non-conduction meshes found in selectables!"
        assert t3_val["emissive"] == "#b026ff", "FAIL: Conduction structure not highlighted in Electric Purple!"
        print(">>> PASS: Only conduction system selectable, correctly inspected and highlighted! <<<", flush=True)
        await capture("test3_conduction_only_selected.png")

        # ---------------------------------------------------------------------
        # TEST CASE 4: Requirement 8 - Clear selection when layer unchecked
        # ---------------------------------------------------------------------
        print("\n================== TEST 4: UNCHECK LAYER CLEARS SELECTION ==================", flush=True)
        t4_res = await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const vDoc = st.contentDocument.getElementById('viewerIframe').contentDocument;
                    const vWin = st.contentDocument.getElementById('viewerIframe').contentWindow;

                    // Uncheck conduction_system while a conduction mesh is currently selected
                    const condCheck = vDoc.querySelector('[data-group="conduction_system"]');
                    condCheck.checked = false;
                    condCheck.dispatchEvent(new Event('change'));

                    return {
                        selectedMeshIsNull: vWin.getCurrentlySelectedMesh() === null,
                        activeOutlinesCount: vWin.getActiveOutlineMeshes().length,
                        detailTitle: vDoc.querySelector('#detail strong') ? vDoc.querySelector('#detail strong').textContent : ''
                    };
                })()
            """,
            "returnByValue": True
        })
        t4_val = t4_res.get("result", {}).get("value", {})
        print("Test 4 Result:", json.dumps(t4_val, indent=2), flush=True)
        assert t4_val["selectedMeshIsNull"] is True, "FAIL: Selection was not cleared when layer was unchecked!"
        assert t4_val["activeOutlinesCount"] == 0, "FAIL: Outlines were not removed!"
        assert t4_val["detailTitle"] == "Anatomical Inspector", "FAIL: Detail card was not reset!"
        print(">>> PASS: Selection properly cleared and inspector reset when layer unchecked! <<<", flush=True)
        await capture("test4_uncheck_layer_clears_selection.png")

        # ---------------------------------------------------------------------
        # TEST CASE 5: Coronary Focus Click-Through Ghosted Myocardium
        # ---------------------------------------------------------------------
        print("\n================== TEST 5: CORONARY FOCUS CLICK-THROUGH ==================", flush=True)
        t5_res = await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const vDoc = st.contentDocument.getElementById('viewerIframe').contentDocument;
                    const vWin = st.contentDocument.getElementById('viewerIframe').contentWindow;

                    // Click Coronary Focus preset
                    vDoc.querySelector('#presetCoronary').click();

                    // Check eligibility of outer myocardium vs coronary arteries
                    let ventMesh = null;
                    let ladMesh = null;
                    vWin.root.traverse(c => {
                        if (c.isMesh && c.userData && c.userData.group === 'ventricles' && !ventMesh) ventMesh = c;
                        if (c.isMesh && c.userData && c.userData.group === 'lad' && !ladMesh) ladMesh = c;
                    });

                    const ventEligible = ventMesh ? vWin.isMeshEligibleForRaycast(ventMesh) : true;
                    const ladEligible = ladMesh ? vWin.isMeshEligibleForRaycast(ladMesh) : false;

                    return {
                        isCoronaryActive: vDoc.querySelector('#presetCoronary').classList.contains('active'),
                        ventricleMeshEligible: ventEligible,
                        ladMeshEligible: ladEligible
                    };
                })()
            """,
            "returnByValue": True
        })
        t5_val = t5_res.get("result", {}).get("value", {})
        print("Test 5 Result:", json.dumps(t5_val, indent=2), flush=True)
        assert t5_val["ventricleMeshEligible"] is False, "FAIL: Ghosted myocardium must be click-through in Coronary Focus mode!"
        assert t5_val["ladMeshEligible"] is True, "FAIL: LAD must remain selectable in Coronary Focus mode!"
        print(">>> PASS: Ghosted myocardium is click-through, arteries remain selectable! <<<", flush=True)
        await capture("test5_coronary_focus_click_through.png")

        # ---------------------------------------------------------------------
        # TEST CASE 6: Re-enable Complete Heart Mode
        # ---------------------------------------------------------------------
        print("\n================== TEST 6: RE-ENABLE COMPLETE HEART ==================", flush=True)
        t6_res = await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const vDoc = st.contentDocument.getElementById('viewerIframe').contentDocument;
                    const vWin = st.contentDocument.getElementById('viewerIframe').contentWindow;

                    // Click Complete Heart preset
                    vDoc.querySelector('#presetComplete').click();

                    let ventMesh = null;
                    vWin.root.traverse(c => {
                        if (c.isMesh && c.userData && c.userData.group === 'ventricles' && !ventMesh) ventMesh = c;
                    });

                    const ventEligible = ventMesh ? vWin.isMeshEligibleForRaycast(ventMesh) : false;

                    // Select a ventricular wall in complete mode
                    if (ventMesh) vWin.selectMesh(ventMesh);

                    return {
                        isCompleteActive: vDoc.querySelector('#presetComplete').classList.contains('active'),
                        ventricleMeshEligible: ventEligible,
                        selectedTitle: vDoc.querySelector('#detail strong') ? vDoc.querySelector('#detail strong').textContent : '',
                        outlinesCount: vWin.getActiveOutlineMeshes().length
                    };
                })()
            """,
            "returnByValue": True
        })
        t6_val = t6_res.get("result", {}).get("value", {})
        print("Test 6 Result:", json.dumps(t6_val, indent=2), flush=True)
        assert t6_val["ventricleMeshEligible"] is True, "FAIL: Ventricles should be selectable in Complete Heart mode!"
        assert t6_val["outlinesCount"] >= 1, "FAIL: Ventricle outline not added!"
        print(">>> PASS: Complete Heart mode restored normal anatomical selection! <<<", flush=True)
        await capture("test6_complete_heart_restored.png")

        print("\n>>> ALL 6 HIDDEN-LAYER RAYCASTING TEST CASES PASSED SUCCESSFULLY! <<<", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
