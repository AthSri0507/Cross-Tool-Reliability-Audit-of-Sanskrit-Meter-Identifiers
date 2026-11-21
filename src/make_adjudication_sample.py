"""Stratified sample of tool disagreements that need a human verdict.

Usage: python src/make_adjudication_sample.py --out results/adjudication_sample.csv

Strata (automatic first-pass classes from classify_faults.py and the verse-level comparison):
  B-length        skrutable fault; a pada has extra/missing syllables vs the gana formula
  B-internal      skrutable fault; same length, pattern differs at a non-final position
  B-anustubh      skrutable fault tag on an anustubh verse (asamicina / adhika / una / vikrta)
  B-padanta       fault only at pada-final syllables (sanity check of the automatic finding)
  C-boundary      verse L/G differs only at the last syllable of line 1 (half-verse boundary)
  C-other         verse L/G differs elsewhere (re-splitting of an irregular verse)
  D-name          same L/G, but chanda's candidate names do not include skrutable's meter
"""
import argparse
import collections
import csv
import json
import random

QUOTA = {"B-length": 12, "B-internal": 12, "B-anustubh": 12, "B-padanta": 4,
         "C-boundary": 4, "C-other": 10, "D-name": 12}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verses", default="data/interim/verses_labeled_v2.jsonl")
    ap.add_argument("--faults", default="results/fault_classes.jsonl")
    ap.add_argument("--lines", default="data/interim/audit_lines.jsonl")
    ap.add_argument("--out", default="results/adjudication_sample.csv")
    ap.add_argument("--seed", type=int, default=21)
    args = ap.parse_args()
    rng = random.Random(args.seed)

    V = {v["id"]: v for v in (json.loads(l) for l in open(args.verses, encoding="utf-8"))}
    F = {r["id"]: r["fault_class"] for r in (json.loads(l) for l in open(args.faults, encoding="utf-8"))}
    lines = collections.defaultdict(list)
    for l in open(args.lines, encoding="utf-8"):
        r = json.loads(l)
        lines[r["verse_id"]].append(r)

    strata = collections.defaultdict(list)
    for vid, v in V.items():
        if v["gold"]:
            continue
        if vid in F:
            fc = F[vid]
            s = {"length": "B-length", "internal": "B-internal", "padanta_only": "B-padanta"}.get(
                fc, "B-anustubh" if fc.startswith("skr_tag") and v["meter_class"] == "anustubh" else None)
        elif not v["agree_lg"]:
            a, cut = "".join(v["chanda_lg"]), len(v["chanda_lg"][0])
            b = "".join(v["skr_lg_padas"])
            d = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
            s = "C-boundary" if len(a) == len(b) and d and all(i == cut - 1 for i in d) else "C-other"
        elif not v["agree_meter"]:
            s = "D-name"
        else:
            s = None
        if s:
            strata[s].append(v)

    with open(args.out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sample_id", "stratum", "verse_id", "source", "text", "skrutable_label",
                    "chanda_meters", "chanda_LG_by_line", "skrutable_LG_by_pada",
                    "proposed_cause", "proposed_rationale", "human_cause", "human_notes"])
        k = 0
        for s, quota in QUOTA.items():
            rows = sorted(strata[s], key=lambda v: v["id"])
            rng.shuffle(rows)
            for v in rows[:quota]:
                k += 1
                names = sorted({n for x in v["chanda_names"] for n in x})[:4]
                w.writerow([k, s, v["id"], v["source"], " / ".join(v["lines"]), v["skr_label"],
                            "; ".join(names), " / ".join(v["chanda_lg"]), " / ".join(v["skr_lg_padas"]),
                            "", "", "", ""])
    print("stratum sizes (population):", {s: len(strata[s]) for s in QUOTA})
    print(f"wrote {k} rows -> {args.out}")


if __name__ == "__main__":
    main()
