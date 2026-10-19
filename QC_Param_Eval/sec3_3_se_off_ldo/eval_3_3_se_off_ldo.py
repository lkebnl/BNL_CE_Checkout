#!/usr/bin/env python3
"""
Parameter-by-parameter evaluation - Report Section 3.3
SE OFF LDO Measurement (on-board LDO outputs in mV, SE OFF configuration)

- Board set: FEMB-IO 1826-1L, latest passing test per board (see common.py)
- Board-level LDO parameters: 3σ / 5σ / 7σ (PASS / WARN / ALERT / FAIL)
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from board_scalar import run, ldo_block, LDO_PARAMS

PARAMS = LDO_PARAMS

CONFIG = {
    "sec": "3_3",
    "title": "SE OFF LDO Measurement",
    "here": HERE,
    "report": "Report_3_3_SE_OFF_LDO.md",
    "script": os.path.basename(__file__),
    "params": PARAMS,
    "extract": lambda rows: ldo_block(rows, 0),
    "max_sigma": 7,
    "scope": [
        "Section 3.3 of the per-board checkout report lists the outputs of the 11 on-board LDO / monitor "
        "points, read in mV by the board monitor ADC while the FEMB is in the SE OFF configuration "
        "(same configuration as 3.1 / 3.2). One value per board per point; all 11 are evaluated, using the values as reported in the CSV.\n",
        "| Parameter | Description |",
        "|---|---|",
    ] + [f"| `{p}` – {n} | {d} |" for p, n, u, r, d in PARAMS] + [""],
}

if __name__ == "__main__":
    run(CONFIG)
