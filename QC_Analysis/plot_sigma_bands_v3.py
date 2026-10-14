#!/usr/bin/env python3
"""
Plot QC parameters with 3σ and 5σ background bands
- Only use the LATEST passing test for each board
"""

import os
import csv
import ast
import re
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

QC_DATA_ROOT = "/home/dune/Documents/data/FEMB_QC/Report"
OUTPUT_DIR = "/home/dune/PycharmProjects/BNL_CE_Checkout/QC_Analysis/output_1826_1L"
EXCLUDED_BOARDS = ["00046"]

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
    """Extract timestamp from path like Time_2026_08/03_22_20_20_..."""
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
    print("Plotting with 3σ and 5σ (V3 - Only LATEST passing test per board)")
    print("=" * 70)

    csv_files = find_1826_1L_csv_files(QC_DATA_ROOT)
    print(f"\nFound {len(csv_files)} 1826-1L CSV files")

    # Collect all passing tests with timestamps
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
        except Exception as e:
            print(f"  Error: {e}")

    print(f"\nTotal passing tests: {len(all_tests)}")

    # Keep only the LATEST test for each board
    latest_tests = {}
    for test in all_tests:
        board_num = test["board_num"]
        if board_num not in latest_tests or test["timestamp"] > latest_tests[board_num]["timestamp"]:
            latest_tests[board_num] = test

    good_boards = list(latest_tests.values())
    print(f"Unique boards (latest test only): {len(good_boards)}")

    # Show which tests are used
    print("\nUsing latest tests:")
    for board_num in sorted(latest_tests.keys()):
        t = latest_tests[board_num]
        print(f"  {board_num}: {t['timestamp'].strftime('%Y-%m-%d %H:%M')}")

    # Parameters
    params = ["ped", "rms", "PPK_mean", "NPK_mean", "BL_mean"]
    param_names = {
        "ped": "Pedestal",
        "rms": "RMS Noise",
        "PPK_mean": "Positive Peak (PPK)",
        "NPK_mean": "Negative Peak (NPK)",
        "BL_mean": "Baseline (BL)"
    }

    # Collect data
    all_data = {p: [] for p in params}
    board_boundaries = []
    current_idx = 0

    for board in sorted(good_boards, key=lambda x: x["board_num"]):
        data = board["data"]
        board_boundaries.append((current_idx, board["board_num"]))

        for param in params:
            if param in data and isinstance(data[param], list) and len(data[param]) == 128:
                values = [float(v) for v in data[param]]
                all_data[param].extend(values)

        current_idx += 128

    # Calculate statistics
    print("\n" + "=" * 70)
    print("QC Criteria (Latest Test Only)")
    print("=" * 70)

    criteria = {}
    for param in params:
        if not all_data[param]:
            continue

        arr = np.array(all_data[param])
        mean = np.mean(arr)
        std = np.std(arr)

        lower_3sigma = mean - 3 * std
        upper_3sigma = mean + 3 * std
        lower_5sigma = mean - 5 * std
        upper_5sigma = mean + 5 * std

        criteria[param] = {
            "mean": mean, "std": std,
            "lower_3sigma": lower_3sigma, "upper_3sigma": upper_3sigma,
            "lower_5sigma": lower_5sigma, "upper_5sigma": upper_5sigma,
            "min": np.min(arr), "max": np.max(arr)
        }

        n_within_3sigma = np.sum((arr >= lower_3sigma) & (arr <= upper_3sigma))
        n_between = np.sum(((arr < lower_3sigma) & (arr >= lower_5sigma)) |
                           ((arr > upper_3sigma) & (arr <= upper_5sigma)))
        n_outside_5sigma = np.sum((arr < lower_5sigma) | (arr > upper_5sigma))

        print(f"\n{param}:")
        print(f"  Mean ± Std: {mean:.2f} ± {std:.2f}")
        print(f"  5σ Range: [{lower_5sigma:.2f}, {upper_5sigma:.2f}]")
        print(f"  Actual: [{np.min(arr):.2f}, {np.max(arr):.2f}]")
        print(f"  Within 3σ: {n_within_3sigma} ({100*n_within_3sigma/len(arr):.2f}%)")
        print(f"  3σ-5σ: {n_between} ({100*n_between/len(arr):.2f}%)")
        print(f"  Outside 5σ: {n_outside_5sigma} ({100*n_outside_5sigma/len(arr):.2f}%)")

    # Create plots
    print("\nGenerating plots...")
    for param in params:
        if not all_data[param]:
            continue

        arr = np.array(all_data[param])
        c = criteria[param]

        fig, ax = plt.subplots(figsize=(16, 8))

        y_min = min(c["lower_5sigma"], c["min"]) - 0.1 * c["std"]
        y_max = max(c["upper_5sigma"], c["max"]) + 0.1 * c["std"]

        # Background bands
        ax.axhspan(y_min, c["lower_5sigma"], alpha=0.3, color='red', label='Outside 5σ (FAIL)')
        ax.axhspan(c["upper_5sigma"], y_max, alpha=0.3, color='red')
        ax.axhspan(c["lower_5sigma"], c["lower_3sigma"], alpha=0.3, color='yellow', label='3σ-5σ (WARNING)')
        ax.axhspan(c["upper_3sigma"], c["upper_5sigma"], alpha=0.3, color='yellow')
        ax.axhspan(c["lower_3sigma"], c["upper_3sigma"], alpha=0.3, color='lightgreen', label='Within 3σ (PASS)')

        x = np.arange(len(arr))
        colors = ['darkred' if (v < c["lower_5sigma"] or v > c["upper_5sigma"]) else
                  'orange' if (v < c["lower_3sigma"] or v > c["upper_3sigma"]) else
                  'blue' for v in arr]

        ax.scatter(x, arr, c=colors, s=1, alpha=0.6)

        ax.axhline(y=c["mean"], color='black', linestyle='-', linewidth=2, label=f'Mean={c["mean"]:.1f}')
        ax.axhline(y=c["lower_3sigma"], color='green', linestyle='--', linewidth=1.5)
        ax.axhline(y=c["upper_3sigma"], color='green', linestyle='--', linewidth=1.5, label=f'±3σ')
        ax.axhline(y=c["lower_5sigma"], color='red', linestyle='--', linewidth=1.5)
        ax.axhline(y=c["upper_5sigma"], color='red', linestyle='--', linewidth=1.5, label=f'±5σ')

        for idx, board_num in board_boundaries:
            ax.axvline(x=idx, color='gray', linestyle='-', alpha=0.2, linewidth=0.5)

        ax.set_xlabel(f"Channel (128 × {len(good_boards)} boards)", fontsize=12)
        ax.set_ylabel(f"{param_names[param]} (ADC)", fontsize=12)
        ax.set_title(f"{param_names[param]} - Latest Test Only ({len(good_boards)} boards)", fontsize=14)
        ax.set_xlim(0, len(arr))
        ax.set_ylim(y_min, y_max)
        ax.legend(loc='upper right', fontsize=10)

        n_out = np.sum((arr < c["lower_5sigma"]) | (arr > c["upper_5sigma"]))
        stats = f"Within 3σ: {100*np.sum((arr >= c['lower_3sigma']) & (arr <= c['upper_3sigma']))/len(arr):.2f}%\nOutside 5σ: {n_out}"
        ax.text(0.02, 0.98, stats, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, f"sigma_bands_{param}_v3.png"), dpi=150)
        plt.close()
        print(f"  Saved sigma_bands_{param}_v3.png")

    # Save criteria
    csv_out = os.path.join(OUTPUT_DIR, "QC_Criteria_5Sigma_v3.csv")
    with open(csv_out, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Parameter", "Mean", "Std", "Lower_3Sigma", "Upper_3Sigma",
                        "Lower_5Sigma", "Upper_5Sigma", "Min", "Max", "N_Boards"])
        for param in params:
            c = criteria[param]
            writer.writerow([param, f"{c['mean']:.2f}", f"{c['std']:.2f}",
                           f"{c['lower_3sigma']:.2f}", f"{c['upper_3sigma']:.2f}",
                           f"{c['lower_5sigma']:.2f}", f"{c['upper_5sigma']:.2f}",
                           f"{c['min']:.2f}", f"{c['max']:.2f}", len(good_boards)])

    # Save board list
    with open(os.path.join(OUTPUT_DIR, "good_boards_list_v3.txt"), 'w') as f:
        f.write(f"1826-1L Good Boards - Latest Test Only ({len(good_boards)} boards)\n")
        f.write("=" * 60 + "\n")
        for board_num in sorted(latest_tests.keys()):
            t = latest_tests[board_num]
            f.write(f"BNL_FEMB_IO-1826-1L_{board_num}  ({t['timestamp'].strftime('%Y-%m-%d %H:%M')})\n")

    print(f"\nSaved: {csv_out}")
    print("Done!")

if __name__ == "__main__":
    main()
