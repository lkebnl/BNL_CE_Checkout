#!/usr/bin/env python3
"""
Parameter-by-parameter evaluation - Report Section 4.2
DIFF Power Measurement (power readings with ColdADC in differential mode, 900 mV BL, 14 mV/fC, 2 us)

- Board set: FEMB-IO 1826-1L, latest passing test per board (see common.py)
- Board-level power parameters: 3σ / 5σ / 7σ (PASS / WARN / ALERT / FAIL)
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from board_scalar import run, power_extractor, POWER_PARAMS, POWER_SCOPE_TABLE

CONFIG = {
    "sec": "4_2",
    "title": "DIFF Power Measurement",
    "here": HERE,
    "report": "Report_4_2_DIFF_Power.md",
    "script": os.path.basename(__file__),
    "params": POWER_PARAMS,
    "extract": power_extractor(2),
    "max_sigma": 7,
    "scope": [
        "Section 4.2 of the per-board checkout report is the power-supply reading taken while the FEMB is "
        "in the DIFF configuration of section 4.1 (ColdADC differential input, FE differential driver on, "
        "900 mV baseline, 14 mV/fC, 2 µs, calibration pulse on). It has the same 17 numbers as sections "
        "2.1 and 3.2: V_set / V_meas / I_meas / P_meas for the 4 rails (BIAS, LArASIC, ColdDATA, ColdADC), "
        "plus Total Power. In the CSV it is the third power block.\n",
    ] + POWER_SCOPE_TABLE,
}

if __name__ == "__main__":
    run(CONFIG)
