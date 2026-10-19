#!/usr/bin/env python3
"""
Analyze Board 46 against QC Criteria
"""

import csv
import ast
import numpy as np
import os

# Board 46 CSV files
BOARD46_FILES = [
    "/home/dune/Documents/data/FEMB_QC/Report/Time_2026_07/27_23_48_32_CTS_BNL_S0BNL_FEMB_IO-1826-1L_00062_S1BNL_FEMB_IO-1826-1L_00047_S2BNL_FEMB_IO-1826-1L_00017_S3BNL_FEMB_IO-1826-1L_00046_RT_CHK/Report/FEMBBNL_FEMB_IO-1826-1L_00046_RT_PCB_Based/DataBase_FEMB_BNL_FEMB_IO-1826-1L_00046_S3_P.csv",
    "/home/dune/Documents/data/FEMB_QC/Report/Time_2026_08/03_18_53_24_CTS_BNL_S0BNL_FEMB_IO-1826-1L_00059_S1BNL_FEMB_IO-1826-1L_00004_S2BNL_FEMB_IO-1826-1L_00061_S3BNL_FEMB_IO-1826-1L_00046_RT_CHK/Report/FEMBBNL_FEMB_IO-1826-1L_00046_RT_PCB_Based/DataBase_FEMB_BNL_FEMB_IO-1826-1L_00046_S3_P.csv",
    "/home/dune/Documents/data/FEMB_QC/Report/Time_2026_09/11_19_03_16_CTS_BNL_S0BNL_FEMB_IO-1826-1L_00024_S1BNL_FEMB_IO-1826-1L_00020_S2BNL_FEMB_IO-1826-1L_00017_S3BNL_FEMB_IO-1826-1L_00046_RT_CHK/Report/FEMBBNL_FEMB_IO-1826-1L_00046_RT_PCB_Based/DataBase_FEMB_BNL_FEMB_IO-1826-1L_00046_S3_P.csv"
]

# QC Criteria from good boards
CRITERIA_FILE = "/home/dune/PycharmProjects/BNL_CE_Checkout/QC_Analysis/output_1826_1L_final/QC_Criteria_Complete.csv"

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
                    'type': row['Type']
                }
    return criteria

def load_board_data(csv_path):
    """Load data from board CSV"""
    data = {'128ch': {}, 'ldo': {}, 'current': {}, 'asic': {}}
    results = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    i_meas_count = 0
    current_stage = None

    for line in lines:
        parts = line.strip().split(',', 1)
        if len(parts) < 2:
            continue
        key = parts[0]
        value = parts[1].strip('"')

        if key == "Result":
            results.append(value)

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

        # Track test stage
        if key == "I_meas/A":
            i_meas_count += 1
            i_list = parse_list_string(value)
            if len(i_list) >= 4:
                if i_meas_count == 2:
                    current_stage = "ped"
                    data['current']['I_LArASIC_ped'] = i_list[1]
                    data['current']['I_ColdDATA_ped'] = i_list[2]
                    data['current']['I_ColdADC_ped'] = i_list[3]
                elif i_meas_count == 3:
                    current_stage = "pulse"
                    data['current']['I_LArASIC_pulse'] = i_list[1]
                    data['current']['I_ColdDATA_pulse'] = i_list[2]
                    data['current']['I_ColdADC_pulse'] = i_list[3]

        # LDO parameters
        for ldo_param in ["CDVDDA", "CDVDDIO_HALF", "ADCRVDDD1P2", "ADCLVDDD1P2",
                          "FERVDDP", "FELVDDP", "ADCRP25V_1_HALF", "ADCLP25V_1_HALF",
                          "ADCRP25V_HALF", "ADCLP25V_HALF", "GND"]:
            if key == ldo_param:
                try:
                    val = float(value)
                    if current_stage == "ped":
                        data['ldo'][f"{ldo_param}_ped"] = val
                    elif current_stage == "pulse":
                        data['ldo'][f"{ldo_param}_pulse"] = val
                except:
                    pass

        # ASIC parameters
        for asic_param in ["FE T", "FE BGP", "ADC_VCMI", "ADC_VCMO", "ADC_VREFP", "ADC_VREFN", "VSSA"]:
            if key == asic_param:
                data['asic'][asic_param] = parse_list_string(value)

    return data, results

def check_against_criteria(data, criteria):
    """Check board data against QC criteria"""
    issues = []

    # Check 128-channel parameters
    for param in ['ped', 'rms', 'PPK_mean', 'NPK_mean', 'BL_mean', 'pedmax', 'pedmin']:
        if param in data['128ch'] and param in criteria:
            values = np.array(data['128ch'][param])
            c = criteria[param]

            # Count violations
            outside_3sigma = np.sum((values < c['lower_3sigma']) | (values > c['upper_3sigma']))
            outside_5sigma = np.sum((values < c['lower_5sigma']) | (values > c['upper_5sigma']))

            if outside_5sigma > 0:
                # Find which channels are outside
                bad_channels = np.where((values < c['lower_5sigma']) | (values > c['upper_5sigma']))[0]
                bad_values = values[bad_channels]
                issues.append({
                    'param': param,
                    'type': 'FAIL (outside 5σ)',
                    'count': outside_5sigma,
                    'channels': bad_channels.tolist()[:10],  # First 10
                    'values': bad_values.tolist()[:10],
                    'bounds': (c['lower_5sigma'], c['upper_5sigma'])
                })
            elif outside_3sigma > 0:
                issues.append({
                    'param': param,
                    'type': 'WARNING (outside 3σ)',
                    'count': outside_3sigma,
                    'bounds': (c['lower_3sigma'], c['upper_3sigma'])
                })

    # Check LDO parameters (7σ)
    for param, value in data['ldo'].items():
        if param in criteria:
            c = criteria[param]
            if value < c['lower_7sigma'] or value > c['upper_7sigma']:
                issues.append({
                    'param': param,
                    'type': 'FAIL (outside 7σ)',
                    'value': value,
                    'bounds': (c['lower_7sigma'], c['upper_7sigma']),
                    'mean': c['mean']
                })
            elif value < c['lower_5sigma'] or value > c['upper_5sigma']:
                issues.append({
                    'param': param,
                    'type': 'WARNING (outside 5σ)',
                    'value': value,
                    'bounds': (c['lower_5sigma'], c['upper_5sigma'])
                })

    # Check current parameters (7σ)
    for param, value in data['current'].items():
        if param in criteria:
            c = criteria[param]
            if value < c['lower_7sigma'] or value > c['upper_7sigma']:
                issues.append({
                    'param': param,
                    'type': 'FAIL (outside 7σ)',
                    'value': value,
                    'bounds': (c['lower_7sigma'], c['upper_7sigma']),
                    'mean': c['mean']
                })

    # Check ASIC parameters (5σ)
    for param, values in data['asic'].items():
        if param in criteria:
            c = criteria[param]
            values = np.array(values)
            outside_5sigma = np.sum((values < c['lower_5sigma']) | (values > c['upper_5sigma']))
            if outside_5sigma > 0:
                bad_chips = np.where((values < c['lower_5sigma']) | (values > c['upper_5sigma']))[0]
                bad_values = values[bad_chips]
                issues.append({
                    'param': param,
                    'type': 'FAIL (outside 5σ)',
                    'count': outside_5sigma,
                    'chips': bad_chips.tolist(),
                    'values': bad_values.tolist(),
                    'bounds': (c['lower_5sigma'], c['upper_5sigma'])
                })

    return issues

def main():
    print("=" * 80)
    print("BOARD 46 ANALYSIS - Checking Against QC Criteria")
    print("=" * 80)

    # Load criteria
    print("\nLoading QC criteria from good boards...")
    criteria = load_criteria()
    print(f"Loaded criteria for {len(criteria)} parameters")

    # Analyze each test of board 46
    for i, csv_path in enumerate(BOARD46_FILES):
        # Extract date from path
        date_part = csv_path.split("Time_")[1].split("/")[0]

        print(f"\n{'=' * 80}")
        print(f"Test {i+1}: {date_part}")
        print(f"{'=' * 80}")

        if not os.path.exists(csv_path):
            print(f"File not found: {csv_path}")
            continue

        data, results = load_board_data(csv_path)

        # Check Result field
        print(f"\nResult fields in CSV: {results}")

        # Check against criteria
        issues = check_against_criteria(data, criteria)

        if not issues:
            print("\n✓ No issues detected - All parameters within tolerance")
        else:
            print(f"\n✗ Found {len(issues)} issues:")
            print("-" * 60)

            for issue in issues:
                param = issue['param']
                issue_type = issue['type']

                if 'channels' in issue:
                    print(f"\n  {param}: {issue_type}")
                    print(f"    - {issue['count']} channels outside bounds")
                    print(f"    - Bounds: [{issue['bounds'][0]:.2f}, {issue['bounds'][1]:.2f}]")
                    print(f"    - Bad channels: {issue['channels']}")
                    print(f"    - Bad values: {[f'{v:.2f}' for v in issue['values']]}")
                elif 'chips' in issue:
                    print(f"\n  {param}: {issue_type}")
                    print(f"    - {issue['count']} chips outside bounds")
                    print(f"    - Bounds: [{issue['bounds'][0]:.2f}, {issue['bounds'][1]:.2f}]")
                    print(f"    - Bad chips: {issue['chips']}")
                    print(f"    - Bad values: {[f'{v:.2f}' for v in issue['values']]}")
                elif 'value' in issue:
                    print(f"\n  {param}: {issue_type}")
                    print(f"    - Value: {issue['value']:.4f}")
                    print(f"    - Mean: {issue.get('mean', 'N/A')}")
                    print(f"    - Bounds: [{issue['bounds'][0]:.4f}, {issue['bounds'][1]:.4f}]")
                else:
                    print(f"\n  {param}: {issue_type}")
                    print(f"    - {issue['count']} items outside bounds")

    print("\n" + "=" * 80)
    print("Analysis Complete")
    print("=" * 80)

if __name__ == "__main__":
    main()
