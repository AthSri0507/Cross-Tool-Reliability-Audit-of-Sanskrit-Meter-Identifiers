"""Write the verified adjudication sheet and the cause-by-stratum table.

Inputs:
  results/adjudication_sample.csv   66 sampled verses with first-pass proposals
  results/correction_check.tsv      output of src/verify_corrections.py
Outputs:
  results/adjudication_verified.csv
  results/adjudication_table.md

Evidence codes (one or more per verse):
  M  the corrected reading makes skrutable report a perfect fit
     (src/verify_corrections.py)
  W  an independent e-text attests the reading (results/witness_check.md)
  G  the printed form is not well-formed Sanskrit (non-word, impossible sandhi)
  C  controlled pattern test: the verse deviates only at pada-final syllables
  P  the same error appears in the Sanskrit Wikisource transcription
     (a copy of the same digitisation, so not an independent witness)

Confidence: high = M or W plus G/W; medium = M only (a conjectural reading);
low = no metrical reconstruction found.

The sample was coded in a single pass; see results/witness_check.md.
"""
import collections
import csv

# sample_id: (cause, evidence, confidence, corrected reading / note)
D = {
    1: ("TXT", "MG", "high", "sthitavaterapi -> sthitavate 'pi"),
    2: ("TXT", "M", "medium", "rucitayety -> ruciratayety (conjecture); residual: pada-final light, rejected in ardhasama"),
    3: ("TXT", "M", "medium", "haplography: dāśarathir bhavān -> dāśarathir bhavan bhavān (conjecture)"),
    4: ("TXT", "MG", "high", "pītaśītadhumadhurair midhunānām -> pītaśītamadhubhir mithunānām"),
    5: ("TXT", "M", "medium", "haplography: taraṅgalīlā -> taraṅgaraṅgalīlā (conjecture)"),
    6: ("ENC", "MP", "high", "GRETIL Kirāta writes saḥ + a- as 'sa a-' (also 2.58, 4.4); so 'rthinaṃ restores the meter"),
    7: ("TXT", "MG", "high", "ekeṣeṇaiva -> ekeṣuṇaiva; yogārdhvāv -> yogād ūrdhvāv"),
    8: ("TXT", "M", "high", "acaleṣa -> acala eṣa (yamaka with saharitā lasamāna)"),
    9: ("TXT", "MG", "high", "dvaguṇī -> dviguṇī; tanutanūnapād dhūmamavitānam -> tanus tanūnapād dhūmavitānam"),
    10: ("TXT", "MG", "medium", "smṛsayauvana -> smṛtasayauvana (conjecture)"),
    11: ("TXT", "MGP", "high", "rodharasaḥ -> rodhasaḥ"),
    12: ("TXT", "G", "low", "pāda 3 'pāriṇinaṃsurāvupaiti' is not well-formed; no metrical reconstruction found; dvarada -> dvirada"),
    13: ("TXT", "M", "high", "yadaṅganarūpa -> yadaṅganārūpa; verse becomes upajāti"),
    14: ("TXT", "MG", "high", "jaghanamelagha -> jaghanam alaghu; residual: pada-final light"),
    15: ("TXT", "MP", "high", "paraparatulām -> parasparatulām"),
    16: ("TXT", "M", "high", "abhīṣṭatāmām -> abhīṣṭatamām"),
    17: ("TXT", "M", "medium", "sañcaritena -> saṃcāritena (conjecture); proposal was UNK"),
    18: ("TXT", "MGP", "high", "dhavja -> dhvaja"),
    19: ("TXT", "MG", "high", "grathitaḥ eṣa -> grathita eṣa (visarga before a vowel)"),
    20: ("TXT", "MGP", "high", "bhuṣaṇāyāḥ -> bhūṣaṇāyāḥ"),
    21: ("TXT", "MG", "high", "jvalā -> jvālā; tejasaḥ iva -> tejasa iva"),
    22: ("TXT", "MP", "high", "jarāya -> jarāyā; nṝṇāṃ -> nṛṇāṃ (optional form, unmetrical here); dhainya -> dainya"),
    23: ("TXT", "MG", "high", "muktvāśāniṃ -> muktvāśaniṃ"),
    24: ("TXT", "M", "medium", "padalekhā -> patralekhā (conjecture); proposal was UNK"),
    25: ("LIC", "", "medium", "pāda 3 has GGL at 5-7 (not a classical vipulā) in a yamaka canto; also taikṣṇād -> taikṣṇyād"),
    26: ("ENC", "M", "high", "commentary connective 'kiṃ ca' captured as a verse line (extraction artefact)"),
    27: ("TXT", "M", "high", "anuvṛtena -> anuvṛttena"),
    28: ("LIC", "W", "high", "standard text śraddadhānā matparamā: bha-vipulā without ra-gaṇa at 2-4"),
    29: ("TXT", "MW", "high", "vartaiva -> varta eva"),
    30: ("TXT", "MGP", "high", "bhartaṃ -> bharataṃ"),
    31: ("TXT", "MG", "medium", "ciramaviramād -> ciramāviramād; vigalanna madhu -> vigalan madhu; nmamīlad -> nimamīlad"),
    32: ("TXT", "M", "high", "praṇānaharad -> prāṇān aharad"),
    33: ("TXT", "MGP", "high", "rakaṣatur -> rarakṣatur; raśāmibhiḥ -> raśmibhiḥ"),
    34: ("TXT", "MGP", "high", "pratiṣṭam -> pratiṣṭhitam"),
    35: ("UNK", "P", "low", "pāda 3 virarāja rathapṛṣṭhair has LLG at 5-7; text well-formed; no reading found"),
    36: ("TXT", "MG", "high", "manobhavabhavā -> manobhavabhāvād; dhārṣṭyaastenire -> dhārṣṭyaṃ tenire"),
    37: ("PAD", "C", "high", "only pāda-final light syllables (automatic class); ardhasama"),
    38: ("PAD", "C", "high", "only pāda-final light syllables; ardhasama"),
    39: ("PAD", "C", "high", "only pāda-final light syllables; viṣama (udgatā)"),
    40: ("PAD", "C", "high", "only pāda-final light syllables; ardhasama"),
    41: ("PAD", "C", "high", "line-final syllable before a next-pāda conjunct"),
    42: ("PAD", "C", "high", "line-final syllable before a next-pāda conjunct"),
    43: ("PAD", "C", "high", "line-final syllable before a next-pāda conjunct"),
    44: ("PAD", "C", "high", "line-final syllable before a next-pāda conjunct"),
    45: ("PAD", "C", "high", "line-final syllable before a next-pāda conjunct"),
    46: ("LIC", "W", "high", "standard text hypermetric ṛte 'pi tvāṃ na bhaviṣyanti sarve; GRETIL also has tvā for tvāṃ"),
    47: ("TXT", "MG", "high", "tanay.am -> tanayam"),
    48: ("TXT", "M", "medium", "brahmāpi taṃ naraṃ -> brahmāpi naraṃ (witnesses split); with taṃ, skrutable re-splits mid-word"),
    49: ("TXT", "MG", "high", "sārasānāvalambisabhāti sma dāmāprapadīyamānasya -> sārasanāvalambi bhāti sma dāmāprapadīnam asya; trisasrotasaḥ -> trisrotasaḥ"),
    50: ("UNK", "", "low", "yamaka; rāmatā -> rāgatā (to match line 2) does not restore a meter"),
    51: ("TXT", "MP", "high", "line break after dvandvaṃ belongs after cendīvara; gata -> gataṃ"),
    52: ("TXT", "M", "medium", "ghanatarachāyo -> ghanataracchāyo; svarair -> svair; saṃyukta -> saṃyuktaḥ (conjecture)"),
    53: ("TXT", "MG", "high", "pūrvācaritai kṛtarṃ śubhai -> pūrvācaritaiḥ kṛtaṃ śubhaiḥ"),
    54: ("PAD", "C", "high", "line-final syllable before a next-pāda conjunct"),
    55: ("PAD", "C", "high", "upajāti; deviates only at pāda-final positions"),
    56: ("PAD", "C", "high", "upajāti; deviates only at pāda-final positions"),
    57: ("PAD", "C", "high", "indravajrā; deviates only at pāda-final positions"),
    58: ("DB", "", "high", "na-vipulā in both odd pādas; chanda's anuṣṭubh rule covers pathyā only"),
    59: ("DB", "", "high", "ssjgg/sBry: aupacchandasika (skrutable) = vasantamālikā (chanda)"),
    60: ("PAD", "C", "high", "upajāti; deviates only at pāda-final positions"),
    61: ("PAD", "MC", "high", "deviates only at pāda-final positions; typo abhyupāyasśca does not change weights"),
    62: ("PAD", "C", "high", "upajāti; deviates only at pāda-final positions"),
    63: ("PAD", "C", "high", "upajāti; deviates only at pāda-final positions"),
    64: ("DB", "", "high", "ssjgg/sBry naming conflict"),
    65: ("PAD", "C", "high", "upajāti; deviates only at pāda-final positions"),
    66: ("PAD", "C", "high", "upajāti (indravaṃśā + indravajrā); deviates only at pāda-final positions"),
}
ORDER = ["TXT", "ENC", "CHN", "SKR", "PAD", "DB", "LIC", "UNK"]
STRATA = ["B-length", "B-internal", "B-anustubh", "B-padanta", "C-boundary", "C-other", "D-name"]


def main():
    rows = list(csv.DictReader(open("results/adjudication_sample.csv", encoding="utf-8-sig")))
    mech = {int(r["sample_id"]): r for r in
            csv.DictReader(open("results/correction_check.tsv", encoding="utf-8"), delimiter="\t")}
    out = []
    for r in rows:
        sid = int(r["sample_id"])
        cause, ev, conf, note = D[sid]
        m = mech.get(sid)
        if "M" in ev:
            # Either a perfect fit, or (residual pada-final case) skrutable's label
            # carries no fault annotation and the rest is the PAD convention.
            assert m and (m["skr_perfect_after"] == "True" or
                          ("residual" in note and "(" not in m["skr_label_after"])), sid
        out.append({
            "sample_id": sid, "stratum": r["stratum"], "verse_id": r["verse_id"], "source": r["source"],
            "text": r["text"], "proposed_cause": r["proposed_cause"], "verified_cause": cause,
            "changed": "yes" if cause != r["proposed_cause"] else "",
            "evidence": ev, "confidence": conf, "reading_or_note": note,
            "skr_label_after_correction": m["skr_label_after"] if m else "",
            "skr_perfect_after_correction": m["skr_perfect_after"] if m else "",
        })
    with open("results/adjudication_verified.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=out[0].keys())
        w.writeheader()
        w.writerows(out)
    tab = collections.Counter((o["stratum"], o["verified_cause"]) for o in out)
    used = [c for c in ORDER if any(o["verified_cause"] == c for o in out)]
    lines = ["| Stratum | n | " + " | ".join(used) + " |", "|---|---|" + "---|" * len(used)]
    for s in STRATA:
        n = sum(1 for o in out if o["stratum"] == s)
        lines.append(f"| {s} | {n} | " + " | ".join(str(tab[(s, c)] or "") for c in used) + " |")
    tot = collections.Counter(o["verified_cause"] for o in out)
    lines.append(f"| **All** | {len(out)} | " + " | ".join(f"**{tot[c]}**" for c in used) + " |")
    agree = sum(1 for o in out if not o["changed"])
    ev = collections.Counter(ch for o in out for ch in o["evidence"])
    conf = collections.Counter(o["confidence"] for o in out)
    txt = [o for o in out if o["verified_cause"] == "TXT"]
    lines += ["", f"Proposal kept: {agree}/{len(out)}.",
              f"Evidence counts: {dict(ev)}. Confidence: {dict(conf)}.",
              f"TXT verses: {len(txt)}; with M: {sum('M' in o['evidence'] for o in txt)}; "
              f"conjectural (medium): {sum(o['confidence'] == 'medium' for o in txt)}; "
              f"error also in Wikisource (P): {sum('P' in o['evidence'] for o in txt)}."]
    open("results/adjudication_table.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    for o in out:
        if o["changed"]:
            print("changed", o["sample_id"], o["proposed_cause"], "->", o["verified_cause"])


if __name__ == "__main__":
    main()
