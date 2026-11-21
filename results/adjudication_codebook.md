# Adjudication codebook: why do chanda and skrutable disagree?

Every sampled verse gets **one primary cause** in `human_cause`, chosen by working down the list and stopping at the first that applies. Notes go in `human_notes`.

The `proposed_cause` column is a first-pass suggestion. The adjudicator must check each one against the verse and the rules below, and overrule it freely.

| Code | Cause | Decide this when… | Example |
|---|---|---|---|
| `TXT` | **E-text error** | The digital text has a typo, OCR error, dropped or extra akṣara, or a broken conjunct. Correcting it to the standard reading restores the meter. | `gaur ivaitei` for `gaur iva`; `paṃṅkateḥ` |
| `ENC` | **Edition/encoding convention** | The text is faithful to its edition, but its notation changes syllable count or weight: hiatus written with doubled vowels (`ogaantas`), sandhi deliberately undone, a speaker label inside the line. | Buddhacarita `yatha āṇḍajāḥ` |
| `CHN` | **chanda error** | The text is fine and skrutable's scansion is right by the weight rules (below); chanda's syllables or weights are wrong. | cross-word `tad evam` (as-printed input) |
| `SKR` | **skrutable error** | The text is fine and chanda's scansion is right; skrutable's syllables, weights, pāda split or meter name are wrong. | |
| `PAD` | **Pāda-final convention** | The only issue is a pāda-final syllable. It is light where the meter prescribes heavy (*pādānta-guru*), or one tool carries weight-by-position across a pāda boundary and the other does not. Use this when a tool rejects or mis-scores the verse only for that reason. | skrutable rejects viyoginī with a light final; chanda names no meter for an indravajrā line ending light |
| `DB` | **Meter database gap / naming** | Both scan the same, but one tool lacks the meter, or names it differently (alias, regional name, different upajāti sub-name). | `vasantamālikā` vs `aupacchandasika` |
| `LIC` | **Genuine licence or ambiguity** | The verse really deviates (pāda-final weight, yati, a recognised vipulā or irregular pāda, archaic Vedic/epic usage), so "who is right" depends on convention. | epic anuṣṭubh with irregular pāda |
| `UNK` | **Cannot decide** | Not enough evidence. Explain in notes. | |

## Syllable-weight rules used for adjudication
1. Syllables are divided across word boundaries. A word-final consonant joins the next vowel: *tad evam* → *ta-de-vam*.
2. Two vowels meeting across a word boundary (hiatus, e.g. *kara iva*) stay **two** syllables: *ra-i-va*. They are not the diphthong *ai*.
3. **Guru** if the vowel is long (ā ī ū ṝ e ai o au), or the syllable ends in anusvāra (ṃ) or visarga (ḥ), or a short vowel is followed by a conjunct (two or more consonants, even across a word boundary), or by a consonant at the end of the pāda/line.
4. Otherwise **laghu**.
5. Pāda-final syllables may count as guru by convention (*pādānta-guru*). A difference at that position alone counts as `PAD`, not as `CHN`/`SKR`.

## Procedure
1. Read the verse and both tools' syllable lists (`line_diffs`).
2. Scan the disputed span by hand with the rules above.
3. If a text problem is suspected, compare with a printed edition or a second e-text (e.g. sanskritdocuments.org / Wikisource) and record the reading in notes.
4. Fill `human_cause` (one code) and `human_notes`.
5. A second person adjudicates the same sample independently; report Cohen's κ for the two.
