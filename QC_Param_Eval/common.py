"""
Shared helpers for parameter-by-parameter QC evaluation (FEMB-IO 1826-1L).

- Board set: latest passing test per board, EXCLUDED_BOARDS removed
- Judgement: |x - mean| / σ, two schemes selected by `max_sigma`
    max_sigma=7 (board-level power/LDO): PASS ≤3σ, WARN 3-5σ, ALERT 5-7σ, FAIL >7σ
    max_sigma=5 (channel-level noise/pulse): PASS ≤3σ, WARN 3-5σ, FAIL >5σ
- Plot background bands: green / yellow / red / dark red  (5σ scheme: green / yellow / red)
"""

import os
import re
import ast
import numpy as np

QC_DATA_ROOT = "/home/dune/Documents/data/FEMB_QC/Report"
EXCLUDED_BOARDS = ["00046"]
SN_PREFIX = "BNL_FEMB_IO-1826-1L_"

LEVELS = ["PASS", "WARN", "ALERT", "FAIL"]   # ≤3σ, 3-5σ, 5-7σ, >7σ (ALERT unused when max_sigma=5)
LEVEL_COLORS = {"PASS": "blue", "WARN": "darkorange", "ALERT": "red", "FAIL": "darkred", "N/A": "gray"}


# ----------------------------------------------------------------- data loading

def parse_list(s):
    try:
        return [float(x) if x != '' else np.nan for x in ast.literal_eval(s)]
    except (ValueError, SyntaxError):
        return []


def find_csv_files(root_dir=QC_DATA_ROOT):
    for root, _, files in os.walk(root_dir):
        for f in files:
            if "1826-1L" in f and f.startswith("DataBase_FEMB_") and f.endswith(".csv"):
                yield os.path.join(root, f)


def test_time(path):
    m = re.search(r'Time_(\d{4})_(\d{2})/(\d{2})_(\d{2})_(\d{2})_(\d{2})', path)
    return m.groups() if m else ("0",) * 6


def fmt_time(t):
    return "{}-{}-{} {}:{}".format(*t[:5])


def read_rows(path):
    """CSV as an ordered list of (key, value) - keys repeat between report sections."""
    rows = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            parts = line.rstrip('\n').split(',', 1)
            if len(parts) == 2:
                rows.append((parts[0], parts[1].strip('"')))
    return rows


def all_pass(rows):
    return not any(k == "Result" and v.strip().lower() == "false" for k, v in rows)


def load_boards():
    """{sn: {"time", "rows", "path"}} for the latest passing test of each board, sorted by SN."""
    latest = {}
    for path in find_csv_files():
        sn = re.search(r'1826-1L_(\d{5})', os.path.basename(path)).group(1)
        if sn in EXCLUDED_BOARDS:
            continue
        rows = read_rows(path)
        if not all_pass(rows):
            continue
        t = test_time(path)
        if sn not in latest or t > latest[sn]["time"]:
            latest[sn] = {"time": t, "rows": rows, "path": path}
    return dict(sorted(latest.items()))


# ------------------------------------------------------------------- judgement

def levels_for(max_sigma):
    return ["PASS", "WARN", "FAIL"] if max_sigma == 5 else LEVELS


def judge(value, mean, std, max_sigma=7):
    if np.isnan(value):
        return "N/A", np.nan
    n = abs(value - mean) / std if std > 0 else 0.0
    if n <= 3:
        return "PASS", n
    if n <= 5:
        return "WARN", n
    if max_sigma == 5:
        return "FAIL", n
    if n <= 7:
        return "ALERT", n
    return "FAIL", n


def judge_array(nsig, max_sigma=7):
    """Vectorised judge on an array of |x - mean| / σ."""
    lv = np.full(nsig.shape, "N/A", dtype=object)
    lv[nsig <= 3] = "PASS"
    lv[(nsig > 3) & (nsig <= 5)] = "WARN"
    if max_sigma == 5:
        lv[nsig > 5] = "FAIL"
    else:
        lv[(nsig > 5) & (nsig <= 7)] = "ALERT"
        lv[nsig > 7] = "FAIL"
    return lv


def worse(a, b):
    """The more severe of two levels (N/A ignored)."""
    ia = LEVELS.index(a) if a in LEVELS else -1
    ib = LEVELS.index(b) if b in LEVELS else -1
    return a if ia >= ib else b


# -------------------------------------------------------------------- plotting

def y_range(valid, mean, std, max_sigma=7, pad_frac=0.15):
    s = std if std > 0 else 1e-6
    span = max(valid.max() - valid.min(), 2 * max_sigma * s)
    pad = pad_frac * span
    return min(mean - max_sigma * s, valid.min()) - pad, max(mean + max_sigma * s, valid.max()) + pad


def draw_sigma_bands(axes, mean, std, y_min, y_max, max_sigma=7):
    """Background bands on every axis in `axes`; legend proxies on axes[0]."""
    s = std if std > 0 else 1e-6
    b = {k: (mean - k * s, mean + k * s) for k in (3, 5, 7)}
    if max_sigma == 5:
        for a in axes:
            a.axhspan(y_min, b[5][0], color='red', alpha=0.25)
            a.axhspan(b[5][1], y_max, color='red', alpha=0.25)
            a.axhspan(b[5][0], b[3][0], color='yellow', alpha=0.25)
            a.axhspan(b[3][1], b[5][1], color='yellow', alpha=0.25)
            a.axhspan(b[3][0], b[3][1], color='lightgreen', alpha=0.25)
        ax = axes[0]
        ax.fill_between([], [], color='lightgreen', alpha=0.4, label='Within 3σ (PASS)')
        ax.fill_between([], [], color='yellow', alpha=0.4, label='3σ-5σ (WARN)')
        ax.fill_between([], [], color='red', alpha=0.4, label='Outside 5σ (FAIL)')
        return b
    for a in axes:
        a.axhspan(y_min, b[7][0], color='darkred', alpha=0.25)
        a.axhspan(b[7][1], y_max, color='darkred', alpha=0.25)
        a.axhspan(b[7][0], b[5][0], color='red', alpha=0.2)
        a.axhspan(b[5][1], b[7][1], color='red', alpha=0.2)
        a.axhspan(b[5][0], b[3][0], color='yellow', alpha=0.25)
        a.axhspan(b[3][1], b[5][1], color='yellow', alpha=0.25)
        a.axhspan(b[3][0], b[3][1], color='lightgreen', alpha=0.25)

    ax = axes[0]
    ax.fill_between([], [], color='lightgreen', alpha=0.4, label='Within 3σ (PASS)')
    ax.fill_between([], [], color='yellow', alpha=0.4, label='3σ-5σ (WARN)')
    ax.fill_between([], [], color='red', alpha=0.3, label='5σ-7σ (ALERT)')
    ax.fill_between([], [], color='darkred', alpha=0.4, label='Outside 7σ (FAIL)')
    return b


def draw_sigma_lines(ax, mean, std, label_fmt, max_sigma=7):
    ax.axhline(mean, color='black', linewidth=2, label=f'Mean = {label_fmt(mean)}')
    for k, c in ((3, 'green'), (5, 'orange'), (7, 'red')):
        if k > max_sigma:
            break
        ax.axhline(mean - k * std, color=c, linestyle='--', linewidth=1.3)
        ax.axhline(mean + k * std, color=c, linestyle='--', linewidth=1.3, label=f'±{k}σ')
