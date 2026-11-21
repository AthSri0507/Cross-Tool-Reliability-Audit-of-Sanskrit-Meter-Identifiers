"""Deterministic census of all outcome-C and outcome-D verses (no sampling).

C (L/G differ, 82 verses): locate every differing syllable.
  - boundary: every difference falls on the last syllable of a line or of a
    skrutable pāda (weight carried across a pāda boundary by one tool only);
  - malformed: the verse contains characters outside the IAST letter set used
    for Sanskrit (stray '.', ';', 'ḥ' inside a word, 'xxxx');
  - other.
D (same L/G, names differ, 246 verses):
  - vipulā: anuṣṭubh in a vipulā form, and chanda names no meter for that line;
  - pāda-final: chanda names no meter for some line, and skrutable's accepted
    verse has a light syllable where its meter prescribes heavy at a pāda end;
  - naming: chanda names a meter for every line, but not skrutable's;
  - other.

Usage: python src/census_cd.py   -> results/census_cd.md, results/census_cd.jsonl
"""
import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from classify_faults import pattern_from_label  # noqa: E402

# stray punctuation, visarga inside a word, lacuna marks, anusvāra right after a consonant
MALFORMED = re.compile(r"[.;:]|ḥ(?=\w)|x{2,}|(?<=[bcdghjklmnprstvyṭḍṇśṣ])ṃ", re.I)
TRISTUBH = {"GGLGGLLGLGG", "LGLGGLLGLGG", "GGLGGLLGLGLG", "LGLGGLLGLGLG"}


def c_class(v):
    a, b = "".join(v["chanda_lg"]), "".join(v["skr_lg_padas"])
    malformed = bool(MALFORMED.search(" ".join(v["lines"])))
    if len(a) != len(b):
        return "malformed" if malformed else "other"
    d = [i for i in range(len(a)) if a[i] != b[i]]
    ends = set()
    for seq in (v["chanda_lg"], v["skr_lg_padas"]):
        p = 0
        for s in seq:
            p += len(s)
            ends.add(p - 1)
    if all(i in ends for i in d):
        return "boundary"
    return "malformed" if malformed else "other"


def d_class(v):
    empty = any(not names for names in v["chanda_names"])
    lab = v["skr_label"]
    if v["meter_class"] == "anustubh":
        if empty and "vipulā" in lab:
            return "vipulā", None
        return ("other", None) if empty else ("naming", None)
    if empty and v["meter_class"] == "upajati":
        light_final = any(p[-1] == "L" and any(p[:-1] == t[:-1] and t[-1] == "G" for t in TRISTUBH)
                          for p in v["skr_lg_padas"])
        return ("pāda-final" if light_final else "coverage"), None
    if empty and v["meter_class"] == "matra_or_ardhasama" and pattern_from_label(lab) is None:
        return "coverage", None
    if empty:
        pat = pattern_from_label(lab)
        if pat and len(pat) == len(v["skr_lg_padas"]):
            light_final = any(p[-1] == "L" and r[-1] == "G"
                              for p, r in zip(v["skr_lg_padas"], pat) if len(p) == len(r))
            if light_final:
                return "pāda-final", None
        return "other", None
    names = sorted({n for ns in v["chanda_names"] for n in ns})
    return "naming", " / ".join(names[:3])


def main():
    V = [json.loads(l) for l in open(ROOT / "data/interim/verses_labeled_v2.jsonl", encoding="utf-8")]
    C = [v for v in V if not v["agree_lg"] and not v["skr_label"].startswith("ERROR")]
    D = [v for v in V if v["agree_lg"] and v["skr_perfect"] and not v["agree_meter"]
         and not v["gold"]]
    rows = []
    cc = collections.Counter()
    for v in C:
        k = c_class(v)
        cc[k] += 1
        rows.append({"id": v["id"], "outcome": "C", "class": k})
    dc = collections.Counter()
    pairs = collections.Counter()
    for v in D:
        k, names = d_class(v)
        dc[k] += 1
        if k == "naming":
            pairs[(v["meter"], names)] += 1
        rows.append({"id": v["id"], "outcome": "D", "class": k, "meter": v["meter"],
                     "chanda": names})
    with open(ROOT / "results/census_cd.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    out = ["# Census of outcomes C and D", "", f"C: {len(C)} verses", ""]
    out += [f"- {k}: {n}" for k, n in cc.most_common()]
    out += ["", f"D: {len(D)} verses", ""] + [f"- {k}: {n}" for k, n in dc.most_common()]
    out += ["", "Most frequent naming pairs (skrutable meter -> chanda names):", ""]
    out += [f"- {m} -> {c}: {n}" for (m, c), n in pairs.most_common(12)]
    (ROOT / "results/census_cd.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
