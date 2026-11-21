# Second-coder task (about 1–2 hours)

You will independently code 66 verses on which two Sanskrit meter tools (chanda and skrutable) disagree. The paper reports how well your codes agree with the first coder's (Cohen's κ). The score only means something if you work **without seeing the first coder's answers**.

## Do not open
- `results/adjudication_verified.csv`
- `results/adjudication_sample.csv`
- `results/witness_check.md`
- `paper/` (the draft quotes some answers)

Don't discuss the verses with the first coder until you're done.

## Steps
1. Open `results/coder2_sheet.xlsx`.
2. Read the **codebook** tab once: 8 codes and the syllable-weight rules.
3. Fill in each row on the **coding** tab:
   - **`coder2_cause`:** pick one code from the dropdown.
   - **`coder2_notes`:** write one short reason, e.g. "typo dhavja→dhvaja" or "only the last syllable of pāda 2 is light".
4. Columns to read:
   - `text`: the verse.
   - `skrutable_label`: the meter skrutable found, plus its complaint in brackets (e.g. *pāda 3 ūnākṣarā* = pāda 3 is a syllable short).
   - `chanda_meters`: what chanda found.
   - The two `LG` columns: each tool's light (L) / heavy (G) pattern.
5. To decide whether a word is a typo, look the verse up in a printed edition or another e-text (e.g. sanskritdocuments.org, Wikisource), and note the source you used.
6. Save the file and send it back. Agreement is then computed with:

   ```
   .venv/Scripts/python -I -X utf8 src/compute_kappa.py results/coder2_sheet.xlsx
   ```

## Quick guide
| If… | Code |
|---|---|
| A word is misspelt or garbled, and fixing it would make the meter work | TXT |
| The text follows an odd edition habit (sandhi undone on purpose, a non-verse line included) | ENC |
| Only a pāda-final syllable is the problem | PAD |
| Both tools see the same syllables, but one tool doesn't know the meter or calls it a different name | DB |
| The verse itself really breaks the rule (known licence) | LIC |
| chanda (CHN) or skrutable (SKR) mis-scans text that is correct | CHN / SKR |
| You can't tell | UNK (say why in notes) |

Work down the list TXT → ENC → CHN → SKR → PAD → DB → LIC → UNK and stop at the first code that fits.
