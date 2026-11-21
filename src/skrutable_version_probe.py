"""Run Chandomitra's released "Full anuṣṭubh" metric under a given skrutable version.

Usage: python src/skrutable_version_probe.py <skrutable_dir|installed> <split> [limit]
  skrutable_dir: a folder made with `pip install --no-deps --target DIR skrutable==X`,
                 or "installed" for the environment's own skrutable.
Prints the skrutable version, the share of reference verses scored "Full",
and the most common labels. The metric code is copied from Chandomitra's
evalutils.py (regex and the identify_meter call with its retry loop).
"""
import collections
import json
import re
import sys
from pathlib import Path

if sys.argv[1] != "installed":
    sys.path.insert(0, sys.argv[1])
import pyarrow.parquet as pq  # noqa: E402
import skrutable  # noqa: E402
from skrutable.meter_identification import MeterIdentifier  # noqa: E402

# Verbatim from Chandomitra evalutils.py
valid_label_regex = re.compile(r'^anuṣṭubh \(\d,\d\: (?!asamīcīna).+?, \d,\d\: (?!asamīcīna).+?\)$')
# Same rule with either half-verse separator (", " up to 2.1.x, "; " from 2.2.0).
fixed_label_regex = re.compile(r'^anuṣṭubh \(\d,\d\: (?!asamīcīna).+?[,;] \d,\d\: (?!asamīcīna).+?\)$')


def identify(mi, x):
    i = 0
    while i < len(x):
        try:
            return mi.identify_meter(x[i:], from_scheme='DEV', resplit_option='resplit_max')
        except Exception:  # noqa: BLE001 - same retry as the original
            i += 1
    return mi.identify_meter('')


def main():
    split = sys.argv[2]
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else None
    root = Path(__file__).resolve().parent.parent
    rows = pq.read_table(root / f"data/raw/chandomitra/{split}.parquet").to_pylist()[:limit]
    mi = MeterIdentifier()
    labels = collections.Counter()
    full = length32 = fixed = 0
    for r in rows:
        m = identify(mi, r["Sanskrit"])
        labels[m.meter_label] += 1
        fixed += bool(fixed_label_regex.match(m.meter_label))
        if valid_label_regex.match(m.meter_label):
            full += 1
        elif len(m.syllable_weights.replace("\n", "")) == 32:
            length32 += 1
    ver = getattr(skrutable, "__version__", None)
    if ver is None:
        dist = list(Path(sys.argv[1]).glob("skrutable-*.dist-info")) if sys.argv[1] != "installed" else []
        ver = dist[0].name.split("-")[1] if dist else "installed"
    out = {"skrutable": ver, "split": split, "n": len(rows),
           "full_pct": round(100 * full / len(rows), 2),
           "partial_pct": round(100 * length32 / len(rows), 2),
           "full_pct_either_separator": round(100 * fixed / len(rows), 2),
           "top_labels": labels.most_common(6)}
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
