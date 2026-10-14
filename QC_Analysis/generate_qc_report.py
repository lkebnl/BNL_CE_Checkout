#!/usr/bin/env python3
"""
Generate QC Criteria Report from CSV data
Automatically includes all parameters and plots
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

# Parameter descriptions
PARAM_DESCRIPTIONS = {
    # 128-channel parameters
    "ped": ("Pedestal", "The baseline ADC value when no signal is present. Represents the DC offset of each channel's readout electronics.", "Pedestal values vary across channels due to manufacturing variations. Values outside 5σ bounds may indicate channel issues."),
    "rms": ("RMS Noise", "Root Mean Square of the baseline fluctuations. Measures the intrinsic electronic noise of each channel in ADC counts.", "Lower noise is better. High RMS indicates noisy channels that may affect signal quality."),
    "PPK_mean": ("Positive Peak", "Mean ADC value of the positive pulse response when injecting a calibration pulse. Measures the channel gain for positive signals.", "Consistent PPK values across channels indicate uniform gain. Large deviations suggest gain calibration issues."),
    "NPK_mean": ("Negative Peak", "Mean ADC value of the negative pulse response. Measures the channel response to negative-going signals.", "NPK should be symmetric with PPK relative to baseline. Asymmetry may indicate amplifier nonlinearity."),
    "BL_mean": ("Baseline", "Mean baseline level during pulse response measurement. Should be centered around mid-range ADC value.", "Baseline provides reference for pulse amplitude measurements. Stable baseline indicates good DC performance."),
    "pedmax": ("Pedestal Max", "Maximum pedestal value observed during the measurement window. Used to check for pedestal stability.", "Large difference between pedmax and pedmin indicates pedestal instability or excessive noise spikes."),
    "pedmin": ("Pedestal Min", "Minimum pedestal value observed during the measurement window.", "Together with pedmax, defines the pedestal variation range. (pedmax - pedmin) should be small for stable channels."),

    # LDO parameters
    "CDVDDA": ("COLDATA Analog Supply", "COLDATA analog supply voltage (VDDA). Powers the analog sections of the COLDATA ASIC.", "Should be stable and within specification."),
    "CDVDDIO_HALF": ("COLDATA I/O Supply", "COLDATA I/O supply voltage (divided by 2 for ADC range). Powers the digital I/O of COLDATA.", "Should be stable and within specification."),
    "ADCRVDDD1P2": ("Right ADC Digital 1.2V", "Right ColdADC digital 1.2V supply voltage. Powers the digital logic of the right-side ColdADC.", "Should be stable around 1.2V equivalent."),
    "ADCLVDDD1P2": ("Left ADC Digital 1.2V", "Left ColdADC digital 1.2V supply voltage. Powers the digital logic of the left-side ColdADC.", "Should be stable around 1.2V equivalent."),
    "FERVDDP": ("Right FE Supply", "Right LArASIC (FE) positive supply voltage. Powers the right-side front-end ASIC.", "Higher during pedestal, lower during pulse due to increased current draw."),
    "FELVDDP": ("Left FE Supply", "Left LArASIC (FE) positive supply voltage. Powers the left-side front-end ASIC.", "Higher during pedestal, lower during pulse due to increased current draw."),
    "ADCRP25V_1_HALF": ("Right ADC 2.5V #1", "Right ColdADC 2.5V supply #1 (divided by 2). Analog reference voltage for right ADC.", "Should be stable around 2.5V equivalent."),
    "ADCLP25V_1_HALF": ("Left ADC 2.5V #1", "Left ColdADC 2.5V supply #1 (divided by 2). Analog reference voltage for left ADC.", "Should be stable around 2.5V equivalent."),
    "ADCRP25V_HALF": ("Right ADC 2.5V Main", "Right ColdADC 2.5V main supply (divided by 2). Main 2.5V reference for right ADC.", "Should be stable around 2.5V equivalent."),
    "ADCLP25V_HALF": ("Left ADC 2.5V Main", "Left ColdADC 2.5V main supply (divided by 2). Main 2.5V reference for left ADC.", "Should be stable around 2.5V equivalent."),
    "GND": ("Ground Reference", "Ground reference measurement. Should be near zero.", "Non-zero value represents ADC offset. Should be consistent across boards."),

    # Current parameters
    "I_LArASIC": ("LArASIC Current", "LArASIC front-end ASIC current consumption.", "Higher during pulse mode due to active signal processing."),
    "I_ColdDATA": ("ColdDATA Current", "COLDATA serializer ASIC current consumption.", "Should be relatively constant between modes."),
    "I_ColdADC": ("ColdADC Current", "ColdADC digitizer current consumption.", "Should be relatively constant between modes."),

    # Power parameters
    "Total_Power": ("Total Power", "Total board power consumption.", "Pulse configuration draws more power than pedestal due to active signal processing."),

    # ASIC parameters
    "FE T": ("FE Temperature", "LArASIC temperature sensor reading in ADC counts. Higher values indicate higher temperature.", "Temperature should be consistent across chips and boards at room temperature testing."),
    "FE BGP": ("FE Bandgap", "LArASIC bandgap reference voltage in ADC counts. Critical for stable operation.", "Bandgap provides voltage reference for the ASIC. Should be very stable."),
    "ADC_VCMI": ("ADC VCMI", "ColdADC common-mode input voltage reference.", "Should be consistent across chips."),
    "ADC_VCMO": ("ADC VCMO", "ColdADC common-mode output voltage reference.", "Should be consistent across chips."),
    "ADC_VREFP": ("ADC VREFP", "ColdADC positive reference voltage. Sets the upper limit of ADC range.", "Critical for ADC linearity and range."),
    "ADC_VREFN": ("ADC VREFN", "ColdADC negative reference voltage. Sets the lower limit of ADC range.", "Critical for ADC linearity and range."),
    "VSSA": ("VSSA", "Analog ground reference voltage. Should be near zero.", "Non-zero value represents ADC offset."),
}

def get_param_info(param_name):
    """Get description info for a parameter"""
    # Check for exact match
    if param_name in PARAM_DESCRIPTIONS:
        return PARAM_DESCRIPTIONS[param_name]

    # Check for base name (without _ped or _pulse suffix)
    base_name = param_name.replace("_ped", "").replace("_pulse", "")
    if base_name in PARAM_DESCRIPTIONS:
        return PARAM_DESCRIPTIONS[base_name]

    # Default
    return (param_name, f"Parameter {param_name}", "See plot for distribution.")

def get_plot_filename(param_name):
    """Get the plot filename for a parameter"""
    # Handle special characters in parameter names
    clean_name = param_name.replace(" ", "_")
    return f"plot_{clean_name}.png"

def load_csv_data():
    """Load all parameters from CSV"""
    params = []
    with open(CSV_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Parameter']:  # Skip empty rows
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

    # Determine unit based on type
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
| MAD | {float(param['MAD']):.4f} |
| 3σ Lower | {float(param['Lower_3Sigma']):.4f} |
| 3σ Upper | {float(param['Upper_3Sigma']):.4f} |
| 5σ Lower | {float(param['Lower_5Sigma']):.4f} |
| 5σ Upper | {float(param['Upper_5Sigma']):.4f} |
| Min | {float(param['Min']):.4f} |
| Max | {float(param['Max']):.4f} |
| N | {param['N']} |

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

This report documents the Quality Control (QC) criteria derived from 44 FEMB-IO 1826-1L boards that passed checkout testing at BNL. The criteria are established using statistical analysis with 3σ (99.7% coverage) and 5σ (99.99994% coverage) bounds.

### Statistical Methods

- **Mean:** Arithmetic average of all measurements
- **Std:** Standard deviation
- **Median:** Middle value (robust to outliers)
- **MAD:** Median Absolute Deviation (robust measure of spread)
- **3σ Bounds:** Mean ± 3×Std (99.7% of normal distribution) - shown in green
- **5σ Bounds:** Mean ± 5×Std (recommended pass/fail threshold) - shown in red
- **N:** Number of data points

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

## 1. 128-Channel Parameters

These parameters are measured for all 128 channels on each FEMB board (5632 total data points = 44 boards × 128 channels).

"""

    # Add 128-channel parameters
    for i, p in enumerate(categories['128ch'], 1):
        md += generate_param_section(p, f"1.{i}")

    md += """## 2. LDO Voltage Parameters (Pedestal Configuration)

Low Dropout (LDO) regulator output voltages measured during pedestal check. These monitor the on-board power regulation.

"""

    # Add LDO pedestal parameters
    for i, p in enumerate(categories['ldo_ped'], 1):
        md += generate_param_section(p, f"2.{i}")

    md += """## 3. LDO Voltage Parameters (Pulse Configuration)

Same LDO measurements during pulse response check. Different operating conditions may show slight voltage shifts due to varying current draw.

"""

    # Add LDO pulse parameters
    for i, p in enumerate(categories['ldo_pulse'], 1):
        md += generate_param_section(p, f"3.{i}")

    md += """## 4. Current Measurements

Board-level current consumption for each power rail, measured at different operating configurations.

"""

    # Add current parameters
    for i, p in enumerate(categories['current'], 1):
        md += generate_param_section(p, f"4.{i}")

    md += """## 5. Power Measurements

Total board power consumption at different operating configurations.

"""

    # Add power parameters
    for i, p in enumerate(categories['power'], 1):
        md += generate_param_section(p, f"5.{i}")

    md += """## 6. ASIC-Level Parameters (8-Chip)

These parameters are measured per ASIC chip (8 chips per board, 352 total data points = 44 boards × 8 chips).

"""

    # Add 8-chip parameters
    for i, p in enumerate(categories['8chip'], 1):
        md += generate_param_section(p, f"6.{i}")

    # Add appendices
    md += """## Appendix A: Complete Pass/Fail Criteria Summary

For QC purposes, use the **5σ bounds** as pass/fail thresholds. All parameters with their 5σ bounds:

| Parameter | Type | 5σ Lower | 5σ Upper |
|-----------|------|----------|----------|
"""

    for p in params:
        md += f"| {p['Parameter']} | {p['Type']} | {float(p['Lower_5Sigma']):.4f} | {float(p['Upper_5Sigma']):.4f} |\n"

    md += """
---

## Appendix B: Board List

44 boards were used in this analysis (latest passing test only).
See `good_boards_list.txt` for the complete list of board serial numbers.

---

## Appendix C: Excluded Boards

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

    # Find all image references and convert to base64
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
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #2980b9;
            border-bottom: 2px solid #bdc3c7;
            padding-bottom: 5px;
            margin-top: 30px;
        }
        h3 {
            color: #34495e;
            margin-top: 20px;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
        }
        th, td {
            border: 1px solid #bdc3c7;
            padding: 8px 12px;
            text-align: left;
        }
        th {
            background-color: #3498db;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #ecf0f1;
        }
        code {
            background-color: #f4f4f4;
            padding: 2px 5px;
            border-radius: 3px;
        }
        hr {
            border: none;
            border-top: 1px solid #bdc3c7;
            margin: 30px 0;
        }
        strong {
            color: #2c3e50;
        }
        p {
            margin: 10px 0;
        }
        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 20px auto;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        @media print {
            body { padding: 20px; }
            img { max-width: 90%; page-break-inside: avoid; }
        }
    </style>
</head>
<body>
''' + html_content + '''
</body>
</html>'''

    return html_template

def main():
    print("Loading CSV data...")
    params = load_csv_data()
    print(f"Found {len(params)} parameters")

    print("\nGenerating markdown report...")
    md_content = generate_markdown_report(params)

    # Save markdown
    md_file = os.path.join(OUTPUT_DIR, "FEMB_QC_Criteria_Report.md")
    with open(md_file, 'w') as f:
        f.write(md_content)
    print(f"Saved: {md_file}")

    print("\nConverting to HTML with embedded images...")
    html_content = convert_to_html(md_content, OUTPUT_DIR)

    # Save HTML
    html_file = os.path.join(OUTPUT_DIR, "FEMB_QC_Criteria_Report.html")
    with open(html_file, 'w') as f:
        f.write(html_content)
    print(f"Saved: {html_file}")

    # Copy CSV and board list
    shutil.copy(CSV_FILE, OUTPUT_DIR)
    boards_file = os.path.join(INPUT_DIR, "good_boards_list.txt")
    if os.path.exists(boards_file):
        shutil.copy(boards_file, OUTPUT_DIR)

    print(f"\nReport files generated in: {OUTPUT_DIR}")
    print("Run Chrome to generate PDF:")
    print(f'google-chrome --headless --disable-gpu --print-to-pdf="{OUTPUT_DIR}/FEMB_QC_Criteria_Report.pdf" "{html_file}"')

if __name__ == "__main__":
    main()
