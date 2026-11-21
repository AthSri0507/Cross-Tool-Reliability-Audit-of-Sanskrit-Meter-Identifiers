"""Inter-coder agreement on the 66-verse adjudication sample.

Usage: python src/compute_kappa.py [results/coder2_sheet.xlsx]
Compares coder 1 (results/adjudication_verified.csv, verified_cause) with
coder 2 (coder2_cause in the Excel sheet). Prints raw agreement, Cohen's kappa
with a bootstrap 95% CI, the confusion matrix, and the disagreements to resolve.
"""
import collections
import csv
import random
import sys

from openpyxl import load_workbook

CODES = ["TXT", "ENC", "CHN", "SKR", "PAD", "DB", "LIC", "UNK"]


def kappa(pairs):
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    ca = collections.Counter(a for a, _ in pairs)
    cb = collections.Counter(b for _, b in pairs)
    pe = sum(ca[c] * cb[c] for c in set(ca) | set(cb)) / (n * n)
    return po, (po - pe) / (1 - pe) if pe < 1 else 1.0


def main(path):
    c1 = {r["sample_id"]: r["verified_cause"] for r in
          csv.DictReader(open("results/adjudication_verified.csv", encoding="utf-8-sig"))}
    ws = load_workbook(path).active
    head = [c.value for c in ws[1]]
    i_id, i_code = head.index("sample_id"), head.index("coder2_cause")
    c2 = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[i_id] is not None and row[i_code]:
            c2[str(row[i_id])] = str(row[i_code]).strip().upper()
    bad = {k: v for k, v in c2.items() if v not in CODES}
    if bad:
        sys.exit(f"invalid codes: {bad}")
    missing = sorted(set(c1) - set(c2), key=int)
    if missing:
        print(f"WARNING: {len(missing)} verses not yet coded: {missing}")
    ids = sorted(set(c1) & set(c2), key=int)
    pairs = [(c1[i], c2[i]) for i in ids]
    po, k = kappa(pairs)
    rng = random.Random(21)
    boots = sorted(kappa([rng.choice(pairs) for _ in pairs])[1] for _ in range(5000))
    lo, hi = boots[int(0.025 * len(boots))], boots[int(0.975 * len(boots))]
    print(f"n = {len(pairs)}  raw agreement = {po:.3f}  Cohen's kappa = {k:.3f} "
          f"[95% CI {lo:.3f}, {hi:.3f}]")
    used = [c for c in CODES if any(c in p for p in pairs)]
    print("\nrows = coder 1, columns = coder 2")
    print("      " + " ".join(f"{c:>4}" for c in used))
    cm = collections.Counter(pairs)
    for a in used:
        print(f"{a:>5} " + " ".join(f"{cm[(a, b)] or '.':>4}" for b in used))
    dis = [(i, c1[i], c2[i]) for i in ids if c1[i] != c2[i]]
    print(f"\n{len(dis)} disagreements to resolve:")
    for i, a, b in dis:
        print(f"  sample {i}: coder1 {a}, coder2 {b}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "results/coder2_sheet.xlsx")
