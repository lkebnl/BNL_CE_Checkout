#!/usr/bin/env python3
"""
FEMB QC Analysis Tool
- Load all checkout CSV data
- Detect outlier channels using IQR/MAD method
- Plot distribution of all boards
- Generate summary report with bad channel detection
"""

import os
import csv
import ast
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from pathlib import Path
import json

# Configuration
QC_DATA_ROOT = "/home/dune/Documents/data/FEMB_QC/Report"
OUTPUT_DIR = "/home/dune/PycharmProjects/BNL_CE_Checkout/QC_Analysis/output"

# QC Criteria from code analysis
QC_CRITERIA = {
    "rms": {"method": "relative", "threshold": 0.6, "desc": "RMS deviation from median > 60%"},
    "ped": {"method": "absolute", "threshold": 1500, "desc": "Pedestal deviation from median > 1500"},
    "PPK": {"method": "absolute", "threshold": 1000, "desc": "Positive Peak deviation > 1000"},
    "NPK": {"method": "absolute", "threshold": 1000, "desc": "Negative Peak deviation > 1000"},
    "BL": {"method": "absolute", "threshold": 1000, "desc": "Baseline deviation > 1000"},
}


def parse_list_string(s):
    """Parse a string representation of a list into actual list."""
    if not s or s == '':
        return []
    try:
        return ast.literal_eval(s)
    except:
        return []


def detect_outliers_iqr(data, multiplier=1.5):
    """
    Detect outliers using IQR method.
    Returns indices of outlier channels.
    """
    data = np.array(data, dtype=float)
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr = q3 - q1
    lower_bound = q1 - multiplier * iqr
    upper_bound = q3 + multiplier * iqr
    outliers = np.where((data < lower_bound) | (data > upper_bound))[0]
    return outliers.tolist(), lower_bound, upper_bound


def detect_outliers_mad(data, threshold=3.5):
    """
    Detect outliers using MAD (Median Absolute Deviation) method.
    More robust to outliers than IQR for single extreme values.
    """
    data = np.array(data, dtype=float)
    median = np.median(data)
    mad = np.median(np.abs(data - median))
    if mad == 0:
        mad = 1e-6  # Prevent division by zero
    modified_z_scores = 0.6745 * (data - median) / mad
    outliers = np.where(np.abs(modified_z_scores) > threshold)[0]
    return outliers.tolist(), median, mad


def detect_outliers_combined(data, name="parameter"):
    """
    Combined outlier detection using both IQR and MAD methods.
    A channel is flagged if detected by either method.
    """
    data = np.array(data, dtype=float)

    # IQR method (good for general outlier detection)
    iqr_outliers, iqr_low, iqr_high = detect_outliers_iqr(data, multiplier=2.0)

    # MAD method (good for single extreme outliers like channel 95)
    mad_outliers, median, mad = detect_outliers_mad(data, threshold=3.5)

    # Combine outliers
    all_outliers = list(set(iqr_outliers) | set(mad_outliers))
    all_outliers.sort()

    # Calculate severity for each outlier
    outlier_details = []
    for ch in all_outliers:
        value = data[ch]
        deviation_from_median = abs(value - median)
        z_score = 0.6745 * deviation_from_median / mad if mad > 0 else 0
        outlier_details.append({
            "channel": ch,
            "chip": ch // 16,
            "value": round(value, 2),
            "median": round(median, 2),
            "deviation": round(deviation_from_median, 2),
            "z_score": round(z_score, 2),
            "method": "IQR" if ch in iqr_outliers else "MAD" if ch in mad_outliers else "BOTH"
        })

    return all_outliers, outlier_details, {
        "median": median,
        "mad": mad,
        "iqr_bounds": (iqr_low, iqr_high),
        "count": len(all_outliers)
    }


def load_csv_data(csv_path):
    """Load and parse FEMB checkout CSV file."""
    data = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                key = row[0]
                value = row[1]
                # Try to parse as list
                parsed = parse_list_string(value)
                if parsed:
                    data[key] = parsed
                else:
                    data[key] = value
    return data


def find_all_csv_files(root_dir):
    """Find all FEMB checkout CSV files."""
    csv_files = []
    for root, dirs, files in os.walk(root_dir):
        for f in files:
            if f.startswith("DataBase_FEMB_") and f.endswith(".csv"):
                csv_files.append(os.path.join(root, f))
    return csv_files


def extract_femb_id(csv_path):
    """Extract FEMB ID from CSV path or filename."""
    filename = os.path.basename(csv_path)
    # Pattern: DataBase_FEMB_XXX_SX_P.csv
    parts = filename.replace("DataBase_FEMB_", "").replace(".csv", "").rsplit("_", 2)
    if parts:
        return parts[0]
    return filename


def analyze_all_boards(output_dir):
    """Main analysis function to process all boards."""
    os.makedirs(output_dir, exist_ok=True)

    # Find all CSV files
    csv_files = find_all_csv_files(QC_DATA_ROOT)
    print(f"Found {len(csv_files)} CSV files")

    # Store all data for plotting
    all_data = {
        "rms": [],
        "ped": [],
        "PPK_mean": [],
        "NPK_mean": [],
        "BL_mean": []
    }

    # Store board info
    board_info = []
    outlier_report = []

    for csv_path in csv_files:
        femb_id = extract_femb_id(csv_path)
        try:
            data = load_csv_data(csv_path)
        except Exception as e:
            print(f"Error loading {csv_path}: {e}")
            continue

        board_result = {
            "femb_id": femb_id,
            "csv_path": csv_path,
            "outliers": {}
        }

        # Process each parameter
        for param in ["rms", "ped", "PPK_mean", "NPK_mean", "BL_mean"]:
            if param in data and isinstance(data[param], list) and len(data[param]) == 128:
                values = [float(v) for v in data[param]]
                all_data[param].append({
                    "femb_id": femb_id,
                    "values": values
                })

                # Detect outliers
                outliers, details, stats = detect_outliers_combined(values, param)
                if outliers:
                    board_result["outliers"][param] = {
                        "channels": outliers,
                        "details": details,
                        "stats": {
                            "median": float(stats["median"]),
                            "mad": float(stats["mad"]),
                            "count": stats["count"]
                        }
                    }

        if board_result["outliers"]:
            outlier_report.append(board_result)

        board_info.append({
            "femb_id": femb_id,
            "has_outliers": len(board_result["outliers"]) > 0
        })

    # Generate plots
    print("\nGenerating distribution plots...")
    plot_distributions(all_data, output_dir)

    # Generate outlier report
    print("\nGenerating outlier report...")
    generate_outlier_report(outlier_report, output_dir)

    # Save summary
    summary = {
        "total_boards": len(csv_files),
        "boards_with_outliers": len(outlier_report),
        "outlier_boards": [b["femb_id"] for b in outlier_report]
    }

    with open(os.path.join(output_dir, "summary.json"), 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n=== Analysis Complete ===")
    print(f"Total boards analyzed: {len(csv_files)}")
    print(f"Boards with outliers: {len(outlier_report)}")

    return summary, outlier_report


def plot_distributions(all_data, output_dir):
    """Plot distribution of all boards' data."""

    # 1. RMS distribution across all boards
    if all_data["rms"]:
        plt.figure(figsize=(14, 8))

        for i, board in enumerate(all_data["rms"]):
            alpha = 0.3 if len(all_data["rms"]) > 20 else 0.5
            plt.plot(range(128), board["values"], alpha=alpha, linewidth=0.8, label=board["femb_id"] if i < 5 else "")

        # Calculate and plot average
        all_rms = np.array([b["values"] for b in all_data["rms"]])
        avg_rms = np.mean(all_rms, axis=0)
        plt.plot(range(128), avg_rms, 'k-', linewidth=2, label='Average')

        plt.xlabel("Channel", fontsize=12)
        plt.ylabel("RMS (ADC counts)", fontsize=12)
        plt.title(f"RMS Distribution - All Boards (n={len(all_data['rms'])})", fontsize=14)
        plt.xlim(0, 127)
        plt.grid(True, alpha=0.3)
        plt.xticks(range(0, 128, 16))

        # Add chip boundaries
        for chip in range(1, 8):
            plt.axvline(x=chip*16, color='gray', linestyle='--', alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "rms_distribution_all_boards.png"), dpi=150)
        plt.close()

    # 2. Pedestal distribution
    if all_data["ped"]:
        plt.figure(figsize=(14, 8))

        for i, board in enumerate(all_data["ped"]):
            alpha = 0.3 if len(all_data["ped"]) > 20 else 0.5
            plt.plot(range(128), board["values"], alpha=alpha, linewidth=0.8)

        all_ped = np.array([b["values"] for b in all_data["ped"]])
        avg_ped = np.mean(all_ped, axis=0)
        plt.plot(range(128), avg_ped, 'k-', linewidth=2, label='Average')

        plt.xlabel("Channel", fontsize=12)
        plt.ylabel("Pedestal (ADC counts)", fontsize=12)
        plt.title(f"Pedestal Distribution - All Boards (n={len(all_data['ped'])})", fontsize=14)
        plt.xlim(0, 127)
        plt.grid(True, alpha=0.3)
        plt.xticks(range(0, 128, 16))

        for chip in range(1, 8):
            plt.axvline(x=chip*16, color='gray', linestyle='--', alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "pedestal_distribution_all_boards.png"), dpi=150)
        plt.close()

    # 3. PPK (Positive Peak) distribution
    if all_data["PPK_mean"]:
        plt.figure(figsize=(14, 8))

        for i, board in enumerate(all_data["PPK_mean"]):
            alpha = 0.3 if len(all_data["PPK_mean"]) > 20 else 0.5
            plt.plot(range(128), board["values"], alpha=alpha, linewidth=0.8)

        all_ppk = np.array([b["values"] for b in all_data["PPK_mean"]])
        avg_ppk = np.mean(all_ppk, axis=0)
        plt.plot(range(128), avg_ppk, 'k-', linewidth=2, label='Average')

        plt.xlabel("Channel", fontsize=12)
        plt.ylabel("Positive Peak (ADC counts)", fontsize=12)
        plt.title(f"Positive Peak Distribution - All Boards (n={len(all_data['PPK_mean'])})", fontsize=14)
        plt.xlim(0, 127)
        plt.grid(True, alpha=0.3)
        plt.xticks(range(0, 128, 16))

        for chip in range(1, 8):
            plt.axvline(x=chip*16, color='gray', linestyle='--', alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "ppk_distribution_all_boards.png"), dpi=150)
        plt.close()

    # 4. Combined histogram of all channels
    plt.figure(figsize=(12, 10))

    params = [("rms", "RMS"), ("ped", "Pedestal"), ("PPK_mean", "Positive Peak"), ("BL_mean", "Baseline")]

    for idx, (param, title) in enumerate(params):
        if all_data[param]:
            ax = plt.subplot(2, 2, idx + 1)
            all_values = []
            for board in all_data[param]:
                all_values.extend(board["values"])

            ax.hist(all_values, bins=50, edgecolor='black', alpha=0.7)
            ax.set_xlabel(f"{title} (ADC counts)")
            ax.set_ylabel("Count")
            ax.set_title(f"{title} Histogram")

            # Mark outlier region
            median = np.median(all_values)
            mad = np.median(np.abs(np.array(all_values) - median))
            ax.axvline(x=median, color='r', linestyle='--', label=f'Median={median:.1f}')
            ax.axvline(x=median + 3.5*mad/0.6745, color='orange', linestyle=':', label='3.5σ')
            ax.axvline(x=median - 3.5*mad/0.6745, color='orange', linestyle=':')
            ax.legend(fontsize=8)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "all_parameters_histogram.png"), dpi=150)
    plt.close()

    print(f"  Saved distribution plots to {output_dir}")


def generate_outlier_report(outlier_report, output_dir):
    """Generate detailed outlier report."""

    # CSV report
    csv_path = os.path.join(output_dir, "outlier_report.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["FEMB_ID", "Parameter", "Channel", "Chip", "Value", "Median", "Deviation", "Z_Score", "Detection_Method"])

        for board in outlier_report:
            femb_id = board["femb_id"]
            for param, info in board["outliers"].items():
                for detail in info["details"]:
                    writer.writerow([
                        femb_id,
                        param,
                        detail["channel"],
                        detail["chip"],
                        detail["value"],
                        detail["median"],
                        detail["deviation"],
                        detail["z_score"],
                        detail["method"]
                    ])

    # JSON report with full details
    json_path = os.path.join(output_dir, "outlier_report.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(outlier_report, f, indent=2)

    # Human-readable text report
    txt_path = os.path.join(output_dir, "outlier_report.txt")
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("FEMB QC Outlier Detection Report\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total boards with outliers: {len(outlier_report)}\n\n")

        for board in outlier_report:
            f.write("-" * 60 + "\n")
            f.write(f"FEMB ID: {board['femb_id']}\n")
            f.write(f"CSV Path: {board['csv_path']}\n")
            f.write("\nOutlier Channels:\n")

            for param, info in board["outliers"].items():
                f.write(f"\n  {param}:\n")
                f.write(f"    Median: {info['stats']['median']:.2f}\n")
                f.write(f"    MAD: {info['stats']['mad']:.2f}\n")
                f.write(f"    Outlier count: {info['stats']['count']}\n")
                f.write("    Channels:\n")
                for detail in info["details"]:
                    f.write(f"      CH{detail['channel']:3d} (Chip{detail['chip']}): "
                           f"value={detail['value']:.2f}, "
                           f"deviation={detail['deviation']:.2f}, "
                           f"z_score={detail['z_score']:.2f}\n")
            f.write("\n")

    print(f"  Saved outlier reports:")
    print(f"    - {csv_path}")
    print(f"    - {json_path}")
    print(f"    - {txt_path}")


def plot_single_board_analysis(femb_id, output_dir):
    """Generate detailed analysis plot for a single board with outliers."""
    # Find the CSV file for this board
    csv_files = find_all_csv_files(QC_DATA_ROOT)
    target_csv = None
    for csv_path in csv_files:
        if femb_id in csv_path:
            target_csv = csv_path
            break

    if not target_csv:
        print(f"CSV file not found for {femb_id}")
        return

    data = load_csv_data(target_csv)

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle(f"FEMB {femb_id} - Outlier Analysis", fontsize=14)

    params = [
        ("ped", "Pedestal", axes[0, 0]),
        ("rms", "RMS", axes[0, 1]),
        ("PPK_mean", "Positive Peak", axes[0, 2]),
        ("NPK_mean", "Negative Peak", axes[1, 0]),
        ("BL_mean", "Baseline", axes[1, 1])
    ]

    for param, title, ax in params:
        if param in data and isinstance(data[param], list) and len(data[param]) == 128:
            values = [float(v) for v in data[param]]
            outliers, details, stats = detect_outliers_combined(values, param)

            # Plot all channels
            colors = ['red' if i in outliers else 'blue' for i in range(128)]
            ax.bar(range(128), values, color=colors, alpha=0.7, width=1.0)

            # Mark median
            ax.axhline(y=stats["median"], color='green', linestyle='--', label=f'Median={stats["median"]:.1f}')

            ax.set_xlabel("Channel")
            ax.set_ylabel(title)
            ax.set_title(f"{title} (Outliers: {len(outliers)})")
            ax.set_xlim(-1, 128)
            ax.legend(fontsize=8)

            # Add chip boundaries
            for chip in range(1, 8):
                ax.axvline(x=chip*16 - 0.5, color='gray', linestyle=':', alpha=0.5)

    # Use last subplot for summary
    ax = axes[1, 2]
    ax.axis('off')
    summary_text = f"FEMB ID: {femb_id}\n\nOutlier Summary:\n"
    for param, title, _ in params:
        if param in data and isinstance(data[param], list) and len(data[param]) == 128:
            values = [float(v) for v in data[param]]
            outliers, details, stats = detect_outliers_combined(values, param)
            if outliers:
                summary_text += f"\n{title}:\n"
                for d in details[:5]:  # Show first 5 outliers
                    summary_text += f"  CH{d['channel']}: {d['value']:.1f} (z={d['z_score']:.1f})\n"
                if len(details) > 5:
                    summary_text += f"  ... and {len(details)-5} more\n"

    ax.text(0.1, 0.9, summary_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', fontfamily='monospace')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"analysis_{femb_id}.png"), dpi=150)
    plt.close()

    print(f"  Saved single board analysis: analysis_{femb_id}.png")


if __name__ == "__main__":
    print("=" * 60)
    print("FEMB QC Analysis Tool")
    print("=" * 60)

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Run analysis
    summary, outlier_report = analyze_all_boards(OUTPUT_DIR)

    # Generate detailed analysis for boards with outliers
    print("\nGenerating detailed analysis for outlier boards...")
    for board in outlier_report[:10]:  # Limit to first 10
        plot_single_board_analysis(board["femb_id"], OUTPUT_DIR)

    print("\n" + "=" * 60)
    print("Analysis complete!")
    print(f"Output directory: {OUTPUT_DIR}")
    print("=" * 60)
