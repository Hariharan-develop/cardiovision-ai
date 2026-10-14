import asyncio, json, urllib.request, websockets, time

async def main():
    pages = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json/list").read().decode())
    target = [p for p in pages if "8501" in p.get("url", "")][0]
    print("Connecting to:", target["title"])

    async with websockets.connect(target["webSocketDebuggerUrl"]) as ws:
        msg_id = 0
        async def call(method, params=None):
            nonlocal msg_id
            msg_id += 1
            cid = msg_id
            await ws.send(json.dumps({"id": cid, "method": method, "params": params or {}}))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == cid:
                    return msg.get("result", {})

        # Switch to 3D tab
        await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const doc = st ? st.contentDocument : document;
                    const nav = Array.from(doc.querySelectorAll('.navItem')).find(el => el.textContent.includes('3D Visualization'));
                    if (nav) nav.click();
                })()
            """
        })
        await asyncio.sleep(1)

        # Inject and test heartbeat deformation prototype
        test_res = await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const vWin = st.contentDocument.getElementById('viewerIframe').contentWindow;
                    const THREE = vWin.THREE;

                    // Compute centers
                    const ventCenter = new THREE.Vector3(0.045, -0.159, -0.424);
                    const atriaCenter = new THREE.Vector3(-0.323, 0.254, -0.070);

                    const ventGroups = new Set([
                        'ventricles', 'internal_myocardium', 'conduction_system', 'cardiac_veins',
                        'left_coronary_stem', 'lad', 'lad_branches', 'lcx', 'lcx_branches', 'rca', 'rca_branches'
                    ]);
                    const atriaGroups = new Set(['atria', 'valves']);

                    // Test applying a 5% systolic contraction
                    const V = 1.0; // peak systole
                    const Sx = 1.0 - 0.038 * V;
                    const Sy = 1.0 - 0.042 * V;
                    const Sz = 1.0 - 0.024 * V;
                    const S_vent = new THREE.Vector3(Sx, Sy, Sz);
                    const R_vent = new THREE.Euler(0.006 * V, -0.008 * V, 0.020 * V);
                    const D_vent = new THREE.Vector3(0, 0, 0.015 * V);

                    // Compute obj position: C - R*(S*C) + D
                    // We can use a helper function:
                    function computeOffset(C, S, euler, D) {
                        const q = new THREE.Quaternion().setFromEuler(euler);
                        const scaledC = C.clone().multiply(S);
                        const rotScaledC = scaledC.applyQuaternion(q);
                        return C.clone().sub(rotScaledC).add(D);
                    }

                    const P_vent = computeOffset(ventCenter, S_vent, R_vent, D_vent);

                    let ventCount = 0;
                    let atriaCount = 0;
                    let vesselCount = 0;

                    vWin.root.children.forEach(obj => {
                        const g = obj.userData ? obj.userData.group : '';
                        if (ventGroups.has(g)) {
                            obj.scale.copy(S_vent);
                            obj.rotation.copy(R_vent);
                            obj.position.copy(P_vent);
                            ventCount++;
                        } else if (atriaGroups.has(g)) {
                            atriaCount++;
                        } else {
                            vesselCount++;
                        }
                    });

                    vWin.root.updateMatrixWorld(true);

                    return { ventCount, atriaCount, vesselCount, P_vent };
                })()
            """,
            "returnByValue": True
        })

        print("Test result:", json.dumps(test_res, indent=2))
        await asyncio.sleep(2)

        # Reset to identity
        reset_res = await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const vWin = st.contentDocument.getElementById('viewerIframe').contentWindow;
                    vWin.root.children.forEach(obj => {
                        obj.position.set(0, 0, 0);
                        obj.rotation.set(0, 0, 0);
                        obj.scale.set(1, 1, 1);
                    });
                    vWin.root.updateMatrixWorld(true);
                    return { reset: true };
                })()
            """,
            "returnByValue": True
        })
        print("Reset result:", json.dumps(reset_res, indent=2))

if __name__ == '__main__':
    asyncio.run(main())
