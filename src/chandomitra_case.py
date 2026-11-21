"""Case study: anuṣṭubh forms in the Chandomitra dataset vs. the Vālmīki Rāmāyaṇa.

Chandomitra (Jagadeeshan et al., EACL 2026) kept "only verses in the Anuṣṭubh
meter using Chandojñānam" (the chanda library). chanda's anuṣṭubh rule admits
only the pathyā form, so if the filter worked line by line it would remove
vipulā half-verses. We measure the half-verse forms (pathyā / vipulā /
other) in Chandomitra's released train+test sets and in the GRETIL critical
edition of the Rāmāyaṇa, with skrutable (current release) as the scanner,
and check which half-verses chanda names as anuṣṭubh.

Usage: python src/chandomitra_case.py --workers 6
Writes results/chandomitra/forms.jsonl and results/chandomitra/forms_summary.md
"""
import argparse
import collections
import json
import re
import sys
import xml.etree.ElementTree as ET
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from prosody_text import join_for_scansion  # noqa: E402

TEI = "{http://www.tei-c.org/ns/1.0}"
XMLID = "{http://www.w3.org/XML/1998/namespace}id"
_MI = None


def load_chandomitra():
    import pyarrow.parquet as pq
    from indic_transliteration import sanscript
    out = []
    for split in ("train", "test"):
        rows = pq.read_table(ROOT / f"data/raw/chandomitra/{split}.parquet").to_pylist()
        for i, r in enumerate(rows):
            halves = [h.strip() for h in re.split(r"[।॥|]+", r["Sanskrit"]) if h.strip()]
            halves = [re.sub(r"[०-९0-9]+", "", h).strip() for h in halves]
            iast = [sanscript.transliterate(h, sanscript.DEVANAGARI, sanscript.IAST) for h in halves]
            out.append({"corpus": "Chandomitra", "id": f"{split}:{i}", "halves": iast})
    return out


def load_ramayana():
    tree = ET.parse(ROOT / "data/raw/gretil/sa_rAmAyaNa.xml")
    out = []
    for lg in tree.iter(TEI + "lg"):
        lines = ["".join(l.itertext()).strip() for l in lg.findall(TEI + "l")]
        lines = [re.sub(r"[/|0-9]+", "", x).strip() for x in lines if x.strip()]
        if len(lines) == 2:
            out.append({"corpus": "Ramayana (GRETIL)", "id": lg.get(XMLID), "halves": lines})
    return out


def half_forms(label):
    m = re.match(r"anuṣṭubh \((.*)\)$", label)
    if not m:
        return None
    parts = re.split(r"; (?=\d,\d:)", m.group(1))
    forms = []
    for p in parts:
        body = p.split(":", 1)[1].strip() if ":" in p else p
        head = body.split(",")[0].strip()
        if head == "pathyā":
            forms.append("pathyā")
        elif head.endswith("-vipulā"):
            forms.append(head)
        elif head.startswith("asamīcīn"):
            forms.append("asamīcīnā")
        else:
            forms.append("other")
    return forms


def analyse(v):
    global _MI
    from chanda import analyze_line
    from skrutable import meter_identification as mi
    if _MI is None:
        _MI = mi.MeterIdentifier()
    out = dict(v)
    try:
        res = _MI.identify_meter("\n".join(v["halves"]), from_scheme="IAST",
                                 resplit_option="resplit_max")
        out["skr_label"] = res.meter_label
    except Exception as e:  # noqa: BLE001
        out["skr_label"] = f"ERROR {e}"
    out["forms"] = half_forms(out["skr_label"])
    ch = []
    for h in v["halves"]:
        try:
            r = analyze_line(join_for_scansion(h), fuzzy=False)
            names = " ".join(n for n, _ in (r.chanda or []))
            ch.append("अनुष्टुभ्" in names)
        except Exception:  # noqa: BLE001
            ch.append(None)
    out["chanda_anustubh"] = ch
    return out


def summarise(rows):
    lines = ["# Anuṣṭubh half-verse forms: Chandomitra dataset vs. Rāmāyaṇa", ""]
    for corpus in ("Chandomitra", "Ramayana (GRETIL)"):
        R = [r for r in rows if r["corpus"] == corpus]
        A = [r for r in R if r["forms"] and len(r["forms"]) == 2 and len(r["halves"]) == 2]
        forms = collections.Counter(f for r in A for f in r["forms"])
        nh = sum(forms.values())
        vip = sum(c for f, c in forms.items() if f.endswith("vipulā"))
        verses_with_vip = sum(any(f.endswith("vipulā") for f in r["forms"]) for r in A)
        ch = collections.defaultdict(lambda: [0, 0])
        for r in A:
            for f, c in zip(r["forms"], r["chanda_anustubh"]):
                key = "vipulā" if f.endswith("vipulā") else f
                ch[key][0] += bool(c)
                ch[key][1] += 1
        lines += [f"## {corpus}", "",
                  f"- verses: {len(R)}; scanned by skrutable as two-half anuṣṭubh: {len(A)}",
                  f"- half-verses: {nh}; vipulā: {vip} ({100 * vip / nh:.2f}%); "
                  f"verses with at least one vipulā half: {verses_with_vip} "
                  f"({100 * verses_with_vip / len(A):.2f}%)", "",
                  "| half-verse form | n | % |", "|---|---|---|"]
        for f, c in forms.most_common():
            lines.append(f"| {f} | {c} | {100 * c / nh:.2f} |")
        lines += ["", "| skrutable form | chanda names anuṣṭubh | n | % |", "|---|---|---|---|"]
        for k, (a, n) in sorted(ch.items(), key=lambda x: -x[1][1]):
            lines.append(f"| {k} | {a} | {n} | {100 * a / n:.1f} |")
        lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    verses = load_chandomitra() + load_ramayana()
    if args.limit:
        verses = verses[:args.limit] + verses[-args.limit:]
    outdir = ROOT / "results/chandomitra"
    outdir.mkdir(parents=True, exist_ok=True)
    with ProcessPoolExecutor(args.workers) as ex:
        rows = list(ex.map(analyse, verses, chunksize=50))
    with open(outdir / "forms.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    summary = summarise(rows)
    (outdir / "forms_summary.md").write_text(summary, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
