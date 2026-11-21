"""Test each proposed text correction mechanically: does it restore the meter?

For every adjudicated verse with a text-level proposal, apply the corrected
reading and re-run both tools exactly as in label_meters.py. A correction
"restores the meter" when skrutable reports a perfect fit and both tools
give the same L/G sequence (i.e. the verse would enter the gold set).

This tests metrical sufficiency only. Whether a reading is attested is a
separate question, answered by the `witness` column of
results/adjudication_verified.csv (second e-text or printed edition).

Usage: python src/verify_corrections.py > results/correction_check.tsv
"""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from label_meters import label  # noqa: E402

# sample_id -> list of (old, new) replacements on the verse text (lines joined by "\n").
FIX = {
    1: [("sthitavaterapi", "sthitavate 'pi")],
    2: [("rucitayetyavanamya", "ruciratayetyavanamya")],
    3: [("dāśarathirbhavānamuṃ", "dāśarathirbhavanbhavānamuṃ")],
    4: [("pītaśītadhumadhurairmidhunānām", "pītaśītamadhubhirmithunānām")],
    5: [("taralataraṅgalīlā", "taralataraṅgaraṅgalīlā")],
    6: [("sa arthinaṃ", "so 'rthinaṃ")],
    7: [("ekeṣeṇaiva", "ekeṣuṇaiva"), ("yogārdhvāveva", "yogādūrdhvāveva")],
    8: [("acaleṣabhavāniva", "acala eṣa bhavāniva")],
    9: [("dvaguṇī", "dviguṇī"), ("tanutanūnapāddhūmamavitānam", "tanustanūnapāddhūmavitānam")],
    10: [("smṛsayauvana", "smṛtasayauvana")],
    11: [("rodharasaḥ", "rodhasaḥ")],
    12: [("pratidvarada", "pratidvirada")],  # pada 3 left as printed: no reconstruction found
    13: [("yadaṅganarūpa", "yadaṅganārūpa")],
    14: [("jaghanamelaghapīvaroru", "jaghanamalaghupīvaroru")],
    15: [("paraparatulām", "parasparatulām")],
    16: [("abhīṣṭatāmām", "abhīṣṭatamām")],
    17: [("saṅgasañcaritena", "saṅgasaṃcāritena")],
    18: [("dhavja", "dhvaja")],
    19: [("grathitaḥ eṣa", "grathita eṣa")],
    20: [("bhuṣaṇāyāḥ", "bhūṣaṇāyāḥ")],
    21: [("jvalākaṇā", "jvālākaṇā"), ("śeṣeṇatejasaḥ ivollasatā", "śeṣeṇa tejasa ivollasatā")],
    22: [("jarāya bhayam", "jarāyā bhayam"), ("nṝṇāṃ", "nṛṇāṃ"), ("dhainya", "dainya")],
    23: [("muktvāśāniṃ", "muktvāśaniṃ")],
    24: [("sarasarāgapadalekhā", "sarasarāgapatralekhā")],
    25: [("taikṣṇād", "taikṣṇyād")],  # pada 3 (ta-vipula) is the licence; left as printed
    26: [("kiṃ ca\n", "")],
    27: [("nuvṛtena", "nuvṛttena")],
    29: [("vartaiva", "varta eva")],
    30: [("bhartaṃ", "bharataṃ")],
    31: [("ciramaviramād", "ciramāviramād"), ("vigalannamadhuvrata", "vigalanmadhuvrata"),
         ("nmamīlad", "nimamīlad")],
    32: [("praṇānaharad", "prāṇānaharad")],
    33: [("rakaṣatur", "rarakṣatur"), ("raśāmibhiḥ", "raśmibhiḥ")],
    34: [("pratiṣṭam", "pratiṣṭhitam")],
    36: [("manobhavabhavā", "manobhavabhāvād"), ("dhārṣṭyaastenire", "dhārṣṭyaṃ tenire")],
    46: [("ṛte 'pi tvā na", "ṛte 'pi tvāṃ na")],  # still hypermetric: the licence stays
    47: [("tanay.am", "tanayam")],
    48: [("brahmāpi taṃ naraṃ", "brahmāpi naraṃ")],
    49: [("sārasānāvalambisabhāti sma dāmāprapadīyamānasya", "sārasanāvalambi bhāti sma dāmāprapadīnam asya"),
          ("trisasrotasaḥ", "trisrotasaḥ"), ("saṃtatadhārāmambhaḥ", "saṃtatadhāram ambhaḥ")],
    50: [("'smannanavaratamamandarāmatā", "'sminnanavaratamamandarāgatā")],
    51: [("cendīvaradvandvaṃ\nlocanatāṃ gata na", "cendīvara\ndvandvaṃ locanatāṃ gataṃ na")],
    52: [("ghanatarachāyo", "ghanataracchāyo"), ("saṃyuktaphalito", "saṃyuktaḥ phalito"),
         ("svarair eva", "svair eva")],
    53: [("pūrvācaritai kṛtarṃ śubhai", "pūrvācaritaiḥ kṛtaṃ śubhaiḥ")],
    61: [("bhyupāyasśca", "bhyupāyaśca")],
}


def main():
    sample = {int(r["sample_id"]): r for r in
              csv.DictReader(open("results/adjudication_sample.csv", encoding="utf-8-sig"))}
    verses = {}
    for line in open("data/interim/verses_labeled_v2.jsonl", encoding="utf-8"):
        v = json.loads(line)
        verses[v["id"]] = v
    w = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    w.writerow(["sample_id", "verse_id", "all_found", "skr_label_after", "skr_perfect_after",
                "lg_agree_after", "name_agree_after", "gold_after"])
    for sid, fixes in FIX.items():
        v = verses[sample[sid]["verse_id"]]
        text = "\n".join(v["lines"])
        found = True
        for old, new in fixes:
            if old not in text:
                found = False
            text = text.replace(old, new)
        row = {"id": v["id"], "source": v["source"],
               "lines": [x for x in text.split("\n") if x.strip()]}
        out = label(row)
        w.writerow([sid, v["id"], found, out["skr_label"], out["skr_perfect"],
                    out["agree_lg"], out["agree_meter"], out["gold"]])


if __name__ == "__main__":
    main()
