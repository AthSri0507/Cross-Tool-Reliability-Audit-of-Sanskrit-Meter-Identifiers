"""Make the blind coding sheet for the second coder (Excel), without coder 1's causes.

Usage: python src/make_blind_sheet.py
Writes results/coder2_sheet.xlsx (codebook on a second tab).
"""
import csv

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

CODES = [
    ("TXT", "E-text error: typo, OCR error, dropped or extra akṣara. Correcting it to the "
            "standard reading restores the meter."),
    ("ENC", "Edition/encoding convention: text faithful to its edition, but notation changes "
            "syllable count or weight (sandhi deliberately undone, a non-verse line captured)."),
    ("CHN", "chanda error: text is fine and skrutable's scansion is right by the weight rules."),
    ("SKR", "skrutable error: text is fine and chanda's scansion is right."),
    ("PAD", "Pāda-final convention: the only issue is a pāda-final syllable (light where the "
            "meter wants heavy), or weight carried across a line boundary by one tool only."),
    ("DB", "Meter database gap or naming: both scan the same, but one tool lacks the meter or "
           "names it differently."),
    ("LIC", "Genuine licence: the verse really deviates (rare vipulā, hypermetric pāda, epic "
            "irregularity)."),
    ("UNK", "Cannot decide; explain in notes."),
]
RULES = [
    "Work down the list TXT, ENC, CHN, SKR, PAD, DB, LIC, UNK and stop at the first code that "
    "applies. Give exactly one code per verse.",
    "Weight rules: a syllable is heavy (G) if its vowel is long (ā ī ū ṝ e ai o au), if it ends in "
    "ṃ or ḥ, or if a short vowel is followed by two or more consonants (also across a word "
    "boundary). Otherwise light (L).",
    "Two vowels meeting across a word boundary (kara iva) stay two syllables: ra-i-va.",
    "A word-final consonant joins the next word's vowel: tad evam = ta-de-vam.",
    "If the only difference is at a pāda-final syllable, code PAD, not CHN or SKR.",
    "You may check readings in a printed edition or another e-text. Record what you found in "
    "notes.",
    "Do NOT open results/adjudication_verified.csv, results/adjudication_sample.csv or "
    "results/witness_check.md, and do not discuss verses with the first coder until you finish.",
]
SHOW = ["sample_id", "stratum", "verse_id", "source", "text", "skrutable_label", "chanda_meters",
        "chanda_LG_by_line", "skrutable_LG_by_pada"]
STRATUM_HELP = {
    "B": "both tools give the same L/G, but skrutable says the verse does not fit its meter",
    "C": "the two tools give different L/G sequences",
    "D": "same L/G, but the meter names differ",
}


def main():
    rows = list(csv.DictReader(open("results/adjudication_sample.csv", encoding="utf-8-sig")))
    wb = Workbook()
    ws = wb.active
    ws.title = "coding"
    head = SHOW + ["coder2_cause", "coder2_notes"]
    ws.append(head)
    for r in rows:
        ws.append([r[c] for c in SHOW] + ["", ""])
    bold = Font(bold=True)
    for c in ws[1]:
        c.font = bold
    widths = {"A": 9, "B": 12, "C": 26, "D": 15, "E": 70, "F": 34, "G": 30, "H": 30, "I": 30,
              "J": 14, "K": 50}
    for col, w in widths.items():
        ws.column_dimensions[col].width = w
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    fill = PatternFill("solid", fgColor="FFF2CC")
    for i in range(2, len(rows) + 2):
        ws[f"J{i}"].fill = fill
        ws[f"K{i}"].fill = fill
    dv = DataValidation(type="list", formula1='"' + ",".join(c for c, _ in CODES) + '"',
                        allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"J2:J{len(rows) + 1}")
    ws.freeze_panes = "E2"

    cb = wb.create_sheet("codebook")
    cb.append(["Code", "Meaning"])
    for c in cb[1]:
        c.font = bold
    for code, text in CODES:
        cb.append([code, text])
    cb.append([])
    cb.append(["Rules"])
    cb[cb.max_row][0].font = bold
    for r in RULES:
        cb.append(["", r])
    cb.append([])
    cb.append(["Stratum letters"])
    cb[cb.max_row][0].font = bold
    for k, v in STRATUM_HELP.items():
        cb.append([k, v])
    cb.column_dimensions["A"].width = 16
    cb.column_dimensions["B"].width = 110
    for row in cb.iter_rows():
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    wb.save("results/coder2_sheet.xlsx")
    print(f"wrote results/coder2_sheet.xlsx ({len(rows)} verses)")


if __name__ == "__main__":
    main()
