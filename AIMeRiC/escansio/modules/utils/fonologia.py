"""
Mòdul: fonologia.py
- Funcions  per obtenir propietats fonològiques de mots i síl·labes:
  `starts_with_vowel(self)`, `ends_with_vowel(self)`, `get_vowel(string)`.
"""
from copy import deepcopy
from typing import Any
import re

__all__ = ["starts_with_vowel", "ends_with_vowel", "get_vowel"]

# Expressions precompilades per optimitzar cerca
_RE_START = re.compile(r"^-?h?[aeiouàáèéíìóòúùïüy]", re.IGNORECASE)
_RE_START_SEMI = re.compile(r"^[iuy][aeiouàáèéíìóòúùïüy]", re.IGNORECASE)
_RE_END_VOWEL = re.compile(r"([^aeiouàáèéíìóòúùïü]*[aeiouàáèéíìóòúùïüy]|[qg]u[aeioàáèéíìóòúùïü]|^y)r?-?$",
                           re.IGNORECASE)
_RE_YR = re.compile(r"[aeiouàáèéíìóòúùïü]yr$", re.IGNORECASE)

# Regex per a normalització dins de get_vowel
_RE_REMOVE = re.compile(r"(^[h']?[iuy](?=.)|[gq]u|[^aeoiuàáèéìíòóùúyýÿïüâêîôû])", re.IGNORECASE)
_RE_SEMI_REMOVE = re.compile(r"([aeoiuàáèéìíòóùúyýÿïüâêîôû])([iuy])", re.IGNORECASE)

# Substitucions d'accentuació per normalitzar a vocables simples
_CLEAN_SUBS = [
    (re.compile(r"[aàáâ]", re.IGNORECASE), "a"),
    (re.compile(r"[eèéê]", re.IGNORECASE), "e"),
    (re.compile(r"[iíìïyýÿî]", re.IGNORECASE), "i"),
    (re.compile(r"[oòóô]", re.IGNORECASE), "o"),
    (re.compile(r"[uúùüû]", re.IGNORECASE), "u"),
]


def starts_with_vowel(self: Any) -> bool:
    """
    Retorna True si l'objecte `self` (que ha de tenir `text`) comença per vocal,
    tenint en compte `h` inicial i la regla que exclou semivocals inicials
    com `ia/iu/ya` (p. ex. `i+vocal` no compta com a vocal inicial).
    """
    txt = deepcopy(getattr(self, "text", "") or "").replace("-", "")
    if _RE_START.search(txt):
        # Si comença per semivocal seguida de vocal, excloure
        if _RE_START_SEMI.search(txt):
            return False
        return True
    return False


def ends_with_vowel(self: Any) -> bool:
    """
    Retorna True si `self.text` acaba en vocal segons regles catalanes
    aplicades en l'escansió. Utilitza atributs com `stress` i `pos_`
    quan calen per casos especials (paraules acabades en `-r`, formes com
    `per`, `llur`, etc.).
    """
    txt = deepcopy(getattr(self, "text", "") or "").replace("-", "")
    # llista de paraules exceptions que no compten com a final en -r
    exceptions = {"per", "llur"}
    if txt in exceptions:
        # si existeix la propietat stress, reflectir el canvi també
        stress = getattr(self, "stress", None)
        if stress:
            try:
                stress[0].ends_with_vowel = False
            except Exception:
                pass
        return False

    # casos amb -r final: comprovar accents en síl·labes previs
    if txt.endswith("r"):
        stress = getattr(self, "stress", [])
        # esdrúixola (més de 2 síl·labes i la -3 té pes > 1)
        if len(stress) > 2:
            try:
                if int(stress[-3].pes) > 1:
                    return False
            except Exception:
                pass
        # plana (més d'1 síl·laba i la -2 té pes > 1)
        if len(stress) > 1:
            try:
                if int(stress[-2].pes) > 1:
                    return False
            except Exception:
                pass

    # regla principal per detectar final vocàlic
    if _RE_END_VOWEL.search(txt):
        # cas especial: verb infinitiu + pronom feble, evitar fusió
        pos_tag = getattr(self, "pos_", None)
        if txt.endswith("r") and pos_tag == "ADP":
            return False
        # casos consonant + 'y' final o 'ny' final
        if len(txt) > 1 and txt.endswith("y") and txt[-2] == "n":
            return False
        # seqüència vocal + semivocal terminal: p.ex. 'ai', 'ei'... tractar com a no-vocal
        if re.search(r"([aeiouàáèéíìóòúùïüy][iuy])$", txt, re.IGNORECASE):
            # però si és 'qu' o 'gu' + vocal anterior, considerar com a vocal
            if re.search(r"[qg]u[aeiouàáèéíìóòúùïüy]$", txt, re.IGNORECASE):
                return True
            return False
        return True

    # codi addicional per patrons com '...yr'
    if _RE_YR.search(txt):
        return False

    return False


def get_vowel(string: str) -> str:
    """
    Retorna la vocal 'núcli' d'una cadena normalitzada:
    - elimina guions d'enllaç com `gq`u etc. i caràcters no vocals,
    - elimina semivocals finals adherides per reduir a nucli simple,
    - normalitza accents a `a/e/i/o/u`.
    """
    if not string:
        return ""

    s = string
    # eliminar prefixos com h' abans de semivocal, grups [gq]u i altres no-vocals
    s = _RE_REMOVE.sub("", s)

    # eliminar semivocal final adherida a nucli (p. ex. `ai` -> `a`)
    s = _RE_SEMI_REMOVE.sub(r"\1", s)

    # normalitzar accents i variants a vocals simples
    for pat, repl in _CLEAN_SUBS:
        s = pat.sub(repl, s)

    return s
