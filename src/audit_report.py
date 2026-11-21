"""Tables for the tool-audit paper, plus a stratified sample for manual adjudication.

Usage:
  python src/audit_report.py --lines data/interim/audit_lines.jsonl \
      --verses data/interim/verses_labeled_v2.jsonl --out results/audit_report.md \
      --sample-out results/adjudication_sample.csv --per-stratum 15

Tables
  T1  corpus: verses and lines per source text
  T2  line-level L/G agreement between chanda and skrutable under three chanda
      input modes (as printed / all spaces stripped / boundary-aware join),
      overall and per source, with Wilson 95% CIs
  T3  verse-level outcomes (gold / both flag the text / L/G differs / meter name differs / tool crash)
  T4  residual line-level disagreements under the boundary-aware join, by span type
Adjudication sample
  up to --per-stratum verses from each non-gold verse outcome, written to CSV
  with empty columns for the human verdict.
"""
import argparse
import collections
import csv
import difflib
import json
import math
import random
import re


def wilson(k, n, z=1.96):
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def pct(k, n):
    lo, hi = wilson(k, n)
    return f"{100*k/n:.1f} [{100*lo:.1f}, {100*hi:.1f}]" if n else "-"


def verse_outcome(v):
    if v["skr_label"].startswith("ERROR"):
        return "X. skrutable crashed"
    if v["gold"]:
        return "A. full agreement (consensus set)"
    if not v["skr_perfect"] and v["agree_lg"]:
        return "B. same L/G; skrutable reports a metrical fault"
    if not v["agree_lg"]:
        return "C. L/G sequences differ"
    if not v["agree_meter"]:
        return "D. same L/G; meter names differ"
    return "E. other"


def norm(s):
    return s.replace("'", "").replace("ai", "E").replace("au", "O")


def span_type(line):
    """Coarse label for why one line's L/G differs under the boundary-aware join."""
    a = [norm(x) for x in line["chanda_syl"]]
    b = [norm(x) for x in line["skr_syl"]]
    if a == b:
        return "same syllables, weight differs"
    if len(a) != len(b):
        sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
        ops = [op for op in sm.get_opcodes() if op[0] != "equal"]
        a_txt = "".join("".join(a[i1:i2]) for _, i1, i2, _, _ in ops)
        if re.search(r"[aAiIuUfFeEoO]$", a_txt) and len(a) < len(b):
            return "syllable count differs (vowel junction)"
        return "syllable count differs (other)"
    return "same count, different division"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lines", default="data/interim/audit_lines.jsonl")
    ap.add_argument("--verses", default="data/interim/verses_labeled_v2.jsonl")
    ap.add_argument("--out", default="results/audit_report.md")
    # Legacy first-pass sample. Off by default: the study's sample is drawn by
    # make_adjudication_sample.py and must not be overwritten.
    ap.add_argument("--sample-out", default=None)
    ap.add_argument("--per-stratum", type=int, default=15)
    ap.add_argument("--seed", type=int, default=11)
    args = ap.parse_args()

    L = [json.loads(l) for l in open(args.lines, encoding="utf-8")]
    V = [json.loads(l) for l in open(args.verses, encoding="utf-8")]
    ok = [l for l in L if "error" not in l]
    out = ["# Tool audit: chanda vs skrutable", ""]

    # T1
    vs = collections.Counter(v["source"] for v in V)
    ls = collections.Counter(l["source"] for l in L)
    out += ["## T1. Corpus", "", "| Text | Verses | Lines |", "|---|---|---|"]
    for s in sorted(vs):
        out.append(f"| {s} | {vs[s]} | {ls[s]} |")
    out += [f"| **Total** | **{len(V)}** | **{len(L)}** |", ""]

    # T2
    modes = [("lg_agree_spaced", "as printed (spaced)"), ("lg_agree_naive", "all spaces stripped"),
             ("lg_agree", "boundary-aware join")]
    out += ["## T2. Line-level L/G agreement with skrutable, by chanda input mode",
            "", "| Text | n lines | " + " | ".join(m for _, m in modes) + " |",
            "|---|---|" + "---|" * len(modes)]
    by_src = collections.defaultdict(list)
    for l in ok:
        by_src[l["source"]].append(l)
    for s in sorted(by_src):
        g = by_src[s]
        out.append(f"| {s} | {len(g)} | " + " | ".join(pct(sum(x[k] for x in g), len(g)) for k, _ in modes) + " |")
    out.append(f"| **All** | **{len(ok)}** | " + " | ".join(
        "**" + pct(sum(x[k] for x in ok), len(ok)) + "**" for k, _ in modes) + " |")
    out += ["", f"Lines where a tool raised an error: {len(L) - len(ok)}", ""]

    # T3
    oc = collections.Counter(verse_outcome(v) for v in V)
    out += ["## T3. Verse-level outcomes (boundary-aware join)", "", "| Outcome | Verses | % [95% CI] |", "|---|---|---|"]
    for k in sorted(oc):
        out.append(f"| {k} | {oc[k]} | {pct(oc[k], len(V))} |")
    out.append("")

    # T4
    resid = [l for l in ok if not l["lg_agree"]]
    tc = collections.Counter(span_type(l) for l in resid)
    out += ["## T4. Residual line-level disagreements (boundary-aware join)", "",
            f"{len(resid)} of {len(ok)} lines disagree.", "", "| Type | Lines |", "|---|---|"]
    for k, n in tc.most_common():
        out.append(f"| {k} | {n} |")
    out.append("")

    # Consensus-set summary (the `gold` field marks consensus membership)
    gold = [v for v in V if v["gold"]]
    out += ["## Consensus set (released dataset, silver standard)", "",
            f"{len(gold)} verses; by class: {dict(collections.Counter(v['meter_class'] for v in gold))}", ""]

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print("wrote", args.out)

    # Adjudication sample (legacy; only when --sample-out is given)
    if not args.sample_out:
        return
    rng = random.Random(args.seed)
    strata = collections.defaultdict(list)
    for v in V:
        o = verse_outcome(v)
        if not o.startswith("A."):
            strata[o].append(v)
    lines_by_verse = collections.defaultdict(list)
    for l in L:
        lines_by_verse[l["verse_id"]].append(l)
    with open(args.sample_out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sample_id", "stratum", "verse_id", "source", "text", "skrutable_label",
                    "chanda_meters", "chanda_LG", "skrutable_LG", "line_diffs",
                    "proposed_cause", "proposed_rationale", "human_cause", "human_notes"])
        k = 0
        for stratum in sorted(strata):
            rows = sorted(strata[stratum], key=lambda v: v["id"])
            rng.shuffle(rows)
            for v in rows[: args.per_stratum]:
                k += 1
                diffs = []
                for l in lines_by_verse[v["id"]]:
                    if "error" in l:
                        diffs.append(f"L{l['line_idx']}: ERROR {l['error'][:60]}")
                    elif not l["lg_agree"]:
                        diffs.append(f"L{l['line_idx']}: chanda {' '.join(l['chanda_syl'])} | skr {' '.join(l['skr_syl'])}")
                names = sorted({n for x in v["chanda_names"] for n in x})[:4]
                w.writerow([k, stratum, v["id"], v["source"], " / ".join(v["lines"]), v["skr_label"],
                            "; ".join(names), " / ".join(v["chanda_lg"]), " / ".join(v["skr_lg_padas"]),
                            " || ".join(diffs), "", "", "", ""])
    print("wrote", args.sample_out, f"({k} verses)")


if __name__ == "__main__":
    main()
