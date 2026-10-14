import asyncio, json, urllib.request, websockets, base64, time, os

ARTIFACT_DIR = r"C:\Users\hario\.gemini\antigravity-ide\brain\8cd09337-1c91-438d-aacf-249a561d03c7"

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
                r = json.loads(await ws.recv())
                if r.get("id") == cid: return r.get("result", {})

        async def capture(name):
            await asyncio.sleep(0.3)
            shot = await call("Page.captureScreenshot", {"format": "png"})
            path = os.path.join(ARTIFACT_DIR, name)
            with open(path, "wb") as f:
                f.write(base64.b64decode(shot["data"]))
            print("Saved screenshot:", path)
            return path

        # Make sure we are on 3D view
        await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const doc = st ? (st.contentDocument || st.contentWindow.document) : document;
                    if (doc.defaultView && doc.defaultView.switchNav) {
                        doc.defaultView.switchNav('viewer3d');
                    }
                })()
            """
        })
        await asyncio.sleep(1)

        # Inject unified deformation engine into viewer
        res = await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const vWin = st.contentDocument.getElementById('viewerIframe').contentWindow;
                    const THREE = vWin.THREE;

                    // Base anchor
                    const baseBox = new THREE.Box3();
                    vWin.root.children.forEach(obj => {
                        const g = obj.userData ? obj.userData.group : '';
                        if (g === 'great_vessels' || g === 'valves') baseBox.expandByObject(obj);
                    });
                    const baseCenter = baseBox.getCenter(new THREE.Vector3());

                    // Replace updateHeartbeat with Unified Continuous Deformation
                    const _tempQuat = new THREE.Quaternion();
                    const _tempScaledC = new THREE.Vector3();
                    const S_heart = new THREE.Vector3(1, 1, 1);
                    const R_heart = new THREE.Euler(0, 0, 0);
                    const D_heart = new THREE.Vector3(0, 0, 0);
                    const P_heart = new THREE.Vector3(0, 0, 0);

                    function computeAffineOffset(center, scaleVec, euler, dispVec, outVec) {
                        const q = _tempQuat.setFromEuler(euler);
                        _tempScaledC.copy(center).multiply(scaleVec);
                        _tempScaledC.applyQuaternion(q);
                        outVec.copy(center).sub(_tempScaledC).add(dispVec);
                    }

                    function evaluateCardiacCycle(phase) {
                        // Smooth asymmetric cycle: faster contraction (0 to 0.36), slower relaxation (0.36 to 1.0)
                        if (phase < 0.36) {
                            const p = phase / 0.36;
                            if (p < 0.42) {
                                return Math.pow(Math.sin((p / 0.42) * (Math.PI / 2)), 1.6);
                            } else {
                                return Math.pow(Math.cos(((p - 0.42) / 0.58) * (Math.PI / 2)), 1.6);
                            }
                        } else if (phase < 0.54) {
                            const p = (phase - 0.36) / 0.18;
                            return 0.05 * Math.sin(p * Math.PI);
                        } else {
                            return 0.0;
                        }
                    }

                    let wasRestored = false;

                    vWin.updateHeartbeat = function() {
                        const now = performance.now();
                        const dt = Math.min((now - vWin._lastHbTime || now) / 1000, 0.1);
                        vWin._lastHbTime = now;

                        const targetActivity = (vWin.heartbeatEnabled !== false) ? 1.0 : 0.0;
                        vWin.heartbeatActivity = (vWin.heartbeatActivity !== undefined) ? vWin.heartbeatActivity : 1.0;
                        vWin.heartbeatActivity += (targetActivity - vWin.heartbeatActivity) * 0.12;

                        if (vWin.heartbeatActivity <= 0.001 && targetActivity === 0.0) {
                            vWin.heartbeatActivity = 0.0;
                            if (!wasRestored) {
                                vWin.root.children.forEach(obj => {
                                    obj.position.set(0, 0, 0);
                                    obj.rotation.set(0, 0, 0);
                                    obj.scale.set(1, 1, 1);
                                });
                                vWin.root.updateMatrixWorld(true);
                                wasRestored = true;
                            }
                            return;
                        }

                        wasRestored = false;

                        const bpm = vWin.heartbeatBPM || 72;
                        const cycleDur = 60 / bpm;
                        vWin.heartbeatCyclePhase = ((vWin.heartbeatCyclePhase || 0) + dt / cycleDur) % 1.0;

                        const contraction = evaluateCardiacCycle(vWin.heartbeatCyclePhase);
                        const effV = contraction * vWin.heartbeatActivity;

                        // Subtle, natural, anatomically coordinated scale centered at the heart base:
                        // Gentle radial squeeze in X, Y and subtle longitudinal shortening toward base in Z
                        S_heart.set(
                            1.0 - 0.022 * effV,
                            1.0 - 0.025 * effV,
                            1.0 - 0.016 * effV
                        );
                        R_heart.set(
                            0.003 * effV,
                            -0.004 * effV,
                            0.007 * effV
                        );
                        D_heart.set(0, 0, 0);

                        computeAffineOffset(baseCenter, S_heart, R_heart, D_heart, P_heart);

                        // Apply the IDENTICAL transform to ALL 106 meshes together
                        vWin.root.children.forEach(obj => {
                            obj.scale.copy(S_heart);
                            obj.rotation.copy(R_heart);
                            obj.position.copy(P_heart);
                        });

                        vWin.root.updateMatrixWorld(true);

                        // Pulse dot
                        const vDoc = st.contentDocument.getElementById('viewerIframe').contentDocument;
                        const dot = vDoc.querySelector('#heartbeatPulseDot');
                        if (dot && vWin.heartbeatActivity > 0.01) {
                            const scale = 1.0 + 0.35 * effV;
                            dot.style.transform = `scale(${scale.toFixed(3)})`;
                            dot.style.boxShadow = `0 0 ${6 + 8 * effV}px rgba(239, 68, 68, ${0.4 + 0.6 * effV})`;
                        }
                    };

                    return { success: true, baseCenter };
                })()
            """,
            "returnByValue": True
        })
        print("Injected test engine:", json.dumps(res, indent=2))

        # Inspect anterior view during contraction
        await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const vWin = st.contentDocument.getElementById('viewerIframe').contentWindow;
                    vWin.setView('front', false);
                })()
            """
        })
        await asyncio.sleep(0.5)
        await capture("unified_heartbeat_anterior.png")

        # Inspect posterior view during contraction
        await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const vWin = st.contentDocument.getElementById('viewerIframe').contentWindow;
                    vWin.setView('back', false);
                })()
            """
        })
        await asyncio.sleep(0.5)
        await capture("unified_heartbeat_posterior.png")

        # Inspect left lateral view during contraction
        await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const vWin = st.contentDocument.getElementById('viewerIframe').contentWindow;
                    vWin.setView('left', false);
                })()
            """
        })
        await asyncio.sleep(0.5)
        await capture("unified_heartbeat_left_lat.png")

        # Inspect right lateral view during contraction
        await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const vWin = st.contentDocument.getElementById('viewerIframe').contentWindow;
                    vWin.setView('right', false);
                })()
            """
        })
        await asyncio.sleep(0.5)
        await capture("unified_heartbeat_right_lat.png")

        # Reset perspective
        await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const vWin = st.contentDocument.getElementById('viewerIframe').contentWindow;
                    vWin.setView('front', false);
                })()
            """
        })

if __name__ == '__main__':
    asyncio.run(main())
