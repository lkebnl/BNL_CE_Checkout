#!/usr/bin/env python3
"""
FEMB 1826-1L QC Criteria Generator
- Only use 1826-1L version boards
- Exclude boards with outliers
- Generate QC criteria based on good boards only
"""

import os
import csv
import ast
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import json

# Configuration
QC_DATA_ROOT = "/home/dune/Documents/data/FEMB_QC/Report"
OUTPUT_DIR = "/home/dune/PycharmProjects/BNL_CE_Checkout/QC_Analysis/output_1826_1L"

def parse_list_string(s):
    """Parse a string representation of a list into actual list."""
    if not s or s == '':
        return []
    try:
        return ast.literal_eval(s)
    except:
        return []

def load_csv_data(csv_path):
    """Load and parse FEMB checkout CSV file."""
    data = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                key = row[0]
                value = row[1]
                parsed = parse_list_string(value)
                if parsed:
                    data[key] = parsed
                else:
                    data[key] = value
    return data

def detect_outliers_mad(data, threshold=3.5):
    """Detect outliers using MAD method."""
    data = np.array(data, dtype=float)
    median = np.median(data)
    mad = np.median(np.abs(data - median))
    if mad == 0:
        mad = 1e-6
    modified_z_scores = 0.6745 * (data - median) / mad
    outliers = np.where(np.abs(modified_z_scores) > threshold)[0]
    return outliers.tolist(), median, mad

def find_1826_1L_csv_files(root_dir):
    """Find all 1826-1L FEMB checkout CSV files."""
    csv_files = []
    for root, dirs, files in os.walk(root_dir):
        for f in files:
            if "1826-1L" in f and f.startswith("DataBase_FEMB_") and f.endswith(".csv"):
                csv_files.append(os.path.join(root, f))
    return csv_files

def extract_femb_id(csv_path):
    """Extract FEMB ID from CSV path."""
    filename = os.path.basename(csv_path)
    parts = filename.replace("DataBase_FEMB_", "").replace(".csv", "").rsplit("_", 2)
    if parts:
        return parts[0]
    return filename

def check_board_has_outliers(data, params=["ped", "rms", "PPK_mean", "NPK_mean", "BL_mean"]):
    """Check if board has any outlier channels."""
    for param in params:
        if param in data and isinstance(data[param], list) and len(data[param]) == 128:
            values = [float(v) for v in data[param]]
            outliers, median, mad = detect_outliers_mad(values, threshold=3.5)
            if outliers:
                return True, param, outliers
    return False, None, []

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 60)
    print("FEMB 1826-1L QC Criteria Generator")
    print("=" * 60)

    # Find all 1826-1L CSV files
    csv_files = find_1826_1L_csv_files(QC_DATA_ROOT)
    print(f"\n找到 {len(csv_files)} 个 1826-1L 板子的CSV文件")

    # First pass: identify boards with outliers
    good_boards = []
    bad_boards = []

    print("\n第一轮：识别有问题的板子...")
    for csv_path in csv_files:
        femb_id = extract_femb_id(csv_path)
        try:
            data = load_csv_data(csv_path)
            has_outlier, param, channels = check_board_has_outliers(data)
            if has_outlier:
                bad_boards.append({
                    "femb_id": femb_id,
                    "csv_path": csv_path,
                    "param": param,
                    "channels": channels,
                    "data": data
                })
            else:
                good_boards.append({
                    "femb_id": femb_id,
                    "csv_path": csv_path,
                    "data": data
                })
        except Exception as e:
            print(f"  Error loading {csv_path}: {e}")

    print(f"\n统计结果：")
    print(f"  好的板子: {len(good_boards)}")
    print(f"  有问题的板子: {len(bad_boards)}")

    # Print bad boards
    print(f"\n有问题的板子列表：")
    for b in bad_boards:
        print(f"  {b['femb_id']}: {b['param']} 通道 {b['channels']}")

    # Second pass: calculate statistics from good boards only
    print(f"\n第二轮：基于 {len(good_boards)} 块好板子计算QC标准...")

    # Collect all data from good boards
    all_data = {
        "rms": [],
        "ped": [],
        "PPK_mean": [],
        "NPK_mean": [],
        "BL_mean": []
    }

    for board in good_boards:
        data = board["data"]
        for param in all_data.keys():
            if param in data and isinstance(data[param], list) and len(data[param]) == 128:
                values = [float(v) for v in data[param]]
                all_data[param].extend(values)

    # Calculate statistics and criteria
    criteria = {}
    print("\n" + "=" * 60)
    print("QC标准 (基于好板子)")
    print("=" * 60)

    for param, values in all_data.items():
        if values:
            arr = np.array(values)
            mean = np.mean(arr)
            std = np.std(arr)
            median = np.median(arr)
            mad = np.median(np.abs(arr - median))
            min_val = np.min(arr)
            max_val = np.max(arr)

            # Calculate criteria (Mean ± 3σ)
            lower_3sigma = mean - 3 * std
            upper_3sigma = mean + 3 * std

            # Calculate criteria (Median ± 3.5*MAD/0.6745)
            lower_mad = median - 3.5 * mad / 0.6745
            upper_mad = median + 3.5 * mad / 0.6745

            criteria[param] = {
                "mean": round(mean, 2),
                "std": round(std, 2),
                "median": round(median, 2),
                "mad": round(mad, 2),
                "min": round(min_val, 2),
                "max": round(max_val, 2),
                "lower_3sigma": round(lower_3sigma, 2),
                "upper_3sigma": round(upper_3sigma, 2),
                "lower_mad": round(lower_mad, 2),
                "upper_mad": round(upper_mad, 2),
                "n_channels": len(values),
                "n_boards": len(values) // 128
            }

            print(f"\n{param}:")
            print(f"  样本数: {len(values)} 通道 ({len(values)//128} 块板)")
            print(f"  Mean ± Std: {mean:.2f} ± {std:.2f}")
            print(f"  Median: {median:.2f}, MAD: {mad:.2f}")
            print(f"  Range: [{min_val:.2f}, {max_val:.2f}]")
            print(f"  3σ标准: [{lower_3sigma:.2f}, {upper_3sigma:.2f}]")
            print(f"  MAD标准: [{lower_mad:.2f}, {upper_mad:.2f}]")

    # Generate distribution plots
    print("\n生成分布图...")

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle(f"1826-1L Good Boards Distribution (n={len(good_boards)} boards)", fontsize=14)

    params_plot = [
        ("ped", "Pedestal", axes[0, 0]),
        ("rms", "RMS", axes[0, 1]),
        ("PPK_mean", "Positive Peak", axes[0, 2]),
        ("NPK_mean", "Negative Peak", axes[1, 0]),
        ("BL_mean", "Baseline", axes[1, 1])
    ]

    for param, title, ax in params_plot:
        if all_data[param]:
            arr = np.array(all_data[param])
            ax.hist(arr, bins=50, edgecolor='black', alpha=0.7, color='blue')

            # Add statistics lines
            mean = criteria[param]["mean"]
            std = criteria[param]["std"]
            ax.axvline(x=mean, color='red', linestyle='-', linewidth=2, label=f'Mean={mean:.1f}')
            ax.axvline(x=mean - 3*std, color='orange', linestyle='--', label=f'-3σ={mean-3*std:.1f}')
            ax.axvline(x=mean + 3*std, color='orange', linestyle='--', label=f'+3σ={mean+3*std:.1f}')

            ax.set_xlabel(f"{title} (ADC counts)")
            ax.set_ylabel("Count")
            ax.set_title(f"{title}")
            ax.legend(fontsize=8)

    # Summary in last subplot
    ax = axes[1, 2]
    ax.axis('off')
    summary_text = "QC Criteria Summary\n"
    summary_text += "=" * 30 + "\n\n"
    summary_text += f"Good boards: {len(good_boards)}\n"
    summary_text += f"Bad boards: {len(bad_boards)}\n\n"
    summary_text += "Pass Criteria (Mean ± 3σ):\n"
    for param in ["rms", "ped", "PPK_mean", "NPK_mean", "BL_mean"]:
        if param in criteria:
            c = criteria[param]
            summary_text += f"\n{param}:\n"
            summary_text += f"  [{c['lower_3sigma']:.0f}, {c['upper_3sigma']:.0f}]\n"

    ax.text(0.1, 0.95, summary_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', fontfamily='monospace')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "1826_1L_good_boards_distribution.png"), dpi=150)
    plt.close()

    # Plot all good boards on same axis
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f"1826-1L All Good Boards Overlay (n={len(good_boards)})", fontsize=14)

    params_overlay = [
        ("ped", "Pedestal", axes[0, 0]),
        ("rms", "RMS", axes[0, 1]),
        ("PPK_mean", "Positive Peak", axes[1, 0]),
        ("BL_mean", "Baseline", axes[1, 1])
    ]

    for param, title, ax in params_overlay:
        for board in good_boards:
            data = board["data"]
            if param in data and isinstance(data[param], list) and len(data[param]) == 128:
                values = [float(v) for v in data[param]]
                ax.plot(range(128), values, alpha=0.3, linewidth=0.8)

        # Plot mean line
        if all_data[param]:
            per_channel_mean = []
            for ch in range(128):
                ch_values = []
                for board in good_boards:
                    data = board["data"]
                    if param in data and isinstance(data[param], list) and len(data[param]) == 128:
                        ch_values.append(float(data[param][ch]))
                if ch_values:
                    per_channel_mean.append(np.mean(ch_values))
            if per_channel_mean:
                ax.plot(range(128), per_channel_mean, 'k-', linewidth=2, label='Mean')

        ax.set_xlabel("Channel")
        ax.set_ylabel(f"{title}")
        ax.set_title(f"{title} - All Good Boards")
        ax.set_xlim(0, 127)
        ax.grid(True, alpha=0.3)

        # Add chip boundaries
        for chip in range(1, 8):
            ax.axvline(x=chip*16, color='gray', linestyle='--', alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "1826_1L_good_boards_overlay.png"), dpi=150)
    plt.close()

    # Save criteria to CSV
    csv_path = os.path.join(OUTPUT_DIR, "QC_Criteria_1826_1L.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Parameter", "Mean", "Std", "Median", "MAD", "Min", "Max",
                        "Lower_3Sigma", "Upper_3Sigma", "Lower_MAD", "Upper_MAD",
                        "N_Channels", "N_Boards"])
        for param, c in criteria.items():
            writer.writerow([param, c["mean"], c["std"], c["median"], c["mad"],
                           c["min"], c["max"], c["lower_3sigma"], c["upper_3sigma"],
                           c["lower_mad"], c["upper_mad"], c["n_channels"], c["n_boards"]])

    # Save to JSON
    json_path = os.path.join(OUTPUT_DIR, "QC_Criteria_1826_1L.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            "criteria": criteria,
            "good_boards": [b["femb_id"] for b in good_boards],
            "bad_boards": [{
                "femb_id": b["femb_id"],
                "param": b["param"],
                "channels": b["channels"]
            } for b in bad_boards]
        }, f, indent=2)

    # Save bad boards list
    bad_boards_path = os.path.join(OUTPUT_DIR, "bad_boards_1826_1L.txt")
    with open(bad_boards_path, 'w', encoding='utf-8') as f:
        f.write("1826-1L 有问题的板子列表\n")
        f.write("=" * 60 + "\n\n")
        for b in bad_boards:
            f.write(f"FEMB ID: {b['femb_id']}\n")
            f.write(f"  问题参数: {b['param']}\n")
            f.write(f"  异常通道: {b['channels']}\n")
            f.write(f"  CSV: {b['csv_path']}\n\n")

    print(f"\n输出文件：")
    print(f"  {csv_path}")
    print(f"  {json_path}")
    print(f"  {bad_boards_path}")
    print(f"  {OUTPUT_DIR}/1826_1L_good_boards_distribution.png")
    print(f"  {OUTPUT_DIR}/1826_1L_good_boards_overlay.png")

    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
