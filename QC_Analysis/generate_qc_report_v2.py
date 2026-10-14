#!/usr/bin/env python3
"""
Generate QC Criteria Report from CSV data
Uses fixed tolerances for voltage/current parameters
Uses 5σ for channel-level parameters
"""

import csv
import os
import base64
import markdown
import re
import shutil

# Paths
INPUT_DIR = "/home/dune/PycharmProjects/BNL_CE_Checkout/QC_Analysis/output_1826_1L_final"
OUTPUT_DIR = "/home/dune/PycharmProjects/BNL_CE_Checkout/QC_Analysis/output_1826_1L_report"
CSV_FILE = os.path.join(INPUT_DIR, "QC_Criteria_Complete.csv")

# Tolerance settings
# Power rail parameters use 7σ, channel/ASIC parameters use 5σ
TOLERANCE_CONFIG = {
    'ldo_ped': {'type': 'sigma', 'value': 7},          # 7σ for LDO voltages
    'ldo_pulse': {'type': 'sigma', 'value': 7},        # 7σ for LDO voltages
    'current': {'type': 'sigma', 'value': 7},          # 7σ for currents
    'power': {'type': 'sigma', 'value': 7},            # 7σ for power
    '128ch': {'type': 'sigma', 'value': 5},            # 5σ for channel params
    '8chip': {'type': 'sigma', 'value': 5},            # 5σ for ASIC params
}

# GND parameters also use 7σ (no special case needed anymore)

# Parameter descriptions
PARAM_DESCRIPTIONS = {
    # 128-channel parameters
    "ped": ("Pedestal", "The baseline ADC value when no signal is present. Represents the DC offset of each channel's readout electronics.", "Pedestal values vary across channels due to manufacturing variations."),
    "rms": ("RMS Noise", "Root Mean Square of the baseline fluctuations. Measures the intrinsic electronic noise of each channel in ADC counts.", "Lower noise is better. High RMS indicates noisy channels."),
    "PPK_mean": ("Positive Peak", "Mean ADC value of the positive pulse response when injecting a calibration pulse.", "Consistent PPK values indicate uniform gain."),
    "NPK_mean": ("Negative Peak", "Mean ADC value of the negative pulse response.", "NPK should be symmetric with PPK relative to baseline."),
    "BL_mean": ("Baseline", "Mean baseline level during pulse response measurement.", "Stable baseline indicates good DC performance."),
    "pedmax": ("Pedestal Max", "Maximum pedestal value observed during the measurement window.", "Large pedmax-pedmin difference indicates instability."),
    "pedmin": ("Pedestal Min", "Minimum pedestal value observed during the measurement window.", "Together with pedmax, defines pedestal variation range."),

    # LDO parameters
    "CDVDDA": ("COLDATA Analog Supply", "COLDATA analog supply voltage (VDDA).", "Should be stable within 7σ bounds."),
    "CDVDDIO_HALF": ("COLDATA I/O Supply", "COLDATA I/O supply voltage (divided by 2).", "Should be stable within 7σ bounds."),
    "ADCRVDDD1P2": ("Right ADC Digital 1.2V", "Right ColdADC digital 1.2V supply.", "Should be stable within 7σ bounds."),
    "ADCLVDDD1P2": ("Left ADC Digital 1.2V", "Left ColdADC digital 1.2V supply.", "Should be stable within 7σ bounds."),
    "FERVDDP": ("Right FE Supply", "Right LArASIC positive supply voltage.", "Higher during pedestal, lower during pulse."),
    "FELVDDP": ("Left FE Supply", "Left LArASIC positive supply voltage.", "Higher during pedestal, lower during pulse."),
    "ADCRP25V_1_HALF": ("Right ADC 2.5V #1", "Right ColdADC 2.5V supply #1 (divided by 2).", "Should be stable within 7σ bounds."),
    "ADCLP25V_1_HALF": ("Left ADC 2.5V #1", "Left ColdADC 2.5V supply #1 (divided by 2).", "Should be stable within 7σ bounds."),
    "ADCRP25V_HALF": ("Right ADC 2.5V Main", "Right ColdADC 2.5V main supply (divided by 2).", "Should be stable within 7σ bounds."),
    "ADCLP25V_HALF": ("Left ADC 2.5V Main", "Left ColdADC 2.5V main supply (divided by 2).", "Should be stable within 7σ bounds."),
    "GND": ("Ground Reference", "Ground reference measurement.", "Should be near zero, within 7σ bounds."),

    # Current parameters
    "I_LArASIC": ("LArASIC Current", "LArASIC front-end ASIC current consumption.", "Should be within 7σ bounds."),
    "I_ColdDATA": ("ColdDATA Current", "COLDATA serializer ASIC current consumption.", "Should be within 7σ bounds."),
    "I_ColdADC": ("ColdADC Current", "ColdADC digitizer current consumption.", "Should be within 7σ bounds."),

    # Power parameters
    "Total_Power": ("Total Power", "Total board power consumption.", "Should be within 7σ bounds."),

    # ASIC parameters
    "FE T": ("FE Temperature", "LArASIC temperature sensor reading.", "Should be consistent at room temperature."),
    "FE BGP": ("FE Bandgap", "LArASIC bandgap reference voltage.", "Critical for stable operation."),
    "ADC_VCMI": ("ADC VCMI", "ColdADC common-mode input voltage.", "Should be consistent across chips."),
    "ADC_VCMO": ("ADC VCMO", "ColdADC common-mode output voltage.", "Should be consistent across chips."),
    "ADC_VREFP": ("ADC VREFP", "ColdADC positive reference voltage.", "Sets upper ADC range limit."),
    "ADC_VREFN": ("ADC VREFN", "ColdADC negative reference voltage.", "Sets lower ADC range limit."),
    "VSSA": ("VSSA", "Analog ground reference voltage.", "Should be near zero."),
}

def get_param_info(param_name):
    """Get description info for a parameter"""
    if param_name in PARAM_DESCRIPTIONS:
        return PARAM_DESCRIPTIONS[param_name]
    base_name = param_name.replace("_ped", "").replace("_pulse", "")
    if base_name in PARAM_DESCRIPTIONS:
        return PARAM_DESCRIPTIONS[base_name]
    return (param_name, f"Parameter {param_name}", "See plot for distribution.")

def get_plot_filename(param_name):
    """Get the plot filename for a parameter"""
    clean_name = param_name.replace(" ", "_")
    return f"plot_{clean_name}.png"

def calculate_tolerance_bounds(param):
    """Calculate tolerance bounds based on parameter type"""
    param_type = param['Type']
    mean = float(param['Mean'])
    std = float(param['Std'])

    config = TOLERANCE_CONFIG.get(param_type, {'type': 'sigma', 'value': 5})

    # All parameters now use sigma-based tolerance
    lower = mean - config['value'] * std
    upper = mean + config['value'] * std
    method = f"{config['value']}σ"

    return lower, upper, method

def load_csv_data():
    """Load all parameters from CSV"""
    params = []
    with open(CSV_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Parameter']:
                # Calculate tolerance bounds
                lower, upper, method = calculate_tolerance_bounds(row)
                row['Tol_Lower'] = lower
                row['Tol_Upper'] = upper
                row['Tol_Method'] = method
                params.append(row)
    return params

def categorize_params(params):
    """Categorize parameters by type"""
    categories = {
        '128ch': [],
        'ldo_ped': [],
        'ldo_pulse': [],
        'current': [],
        'power': [],
        '8chip': []
    }
    for p in params:
        param_type = p['Type']
        if param_type in categories:
            categories[param_type].append(p)
    return categories

def generate_param_section(param, section_num):
    """Generate markdown section for a parameter"""
    name = param['Parameter']
    display_name = param['Name']
    param_type = param['Type']

    title, description, interpretation = get_param_info(name)

    # Determine unit
    unit = "ADC"
    if 'current' in param_type.lower() or name.startswith('I_'):
        unit = "A"
    elif 'power' in param_type.lower() or 'Power' in name:
        unit = "W"

    md = f"""### {section_num} {display_name} ({name})

**Description:** {description}

| Statistic | Value |
|-----------|-------|
| Mean | {float(param['Mean']):.4f} |
| Std | {float(param['Std']):.4f} |
| Median | {float(param['Median']):.4f} |
| Min | {float(param['Min']):.4f} |
| Max | {float(param['Max']):.4f} |
| N | {param['N']} |

**Pass/Fail Criteria ({param['Tol_Method']}):**

| Lower Limit | Upper Limit |
|-------------|-------------|
| {param['Tol_Lower']:.4f} | {param['Tol_Upper']:.4f} |

**Interpretation:** {interpretation}

![{display_name}]({get_plot_filename(name)})

---

"""
    return md

def generate_markdown_report(params):
    """Generate the complete markdown report"""
    categories = categorize_params(params)

    md = """# FEMB QC Criteria Report

## FEMB-IO 1826-1L Quality Control Analysis

**Analysis Date:** October 2026
**Board Version:** FEMB-IO 1826-1L
**Number of Boards Analyzed:** 44
**Total Parameters:** """ + str(len(params)) + """
**Analysis Method:** Statistical analysis using latest passing test per board

---

## Overview

This report documents the Quality Control (QC) criteria derived from 44 FEMB-IO 1826-1L boards that passed checkout testing at BNL.

### Tolerance Methods

Different tolerance methods are used based on parameter type:

| Parameter Type | Tolerance Method | Rationale |
|----------------|------------------|-----------|
| 128-Channel (ped, rms, etc.) | 5σ | Statistical outlier detection for large datasets (5632 points) |
| 8-Chip ASIC | 5σ | Statistical outlier detection (352 points) |
| LDO Voltages | 7σ | Wider tolerance for power rail monitoring (44 points) |
| Currents | 7σ | Wider tolerance for current measurements (44 points) |
| Power | 7σ | Wider tolerance for power measurements (44 points) |

### Parameter Categories

| Category | Description | Count |
|----------|-------------|-------|
| 128-Channel | Per-channel measurements (128 ch × 44 boards = 5632 points) | """ + str(len(categories['128ch'])) + """ |
| LDO Pedestal | LDO voltage readings during pedestal check | """ + str(len(categories['ldo_ped'])) + """ |
| LDO Pulse | LDO voltage readings during pulse check | """ + str(len(categories['ldo_pulse'])) + """ |
| Current | Power rail current measurements | """ + str(len(categories['current'])) + """ |
| Power | Total power measurements | """ + str(len(categories['power'])) + """ |
| 8-Chip ASIC | Per-ASIC measurements (8 chips × 44 boards = 352 points) | """ + str(len(categories['8chip'])) + """ |

---

## 1. 128-Channel Parameters (5σ Tolerance)

These parameters are measured for all 128 channels on each FEMB board (5632 total data points).

"""

    for i, p in enumerate(categories['128ch'], 1):
        md += generate_param_section(p, f"1.{i}")

    md += """## 2. LDO Voltage Parameters - Pedestal (7σ Tolerance)

LDO regulator output voltages measured during pedestal check.

"""

    for i, p in enumerate(categories['ldo_ped'], 1):
        md += generate_param_section(p, f"2.{i}")

    md += """## 3. LDO Voltage Parameters - Pulse (7σ Tolerance)

LDO measurements during pulse response check.

"""

    for i, p in enumerate(categories['ldo_pulse'], 1):
        md += generate_param_section(p, f"3.{i}")

    md += """## 4. Current Measurements (7σ Tolerance)

Board-level current consumption for each power rail.

"""

    for i, p in enumerate(categories['current'], 1):
        md += generate_param_section(p, f"4.{i}")

    md += """## 5. Power Measurements (7σ Tolerance)

Total board power consumption.

"""

    for i, p in enumerate(categories['power'], 1):
        md += generate_param_section(p, f"5.{i}")

    md += """## 6. ASIC-Level Parameters (5σ Tolerance)

Per-ASIC measurements (8 chips per board, 352 total data points).

"""

    for i, p in enumerate(categories['8chip'], 1):
        md += generate_param_section(p, f"6.{i}")

    # Summary table
    md += """## Appendix A: Complete Pass/Fail Criteria Summary

| Parameter | Type | Method | Lower Limit | Upper Limit |
|-----------|------|--------|-------------|-------------|
"""

    for p in params:
        md += f"| {p['Parameter']} | {p['Type']} | {p['Tol_Method']} | {p['Tol_Lower']:.4f} | {p['Tol_Upper']:.4f} |\n"

    md += """
---

## Appendix B: Tolerance Configuration

| Parameter Type | Tolerance | Description |
|----------------|-----------|-------------|
| 128-Channel | 5σ | Mean ± 5×Std, for large datasets (5632 points) |
| 8-Chip ASIC | 5σ | Mean ± 5×Std, for ASIC-level measurements (352 points) |
| LDO Voltages | 7σ | Mean ± 7×Std, wider tolerance for power rail (44 points) |
| Currents | 7σ | Mean ± 7×Std, wider tolerance for current measurements |
| Power | 7σ | Mean ± 7×Std, wider tolerance for power measurements |

---

## Appendix C: Board List

44 boards were used in this analysis (latest passing test only).
See `good_boards_list.txt` for the complete list.

---

## Appendix D: Excluded Boards

- **Board 00046:** Manually excluded (known bad board)
- Boards with only failed tests were automatically excluded

---

*Report generated from QC checkout data analysis*
*BNL Cold Electronics Testing Facility*
"""

    return md

def convert_to_html(md_content, output_dir):
    """Convert markdown to HTML with embedded images"""
    html_content = markdown.markdown(md_content, extensions=['tables', 'toc'])

    def embed_image(match):
        alt = match.group(1)
        src = match.group(2)
        img_path = os.path.join(INPUT_DIR, src)
        if os.path.exists(img_path):
            with open(img_path, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
            return f'<img src="data:image/png;base64,{img_data}" alt="{alt}" style="max-width:100%; height:auto;">'
        else:
            print(f"Warning: Image not found: {img_path}")
            return f'<p style="color:red;">[Image not found: {src}]</p>'

    html_content = re.sub(r'<img alt="([^"]+)" src="([^"]+)" ?/?>', embed_image, html_content)

    html_template = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>FEMB QC Criteria Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px;
            line-height: 1.6;
            font-size: 11pt;
        }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2 { color: #2980b9; border-bottom: 2px solid #bdc3c7; padding-bottom: 5px; margin-top: 30px; }
        h3 { color: #34495e; margin-top: 20px; }
        table { border-collapse: collapse; width: 100%; margin: 15px 0; }
        th, td { border: 1px solid #bdc3c7; padding: 8px 12px; text-align: left; }
        th { background-color: #3498db; color: white; }
        tr:nth-child(even) { background-color: #ecf0f1; }
        hr { border: none; border-top: 1px solid #bdc3c7; margin: 30px 0; }
        strong { color: #2c3e50; }
        img { max-width: 100%; height: auto; display: block; margin: 20px auto; border: 1px solid #ddd; border-radius: 4px; }
        @media print { body { padding: 20px; } img { max-width: 90%; page-break-inside: avoid; } }
    </style>
</head>
<body>
''' + html_content + '''
</body>
</html>'''

    return html_template

def save_criteria_csv(params, output_dir):
    """Save the criteria with tolerance bounds to CSV"""
    csv_file = os.path.join(output_dir, "QC_Criteria_WithTolerance.csv")

    fieldnames = ['Parameter', 'Name', 'Type', 'Mean', 'Std', 'Min', 'Max',
                  'Tol_Method', 'Tol_Lower', 'Tol_Upper', 'N']

    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for p in params:
            row = {k: p.get(k, '') for k in fieldnames}
            writer.writerow(row)

    print(f"Saved: {csv_file}")

def main():
    print("Loading CSV data...")
    params = load_csv_data()
    print(f"Found {len(params)} parameters")

    print("\nTolerance summary:")
    for p in params[:5]:
        print(f"  {p['Parameter']}: {p['Tol_Method']} -> [{p['Tol_Lower']:.2f}, {p['Tol_Upper']:.2f}]")
    print("  ...")

    print("\nGenerating markdown report...")
    md_content = generate_markdown_report(params)

    md_file = os.path.join(OUTPUT_DIR, "FEMB_QC_Criteria_Report.md")
    with open(md_file, 'w') as f:
        f.write(md_content)
    print(f"Saved: {md_file}")

    print("\nConverting to HTML with embedded images...")
    html_content = convert_to_html(md_content, OUTPUT_DIR)

    html_file = os.path.join(OUTPUT_DIR, "FEMB_QC_Criteria_Report.html")
    with open(html_file, 'w') as f:
        f.write(html_content)
    print(f"Saved: {html_file}")

    print("\nSaving criteria CSV with tolerances...")
    save_criteria_csv(params, OUTPUT_DIR)

    # Copy supporting files
    shutil.copy(CSV_FILE, OUTPUT_DIR)
    boards_file = os.path.join(INPUT_DIR, "good_boards_list.txt")
    if os.path.exists(boards_file):
        shutil.copy(boards_file, OUTPUT_DIR)

    print(f"\nReport files generated in: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
