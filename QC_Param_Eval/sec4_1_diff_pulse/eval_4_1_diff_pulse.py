#!/usr/bin/env python3
"""
Parameter-by-parameter evaluation - Report Section 4.1
DIFF Pulse Measurement (900 mV BL, 14 mV/fC, 2 us, calibration DAC 0x10) - 128 channels per board

- Board set: FEMB-IO 1826-1L, latest passing test per board (see common.py)
- Channel-level limit is 5σ: PASS ≤3σ, WARN 3σ-5σ, FAIL >5σ (see channel_array.py)
- The checkout CSV only stores the 4.1 True/False result; per-channel values are read from
  Pulse_Raw_DIFF_900mVBL_14_0mVfC_2_0us_0x10.bin next to the CSV, written by QC_tools.GetPeaks()
  as pickle [pkps, pkns, peds] = [PPK, NPK, BL] (128 channels each).
"""

import os
import sys
import pickle
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from channel_array import run

PULSE_FILE = "Pulse_Raw_DIFF_900mVBL_14_0mVfC_2_0us_0x10.bin"

# (parameter id, display name, description) - ids match section 3.4
PARAMS = [
    ("PPK_mean", "Positive Peak", "Positive peak of the averaged calibration pulse, ADC counts"),
    ("BL_mean", "Baseline", "Baseline level of the pulse waveform, ADC counts"),
    ("NPK_mean", "Negative Peak", "Negative peak (undershoot minimum) of the pulse waveform, ADC counts"),
]


def extract_diff_pulse(board):
    fp = os.path.join(os.path.dirname(board["path"]), PULSE_FILE)
    if not os.path.exists(fp):
        return {}
    with open(fp, 'rb') as f:
        ppk, npk, bl = pickle.load(f)
    return {"PPK_mean": np.array(ppk, dtype=float),
            "NPK_mean": np.array(npk, dtype=float),
            "BL_mean": np.array(bl, dtype=float)}


CONFIG = {
    "sec": "4_1",
    "title": "DIFF Pulse Measurement",
    "plot_title": "DIFF Pulse (900mV BL, 14mV/fC, 2us)",
    "configuration": "differential ColdADC input (SDD on), 900 mV baseline, 14 mV/fC, 2 µs, "
                     "calibration pulse DAC 0x10",
    "here": HERE,
    "report": "Report_4_1_DIFF_Pulse.md",
    "script": os.path.basename(__file__),
    "params": PARAMS,
    "extract_board": extract_diff_pulse,
    "scope": [
        "Section 4.1 of the checkout report repeats the pulse-response test of section 3.4 with the "
        "ColdADC in differential mode (FE differential driver SDD on): the calibration pulse (DAC 0x10) is "
        "injected into every channel and the positive peak, baseline and negative peak are measured.\n",
        "**Data source.** The checkout CSV stores only the 4.1 True/False result. The per-channel values "
        f"are read from `{PULSE_FILE}` in each board's report folder, the pickle "
        "`[PPK, NPK, BL]` written by `QC_tools.GetPeaks()` during the checkout. "
        "(Cross-check: the same file type for section 3.4 agrees with the 3.4 CSV values to < 1 ADC; the "
        "CSV values are rounded.)\n",
    ],
}

if __name__ == "__main__":
    run(CONFIG)
