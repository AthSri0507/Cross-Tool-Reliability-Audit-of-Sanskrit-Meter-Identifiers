"""Line-level audit of two Sanskrit meter tools (chanda vs skrutable).

Usage: python src/audit_tools.py data/interim/verses_raw.jsonl data/interim/audit_lines.jsonl

For every line of every verse it records:
  * chanda on the line as printed (spaced)    -> L/G  (original tool behaviour)
  * chanda on the line with spaces removed    -> syllables + L/G
  * skrutable scanner on the line              -> syllables + L/G
and where the two tools differ:
  * syl_agree   : identical syllable division (compared in SLP1)
  * lg_agree    : identical L/G strings (unspaced chanda vs skrutable)
  * lg_agree_spaced : identical L/G strings (spaced chanda vs skrutable)
  * diffs       : list of differing spans with the syllables each tool produced
"""
import difflib
import json
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from chanda import analyze_line
from indic_transliteration import sanscript
from skrutable import scansion

sys.path.insert(0, str(Path(__file__).resolve().parent))  # local modules under `python -I`
from prosody_text import join_for_scansion  # noqa: E402

_SCANNER = None


def chanda_scan(line: str):
    r = analyze_line(line, fuzzy=False)
    syls, lg = [], []
    for s, w in zip(r.syllables, r.lg):
        if w == "" and syls:            # stray consonant chanda keeps apart: belongs to previous syllable
            syls[-1] += s
        elif w:
            syls.append(s)
            lg.append({"ग": "G", "ल": "L"}[w])
    syls = [sanscript.transliterate(s, sanscript.DEVANAGARI, sanscript.SLP1) for s in syls]
    return syls, "".join(lg)


def skr_scan(line: str):
    global _SCANNER
    if _SCANNER is None:
        _SCANNER = scansion.Scanner()
    v = _SCANNER.scan(line, from_scheme="IAST")
    syls = v.text_syllabified.split()
    lg = v.syllable_weights.replace("\n", "").upper()
    return syls, lg


def norm_syl(s: str) -> str:
    # skrutable prints the diphthongs ai/au as two letters; SLP1 uses E/O.
    return s.replace("'", "").replace(" ", "").replace("ai", "E").replace("au", "O")


def diff_spans(a_syl, a_lg, b_syl, b_lg):
    """Differing spans between two syllabified lines (a = chanda, b = skrutable)."""
    out = []
    if [norm_syl(x) for x in a_syl] == [norm_syl(x) for x in b_syl]:
        for i, (x, y) in enumerate(zip(a_lg, b_lg)):
            if x != y:
                out.append({"kind": "weight", "pos": i, "n_syl": len(a_syl),
                            "ctx": a_syl[max(0, i - 1): i + 2], "chanda": x, "skr": y,
                            "syl": a_syl[i], "next": a_syl[i + 1] if i + 1 < len(a_syl) else None})
        return out
    sm = difflib.SequenceMatcher(a=[norm_syl(x) for x in a_syl], b=[norm_syl(x) for x in b_syl], autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            out.append({"kind": "syllabification", "op": tag, "pos": i1,
                        "chanda_syl": a_syl[i1:i2], "skr_syl": b_syl[j1:j2],
                        "chanda_lg": a_lg[i1:i2], "skr_lg": b_lg[j1:j2]})
    return out


def audit(row):
    lines = []
    for k, line in enumerate(row["lines"]):
        rec = {"verse_id": row["id"], "source": row["source"], "line_idx": k, "text": line}
        try:
            c_syl, c_lg = chanda_scan(join_for_scansion(line))            # boundary-aware join
            _, c_lg_naive = chanda_scan(re.sub(r"\s+", "", line).replace("'", ""))  # strip all spaces
            _, c_lg_spaced = chanda_scan(line)                             # as printed (tool default)
            s_syl, s_lg = skr_scan(line)
        except Exception as e:  # noqa: BLE001 - a crash is a finding, record it
            rec.update(error=str(e)[:200])
            lines.append(rec)
            continue
        rec.update(chanda_syl=c_syl, chanda_lg=c_lg, chanda_lg_naive=c_lg_naive,
                   chanda_lg_spaced=c_lg_spaced, skr_syl=s_syl, skr_lg=s_lg,
                   syl_agree=[norm_syl(x) for x in c_syl] == [norm_syl(x) for x in s_syl],
                   lg_agree=c_lg == s_lg, lg_agree_naive=c_lg_naive == s_lg,
                   lg_agree_spaced=c_lg_spaced == s_lg,
                   diffs=diff_spans(c_syl, c_lg, s_syl, s_lg))
        lines.append(rec)
    return lines


def main(inp, outp):
    rows = [json.loads(l) for l in open(inp, encoding="utf-8")]
    Path(outp).parent.mkdir(parents=True, exist_ok=True)
    n = 0
    agree = {"lg_agree": 0, "lg_agree_naive": 0, "lg_agree_spaced": 0}
    with open(outp, "w", encoding="utf-8") as f, ProcessPoolExecutor() as ex:
        for i, recs in enumerate(ex.map(audit, rows, chunksize=64), 1):
            for r in recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
                if "error" not in r:
                    n += 1
                    for k in agree:
                        agree[k] += r[k]
            if i % 2000 == 0:
                print(f"{i}/{len(rows)} verses", flush=True)
    print(f"lines: {n}")
    for k, label in (("lg_agree_spaced", "chanda as printed (spaced)"),
                     ("lg_agree_naive", "chanda, all spaces stripped"),
                     ("lg_agree", "chanda, boundary-aware join")):
        print(f"  L/G agreement with skrutable, {label:30s}: {agree[k]} ({100*agree[k]/n:.1f}%)")


if __name__ == "__main__":
    main(*sys.argv[1:3])
