#!/usr/bin/env python3
"""
FEMB 1826-1L QC Complete Analysis - ALL Parameters
- 128-channel parameters (ped, rms, PPK, NPK, BL)
- 8-chip parameters (LDO/Monitor voltages, ASIC readings)
- Power measurements
"""

import os
import csv
import ast
import re
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Configuration
QC_DATA_ROOT = "/home/dune/Documents/data/FEMB_QC/Report"
OUTPUT_DIR = "/home/dune/PycharmProjects/BNL_CE_Checkout/QC_Analysis/output_1826_1L_final"
EXCLUDED_BOARDS = ["00046"]

# Parameter categories
PARAMS_128CH = ["ped", "rms", "PPK_mean", "NPK_mean", "BL_mean", "pedmax", "pedmin"]

PARAMS_8CHIP = [
    "CDVDDA", "CDVDDIO_HALF",
    "ADCRVDDD1P2", "ADCLVDDD1P2",
    "FERVDDP", "FELVDDP",
    "ADCRP25V_1_HALF", "ADCLP25V_1_HALF",
    "ADCRP25V_HALF", "ADCLP25V_HALF",
    "GND",
    "FE T", "FE BGP",
    "ADC_VCMI", "ADC_VCMO", "ADC_VREFP", "ADC_VREFN",
    "VSSA"
]

PARAMS_POWER = ["V_meas/V", "I_meas/A", "P_meas/W", "Total Power"]

PARAM_NAMES = {
    # 128-channel
    "ped": "Pedestal", "rms": "RMS Noise",
    "PPK_mean": "Positive Peak", "NPK_mean": "Negative Peak", "BL_mean": "Baseline",
    "pedmax": "Pedestal Max", "pedmin": "Pedestal Min",
    # 8-chip LDO/Monitor
    "CDVDDA": "COLDATA VDDA", "CDVDDIO_HALF": "COLDATA VDDIO/2",
    "ADCRVDDD1P2": "ADC-R VDDD 1.2V", "ADCLVDDD1P2": "ADC-L VDDD 1.2V",
    "FERVDDP": "FE-R VDDP", "FELVDDP": "FE-L VDDP",
    "ADCRP25V_1_HALF": "ADC-R P25V_1/2", "ADCLP25V_1_HALF": "ADC-L P25V_1/2",
    "ADCRP25V_HALF": "ADC-R P25V/2", "ADCLP25V_HALF": "ADC-L P25V/2",
    "GND": "Ground",
    # ASIC
    "FE T": "FE Temperature", "FE BGP": "FE Bandgap",
    "ADC_VCMI": "ADC VCMI", "ADC_VCMO": "ADC VCMO",
    "ADC_VREFP": "ADC VREFP", "ADC_VREFN": "ADC VREFN",
    "VSSA": "VSSA",
    # Power
    "V_meas/V": "Voltage (V)", "I_meas/A": "Current (A)",
    "P_meas/W": "Power (W)", "Total Power": "Total Power (W)"
}

def parse_list_string(s):
    if not s or s == '':
        return []
    try:
        return ast.literal_eval(s)
    except:
        return []

def load_csv_data(csv_path):
    data = {}
    results = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                key = row[0]
                value = row[1]
                if key == "Result":
                    results.append(value)
                parsed = parse_list_string(value)
                if parsed:
                    data[key] = parsed
                else:
                    try:
                        data[key] = float(value)
                    except:
                        data[key] = value
    return data, results

def check_all_results_pass(results):
    for r in results:
        if r is False or str(r).lower() == "false":
            return False
    return True

def extract_timestamp(csv_path):
    match = re.search(r'Time_(\d{4})_(\d{2})/(\d{2})_(\d{2})_(\d{2})_(\d{2})', csv_path)
    if match:
        year, month, day, hour, minute, second = match.groups()
        return datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
    return datetime.min

def find_1826_1L_csv_files(root_dir):
    csv_files = []
    for root, dirs, files in os.walk(root_dir):
        for f in files:
            if "1826-1L" in f and f.startswith("DataBase_FEMB_") and f.endswith(".csv"):
                csv_files.append(os.path.join(root, f))
    return csv_files

def extract_board_number(csv_path):
    filename = os.path.basename(csv_path)
    parts = filename.split("_")
    for p in parts:
        if p.isdigit() and len(p) == 5:
            return p
    return None

def plot_parameter(arr, criteria, param, param_name, n_boards, n_items_per_board, output_dir, item_label="Channel"):
    """Generic plotting function for any parameter type."""
    c = criteria

    fig, ax = plt.subplots(figsize=(16, 8))

    # Calculate y limits with 15% padding
    data_range = c["max"] - c["min"]
    sigma_range = c["upper_5sigma"] - c["lower_5sigma"]
    total_range = max(data_range, sigma_range)
    padding = total_range * 0.15

    y_min = min(c["lower_5sigma"], c["min"]) - padding
    y_max = max(c["upper_5sigma"], c["max"]) + padding

    # Background bands
    ax.axhspan(y_min, c["lower_5sigma"], alpha=0.25, color='red', label='Outside 5σ (FAIL)')
    ax.axhspan(c["upper_5sigma"], y_max, alpha=0.25, color='red')
    ax.axhspan(c["lower_5sigma"], c["lower_3sigma"], alpha=0.25, color='yellow', label='3σ-5σ (WARNING)')
    ax.axhspan(c["upper_3sigma"], c["upper_5sigma"], alpha=0.25, color='yellow')
    ax.axhspan(c["lower_3sigma"], c["upper_3sigma"], alpha=0.25, color='lightgreen', label='Within 3σ (PASS)')

    # Plot data
    x = np.arange(len(arr))
    valid_mask = ~np.isnan(arr)
    arr_valid = arr[valid_mask]

    colors = []
    for v in arr:
        if np.isnan(v):
            colors.append('gray')
        elif v < c["lower_5sigma"] or v > c["upper_5sigma"]:
            colors.append('darkred')
        elif v < c["lower_3sigma"] or v > c["upper_3sigma"]:
            colors.append('darkorange')
        else:
            colors.append('blue')

    ax.scatter(x[valid_mask], arr_valid,
               c=[colors[i] for i in range(len(arr)) if valid_mask[i]],
               s=3 if n_items_per_board <= 8 else 2, alpha=0.6)

    # Sigma lines
    ax.axhline(y=c["mean"], color='black', linestyle='-', linewidth=2,
               label=f'Mean = {c["mean"]:.2f}')
    ax.axhline(y=c["lower_3sigma"], color='green', linestyle='--', linewidth=1.5)
    ax.axhline(y=c["upper_3sigma"], color='green', linestyle='--', linewidth=1.5,
               label=f'±3σ = [{c["lower_3sigma"]:.2f}, {c["upper_3sigma"]:.2f}]')
    ax.axhline(y=c["lower_5sigma"], color='red', linestyle='--', linewidth=1.5)
    ax.axhline(y=c["upper_5sigma"], color='red', linestyle='--', linewidth=1.5,
               label=f'±5σ = [{c["lower_5sigma"]:.2f}, {c["upper_5sigma"]:.2f}]')

    # Board boundaries
    for i in range(n_boards + 1):
        ax.axvline(x=i * n_items_per_board, color='gray', linestyle='-', alpha=0.3, linewidth=0.5)

    # Labels
    ax.set_xlabel(f"{item_label} Index ({n_items_per_board} × {n_boards} boards = {len(arr)})", fontsize=12)
    ax.set_ylabel(f"{param_name}", fontsize=12)
    ax.set_title(f"{param_name} Distribution\n1826-1L ({n_boards} boards)", fontsize=14)

    ax.set_xlim(-len(arr)*0.01, len(arr)*1.01)
    ax.set_ylim(y_min, y_max)
    ax.legend(loc='upper right', fontsize=9, framealpha=0.9)

    # Stats box
    n_within_3 = np.sum((arr_valid >= c["lower_3sigma"]) & (arr_valid <= c["upper_3sigma"]))
    n_between = np.sum(((arr_valid < c["lower_3sigma"]) & (arr_valid >= c["lower_5sigma"])) |
                       ((arr_valid > c["upper_3sigma"]) & (arr_valid <= c["upper_5sigma"])))
    n_outside_5 = np.sum((arr_valid < c["lower_5sigma"]) | (arr_valid > c["upper_5sigma"]))

    stats_text = (f"Statistics:\n"
                 f"  N: {len(arr_valid)}\n"
                 f"  Within 3σ: {n_within_3} ({100*n_within_3/len(arr_valid):.2f}%)\n"
                 f"  3σ-5σ: {n_between} ({100*n_between/len(arr_valid):.2f}%)\n"
                 f"  Outside 5σ: {n_outside_5} ({100*n_outside_5/len(arr_valid):.2f}%)")

    ax.text(0.02, 0.97, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray'))

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"plot_{param.replace('/', '_').replace(' ', '_')}.png"), dpi=150)
    plt.close()

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 70)
    print("FEMB 1826-1L QC Complete Analysis - ALL Parameters")
    print("=" * 70)

    # Find CSV files
    csv_files = find_1826_1L_csv_files(QC_DATA_ROOT)
    print(f"\nFound {len(csv_files)} CSV files")

    # Get latest passing tests
    all_tests = []
    for csv_path in csv_files:
        board_num = extract_board_number(csv_path)
        if board_num in EXCLUDED_BOARDS:
            continue
        try:
            data, results = load_csv_data(csv_path)
            if check_all_results_pass(results):
                timestamp = extract_timestamp(csv_path)
                all_tests.append({
                    "board_num": board_num,
                    "csv_path": csv_path,
                    "data": data,
                    "timestamp": timestamp
                })
        except:
            pass

    # Keep latest test per board
    latest_tests = {}
    for test in all_tests:
        board_num = test["board_num"]
        if board_num not in latest_tests or test["timestamp"] > latest_tests[board_num]["timestamp"]:
            latest_tests[board_num] = test

    good_boards = sorted(latest_tests.values(), key=lambda x: x["board_num"])
    n_boards = len(good_boards)
    print(f"Using {n_boards} boards (latest tests)")

    all_criteria = {}

    # ==================== 128-CHANNEL PARAMETERS ====================
    print("\n" + "=" * 70)
    print("128-Channel Parameters")
    print("=" * 70)

    for param in PARAMS_128CH:
        all_values = []
        for board in good_boards:
            data = board["data"]
            if param in data and isinstance(data[param], list) and len(data[param]) == 128:
                all_values.extend([float(v) for v in data[param]])
            else:
                all_values.extend([np.nan] * 128)

        arr = np.array(all_values)
        arr_valid = arr[~np.isnan(arr)]

        if len(arr_valid) == 0:
            continue

        mean, std = np.mean(arr_valid), np.std(arr_valid)
        criteria = {
            "mean": mean, "std": std,
            "median": np.median(arr_valid), "mad": np.median(np.abs(arr_valid - np.median(arr_valid))),
            "min": np.min(arr_valid), "max": np.max(arr_valid),
            "lower_3sigma": mean - 3*std, "upper_3sigma": mean + 3*std,
            "lower_5sigma": mean - 5*std, "upper_5sigma": mean + 5*std,
            "n": len(arr_valid), "type": "128ch"
        }
        all_criteria[param] = criteria

        n_outside_5 = np.sum((arr_valid < criteria["lower_5sigma"]) | (arr_valid > criteria["upper_5sigma"]))
        print(f"\n{param} ({PARAM_NAMES.get(param, param)}):")
        print(f"  Mean ± Std: {mean:.2f} ± {std:.2f}")
        print(f"  5σ: [{criteria['lower_5sigma']:.2f}, {criteria['upper_5sigma']:.2f}]")
        print(f"  Outside 5σ: {n_outside_5}")

        plot_parameter(arr, criteria, param, PARAM_NAMES.get(param, param),
                      n_boards, 128, OUTPUT_DIR, "Channel")
        print(f"  Saved plot_{param}.png")

    # ==================== 8-CHIP PARAMETERS ====================
    print("\n" + "=" * 70)
    print("8-Chip Parameters (LDO/Monitor, ASIC)")
    print("=" * 70)

    for param in PARAMS_8CHIP:
        all_values = []
        for board in good_boards:
            data = board["data"]
            if param in data and isinstance(data[param], list) and len(data[param]) == 8:
                all_values.extend([float(v) for v in data[param]])
            else:
                all_values.extend([np.nan] * 8)

        arr = np.array(all_values)
        arr_valid = arr[~np.isnan(arr)]

        if len(arr_valid) == 0:
            continue

        mean, std = np.mean(arr_valid), np.std(arr_valid)
        if std == 0:
            std = 1e-6

        criteria = {
            "mean": mean, "std": std,
            "median": np.median(arr_valid), "mad": np.median(np.abs(arr_valid - np.median(arr_valid))),
            "min": np.min(arr_valid), "max": np.max(arr_valid),
            "lower_3sigma": mean - 3*std, "upper_3sigma": mean + 3*std,
            "lower_5sigma": mean - 5*std, "upper_5sigma": mean + 5*std,
            "n": len(arr_valid), "type": "8chip"
        }
        all_criteria[param] = criteria

        n_outside_5 = np.sum((arr_valid < criteria["lower_5sigma"]) | (arr_valid > criteria["upper_5sigma"]))
        print(f"\n{param} ({PARAM_NAMES.get(param, param)}):")
        print(f"  Mean ± Std: {mean:.4f} ± {std:.4f}")
        print(f"  5σ: [{criteria['lower_5sigma']:.4f}, {criteria['upper_5sigma']:.4f}]")
        print(f"  Outside 5σ: {n_outside_5}")

        plot_parameter(arr, criteria, param, PARAM_NAMES.get(param, param),
                      n_boards, 8, OUTPUT_DIR, "Chip")
        print(f"  Saved plot_{param.replace('/', '_').replace(' ', '_')}.png")

    # ==================== POWER PARAMETERS ====================
    print("\n" + "=" * 70)
    print("Power Parameters")
    print("=" * 70)

    for param in PARAMS_POWER:
        all_values = []
        for board in good_boards:
            data = board["data"]
            if param in data:
                val = data[param]
                if isinstance(val, (int, float)):
                    all_values.append(float(val))
                elif isinstance(val, list) and len(val) > 0:
                    all_values.append(float(val[0]))
                else:
                    all_values.append(np.nan)
            else:
                all_values.append(np.nan)

        arr = np.array(all_values)
        arr_valid = arr[~np.isnan(arr)]

        if len(arr_valid) == 0:
            continue

        mean, std = np.mean(arr_valid), np.std(arr_valid)
        if std == 0:
            std = 1e-6

        criteria = {
            "mean": mean, "std": std,
            "median": np.median(arr_valid), "mad": np.median(np.abs(arr_valid - np.median(arr_valid))),
            "min": np.min(arr_valid), "max": np.max(arr_valid),
            "lower_3sigma": mean - 3*std, "upper_3sigma": mean + 3*std,
            "lower_5sigma": mean - 5*std, "upper_5sigma": mean + 5*std,
            "n": len(arr_valid), "type": "power"
        }
        all_criteria[param] = criteria

        n_outside_5 = np.sum((arr_valid < criteria["lower_5sigma"]) | (arr_valid > criteria["upper_5sigma"]))
        print(f"\n{param} ({PARAM_NAMES.get(param, param)}):")
        print(f"  Mean ± Std: {mean:.4f} ± {std:.4f}")
        print(f"  5σ: [{criteria['lower_5sigma']:.4f}, {criteria['upper_5sigma']:.4f}]")
        print(f"  Outside 5σ: {n_outside_5}")

        plot_parameter(arr, criteria, param, PARAM_NAMES.get(param, param),
                      n_boards, 1, OUTPUT_DIR, "Board")
        print(f"  Saved plot_{param.replace('/', '_').replace(' ', '_')}.png")

    # ==================== SAVE CRITERIA ====================
    csv_path = os.path.join(OUTPUT_DIR, "QC_Criteria_All_Parameters.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Parameter", "Name", "Type", "Mean", "Std", "Median", "MAD",
                        "Lower_3Sigma", "Upper_3Sigma", "Lower_5Sigma", "Upper_5Sigma",
                        "Min", "Max", "N", "N_Boards"])

        for param in PARAMS_128CH + PARAMS_8CHIP + PARAMS_POWER:
            if param in all_criteria:
                c = all_criteria[param]
                writer.writerow([
                    param, PARAM_NAMES.get(param, param), c["type"],
                    f"{c['mean']:.4f}", f"{c['std']:.4f}",
                    f"{c['median']:.4f}", f"{c['mad']:.4f}",
                    f"{c['lower_3sigma']:.4f}", f"{c['upper_3sigma']:.4f}",
                    f"{c['lower_5sigma']:.4f}", f"{c['upper_5sigma']:.4f}",
                    f"{c['min']:.4f}", f"{c['max']:.4f}",
                    c['n'], n_boards
                ])

    print(f"\n\nSaved: {csv_path}")

    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"  Boards: {n_boards}")
    print(f"  128-ch parameters: {len([p for p in PARAMS_128CH if p in all_criteria])}")
    print(f"  8-chip parameters: {len([p for p in PARAMS_8CHIP if p in all_criteria])}")
    print(f"  Power parameters: {len([p for p in PARAMS_POWER if p in all_criteria])}")
    print(f"  Total parameters: {len(all_criteria)}")
    print(f"  Output: {OUTPUT_DIR}")
    print("\nDone!")

if __name__ == "__main__":
    main()
