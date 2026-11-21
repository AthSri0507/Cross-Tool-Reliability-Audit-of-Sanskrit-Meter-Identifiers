# Cross-Tool Reliability Audit of Sanskrit Meter Identifiers

A systematic audit of two open-source Sanskrit meter identifiers, **chanda** and **skrutable**, on 7,714 verses from twelve classical works, with an independent third scanner (**vidyut-chandas**) as a cross-check.

The repository releases three things:
- **A 6,115-verse consensus dataset** of Sanskrit verse labelled with syllable weights and meter.
- **The full audit pipeline.**
- **Every intermediate result** behind the reported numbers.

[![Dataset license: CC BY-NC-SA 4.0](https://img.shields.io/badge/dataset-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)

---

## Contents

- [Why this project](#why-this-project)
- [Key findings](#key-findings)
- [The dataset](#the-dataset)
- [Repository layout](#repository-layout)
- [Results files](#results-files)
- [Reproducing the study](#reproducing-the-study)
- [Method in brief](#method-in-brief)
- [Limitations](#limitations)
- [Citation](#citation)
- [License](#license)
- [Acknowledgements](#acknowledgements)
- [Authors](#authors)

---

## Why this project

Sanskrit verse is built from fixed patterns of light (*laghu*, L) and heavy (*guru*, G) syllables. Because syllable weight follows deterministic rules, meter identification is usually handled by rule-based software.

These tools are increasingly used as ground truth: to filter training corpora, to score generated poetry, and to detect errors in digitised texts. Yet their published evaluations cover only around a thousand verses.

This project asks four questions:
1. How often do two independent identifiers agree?
2. Why do they disagree when they do?
3. What does it take to turn their output into reliable labels?
4. Do their differences affect published downstream work?

## Key findings

| Finding | Evidence |
|---|---|
| Input handling dominates line-level disagreement. | On e-text as printed, the tools agree on only **74.3%** of lines. A boundary-aware word join that resyllabifies consonant-final words and keeps vowel hiatus apart raises agreement to **99.95%**. The 8 remaining lines all contain malformed characters. |
| Verse-level agreement is high once input is fixed. | The two tools agree completely on **79.3%** of verses (6,115 of 7,714). |
| No scansion error on well-formed text. | A census of all 82 verses whose scansions differ finds that every difference lies at a pāda or line boundary (75 verses) or involves malformed characters (7). |
| A third scanner confirms the consensus. | vidyut-chandas gives the same L/G sequence on **99.95%** of consensus lines, setting aside the line-final syllable. For the 2,644 consensus verses whose meter it knows, it gives the same meter name 94.25% of the time. |
| The tools follow different prosodic conventions. | skrutable accepts a light pāda-final syllable in 831 samavṛtta verses, but in none of 217 ardhasama or viṣama verses. chanda names no meter when a pāda ends light. chanda does not cover the anuṣṭubh *vipulā* forms. |
| Flagged faults are mostly e-text errors. | In a stratified sample, 23 of 24 verses with a length or internal deviation contain a text error. Each correction was tested by re-scanning. |
| Corpus issues. | 906 sandhi-dissolved duplicate verses in four GRETIL files. The sampled GRETIL errors also reappear in Sanskrit Wikisource. |
| Downstream effects on a published benchmark (Chandomitra, EACL 2026). | Its chanda-filtered dataset contains *vipulā* forms in **0.05%** of verses, against **20.1%** in the Rāmāyaṇa. Its released metric scores every human reference verse as non-metrical under skrutable ≥ 2.2.0, because of a change in the label format. |

![Line-level agreement between chanda and skrutable per text, under three input modes](figures/fig_line_agreement.png)

## The dataset

`release/` contains the **two-tool consensus set**:
- 6,115 verses;
- 42 meters;
- 12 works.

A verse is included only when both of these hold:
- skrutable judges it a perfect fit for its meter;
- both tools give the identical L/G sequence and agree on the meter name.

> **Silver standard.** Membership rests on agreement between independent tools, not on manual verification. An error shared by both tools would pass the filter; the third-scanner check reduces, but does not remove, that risk.

| File | Format |
|---|---|
| `release/chandas_consensus.jsonl` | One JSON object per verse |
| `release/chandas_consensus.csv` | Flat table (lines joined with ` / `) |
| `release/README.md` | Data card: counts by text and meter, caveats, license |

**Fields**

| Field | Description |
|---|---|
| `id` | `<Text>:<GRETIL xml:id>`, e.g. `Meghaduta:KMgD_1` |
| `source_text` | Work |
| `gretil_file` | Source TEI file |
| `lines_iast` | Verse lines in IAST, as printed in GRETIL (editorial marks removed) |
| `lg_by_line` | L/G sequence per line |
| `lg_by_pada` | L/G sequence per pāda |
| `meter` | Meter name (IAST) |
| `meter_class` | `anustubh`, `samavrtta`, `upajati`, `ardhasama` or `vishama` |
| `skrutable_label` | Full skrutable label, including the gaṇa formula (JSONL only) |

**Example record**

```json
{
  "id": "Meghaduta:KMgD_1",
  "source_text": "Meghaduta",
  "lines_iast": ["kaś cit kāntāvirahaguruṇā svādhikārapramattaḥ śāpenāstaṅgamitamahimā varṣabhogyeṇa bhartuḥ", "..."],
  "lg_by_pada": ["GGGGLLLLLGGLGGLGG", "GGGGLLLLLGGLGGLGG", "GGGGLLLLLGGLGGLGG", "GGGGLLLLLGGLGGLGL"],
  "meter": "mandākrāntā",
  "meter_class": "samavrtta"
}
```

**Composition.** By meter class:

| Meter class | Verses |
|---|---|
| anuṣṭubh | 1,991 |
| upajāti | 1,246 |
| other samavṛtta | 2,422 |
| ardhasama | 309 |
| viṣama | 147 |

By work:

| Work | Verses |
|---|---|
| Raghuvaṃśa | 1,313 |
| Śiśupālavadha | 963 |
| Kirātārjunīya | 912 |
| Saundarananda | 906 |
| Kumārasambhava | 578 |
| Bhagavadgītā | 540 |
| Buddhacarita | 413 |
| Bhartṛhari | 208 |
| Meghadūta | 111 |
| Saundaryalaharī | 92 |
| Bhallaṭaśataka | 68 |
| Amaruśataka | 11 |

## Repository layout

```
.
├── release/            Consensus dataset (JSONL, CSV) and its data card
├── results/            Every report, table and per-verse classification behind the findings
│   └── chandomitra/    Downstream case study (Chandomitra benchmark)
├── figures/            Figures (PNG and PDF)
├── src/                Pipeline scripts
├── requirements.txt    Pinned dependencies
└── README.md
```

Not tracked (see `.gitignore`):
- `data/raw/`: third-party sources, downloaded by the setup steps below.
- `data/interim/`: regenerated by the pipeline.

### Scripts (`src/`)

| Script | Purpose |
|---|---|
| `extract_gretil.py` | Extracts clean IAST verses from the GRETIL TEI files and drops sandhi-dissolved duplicate copies |
| `prosody_text.py` | **Boundary-aware word join**: resyllabifies consonant-final words and keeps vowel hiatus apart |
| `label_meters.py` | Runs chanda (per line) and skrutable (per verse), and marks consensus membership |
| `audit_tools.py` | Line-level comparison under three chanda input modes (as printed, spaces stripped, boundary-aware) |
| `audit_report.py` | Corpus, line- and verse-level tables with Wilson 95% intervals (`results/audit_report.md`) |
| `classify_faults.py` | Classifies skrutable-flagged verses: length, internal or pāda-final deviation, anuṣṭubh fault tags |
| `census_cd.py` | Deterministic census of **every** verse with differing scansions (C) or differing names (D) |
| `vidyut_check.py` | Third-scanner check with vidyut-chandas on all 16,205 lines |
| `make_adjudication_sample.py` | Draws the stratified 66-verse adjudication sample (seed 21) |
| `fill_proposals.py` | Writes first-pass causes into the sample sheet |
| `verify_corrections.py` | Applies each proposed text correction and re-runs both tools (metrical-restoration test) |
| `finalize_adjudication.py` | Produces the verified sheet and the cause-by-stratum table |
| `make_blind_sheet.py` | Creates the blind Excel sheet for an independent second coder |
| `compute_kappa.py` | Cohen's κ with bootstrap CI and confusion matrix, once the second coder has finished |
| `chandomitra_case.py` | Case study: anuṣṭubh half-verse forms in the Chandomitra dataset vs. the Rāmāyaṇa |
| `skrutable_version_probe.py` | Runs Chandomitra's released metric under any skrutable version |
| `export_gold.py` | Exports the consensus set to `release/` |
| `make_figures.py` | Renders the figures in `figures/` |

## Results files

| File | Contents |
|---|---|
| `results/audit_report.md` | Corpus table, line-level agreement by input mode and text, verse-level outcomes |
| `results/fault_classes.jsonl` | Fault class for each of the 1,271 skrutable-flagged verses |
| `results/census_cd.md`, `census_cd.jsonl` | Census of all outcome-C (82) and outcome-D (246) verses |
| `results/vidyut_check.md` | Third-scanner agreement by outcome group, meter-name agreement |
| `results/adjudication_codebook.md` | Codes (TXT, ENC, CHN, SKR, PAD, DB, LIC, UNK) and weight rules |
| `results/adjudication_sample.csv` | The 66 sampled verses with tool outputs and first-pass causes |
| `results/adjudication_verified.csv` | Final cause, evidence codes, confidence and corrected reading per verse |
| `results/adjudication_table.md` | Causes by stratum |
| `results/correction_check.tsv` | Tool output after each proposed correction |
| `results/witness_check.md` | Readings checked against independent e-texts, and errors propagated to Wikisource |
| `results/coder2_sheet.xlsx`, `CODER2_INSTRUCTIONS.md` | Blind second-coder sheet and instructions |
| `results/chandomitra/forms_summary.md` | Half-verse form distribution: Chandomitra dataset vs. Rāmāyaṇa |
| `results/chandomitra/metric_by_version.jsonl` | Chandomitra's metric on reference verses under skrutable 2.0.7 and 2.10.0 |
| `results/chandomitra/metric_current_fixed.jsonl` | The same metric with the separator patched |

## Reproducing the study

### 1. Environment

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

All reported numbers were produced with Python 3.10 and the pinned versions:
- chanda 1.1.0;
- skrutable 2.10.0;
- vidyut 0.4.0.

On Windows, run scripts with `python -X utf8 ...` so that IAST prints correctly in the console.

### 2. Source data

```bash
# GRETIL TEI editions (CC BY-NC-SA 4.0)
mkdir -p data/raw/gretil
for f in sa_kAlidAsa-meghadUta sa_bhAravi-kirAtArjunIya sa_mAgha-zizupAlavadha \
         sa_kAlidAsa-raghuvaMza sa_kAlidAsa-kumArasaMbhava sa_amaru-amaruzataka \
         sa_bhatRhari-zatakatraya sa_zaMkara-saundaryalaharI sa_azvaghoSa-buddhacarita \
         sa_azvaghoSa-saundarAnanda sa_bhallaTa-bhallaTazataka sa_bhagavadgItA-comm \
         sa_rAmAyaNa; do
  curl -L -o "data/raw/gretil/$f.xml" "https://gretil.sub.uni-goettingen.de/gretil/corpustei/$f.xml"
done

# Meter data for vidyut-chandas
python -c "import vidyut; vidyut.download_data('data/raw/vidyut')"

# Chandomitra dataset (case study only)
mkdir -p data/raw/chandomitra
for s in train test; do
  curl -L -o "data/raw/chandomitra/$s.parquet" \
    "https://huggingface.co/datasets/sanganaka/anushtup/resolve/main/data/$s-00000-of-00001.parquet"
done

# Older skrutable release for the version study (case study only)
pip install --no-deps --target data/raw/skrutable/2.0.7 skrutable==2.0.7
```

The Rāmāyaṇa file is used only by the case study; the corpus extractor reads the twelve named works.

### 3. Audit pipeline

```bash
python src/extract_gretil.py data/raw/gretil data/interim/verses_raw_v2.jsonl
python src/label_meters.py   data/interim/verses_raw_v2.jsonl data/interim/verses_labeled_v2.jsonl
python src/audit_tools.py    data/interim/verses_raw_v2.jsonl data/interim/audit_lines.jsonl
python src/audit_report.py                       # -> results/audit_report.md
python src/classify_faults.py data/interim/verses_labeled_v2.jsonl results/fault_classes.jsonl
python src/census_cd.py                          # -> results/census_cd.md
python src/vidyut_check.py                       # -> results/vidyut_check.md
python src/export_gold.py                        # -> release/
python src/make_figures.py --out figures
```

### 4. Adjudication

```bash
python src/make_adjudication_sample.py           # 66-verse stratified sample (seed 21)
python src/fill_proposals.py results/adjudication_sample.csv
python src/verify_corrections.py > results/correction_check.tsv
python src/finalize_adjudication.py              # -> results/adjudication_verified.csv
python src/make_blind_sheet.py                   # -> results/coder2_sheet.xlsx
python src/compute_kappa.py results/coder2_sheet.xlsx   # after the second coder has finished
```

`make_adjudication_sample.py` rewrites the sample sheet. Run `fill_proposals.py` again afterwards.

### 5. Downstream case study

```bash
python src/chandomitra_case.py --workers 6       # -> results/chandomitra/forms_summary.md
python src/skrutable_version_probe.py data/raw/skrutable/2.0.7 test
python src/skrutable_version_probe.py installed test
```

## Method in brief

1. **Line level.** Each line is scanned by both tools. chanda treats a space as a syllable boundary, so it is run on three versions of the input:
   - **(a)** the text as printed;
   - **(b)** the text with all spaces removed;
   - **(c)** the boundary-aware join. Words are concatenated, except where a vowel-final word meets a vowel-initial word, where the space is kept. This encodes two rules:
     - *tad evam* → *ta-de-vam*;
     - *vyatikara iva* → *ra-i-va*, not the diphthong *rai*.
2. **Verse level.** skrutable identifies the meter of the whole verse and reports whether it fits perfectly; chanda proposes meters per line. Each verse falls into one outcome:
   - **A.** Full agreement: the consensus set.
   - **B.** Same L/G, but skrutable flags a fault.
   - **C.** The L/G sequences differ.
   - **D.** The meter names differ.
3. **Census.** All C and D verses are classified by deterministic rules: boundary-only difference, malformed characters, vipulā, pāda-final, coverage, or naming.
4. **Third scanner.** vidyut-chandas, an independent implementation, re-scans every line.
5. **Adjudication.** A stratified sample of 66 non-consensus verses is coded with the codebook. Each proposed text correction is applied and re-scanned. Readings are checked against independent e-texts where one is reachable.
6. **Case study.** The same tools are examined inside the released Chandomitra dataset and evaluation code.

## Limitations

- **Tool coverage.** Two primary tools are compared, and mātrā meters are almost absent from the consensus set.
- **Single coder for outcome B.** The cause shares for outcome B come from a stratified sample coded in a single pass; inter-annotator agreement is pending.
- **Unattested corrections.** Nine corrections are metrically sufficient but not confirmed against a printed edition.
- **Corpus-specific rates.** Edition conventions differ across GRETIL files, so absolute rates hold for this corpus only. The failure modes and the convention findings do not depend on the corpus.
- **Case study scope.** The Chandomitra dataset and the GRETIL Rāmāyaṇa follow different editions. The model outputs are not public, so the metric was tested on reference verses only.

## Citation

If you use the dataset or code, please cite:

```bibtex
@misc{srivastava2026meteraudit,
  title  = {A Cross-Tool Reliability Audit of Sanskrit Meter Identifiers:
            Input Handling, Prosodic Conventions, and Downstream Reproducibility},
  author = {Srivastava, Atharva and K, Aditya and Potharaju, Abhinav and S K, Nischitha},
  year   = {2026},
  note   = {Dataset and code. RV College of Engineering, Bengaluru}
}
```

Please also cite GRETIL and the tools:
- chanda / Chandojñānam (Terdalkar & Bhattacharya, 2023);
- skrutable (Neill);
- vidyut (Ambuda).

## License

- **Dataset** (`release/`): [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). The verse texts derive from GRETIL e-texts distributed under the same license, so the dataset inherits it: attribution, non-commercial use, and share-alike.
- **Code** (`src/`): see `LICENSE`.

## Acknowledgements

- **Source texts:** the GRETIL project (SUB Göttingen) and its contributors, for the TEI editions of the source texts.
- **Tools:**
  - Hrishikesh Terdalkar and Arnab Bhattacharya, for *chanda*;
  - Tyler Neill, for *skrutable*;
  - the Ambuda project, for *vidyut*.
- **Chandomitra:** the Chandomitra authors, for releasing their dataset and evaluation code.

## Authors

| Name | Affiliation | Contact |
|---|---|---|
| Atharva Srivastava | Department of AIML, RV College of Engineering, Bengaluru | atharvas.ai23@rvce.edu.in |
| Aditya K | Department of AIML, RV College of Engineering, Bengaluru | adityak.ai23@rvce.edu.in |
| Abhinav Potharaju | Department of AIML, RV College of Engineering, Bengaluru | abhinavsrinivas.ai23@rvce.edu.in |
| Nischitha S K | Department of CSE, RV College of Engineering, Bengaluru | nischithask@rvce.edu.in |
