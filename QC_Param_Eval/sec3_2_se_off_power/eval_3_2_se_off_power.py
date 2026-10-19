#!/usr/bin/env python3
"""
Parameter-by-parameter evaluation - Report Section 3.2
SE OFF Power Measurement (power readings after configuring SE OFF, 200 mV BL, 14 mV/fC, 2 us)

- Board set: FEMB-IO 1826-1L, latest passing test per board (see common.py)
- Board-level power parameters: 3σ / 5σ / 7σ (PASS / WARN / ALERT / FAIL)
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from board_scalar import run, power_extractor, POWER_PARAMS, POWER_SCOPE_TABLE

CONFIG = {
    "sec": "3_2",
    "title": "SE OFF Power Measurement",
    "here": HERE,
    "report": "Report_3_2_SE_OFF_Power.md",
    "script": os.path.basename(__file__),
    "params": POWER_PARAMS,
    "extract": power_extractor(1),
    "max_sigma": 7,
    "scope": [
        "Section 3.2 of the per-board checkout report is the power-supply reading taken after the FEMB is "
        "configured for the SE OFF noise measurement (single-ended, SE buffer OFF, 200 mV baseline, 14 mV/fC, "
        "2 µs). It has the same 17 numbers as section 2.1: V_set / V_meas / I_meas / P_meas for the 4 rails "
        "(BIAS, LArASIC, ColdDATA, ColdADC), plus Total Power.\n",
    ] + POWER_SCOPE_TABLE,
}

if __name__ == "__main__":
    run(CONFIG)
