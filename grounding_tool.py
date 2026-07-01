"""Transmission Tower Grounding Risk Assessment Tool.

Estimates induced voltage at transmission line tower grounding systems under
lightning surge conditions, accounting for soil ionisation effects. Voltage
values are linearly interpolated from validated CDEGS electromagnetic
simulation data (Fatehah Burhannudin, "Electromagnetic Modelling Analysis of
Soil Ionisation Effects on Transmission Line Tower Grounding Performance",
UTM 2023).
"""

from datetime import datetime
from typing import Literal

SoilModel = Literal["horizontal", "uniform"]

FYP_HORIZONTAL_DATA = [
    {"radius": 0.0070, "voltage_kv": 11.6, "pct_diff": 0.0},
    {"radius": 0.0114, "voltage_kv": 11.3, "pct_diff": 2.59},
    {"radius": 0.1212, "voltage_kv": 10.6, "pct_diff": 8.62},
    {"radius": 0.2052, "voltage_kv": 10.4, "pct_diff": 10.34},
    {"radius": 0.3032, "voltage_kv": 10.2, "pct_diff": 12.07},
    {"radius": 0.4082, "voltage_kv": 10.0, "pct_diff": 13.79},
]

FYP_UNIFORM_DATA = [
    {"radius": 0.0070, "voltage_kv": 11.3, "pct_diff": 0.0},
    {"radius": 0.0114, "voltage_kv": 11.1, "pct_diff": 3.57},
    {"radius": 0.1212, "voltage_kv": 10.0, "pct_diff": 12.07},
    {"radius": 0.2052, "voltage_kv": 9.7,  "pct_diff": 14.66},
    {"radius": 0.3032, "voltage_kv": 9.4,  "pct_diff": 17.24},
    {"radius": 0.4082, "voltage_kv": 9.3,  "pct_diff": 19.83},
]

FYP_PARAMS = {
    "tower_voltage_kv": 500,
    "lightning_current_ka": 16,
    "key_frequency_hz": 50,
    "copper_resistivity": 1.67e-8,
}

SCENARIOS = [
    {"radius": 0.0070, "label": "Minimum (r=0.007m)"},
    {"radius": 0.0114, "label": "Small (r=0.0114m)"},
    {"radius": 0.1212, "label": "Medium (r=0.1212m)"},
    {"radius": 0.2052, "label": "Large (r=0.2052m)"},
    {"radius": 0.3032, "label": "Larger (r=0.3032m)"},
    {"radius": 0.4082, "label": "Maximum (r=0.4082m)"},
]

# Ordered highest-to-lowest; first threshold exceeded by the ratio wins.
RISK_THRESHOLDS = (
    (0.025, "CRITICAL", "#d83b01"),
    (0.020, "HIGH", "#ff8c00"),
    (0.018, "MODERATE", "#b8860b"),
)
DEFAULT_RISK = ("LOW", "#107c10")


def _data_for_soil(soil_model: SoilModel) -> list[dict]:
    return FYP_HORIZONTAL_DATA if soil_model == "horizontal" else FYP_UNIFORM_DATA


def estimate_voltage(radius_m: float, soil_model: SoilModel) -> float:
    """Linearly interpolate induced voltage (kV) for a given conductor radius.

    Radii outside the validated range are clamped to the nearest endpoint.
    """
    data = _data_for_soil(soil_model)
    if radius_m <= data[0]["radius"]:
        return data[0]["voltage_kv"]
    if radius_m >= data[-1]["radius"]:
        return data[-1]["voltage_kv"]
    for point, next_point in zip(data, data[1:]):
        r1, r2 = point["radius"], next_point["radius"]
        if r1 <= radius_m <= r2:
            t = (radius_m - r1) / (r2 - r1)
            v1, v2 = point["voltage_kv"], next_point["voltage_kv"]
            return round(v1 + t * (v2 - v1), 2)
    return data[-1]["voltage_kv"]


def voltage_reduction(radius_m: float, soil_model: SoilModel) -> tuple[float, float]:
    """Return (reduction_kv, reduction_pct) relative to the baseline (smallest radius)."""
    base = _data_for_soil(soil_model)[0]["voltage_kv"]
    estimated = estimate_voltage(radius_m, soil_model)
    red_kv = round(base - estimated, 2)
    red_pct = round((red_kv / base) * 100, 2)
    return red_kv, red_pct


def assess_risk(voltage_kv: float, tower_kv: float) -> tuple[str, str]:
    """Classify risk level and display colour from the induced-voltage-to-tower-rating ratio."""
    ratio = voltage_kv / tower_kv
    for threshold, level, color in RISK_THRESHOLDS:
        if ratio > threshold:
            return level, color
    return DEFAULT_RISK


def get_recommendations(risk: str, radius_m: float, soil_model: SoilModel) -> list[str]:
    """Build engineering recommendations for a scenario's risk level and soil model."""
    recs = []
    if risk == "CRITICAL":
        recs.append("IMMEDIATE ACTION: Conductor radius critically small. Increase radius to reduce induced voltage.")
        recs.append("Review grounding system design against IEEE 80-2013 and CIGRE guidelines.")
        recs.append("Consider adding additional grounding electrodes or ground rods.")
    elif risk == "HIGH":
        recs.append("Increase ground conductor radius to improve lightning surge performance.")
        recs.append("Conduct soil resistivity measurement to validate soil model assumptions.")
    elif risk == "MODERATE":
        recs.append("System within acceptable range. Monitor conductor condition regularly.")
        recs.append("Consider radius increase if soil conditions change significantly.")
    else:
        recs.append("Grounding system performance is satisfactory for current conditions.")
        recs.append("Maintain regular preventive maintenance schedule.")

    if soil_model == "uniform":
        recs.append("Note: Uniform soil model may oversimplify ionisation effects. Consider horizontal model for layered soils.")
    else:
        recs.append("Horizontal soil model accounts for depth-varying properties — recommended for layered soil conditions.")

    if radius_m > FYP_HORIZONTAL_DATA[-1]["radius"]:
        recs.append("WARNING: Radius exceeds validated research range. Results are extrapolated.")

    return recs


def run_assessment() -> list[dict]:
    """Evaluate every scenario/soil-model combination and return the results."""
    results = []
    for scenario in SCENARIOS:
        for soil in ("horizontal", "uniform"):
            voltage = estimate_voltage(scenario["radius"], soil)
            red_kv, red_pct = voltage_reduction(scenario["radius"], soil)
            risk, color = assess_risk(voltage, FYP_PARAMS["tower_voltage_kv"])
            results.append({
                "label": scenario["label"],
                "radius": scenario["radius"],
                "soil": soil,
                "voltage_kv": voltage,
                "reduction_kv": red_kv,
                "reduction_pct": red_pct,
                "risk": risk,
                "color": color,
                "recommendations": get_recommendations(risk, scenario["radius"], soil),
            })
            print(f"{scenario['label']} | {soil.capitalize()} | Voltage: {voltage} kV | Reduction: {red_pct}% | Risk: {risk}")
    return results


def _benchmark_table_rows(data: list[dict]) -> str:
    rows = ""
    for d in data:
        effect = "Baseline (no ionisation)" if d["pct_diff"] == 0 else f"{d['pct_diff']}% reduction from ionisation"
        rows += f"<tr><td>{d['radius']}</td><td>{d['voltage_kv']}</td><td>{d['pct_diff']}%</td><td>{effect}</td></tr>"
    return rows


def _results_table_rows(results: list[dict]) -> str:
    rows = ""
    for r in results:
        rows += f"""<tr>
<td>{r['label']}</td><td>{r['radius']}</td><td>{r['soil'].capitalize()}</td>
<td>{r['voltage_kv']} kV</td><td>{r['reduction_pct']}% ({r['reduction_kv']} kV)</td>
<td class="{r['risk']}">{r['risk']}</td>
</tr>"""
    return rows


def _recommendations_section(results: list[dict]) -> str:
    section = "<h2>Engineering Recommendations</h2>"
    seen = set()
    for r in results:
        key = f"{r['label']}-{r['soil']}"
        if key in seen:
            continue
        seen.add(key)
        section += f"<h3>{r['label']} | {r['soil'].capitalize()} Soil | <span class='{r['risk']}'>{r['risk']}</span></h3>"
        for rec in r["recommendations"]:
            section += f'<div class="rec {r["risk"]}">{rec}</div>'
    return section


def build_report_html(results: list[dict], now: datetime) -> str:
    """Render the full client-ready HTML report for a set of assessment results."""
    timestamp = now.strftime("%Y-%m-%d %H:%M")
    report_date = now.strftime("%B %d, %Y")

    critical = sum(1 for r in results if r["risk"] == "CRITICAL")
    high = sum(1 for r in results if r["risk"] == "HIGH")
    moderate = sum(1 for r in results if r["risk"] == "MODERATE")
    low = sum(1 for r in results if r["risk"] == "LOW")

    return f"""<!DOCTYPE html>
<html>
<head>
<title>Transmission Tower Grounding Risk Assessment</title>
<style>
body{{font-family:Arial;margin:auto;max-width:1100px;padding:40px;color:#333}}
h1{{color:#1a1a2e;border-bottom:3px solid #1a1a2e;padding-bottom:10px}}
h2{{color:#1a1a2e;margin-top:30px}}
h3{{color:#333;margin-top:20px}}
.meta{{color:#666;font-size:13px;line-height:1.8;margin-bottom:20px}}
.info{{background:#f0f8ff;border-left:4px solid #0078d4;padding:15px;margin:15px 0;border-radius:0 5px 5px 0}}
table{{border-collapse:collapse;width:100%;margin:15px 0;font-size:13px}}
th{{background:#1a1a2e;color:white;padding:10px;text-align:left}}
td{{padding:8px 10px;border-bottom:1px solid #eee}}
tr:nth-child(even){{background:#f9f9f9}}
.CRITICAL{{color:#d83b01;font-weight:bold}}
.HIGH{{color:#ff8c00;font-weight:bold}}
.MODERATE{{color:#b8860b;font-weight:bold}}
.LOW{{color:#107c10;font-weight:bold}}
.rec{{padding:10px;margin:6px 0;border-radius:0 5px 5px 0;font-size:13px}}
.rec.CRITICAL{{background:#fff4f0;border-left:4px solid #d83b01}}
.rec.HIGH{{background:#fff8f0;border-left:4px solid #ff8c00}}
.rec.MODERATE{{background:#fffbf0;border-left:4px solid #b8860b}}
.rec.LOW{{background:#f0fff4;border-left:4px solid #107c10}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin:20px 0}}
.card{{padding:15px;border-radius:8px;text-align:center;color:white}}
.card h3{{margin:0;font-size:28px}}
.card p{{margin:5px 0 0;font-size:13px}}
.footer{{margin-top:40px;font-size:12px;color:#666;border-top:1px solid #ddd;padding-top:15px}}
</style>
</head>
<body>
<h1>Transmission Tower Grounding Risk Assessment Report</h1>
<div class="meta">
<strong>Tool:</strong> Grounding Risk Assessment Tool v1.0<br>
<strong>Research Basis:</strong> Electromagnetic Modelling Analysis of Soil Ionisation Effects on Transmission Line Tower Grounding Performance — Fatehah Burhannudin, UTM 2023<br>
<strong>Tower Rating:</strong> 500 kV &nbsp;|&nbsp; <strong>Lightning Current:</strong> 16 kA &nbsp;|&nbsp; <strong>Key Frequency:</strong> 50 Hz<br>
<strong>Generated:</strong> {report_date} at {timestamp} &nbsp;|&nbsp; <strong>Prepared by:</strong> Fatehah Burhannudin
</div>

<div class="info">
<strong>About This Tool:</strong> Estimates induced voltage at transmission line tower grounding systems under lightning surge conditions, accounting for soil ionisation effects. Results are interpolated from validated CDEGS electromagnetic simulation data from the author's FYP research. Soil ionisation is modelled by varying ground conductor radius as recommended by CIGRE and IEEE Working Groups.
</div>

<h2>FYP Research Benchmark Data — Horizontal Soil Model</h2>
<table>
<tr><th>Conductor Radius (m)</th><th>Induced Voltage (kV)</th><th>Voltage Reduction (%)</th><th>Soil Ionisation Effect</th></tr>
{_benchmark_table_rows(FYP_HORIZONTAL_DATA)}
</table>

<h2>FYP Research Benchmark Data — Uniform Soil Model</h2>
<table>
<tr><th>Conductor Radius (m)</th><th>Induced Voltage (kV)</th><th>Voltage Reduction (%)</th><th>Soil Ionisation Effect</th></tr>
{_benchmark_table_rows(FYP_UNIFORM_DATA)}
</table>

<h2>Risk Assessment Summary</h2>
<div class="grid">
<div class="card" style="background:#d83b01"><h3>{critical}</h3><p>Critical</p></div>
<div class="card" style="background:#ff8c00"><h3>{high}</h3><p>High</p></div>
<div class="card" style="background:#b8860b"><h3>{moderate}</h3><p>Moderate</p></div>
<div class="card" style="background:#107c10"><h3>{low}</h3><p>Low</p></div>
</div>

<h2>Detailed Assessment Results</h2>
<table>
<tr><th>Scenario</th><th>Radius (m)</th><th>Soil Model</th><th>Induced Voltage (kV)</th><th>Voltage Reduction</th><th>Risk Level</th></tr>
{_results_table_rows(results)}
</table>

{_recommendations_section(results)}

<h2>Key Research Findings</h2>
<div class="info">
<strong>Finding 1:</strong> Soil ionisation reduces induced voltage by 2.59% to 13.79% for horizontal soil conditions as conductor radius increases from 0.007m to 0.4082m.<br><br>
<strong>Finding 2:</strong> Uniform soil shows higher reduction (3.57% to 19.83%) but oversimplifies ionisation — horizontal model is more accurate for real-world layered conditions.<br><br>
<strong>Finding 3:</strong> Increasing ground conductor radius is an effective mitigation strategy — larger radius accounts for soil ionisation and reduces lightning surge voltage.<br><br>
<strong>Finding 4:</strong> Validated against experimental data from benchmarking reference — both waveform shape and magnitude confirmed consistent with literature.
</div>

<h2>Standards & Methodology Reference</h2>
<table>
<tr><th>Tool / Standard</th><th>Application in This Research</th></tr>
<tr><td>CDEGS HIFREQ-SESCAD Module</td><td>Electromagnetic field simulation for grounding system analysis</td></tr>
<tr><td>FFTSES / IFFTSES Module</td><td>Fast Fourier Transform analysis of lightning impulse waveforms</td></tr>
<tr><td>CIGRE Guidelines</td><td>Soil ionisation modelling methodology</td></tr>
<tr><td>IEEE Working Group Recommendations</td><td>Electromagnetic approach for high-frequency grounding analysis</td></tr>
<tr><td>IEEE 80-2013</td><td>Reference standard for AC substation grounding safety</td></tr>
</table>

<div class="footer">
<p><strong>Fatehah Burhannudin</strong> | fatehahdean@gmail.com | linkedin.com/in/fatehahburhannudin</p>
<p>This tool is based on validated CDEGS simulation data from the author's Final Year Project at Universiti Teknologi Malaysia (2023), supervised by Dr. Zuraimy Adzis.</p>
<p>Generated: {timestamp}</p>
</div>
</body></html>"""


def main() -> None:
    print("Transmission Tower Grounding Risk Assessment Tool")
    print("Based on FYP Research - Fatehah Burhannudin, UTM 2023")
    print("=" * 60)

    results = run_assessment()
    now = datetime.now()
    html = build_report_html(results, now)

    filename = f"grounding_report_{now.strftime('%Y%m%d_%H%M')}.html"
    with open(filename, "w") as f:
        f.write(html)

    critical = sum(1 for r in results if r["risk"] == "CRITICAL")
    high = sum(1 for r in results if r["risk"] == "HIGH")
    moderate = sum(1 for r in results if r["risk"] == "MODERATE")
    low = sum(1 for r in results if r["risk"] == "LOW")

    print(f"\nReport saved: {filename}")
    print(f"Critical: {critical} | High: {high} | Moderate: {moderate} | Low: {low}")
    print("Open the HTML file in your browser to view the full report.")


if __name__ == "__main__":
    main()
