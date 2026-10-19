#!/usr/bin/env python3
"""
Parameter-by-parameter evaluation - Report Section 2.1
Initial Current Measurement (power-on, before any configuration)

- Board set: FEMB-IO 1826-1L, latest passing test per board (see common.py)
- Board-level power parameters: 3σ / 5σ / 7σ (PASS / WARN / ALERT / FAIL)
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from board_scalar import run, power_extractor, POWER_PARAMS, POWER_SCOPE_TABLE

CONFIG = {
    "sec": "2_1",
    "title": "Initial Current Measurement",
    "here": HERE,
    "report": "Report_2_1_Initial_Power.md",
    "script": os.path.basename(__file__),
    "params": POWER_PARAMS,
    "extract": power_extractor(0),
    "max_sigma": 7,
    "scope": [
        "Section 2.1 of the per-board checkout report is the power-on reading of the four power-supply "
        "channels (BIAS, LArASIC, ColdDATA, ColdADC), taken before any configuration. "
        "It contains 17 numbers: V_set / V_meas / I_meas / P_meas for 4 rails, plus Total Power.\n",
    ] + POWER_SCOPE_TABLE,
}

if __name__ == "__main__":
    run(CONFIG)
