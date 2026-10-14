#!/usr/bin/env python3
"""
FEMB 1826-1L QC Complete Analysis - ALL Parameters Including LDO and Currents
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

# LDO parameters (single value per board per test stage)
PARAMS_LDO = [
    "CDVDDA", "CDVDDIO_HALF",
    "ADCRVDDD1P2", "ADCLVDDD1P2",
    "FERVDDP", "FELVDDP",
    "ADCRP25V_1_HALF", "ADCLP25V_1_HALF",
    "ADCRP25V_HALF", "ADCLP25V_HALF",
    "GND"
]

# ASIC parameters (8 chips)
PARAMS_ASIC = ["FE T", "FE BGP", "ADC_VCMI", "ADC_VCMO", "ADC_VREFP", "ADC_VREFN", "VSSA"]

PARAM_NAMES = {
    # 128-channel
    "ped": "Pedestal", "rms": "RMS Noise",
    "PPK_mean": "Positive Peak", "NPK_mean": "Negative Peak", "BL_mean": "Baseline",
    "pedmax": "Pedestal Max", "pedmin": "Pedestal Min",
    # LDO
    "CDVDDA": "COLDATA VDDA", "CDVDDIO_HALF": "COLDATA VDDIO/2",
    "ADCRVDDD1P2": "ADC-R VDDD 1.2V", "ADCLVDDD1P2": "ADC-L VDDD 1.2V",
    "FERVDDP": "FE-R VDDP", "FELVDDP": "FE-L VDDP",
    "ADCRP25V_1_HALF": "ADC-R P25V_1/2", "ADCLP25V_1_HALF": "ADC-L P25V_1/2",
    "ADCRP25V_HALF": "ADC-R P25V/2", "ADCLP25V_HALF": "ADC-L P25V/2",
    "GND": "Ground",
    # ASIC
    "FE T": "FE Temperature", "FE BGP": "FE Bandgap",
    "ADC_VCMI": "ADC VCMI", "ADC_VCMO": "ADC VCMO",
    "ADC_VREFP": "ADC VREFP", "ADC_VREFN": "ADC VREFN", "VSSA": "VSSA",
    # Current per rail
    "I_LArASIC_ped": "I LArASIC (Ped)", "I_ColdDATA_ped": "I ColdDATA (Ped)", "I_ColdADC_ped": "I ColdADC (Ped)",
    "I_LArASIC_pulse": "I LArASIC (Pulse)", "I_ColdDATA_pulse": "I ColdDATA (Pulse)", "I_ColdADC_pulse": "I ColdADC (Pulse)",
    "Total_Power_ped": "Total Power (Ped)", "Total_Power_pulse": "Total Power (Pulse)"
}

def parse_list_string(s):
    if not s or s == '':
        return []
    try:
        result = ast.literal_eval(s)
        if isinstance(result, list):
            return [float(x) if x != '' else np.nan for x in result]
        return []
    except:
        return []

def load_csv_full(csv_path):
    """Load CSV and extract all data including multiple test stages."""
    data = {"128ch": {}, "ldo_ped": {}, "ldo_pulse": {}, "asic": {}, "current": {}, "power": {}}
    results = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_stage = None  # Track which test stage we're in
    i_meas_count = 0

    for line in lines:
        parts = line.strip().split(',', 1)
        if len(parts) < 2:
            continue
        key = parts[0]
        value = parts[1].strip('"')

        if key == "Result":
            results.append(value)

        # Track test stage by counting I_meas/A occurrences
        if key == "I_meas/A":
            i_meas_count += 1
            i_list = parse_list_string(value)
            if len(i_list) >= 4:
                if i_meas_count == 1:
                    # First I_meas is power-on check (skip)
                    pass
                elif i_meas_count == 2:
                    # Second I_meas is pedestal check
                    current_stage = "ped"
                    data["current"]["I_LArASIC_ped"] = i_list[1]
                    data["current"]["I_ColdDATA_ped"] = i_list[2]
                    data["current"]["I_ColdADC_ped"] = i_list[3]
                elif i_meas_count == 3:
                    # Third I_meas is pulse check
                    current_stage = "pulse"
                    data["current"]["I_LArASIC_pulse"] = i_list[1]
                    data["current"]["I_ColdDATA_pulse"] = i_list[2]
                    data["current"]["I_ColdADC_pulse"] = i_list[3]

        # Total Power
        if key == "Total Power":
            tp_list = parse_list_string(value)
            if tp_list and not np.isnan(tp_list[0]):
                if i_meas_count == 2:
                    data["power"]["Total_Power_ped"] = tp_list[0]
                elif i_meas_count == 3:
                    data["power"]["Total_Power_pulse"] = tp_list[0]

        # 128-channel parameters
        if key in PARAMS_128CH:
            parsed = parse_list_string(value)
            if len(parsed) == 128:
                data["128ch"][key] = parsed

        # LDO parameters
        if key in PARAMS_LDO:
            try:
                val = float(value)
                if current_stage == "ped" or i_meas_count == 2:
                    data["ldo_ped"][key] = val
                elif current_stage == "pulse" or i_meas_count == 3:
                    data["ldo_pulse"][key] = val
            except:
                pass

        # ASIC parameters (8 chips)
        if key in PARAMS_ASIC:
            parsed = parse_list_string(value)
            if len(parsed) == 8:
                data["asic"][key] = parsed

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

def plot_parameter(arr, criteria, param, param_name, n_boards, n_items_per_board, output_dir, item_label="Channel", use_7sigma=False):
    c = criteria
    fig, ax = plt.subplots(figsize=(16, 8))

    data_range = c["max"] - c["min"]
    if use_7sigma:
        sigma_range = c["upper_7sigma"] - c["lower_7sigma"]
    else:
        sigma_range = c["upper_5sigma"] - c["lower_5sigma"]
    total_range = max(data_range, sigma_range)
    padding = total_range * 0.15

    if use_7sigma:
        y_min = min(c["lower_7sigma"], c["min"]) - padding
        y_max = max(c["upper_7sigma"], c["max"]) + padding

        # 7σ bands for power rail parameters
        ax.axhspan(y_min, c["lower_7sigma"], alpha=0.25, color='darkred', label='Outside 7σ (FAIL)')
        ax.axhspan(c["upper_7sigma"], y_max, alpha=0.25, color='darkred')
        ax.axhspan(c["lower_7sigma"], c["lower_5sigma"], alpha=0.2, color='red', label='5σ-7σ')
        ax.axhspan(c["upper_5sigma"], c["upper_7sigma"], alpha=0.2, color='red')
        ax.axhspan(c["lower_5sigma"], c["lower_3sigma"], alpha=0.25, color='yellow', label='3σ-5σ')
        ax.axhspan(c["upper_3sigma"], c["upper_5sigma"], alpha=0.25, color='yellow')
        ax.axhspan(c["lower_3sigma"], c["upper_3sigma"], alpha=0.25, color='lightgreen', label='Within 3σ')
    else:
        y_min = min(c["lower_5sigma"], c["min"]) - padding
        y_max = max(c["upper_5sigma"], c["max"]) + padding

        ax.axhspan(y_min, c["lower_5sigma"], alpha=0.25, color='red', label='Outside 5σ (FAIL)')
        ax.axhspan(c["upper_5sigma"], y_max, alpha=0.25, color='red')
        ax.axhspan(c["lower_5sigma"], c["lower_3sigma"], alpha=0.25, color='yellow', label='3σ-5σ (WARNING)')
        ax.axhspan(c["upper_3sigma"], c["upper_5sigma"], alpha=0.25, color='yellow')
        ax.axhspan(c["lower_3sigma"], c["upper_3sigma"], alpha=0.25, color='lightgreen', label='Within 3σ (PASS)')

    x = np.arange(len(arr))
    valid_mask = ~np.isnan(arr)
    arr_valid = arr[valid_mask]

    # Color points based on sigma bounds
    if use_7sigma:
        colors = []
        for v in arr:
            if np.isnan(v):
                colors.append('gray')
            elif v < c["lower_7sigma"] or v > c["upper_7sigma"]:
                colors.append('darkred')
            elif v < c["lower_5sigma"] or v > c["upper_5sigma"]:
                colors.append('red')
            elif v < c["lower_3sigma"] or v > c["upper_3sigma"]:
                colors.append('darkorange')
            else:
                colors.append('blue')
    else:
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

    ax.axhline(y=c["mean"], color='black', linestyle='-', linewidth=2, label=f'Mean = {c["mean"]:.2f}')
    ax.axhline(y=c["lower_3sigma"], color='green', linestyle='--', linewidth=1.5)
    ax.axhline(y=c["upper_3sigma"], color='green', linestyle='--', linewidth=1.5, label=f'±3σ')
    ax.axhline(y=c["lower_5sigma"], color='orange', linestyle='--', linewidth=1.5)
    ax.axhline(y=c["upper_5sigma"], color='orange', linestyle='--', linewidth=1.5, label=f'±5σ')

    if use_7sigma:
        ax.axhline(y=c["lower_7sigma"], color='red', linestyle='--', linewidth=1.5)
        ax.axhline(y=c["upper_7sigma"], color='red', linestyle='--', linewidth=1.5, label=f'±7σ')

    for i in range(n_boards + 1):
        ax.axvline(x=i * n_items_per_board, color='gray', linestyle='-', alpha=0.3, linewidth=0.5)

    ax.set_xlabel(f"{item_label} Index ({n_items_per_board} × {n_boards} = {len(arr)})", fontsize=12)
    ax.set_ylabel(f"{param_name}", fontsize=12)
    ax.set_title(f"{param_name} Distribution - 1826-1L ({n_boards} boards)", fontsize=14)

    ax.set_xlim(-len(arr)*0.01, len(arr)*1.01)
    ax.set_ylim(y_min, y_max)
    ax.legend(loc='upper right', fontsize=9, framealpha=0.9)

    n_within_3 = np.sum((arr_valid >= c["lower_3sigma"]) & (arr_valid <= c["upper_3sigma"]))
    if use_7sigma:
        n_outside_7 = np.sum((arr_valid < c["lower_7sigma"]) | (arr_valid > c["upper_7sigma"]))
        stats = f"N: {len(arr_valid)} | Within 3σ: {100*n_within_3/len(arr_valid):.1f}% | Outside 7σ: {n_outside_7}"
    else:
        n_outside_5 = np.sum((arr_valid < c["lower_5sigma"]) | (arr_valid > c["upper_5sigma"]))
        stats = f"N: {len(arr_valid)} | Within 3σ: {100*n_within_3/len(arr_valid):.1f}% | Outside 5σ: {n_outside_5}"

    ax.text(0.02, 0.97, stats, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

    plt.tight_layout()
    safe_name = param.replace('/', '_').replace(' ', '_')
    plt.savefig(os.path.join(output_dir, f"plot_{safe_name}.png"), dpi=150)
    plt.close()

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 70)
    print("FEMB 1826-1L Complete QC Analysis")
    print("Including LDO and Current Parameters")
    print("=" * 70)

    csv_files = find_1826_1L_csv_files(QC_DATA_ROOT)
    print(f"\nFound {len(csv_files)} CSV files")

    # Get latest passing tests
    all_tests = []
    for csv_path in csv_files:
        board_num = extract_board_number(csv_path)
        if board_num in EXCLUDED_BOARDS:
            continue
        try:
            data, results = load_csv_full(csv_path)
            if check_all_results_pass(results):
                timestamp = extract_timestamp(csv_path)
                all_tests.append({
                    "board_num": board_num,
                    "data": data,
                    "timestamp": timestamp
                })
        except Exception as e:
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
            if param in board["data"]["128ch"]:
                all_values.extend(board["data"]["128ch"][param])
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
            "lower_7sigma": mean - 7*std, "upper_7sigma": mean + 7*std,
            "n": len(arr_valid), "type": "128ch"
        }
        all_criteria[param] = criteria

        n_outside_5 = np.sum((arr_valid < criteria["lower_5sigma"]) | (arr_valid > criteria["upper_5sigma"]))
        print(f"{param}: Mean={mean:.2f}, Std={std:.2f}, Outside 5σ={n_outside_5}")

        plot_parameter(arr, criteria, param, PARAM_NAMES.get(param, param), n_boards, 128, OUTPUT_DIR, "Channel", use_7sigma=False)

    # ==================== LDO PARAMETERS (Pedestal Check) ====================
    print("\n" + "=" * 70)
    print("LDO Parameters (Pedestal Check)")
    print("=" * 70)

    for param in PARAMS_LDO:
        all_values = [board["data"]["ldo_ped"].get(param, np.nan) for board in good_boards]
        arr = np.array(all_values)
        arr_valid = arr[~np.isnan(arr)]
        if len(arr_valid) == 0:
            continue

        mean, std = np.mean(arr_valid), np.std(arr_valid) if np.std(arr_valid) > 0 else 1e-6
        criteria = {
            "mean": mean, "std": std,
            "median": np.median(arr_valid), "mad": np.median(np.abs(arr_valid - np.median(arr_valid))),
            "min": np.min(arr_valid), "max": np.max(arr_valid),
            "lower_3sigma": mean - 3*std, "upper_3sigma": mean + 3*std,
            "lower_5sigma": mean - 5*std, "upper_5sigma": mean + 5*std,
            "lower_7sigma": mean - 7*std, "upper_7sigma": mean + 7*std,
            "n": len(arr_valid), "type": "ldo_ped"
        }
        param_key = f"{param}_ped"
        all_criteria[param_key] = criteria

        n_outside_7 = np.sum((arr_valid < criteria["lower_7sigma"]) | (arr_valid > criteria["upper_7sigma"]))
        print(f"{param}: Mean={mean:.2f}, Std={std:.2f}, Outside 7σ={n_outside_7}")

        plot_parameter(arr, criteria, param_key, f"{PARAM_NAMES.get(param, param)} (Ped)", n_boards, 1, OUTPUT_DIR, "Board", use_7sigma=True)

    # ==================== LDO PARAMETERS (Pulse Check) ====================
    print("\n" + "=" * 70)
    print("LDO Parameters (Pulse Check)")
    print("=" * 70)

    for param in PARAMS_LDO:
        all_values = [board["data"]["ldo_pulse"].get(param, np.nan) for board in good_boards]
        arr = np.array(all_values)
        arr_valid = arr[~np.isnan(arr)]
        if len(arr_valid) == 0:
            continue

        mean, std = np.mean(arr_valid), np.std(arr_valid) if np.std(arr_valid) > 0 else 1e-6
        criteria = {
            "mean": mean, "std": std,
            "median": np.median(arr_valid), "mad": np.median(np.abs(arr_valid - np.median(arr_valid))),
            "min": np.min(arr_valid), "max": np.max(arr_valid),
            "lower_3sigma": mean - 3*std, "upper_3sigma": mean + 3*std,
            "lower_5sigma": mean - 5*std, "upper_5sigma": mean + 5*std,
            "lower_7sigma": mean - 7*std, "upper_7sigma": mean + 7*std,
            "n": len(arr_valid), "type": "ldo_pulse"
        }
        param_key = f"{param}_pulse"
        all_criteria[param_key] = criteria

        n_outside_7 = np.sum((arr_valid < criteria["lower_7sigma"]) | (arr_valid > criteria["upper_7sigma"]))
        print(f"{param}: Mean={mean:.2f}, Std={std:.2f}, Outside 7σ={n_outside_7}")

        plot_parameter(arr, criteria, param_key, f"{PARAM_NAMES.get(param, param)} (Pulse)", n_boards, 1, OUTPUT_DIR, "Board", use_7sigma=True)

    # ==================== CURRENT PARAMETERS ====================
    print("\n" + "=" * 70)
    print("Current Parameters")
    print("=" * 70)

    current_params = ["I_LArASIC_ped", "I_ColdDATA_ped", "I_ColdADC_ped",
                      "I_LArASIC_pulse", "I_ColdDATA_pulse", "I_ColdADC_pulse"]

    for param in current_params:
        all_values = [board["data"]["current"].get(param, np.nan) for board in good_boards]
        arr = np.array(all_values)
        arr_valid = arr[~np.isnan(arr)]
        if len(arr_valid) == 0:
            continue

        mean, std = np.mean(arr_valid), np.std(arr_valid) if np.std(arr_valid) > 0 else 1e-6
        criteria = {
            "mean": mean, "std": std,
            "median": np.median(arr_valid), "mad": np.median(np.abs(arr_valid - np.median(arr_valid))),
            "min": np.min(arr_valid), "max": np.max(arr_valid),
            "lower_3sigma": mean - 3*std, "upper_3sigma": mean + 3*std,
            "lower_5sigma": mean - 5*std, "upper_5sigma": mean + 5*std,
            "lower_7sigma": mean - 7*std, "upper_7sigma": mean + 7*std,
            "n": len(arr_valid), "type": "current"
        }
        all_criteria[param] = criteria

        n_outside_7 = np.sum((arr_valid < criteria["lower_7sigma"]) | (arr_valid > criteria["upper_7sigma"]))
        print(f"{param}: Mean={mean:.4f}A, Std={std:.4f}, Outside 7σ={n_outside_7}")

        plot_parameter(arr, criteria, param, PARAM_NAMES.get(param, param), n_boards, 1, OUTPUT_DIR, "Board", use_7sigma=True)

    # ==================== POWER PARAMETERS ====================
    print("\n" + "=" * 70)
    print("Power Parameters")
    print("=" * 70)

    power_params = ["Total_Power_ped", "Total_Power_pulse"]

    for param in power_params:
        all_values = [board["data"]["power"].get(param, np.nan) for board in good_boards]
        arr = np.array(all_values)
        arr_valid = arr[~np.isnan(arr)]
        if len(arr_valid) == 0:
            continue

        mean, std = np.mean(arr_valid), np.std(arr_valid) if np.std(arr_valid) > 0 else 1e-6
        criteria = {
            "mean": mean, "std": std,
            "median": np.median(arr_valid), "mad": np.median(np.abs(arr_valid - np.median(arr_valid))),
            "min": np.min(arr_valid), "max": np.max(arr_valid),
            "lower_3sigma": mean - 3*std, "upper_3sigma": mean + 3*std,
            "lower_5sigma": mean - 5*std, "upper_5sigma": mean + 5*std,
            "lower_7sigma": mean - 7*std, "upper_7sigma": mean + 7*std,
            "n": len(arr_valid), "type": "power"
        }
        all_criteria[param] = criteria

        n_outside_7 = np.sum((arr_valid < criteria["lower_7sigma"]) | (arr_valid > criteria["upper_7sigma"]))
        print(f"{param}: Mean={mean:.3f}W, Std={std:.4f}, Outside 7σ={n_outside_7}")

        plot_parameter(arr, criteria, param, PARAM_NAMES.get(param, param), n_boards, 1, OUTPUT_DIR, "Board", use_7sigma=True)

    # ==================== ASIC PARAMETERS (8 chips) ====================
    print("\n" + "=" * 70)
    print("ASIC Parameters (8 chips)")
    print("=" * 70)

    for param in PARAMS_ASIC:
        all_values = []
        for board in good_boards:
            if param in board["data"]["asic"]:
                all_values.extend(board["data"]["asic"][param])
            else:
                all_values.extend([np.nan] * 8)

        arr = np.array(all_values)
        arr_valid = arr[~np.isnan(arr)]
        if len(arr_valid) == 0:
            continue

        mean, std = np.mean(arr_valid), np.std(arr_valid) if np.std(arr_valid) > 0 else 1e-6
        criteria = {
            "mean": mean, "std": std,
            "median": np.median(arr_valid), "mad": np.median(np.abs(arr_valid - np.median(arr_valid))),
            "min": np.min(arr_valid), "max": np.max(arr_valid),
            "lower_3sigma": mean - 3*std, "upper_3sigma": mean + 3*std,
            "lower_5sigma": mean - 5*std, "upper_5sigma": mean + 5*std,
            "lower_7sigma": mean - 7*std, "upper_7sigma": mean + 7*std,
            "n": len(arr_valid), "type": "8chip"
        }
        all_criteria[param] = criteria

        n_outside_5 = np.sum((arr_valid < criteria["lower_5sigma"]) | (arr_valid > criteria["upper_5sigma"]))
        print(f"{param}: Mean={mean:.2f}, Std={std:.2f}, Outside 5σ={n_outside_5}")

        plot_parameter(arr, criteria, param, PARAM_NAMES.get(param, param), n_boards, 8, OUTPUT_DIR, "Chip", use_7sigma=False)

    # ==================== SAVE ALL CRITERIA ====================
    csv_path = os.path.join(OUTPUT_DIR, "QC_Criteria_Complete.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Parameter", "Name", "Type", "Mean", "Std", "Median", "MAD",
                        "Lower_3Sigma", "Upper_3Sigma", "Lower_5Sigma", "Upper_5Sigma",
                        "Lower_7Sigma", "Upper_7Sigma", "Min", "Max", "N", "N_Boards"])
        for param, c in all_criteria.items():
            writer.writerow([
                param, PARAM_NAMES.get(param, param), c["type"],
                f"{c['mean']:.4f}", f"{c['std']:.4f}",
                f"{c['median']:.4f}", f"{c['mad']:.4f}",
                f"{c['lower_3sigma']:.4f}", f"{c['upper_3sigma']:.4f}",
                f"{c['lower_5sigma']:.4f}", f"{c['upper_5sigma']:.4f}",
                f"{c['lower_7sigma']:.4f}", f"{c['upper_7sigma']:.4f}",
                f"{c['min']:.4f}", f"{c['max']:.4f}",
                c['n'], n_boards
            ])

    print(f"\n\nSaved: {csv_path}")

    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"  Boards: {n_boards}")
    print(f"  Total parameters: {len(all_criteria)}")

    type_counts = {}
    for c in all_criteria.values():
        t = c["type"]
        type_counts[t] = type_counts.get(t, 0) + 1
    for t, count in sorted(type_counts.items()):
        print(f"    {t}: {count}")

    print(f"  Output: {OUTPUT_DIR}")
    print("\nDone!")

if __name__ == "__main__":
    main()
