"""
Generic evaluation for channel-level parameters (128 values per board):
noise (ped / rms), pulse response (PPK / NPK / BL), ...

Every channel is judged against the pooled distribution of all channels of all boards.
Channel-level limit is 5σ: PASS ≤3σ, WARN 3σ-5σ, FAIL >5σ.

A section script supplies a config dict and calls run(cfg):
    sec           "3_4"                          -> file names (plot_3_4_*.png, criteria_3_4.csv, ...)
    title         "SE OFF Pulse Response"        -> report title
    plot_title    "SE OFF Pulse (900mV BL, ...)" -> plot titles
    configuration one-line description of the FE configuration
    here          directory of the section script (output/ and the report go there)
    report        report file name
    script        section script file name (shown in the report)
    params        [(pid, name, description)]
    extract       rows -> {pid: np.array(128)}
    extract_board alternative to extract: board dict {"rows", "path", "time"} -> {pid: np.array(128)},
                  for data that is not in the CSV (e.g. pulse pickles next to it)
    scope         list of Markdown lines for the "Scope" section
    observations  optional callable(results) -> list of Markdown bullet lines
  optional geometry (defaults: 128 channels in chips of 16, ADC counts):
    n_items       values per board (128, or 8 for per-ASIC monitoring)
    item / abbr   "channel" / "ch"  or  "chip" / "chip"
    group_size    items per chip (16), or None when the item already is a chip
    unit          "ADC" or "mV"
    limit_note    sentence explaining why the 5σ limit applies
"""

import os
import csv
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

from common import (EXCLUDED_BOARDS, SN_PREFIX, LEVEL_COLORS, parse_list, load_boards, fmt_time,
                    levels_for, judge_array, y_range, draw_sigma_bands, draw_sigma_lines)

MAX_SIGMA = 5                    # channel-level limit: beyond 5σ is FAIL
LEVELS = levels_for(MAX_SIGMA)   # PASS / WARN / FAIL
FLAG = ["WARN", "FAIL"]
N_CH = 128
CH_PER_CHIP = 16
CHIP_CLUSTER = 4                 # ≥ this many flagged channels on one chip is reported as a cluster


def geom(cfg):
    """Per-section geometry / wording with channel-level defaults."""
    item = cfg.get("item", "channel")
    return {"n": cfg.get("n_items", N_CH), "item": item, "Item": item.capitalize(),
            "abbr": cfg.get("abbr", "ch"), "group": cfg.get("group_size", CH_PER_CHIP),
            "unit": cfg.get("unit", "ADC")}


def array_block(rows, keys, n=0):
    """{key: np.array} for the n-th (0-based) occurrence of each key."""
    seen, block = {}, {}
    for k, v in rows:
        if k in keys:
            i = seen.get(k, 0)
            if i == n:
                block[k] = np.array(parse_list(v), dtype=float)
            seen[k] = i + 1
    return block


# -------------------------------------------------------------------- plotting

def plot_param(cfg, sns, r, pid, name, out_dir):
    """Flattened channel index on x (boards separated), side histogram on log scale."""
    mat, mean, std, lv, nsig = r["mat"], r["mean"], r["std"], r["lv"], r["nsig"]
    g = geom(cfg)
    n = g["n"]
    arr = mat.ravel()
    nb = len(sns)
    fig, (ax, axh) = plt.subplots(1, 2, figsize=(20, 7.5), sharey=True,
                                  gridspec_kw={"width_ratios": [6, 1], "wspace": 0.03})
    valid = arr[~np.isnan(arr)]
    y_min, y_max = y_range(valid, mean, std, MAX_SIGMA)
    draw_sigma_bands((ax, axh), mean, std, y_min, y_max, MAX_SIGMA)

    x = np.arange(arr.size)
    flat_lv = lv.ravel()
    for level in LEVELS:
        m = flat_lv == level
        if m.any():
            big = level != "PASS"
            ax.scatter(x[m], arr[m], c=LEVEL_COLORS[level], s=14 if big else (2 if n > 16 else 6),
                       alpha=1.0 if big else 0.5, zorder=4 if big else 3,
                       edgecolors='black' if big else 'none', linewidths=0.3)

    draw_sigma_lines(ax, mean, std, lambda v: f"{v:.2f}", MAX_SIGMA)

    for i in range(nb + 1):
        ax.axvline(i * n, color='gray', linewidth=0.4, alpha=0.5)

    # Annotate the worst channel of each board beyond the limit
    for bi, sn in enumerate(sns):
        row = nsig[bi]
        if np.all(np.isnan(row)):
            continue
        ci = int(np.nanargmax(row))
        if row[ci] > MAX_SIGMA:
            ax.annotate(f"{sn} {g['abbr']}{ci}\n{row[ci]:.1f}σ", (bi * n + ci, mat[bi, ci]),
                        textcoords="offset points", xytext=(5, 5), fontsize=7,
                        color=LEVEL_COLORS[lv[bi, ci]], fontweight='bold')

    ax.set_xticks(np.arange(nb) * n + n / 2)
    ax.set_xticklabels(sns, rotation=90, fontsize=8)
    ax.set_xlim(-n * 0.3, arr.size + n * 0.3)
    ax.set_ylim(y_min, y_max)
    ax.set_xlabel(f"FEMB SN ({SN_PREFIX}xxxxx), {n} {g['item']}s each ({arr.size} {g['item']}s total)",
                  fontsize=11)
    ax.set_ylabel(f"{name} [{g['unit']}]", fontsize=11)
    fig.suptitle(f"Report {cfg['sec'].replace('_', '.')} {cfg['plot_title']} - {name} ({pid}) - {nb} boards",
                 fontsize=14, y=0.98)
    ax.legend(loc='lower left', bbox_to_anchor=(0.0, 1.01), fontsize=9, framealpha=0.9, ncol=8)

    c = {l: int((flat_lv == l).sum()) for l in LEVELS}
    stats = (f"Mean={mean:.2f}  Std={std:.2f}  Min={valid.min():.2f}  Max={valid.max():.2f}\n"
             f"{g['Item']}s: PASS={c['PASS']}  WARN={c['WARN']}  FAIL={c['FAIL']}  (limit {MAX_SIGMA}σ)")
    ax.text(0.01, 0.98, stats, transform=ax.transAxes, fontsize=9, va='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

    axh.hist(valid, bins=80 if n > 16 else 40, orientation='horizontal', color='steelblue', edgecolor='black',
             linewidth=0.3, alpha=0.8)
    axh.set_xscale('log')
    axh.axhline(mean, color='black', linewidth=2)
    axh.set_xlabel(f"{g['Item']}s (log)")
    axh.tick_params(labelleft=False)

    fig.subplots_adjust(left=0.05, right=0.985, top=0.87, bottom=0.17)
    plt.savefig(os.path.join(out_dir, f"plot_{cfg['sec']}_{pid.replace(' ', '_')}.png"), dpi=150)
    plt.close()


def plot_board_summary(cfg, sns, results, out_dir):
    """Stacked bar: number of flagged channels per board for each parameter."""
    params = cfg["params"]
    g = geom(cfg)
    fig, axes = plt.subplots(len(params), 1, figsize=(18, 2 + 3.2 * len(params)), sharex=True, squeeze=False)
    axes = axes[:, 0]
    x = np.arange(len(sns))
    for ax, (pid, name, _) in zip(axes, params):
        lv = results[pid]["lv"]
        bottom = np.zeros(len(sns))
        for level in FLAG:
            cnt = (lv == level).sum(axis=1)
            ax.bar(x, cnt, bottom=bottom, color=LEVEL_COLORS[level], label=level, edgecolor='black', linewidth=0.3)
            bottom += cnt
        for i, t in enumerate(bottom):
            if t > 0:
                ax.text(i, t, f"{int(t)}", ha='center', va='bottom', fontsize=7)
        ax.set_ylabel(f"Flagged {g['abbr']}")
        ax.set_title(f"{name} ({pid}) - {g['item']}s beyond 3σ per board", fontsize=11, loc='left')
        ax.set_ylim(0, max(1, bottom.max()) * 1.25)
        ax.grid(axis='y', alpha=0.3)
        ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    axes[0].legend(loc='upper right', fontsize=9, ncol=2)
    axes[-1].set_xticks(x)
    axes[-1].set_xticklabels(sns, rotation=90, fontsize=8)
    axes[-1].set_xlabel(f"FEMB SN ({SN_PREFIX}xxxxx)")
    fig.suptitle(f"Report {cfg['sec'].replace('_', '.')} {cfg['title']} - Flagged {g['Item']}s per Board", fontsize=14)
    top = 1 - 1.1 / (2 + 3.2 * len(params))
    bottom = 1.9 / (2 + 3.2 * len(params))
    fig.subplots_adjust(left=0.05, right=0.985, top=top, bottom=bottom, hspace=0.35)
    plt.savefig(os.path.join(out_dir, f"plot_{cfg['sec']}_board_summary.png"), dpi=150)
    plt.close()


# -------------------------------------------------------------------- report

def write_report(cfg, boards, results, out_dir):
    sec, secd = cfg["sec"], cfg["sec"].replace("_", ".")
    sns = list(boards.keys())
    nb = len(sns)
    rel = os.path.relpath(out_dir, cfg["here"])
    dates = sorted(fmt_time(b["time"]) for b in boards.values())
    params = cfg["params"]
    g = geom(cfg)
    n, it, unit, grp = g["n"], g["item"], g["unit"], g["group"]

    md = [f"# FEMB QC Parameter Evaluation - Report Section {secd}: {cfg['title']}\n"]
    md.append("**Board version:** FEMB-IO 1826-1L  ")
    md.append(f"**Boards used:** {nb} (latest passing test per board; excluded: {', '.join(EXCLUDED_BOARDS)})  ")
    md.append(f"**{g['Item']}s:** {nb} × {n} = {nb * n}  ")
    md.append(f"**Test period:** {dates[0]} - {dates[-1]}  ")
    md.append(f"**Configuration:** {cfg['configuration']}  ")
    md.append(f"**Generated:** {datetime.now():%Y-%m-%d %H:%M}  ")
    md.append(f"**Script:** `{cfg['script']}`\n")

    md.append("## 1. Scope\n")
    md += cfg["scope"]
    md.append("| Parameter | Description |")
    md.append("|---|---|")
    for pid, name, desc in params:
        md.append(f"| `{pid}` – {name} | {desc} |")
    md.append("")

    md.append("## 2. Judgement Method\n")
    md.append(f"For each parameter the mean and σ are computed over all {nb * n} {it}s pooled together; "
              f"each {it} is graded by |x − mean| / σ. A board takes the worst level among its {it}s.\n")
    md.append(cfg.get("limit_note",
                      f"Channel-level (noise / pulse) parameters use **{MAX_SIGMA}σ as the limit**: a channel beyond "
                      f"{MAX_SIGMA}σ fails. (Board-level power and LDO parameters keep the wider 7σ limit.)") + "\n")
    md.append("| Level | Deviation | Plot background |")
    md.append("|---|---|---|")
    md.append("| PASS | ≤ 3σ | green |")
    md.append("| WARN | 3σ – 5σ | yellow |")
    md.append("| FAIL | > 5σ | red |\n")
    md.append(f"For a Gaussian distribution, about 0.27 % of {it}s (≈ {0.0027 * nb * n:.0f} of "
              f"{nb * n}) are expected beyond 3σ by chance, so isolated WARN {it}s are normal.\n")

    md.append("## 3. Summary\n")
    md.append("| Parameter | Mean | Std | Min | Max | PASS | WARN | FAIL | Boards with ≥1 FAIL |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    for pid, name, _ in params:
        r = results[pid]
        c = {l: int((r["lv"] == l).sum()) for l in LEVELS}
        bad = [sns[i] for i in range(nb) if (r["lv"][i] == "FAIL").any()]
        md.append(f"| `{pid}` | {r['mean']:.2f} | {r['std']:.2f} | {r['min']:.2f} | {r['max']:.2f} | "
                  f"{c['PASS']} | {c['WARN']} | {c['FAIL']} | {', '.join(bad) or '–'} |")
    md.append("")
    md.append(f"### Criteria (limits, {'ADC counts' if unit == 'ADC' else unit})\n")
    md.append("| Parameter | −5σ (FAIL) | −3σ | Mean | +3σ | +5σ (FAIL) |")
    md.append("|---|---|---|---|---|---|")
    for pid, *_ in params:
        m, s = results[pid]["mean"], results[pid]["std"]
        md.append(f"| `{pid}` | " + " | ".join(f"{m + k * s:.2f}" for k in (-5, -3, 0, 3, 5)) + " |")
    md.append("")
    md.append(f"### Flagged {it}s per board\n")
    md.append(f"![board summary]({rel}/plot_{sec}_board_summary.png)\n")

    def section(num, pid, name):
        r = results[pid]
        out = [f"### {num} {name} (`{pid}`)\n"]
        out.append(f"Mean = {r['mean']:.2f}, σ = {r['std']:.2f}, range [{r['min']:.2f}, {r['max']:.2f}] {unit}. "
                   f"Spread of per-board means: σ = {r['board_mean_std']:.2f}; "
                   f"spread of per-{it} means across boards: σ = {r['chan_mean_std']:.2f}.\n")
        out.append(f"![{pid}]({rel}/plot_{sec}_{pid.replace(' ', '_')}.png)\n")
        idx = np.argwhere(np.isin(r["lv"], FLAG))
        if len(idx):
            rows = sorted(((sns[b], c, r["mat"][b, c], r["nsig"][b, c], r["lv"][b, c]) for b, c in idx),
                          key=lambda t: -t[3])
            out.append(f"{len(rows)} {it}(s) beyond 3σ:\n")
            out.append(f"| FEMB SN | {g['Item']} |" + (" Chip |" if grp else "") + " Value | Deviation | Level |")
            out.append("|---|---|" + ("---|" if grp else "") + "---|---|---|")
            for sn, c, v, ns, l in rows:
                lvl = l if l == "WARN" else f"**{l}**"
                chip = f" {c // grp} |" if grp else ""
                out.append(f"| {SN_PREFIX}{sn} | {c} |{chip} {v:.2f} | {ns:.1f}σ | {lvl} |")
            out.append("")
        else:
            out.append(f"All {it}s within 3σ.\n")
        return out

    md.append("## 4. Parameters\n")
    for i, (pid, name, _) in enumerate(params, 1):
        md += section(f"4.{i}", pid, name)

    md.append("## 5. Observations\n")
    for pid, name, _ in params:
        r = results[pid]
        bad = {}
        for b, c in np.argwhere(r["lv"] == "FAIL"):
            bad.setdefault(sns[b], []).append(f"{g['abbr']}{c} {r['nsig'][b, c]:.1f}σ")
        if bad:
            md.append(f"- **{pid}** FAIL: " + "; ".join(f"{sn} ({', '.join(v)})" for sn, v in sorted(bad.items())))
        else:
            md.append(f"- **{pid}**: no {it} beyond {MAX_SIGMA}σ.")
    # Flagged channels clustering on one chip point to a chip-level shift rather than random fluctuation
    for pid, name, _ in (params if grp else []):
        r = results[pid]
        chips = {}
        for b, c in np.argwhere(np.isin(r["lv"], FLAG)):
            chips.setdefault((sns[b], c // grp), []).append(int(c))
        for (sn, chip), chans in sorted(chips.items()):
            if len(chans) >= CHIP_CLUSTER:
                md.append(f"- **{pid}**: {SN_PREFIX}{sn} chip {chip} has {len(chans)} flagged channels "
                          f"({', '.join(f'ch{c}' for c in chans)}) – clustered on one chip, "
                          "suggests a chip-level offset rather than random channels.")
    if cfg.get("observations"):
        md += cfg["observations"](results)
    md.append("")

    md.append("## Appendix A: Per-Board Judgement\n")
    md.append(f"Each cell: number of {it}s WARN / FAIL, and worst deviation.\n")
    ids = [p[0] for p in params]
    md.append("| FEMB SN | Test time | " + " | ".join(f"`{p}`" for p in ids) + " | Worst |")
    md.append("|---|---|" + "---|" * len(ids) + "---|")
    for bi, sn in enumerate(sns):
        cells, worst = [], "PASS"
        for pid in ids:
            r = results[pid]
            lv = r["lv"][bi]
            w, f = (int((lv == l).sum()) for l in FLAG)
            mx = np.nanmax(r["nsig"][bi])
            cell = f"{w}/{f} ({mx:.1f}σ)"
            cells.append(f"**{cell}**" if f else cell)
            for l in FLAG:
                if (lv == l).any() and LEVELS.index(l) > LEVELS.index(worst):
                    worst = l
        md.append(f"| {SN_PREFIX}{sn} | {fmt_time(boards[sn]['time'])} | " + " | ".join(cells) + f" | {worst} |")
    md.append("")
    md.append("## Appendix B: Output Files\n")
    md.append(f"- `{rel}/criteria_{sec}.csv` – mean, σ and 3σ/5σ limits per parameter")
    md.append(f"- `{rel}/judgement_{sec}_{it}s.csv` – every {it} beyond 3σ (board, {it}, value, deviation, level)")
    md.append(f"- `{rel}/judgement_{sec}_boards.csv` – per-board counts and worst level")
    md.append(f"- `{rel}/plot_{sec}_*.png` – distribution plots and per-board summary\n")

    with open(os.path.join(cfg["here"], cfg["report"]), 'w', encoding='utf-8') as f:
        f.write("\n".join(md))


# ----------------------------------------------------------------------- run

def run(cfg):
    sec = cfg["sec"]
    g = geom(cfg)
    out_dir = os.path.join(cfg["here"], "output")
    os.makedirs(out_dir, exist_ok=True)
    boards = load_boards()
    sns = list(boards.keys())
    for b in boards.values():
        b["block"] = cfg["extract_board"](b) if "extract_board" in cfg else cfg["extract"](b["rows"])
    print(f"Report {sec.replace('_', '.')} {cfg['title']} - {len(sns)} boards")

    results = {}
    for pid, name, _ in cfg["params"]:
        mat = np.array([boards[sn]["block"].get(pid, np.full(g["n"], np.nan)) for sn in sns], dtype=float)
        valid = mat[~np.isnan(mat)]
        mean, std = float(valid.mean()), float(valid.std())
        nsig = np.abs(mat - mean) / std
        lv = judge_array(nsig, MAX_SIGMA)
        results[pid] = {"mat": mat, "mean": mean, "std": std, "min": float(valid.min()),
                        "max": float(valid.max()), "nsig": nsig, "lv": lv,
                        "board_mean_std": float(np.nanmean(mat, axis=1).std()),
                        "chan_mean_std": float(np.nanmean(mat, axis=0).std())}
        plot_param(cfg, sns, results[pid], pid, name, out_dir)

        c = {l: int((lv == l).sum()) for l in LEVELS}
        print(f"\n{pid:9s} mean={mean:.2f} std={std:.2f}  " + "  ".join(f"{l}={c[l]}" for l in LEVELS))
        for b, ch in sorted(np.argwhere(lv == "FAIL"), key=lambda t: -nsig[t[0], t[1]]):
            print(f"    {lv[b, ch]:5s} 1826-1L_{sns[b]} {g['abbr']}{ch:3d}  {mat[b, ch]:.2f}  {nsig[b, ch]:.1f}σ")

    plot_board_summary(cfg, sns, results, out_dir)

    with open(os.path.join(out_dir, f"criteria_{sec}.csv"), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(["Parameter", "Name", "Role", "Mean", "Std", "Min", "Max", "N",
                    "Lower_3Sigma", "Upper_3Sigma", "Lower_5Sigma_FAIL", "Upper_5Sigma_FAIL"]
                   + [f"N_{l}" for l in LEVELS])
        for pid, name, _ in cfg["params"]:
            r = results[pid]
            m, s = r["mean"], r["std"]
            w.writerow([pid, name, "core", f"{m:.4f}", f"{s:.4f}", f"{r['min']:.4f}", f"{r['max']:.4f}",
                        int((~np.isnan(r["mat"])).sum())]
                       + [f"{m + sg * k * s:.4f}" for k in (3, 5) for sg in (-1, 1)]
                       + [int((r["lv"] == l).sum()) for l in LEVELS])

    with open(os.path.join(out_dir, f"judgement_{sec}_{g['item']}s.csv"), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(["FEMB_SN", "Parameter", g["Item"]] + (["Chip"] if g["group"] else []) + ["Value", "NSigma", "Level"])
        for pid, *_ in cfg["params"]:
            r = results[pid]
            for b, ch in np.argwhere(np.isin(r["lv"], FLAG)):
                w.writerow([SN_PREFIX + sns[b], pid, ch] + ([ch // g["group"]] if g["group"] else []) + [f"{r['mat'][b, ch]:.3f}",
                            f"{r['nsig'][b, ch]:.2f}", r["lv"][b, ch]])

    with open(os.path.join(out_dir, f"judgement_{sec}_boards.csv"), 'w', newline='') as f:
        w = csv.writer(f)
        pids = [p[0] for p in cfg["params"]]
        w.writerow(["FEMB_SN", "Test_time"]
                   + [f"{p}_{s}" for p in pids for s in ("N_WARN", "N_FAIL", "Max_NSigma")]
                   + ["Worst"])
        for bi, sn in enumerate(sns):
            row, worst = [SN_PREFIX + sn, fmt_time(boards[sn]["time"])], "PASS"
            for pid in pids:
                lv = results[pid]["lv"][bi]
                row += [int((lv == l).sum()) for l in FLAG]
                row.append(f"{np.nanmax(results[pid]['nsig'][bi]):.2f}")
                for l in FLAG:
                    if (lv == l).any() and LEVELS.index(l) > LEVELS.index(worst):
                        worst = l
            w.writerow(row + [worst])

    write_report(cfg, boards, results, out_dir)
    print(f"\nOutput: {out_dir}")
    print(f"Report: {os.path.join(cfg['here'], cfg['report'])}")
    return boards, results
