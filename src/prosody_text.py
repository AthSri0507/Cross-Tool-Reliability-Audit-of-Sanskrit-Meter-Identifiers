"""Prepare spaced IAST text for a scansion tool that treats spaces as syllable breaks.

Sanskrit prosody ignores word boundaries, with one exception that the spacing
in e-texts encodes:
  * consonant-final word + next word  -> join  (tad evam -> ta-de-vam; the
    final consonant takes the next vowel, or closes a cluster)
  * vowel-final word + vowel-initial word (hiatus left after sandhi, e.g.
    vyatikara iva)                    -> keep apart (ra-i-va, NOT the diphthong rai)
  * vowel-final word + consonant-initial word -> join (sa prāha: the cluster
    pr makes sa heavy)
The avagraha (') marks an elided a and carries no syllable, so it is dropped.
"""
import re

VOWEL = "aāiīuūṛṝḷḹeo"
_SPACE = re.compile(r"\s+")


def join_for_scansion(line: str) -> str:
    line = line.replace("'", "")
    parts = _SPACE.split(line.strip())
    out = parts[0] if parts else ""
    for word in parts[1:]:
        if not word:
            continue
        if out and out[-1].lower() in VOWEL and word[0].lower() in VOWEL:
            out += " " + word      # hiatus: keep the vowels in separate syllables
        else:
            out += word
    return out
