#!/usr/bin/env python3
"""
Collect the present thresholds of every evaluated parameter into one CSV for the checkout code.

Reads the per-section criteria files (sec*/output/criteria_*.csv, written by the eval scripts)
and writes ../components/qc_thresholds.csv, one row per parameter:

    PASS   value inside [PASS_Low, PASS_High]          (mean ± 3σ)
    WARN   value inside [WARN_Low, WARN_High]          (mean ± 5σ)
    ALERT  value inside [ALERT_Low, ALERT_High]        (mean ± 7σ, board-level power / LDO only)
    FAIL   outside the widest band given for that parameter

Usage:
    venv/bin/python QC_Param_Eval/export_thresholds.py            # from the existing criteria files
    venv/bin/python QC_Param_Eval/export_thresholds.py --rerun    # rerun every section script first
"""

import os
import sys
import csv
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_CSV = os.path.join(os.path.dirname(HERE), "components", "qc_thresholds.csv")

POWER_SRC = {
    "I_LArASIC": "I_meas/A[1]", "I_ColdDATA": "I_meas/A[2]", "I_ColdADC": "I_meas/A[3]",
    "V_LArASIC": "V_meas/V[1]", "V_ColdDATA": "V_meas/V[2]", "V_ColdADC": "V_meas/V[3]",
    "Total_Power": "Total Power", "V_BIAS": "V_meas/V[0]", "I_BIAS": "I_meas/A[0]",
}

# section, folder, script, test item, level, unit (array sections only), source of the value
SECTIONS = [
    ("2.1", "sec2_1_initial_power", "eval_2_1_initial_power.py", "Initial Current Measurement", "board", None,
     lambda p: f"DataBase CSV power block #1: {POWER_SRC[p]}"),
    ("3.1", "sec3_1_se_off_noise", "eval_3_1_noise.py", "SE OFF Noise", "channel", "ADC counts",
     lambda p: f"DataBase CSV key '{p}' (128 values)"),
    ("3.2", "sec3_2_se_off_power", "eval_3_2_se_off_power.py", "SE OFF Power Measurement", "board", None,
     lambda p: f"DataBase CSV power block #2: {POWER_SRC[p]}"),
    ("3.3", "sec3_3_se_off_ldo", "eval_3_3_se_off_ldo.py", "SE OFF LDO Measurement", "board", None,
     lambda p: f"DataBase CSV LDO block #1: '{p}'"),
    ("3.4", "sec3_4_se_off_pulse", "eval_3_4_se_off_pulse.py", "SE OFF Pulse Response", "channel", "ADC counts",
     lambda p: f"DataBase CSV key '{p}' (128 values)"),
    ("4.1", "sec4_1_diff_pulse", "eval_4_1_diff_pulse.py", "DIFF Pulse Response", "channel", "ADC counts",
     lambda p: "Pulse_Raw_DIFF_900mVBL_14_0mVfC_2_0us_0x10.bin: "
               + {"PPK_mean": "pkps", "BL_mean": "peds", "NPK_mean": "pkns"}[p] + " (128 values)"),
    ("4.2", "sec4_2_diff_power", "eval_4_2_diff_power.py", "DIFF Power Measurement", "board", None,
     lambda p: f"DataBase CSV power block #3: {POWER_SRC[p]}"),
    ("4.3", "sec4_3_diff_ldo", "eval_4_3_diff_ldo.py", "DIFF LDO Measurement", "board", None,
     lambda p: f"DataBase CSV LDO block #2: '{p}'"),
    ("5", "sec5_monitoring", "eval_5_monitoring.py", "Monitoring Measurement", "chip", "mV",
     lambda p: f"DataBase CSV key '{p}' (8 values: one per ASIC)"),
]

N_ITEMS = {"board": 1, "channel": 128, "chip": 8}

COLUMNS = ["Section", "Test_Item", "Level", "Parameter", "Name", "Unit", "Role", "Source", "Max_Sigma",
           "Mean", "Std", "N_Values", "N_Boards",
           "PASS_Low", "PASS_High", "WARN_Low", "WARN_High", "ALERT_Low", "ALERT_High", "Rule"]

RULE_7 = "PASS <=3σ; WARN 3-5σ; ALERT 5-7σ; FAIL >7σ"
RULE_5 = "PASS <=3σ; WARN 3-5σ; FAIL >5σ"

# BIAS rail (aux): value ≈ constant, σ too small / meaningless -> fixed limits from QC_Criteria_Summary.csv
# (section, parameter) -> (low, high); PASS inside, FAIL outside
FIXED_LIMITS = {
    ("2.1", "V_BIAS"): (4.5, 5.5), ("2.1", "I_BIAS"): (-0.15, 0.15),
    ("3.2", "V_BIAS"): (4.5, 5.5), ("3.2", "I_BIAS"): (-0.2, 0.2),
    ("4.2", "V_BIAS"): (4.5, 5.5), ("4.2", "I_BIAS"): (-0.02, 0.15),
}


def main():
    if "--rerun" in sys.argv:
        for sec, folder, script, *_ in SECTIONS:
            print(f"Running {sec} ...")
            subprocess.run([sys.executable, os.path.join(HERE, folder, script)], check=True,
                           stdout=subprocess.DEVNULL)

    rows = []
    for sec, folder, script, item, level, unit, source in SECTIONS:
        path = os.path.join(HERE, folder, "output", f"criteria_{sec.replace('.', '_')}.csv")
        with open(path, newline="") as f:
            for r in csv.DictReader(f):
                board_level = level == "board"
                if board_level:
                    n_values = sum(int(r[k]) for k in ("N_PASS", "N_WARN", "N_ALERT", "N_FAIL"))
                    n_boards = n_values
                else:
                    n_values = int(r["N"])
                    n_boards = n_values // N_ITEMS[level]
                rows.append({
                    "Section": sec, "Test_Item": item, "Level": level,
                    "Parameter": r["Parameter"], "Name": r["Name"],
                    "Unit": r["Unit"] if board_level else unit, "Role": r["Role"],
                    "Source": source(r["Parameter"]), "Max_Sigma": 7 if board_level else 5,
                    "Mean": r["Mean"], "Std": r["Std"], "N_Values": n_values, "N_Boards": n_boards,
                    "PASS_Low": r["Lower_3Sigma"], "PASS_High": r["Upper_3Sigma"],
                    "WARN_Low": r["Lower_5Sigma"] if board_level else r["Lower_5Sigma_FAIL"],
                    "WARN_High": r["Upper_5Sigma"] if board_level else r["Upper_5Sigma_FAIL"],
                    "ALERT_Low": r["Lower_7Sigma"] if board_level else "",
                    "ALERT_High": r["Upper_7Sigma"] if board_level else "",
                    "Rule": RULE_7 if board_level else RULE_5,
                })
                fixed = FIXED_LIMITS.get((sec, r["Parameter"]))
                if fixed:
                    rows[-1].update({"Max_Sigma": "", "PASS_Low": fixed[0], "PASS_High": fixed[1],
                                     "WARN_Low": "", "WARN_High": "", "ALERT_Low": "", "ALERT_High": "",
                                     "Rule": f"Fixed limit: PASS {fixed[0]} <= value <= {fixed[1]}; FAIL outside"})

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} parameters -> {OUT_CSV}")


if __name__ == "__main__":
    main()
