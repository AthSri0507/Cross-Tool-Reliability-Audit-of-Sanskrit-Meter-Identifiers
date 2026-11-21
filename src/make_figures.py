"""Figures for the IEEE paper (print-safe: palette validated, plus markers and hatching).

Usage: python src/make_figures.py --out figures
"""
import argparse
import collections
import csv
import re
from pathlib import Path

import matplotlib
import matplotlib.ticker

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# Reference categorical palette, first slots in fixed order (validated: dataviz validate_palette.js).
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]
INK, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#ffffff"
NAMES = {
    "Sisupalavadha": "Śiśupālavadha", "Raghuvamsa": "Raghuvaṃśa", "Saundarananda": "Saundarananda",
    "Kiratarjuniya": "Kirātārjunīya", "Bhagavadgita": "Bhagavadgītā", "Kumarasambhava": "Kumārasambhava",
    "Buddhacarita": "Buddhacarita", "Bhartrhari": "Bhartṛhari", "Meghaduta": "Meghadūta",
    "Saundaryalahari": "Saundaryalaharī", "Bhallatasataka": "Bhallaṭaśataka", "Amarusataka": "Amaruśataka",
}

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"], "font.size": 8,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": INK,
    "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 300,
})


def fig_line_agreement(out):
    rows = []
    for line in open("results/audit_report.md", encoding="utf-8"):
        m = re.match(r"\| (\w+) \| (\d+) \| ([\d.]+) \[.*?\] \| ([\d.]+) \[.*?\] \| ([\d.]+) \[", line)
        if m and m.group(1) != "All":
            rows.append((m.group(1), float(m.group(3)), float(m.group(4)), float(m.group(5))))
    rows.sort(key=lambda r: r[1])  # worst as-printed agreement at the bottom
    fig, ax = plt.subplots(figsize=(3.45, 2.9))
    y = range(len(rows))
    for i, r in enumerate(rows):
        ax.plot([r[1], r[3]], [i, i], color=GRID, lw=1.2, zorder=1)
    spec = [("as printed", 1, "o"), ("all spaces stripped", 2, "s"), ("boundary-aware join", 3, "D")]
    for k, (lab, col, mk) in enumerate(spec):
        ax.scatter([r[col] for r in rows], list(y), s=22, marker=mk, color=SERIES[k],
                   edgecolor=SURFACE, linewidth=0.8, zorder=3 + k, label=lab)
    ax.set_yticks(list(y))
    ax.set_yticklabels([NAMES[r[0]] for r in rows])
    ax.set_xlim(40, 101)
    ax.set_xlabel("Lines with identical L/G sequence (%)")
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(loc="lower center", bbox_to_anchor=(0.42, 1.0), ncol=3, frameon=False,
              fontsize=7, handletextpad=0.2, columnspacing=0.8)
    fig.tight_layout(pad=0.3)
    for ext in ("png", "pdf"):
        fig.savefig(out / f"fig_line_agreement.{ext}", bbox_inches="tight")
    plt.close(fig)


def fig_causes(out):
    rows = list(csv.DictReader(open("results/adjudication_verified.csv", encoding="utf-8-sig")))
    strata = [("B-length", "B: length deviation"), ("B-internal", "B: internal deviation"),
              ("B-anustubh", "B: anuṣṭubh fault"), ("B-padanta", "B: pāda-final only"),
              ("C-boundary", "C: line-boundary weight"), ("C-other", "C: other L/G difference"),
              ("D-name", "D: name mismatch")]
    causes = [("TXT", "e-text error", ""), ("PAD", "pāda-final convention", "///"),
              ("DB", "database/naming", "..."), ("LIC", "metrical licence", "xx"),
              ("ENC", "encoding convention", "\\\\\\"), ("UNK", "undecided", "--")]
    cnt = collections.Counter((r["stratum"], r["verified_cause"]) for r in rows)
    fig, ax = plt.subplots(figsize=(3.45, 2.5))
    plt.rcParams["hatch.linewidth"] = 0.5
    for i, (s, _) in enumerate(strata):
        left = 0
        for k, (c, lab, hatch) in enumerate(causes):
            v = cnt[(s, c)]
            if not v:
                continue
            ax.barh(i, v - 0.12, left=left + 0.06, height=0.62, color=SERIES[k], hatch=hatch,
                    edgecolor=SURFACE, linewidth=0, label=lab if i == 0 or not any(
                        cnt[(t, c)] for t, _ in strata[:i]) else None)
            if v >= 2:
                ax.text(left + v / 2, i, str(v), ha="center", va="center", fontsize=6.5, color=INK,
                        bbox=dict(boxstyle="round,pad=0.15", fc=SURFACE, ec="none"))
            left += v
    ax.set_yticks(range(len(strata)))
    ax.set_yticklabels([lab for _, lab in strata])
    ax.invert_yaxis()
    ax.set_xlabel("Sampled verses")
    ax.set_xlim(0, 12.3)
    ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(2))
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    h, l = ax.get_legend_handles_labels()
    order = [l.index(lab) for _, lab, _ in causes if lab in l]
    ax.legend([h[i] for i in order], [l[i] for i in order], loc="lower center",
              bbox_to_anchor=(0.35, 1.0), ncol=3, frameon=False, fontsize=6.5,
              handlelength=1.4, columnspacing=0.8)
    fig.tight_layout(pad=0.3)
    for ext in ("png", "pdf"):
        fig.savefig(out / f"fig_causes.{ext}", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="figures")
    out = Path(ap.parse_args().out)
    out.mkdir(parents=True, exist_ok=True)
    fig_line_agreement(out)
    fig_causes(out)
    print("figures ->", out)
