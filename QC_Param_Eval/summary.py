#!/usr/bin/env python3
"""
Summary of the parameter-by-parameter QC evaluation over all report sections.

Reads the judgement / criteria CSVs written by each section script and produces
    Report_Summary.md              board × section matrix, flagged items, links to section reports
    output_summary/summary_heatmap.png
    output_summary/summary_boards.csv

Usage:
    python summary.py            build the summary from existing section outputs
    python summary.py --rerun    re-run every section script first
"""

import os
import sys
import csv
import subprocess
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import EXCLUDED_BOARDS, SN_PREFIX, LEVELS

OUT_DIR = os.path.join(HERE, "output_summary")
REPORT_MD = os.path.join(HERE, "Report_Summary.md")

# (section, folder, script, report, title, kind, item) - kind: "board" (one value per board) or "array"
SECTIONS = [
    ("2.1", "sec2_1_initial_power", "eval_2_1_initial_power.py", "Report_2_1_Initial_Power.md",
     "Initial Current Measurement", "board", None),
    ("3.1", "sec3_1_se_off_noise", "eval_3_1_noise.py", "Report_3_1_SE_OFF_Noise.md",
     "SE OFF Noise", "array", "channel"),
    ("3.2", "sec3_2_se_off_power", "eval_3_2_se_off_power.py", "Report_3_2_SE_OFF_Power.md",
     "SE OFF Power", "board", None),
    ("3.3", "sec3_3_se_off_ldo", "eval_3_3_se_off_ldo.py", "Report_3_3_SE_OFF_LDO.md",
     "SE OFF LDO", "board", None),
    ("3.4", "sec3_4_se_off_pulse", "eval_3_4_se_off_pulse.py", "Report_3_4_SE_OFF_Pulse.md",
     "SE OFF Pulse Response", "array", "channel"),
    ("4.1", "sec4_1_diff_pulse", "eval_4_1_diff_pulse.py", "Report_4_1_DIFF_Pulse.md",
     "DIFF Pulse", "array", "channel"),
    ("4.2", "sec4_2_diff_power", "eval_4_2_diff_power.py", "Report_4_2_DIFF_Power.md",
     "DIFF Power", "board", None),
    ("4.3", "sec4_3_diff_ldo", "eval_4_3_diff_ldo.py", "Report_4_3_DIFF_LDO.md",
     "DIFF LDO", "board", None),
    ("5", "sec5_monitoring", "eval_5_monitoring.py", "Report_5_Monitoring.md",
     "Monitoring", "array", "chip"),
]

LEVEL_RANK = {"PASS": 0, "WARN": 1, "ALERT": 2, "FAIL": 3}
HEAT_COLORS = ["#b7e4b0", "#ffe066", "#ff6b6b", "#8b0000"]
CLUSTER = 4          # ≥ this many flagged items on one ASIC within a section -> attention


def read_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def where_txt(x):
    return f"{x['where']} (chip {x['chip']})" if x["where"].startswith("ch") and not x["where"].startswith("chip") else x["where"]


def worst(levels):
    lv = [l for l in levels if l in LEVEL_RANK]
    return max(lv, key=LEVEL_RANK.get) if lv else "PASS"


def load_section(sec, folder, kind, item):
    """Return (scheme, {sn: worst level}, {sn: max nsigma}, [flagged items], n_params)."""
    out = os.path.join(HERE, folder, "output")
    tag = sec.replace(".", "_")
    crit = read_csv(os.path.join(out, f"criteria_{tag}.csv"))
    scheme = "7σ" if any(k.startswith("Lower_7") for k in crit[0]) else "5σ"
    roles = {c["Parameter"]: c["Role"] for c in crit}
    names = {c["Parameter"]: c["Name"] for c in crit}
    units = {c["Parameter"]: c.get("Unit", "") for c in crit}
    core = [p for p, r in roles.items() if r == "core"]

    worst_by, maxn_by, flagged = {}, {}, []
    if kind == "board":
        for row in read_csv(os.path.join(out, f"judgement_{tag}.csv")):
            sn = row["FEMB_SN"].replace(SN_PREFIX, "")
            worst_by[sn] = row["Worst_core"]
            maxn_by[sn] = max(float(row[f"{p}_nsigma"]) for p in core)
            for p in roles:
                l = row[f"{p}_level"]
                if l not in ("PASS", "N/A"):
                    flagged.append({"sn": sn, "sec": sec, "param": p, "name": names[p], "where": "board",
                                    "chip": None, "value": f"{float(row[p]):g} {units[p]}".strip(),
                                    "nsigma": float(row[f"{p}_nsigma"]), "level": l,
                                    "aux": roles[p] != "core"})
    else:
        for row in read_csv(os.path.join(out, f"judgement_{tag}_boards.csv")):
            sn = row["FEMB_SN"].replace(SN_PREFIX, "")
            worst_by[sn] = row["Worst"]
            maxn_by[sn] = max(float(row[f"{p}_Max_NSigma"]) for p in core)
        for row in read_csv(os.path.join(out, f"judgement_{tag}_{item}s.csv")):
            label = item.capitalize()
            if item == "channel":
                where, chip = f"ch{row[label]}", int(row["Chip"])
            else:
                where, chip = f"chip{row[label]}", int(row[label])
            flagged.append({"sn": row["FEMB_SN"].replace(SN_PREFIX, ""), "sec": sec, "param": row["Parameter"],
                            "name": names[row["Parameter"]], "where": where, "chip": chip,
                            "value": f"{float(row['Value']):.2f}",
                            "nsigma": float(row["NSigma"]), "level": row["Level"], "aux": False})
    return scheme, worst_by, maxn_by, flagged, len(core)


def plot_heatmap(sns, secs, mat_level, mat_nsig):
    nb, ns = len(sns), len(secs)
    fig, ax = plt.subplots(figsize=(20, 1.6 + 0.55 * ns))
    cmap = ListedColormap(HEAT_COLORS)
    norm = BoundaryNorm([-0.5, 0.5, 1.5, 2.5, 3.5], cmap.N)
    ax.imshow(mat_level, cmap=cmap, norm=norm, aspect='auto')
    for i in range(ns):
        for j in range(nb):
            ax.text(j, i, f"{mat_nsig[i, j]:.1f}", ha='center', va='center', fontsize=6.5,
                    color='white' if mat_level[i, j] >= 3 else 'black')
    ax.set_xticks(range(nb))
    ax.set_xticklabels(sns, rotation=90, fontsize=8)
    ax.set_yticks(range(ns))
    ax.set_yticklabels(secs, fontsize=9)
    ax.set_xticks(np.arange(-0.5, nb), minor=True)
    ax.set_yticks(np.arange(-0.5, ns), minor=True)
    ax.grid(which='minor', color='white', linewidth=1)
    ax.tick_params(which='minor', length=0)
    ax.set_xlabel(f"FEMB SN ({SN_PREFIX}xxxxx)")
    for lvl, c in zip(LEVELS, HEAT_COLORS):
        ax.bar(0, 0, color=c, label=lvl)
    ax.legend(loc='lower left', bbox_to_anchor=(0, 1.01), ncol=4, fontsize=9, frameon=False)
    fig.suptitle("FEMB-IO 1826-1L QC Evaluation - Worst Level per Board and Section "
                 "(cell text: largest deviation in σ, core parameters)", fontsize=13, y=0.99)
    fig.subplots_adjust(left=0.13, right=0.99, top=0.82, bottom=0.2)
    plt.savefig(os.path.join(OUT_DIR, "summary_heatmap.png"), dpi=150)
    plt.close()


def main():
    if "--rerun" in sys.argv:
        for sec, folder, script, *_ in SECTIONS:
            print(f"Running {sec} ...")
            subprocess.run([sys.executable, os.path.join(HERE, folder, script)], check=True,
                           stdout=subprocess.DEVNULL)
    os.makedirs(OUT_DIR, exist_ok=True)

    data = {}
    for sec, folder, script, report, title, kind, item in SECTIONS:
        data[sec] = load_section(sec, folder, kind, item)
    sns = sorted(set().union(*(d[1].keys() for d in data.values())))
    secs = [s[0] for s in SECTIONS]

    mat_level = np.array([[LEVEL_RANK[data[s][1].get(sn, "PASS")] for sn in sns] for s in secs])
    mat_nsig = np.array([[data[s][2].get(sn, np.nan) for sn in sns] for s in secs])
    overall = {sn: worst(data[s][1].get(sn, "PASS") for s in secs) for sn in sns}
    plot_heatmap(sns, [f"{s[0]}  {s[4]}" for s in SECTIONS], mat_level, mat_nsig)

    all_flagged = [f for s in secs for f in data[s][3]]

    with open(os.path.join(OUT_DIR, "summary_boards.csv"), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(["FEMB_SN"] + [f"S{s}" for s in secs] + ["Overall", "N_WARN_items", "N_ALERT_FAIL_items"])
        for sn in sns:
            items = [x for x in all_flagged if x["sn"] == sn and not x["aux"]]
            w.writerow([SN_PREFIX + sn] + [data[s][1].get(sn, "") for s in secs] + [overall[sn],
                       sum(x["level"] == "WARN" for x in items),
                       sum(x["level"] in ("ALERT", "FAIL") for x in items)])

    # ------------------------------------------------------------------ report
    md = ["# FEMB QC Parameter Evaluation - Summary\n"]
    md.append("**Board version:** FEMB-IO 1826-1L  ")
    md.append(f"**Boards evaluated:** {len(sns)} (latest passing test per board; excluded: {', '.join(EXCLUDED_BOARDS)})  ")
    md.append(f"**Sections:** {len(secs)}  ")
    md.append(f"**Generated:** {datetime.now():%Y-%m-%d %H:%M}  ")
    md.append("**Script:** `summary.py` (`--rerun` regenerates every section first)\n")

    md.append("## 1. Judgement Schemes\n")
    md.append("| Scheme | Used for | PASS | WARN | ALERT | FAIL |")
    md.append("|---|---|---|---|---|---|")
    md.append("| 7σ | Board-level power, current and LDO readings (2.1, 3.2, 3.3, 4.2, 4.3) | ≤ 3σ | 3σ – 5σ | 5σ – 7σ | > 7σ |")
    md.append("| 5σ | Channel-level noise / pulse (3.1, 3.4, 4.1) and per-ASIC monitoring (5) | ≤ 3σ | 3σ – 5σ | – | > 5σ |\n")
    md.append("A board's level in a section is the worst level over the section's core parameters "
              "(auxiliary parameters such as BIAS are listed but not counted). "
              "The overall level is the worst over all sections.\n")

    md.append("## 2. Overall Result\n")
    cnt = {l: sum(1 for sn in sns if overall[sn] == l) for l in LEVELS}
    md.append("| Overall level | Boards |")
    md.append("|---|---|")
    for l in LEVELS:
        md.append(f"| {l} | {cnt[l]} |")
    md.append("")
    attention = [sn for sn in sns if LEVEL_RANK[overall[sn]] >= 2]
    if attention:
        md.append("**Boards at ALERT / FAIL:** " + ", ".join(f"{SN_PREFIX}{sn}" for sn in attention) + "\n")
    else:
        md.append("**No board at ALERT / FAIL.**\n")

    md.append("## 3. Sections\n")
    md.append("| Section | Title | Scheme | Core params | PASS | WARN | ALERT | FAIL | Report |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    for sec, folder, script, report, title, kind, item in SECTIONS:
        scheme, wb, _, _, ncore = data[sec]
        c = {l: sum(1 for sn in sns if wb.get(sn) == l) for l in LEVELS}
        alert = "–" if scheme == "5σ" else c["ALERT"]
        md.append(f"| {sec} | {title} | {scheme} | {ncore} | {c['PASS']} | {c['WARN']} | {alert} | {c['FAIL']} | "
                  f"[{report}]({folder}/{report}) |")
    md.append("")

    md.append("## 4. Board × Section Overview\n")
    md.append("![summary heatmap](output_summary/summary_heatmap.png)\n")

    md.append("## 5. Boards Requiring Attention\n")
    md.append("Isolated WARN channels are expected by chance (≈ 15 per channel-level parameter over all boards), "
              "so a board is listed here only if at least one of these holds:\n")
    md.append("- **ALERT / FAIL** in any section;")
    md.append("- **repeated**: the same parameter at the same location (board-level reading, channel or chip) "
              "is flagged in more than one section (e.g. 2.1 / 3.2 / 4.2, or SE 3.4 and DIFF 4.1);")
    md.append(f"- **chip cluster**: ≥ {CLUSTER} flagged items on one ASIC within one section.\n")
    rows = []
    for sn in sns:
        items = [x for x in all_flagged if x["sn"] == sn and not x["aux"]]
        reasons = []
        if LEVEL_RANK[overall[sn]] >= 2:
            reasons.append(overall[sn])
        loc = {}
        for x in items:
            loc.setdefault((x["param"], x["where"]), set()).add(x["sec"])
        rep = sorted(f"`{p}` {w}" for (p, w), ss in loc.items() if len(ss) > 1)
        if rep:
            reasons.append("repeated: " + ", ".join(rep))
        chips = {}
        for x in items:
            if x["chip"] is not None:
                chips.setdefault((x["sec"], x["chip"]), []).append(x)
        cl = sorted(f"{s} chip {c} ({len(v)})" for (s, c), v in chips.items() if len(v) >= CLUSTER)
        if cl:
            reasons.append("chip cluster: " + ", ".join(cl))
        if reasons:
            rows.append((sn, items, reasons))
    rows.sort(key=lambda t: (-LEVEL_RANK[overall[t[0]]], -len(t[2]), -len(t[1])))
    for sn, items, reasons in rows:
        md.append(f"### {SN_PREFIX}{sn} – overall **{overall[sn]}**\n")
        md.append("Reason: " + "; ".join(reasons) + "\n")
        md.append("| Section | Parameter | Where | Value | Deviation | Level |")
        md.append("|---|---|---|---|---|---|")
        for x in sorted(items, key=lambda x: (secs.index(x["sec"]), -x["nsigma"])):
            lvl = x["level"] if x["level"] == "WARN" else f"**{x['level']}**"
            md.append(f"| {x['sec']} | `{x['param']}` | {where_txt(x)} | {x['value']} | {x['nsigma']:.1f}σ | {lvl} |")
        md.append("")
    if not rows:
        md.append("None.\n")

    md.append("## 6. Per-Board Matrix\n")
    md.append("Cell: section level (largest core-parameter deviation).\n")
    md.append("| FEMB SN | " + " | ".join(secs) + " | Overall |")
    md.append("|---|" + "---|" * len(secs) + "---|")
    for j, sn in enumerate(sns):
        cells = []
        for i, s in enumerate(secs):
            l = data[s][1].get(sn, "")
            txt = f"{l} ({mat_nsig[i, j]:.1f}σ)" if l and l != "PASS" else "PASS"
            cells.append(f"**{txt}**" if LEVEL_RANK.get(l, 0) >= 2 else txt)
        o = overall[sn]
        md.append(f"| {sn} | " + " | ".join(cells) + f" | {'**' + o + '**' if LEVEL_RANK[o] >= 2 else o} |")
    md.append("")

    md.append("## 7. All Flagged Items\n")
    md.append(f"{len(all_flagged)} items beyond 3σ across all sections "
              "(`aux` = auxiliary parameter, not counted in the board level).\n")
    md.append("| FEMB SN | Section | Parameter | Where | Value | Deviation | Level |")
    md.append("|---|---|---|---|---|---|---|")
    for x in sorted(all_flagged, key=lambda x: (x["sn"], secs.index(x["sec"]), -x["nsigma"])):
        lvl = x["level"] if x["level"] == "WARN" else f"**{x['level']}**"
        aux = " (aux)" if x["aux"] else ""
        md.append(f"| {x['sn']} | {x['sec']} | `{x['param']}`{aux} | {where_txt(x)} | {x['value']} | "
                  f"{x['nsigma']:.1f}σ | {lvl} |")
    md.append("")
    md.append("## Appendix: Output Files\n")
    md.append("- `output_summary/summary_heatmap.png` – board × section worst level")
    md.append("- `output_summary/summary_boards.csv` – per-board level in each section and overall")
    md.append("- `secX_Y_*/Report_*.md` – detailed section reports with distribution plots\n")

    with open(REPORT_MD, 'w', encoding='utf-8') as f:
        f.write("\n".join(md))
    print(f"Boards: {len(sns)}  Overall: " + "  ".join(f"{l}={cnt[l]}" for l in LEVELS))
    print(f"Report: {REPORT_MD}")


if __name__ == "__main__":
    main()
