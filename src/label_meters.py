"""Label verses with two independent meter tools and keep only agreements.

Usage: python src/label_meters.py data/interim/verses_raw.jsonl data/interim/verses_labeled.jsonl

For each verse:
  * chanda (Terdalkar & Bhattacharya) runs line by line -> L/G string per line
    and candidate meter names per line.
  * skrutable (Neill) runs on the whole verse with pada re-splitting -> meter
    label, perfection flag, L/G per pada.
A verse is `gold` when skrutable calls it perfect, both tools produce the same
L/G sequence for the whole verse, and chanda's names include skrutable's meter
(or both call it an upajati / mixed meter).
"""
import json
import re
import sys
import unicodedata
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from chanda import analyze_line
from indic_transliteration import sanscript
from skrutable import meter_identification as mi

sys.path.insert(0, str(Path(__file__).resolve().parent))  # local modules under `python -I`
from prosody_text import join_for_scansion  # noqa: E402

_METER = None


def norm(name: str) -> str:
    """Comparable key for a meter name in any script: IAST, no diacritics, letters only."""
    if re.search(r"[ऀ-ॿ]", name):
        name = sanscript.transliterate(name, sanscript.DEVANAGARI, sanscript.IAST)
    name = unicodedata.normalize("NFKD", name.lower())
    name = "".join(c for c in name if not unicodedata.combining(c))
    return re.sub(r"[^a-z]", "", name)


def skr_base(label: str) -> str:
    return re.split(r"\s*[\[(:=]", label, maxsplit=1)[0].strip()


def meter_class(base: str, n_lines_lg) -> str:
    b = norm(base)
    if b.startswith("anustubh"):
        return "anustubh"
    if b.startswith("upajati"):
        return "upajati"
    if b in {"arya", "giti", "udgiti", "upagiti", "aryagiti", "vaitaliya", "aupacchandasika"}:
        return "matra_or_ardhasama"
    if b in {"viyogini", "puspitagra", "aparavaktra", "sundari", "malabhari"}:
        return "ardhasama"
    if b.startswith("udgata") or b in {"saurabhaka", "lalita", "padacaturuurdhva"}:
        return "vishama"
    return "samavrtta"


def label(row):
    global _METER
    if _METER is None:
        _METER = mi.MeterIdentifier()
    out = dict(row)
    # --- chanda, line by line
    ch_lg, ch_names, ch_ok = [], [], True
    for line in row["lines"]:
        # chanda treats spaces as syllable breaks. Join words for scansion
        # (tad evam -> ta-de-vam) but keep vowel-vowel hiatus apart
        # (vyatikara iva -> ra-i-va, not the diphthong rai). See prosody_text.py.
        joined = join_for_scansion(line)
        try:
            r = analyze_line(joined, fuzzy=False)
        except Exception:
            ch_ok = False
            break
        lg = "".join({"ग": "G", "ल": "L"}.get(x, "") for x in r.lg)
        ch_lg.append(lg)
        names = []
        for name, _ in (r.chanda or []):
            names += [n.strip() for n in name.split("=")]
        ch_names.append(names)
        if not r.found:
            ch_ok = False
    out["chanda_lg"] = ch_lg
    out["chanda_names"] = ch_names
    out["chanda_found"] = ch_ok
    # --- skrutable, whole verse
    try:
        v = _METER.identify_meter("\n".join(row["lines"]), from_scheme="IAST",
                                  resplit_option="resplit_max")
        out["skr_label"] = v.meter_label
        # skrutable's result for vizama meters (e.g. udgata) has no is_perfect
        # field; there its top identification score (9) means a perfect match.
        out["skr_perfect"] = bool(v.is_perfect) if hasattr(v, "is_perfect") \
            else getattr(v, "identification_score", 0) >= 9
        out["skr_lg_padas"] = v.syllable_weights.upper().split("\n")
    except Exception as e:  # noqa: BLE001 - tool failure is a data point, not a crash
        out["skr_label"], out["skr_perfect"], out["skr_lg_padas"] = f"ERROR {e}", False, []
    base = skr_base(out["skr_label"])
    out["meter"] = base
    out["meter_class"] = meter_class(base, ch_lg)
    # --- agreement
    lg_agree = "".join(ch_lg) == "".join(out["skr_lg_padas"])
    flat = {norm(n) for names in ch_names for n in names}
    if out["meter_class"] == "upajati":
        name_agree = any(n.startswith("upajati") for n in flat)
    else:
        name_agree = norm(base) in flat
    out["agree_lg"], out["agree_meter"] = lg_agree, name_agree
    # chanda often names no meter for one half-line (odd/even anustubh padas,
    # mixed upajati halves) even when its L/G string matches exactly, so the
    # name check needs a match on at least one line, not on every line.
    out["gold"] = bool(out["skr_perfect"] and lg_agree and name_agree
                       and len(ch_lg) == len(row["lines"]))
    # Phenomenon tags for error analysis.
    text = " ".join(row["lines"])
    out["has_cross_word_resyllabification"] = bool(CROSS_WORD.search(text))
    return out


# Word-final consonant (incl. anusvara-less stops/nasals/visarga-less) + space + vowel-initial word.
CROSS_WORD = re.compile(r"[kgcjṭḍtdpbnmṅñṇśṣsrlyvh] +[aāiīuūṛṝḷeoaiau]", re.I)


def main(inp, outp):
    rows = [json.loads(l) for l in open(inp, encoding="utf-8")]
    Path(outp).parent.mkdir(parents=True, exist_ok=True)
    n_gold = 0
    with open(outp, "w", encoding="utf-8") as f, ProcessPoolExecutor() as ex:
        for i, r in enumerate(ex.map(label, rows, chunksize=64), 1):
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            n_gold += r["gold"]
            if i % 1000 == 0:
                print(f"{i}/{len(rows)} labeled, {n_gold} gold", flush=True)
    print(f"done: {len(rows)} labeled, {n_gold} gold")


if __name__ == "__main__":
    main(*sys.argv[1:3])
