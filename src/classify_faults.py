"""Automatic first-pass classification of verses where both tools scan identically
but skrutable reports a metrical fault (audit outcome B).

Usage: python src/classify_faults.py data/interim/verses_labeled_v2.jsonl results/fault_classes.jsonl

For fixed-pattern meters, each flagged verse is compared pada by pada with the
meter's canonical pattern (the most frequent pattern among gold verses of that
meter):
  padanta_only   differs only at pada-final syllables (padanta-guru convention)
  internal       same length, differs at a non-final position (text error or licence)
  length         a pada has extra/missing syllables (text error, encoding, sandhi)
Anustubh is variable by definition, so its verses keep skrutable's own fault tag.
"""
import collections
import json
import re
import sys
from pathlib import Path


GANA = {"y": "LGG", "m": "GGG", "t": "GGL", "r": "GLG", "j": "LGL", "B": "GLL",
        "n": "LLL", "s": "LLG", "g": "G", "l": "L"}
BRACKET = re.compile(r"\[(\d+): ([ymtrjBnsgl]+)\]\s*([\d,]*)")


def pattern_from_label(label: str):
    """Four pada L/G patterns decoded from skrutable's gana notation, or None.

    '[17: mBnttgg]'                          -> same pattern for all four padas
    '[10: ssjg] 1,3 + [11: sBrlg] 2,4'       -> odd / even padas
    '[10: sjsl] + [10: nsjg] + [11: ..] + [13: ..]' -> one bracket per pada
    """
    found = BRACKET.findall(label)
    if not found:
        return None
    pats = []
    for n, ganas, _ in found:
        p = "".join(GANA[c] for c in ganas)
        if len(p) != int(n):
            return None
        pats.append((p, _))
    if len(pats) == 1:
        return [pats[0][0]] * 4
    if len(pats) == 2 and pats[0][1] == "1,3" and pats[1][1] == "2,4":
        return [pats[0][0], pats[1][0], pats[0][0], pats[1][0]]
    if len(pats) == 4:
        return [p for p, _ in pats]
    return None


def classify(v, canon):
    padas = v["skr_lg_padas"]
    ref = pattern_from_label(v["skr_label"]) or canon.get(v["meter"])
    if v["meter_class"] == "anustubh" or ref is None:
        lab = v["skr_label"]
        for tag in ("asamīcīnā", "adhikākṣarā", "ūnākṣarā", "vikṛtavṛtta"):
            if tag in lab:
                return f"skr_tag:{tag}"
        return "skr_tag:other"
    if len(padas) != len(ref) or any(len(p) != len(r) for p, r in zip(padas, ref)):
        return "length"
    diff_final = any(p[-1] != r[-1] for p, r in zip(padas, ref))
    diff_inner = any(p[:-1] != r[:-1] for p, r in zip(padas, ref))
    if diff_inner:
        return "internal"
    return "padanta_only" if diff_final else "matches_canon"


def main(inp, outp):
    V = [json.loads(l) for l in open(inp, encoding="utf-8")]
    gold_pats = collections.defaultdict(collections.Counter)
    for v in V:
        if v["gold"] and v["meter_class"] not in ("anustubh", "upajati"):
            gold_pats[v["meter"]][tuple(v["skr_lg_padas"])] += 1
    canon = {m: list(c.most_common(1)[0][0]) for m, c in gold_pats.items()}
    B = [v for v in V if not v["gold"] and not v["skr_perfect"] and v["agree_lg"]]
    Path(outp).parent.mkdir(parents=True, exist_ok=True)
    counts = collections.Counter()
    by_meter = collections.defaultdict(collections.Counter)
    with open(outp, "w", encoding="utf-8") as f:
        for v in B:
            c = classify(v, canon)
            counts[c] += 1
            by_meter[v["meter"]][c] += 1
            f.write(json.dumps({"id": v["id"], "meter": v["meter"], "fault_class": c,
                                "skr_label": v["skr_label"]}, ensure_ascii=False) + "\n")
    print(f"{len(B)} verses with a skrutable-reported fault:")
    for k, n in counts.most_common():
        print(f"  {k:28s}{n:5d}")
    print("padanta_only by meter:", {m: c["padanta_only"] for m, c in by_meter.items() if c["padanta_only"]})


if __name__ == "__main__":
    main(*sys.argv[1:3])
