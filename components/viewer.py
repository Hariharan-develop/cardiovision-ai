import os
import streamlit.components.v1 as components

def render_heart_viewer(
    cad_risk: float,
    lad_risk: float,
    lcx_risk: float,
    rca_risk: float,
    cad_label: str = "CAD",
    lad_label: str = "Stenotic",
    lcx_label: str = "Stenotic",
    rca_label: str = "Stenotic",
    is_custom_pred: bool = False,
    height: int = 580,
):
    """
    Renders the interactive 3D WebGL Coronary Artery Viewer using Three.js.
    Injects model predicted probabilities and labels for CAD, LAD, LCX, and RCA.
    """
    html_path = os.path.join(os.path.dirname(__file__), "heart_viewer.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_template = f.read()

    html_content = (
        html_template
        .replace("{{CAD_RISK}}", f"{float(cad_risk):.1f}")
        .replace("{{LAD_RISK}}", f"{float(lad_risk):.1f}")
        .replace("{{LCX_RISK}}", f"{float(lcx_risk):.1f}")
        .replace("{{RCA_RISK}}", f"{float(rca_risk):.1f}")
        .replace("{{CAD_LABEL}}", str(cad_label))
        .replace("{{LAD_LABEL}}", str(lad_label))
        .replace("{{LCX_LABEL}}", str(lcx_label))
        .replace("{{RCA_LABEL}}", str(rca_label))
        .replace("{{IS_CUSTOM_PRED}}", "true" if is_custom_pred else "false")
    )

    components.html(html_content, height=height, scrolling=False)
