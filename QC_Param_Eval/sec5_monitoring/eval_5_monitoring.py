#!/usr/bin/env python3
"""
Parameter-by-parameter evaluation - Report Part 05
Monitoring Measurement - one value per ASIC (8 per board), mV

- Board set: FEMB-IO 1826-1L, latest passing test per board (see common.py)
- Per-ASIC limit is 5σ: PASS ≤3σ, WARN 3σ-5σ, FAIL >5σ (see channel_array.py)
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from channel_array import run, array_block

# (CSV key / parameter id, display name, description)
PARAMS = [
    ("FE T", "FE Temperature Sensor", "LArASIC on-chip temperature sensor output, mV (depends on ambient temperature)"),
    ("FE BGP", "FE Bandgap Reference", "LArASIC bandgap reference voltage, mV"),
    ("ADC_VCMI", "ADC VCMI", "ColdADC input common-mode voltage, mV"),
    ("ADC_VCMO", "ADC VCMO", "ColdADC output common-mode voltage, mV"),
    ("ADC_VREFP", "ADC VREFP", "ColdADC positive reference voltage, mV"),
    ("ADC_VREFN", "ADC VREFN", "ColdADC negative reference voltage, mV"),
    ("VSSA", "VSSA", "ColdADC analog ground (VSSA) as seen by the monitor, mV"),
]

CONFIG = {
    "sec": "5",
    "title": "Monitoring Measurement",
    "plot_title": "Monitoring",
    "configuration": "monitoring path through the FEMB monitor ADC, 200 mV baseline, 14 mV/fC (Mon_200mVBL_14_0mVfC)",
    "here": HERE,
    "report": "Report_5_Monitoring.md",
    "script": os.path.basename(__file__),
    "params": PARAMS,
    "extract": lambda rows: array_block(rows, [p[0] for p in PARAMS]),
    "n_items": 8,
    "item": "chip",
    "abbr": "chip",
    "group_size": None,
    "unit": "mV",
    "limit_note": "Per-ASIC monitoring parameters use **5σ as the limit**: a chip beyond 5σ fails "
                  "(same as the channel-level noise / pulse parameters; board-level power and LDO "
                  "parameters keep the wider 7σ limit).",
    "scope": [
        "Part 05 of the checkout report reads the internal monitoring points of the 8 ASIC pairs on the "
        "FEMB (LArASIC + ColdADC, `ASIC #` 0–7) through the board monitor ADC, in mV. Each parameter has "
        "one value per chip, i.e. 8 values per board; every chip is judged against the pooled "
        "distribution of all chips of all boards.\n",
    ],
    "observations": lambda results: [
        "- `FE T` is a temperature-sensor voltage: board-to-board shifts can come from the room / board "
        "temperature at test time rather than from the chip, so a whole-board offset on `FE T` alone is "
        "not by itself a chip defect."
    ],
}

if __name__ == "__main__":
    run(CONFIG)
