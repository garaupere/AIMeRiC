# python
"""Gestió de la visualització de l'escansió.

Aquest mòdul exposa funcions per serialitzar i representar l'escansió d'un vers:
- `anota_vers`: metadades per paraula
- `scansion_array`: matriu de síl·labes (text, pes, fusió, fono)
- `escansio_plana`: representació plana amb punts i hashes
- `escansio_accentual`: representació amb majúscules per accents
- `metronome`: patró mètric compatible amb Metronome
"""

from typing import List, Dict, Any


__all__ = ["anota_vers", "scansion_array", "escansio_plana", "escansio_accentual", "metronome"]


def anota_vers(self) -> List[Dict[str, Any]]:
    """Anota cada paraula del vers amb el text de les síl·labes i la seva metadada.

    Retorna una llista de diccionaris on la clau és `texto_windex` i el valor és el
    resultat de `word.save_metadata()`.
    """
    words = getattr(self, "words", [])
    return [{f"{word.text.lower()}_{word.w_index}": word.save_metadata()} for word in words]


def scansion_array(self) -> List[List[tuple]]:
    """Representa l'escansió com una matriu de tuplos per paraula.

    Cada tupla és: (text_síl·laba, pes_int, fusionada, fono_info).
    """
    words = getattr(self, "words", [])
    result: List[List[tuple]] = []
    for word in words:
        stress = getattr(word, "stress", [])
        # converteix pes a int una sola vegada per síl·laba
        row = [(s.text, int(s.pes), s.fusionada, s.fono_info) for s in stress]
        result.append(row)
    return result


def escansio_plana(self) -> str:
    """Visualitza l'escansió en format pla.

    Sí·labes dins la mateixa paraula separades per punts; paraules separades per `#`.
    """
    words = getattr(self, "words", [])
    parts = []
    for word in words:
        stress = getattr(word, "stress", [])
        parts.append(".".join(s.text for s in stress))
    return "#".join(parts)


def escansio_accentual(self) -> str:
    """Visualitza l'escansió en format accentual.

    Síl·labes amb pes > 1 en majúscula, la resta en minúscula. Manca caractere `_` substituït per `‿`.
    """
    words = getattr(self, "words", [])
    parts = []
    for word in words:
        stress = getattr(word, "stress", [])
        parts.append(".".join((s.text.upper() if int(s.pes) > 1 else s.text.lower()) for s in stress))
    return "#".join(parts).replace("_", "‿")


def metronome(self) -> str:
    """Genera un patró mètric per a Metronome.

    'S' = síl·laba accentuada (pes > 1), 'w' = no accentuada.
    '.' separa paraules i '|' marca el final del vers.
    """
    words = getattr(self, "words", [])
    patro: List[str] = []
    for word in words:
        stress = getattr(word, "stress", [])
        for s in stress:
            patro.append("S" if int(s.pes) > 1 else "w")
        patro.append(".")
    # substituir l'últim separador per '|' si existeix
    if patro:
        patro[-1] = "|"
    else:
        patro.append("|")
    return "".join(patro)