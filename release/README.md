# Two-tool consensus set of Sanskrit metrical verses (silver standard)

6115 verses from 12 classical works (GRETIL TEI editions).
Each verse is labelled with its laghu/guru (L/G) sequence and meter.
A verse is included only when two independent tools agree completely. This is a consensus (silver-standard) set, not a manually verified gold standard:
- chanda (Terdalkar & Bhattacharya) with a boundary-aware word join; and
- skrutable (Neill), which must judge the verse a perfect fit for the meter.

Agreement means the same L/G for every syllable, and the same meter name.

## Fields
- `id`: `<text>:<GRETIL xml:id>`
- `lines_iast`: verse lines as printed in GRETIL (editorial marks removed)
- `lg_by_line`: L/G per line (chanda)
- `lg_by_pada`: L/G per pāda (skrutable)
- `meter`, `meter_class`: anustubh / samavrtta / upajati / ardhasama / vishama

## Counts by text
- Raghuvamsa: 1313
- Sisupalavadha: 963
- Kiratarjuniya: 912
- Saundarananda: 906
- Kumarasambhava: 578
- Bhagavadgita: 540
- Buddhacarita: 413
- Bhartrhari: 208
- Meghaduta: 111
- Saundaryalahari: 92
- Bhallatasataka: 68
- Amarusataka: 11

## Counts by meter (top 25)
- anuṣṭubh: 1991
- upajāti triṣṭubh: 1199
- vaṃśastha: 514
- rathoddhatā: 330
- indravajrā: 236
- viyoginī: 228
- vasantatilakā: 147
- śikhariṇī: 146
- udgatā: 145
- drutavilambita: 127
- mandākrāntā: 123
- svāgatā: 115
- śārdūlavikrīḍita: 106
- pramitākṣarā: 101
- praharṣiṇī: 90
- mālinī: 84
- puṣpitāgrā: 78
- śālinī: 68
- rucirā: 63
- upendravajrā: 62
- mañjubhāṣiṇī: 59
- upajāti jagatī: 42
- sragdharā: 16
- hariṇī: 7
- pramuditavadanā: 6

## Caveats
- Agreement of two tools is strong evidence, not proof. A shared error would pass.
- A third, independent scanner (vidyut-chandas 0.4.0) gives the same L/G on 99.95% of
  the lines, ignoring the line-final syllable (see results/vidyut_check.md).
- Mātrā meters are absent.
- Pāda-final syllables carry their actual weight. Tradition lets them count as guru.
- Some verses keep e-text errors that happen to fit the meter; the set inherits the
  readings of the GRETIL files.

## Source and license
Verse texts are taken from the GRETIL TEI editions (Göttingen Register of Electronic
Texts in Indian Languages, SUB Göttingen, https://gretil.sub.uni-goettingen.de), which
are distributed under CC BY-NC-SA 4.0. This dataset is a derivative work and is
released under the same license: Creative Commons Attribution-NonCommercial-ShareAlike
4.0 International (https://creativecommons.org/licenses/by-nc-sa/4.0/).
When using it, cite GRETIL and the original contributors named in each GRETIL file.