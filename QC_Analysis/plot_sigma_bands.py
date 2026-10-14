#!/usr/bin/env python3
"""
Plot QC parameters with 3σ and 5σ background bands
- Green background: within 3σ (99.7% of normal data)
- Yellow background: between 3σ and 5σ (warning zone)
- Red background: outside 5σ (fail zone)
"""

import os
import csv
import ast
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Configuration
QC_DATA_ROOT = "/home/dune/Documents/data/FEMB_QC/Report"
OUTPUT_DIR = "/home/dune/PycharmProjects/BNL_CE_Checkout/QC_Analysis/output_1826_1L"

# Excluded boards (known bad)
EXCLUDED_BOARDS = ["00046"]

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

def find_1826_1L_csv_files(root_dir):
    """Find all 1826-1L FEMB checkout CSV files."""
    csv_files = []
    for root, dirs, files in os.walk(root_dir):
        for f in files:
            if "1826-1L" in f and f.startswith("DataBase_FEMB_") and f.endswith(".csv"):
                csv_files.append(os.path.join(root, f))
    return csv_files

def extract_board_number(csv_path):
    """Extract board number from CSV path."""
    filename = os.path.basename(csv_path)
    # Format: DataBase_FEMB_BNL_FEMB_IO-1826-1L_00034_...
    parts = filename.split("_")
    for p in parts:
        if p.isdigit() and len(p) == 5:
            return p
    return None

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 60)
    print("Plotting with 3σ and 5σ Background Bands")
    print("=" * 60)

    # Find all CSV files
    csv_files = find_1826_1L_csv_files(QC_DATA_ROOT)
    print(f"\nFound {len(csv_files)} 1826-1L CSV files")

    # Filter boards
    good_boards = []
    for csv_path in csv_files:
        board_num = extract_board_number(csv_path)

        # Skip excluded boards
        if board_num in EXCLUDED_BOARDS:
            print(f"  Excluding board {board_num}")
            continue

        try:
            data = load_csv_data(csv_path)
            # Check Result field (can be bool True or string "True")
            result = data.get("Result", False)
            if result is True or str(result).lower() == "true":
                good_boards.append({
                    "board_num": board_num,
                    "csv_path": csv_path,
                    "data": data
                })
        except Exception as e:
            print(f"  Error loading {csv_path}: {e}")

    print(f"\nGood boards: {len(good_boards)}")

    # Parameters to plot
    params = ["ped", "rms", "PPK_mean", "NPK_mean", "BL_mean"]
    param_names = {
        "ped": "Pedestal",
        "rms": "RMS Noise",
        "PPK_mean": "Positive Peak (PPK)",
        "NPK_mean": "Negative Peak (NPK)",
        "BL_mean": "Baseline (BL)"
    }

    # Collect all data
    all_data = {p: [] for p in params}
    board_boundaries = []  # Store where each board starts

    current_idx = 0
    for board in good_boards:
        data = board["data"]
        board_boundaries.append((current_idx, board["board_num"]))

        for param in params:
            if param in data and isinstance(data[param], list) and len(data[param]) == 128:
                values = [float(v) for v in data[param]]
                all_data[param].extend(values)

        current_idx += 128

    # Calculate statistics and create plots
    print("\n" + "=" * 60)
    print("QC Criteria with 3σ and 5σ")
    print("=" * 60)

    criteria = {}

    for param in params:
        if not all_data[param]:
            continue

        arr = np.array(all_data[param])
        mean = np.mean(arr)
        std = np.std(arr)
        median = np.median(arr)

        # Calculate bounds
        lower_3sigma = mean - 3 * std
        upper_3sigma = mean + 3 * std
        lower_5sigma = mean - 5 * std
        upper_5sigma = mean + 5 * std

        criteria[param] = {
            "mean": mean,
            "std": std,
            "lower_3sigma": lower_3sigma,
            "upper_3sigma": upper_3sigma,
            "lower_5sigma": lower_5sigma,
            "upper_5sigma": upper_5sigma,
            "min": np.min(arr),
            "max": np.max(arr)
        }

        print(f"\n{param} ({param_names[param]}):")
        print(f"  Mean ± Std: {mean:.2f} ± {std:.2f}")
        print(f"  3σ Range: [{lower_3sigma:.2f}, {upper_3sigma:.2f}]")
        print(f"  5σ Range: [{lower_5sigma:.2f}, {upper_5sigma:.2f}]")
        print(f"  Actual Range: [{np.min(arr):.2f}, {np.max(arr):.2f}]")

        # Count points in each zone
        n_within_3sigma = np.sum((arr >= lower_3sigma) & (arr <= upper_3sigma))
        n_between_3_5sigma = np.sum(((arr < lower_3sigma) & (arr >= lower_5sigma)) |
                                     ((arr > upper_3sigma) & (arr <= upper_5sigma)))
        n_outside_5sigma = np.sum((arr < lower_5sigma) | (arr > upper_5sigma))

        print(f"  Within 3σ: {n_within_3sigma} ({100*n_within_3sigma/len(arr):.2f}%)")
        print(f"  Between 3σ-5σ: {n_between_3_5sigma} ({100*n_between_3_5sigma/len(arr):.2f}%)")
        print(f"  Outside 5σ: {n_outside_5sigma} ({100*n_outside_5sigma/len(arr):.2f}%)")

    # Create plots with background bands
    print("\nGenerating plots with sigma bands...")

    for param in params:
        if not all_data[param]:
            continue

        arr = np.array(all_data[param])
        c = criteria[param]

        fig, ax = plt.subplots(figsize=(16, 8))

        # Get y-axis range with some padding
        y_min = min(c["lower_5sigma"], c["min"]) - 0.1 * c["std"]
        y_max = max(c["upper_5sigma"], c["max"]) + 0.1 * c["std"]

        x_range = len(arr)

        # Draw background bands (from bottom to top)
        # Red zone (outside 5σ) - bottom
        ax.axhspan(y_min, c["lower_5sigma"], alpha=0.3, color='red', label='Outside 5σ (FAIL)')
        # Red zone (outside 5σ) - top
        ax.axhspan(c["upper_5sigma"], y_max, alpha=0.3, color='red')

        # Yellow zone (between 3σ and 5σ) - bottom
        ax.axhspan(c["lower_5sigma"], c["lower_3sigma"], alpha=0.3, color='yellow', label='3σ-5σ (WARNING)')
        # Yellow zone (between 3σ and 5σ) - top
        ax.axhspan(c["upper_3sigma"], c["upper_5sigma"], alpha=0.3, color='yellow')

        # Green zone (within 3σ)
        ax.axhspan(c["lower_3sigma"], c["upper_3sigma"], alpha=0.3, color='lightgreen', label='Within 3σ (PASS)')

        # Plot data points
        x = np.arange(len(arr))

        # Color points by zone
        colors = []
        for v in arr:
            if v < c["lower_5sigma"] or v > c["upper_5sigma"]:
                colors.append('darkred')
            elif v < c["lower_3sigma"] or v > c["upper_3sigma"]:
                colors.append('orange')
            else:
                colors.append('blue')

        ax.scatter(x, arr, c=colors, s=1, alpha=0.6)

        # Draw sigma lines
        ax.axhline(y=c["mean"], color='black', linestyle='-', linewidth=2, label=f'Mean={c["mean"]:.1f}')
        ax.axhline(y=c["lower_3sigma"], color='green', linestyle='--', linewidth=1.5, label=f'±3σ=[{c["lower_3sigma"]:.1f}, {c["upper_3sigma"]:.1f}]')
        ax.axhline(y=c["upper_3sigma"], color='green', linestyle='--', linewidth=1.5)
        ax.axhline(y=c["lower_5sigma"], color='red', linestyle='--', linewidth=1.5, label=f'±5σ=[{c["lower_5sigma"]:.1f}, {c["upper_5sigma"]:.1f}]')
        ax.axhline(y=c["upper_5sigma"], color='red', linestyle='--', linewidth=1.5)

        # Draw board boundaries
        for idx, board_num in board_boundaries:
            ax.axvline(x=idx, color='gray', linestyle='-', alpha=0.2, linewidth=0.5)

        # Labels and title
        ax.set_xlabel(f"Channel Index (128 × {len(good_boards)} boards = {len(arr)} channels)", fontsize=12)
        ax.set_ylabel(f"{param_names[param]} (ADC counts)", fontsize=12)
        ax.set_title(f"{param_names[param]} Distribution with 3σ and 5σ Bands\n"
                    f"({len(good_boards)} good 1826-1L boards, {len(arr)} channels)", fontsize=14)

        ax.set_xlim(0, len(arr))
        ax.set_ylim(y_min, y_max)

        # Legend
        ax.legend(loc='upper right', fontsize=10)

        # Add statistics text box
        n_within_3sigma = np.sum((arr >= c["lower_3sigma"]) & (arr <= c["upper_3sigma"]))
        n_between_3_5sigma = np.sum(((arr < c["lower_3sigma"]) & (arr >= c["lower_5sigma"])) |
                                     ((arr > c["upper_3sigma"]) & (arr <= c["upper_5sigma"])))
        n_outside_5sigma = np.sum((arr < c["lower_5sigma"]) | (arr > c["upper_5sigma"]))

        stats_text = (f"Statistics:\n"
                     f"Within 3σ: {n_within_3sigma} ({100*n_within_3sigma/len(arr):.2f}%)\n"
                     f"3σ-5σ: {n_between_3_5sigma} ({100*n_between_3_5sigma/len(arr):.2f}%)\n"
                     f"Outside 5σ: {n_outside_5sigma} ({100*n_outside_5sigma/len(arr):.2f}%)")

        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, f"sigma_bands_{param}.png"), dpi=150)
        plt.close()

        print(f"  Saved sigma_bands_{param}.png")

    # Save updated criteria to CSV with 5σ
    csv_path = os.path.join(OUTPUT_DIR, "QC_Criteria_5Sigma.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Parameter", "Mean", "Std", "Lower_3Sigma", "Upper_3Sigma",
                        "Lower_5Sigma", "Upper_5Sigma", "Min", "Max", "N_Channels"])
        for param in params:
            c = criteria[param]
            writer.writerow([param, f"{c['mean']:.2f}", f"{c['std']:.2f}",
                           f"{c['lower_3sigma']:.2f}", f"{c['upper_3sigma']:.2f}",
                           f"{c['lower_5sigma']:.2f}", f"{c['upper_5sigma']:.2f}",
                           f"{c['min']:.2f}", f"{c['max']:.2f}",
                           len(all_data[param])])

    print(f"\nSaved criteria to {csv_path}")
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)

if __name__ == "__main__":
    main()
