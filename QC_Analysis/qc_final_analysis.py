#!/usr/bin/env python3
"""
FEMB 1826-1L QC Final Analysis
- Only use the LATEST passing test for each board
- Analyze all 128-channel parameters
- Plot with 3σ and 5σ bands with proper y-axis padding
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

# All 128-channel parameters to analyze
PARAMS_128CH = [
    "ped", "rms",
    "PPK_mean", "NPK_mean", "BL_mean",
    "pedmax", "pedmin",
    "PPK_max", "PPK_min",
    "NPK_max", "NPK_min",
    "BL_max", "BL_min"
]

PARAM_NAMES = {
    "ped": "Pedestal",
    "rms": "RMS Noise",
    "PPK_mean": "Positive Peak Mean",
    "NPK_mean": "Negative Peak Mean",
    "BL_mean": "Baseline Mean",
    "pedmax": "Pedestal Max",
    "pedmin": "Pedestal Min",
    "PPK_max": "Positive Peak Max",
    "PPK_min": "Positive Peak Min",
    "NPK_max": "Negative Peak Max",
    "NPK_min": "Negative Peak Min",
    "BL_max": "Baseline Max",
    "BL_min": "Baseline Min"
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

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 70)
    print("FEMB 1826-1L QC Final Analysis")
    print("=" * 70)

    # Find all CSV files
    csv_files = find_1826_1L_csv_files(QC_DATA_ROOT)
    print(f"\nFound {len(csv_files)} 1826-1L CSV files")

    # Collect all passing tests
    all_tests = []
    for csv_path in csv_files:
        board_num = extract_board_number(csv_path)

        if board_num in EXCLUDED_BOARDS:
            print(f"  Excluding board {board_num} (manual exclusion)")
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
        except Exception as e:
            print(f"  Error loading {csv_path}: {e}")

    print(f"\nTotal passing tests: {len(all_tests)}")

    # Keep only the LATEST test for each board
    latest_tests = {}
    for test in all_tests:
        board_num = test["board_num"]
        if board_num not in latest_tests or test["timestamp"] > latest_tests[board_num]["timestamp"]:
            latest_tests[board_num] = test

    good_boards = list(latest_tests.values())
    good_boards.sort(key=lambda x: x["board_num"])

    print(f"Unique boards (latest test only): {len(good_boards)}")

    # Collect data for all parameters
    all_data = {p: [] for p in PARAMS_128CH}
    board_info = []  # (start_idx, board_num)
    current_idx = 0

    for board in good_boards:
        data = board["data"]
        board_info.append((current_idx, board["board_num"]))

        for param in PARAMS_128CH:
            if param in data and isinstance(data[param], list) and len(data[param]) == 128:
                values = [float(v) for v in data[param]]
                all_data[param].extend(values)
            else:
                # Fill with NaN if missing
                all_data[param].extend([np.nan] * 128)

        current_idx += 128

    # Calculate statistics and criteria
    print("\n" + "=" * 70)
    print("QC Criteria Summary")
    print("=" * 70)

    criteria = {}
    for param in PARAMS_128CH:
        arr = np.array(all_data[param])
        arr = arr[~np.isnan(arr)]  # Remove NaN

        if len(arr) == 0:
            print(f"\n{param}: No data")
            continue

        mean = np.mean(arr)
        std = np.std(arr)
        median = np.median(arr)
        mad = np.median(np.abs(arr - median))

        lower_3sigma = mean - 3 * std
        upper_3sigma = mean + 3 * std
        lower_5sigma = mean - 5 * std
        upper_5sigma = mean + 5 * std

        criteria[param] = {
            "mean": mean, "std": std,
            "median": median, "mad": mad,
            "min": np.min(arr), "max": np.max(arr),
            "lower_3sigma": lower_3sigma, "upper_3sigma": upper_3sigma,
            "lower_5sigma": lower_5sigma, "upper_5sigma": upper_5sigma,
            "n_channels": len(arr)
        }

        n_within_3sigma = np.sum((arr >= lower_3sigma) & (arr <= upper_3sigma))
        n_between = np.sum(((arr < lower_3sigma) & (arr >= lower_5sigma)) |
                           ((arr > upper_3sigma) & (arr <= upper_5sigma)))
        n_outside_5sigma = np.sum((arr < lower_5sigma) | (arr > upper_5sigma))

        print(f"\n{param} ({PARAM_NAMES.get(param, param)}):")
        print(f"  Mean ± Std: {mean:.2f} ± {std:.2f}")
        print(f"  3σ: [{lower_3sigma:.2f}, {upper_3sigma:.2f}]")
        print(f"  5σ: [{lower_5sigma:.2f}, {upper_5sigma:.2f}]")
        print(f"  Range: [{np.min(arr):.2f}, {np.max(arr):.2f}]")
        print(f"  Within 3σ: {n_within_3sigma} ({100*n_within_3sigma/len(arr):.2f}%)")
        print(f"  Outside 5σ: {n_outside_5sigma}")

    # Generate plots
    print("\n" + "=" * 70)
    print("Generating Plots")
    print("=" * 70)

    for param in PARAMS_128CH:
        if param not in criteria:
            continue

        arr = np.array(all_data[param])
        valid_mask = ~np.isnan(arr)
        arr_valid = arr[valid_mask]

        if len(arr_valid) == 0:
            continue

        c = criteria[param]

        fig, ax = plt.subplots(figsize=(16, 8))

        # Calculate y limits with padding (10% on each side)
        data_range = c["max"] - c["min"]
        sigma_range = c["upper_5sigma"] - c["lower_5sigma"]
        total_range = max(data_range, sigma_range)
        padding = total_range * 0.15  # 15% padding

        y_min = min(c["lower_5sigma"], c["min"]) - padding
        y_max = max(c["upper_5sigma"], c["max"]) + padding

        # Draw background bands
        ax.axhspan(y_min, c["lower_5sigma"], alpha=0.25, color='red', label='Outside 5σ (FAIL)')
        ax.axhspan(c["upper_5sigma"], y_max, alpha=0.25, color='red')
        ax.axhspan(c["lower_5sigma"], c["lower_3sigma"], alpha=0.25, color='yellow', label='3σ-5σ (WARNING)')
        ax.axhspan(c["upper_3sigma"], c["upper_5sigma"], alpha=0.25, color='yellow')
        ax.axhspan(c["lower_3sigma"], c["upper_3sigma"], alpha=0.25, color='lightgreen', label='Within 3σ (PASS)')

        # Plot data points
        x = np.arange(len(arr))
        colors = []
        for i, v in enumerate(arr):
            if np.isnan(v):
                colors.append('gray')
            elif v < c["lower_5sigma"] or v > c["upper_5sigma"]:
                colors.append('darkred')
            elif v < c["lower_3sigma"] or v > c["upper_3sigma"]:
                colors.append('darkorange')
            else:
                colors.append('blue')

        ax.scatter(x[valid_mask], arr_valid, c=[colors[i] for i in range(len(arr)) if valid_mask[i]],
                   s=2, alpha=0.6)

        # Draw sigma lines
        ax.axhline(y=c["mean"], color='black', linestyle='-', linewidth=2,
                   label=f'Mean = {c["mean"]:.1f}')
        ax.axhline(y=c["lower_3sigma"], color='green', linestyle='--', linewidth=1.5)
        ax.axhline(y=c["upper_3sigma"], color='green', linestyle='--', linewidth=1.5,
                   label=f'±3σ = [{c["lower_3sigma"]:.1f}, {c["upper_3sigma"]:.1f}]')
        ax.axhline(y=c["lower_5sigma"], color='red', linestyle='--', linewidth=1.5)
        ax.axhline(y=c["upper_5sigma"], color='red', linestyle='--', linewidth=1.5,
                   label=f'±5σ = [{c["lower_5sigma"]:.1f}, {c["upper_5sigma"]:.1f}]')

        # Draw board boundaries
        for idx, board_num in board_info:
            ax.axvline(x=idx, color='gray', linestyle='-', alpha=0.3, linewidth=0.5)

        # Labels
        ax.set_xlabel(f"Channel Index (128 × {len(good_boards)} boards = {len(arr)} channels)", fontsize=12)
        ax.set_ylabel(f"{PARAM_NAMES.get(param, param)} (ADC counts)", fontsize=12)
        ax.set_title(f"{PARAM_NAMES.get(param, param)} Distribution\n"
                    f"1826-1L Latest Tests ({len(good_boards)} boards)", fontsize=14)

        ax.set_xlim(-50, len(arr) + 50)
        ax.set_ylim(y_min, y_max)

        # Legend
        ax.legend(loc='upper right', fontsize=9, framealpha=0.9)

        # Statistics box
        n_within_3 = np.sum((arr_valid >= c["lower_3sigma"]) & (arr_valid <= c["upper_3sigma"]))
        n_between = np.sum(((arr_valid < c["lower_3sigma"]) & (arr_valid >= c["lower_5sigma"])) |
                           ((arr_valid > c["upper_3sigma"]) & (arr_valid <= c["upper_5sigma"])))
        n_outside_5 = np.sum((arr_valid < c["lower_5sigma"]) | (arr_valid > c["upper_5sigma"]))

        stats_text = (f"Statistics:\n"
                     f"  Channels: {len(arr_valid)}\n"
                     f"  Within 3σ: {n_within_3} ({100*n_within_3/len(arr_valid):.2f}%)\n"
                     f"  3σ-5σ: {n_between} ({100*n_between/len(arr_valid):.2f}%)\n"
                     f"  Outside 5σ: {n_outside_5} ({100*n_outside_5/len(arr_valid):.2f}%)")

        ax.text(0.02, 0.97, stats_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray'))

        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, f"plot_{param}.png"), dpi=150)
        plt.close()
        print(f"  Saved plot_{param}.png")

    # Save criteria to CSV
    csv_path = os.path.join(OUTPUT_DIR, "QC_Criteria_Final.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Parameter", "Name", "Mean", "Std", "Median", "MAD",
                        "Lower_3Sigma", "Upper_3Sigma", "Lower_5Sigma", "Upper_5Sigma",
                        "Min", "Max", "N_Channels", "N_Boards"])
        for param in PARAMS_128CH:
            if param in criteria:
                c = criteria[param]
                writer.writerow([
                    param, PARAM_NAMES.get(param, param),
                    f"{c['mean']:.2f}", f"{c['std']:.2f}",
                    f"{c['median']:.2f}", f"{c['mad']:.2f}",
                    f"{c['lower_3sigma']:.2f}", f"{c['upper_3sigma']:.2f}",
                    f"{c['lower_5sigma']:.2f}", f"{c['upper_5sigma']:.2f}",
                    f"{c['min']:.2f}", f"{c['max']:.2f}",
                    c['n_channels'], len(good_boards)
                ])
    print(f"\nSaved: {csv_path}")

    # Save board list
    board_list_path = os.path.join(OUTPUT_DIR, "good_boards_list.txt")
    with open(board_list_path, 'w', encoding='utf-8') as f:
        f.write(f"1826-1L Good Boards - Latest Test Only\n")
        f.write(f"Total: {len(good_boards)} boards\n")
        f.write("=" * 60 + "\n\n")
        for board in good_boards:
            f.write(f"BNL_FEMB_IO-1826-1L_{board['board_num']}  "
                   f"({board['timestamp'].strftime('%Y-%m-%d %H:%M')})\n")
    print(f"Saved: {board_list_path}")

    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"  Total boards: {len(good_boards)}")
    print(f"  Total channels: {len(good_boards) * 128}")
    print(f"  Parameters analyzed: {len(criteria)}")
    print(f"  Output directory: {OUTPUT_DIR}")
    print("\nDone!")

if __name__ == "__main__":
    main()
