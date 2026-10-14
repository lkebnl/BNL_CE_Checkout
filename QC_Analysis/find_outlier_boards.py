#!/usr/bin/env python3
"""
Find boards with channels outside 5σ range
"""

import os
import csv
import ast
import numpy as np

# Configuration
QC_DATA_ROOT = "/home/dune/Documents/data/FEMB_QC/Report"
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
    csv_files = []
    for root, dirs, files in os.walk(root_dir):
        for f in files:
            if "1826-1L" in f and f.startswith("DataBase_FEMB_") and f.endswith(".csv"):
                csv_files.append(os.path.join(root, f))
    return csv_files

def extract_board_info(csv_path):
    filename = os.path.basename(csv_path)
    # Extract full FEMB ID like BNL_FEMB_IO-1826-1L_00034
    parts = filename.replace("DataBase_FEMB_", "").replace(".csv", "").split("_S")
    if parts:
        return parts[0]
    return filename

def main():
    # Criteria from previous analysis (5σ bounds)
    criteria = {
        "ped": {"lower": 381.85, "upper": 1438.56},
        "rms": {"lower": 6.58, "upper": 15.90},
        "PPK_mean": {"lower": 12276.72, "upper": 13219.84},
        "NPK_mean": {"lower": 3976.71, "upper": 4841.98},
        "BL_mean": {"lower": 8224.65, "upper": 8933.27}
    }

    csv_files = find_1826_1L_csv_files(QC_DATA_ROOT)

    print("=" * 70)
    print("Boards with channels outside 5σ range")
    print("=" * 70)

    outlier_summary = {p: [] for p in criteria.keys()}

    for csv_path in csv_files:
        femb_id = extract_board_info(csv_path)
        board_num = femb_id.split("_")[-1] if "_" in femb_id else femb_id

        # Skip excluded boards
        if board_num in EXCLUDED_BOARDS:
            continue

        try:
            data = load_csv_data(csv_path)

            # Check Result field
            result = data.get("Result", False)
            if not (result is True or str(result).lower() == "true"):
                continue

            # Check each parameter
            for param, bounds in criteria.items():
                if param in data and isinstance(data[param], list) and len(data[param]) == 128:
                    values = [float(v) for v in data[param]]

                    for ch, val in enumerate(values):
                        if val < bounds["lower"] or val > bounds["upper"]:
                            outlier_summary[param].append({
                                "femb_id": femb_id,
                                "channel": ch,
                                "value": val,
                                "csv_path": csv_path
                            })

        except Exception as e:
            pass

    # Print results
    for param, outliers in outlier_summary.items():
        if outliers:
            print(f"\n{param} (5σ range: [{criteria[param]['lower']:.2f}, {criteria[param]['upper']:.2f}]):")
            print("-" * 70)

            # Group by board
            boards = {}
            for o in outliers:
                if o["femb_id"] not in boards:
                    boards[o["femb_id"]] = []
                boards[o["femb_id"]].append((o["channel"], o["value"]))

            for femb_id, channels in boards.items():
                print(f"  {femb_id}:")
                for ch, val in channels:
                    deviation = ""
                    if val > criteria[param]["upper"]:
                        deviation = f"+{val - criteria[param]['upper']:.2f} above upper"
                    else:
                        deviation = f"-{criteria[param]['lower'] - val:.2f} below lower"
                    print(f"    CH{ch:3d}: {val:10.2f}  ({deviation})")

    print("\n" + "=" * 70)
    print("Summary:")
    print("=" * 70)
    for param, outliers in outlier_summary.items():
        unique_boards = set(o["femb_id"] for o in outliers)
        print(f"  {param}: {len(outliers)} channels in {len(unique_boards)} boards")

if __name__ == "__main__":
    main()
