"""Third-tool check: scan every verse with vidyut-chandas, an independent implementation.

vidyut (ambuda-org, v0.4.0) scans SLP1 text with its own syllabifier and weight
rules, and names vṛtta meters from a list derived from the Vṛttaratnākara via
Rajagopalan's project (no anuṣṭubh, no upajāti, no mātrā meters).

For each line we compare vidyut's L/G with the consensus L/G (chanda with the
boundary-aware join; identical to skrutable on consensus verses), on all
syllables and on all but the line-final one (vidyut leaves a short final
syllable closed by a consonant light). For consensus verses whose meter is in
vidyut's list we also compare the meter name.

Usage: python src/vidyut_check.py
Writes results/vidyut_check.md and data/interim/vidyut_lines.jsonl
"""
import collections
import json
import re
import unicodedata
from math import sqrt
from pathlib import Path

from indic_transliteration import sanscript
from vidyut.chandas import Chandas

ROOT = Path(__file__).resolve().parent.parent
SLP1_OK = re.compile(r"[^aAiIuUfFxXeEoOMHkKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzsh'\s]")


def to_slp1(line):
    s = sanscript.transliterate(line, sanscript.IAST, sanscript.SLP1)
    return SLP1_OK.sub("", s).strip()


def norm_name(n):
    n = unicodedata.normalize("NFKD", n.lower())
    n = "".join(c for c in n if not unicodedata.combining(c))
    return re.sub(r"[^a-z]", "", n)


def wilson(k, n, z=1.96):
    p = k / n
    c = (p + z * z / 2 / n) / (1 + z * z / n)
    h = z * sqrt(p * (1 - p) / n + z * z / 4 / n / n) / (1 + z * z / n)
    return f"{100 * p:.2f}% [{100 * (c - h):.2f}, {100 * (c + h):.2f}]"


def main():
    ch = Chandas(str(ROOT / "data/raw/vidyut/chandas/meters.tsv"))
    known = {}
    for row in open(ROOT / "data/raw/vidyut/chandas/meters.tsv", encoding="utf-8"):
        name = row.split("\t")[0]
        known[norm_name(sanscript.transliterate(name, sanscript.SLP1, sanscript.IAST))] = name
    V = [json.loads(l) for l in open(ROOT / "data/interim/verses_labeled_v2.jsonl", encoding="utf-8")]
    stats = collections.defaultdict(collections.Counter)
    name_stats = collections.Counter()
    name_by_meter = collections.defaultdict(collections.Counter)
    rows = []
    for v in V:
        group = ("A" if v["gold"] else "B" if v["agree_lg"] and not v["skr_perfect"] else
                 "C" if not v["agree_lg"] else "D")
        for i, line in enumerate(v["lines"]):
            ref = v["chanda_lg"][i] if i < len(v["chanda_lg"]) else None
            try:
                m = ch.classify(to_slp1(line))
                vid = "".join("".join(a.weight for a in l) for l in m.aksharas)
            except BaseException:  # noqa: BLE001 - the Rust core panics on odd input
                vid = None
            if ref is None or vid is None:
                stats[group]["error"] += 1
                continue
            stats[group]["lines"] += 1
            if vid == ref:
                stats[group]["exact"] += 1
            if len(vid) == len(ref) and vid[:-1] == ref[:-1]:
                stats[group]["exact_but_final"] += 1
            elif len(vid) != len(ref):
                stats[group]["length_diff"] += 1
            rows.append({"id": v["id"], "line": i, "group": group, "ref": ref, "vidyut": vid})
        if v["gold"]:
            key = norm_name(v["meter"])
            if key in known:
                try:
                    m = ch.classify(to_slp1("\n".join(v["lines"])))
                    p = m.padya if isinstance(m.padya, (str, type(None))) else m.padya.name
                except BaseException:  # noqa: BLE001
                    p = None
                got = norm_name(sanscript.transliterate(p, sanscript.SLP1, sanscript.IAST)) if p else None
                ok = got == key
                name_stats["evaluable"] += 1
                name_stats["same"] += ok
                name_stats["none"] += p is None
                name_by_meter[v["meter"]]["n"] += 1
                name_by_meter[v["meter"]]["same"] += ok
    with open(ROOT / "data/interim/vidyut_lines.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    out = ["# Third-tool check with vidyut-chandas 0.4.0", "",
           "| Verse group | Lines | vidyut L/G identical | identical except line-final syllable | length differs | not scannable |",
           "|---|---|---|---|---|---|"]
    names = {"A": "A consensus", "B": "B same L/G, fault", "C": "C L/G differ", "D": "D names differ"}
    for g in "ABCD":
        s = stats[g]
        n = s["lines"]
        out.append(f"| {names[g]} | {n} | {wilson(s['exact'], n)} | {wilson(s['exact_but_final'], n)} | "
                   f"{s['length_diff']} | {s['error']} |")
    ev = name_stats["evaluable"]
    out += ["", f"Meter names (consensus verses whose meter is in vidyut's list): {ev} verses; "
                f"vidyut names the same meter for {wilson(name_stats['same'], ev)}; "
                f"names no meter for {name_stats['none']}.", "",
            "| Meter | n | same name |", "|---|---|---|"]
    for mtr, c in sorted(name_by_meter.items(), key=lambda x: -x[1]["n"])[:15]:
        out.append(f"| {mtr} | {c['n']} | {c['same']} |")
    (ROOT / "results/vidyut_check.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
