# Script to update Results & Analysis Screen in cardiovision_exact_dashboard.html
import re

html_path = "cardiovision_exact_dashboard.html"
with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add CSS for Results & Analysis Screen components
css_marker = ".patientSummaryCard{background:#f8fbff;border:1px solid #d4e4f7;border-radius:10px;padding:12px 16px;margin-bottom:16px;box-shadow:0 1px 4px rgba(15,44,89,0.04);}"

new_css = """.patientSummaryCard{background:#f8fbff;border:1px solid #d4e4f7;border-radius:10px;padding:12px 16px;margin-bottom:16px;box-shadow:0 1px 4px rgba(15,44,89,0.04);}

/* Results & Analysis Screen Enhancements */
.resStaleBanner {
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-left: 4px solid #f59e0b;
  border-radius: 8px;
  padding: 10px 16px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  font-weight: 650;
  color: #92400e;
}
.resStaleBanner svg { width: 18px; height: 18px; color: #d97706; flex-shrink: 0; }

.resCardsGrid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}
.resPredCard {
  background: white;
  border: 1px solid #d9e5f2;
  border-radius: 12px;
  padding: 16px 20px;
  box-shadow: 0 2px 8px rgba(20,52,95,.05);
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  position: relative;
  overflow: hidden;
}
.resPredCard:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(20,52,95,.08);
}
.resPredCard::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
}
.resPredCard.cad::before { background: #ff4054; }
.resPredCard.lad::before { background: #2a86ef; }
.resPredCard.lcx::before { background: #0fb77d; }
.resPredCard.rca::before { background: #ff9900; }

.resCardHeader {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.resVesselInfo {
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.resVesselTag {
  font-size: 10.5px;
  font-weight: 750;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 2px 7px;
  border-radius: 4px;
  width: fit-content;
}
.resVesselTag.cad { background: #ffe6e8; color: #d91b2f; }
.resVesselTag.lad { background: #e3effe; color: #166cd9; }
.resVesselTag.lcx { background: #e0f6ee; color: #088a5c; }
.resVesselTag.rca { background: #fff2df; color: #c86f00; }

.resVesselTitle {
  font-size: 16px;
  font-weight: 800;
  color: #0b2b5b;
  margin: 2px 0 0;
}
.resModelSub {
  font-size: 11.5px;
  color: #627d9f;
}
.resModelSub code {
  font-size: 11px;
  background: #f0f4f9;
  padding: 1px 5px;
  border-radius: 3px;
  color: #1759e8;
}

/* Circular Progress Indicator */
.resCircleWrap {
  position: relative;
  width: 68px;
  height: 68px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.resCircleSvg {
  width: 68px;
  height: 68px;
  transform: rotate(-90deg);
}
.resCircleBg {
  fill: none;
  stroke: #eaf1fa;
  stroke-width: 6;
}
.resCircleBar {
  fill: none;
  stroke-width: 6;
  stroke-linecap: round;
  transition: stroke-dashoffset 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
.resCircleBar.cad { stroke: #ff4054; }
.resCircleBar.lad { stroke: #2a86ef; }
.resCircleBar.lcx { stroke: #0fb77d; }
.resCircleBar.rca { stroke: #ff9900; }
.resCirclePct {
  position: absolute;
  font-size: 13.5px;
  font-weight: 800;
  color: #0b2b5b;
}

.resCardBody {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: #f8fafc;
  border: 1px solid #e7f0fa;
  border-radius: 8px;
  padding: 10px 14px;
}
.resMetricRow {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  font-size: 12.5px;
}
.resMetricLabel {
  color: #557092;
  font-weight: 600;
}
.resClassBadge {
  font-size: 12px;
  font-weight: 750;
  padding: 2px 9px;
  border-radius: 5px;
}
.resClassBadge.cad { background: #fee2e2; color: #b91c1c; }
.resClassBadge.lad { background: #dbeafe; color: #1d4ed8; }
.resClassBadge.lcx { background: #dcfce7; color: #15803d; }
.resClassBadge.rca { background: #ffedd5; color: #c2410c; }
.resClassBadge.normal { background: #f0fdf4; color: #166534; }
.resClassBadge.awaiting { background: #f1f5f9; color: #64748b; }

.resTierBadge {
  font-size: 11.5px;
  font-weight: 700;
  padding: 2.5px 8.5px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.resTierBadge.tierLow { background: #e8faf3; color: #088a50; border: 1px solid #b7ecd4; }
.resTierBadge.tierModerate { background: #fff7ea; color: #b86e00; border: 1px solid #fedbb0; }
.resTierBadge.tierHigh { background: #fff0f2; color: #cf172a; border: 1px solid #ffccd2; }
.resTierBadge.tierAwaiting { background: #f1f5f9; color: #64748b; border: 1px solid #e2e8f0; }

.resCardFooter {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #64748b;
  font-weight: 500;
  border-top: 1px dashed #e5edf5;
  padding-top: 8px;
}
.resCardFooter svg {
  width: 13px;
  height: 13px;
  color: #94a3b8;
  flex-shrink: 0;
}

/* Comparison Bar Chart Card */
.resChartCard {
  padding: 20px 24px;
  margin-bottom: 20px;
}
.resChartHeader {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 18px;
  border-bottom: 1px solid #e5edf5;
  padding-bottom: 12px;
}
.resSectionTitle {
  font-size: 18px;
  font-weight: 800;
  color: #0b2b5b;
  margin: 0;
}
.resSectionSub {
  font-size: 12.5px;
  color: #557092;
  margin: 4px 0 0;
}
.resChartLegend {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 14px;
  font-size: 12px;
  font-weight: 650;
  color: #3b5a82;
}
.legendItem {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.legendDot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.legendDot.cad { background: #ff4054; }
.legendDot.lad { background: #2a86ef; }
.legendDot.lcx { background: #0fb77d; }
.legendDot.rca { background: #ff9900; }

.resChartContainer {
  display: flex;
  align-items: flex-end;
  height: 220px;
  position: relative;
  padding-left: 48px;
  margin-top: 10px;
  margin-bottom: 10px;
}
.chartYAxis {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 30px;
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  pointer-events: none;
}
.yTick {
  display: flex;
  align-items: center;
  width: 100%;
  font-size: 11px;
  font-weight: 600;
  color: #718ba6;
}
.yTick span {
  width: 42px;
  text-align: right;
  padding-right: 8px;
}
.gridLine {
  flex: 1;
  height: 1px;
  background: #e6eef7;
}
.gridLine.threshold {
  background: #d0e0f3;
  border-top: 1px dashed #b7cde6;
}
.gridLine.zero {
  background: #cbdde9;
  height: 2px;
}

.chartBarsArea {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  width: 100%;
  height: 100%;
  padding-bottom: 30px;
  z-index: 2;
}
.chartBarCol {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 20%;
  max-width: 90px;
  height: 100%;
  position: relative;
}
.barTrack {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: center;
  position: relative;
}
.barValueLabel {
  font-size: 13px;
  font-weight: 800;
  margin-bottom: 6px;
  transition: all 0.3s ease;
}
.barValueLabel.cad { color: #ff4054; }
.barValueLabel.lad { color: #2a86ef; }
.barValueLabel.lcx { color: #0fb77d; }
.barValueLabel.rca { color: #ff9900; }

.barFill {
  width: 100%;
  max-width: 60px;
  border-radius: 8px 8px 0 0;
  transition: height 0.6s cubic-bezier(0.16, 1, 0.3, 1);
  min-height: 4px;
}
.barFill.cad { background: linear-gradient(180deg, #ff4054, #e62338); box-shadow: 0 4px 12px rgba(255,64,84,0.25); }
.barFill.lad { background: linear-gradient(180deg, #2a86ef, #146ed9); box-shadow: 0 4px 12px rgba(42,134,239,0.25); }
.barFill.lcx { background: linear-gradient(180deg, #0fb77d, #089464); box-shadow: 0 4px 12px rgba(15,183,125,0.25); }
.barFill.rca { background: linear-gradient(180deg, #ff9900, #de8100); box-shadow: 0 4px 12px rgba(255,153,0,0.25); }

.barXLabel {
  position: absolute;
  bottom: -28px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  font-size: 12px;
  color: #0b2b5b;
}
.barXLabel b { font-weight: 800; }
.barXLabel span { font-size: 10.5px; color: #627d9f; font-weight: 600; }

.chartNote {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 11.5px;
  color: #627d9f;
  margin-top: 26px;
  padding-top: 10px;
  border-top: 1px dashed #e2ebf5;
}
.chartNote svg { width: 14px; height: 14px; color: #1759e8; flex-shrink: 0; }

/* Performance Table Card */
.perfTableCard {
  padding: 20px 24px;
  margin-bottom: 20px;
}
.perfTable {
  width: 100%;
  border-collapse: collapse;
  margin-top: 14px;
  margin-bottom: 12px;
  font-size: 13px;
}
.perfTable th {
  background: #f0f6fc;
  color: #0e366e;
  padding: 10px 14px;
  font-weight: 750;
  border-bottom: 2px solid #d2e1f2;
  text-align: left;
}
.perfTable td {
  padding: 10px 14px;
  border-bottom: 1px solid #e7f0f8;
  color: #1c3e6b;
}
.perfTable tr:hover td {
  background: #f8fbff;
}
.cautionNotice {
  background: #fffbeb;
  border-left: 4px solid #f59e0b;
  border-radius: 6px;
  padding: 11px 16px;
  font-size: 12.5px;
  color: #92400e;
  display: flex;
  align-items: center;
  gap: 9px;
  margin-top: 10px;
}
.cautionNotice svg {
  width: 16px;
  height: 16px;
  color: #d97706;
  flex-shrink: 0;
}

/* Understanding Prediction (Explainability) */
.explainCard {
  padding: 20px 24px;
  margin-bottom: 20px;
}
.explainGrid {
  display: grid;
  grid-template-columns: 1.15fr 1fr;
  gap: 20px;
  margin-top: 14px;
}
.explainCol {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.explainBox {
  background: #f8fbff;
  border: 1px solid #d9e7f5;
  border-radius: 8px;
  padding: 14px 16px;
  font-size: 12.5px;
  color: #234470;
  line-height: 1.55;
}
.explainBox ul {
  margin: 6px 0 0;
  padding-left: 18px;
}
.explainBox li {
  margin-bottom: 4px;
}
.explainStatusBox {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.explainStatusTitle {
  font-size: 13.5px;
  font-weight: 750;
  color: #334155;
  display: flex;
  align-items: center;
  gap: 8px;
}
.explainStatusTitle svg { width: 17px; height: 17px; color: #64748b; }
.explainStatusDesc {
  font-size: 12px;
  color: #64748b;
  line-height: 1.5;
}

@media (max-width: 900px) {
  .resCardsGrid { grid-template-columns: 1fr; }
  .explainGrid { grid-template-columns: 1fr; }
}"""

if css_marker in content:
    content = content.replace(css_marker, new_css, 1)
    print("1. CSS added successfully.")
else:
    print("ERROR: css_marker not found.")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Part 1 finished.")
