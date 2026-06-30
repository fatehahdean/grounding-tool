# Transmission Tower Grounding Risk Assessment Tool

A Python-based risk assessment tool for transmission line tower grounding systems, built on validated electromagnetic simulation data from original FYP research.

**Author:** Fatehah Burhannudin
**Research Basis:** "Electromagnetic Modelling Analysis of Soil Ionisation Effects on Transmission Line Tower Grounding Performance" — Universiti Teknologi Malaysia, 2023
**Supervisor:** Dr. Zuraimy Adzis

---

## What This Tool Does

Estimates induced voltage at transmission line tower grounding systems under lightning surge conditions, accounting for soil ionisation effects. Results are interpolated from validated CDEGS electromagnetic simulation data from the author's FYP research.

The tool assesses risk for six conductor radius configurations across two soil models, generates engineering recommendations, and produces a client-ready HTML report.

---

## Research Background

When lightning strikes a transmission tower, current flows into the grounding system. Soil ionisation changes how that current distributes — reducing effective soil resistance and lowering induced voltage.

This tool models that effect by varying the ground conductor radius as recommended by CIGRE and IEEE Working Groups. All data points were validated against experimental results from benchmarking literature.

**Key findings from FYP research:**
- Soil ionisation reduces induced voltage by 2.59% to 13.79% for horizontal soil conditions
- Uniform soil shows higher reduction (3.57% to 19.83%) but oversimplifies real-world layered conditions
- Horizontal soil model is recommended for accurate real-world grounding system analysis

---

## System Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| Tower Voltage Rating | 500 kV | FYP Research Specification |
| Lightning Injection Current | 16 kA | FYP Research Specification |
| Key Frequency | 50 Hz | FYP Research Specification |
| Conductor Material | Copper (1.67e-8 ohm-m) | FYP Research Specification |
| Conductor Radius Range | 0.007m to 0.4082m | FYP Validated Range |

---

## FYP Research Data — Horizontal Soil Model

| Conductor Radius (m) | Induced Voltage (kV) | Voltage Reduction (%) |
|---------------------|---------------------|----------------------|
| 0.0070 | 11.6 | Baseline |
| 0.0114 | 11.3 | 2.59% |
| 0.1212 | 10.6 | 8.62% |
| 0.2052 | 10.4 | 10.34% |
| 0.3032 | 10.2 | 12.07% |
| 0.4082 | 10.0 | 13.79% |

---

## FYP Research Data — Uniform Soil Model

| Conductor Radius (m) | Induced Voltage (kV) | Voltage Reduction (%) |
|---------------------|---------------------|----------------------|
| 0.0070 | 11.3 | Baseline |
| 0.0114 | 11.1 | 3.57% |
| 0.1212 | 10.0 | 12.07% |
| 0.2052 | 9.7 | 14.66% |
| 0.3032 | 9.4 | 17.24% |
| 0.4082 | 9.3 | 19.83% |

---

## Risk Assessment Logic

| Risk Level | Condition | Colour |
|------------|-----------|--------|
| CRITICAL | Voltage ratio > 2.5% of tower rating | Red |
| HIGH | Voltage ratio > 2.0% of tower rating | Orange |
| MODERATE | Voltage ratio > 1.8% of tower rating | Yellow |
| LOW | Voltage ratio <= 1.8% of tower rating | Green |

---

## How to Run

    python3 grounding_tool.py

Opens an HTML report with full risk assessment results, FYP benchmark data tables, and engineering recommendations.

---

## Output Report Includes

- System parameters and research basis
- FYP benchmark data tables for both soil models
- Risk assessment summary (Critical / High / Moderate / Low counts)
- Detailed results for all 12 scenarios (6 radii x 2 soil models)
- Engineering recommendations per scenario
- Key research findings
- Standards and methodology reference
<img width="1470" height="956" alt="Screenshot 2026-07-01 at 1 20 55 AM" src="https://github.com/user-attachments/assets/686ed6b5-bcef-41ae-ba1e-f1e78ce5dfd7" />

---

## Standards and Methodology

| Tool / Standard | Application |
|----------------|-------------|
| CDEGS HIFREQ-SESCAD Module | Electromagnetic field simulation |
| FFTSES / IFFTSES Module | Fast Fourier Transform analysis of lightning impulse waveforms |
| CIGRE Guidelines | Soil ionisation modelling methodology |
| IEEE Working Group Recommendations | Electromagnetic approach for high-frequency analysis |
| IEEE 80-2013 | Reference standard for AC substation grounding safety |

---

## Technologies Used

- Python 3.13
- Linear interpolation for voltage estimation between validated data points
- HTML / CSS for client-ready report generation

---

## Important Notes

- Sensor readings are based on validated CDEGS simulation data — not live measurements
- Results outside the validated radius range (0.007m to 0.4082m) are extrapolated
- Horizontal soil model is recommended over uniform for real-world layered soil conditions
- This tool extends FYP research into a practical engineering assessment application

---

## License

© 2026 Fatehah Burhannudin. All rights reserved.

This tool is based on validated research data from the author's Final Year Project at Universiti Teknologi Malaysia (2023), supervised by Dr. Zuraimy Adzis.
