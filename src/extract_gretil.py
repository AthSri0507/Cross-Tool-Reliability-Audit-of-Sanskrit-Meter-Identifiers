"""Extract clean IAST verses from GRETIL TEI files.

Usage: python src/extract_gretil.py data/raw/gretil data/interim/verses_raw.jsonl

Each output row: {"id", "source", "lines": [str, ...], "text"}
Editorial marks (verse numbers, dandas, compound hyphens) are removed; sandhi
and word spacing are kept as printed, since both affect syllable weight.
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

TEI = "{http://www.tei-c.org/ns/1.0}"
XMLID = "{http://www.w3.org/XML/1998/namespace}id"

# File stem -> short source label used in verse ids.
SOURCES = {
    "sa_kAlidAsa-meghadUta": "Meghaduta",
    "sa_bhAravi-kirAtArjunIya": "Kiratarjuniya",
    "sa_mAgha-zizupAlavadha": "Sisupalavadha",
    "sa_kAlidAsa-raghuvaMza": "Raghuvamsa",
    "sa_kAlidAsa-kumArasaMbhava": "Kumarasambhava",
    "sa_amaru-amaruzataka": "Amarusataka",
    "sa_bhatRhari-zatakatraya": "Bhartrhari",
    "sa_zaMkara-saundaryalaharI": "Saundaryalahari",
    "sa_azvaghoSa-buddhacarita": "Buddhacarita",
    "sa_azvaghoSa-saundarAnanda": "Saundarananda",
    "sa_bhallaTa-bhallaTazataka": "Bhallatasataka",
    "sa_bhagavadgItA-comm": "Bhagavadgita",
}

MARKER = re.compile(r"(\|\||//|\|)?\s*[A-Za-z]+_[\d.,]+[a-z]?\s*(\|\||//|\|)?")  # e.g. || BhG_1.1 ||
DANDA = re.compile(r"[|/।॥]+")
DIGITS = re.compile(r"\d+")
SPACES = re.compile(r"\s+")
EDITORIAL = re.compile(r"[()\[\]{}<>?*+=_#@]|[A-Z]")  # apparatus, gaps, siglum letters
IAST_LETTER = re.compile(r"[a-zāīūṛṝḷḹṃḥṅñṭḍṇśṣ]", re.I)


def clean_line(text: str) -> str:
    text = MARKER.sub(" ", text)
    text = DANDA.sub(" ", text)
    text = DIGITS.sub(" ", text)
    text = text.replace("-", "")          # compound hyphens are editorial
    text = text.replace("’", "'").replace("‘", "'")
    return SPACES.sub(" ", text).strip()


def element_text(el) -> str:
    """Text of an element with editorial notes and variant readings removed."""
    for tag in ("note", "rdg"):
        for node in el.findall(".//" + TEI + tag):
            node.clear()
    return "".join(el.itertext())


def extract(path: Path, label: str):
    root = ET.parse(path).getroot()
    body = root.find(".//" + TEI + "body")
    for n, lg in enumerate(body.iter(TEI + "lg")):
        raw = element_text(lg)
        if label == "Bhagavadgita" and "BhG_" not in raw:
            continue  # commentary verses, not the root text
        lines = [clean_line(element_text(l)) for l in lg.findall(TEI + "l")]
        lines = [l for l in lines if len(IAST_LETTER.findall(l)) >= 4]
        if len(lines) < 2 or any(EDITORIAL.search(l) for l in lines):
            continue  # too short, or carries variant readings / lacunae
        marker = re.search(r"[A-Za-z]+_([\d.,]+[a-z]?)", raw)
        ident = lg.get(XMLID) or (marker.group(0) if marker else None)
        yield {"id": f"{label}:{ident or f'{label}_{n}'}", "source": label, "lines": lines,
               "text": " / ".join(lines), "numbered": ident is not None}


def main(src_dir: str, out_path: str):
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    counts, seen = {}, set()
    with out.open("w", encoding="utf-8") as f:
        for stem, label in SOURCES.items():
            rows = list(extract(Path(src_dir) / f"{stem}.xml", label))
            # Some files carry a second, sandhi-dissolved copy of the text whose
            # verses have no canonical id (checked: near-identical to numbered
            # verses). Where a text has numbered verses, keep only those.
            if any(r["numbered"] for r in rows):
                rows = [r for r in rows if r["numbered"]]
            for row in rows:
                row.pop("numbered")
                if row["text"] in seen:
                    continue  # duplicate verses (repeated benedictions, variants)
                seen.add(row["text"])
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                counts[label] = counts.get(label, 0) + 1
    for k, v in counts.items():
        print(f"{k:18s} {v}")
    print("TOTAL", sum(counts.values()))


if __name__ == "__main__":
    main(*sys.argv[1:3])
