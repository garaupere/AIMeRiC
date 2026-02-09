# python
# -*- coding: utf-8 -*-
"""
Mòdul: fonetica_sintactica.py

Funcionalitat:
- Resolució i puntuació de contactes vocàlics per l'escansió mètrica catalana.
- Utilities per unir/dividir síl·labes i obtenir informació estructurada
  sobre diftongs/triftongs/hiats (index de síl·laba inclòs).
Comentaris i docstrings en català.

Autor: garaupere
Versió: 0.1
"""

from copy import deepcopy
import re
from typing import List, Tuple, Optional, Dict, Any

from AIMeRiC.escansio.modules.syllable import Syllable
from AIMeRiC.escansio.modules.utils.meter import recompte_metric
from AIMeRiC.escansio.modules.utils.stress import get_stress_index

# Caràcters vocals (majúscules/minúscules es tracten on calgui)
_VOWELS = "aeiouyàáèéìíòóùúâêîôûüýÿï"
_RE_VOWEL_CHAR = re.compile(r"[AEIOUaeiou]")
_RE_TIE = re.compile(r"[_:]")
_RE_QU = re.compile(r"([qg])u([ei])", re.IGNORECASE)
_RE_CLEAN_MAP = {
    re.compile(k): v for k, v in {
        r"[aàáâ]": "a", r"[eèéê]": "e", r"[iíìïyýÿî]": "i",
        r"[oòóô]": "o", r"[uúùüû]": "u",
        r"[AÀÁÂ]": "A", r"[EÈÉÊ]": "E", r"[IÍÌÏYÝŸÎ]": "I",
        r"[OÒÓÔ]": "O", r"[UÚÙÜÛ]": "U",
        r"[Hh]": ""
    }.items()
}


def max_pes(syllable1: Syllable, syllable2: Syllable) -> float:
    """Retorna el 'pes' més gran (sense convertir a int innecessàriament)."""
    return syllable1.pes if float(syllable1.pes) >= float(syllable2.pes) else syllable2.pes


def score(syllable: Syllable, vers: List[Syllable]) -> int:
    """Calcula una puntuació heurística per a un candidat de fusió."""
    pts = 0
    f = syllable.fono_info
    pes_i = int(syllable.pes)

    if f.get("alta"):
        pts += 2 if f.get("vocal") == "i" else 1
    if not syllable.tonic and f.get("neutra"):
        pts += 3
    if syllable.triftong:
        pts -= 20
    if not syllable.tonic:
        pts += 2
    if f.get("rotica"):
        pts -= 3
    if syllable.fusionada:
        pts -= 20

    # Penalitzacions segons posició (tall potencial)
    if len(vers) > 6:
        # compare by identity using iteration index is faster at call site,
        # but here maintain existing semantics comparing object equality
        try:
            idx = vers.index(syllable)
        except ValueError:
            idx = -1
        if idx == 3 and pes_i > 2:
            pts -= 8
        elif idx == 4 and pes_i > 2:
            pts -= 4
        elif idx == 5 and pes_i > 2:
            pts -= 2

    syllable.fusionable = pts
    return pts


def score_diftong(syll1: Syllable, syll2: Syllable) -> int:
    """Puntuació addicional basada en tipus vocàlic per diftong/sineresi."""
    if syll1.fusionada or syll2.fusionada:
        return 0
    f1, f2 = syll1.fono_info, syll2.fono_info

    if f1.get("alta"):
        return 10
    if f1.get("neutra") and f2.get("neutra"):
        return 12
    if f1.get("neutra") or f2.get("alta"):
        return 1
    return 0


def best_contacte_vocalic(self) -> List[Tuple[Syllable, Syllable, int]]:
    """Retorna candidats de contacte vocàlic amb puntuació ordenada (descendent)."""
    vers = [s for w in self.words for s in getattr(w, "stress", [])]
    candidats: List[Tuple[Syllable, Syllable, int]] = []

    # Iterar amb index per evitar .index dins del bucle
    n = len(vers)
    for i in range(n - 1):
        s1 = vers[i]
        s2 = vers[i + 1]
        if s1.last and s2.first and s1.ends_with_vowel and s2.starts_with_vowel:
            pts = score(s1, vers) + score(s2, vers)
            pts = pts * vallverdu_score(s1, s2) + score_diftong(s1, s2)
            if s1.fusionada or s2.fusionada:
                pts -= 4
            if pts > 0:
                s1.fusionable = pts
                candidats.append((s1, s2, pts))

    candidats.sort(key=lambda x: x[2], reverse=True)
    return candidats


def vallverdu_score(syllable1: Syllable, syllable2: Syllable) -> int:
    """Regles basades en Vallverdú per decidir el tipus de contacte (0/1/2)."""
    if not (syllable1.ends_with_vowel and syllable2.starts_with_vowel):
        return 0

    # cas específic: infinitiu + pronom feble (ex.: 'arribaré' + '-me')
    if syllable1.fono_info.get("rotica") and syllable2.text.startswith("-"):
        return 0

    v1, v2 = syllable1.fono_info, syllable2.fono_info
    p1, p2 = int(syllable1.pes), int(syllable2.pes)

    # Tòniques / àtones combinacions
    if p1 >= 3 and p2 >= 3:
        return 0
    if p1 >= 3 and p2 < 3:
        if v2.get("neutra"):
            return 2
    if p1 < 3 and p2 >= 3:
        if p2 == 3 and v2.get("alta"):
            return 1
        if v1.get("alta") and not v2.get("alta"):
            return 1
        if v1.get("alta") and v2.get("vocal") != v1.get("vocal"):
            return 1
        if (v1.get("neutra") and (not v2.get("alta"))) or v2.get("neutra"):
            return 2
        return 0

    # p1 < 3 and p2 < 3 (ambdues àtones)
    if (v1.get("neutra") and v2.get("neutra")) or v2.get("neutra") or (v1.get("neutra") and v2.get("alta")):
        return 2
    if v1.get("alta") and v2.get("alta") and v1.get("vocal") == v2.get("vocal"):
        return 2
    if (v1.get("alta") and not v2.get("alta")) or (not v1.get("alta") and v2.get("alta")):
        return 1

    return 0


def join_syllables(self, syllable1: Syllable, syllable2: Syllable) -> Optional[Syllable]:
    """Uneix dues síl·labes en contacte vocàlic si procedeix; retorna Syllable o None."""
    if not (syllable1.ends_with_vowel and syllable2.starts_with_vowel):
        return None
    if syllable1.fusionada or syllable2.fusionada:  # Evita generar fusions de síl·labes ja fusionades (triftongs sintàctics)
        if not syllable1.fono_info.get("alta") and syllable2.fono_info.get("alta"):
            return None
    syllable1.text = f"{syllable1.text}_{syllable2.text}"
    syllable1.pes_fusion = f"{syllable1.pes}_{syllable2.pes}"
    # escollir pes major; tractar cas pes==2 => 0
    pes_sel = float(syllable1.pes) if float(syllable1.pes) >= float(syllable2.pes) else float(syllable2.pes)
    # retorna el pes de la síL·laba amb major pes
    syllable1.pes = syllable1.pes if float(syllable1.pes) >= float(syllable2.pes) else syllable2.pes
    syllable1.fusion_direction = "dreta" if float(syllable1.pes) >= float(syllable2.pes) else "esquerra"
    syllable1.fusionada = True
    syllable1.has_PRONe = True if syllable1.has_PRONe or syllable2.has_PRONe else False
    # actualitzar flag d'acabament amb vocal
    syllable1.ends_with_vowel = bool(_RE_VOWEL_CHAR.search(syllable1.text[-1]))
    reindexa_sillabes_words(self)
    return syllable1


def split_syllable(self, syllable: Syllable) -> Optional[Tuple[Syllable, Syllable]]:
    """Separa una síl·laba fusionada (amb marcador '_' o ':') en dues síl·labes noves."""
    if not (syllable.fusionada or syllable.triftong):
        return None

    parts_text = _RE_TIE.split(syllable.text)
    if len(parts_text) < 2:
        return None

    parts_pes = _RE_TIE.split(syllable.pes_fusion) if syllable.pes_fusion else []
    # crear objectes Syllable amb mateix index i len_word
    pes1 = parts_pes[0] if parts_pes else syllable.pes
    pes2 = parts_pes[1] if len(parts_pes) > 1 else syllable.pes
    s1 = Syllable(index=syllable.s_index, syllable=(parts_text[0], pes1), len_word=syllable.len_word)
    s2 = Syllable(index=syllable.s_index,
                  syllable=("".join(parts_text[1:]) if len(parts_text) > 2 else parts_text[1], pes2),
                  len_word=syllable.len_word)
    s1.fusionada = False
    s2.fusionada = syllable.triftong  # si era triftong, mantenim part de fusió en segona
    s1.triftong = False
    reindexa_sillabes_words(self)
    return s1, s2


def reindexa_sillabes_words(self):
    """Reindexa les síl·labes i actualitza els indexes de paraula."""
    for word in self.words:
        for i in range(0, len(word.stress)):
            word.stress[i].s_index = i


def resol_contactes_vocalics(self, best_mode: str):
    """Aplica successivament contactes vocàlics mentre el recompte mètric difereix de l'objectiu."""

    def get_best(mode: str):
        if mode == "natural":
            return best_contacte_vocalic(self)
        if mode == "sinalefa":
            return best_sinalefa(self)
        return []

    best = get_best(best_mode)
#    if len(best) > 4 and self.recompte_sillabes_metriques - self.objectiu > 4:
#        return  # Evita aplicar contactes si hi ha massa candidats o la diferència és gran
    if not best or self.recompte_sillabes_metriques <= self.objectiu:
        return
    diff = self.recompte_sillabes_metriques - self.objectiu
    attempts = 0
    while diff > 0 and attempts < 5:
        cand_list = get_best(best_mode)
        if not cand_list:
            break
        change = cand_list.pop(0)
        # cerca ràpida: iterar paraules i comparar objectes en stress
        for wi in range(len(self.words) - 1):
            word = self.words[wi]
            if change[0] in word.stress:
                res = join_syllables(self, change[0], change[1])
                if not res:
                    continue
                next_word = self.words[wi + 1]
                # Quatre mètodes per actualitzar llistes de síl·labes/paraules
                if word.n_syllables == 1 and next_word.n_syllables == 1:  # Dos mots monosíl·labs: unir i assignar a un dels dos, eliminar l'altre
                    next_word.stress[0] = res
                    next_word.stress_index = get_stress_index(next_word)
                    next_word.n_syllables = len(next_word.stress)
                    del self.words[wi]
                elif word.n_syllables == 1 and next_word.n_syllables > 1:  # El primer és monosíl·lab i el segon polisíl·lab: assignar nova síl·laba al segon, eliminar la del primer
                    next_word.stress[0] = res
                    next_word.stress_index = get_stress_index(next_word)
                    next_word.n_syllables = len(next_word.stress)
                    del self.words[wi]
                elif word.n_syllables > 1 and next_word.n_syllables == 1:  # El primer és polisíl·lab i el segon monosíl·lab: assignar nova síl·laba al primer, eliminar la del segon
                    word.stress[-1] = res
                    word.stress_index = get_stress_index(word)
                    word.n_syllables = len(word.stress)
                    del self.words[wi + 1]
                else:
                    # ambdues polisíl·labes
                    word.stress[-1] = res
                    word.stress[-1].ends_with_vowel = word.stress[-1].vowel_end()
                    word.n_syllables = len(word.stress)
                    del next_word.stress[0]
                    word.stress_index = get_stress_index(word)
                    next_word.stress_index = get_stress_index(next_word)
                    if next_word.stress:
                        next_word.stress[0].starts_with_vowel = next_word.stress[0].vowel_start()
                        next_word.n_syllables = len(next_word.stress)
                    if not word.stress:
                        del self.words[wi]
                        # ajustar iterador natural de for
                # actualitzar estats globals
                self.nomes_sillabes = [s for w in self.words for s in w.stress]
                self.recompte_sillabes_metriques = recompte_metric(self)
                diff = self.recompte_sillabes_metriques - self.objectiu
                self.actualitza_w_index()
                if diff <= 0:
                    break
        attempts += 1


def contactes_vocalics_info(self) -> Dict[int, Dict[str, Any]]:
    """Detecta diftongs/triftongs/hiats en el text d'escansió i retorna mapping amb s_index (1-based)."""
    clean = deepcopy(getattr(self, "escansio_text", ""))
    # normalitzar text per facilitar cerca (treure 'qu' etc.)
    clean = _RE_QU.sub(r"\1\2", clean)
    for pat, repl in _RE_CLEAN_MAP.items():
        clean = pat.sub(repl, clean)

    candidates: List[Tuple[int, int, Dict[str, Any]]] = []
    consumed: List[Tuple[int, int]] = []

    def overlaps(span: Tuple[int, int]) -> bool:
        s, e = span
        for cs, ce in consumed:
            if not (e <= cs or s >= ce):
                return True
        return False

    def mark(span: Tuple[int, int]):
        consumed.append(span)

    def make_entry(groups: Tuple[Optional[str], ...], tipo: str, sep: Optional[str]) -> Dict[str, Any]:
        vocals = "".join([g for g in groups if g]).lower()
        tonicitat = any(any(ch.isupper() for ch in (g or "")) for g in groups)
        frontera = "exterior" if sep in ("#", "‿", "_") else "interior"
        return {"tipus": tipo, "tonicitat": tonicitat, "frontera": frontera, "vocals": vocals}

    # buscar triftongs amb i sense marcador de ligadura
    for m in re.finditer(r"([AEIOUaeiou])[‿_]([AEIOUaeiou])[‿_]([AEIOUaeiou])", clean):
        span = m.span()
        if not overlaps(span):
            candidates.append((span[0], span[1], make_entry((m.group(1), m.group(2), m.group(3)), "triftong", "‿")))
            mark(span)
    for m in re.finditer(r"([AEIOUaeiou])([AEIOUaeiou])([AEIOUaeiou])", clean):
        span = m.span()
        if not overlaps(span):
            candidates.append((span[0], span[1], make_entry((m.group(1), m.group(2), m.group(3)), "triftong", None)))
            mark(span)

    # diftongs (amb i sense marcador)
    for m in re.finditer(r"([AEIOUaeiou])[‿_]([AEIOUaeiou])", clean):
        span = m.span()
        if not overlaps(span):
            candidates.append((span[0], span[1], make_entry((m.group(1), m.group(2)), "diftong", "‿")))
            mark(span)
    for m in re.finditer(r"([AEIOUaeiou])([AEIOUaeiou])", clean):
        span = m.span()
        if not overlaps(span):
            candidates.append((span[0], span[1], make_entry((m.group(1), m.group(2)), "diftong", None)))
            mark(span)

    # hiats marcats amb # o . (frontera de paraula o punt)
    for m in re.finditer(r"([AEIOUaeiou])#([AEIOUaeiou])", clean):
        span = m.span()
        if not overlaps(span):
            candidates.append((span[0], span[1], make_entry((m.group(1), m.group(2)), "hiat", "#")))
            mark(span)
    for m in re.finditer(r"([AEIOUaeiou])\.([AEIOUaeiou])", clean):
        span = m.span()
        if not overlaps(span):
            candidates.append((span[0], span[1], make_entry((m.group(1), m.group(2)), "hiat", ".")))
            mark(span)

    candidates.sort(key=lambda x: x[0])

    # Substituir cada contacte per un marcador únic per calcular index de nucli vocàlic
    temp = clean
    offset = 0
    for start, end, _ in candidates:
        temp = temp[: start + offset] + "¤" + temp[end + offset:]
        offset += 1 - (end - start)

    # eliminar no-nuclis per obtenir només nuclis vocals i marcadors
    temp_nocons = re.sub(r"[^AEIOUaeiou¤]", "", temp)

    result: Dict[int, Dict[str, Any]] = {}
    idx = 1
    for _, _, entry in candidates:
        if not entry.get("vocals"):
            continue
        try:
            marker_index = temp_nocons.index("¤")
        except ValueError:
            break
        entry["s_index"] = marker_index + 1  # 1-based
        result[idx] = entry
        idx += 1
        temp_nocons = temp_nocons.replace("¤", "", 1)

    setattr(self, "contactes_vocalics", result)
    return result


def best_sinalefa(self) -> List[Tuple[Syllable, Syllable, int]]:
    """Candidats basats en sinalefa (molt similar a best_contacte_vocalic)."""
    candidats = []
    vers = [s for w in self.words for s in getattr(w, "stress", [])]
    n = len(vers)
    for i in range(n - 1):
        s1 = vers[i]
        s2 = vers[i + 1]
        if s1.last and s2.first and s1.ends_with_vowel and s2.starts_with_vowel:
            pts = score(s1, vers) + score(s2, vers)
            candidats.append((s1, s2, pts))
    candidats.sort(key=lambda x: x[2], reverse=True)
    return candidats


def best_sineresi(self) -> List[Tuple[Syllable, Syllable, int]]:
    """Candidats per sineresi."""
    candidats = []
    for w in self.words:
        for s in w.stress:
            s1 = s
            s2 = w.stress[s.s_index + 1] if s.s_index + 1 < len(w.stress) else None
            if s2 and s1.ends_with_vowel and s2.starts_with_vowel:
                pts = score(s1, w.stress) + score(s2, w.stress) + score_diftong(s1, s2)
                s1.fusionable = pts
                candidats.append((s1, s2, pts))
    candidats.sort(key=lambda x: x[2], reverse=True)
    return candidats
