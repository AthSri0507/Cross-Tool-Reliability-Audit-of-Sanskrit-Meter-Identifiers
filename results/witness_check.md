# Verification of the 66 adjudication proposals

Date: 2026-11-12. The verification follows the procedure below. It was coded in a single pass; **no second coder has checked it yet**, so no inter-annotator agreement exists.

Outputs:
- `results/adjudication_verified.csv`: one row per verse, giving the cause, evidence codes, confidence and the corrected reading.
- `results/adjudication_table.md`: causes by stratum.

## Checks

| Code | Check | How it was run |
|---|---|---|
| M | **Metrical restoration.** Apply the corrected reading, then re-run both tools exactly as in the audit. The check passes when skrutable reports a perfect fit. | `src/verify_corrections.py`, output in `results/correction_check.tsv` |
| W | **Independent witness.** Look the reading up in an e-text that is not derived from GRETIL. | Pages listed below |
| G | **Well-formedness.** The printed form is not Sanskrit: a non-word, or impossible sandhi such as a visarga before a vowel. | By inspection |
| C | **Controlled pattern test.** Set each pāda-final syllable to heavy; the line then matches the meter exactly. | Inline script; result recorded per row |
| P | **Propagation.** The Sanskrit Wikisource transcription has the same error. | Pages listed below |

## Witnesses consulted

**Bhagavadgītā.** holy-bhagavad-gita.org, verses 3.22, 11.32 and 12.20. This is an independent text, and it confirms:
- *varta eva ca karmaṇi* (3.22);
- *ṛte 'pi tvāṃ na bhaviṣyanti sarve* (11.32);
- *śraddadhānā matparamā* (12.20).

**Sanskrit Wikisource** (sa.wikisource.org):
- **Raghuvaṃśa**, sargas 5, 11, 12, 15, 17 and 18. The pages reproduce the GRETIL errors: रकषतुर्, रशामिभिः, धव्जतरु, भर्तं, प्रतिष्टं, भुषणायाः, परपरतुलां. They also have the same 15.10 reading.
- **Kirātārjunīya**, sargas 13 and 18. Same text as GRETIL: स अर्थिनं and तरोधरसः.
- **Bhartṛhari**, the pages नीतिशतकम् and भर्तृहरिशतकत्रयी:
  - The Vairāgyaśataka verse has the same errors as GRETIL: जराय, धैन्य, and a garbled नॄणां.
  - Śṛṅgāraśataka 46 has the same *gata*.
  - Nītiśataka 2/3: one page reads *brahmāpi taṃ naraṃ*, the other *brahmāpi naraṃ*.
- **Conclusion:** these Wikisource transcriptions are copies of the same digitisation, so they cannot serve as independent witnesses.

**Not reachable.** sanskritdocuments.org returned HTTP 403 to automated fetches. As a result, no independent witness was found for:
- the Śiśupālavadha;
- the Saundarananda;
- the Bhallaṭaśataka;
- the Buddhacarita.

## Outcome

| Measure | Result |
|---|---|
| First-pass proposals kept | 61 of 66 |
| Proposals changed | 5: four UNK→TXT, after a metrical reconstruction was found (rows 2, 5, 17, 24); one SKR→TXT (row 48). Row 48 has a hypermetric *taṃ*; without it, skrutable finds a perfect āryā and its odd mid-word re-split disappears. |
| TXT verses whose correction passes M | 36 of 37 |
| TXT conjectures (medium confidence) | 9, metrically sufficient but unattested |
| **Readings to check against a printed edition before publication** | Rows 2, 3, 5, 10, 17, 24, 31, 48, 52. Also the unresolved rows 12, 35 and 50. |
