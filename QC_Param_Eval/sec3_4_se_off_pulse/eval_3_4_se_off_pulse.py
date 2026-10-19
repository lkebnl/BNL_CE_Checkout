#!/usr/bin/env python3
"""
Parameter-by-parameter evaluation - Report Section 3.4
SE OFF Pulse Response (900 mV BL, 14 mV/fC, 2 us, calibration DAC 0x10) - 128 channels per board

- Board set: FEMB-IO 1826-1L, latest passing test per board (see common.py)
- Channel-level limit is 5σ: PASS ≤3σ, WARN 3σ-5σ, FAIL >5σ (see channel_array.py)
- CSV source: se_pulse_ana() in components/assembly_function.py (report_log07csv)
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from channel_array import run, array_block

# (CSV key / parameter id, display name, description)
PARAMS = [
    ("PPK_mean", "Positive Peak", "Positive peak of the averaged calibration pulse, ADC counts"),
    ("BL_mean", "Baseline", "Baseline level of the pulse waveform, ADC counts"),
    ("NPK_mean", "Negative Peak", "Negative peak (undershoot minimum) of the pulse waveform, ADC counts"),
]

CONFIG = {
    "sec": "3_4",
    "title": "SE OFF Pulse Response",
    "plot_title": "SE OFF Pulse (900mV BL, 14mV/fC, 2us)",
    "configuration": "single-ended, SE buffer OFF, 900 mV baseline, 14 mV/fC, 2 µs, calibration pulse DAC 0x10",
    "here": HERE,
    "report": "Report_3_4_SE_OFF_Pulse.md",
    "script": os.path.basename(__file__),
    "params": PARAMS,
    "extract": lambda rows: array_block(rows, [p[0] for p in PARAMS]),
    "scope": [
        "Section 3.4 of the checkout report is the pulse-response test in the SE OFF configuration: the "
        "on-chip calibration pulse (DAC 0x10) is injected into every channel and, for each of the 128 "
        "channels, the positive peak, the baseline and the negative peak of the pulse are recorded "
        "(`se_pulse_ana()`, `report_log07csv`).\n",
        "The CSV also stores `PPK_max/min`, `NPK_max/min` and `BL_max/min`; for every board they are "
        "identical to the corresponding `_mean` array (one value per channel), so only the `_mean` "
        "arrays are evaluated.\n",
    ],
}

if __name__ == "__main__":
    run(CONFIG)
