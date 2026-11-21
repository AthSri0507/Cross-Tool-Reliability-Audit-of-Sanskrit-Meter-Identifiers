"""Write the first-pass causes into the adjudication sheet.

These are PROPOSALS for a human adjudicator to check (codebook:
results/adjudication_codebook.md). Readings marked "standard" come from the
proposer's knowledge of the texts and must be verified against a printed
edition before they are reported.

Usage: python src/fill_proposals.py results/adjudication_sample.csv
"""
import csv
import sys

P = {
    1: ("TXT", "sthitavaterapi -> standard sthitavate 'pi; extra syllable in pada 1"),
    2: ("UNK", "pada 2 one syllable short (rucitayety avanamya); also akṣṇo for akṣṇoḥ; check edition"),
    3: ("TXT", "pada 2 two syllables short around vanāntād; word apparently truncated"),
    4: ("TXT", "dhumadhurair midhunānām -> madhubhir mithunānām; extra syllable"),
    5: ("UNK", "line 2 two syllables short (uttere ...); reading unclear; check edition"),
    6: ("ENC", "sa arthinaṃ: hiatus left unsandhied (standard so 'rthinaṃ); adds a syllable"),
    7: ("TXT", "garbled words (bhinnoraskau..., yogārdhvāveva); pada lengths broken"),
    8: ("TXT", "acaleṣa -> acala eṣa (yamaka); wrong vowel merge drops a syllable"),
    9: ("TXT", "tanutanūnapāddhūmama... -> tanūnapād dhūmavitānam; duplicated letters"),
    10: ("TXT", "smṛsayauvana... garbled; pada 3 one syllable short"),
    11: ("TXT", "rodharasaḥ -> rodhasaḥ; extra syllable"),
    12: ("TXT", "pāriṇinaṃsurāvupaiti / ṣiṅgairagadyata garbled"),
    13: ("TXT", "yadaṅgana- -> yad aṅganā-; vowel length lost"),
    14: ("TXT", "jaghanamelaghu- -> jaghanam alaghu-; garbled"),
    15: ("TXT", "paraparatulām -> parasparatulām; missing s changes a weight"),
    16: ("TXT", "abhīṣṭatāmām: long ā where the meter needs a light syllable (likely -tamām); verify"),
    17: ("UNK", "pada 1 deviates at positions 12-15 (sañcaritena); possibly a variant reading"),
    18: ("TXT", "dhavja -> dhvaja; letter transposition changes weights"),
    19: ("TXT", "grathitaḥ eṣa: visarga kept before a vowel (grathita eṣa); makes ta heavy"),
    20: ("TXT", "bhuṣaṇāyāḥ -> bhūṣaṇāyāḥ; vowel length"),
    21: ("TXT", "jvalā- -> jvālā-; tejasaḥ iva visarga kept"),
    22: ("TXT", "jarāya -> jarāyā; nṝṇāṃ -> nṛṇāṃ"),
    23: ("TXT", "muktvāśāniṃ -> muktvāśaniṃ (aśani)"),
    24: ("UNK", "pada 3 deviates at position 9 (sarasarāgapadalekhā); check edition"),
    25: ("LIC", "pada 3 has 5-7 = GGL (rare ta-vipulā) rejected by skrutable; line 1 also garbled"),
    26: ("ENC", "commentary connective 'kiṃ ca' captured as a verse line"),
    27: ("TXT", "anuvṛtena -> anuvṛttena; restores pathyā"),
    28: ("LIC", "genuine Gītā irregularity: bha-vipulā without preceding ra-gaṇa"),
    29: ("TXT", "vartaiva -> varta eva (standard Gītā keeps the hiatus); syllable lost"),
    30: ("TXT", "bhartaṃ -> bharataṃ; skrutable then mis-assigns the short pada"),
    31: ("TXT", "garbled (…nmamīlad…); skrutable misidentifies as 6-pada anuṣṭubh"),
    32: ("TXT", "praṇāna- -> prāṇān a-; vowel length"),
    33: ("TXT", "rakaṣatur -> rarakṣatur; raśāmibhiḥ -> raśmibhiḥ"),
    34: ("TXT", "pratiṣṭam -> pratiṣṭhitam; syllable lost"),
    35: ("UNK", "pada 3 (virarāja rathapṛṣṭhair) not a recognised odd-pada pattern; check edition"),
    36: ("TXT", "garbled (dhārṣṭyaastenire)"),
    37: ("PAD", "only pada-final light syllables; skrutable rejects in ardhasama meters"),
    38: ("PAD", "only pada-final light syllables; skrutable rejects in ardhasama meters"),
    39: ("PAD", "only pada-final light syllables; skrutable rejects in vizama meters"),
    40: ("PAD", "only pada-final light syllables; skrutable rejects in ardhasama meters"),
    41: ("PAD", "pada-final before next-pada conjunct: skrutable heavy by position, chanda light"),
    42: ("PAD", "pada-final before next-pada conjunct (…dhīvareṇa / strī…)"),
    43: ("PAD", "pada-final before next-pada conjunct (…hi / vyāptaṃ)"),
    44: ("PAD", "pada-final before next-pada conjunct (…jīvati / prāṇiti)"),
    45: ("PAD", "pada-final before next-pada conjunct (…śarma / prasīda)"),
    46: ("LIC", "genuine hypermetric triṣṭubh pada in Gītā 11.32 (ṛte 'pi tvā na bhaviṣyanti sarve); skrutable then mis-resplits"),
    47: ("TXT", "stray '.' inside tanay.am"),
    48: ("SKR", "re-splitting of an āryā/udgīti verse shifts a syllable across a pada boundary (low confidence)"),
    49: ("TXT", "words garbled/merged (sārasānāvalambisabhāti …)"),
    50: ("UNK", "yamaka verse; lines fit no meter as printed; check edition"),
    51: ("TXT", "line break misplaced in e-text (…cendīvara / dvandvaṃ locanatāṃ); gata for gatā"),
    52: ("TXT", "ghanatarachāyo -> ghanataracchāyo; missing c changes a weight"),
    53: ("TXT", "pūrvācaritai kṛtarṃ śubhai garbled (pūrvācaritaiḥ kṛtaṃ śubhaiḥ)"),
    54: ("PAD", "pada-final before next-pada conjunct (…ca / strīṇām)"),
    55: ("PAD", "chanda names no meter: a pada ends light in each line; chanda line matching has no pādānta-guru"),
    56: ("PAD", "chanda names no meter: pada-final light syllables"),
    57: ("PAD", "chanda names no meter: pada-final light syllables (controlled test reproduces)"),
    58: ("DB", "chanda's anuṣṭubh rule covers pathyā only; na-vipulā not recognised"),
    59: ("DB", "naming: same pattern (ssjgg/sBry) is aupacchandasika in skrutable, vasantamālikā in chanda"),
    60: ("PAD", "chanda names no meter: pada-final light syllables"),
    61: ("PAD", "chanda names no meter: pada-final light syllables; also typo abhyupāyasśca"),
    62: ("PAD", "chanda names no meter: pada-final light after resyllabification (…nālam / ālola)"),
    63: ("PAD", "chanda names no meter: pada-final light syllables"),
    64: ("DB", "naming: aupacchandasika (skrutable) vs vasantamālikā (chanda)"),
    65: ("PAD", "chanda names no meter: pada-final light syllables"),
    66: ("PAD", "chanda names no meter: pada-final light after resyllabification; note anyoanya hiatus encoding"),
}


def main(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    for r in rows:
        cause, why = P[int(r["sample_id"])]
        r["proposed_cause"], r["proposed_rationale"] = cause, why
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"filled {len(rows)} proposals")


if __name__ == "__main__":
    main(sys.argv[1])
