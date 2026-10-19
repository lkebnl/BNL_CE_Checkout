#!/usr/bin/env python3
"""
Plot Board 46 data against QC Criteria
"""

import csv
import ast
import numpy as np
import matplotlib.pyplot as plt
import os

# Board 46 CSV files
BOARD46_FILES = [
    ("/home/dune/Documents/data/FEMB_QC/Report/Time_2026_07/27_23_48_32_CTS_BNL_S0BNL_FEMB_IO-1826-1L_00062_S1BNL_FEMB_IO-1826-1L_00047_S2BNL_FEMB_IO-1826-1L_00017_S3BNL_FEMB_IO-1826-1L_00046_RT_CHK/Report/FEMBBNL_FEMB_IO-1826-1L_00046_RT_PCB_Based/DataBase_FEMB_BNL_FEMB_IO-1826-1L_00046_S3_P.csv", "July 2026"),
    ("/home/dune/Documents/data/FEMB_QC/Report/Time_2026_08/03_18_53_24_CTS_BNL_S0BNL_FEMB_IO-1826-1L_00059_S1BNL_FEMB_IO-1826-1L_00004_S2BNL_FEMB_IO-1826-1L_00061_S3BNL_FEMB_IO-1826-1L_00046_RT_CHK/Report/FEMBBNL_FEMB_IO-1826-1L_00046_RT_PCB_Based/DataBase_FEMB_BNL_FEMB_IO-1826-1L_00046_S3_P.csv", "Aug 2026"),
    ("/home/dune/Documents/data/FEMB_QC/Report/Time_2026_09/11_19_03_16_CTS_BNL_S0BNL_FEMB_IO-1826-1L_00024_S1BNL_FEMB_IO-1826-1L_00020_S2BNL_FEMB_IO-1826-1L_00017_S3BNL_FEMB_IO-1826-1L_00046_RT_CHK/Report/FEMBBNL_FEMB_IO-1826-1L_00046_RT_PCB_Based/DataBase_FEMB_BNL_FEMB_IO-1826-1L_00046_S3_P.csv", "Sept 2026")
]

CRITERIA_FILE = "/home/dune/PycharmProjects/BNL_CE_Checkout/QC_Analysis/output_1826_1L_final/QC_Criteria_Complete.csv"
OUTPUT_DIR = "/home/dune/PycharmProjects/BNL_CE_Checkout/QC_Analysis/output_board46_analysis"

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

def load_criteria():
    """Load QC criteria from CSV"""
    criteria = {}
    with open(CRITERIA_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Parameter']:
                criteria[row['Parameter']] = {
                    'mean': float(row['Mean']),
                    'std': float(row['Std']),
                    'lower_3sigma': float(row['Lower_3Sigma']),
                    'upper_3sigma': float(row['Upper_3Sigma']),
                    'lower_5sigma': float(row['Lower_5Sigma']),
                    'upper_5sigma': float(row['Upper_5Sigma']),
                    'lower_7sigma': float(row['Lower_7Sigma']),
                    'upper_7sigma': float(row['Upper_7Sigma']),
                    'name': row['Name'],
                    'type': row['Type']
                }
    return criteria

def load_board_data(csv_path):
    """Load data from board CSV"""
    data = {'128ch': {}}

    with open(csv_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        parts = line.strip().split(',', 1)
        if len(parts) < 2:
            continue
        key = parts[0]
        value = parts[1].strip('"')

        # 128-channel parameters
        if key == "ped":
            data['128ch']['ped'] = parse_list_string(value)
        elif key == "rms":
            data['128ch']['rms'] = parse_list_string(value)
        elif key == "PPK_mean":
            data['128ch']['PPK_mean'] = parse_list_string(value)
        elif key == "NPK_mean":
            data['128ch']['NPK_mean'] = parse_list_string(value)
        elif key == "BL_mean":
            data['128ch']['BL_mean'] = parse_list_string(value)
        elif key == "pedmax":
            data['128ch']['pedmax'] = parse_list_string(value)
        elif key == "pedmin":
            data['128ch']['pedmin'] = parse_list_string(value)

    return data

def plot_128ch_parameter(all_data, criteria, param, output_dir):
    """Plot 128-channel parameter for all tests"""
    if param not in criteria:
        return

    c = criteria[param]
    param_name = c['name']

    fig, axes = plt.subplots(3, 1, figsize=(14, 12))
    fig.suptitle(f'Board 46: {param_name} ({param}) - Channel 95 Issue Detection', fontsize=14, fontweight='bold')

    colors = ['#2E86AB', '#A23B72', '#F18F01']

    for idx, (data, test_name) in enumerate(all_data):
        ax = axes[idx]

        if param not in data['128ch']:
            continue

        values = np.array(data['128ch'][param])
        channels = np.arange(len(values))

        # Calculate y-axis limits
        y_min = min(c['lower_5sigma'], np.nanmin(values)) - 0.1 * abs(c['mean'])
        y_max = max(c['upper_5sigma'], np.nanmax(values)) + 0.1 * abs(c['mean'])

        # Plot background bands
        ax.axhspan(y_min, c['lower_5sigma'], alpha=0.3, color='red', label='Outside 5σ (FAIL)')
        ax.axhspan(c['upper_5sigma'], y_max, alpha=0.3, color='red')
        ax.axhspan(c['lower_5sigma'], c['lower_3sigma'], alpha=0.2, color='orange', label='3σ-5σ (WARNING)')
        ax.axhspan(c['upper_3sigma'], c['upper_5sigma'], alpha=0.2, color='orange')
        ax.axhspan(c['lower_3sigma'], c['upper_3sigma'], alpha=0.15, color='green', label='Within 3σ (PASS)')

        # Plot mean line
        ax.axhline(y=c['mean'], color='blue', linestyle='--', linewidth=1.5, label=f'Mean: {c["mean"]:.2f}')

        # Plot data points
        ax.scatter(channels, values, c=colors[idx], s=20, alpha=0.7, edgecolors='none')

        # Highlight Channel 95
        if len(values) > 95:
            ch95_value = values[95]
            ax.scatter([95], [ch95_value], c='red', s=150, marker='X', edgecolors='black',
                      linewidths=2, zorder=10, label=f'Ch 95: {ch95_value:.2f}')

            # Add annotation
            ax.annotate(f'Ch 95\n{ch95_value:.1f}',
                       xy=(95, ch95_value), xytext=(105, ch95_value),
                       fontsize=10, fontweight='bold', color='red',
                       arrowprops=dict(arrowstyle='->', color='red', lw=1.5))

        ax.set_xlim(-2, 130)
        ax.set_ylim(y_min, y_max)
        ax.set_xlabel('Channel', fontsize=10)
        ax.set_ylabel(param_name, fontsize=10)
        ax.set_title(f'Test: {test_name}', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right', fontsize=8)

        # Add ASIC boundaries
        for asic in range(1, 8):
            ax.axvline(x=asic*16, color='gray', linestyle=':', alpha=0.5)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'board46_{param}.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: board46_{param}.png")

def plot_channel95_trend(all_data, criteria, output_dir):
    """Plot Channel 95 values across all tests"""
    params = ['ped', 'NPK_mean', 'BL_mean', 'pedmax', 'pedmin']
    test_names = ['July 2026', 'Aug 2026', 'Sept 2026']

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    for idx, param in enumerate(params):
        ax = axes[idx]
        c = criteria[param]

        ch95_values = []
        for data, _ in all_data:
            if param in data['128ch'] and len(data['128ch'][param]) > 95:
                ch95_values.append(data['128ch'][param][95])
            else:
                ch95_values.append(np.nan)

        # Plot bounds
        ax.axhspan(c['lower_5sigma'], c['upper_5sigma'], alpha=0.3, color='green', label='5σ Range')
        ax.axhline(y=c['mean'], color='blue', linestyle='--', linewidth=1.5, label=f'Mean: {c["mean"]:.1f}')
        ax.axhline(y=c['lower_5sigma'], color='red', linestyle='-', linewidth=1, alpha=0.7)
        ax.axhline(y=c['upper_5sigma'], color='red', linestyle='-', linewidth=1, alpha=0.7, label='5σ Bounds')

        # Plot Channel 95 values
        x = np.arange(len(test_names))
        ax.plot(x, ch95_values, 'ro-', markersize=12, linewidth=2, label='Ch 95 Value')

        for i, (val, name) in enumerate(zip(ch95_values, test_names)):
            ax.annotate(f'{val:.1f}', xy=(i, val), xytext=(0, 10),
                       textcoords='offset points', ha='center', fontsize=10, fontweight='bold')

        ax.set_xticks(x)
        ax.set_xticklabels(test_names)
        ax.set_ylabel(c['name'], fontsize=10)
        ax.set_title(f'{param}', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best', fontsize=8)

    # Remove unused subplot
    axes[5].axis('off')

    fig.suptitle('Board 46 - Channel 95 Values Across Tests\n(All values outside 5σ bounds)',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'board46_channel95_trend.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: board46_channel95_trend.png")

def plot_summary(all_data, criteria, output_dir):
    """Create summary plot showing all parameters for the latest test"""
    data, test_name = all_data[-1]  # Latest test (Sept 2026)

    fig, axes = plt.subplots(3, 3, figsize=(18, 15))
    axes = axes.flatten()

    params = ['ped', 'rms', 'PPK_mean', 'NPK_mean', 'BL_mean', 'pedmax', 'pedmin']

    for idx, param in enumerate(params):
        ax = axes[idx]

        if param not in data['128ch'] or param not in criteria:
            ax.axis('off')
            continue

        c = criteria[param]
        values = np.array(data['128ch'][param])
        channels = np.arange(len(values))

        # Calculate y-axis limits
        y_min = min(c['lower_5sigma'], np.nanmin(values)) - 0.05 * abs(c['mean'])
        y_max = max(c['upper_5sigma'], np.nanmax(values)) + 0.05 * abs(c['mean'])

        # Plot background bands
        ax.axhspan(y_min, c['lower_5sigma'], alpha=0.3, color='red')
        ax.axhspan(c['upper_5sigma'], y_max, alpha=0.3, color='red')
        ax.axhspan(c['lower_5sigma'], c['lower_3sigma'], alpha=0.2, color='orange')
        ax.axhspan(c['upper_3sigma'], c['upper_5sigma'], alpha=0.2, color='orange')
        ax.axhspan(c['lower_3sigma'], c['upper_3sigma'], alpha=0.15, color='green')

        # Plot mean line
        ax.axhline(y=c['mean'], color='blue', linestyle='--', linewidth=1)

        # Plot data points
        ax.scatter(channels, values, c='#2E86AB', s=15, alpha=0.7, edgecolors='none')

        # Highlight Channel 95
        if len(values) > 95:
            ch95_value = values[95]
            is_outside = ch95_value < c['lower_5sigma'] or ch95_value > c['upper_5sigma']
            if is_outside:
                ax.scatter([95], [ch95_value], c='red', s=100, marker='X', edgecolors='black',
                          linewidths=1.5, zorder=10)
                ax.annotate(f'Ch95: {ch95_value:.0f}', xy=(95, ch95_value), xytext=(100, ch95_value),
                           fontsize=8, color='red', fontweight='bold')

        ax.set_xlim(-2, 130)
        ax.set_ylim(y_min, y_max)
        ax.set_xlabel('Channel', fontsize=9)
        ax.set_ylabel(c['name'], fontsize=9)
        ax.set_title(f'{param}: {c["name"]}', fontsize=10, fontweight='bold')
        ax.grid(True, alpha=0.3)

    # Remove unused subplots
    for idx in range(len(params), len(axes)):
        axes[idx].axis('off')

    fig.suptitle(f'Board 46 Summary - {test_name}\nRed X marks Channel 95 (outside 5σ)',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'board46_summary.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: board46_summary.png")

def main():
    print("=" * 60)
    print("BOARD 46 VISUALIZATION")
    print("=" * 60)

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"\nOutput directory: {OUTPUT_DIR}")

    # Load criteria
    print("\nLoading QC criteria...")
    criteria = load_criteria()

    # Load all board 46 data
    print("\nLoading Board 46 data...")
    all_data = []
    for csv_path, test_name in BOARD46_FILES:
        if os.path.exists(csv_path):
            data = load_board_data(csv_path)
            all_data.append((data, test_name))
            print(f"  Loaded: {test_name}")

    # Generate plots
    print("\nGenerating plots...")

    # Plot each 128-channel parameter
    for param in ['ped', 'rms', 'PPK_mean', 'NPK_mean', 'BL_mean', 'pedmax', 'pedmin']:
        plot_128ch_parameter(all_data, criteria, param, OUTPUT_DIR)

    # Plot Channel 95 trend
    plot_channel95_trend(all_data, criteria, OUTPUT_DIR)

    # Plot summary
    plot_summary(all_data, criteria, OUTPUT_DIR)

    print("\n" + "=" * 60)
    print("Visualization Complete")
    print(f"Output saved to: {OUTPUT_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
