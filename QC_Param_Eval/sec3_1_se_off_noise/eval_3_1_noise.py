#!/usr/bin/env python3
"""
Parameter-by-parameter evaluation - Report Section 3.1
SE OFF Noise Measurement (200 mV BL, 14 mV/fC, 2 us) - 128 channels per board

- Board set: FEMB-IO 1826-1L, latest passing test per board (see common.py)
- Channel-level limit is 5σ: PASS ≤3σ, WARN 3σ-5σ, FAIL >5σ (see channel_array.py)
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from channel_array import run, array_block

# (parameter id, display name, description)
PARAMS = [
    ("rms", "RMS Noise", "RMS of the baseline, ADC counts"),
    ("ped", "Pedestal", "Mean baseline (DC offset), ADC counts"),
]

CONFIG = {
    "sec": "3_1",
    "title": "SE OFF Noise Measurement",
    "plot_title": "SE OFF Noise (200mV BL, 14mV/fC, 2us)",
    "configuration": "single-ended, SE buffer OFF, 200 mV baseline, 14 mV/fC, 2 µs, no pulse",
    "here": HERE,
    "report": "Report_3_1_SE_OFF_Noise.md",
    "script": os.path.basename(__file__),
    "params": PARAMS,
    "extract": lambda rows: array_block(rows, ("ped", "rms")),
    "scope": [
        "Section 3.1 of the checkout report is the noise test: no calibration pulse is injected, and for each "
        "of the 128 channels the pedestal and RMS noise are evaluated. Pulse-response quantities "
        "(PPK / NPK / baseline) belong to section 3.4 and are not part of this section.\n",
    ],
    "observations": lambda results: [
        "- Thresholds are pooled over channels; `ped` varies channel-to-channel by design (σ ≈ "
        f"{results['ped']['std']:.0f} ADC), so its limits are wide and mainly catch dead / stuck channels."
    ],
}

if __name__ == "__main__":
    run(CONFIG)
