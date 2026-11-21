"""Export the two-tool consensus set (silver standard) as a release (JSONL + CSV + README).

Usage: python src/export_gold.py --verses data/interim/verses_labeled_v2.jsonl --out release/
"""
import argparse
import collections
import csv
import json
from pathlib import Path

GRETIL_FILES = {
    "Meghaduta": "sa_kAlidAsa-meghadUta", "Kiratarjuniya": "sa_bhAravi-kirAtArjunIya",
    "Sisupalavadha": "sa_mAgha-zizupAlavadha", "Raghuvamsa": "sa_kAlidAsa-raghuvaMza",
    "Kumarasambhava": "sa_kAlidAsa-kumArasaMbhava", "Amarusataka": "sa_amaru-amaruzataka",
    "Bhartrhari": "sa_bhatRhari-zatakatraya", "Saundaryalahari": "sa_zaMkara-saundaryalaharI",
    "Buddhacarita": "sa_azvaghoSa-buddhacarita", "Saundarananda": "sa_azvaghoSa-saundarAnanda",
    "Bhallatasataka": "sa_bhallaTa-bhallaTazataka", "Bhagavadgita": "sa_bhagavadgItA-comm",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verses", default="data/interim/verses_labeled_v2.jsonl")
    ap.add_argument("--out", default="release")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    V = [json.loads(l) for l in open(args.verses, encoding="utf-8")]
    gold = [v for v in V if v["gold"]]
    rows = []
    for v in gold:
        rows.append({
            "id": v["id"], "source_text": v["source"],
            "gretil_file": GRETIL_FILES[v["source"]] + ".xml",
            "lines_iast": v["lines"], "lg_by_line": v["chanda_lg"], "lg_by_pada": v["skr_lg_padas"],
            "meter": v["meter"], "meter_class": v["meter_class"], "skrutable_label": v["skr_label"],
        })
    with open(out / "chandas_consensus.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(out / "chandas_consensus.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "source_text", "gretil_file", "text_iast", "lg_by_line", "lg_by_pada",
                    "meter", "meter_class"])
        for r in rows:
            w.writerow([r["id"], r["source_text"], r["gretil_file"], " / ".join(r["lines_iast"]),
                        " / ".join(r["lg_by_line"]), " / ".join(r["lg_by_pada"]), r["meter"], r["meter_class"]])
    by_meter = collections.Counter(r["meter"] for r in rows)
    by_src = collections.Counter(r["source_text"] for r in rows)
    readme = [
        "# Two-tool consensus set of Sanskrit metrical verses (silver standard)", "",
        f"{len(rows)} verses from {len(by_src)} classical works (GRETIL TEI editions).",
        "Each verse is labelled with its laghu/guru (L/G) sequence and meter.",
        "A verse is included only when two independent tools agree completely. This is a "
        "consensus (silver-standard) set, not a manually verified gold standard:",
        "- chanda (Terdalkar & Bhattacharya) with a boundary-aware word join; and",
        "- skrutable (Neill), which must judge the verse a perfect fit for the meter.",
        "",
        "Agreement means the same L/G for every syllable, and the same meter name.",
        "",
        "## Fields",
        "- `id`: `<text>:<GRETIL xml:id>`",
        "- `lines_iast`: verse lines as printed in GRETIL (editorial marks removed)",
        "- `lg_by_line`: L/G per line (chanda)",
        "- `lg_by_pada`: L/G per pāda (skrutable)",
        "- `meter`, `meter_class`: anustubh / samavrtta / upajati / ardhasama / vishama",
        "",
        "## Counts by text",
        *[f"- {s}: {n}" for s, n in by_src.most_common()],
        "", "## Counts by meter (top 25)",
        *[f"- {m}: {n}" for m, n in by_meter.most_common(25)],
        "", "## Caveats",
        "- Agreement of two tools is strong evidence, not proof. A shared error would pass.",
        "- A third, independent scanner (vidyut-chandas 0.4.0) gives the same L/G on 99.95% of",
        "  the lines, ignoring the line-final syllable (see results/vidyut_check.md).",
        "- Mātrā meters are absent.",
        "- Pāda-final syllables carry their actual weight. Tradition lets them count as guru.",
        "- Some verses keep e-text errors that happen to fit the meter; the set inherits the",
        "  readings of the GRETIL files.",
        "", "## Source and license",
        "Verse texts are taken from the GRETIL TEI editions (Göttingen Register of Electronic",
        "Texts in Indian Languages, SUB Göttingen, https://gretil.sub.uni-goettingen.de), which",
        "are distributed under CC BY-NC-SA 4.0. This dataset is a derivative work and is",
        "released under the same license: Creative Commons Attribution-NonCommercial-ShareAlike",
        "4.0 International (https://creativecommons.org/licenses/by-nc-sa/4.0/).",
        "When using it, cite GRETIL and the original contributors named in each GRETIL file.",
    ]
    (out / "README.md").write_text("\n".join(readme), encoding="utf-8")
    print(f"exported {len(rows)} consensus verses -> {out}")


if __name__ == "__main__":
    main()
