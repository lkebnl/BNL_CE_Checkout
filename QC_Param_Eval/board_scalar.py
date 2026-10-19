"""
Generic evaluation for board-level scalar parameters (one value per board):
power-supply readings, LDO voltages, ...

A section script supplies a config dict and calls run(cfg):
    sec        "3_2"                         -> file names (plot_3_2_*.png, criteria_3_2.csv, ...)
    title      "SE OFF Power Measurement"    -> report / plot titles
    here       directory of the section script (output/ and the report go there)
    report     report file name
    script     section script file name (shown in the report)
    params     [(pid, name, unit, role, description)], role "core" or "aux"
    extract    rows -> {pid: value}
    scope      list of Markdown lines for the "Scope" section
    max_sigma  7 (default, PASS/WARN/ALERT/FAIL) or 5 (PASS/WARN/FAIL)
"""

import os
import csv
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

from common import (EXCLUDED_BOARDS, SN_PREFIX, LEVEL_COLORS, load_boards, fmt_time, judge, levels_for,
                    y_range, draw_sigma_bands, draw_sigma_lines, parse_list)

POWER_KEYS = ("name", "V_set/V", "V_meas/V", "I_meas/A", "P_meas/W", "Total Power")
LDO_KEYS = ("CDVDDA", "CDVDDIO_HALF", "ADCRVDDD1P2", "ADCLVDDD1P2", "FERVDDP", "FELVDDP",
            "ADCRP25V_1_HALF", "ADCLP25V_1_HALF", "ADCRP25V_HALF", "ADCLP25V_HALF", "GND")


# --------------------------------------------------------------- block finders

def power_block(rows, n):
    """n-th (0-based) power-supply block: name / V_set / V_meas / I_meas / P_meas / Total Power.
    Block 0 = report 2.1, 1 = 3.2 (SE OFF), 2 = 4.2 (DIFF)."""
    count, block = -1, None
    for k, v in rows:
        if k == "name":
            count += 1
            block = {} if count == n else None
        if block is not None and k in POWER_KEYS:
            block[k] = parse_list(v)
            if k == "Total Power":
                return block
    return block or {}


def ldo_block(rows, n):
    """n-th (0-based) LDO block (CDVDDA ... GND), values in mV. Block 0 = report 3.3, 1 = 4.3."""
    count, block = -1, None
    for k, v in rows:
        if k == "CDVDDA":
            count += 1
            block = {} if count == n else None
        if block is not None and k in LDO_KEYS:
            try:
                block[k] = float(v)
            except ValueError:
                block[k] = np.nan
            if k == "GND":
                return block
    return block or {}


def power_extractor(n):
    """Standard power-block parameters (same ids as report 2.1)."""
    def extract(rows):
        b = power_block(rows, n)
        get = lambda key, i: b[key][i] if len(b.get(key, [])) > i else np.nan
        return {
            "I_LArASIC": get("I_meas/A", 1), "I_ColdDATA": get("I_meas/A", 2), "I_ColdADC": get("I_meas/A", 3),
            "V_LArASIC": get("V_meas/V", 1), "V_ColdDATA": get("V_meas/V", 2), "V_ColdADC": get("V_meas/V", 3),
            "Total_Power": get("Total Power", 0),
            "V_BIAS": get("V_meas/V", 0), "I_BIAS": get("I_meas/A", 0),
        }
    return extract


POWER_PARAMS = [
    ("I_LArASIC", "LArASIC Current", "A", "core", "LArASIC rail current"),
    ("I_ColdDATA", "ColdDATA Current", "A", "core", "ColdDATA rail current"),
    ("I_ColdADC", "ColdADC Current", "A", "core", "ColdADC rail current"),
    ("V_LArASIC", "LArASIC Voltage", "V", "core", "LArASIC rail voltage at the supply"),
    ("V_ColdDATA", "ColdDATA Voltage", "V", "core", "ColdDATA rail voltage at the supply"),
    ("V_ColdADC", "ColdADC Voltage", "V", "core", "ColdADC rail voltage at the supply"),
    ("Total_Power", "Total Power", "W", "core", "Sum of rail powers"),
    ("V_BIAS", "BIAS Voltage", "V", "aux", "BIAS rail voltage"),
    ("I_BIAS", "BIAS Current", "A", "aux", "BIAS rail current (≈ 0)"),
]

POWER_SCOPE_TABLE = [
    "| Category | Parameters | Treatment |",
    "|---|---|---|",
    "| Core | I_meas & V_meas of LArASIC / ColdDATA / ColdADC, Total Power (7) | Statistical judgement |",
    "| Auxiliary | V_meas & I_meas of BIAS (2) | Shown for reference; I_BIAS ≈ 0 is better served by a fixed limit |",
    "| Not evaluated | V_set (4) | Configuration setpoints, constant |",
    "| Not evaluated | P_meas (4) | Redundant (P = V × I) |",
    "",
]


# (CSV key / parameter id, display name, unit, role, description)
LDO_PARAMS = [
    ("CDVDDA", "COLDATA VDDA", "mV", "core", "COLDATA analog supply"),
    ("CDVDDIO_HALF", "COLDATA VDDIO", "mV", "core", "COLDATA I/O supply"),
    ("ADCRVDDD1P2", "ADC-R VDDD 1.2V", "mV", "core", "Right-side ColdADC digital 1.2 V supply"),
    ("ADCLVDDD1P2", "ADC-L VDDD 1.2V", "mV", "core", "Left-side ColdADC digital 1.2 V supply"),
    ("FERVDDP", "FE-R VDDP", "mV", "core", "Right-side LArASIC supply"),
    ("FELVDDP", "FE-L VDDP", "mV", "core", "Left-side LArASIC supply"),
    ("ADCRP25V_1_HALF", "ADC-R 2.5V #1", "mV", "core", "Right-side ColdADC 2.5 V supply #1"),
    ("ADCLP25V_1_HALF", "ADC-L 2.5V #1", "mV", "core", "Left-side ColdADC 2.5 V supply #1"),
    ("ADCRP25V_HALF", "ADC-R 2.5V", "mV", "core", "Right-side ColdADC 2.5 V main supply"),
    ("ADCLP25V_HALF", "ADC-L 2.5V", "mV", "core", "Left-side ColdADC 2.5 V main supply"),
    ("GND", "Ground", "mV", "core", "Ground reference reading of the monitor ADC"),
]


# ------------------------------------------------------------------- helpers

def fmt(v, unit):
    if unit in ("A", "V"):
        return f"{v:.4f}"
    if unit == "W":
        return f"{v:.3f}"
    return f"{v:.1f}"


def plot_param(cfg, sns, arr, s, levels, nsig, out_dir):
    pid, name, unit, role = s["pid"], s["name"], s["unit"], s["role"]
    mean, std, ms = s["mean"], s["std"], cfg["max_sigma"]
    fig, (ax, axh) = plt.subplots(1, 2, figsize=(18, 7), sharey=True,
                                  gridspec_kw={"width_ratios": [5, 1], "wspace": 0.03})
    valid = arr[~np.isnan(arr)]
    y_min, y_max = y_range(valid, mean, std, ms)
    draw_sigma_bands((ax, axh), mean, std, y_min, y_max, ms)

    x = np.arange(len(arr))
    ax.scatter(x, arr, c=[LEVEL_COLORS.get(l, 'gray') for l in levels], s=40, zorder=3,
               edgecolors='black', linewidths=0.4)
    draw_sigma_lines(ax, mean, std, lambda v: f"{fmt(v, unit)} {unit}", ms)

    for i, (sn, v, l, n) in enumerate(zip(sns, arr, levels, nsig)):
        if l not in ("PASS", "N/A"):
            ax.annotate(f"{sn}\n{n:.1f}σ", (i, v), textcoords="offset points", xytext=(6, 6),
                        fontsize=8, color=LEVEL_COLORS[l], fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(sns, rotation=90, fontsize=8)
    ax.set_xlim(-1, len(arr))
    ax.set_ylim(y_min, y_max)
    ax.set_xlabel(f"FEMB SN ({SN_PREFIX}xxxxx)", fontsize=11)
    ax.set_ylabel(f"{name} [{unit}]", fontsize=11)
    tag = "" if role == "core" else "  [auxiliary]"
    fig.suptitle(f"Report {cfg['sec'].replace('_', '.')} {cfg['title']} - {name} ({pid}) - "
                 f"{len(valid)} boards{tag}", fontsize=14, y=0.98)
    ax.legend(loc='lower left', bbox_to_anchor=(0.0, 1.01), fontsize=9, framealpha=0.9, ncol=8)

    c = s["counts"]
    stats = (f"Mean={fmt(mean, unit)}  Std={fmt(std, unit)}  Min={fmt(valid.min(), unit)}  "
             f"Max={fmt(valid.max(), unit)}\n" + "  ".join(f"{l}={c[l]}" for l in cfg["levels"]))
    ax.text(0.01, 0.98, stats, transform=ax.transAxes, fontsize=9, va='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

    axh.hist(valid, bins=min(30, max(5, len(np.unique(valid)))), orientation='horizontal',
             color='steelblue', edgecolor='black', alpha=0.8)
    axh.axhline(mean, color='black', linewidth=2)
    axh.set_xlabel("Boards")
    axh.tick_params(labelleft=False)

    fig.subplots_adjust(left=0.06, right=0.98, top=0.87, bottom=0.18)
    plt.savefig(os.path.join(out_dir, f"plot_{cfg['sec']}_{pid}.png"), dpi=150)
    plt.close()


# -------------------------------------------------------------------- report

def write_report(cfg, boards, summaries, judgement, out_dir):
    sec, secd, levels, ms = cfg["sec"], cfg["sec"].replace("_", "."), cfg["levels"], cfg["max_sigma"]
    sns = list(boards.keys())
    rel = os.path.relpath(out_dir, cfg["here"])
    dates = sorted(fmt_time(b["time"]) for b in boards.values())
    core = [s for s in summaries if s["role"] == "core"]
    aux = [s for s in summaries if s["role"] == "aux"]
    sig_cols = [k for k in (3, 5, 7) if k <= ms]

    md = [f"# FEMB QC Parameter Evaluation - Report Section {secd}: {cfg['title']}\n"]
    md.append("**Board version:** FEMB-IO 1826-1L  ")
    md.append(f"**Boards used:** {len(sns)} (latest passing test per board; excluded: {', '.join(EXCLUDED_BOARDS)})  ")
    md.append(f"**Test period:** {dates[0]} - {dates[-1]}  ")
    md.append(f"**Generated:** {datetime.now():%Y-%m-%d %H:%M}  ")
    md.append(f"**Script:** `{cfg['script']}`\n")

    md.append("## 1. Scope\n")
    md += cfg["scope"]

    md.append("## 2. Judgement Method\n")
    md.append("For each parameter, mean and standard deviation (σ) are computed over all boards; "
              "each board is graded by its deviation |x − mean| / σ.\n")
    md.append("| Level | Deviation | Plot background |")
    md.append("|---|---|---|")
    md.append("| PASS | ≤ 3σ | green |")
    md.append("| WARN | 3σ – 5σ | yellow |")
    if ms == 5:
        md.append("| FAIL | > 5σ | red |\n")
    else:
        md.append("| ALERT | 5σ – 7σ | red |")
        md.append("| FAIL | > 7σ | dark red |\n")

    md.append("## 3. Summary\n")
    md.append("| Parameter | Role | Mean | Std | Min | Max | N unique | " + " | ".join(levels) + " | Flagged boards |")
    md.append("|---|---|---|---|---|---|---|" + "---|" * len(levels) + "---|")
    for s in summaries:
        u = s["unit"]
        flagged = ", ".join(f"{sn} ({l} {n:.1f}σ)" for sn, l, n in s["flagged"]) or "–"
        md.append(f"| {s['pid']} | {s['role']} | {fmt(s['mean'], u)} {u} | {fmt(s['std'], u)} | "
                  f"{fmt(s['min'], u)} | {fmt(s['max'], u)} | {s['n_unique']} | "
                  + " | ".join(str(s['counts'][l]) for l in levels) + f" | {flagged} |")
    md.append("")

    ks = [-k for k in reversed(sig_cols)] + [0] + sig_cols
    md.append("### Criteria (limits)\n")
    md.append("| Parameter | Unit | " + " | ".join("Mean" if k == 0 else f"{k:+d}σ".replace("-", "−") for k in ks) + " |")
    md.append("|---|---|" + "---|" * len(ks))
    for s in summaries:
        u, m, d = s["unit"], s["mean"], s["std"]
        md.append(f"| {s['pid']} | {u} | " + " | ".join(fmt(m + k * d, u) for k in ks) + " |")
    md.append("")

    def section(num, s):
        u = s["unit"]
        out = [f"### {num} {s['name']} (`{s['pid']}`)\n"]
        if s.get("desc"):
            out.append(f"{s['desc']}.  ")
        out.append(f"Mean = {fmt(s['mean'], u)} {u}, σ = {fmt(s['std'], u)} {u}, "
                   f"range [{fmt(s['min'], u)}, {fmt(s['max'], u)}], "
                   f"{s['n_unique']} distinct values over {s['n']} boards.\n")
        if s["flagged"]:
            out.append("| FEMB SN | Value | Deviation | Level |")
            out.append("|---|---|---|---|")
            for sn, l, n in s["flagged"]:
                out.append(f"| {SN_PREFIX}{sn} | {fmt(s['values'][sn], u)} {u} | {n:.1f}σ | **{l}** |")
            out.append("")
        else:
            out.append("All boards within 3σ.\n")
        out.append(f"![{s['pid']}]({rel}/plot_{sec}_{s['pid']}.png)\n")
        return out

    nsec = 4
    md.append(f"## {nsec}. {'Core ' if aux else ''}Parameters\n")
    for i, s in enumerate(core, 1):
        md += section(f"{nsec}.{i}", s)
    if aux:
        nsec += 1
        md.append(f"## {nsec}. Auxiliary Parameters\n")
        for i, s in enumerate(aux, 1):
            md += section(f"{nsec}.{i}", s)

    nsec += 1
    md.append(f"## {nsec}. Observations\n")
    flagged_boards = {}
    for s in core:
        for sn, l, n in s["flagged"]:
            flagged_boards.setdefault(sn, []).append(f"{s['pid']} {n:.1f}σ ({l})")
    if flagged_boards:
        for sn, items in sorted(flagged_boards.items()):
            md.append(f"- **{SN_PREFIX}{sn}**: " + "; ".join(items))
    else:
        md.append("- No board beyond 3σ on any core parameter.")
    md += cfg.get("observations", [])
    coarse = [s["pid"] for s in core if s["n_unique"] <= 10]
    if coarse:
        md.append(f"- Readout resolution is coarse (≤ 10 distinct values) for: {', '.join(coarse)}. "
                  "σ is therefore small and quantized; a minimum tolerance tied to instrument resolution "
                  "should be considered before using these limits.")
    md.append("- Flagged boards are still included in the statistics and inflate σ; "
              "re-deriving limits without them would tighten the criteria.\n")

    md.append(f"## Appendix A: Per-Board Judgement{' (core parameters)' if aux else ''}\n")
    core_ids = [s["pid"] for s in core]
    md.append("| FEMB SN | Test time | " + " | ".join(core_ids) + " | Worst |")
    md.append("|---|---|" + "---|" * len(core_ids) + "---|")
    for sn in sns:
        cells, worst = [], "PASS"
        for pid in core_ids:
            v, l, n = judgement[sn][pid]
            cells.append(f"{n:.1f}σ" if l in ("PASS", "N/A") else f"**{n:.1f}σ {l}**")
            if l in levels and levels.index(l) > levels.index(worst):
                worst = l
        md.append(f"| {SN_PREFIX}{sn} | {fmt_time(boards[sn]['time'])} | " + " | ".join(cells) + f" | {worst} |")
    md.append("")
    md.append("## Appendix B: Output Files\n")
    lim = "/".join(f"{k}σ" for k in sig_cols)
    md.append(f"- `{rel}/criteria_{sec}.csv` – mean, σ and {lim} limits per parameter")
    md.append(f"- `{rel}/judgement_{sec}.csv` – value, deviation and level per board per parameter")
    md.append(f"- `{rel}/plot_{sec}_*.png` – distribution plots\n")

    with open(os.path.join(cfg["here"], cfg["report"]), 'w', encoding='utf-8') as f:
        f.write("\n".join(md))


# ----------------------------------------------------------------------- run

def run(cfg):
    cfg.setdefault("max_sigma", 7)
    cfg["levels"] = levels_for(cfg["max_sigma"])
    levels_all, ms, sec = cfg["levels"], cfg["max_sigma"], cfg["sec"]
    out_dir = os.path.join(cfg["here"], "output")
    os.makedirs(out_dir, exist_ok=True)

    boards = load_boards()
    for b in boards.values():
        b["block"] = cfg["extract"](b["rows"])
    sns = list(boards.keys())
    print(f"Report {sec.replace('_', '.')} {cfg['title']} - {len(sns)} boards")

    criteria_rows, summaries = [], []
    judgement = {sn: {} for sn in sns}
    sig_cols = [k for k in (3, 5, 7) if k <= ms]

    for pid, name, unit, role, desc in cfg["params"]:
        arr = np.array([boards[sn]["block"].get(pid, np.nan) for sn in sns], dtype=float)
        valid = arr[~np.isnan(arr)]
        mean, std = float(np.mean(valid)), float(np.std(valid))
        res = [judge(v, mean, std, ms) for v in arr]
        levels = [r[0] for r in res]
        nsig = [r[1] for r in res]
        for sn, v, (l, n) in zip(sns, arr, res):
            judgement[sn][pid] = (v, l, n)

        flagged = sorted([(sn, l, n) for sn, l, n in zip(sns, levels, nsig) if l not in ("PASS", "N/A")],
                         key=lambda t: -t[2])
        s = {"pid": pid, "name": name, "unit": unit, "role": role, "desc": desc, "mean": mean, "std": std,
             "min": float(valid.min()), "max": float(valid.max()), "n": len(valid),
             "n_unique": len(np.unique(valid)), "counts": {l: levels.count(l) for l in levels_all},
             "flagged": flagged, "values": dict(zip(sns, arr))}
        summaries.append(s)
        plot_param(cfg, sns, arr, s, levels, nsig, out_dir)

        criteria_rows.append([pid, name, unit, role, f"{mean:.5f}", f"{std:.5f}",
                              f"{valid.min():.4f}", f"{valid.max():.4f}", len(np.unique(valid))]
                             + [f"{mean + sg * k * std:.5f}" for k in sig_cols for sg in (-1, 1)]
                             + [levels.count(l) for l in levels_all])
        print(f"\n{pid:16s} mean={fmt(mean, unit)} std={fmt(std, unit)} {unit}  "
              + "  ".join(f"{l}={levels.count(l)}" for l in levels_all))
        for sn, l, n in flagged:
            print(f"    {l:5s} 1826-1L_{sn}  {n:.1f}σ")

    with open(os.path.join(out_dir, f"criteria_{sec}.csv"), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(["Parameter", "Name", "Unit", "Role", "Mean", "Std", "Min", "Max", "N_unique"]
                   + [f"{side}_{k}Sigma" for k in sig_cols for side in ("Lower", "Upper")]
                   + [f"N_{l}" for l in levels_all])
        w.writerows(criteria_rows)

    pids = [p[0] for p in cfg["params"]]
    with open(os.path.join(out_dir, f"judgement_{sec}.csv"), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(["FEMB_SN"] + [f"{p}{s}" for p in pids for s in ("", "_nsigma", "_level")] + ["Worst_core"])
        for sn in sns:
            row, worst = [SN_PREFIX + sn], "PASS"
            for pid, name, unit, role, desc in cfg["params"]:
                v, l, n = judgement[sn][pid]
                row += [v, f"{n:.2f}", l]
                if role == "core" and l in levels_all and levels_all.index(l) > levels_all.index(worst):
                    worst = l
            w.writerow(row + [worst])

    write_report(cfg, boards, summaries, judgement, out_dir)
    print(f"\nOutput: {out_dir}")
    print(f"Report: {os.path.join(cfg['here'], cfg['report'])}")
    return boards, summaries
