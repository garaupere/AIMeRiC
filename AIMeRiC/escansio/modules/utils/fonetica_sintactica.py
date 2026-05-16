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

from AIMeRiC.escansio.modules.sillaba import Sillaba
from AIMeRiC.escansio.modules.utils.metre import recompte_metric
from AIMeRiC.escansio.modules.utils.accentuacio import get_index_accent, accent_secundari

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


def max_pes(syllable1: Sillaba, syllable2: Sillaba) -> float:
    """Retorna el 'pes' més gran (sense convertir a int innecessàriament)."""
    return syllable1.pes if float(syllable1.pes) >= float(syllable2.pes) else syllable2.pes


def puntua(syllable: Sillaba, vers: List[Sillaba]) -> int:
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


def puntua_diftong(syll1: Sillaba, syll2: Sillaba) -> int:
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


def millor_contacte_vocalic(self) -> List[Tuple[Sillaba, Sillaba, int]]:
    """Retorna candidats de contacte vocàlic amb puntuació ordenada (descendent)."""
    vers = [s for w in self.words for s in getattr(w, "stress", [])]
    candidats: List[Tuple[Sillaba, Sillaba, int]] = []

    # Iterar amb index per evitar .index dins del bucle
    n = len(vers)
    for i in range(n - 1):
        s1 = vers[i]
        s2 = vers[i + 1]
        if s1.last and s2.first and s1.ends_with_vowel and s2.starts_with_vowel:
            pts = puntua(s1, vers) + puntua(s2, vers)
            pts = pts * puntua_vallverdu(s1, s2) + puntua_diftong(s1, s2)
            if s1.fusionada or s2.fusionada:
                pts -= 4
            if pts > 0:
                s1.fusionable = pts
                candidats.append((s1, s2, pts))

    candidats.sort(key=lambda x: x[2], reverse=True)
    return candidats


def puntua_vallverdu(syllable1: Sillaba, syllable2: Sillaba) -> int:
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
    if p1 >= 3 > p2:
        if v2.get("neutra"):
            return 2
    if p1 < 3 <= p2:
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


def join_syllables(self, syllable1: Sillaba, syllable2: Sillaba) -> Optional[Sillaba]:
    """Uneix dues síl·labes en contacte vocàlic si procedeix; retorna Sillaba o None."""
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
    #syllable1.has_PRONe = True if syllable1.has_PRONe or syllable2.has_PRONe else False
    # actualitzar flag d'acabament amb vocal
    syllable1.ends_with_vowel = bool(_RE_VOWEL_CHAR.search(syllable1.text[-1]))
    reindexa_sillabes_words(self)
    return syllable1


def neutralitza_accents_secundaris(self):
    """Resol casos de xocs d'accent secundari amb accent primari (24, 42) convertint secundaris a àtones. S'aplica després de la sinèresi."""
    for word in self.words:
        stresses = getattr(word, "stress", [])
        if 2 in [int(s.pes) for s in stresses]:
            for syl in self.stress:
                if syl.pes <= 2:
                    syl.pes = 0
        word.stress = accent_secundari(
            word)  # aplica alternança rítmica després de neutralitzar secundaris (exemple: con.VIC.ci.Ó -> CON.vic.CIÓ)


def split_syllable(self, syllable: Sillaba) -> Optional[Tuple[Sillaba, Sillaba]]:
    """Separa una síl·laba fusionada (amb marcador '_' o ':') en dues síl·labes noves."""
    if not (syllable.fusionada or syllable.triftong):
        return None

    parts_text = _RE_TIE.split(syllable.text)
    if len(parts_text) < 2:
        return None

    parts_pes = _RE_TIE.split(syllable.pes_fusion) if syllable.pes_fusion else []
    # crear objectes Sillaba amb mateix index i len_word
    pes1 = parts_pes[0] if parts_pes else syllable.pes
    pes2 = parts_pes[1] if len(parts_pes) > 1 else syllable.pes
    s1 = Sillaba(index=syllable.s_index, syllable=(parts_text[0], pes1), len_word=syllable.len_word)
    s2 = Sillaba(index=syllable.s_index,
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
            return millor_contacte_vocalic(self)
        if mode == "sinalefa":
            return millor_sinalefa(self)
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
                    next_word.stress_index = get_index_accent(next_word)
                    next_word.n_syllables = len(next_word.stress)
                    del self.words[wi]
                    actualitza_s_index(self)
                    resol_xoc_accentual_fusio(
                        word)  # Resol xoc accentual creat per la fusió (exemple: SE.va.O.bra > SE.VAO.bra > se.VAO.bra)
                elif word.n_syllables == 1 and next_word.n_syllables > 1:  # El primer és monosíl·lab i el segon polisíl·lab: assignar nova síl·laba al segon, eliminar la del primer
                    next_word.stress[0] = res
                    next_word.stress_index = get_index_accent(next_word)
                    next_word.n_syllables = len(next_word.stress)
                    del self.words[wi]
                    actualitza_s_index(self)
                    resol_xoc_accentual_fusio(
                        word)  # Resol xoc accentual creat per la fusió (exemple: SE.va.O.bra > SE.VAO.bra > se.VAO.bra)
                elif word.n_syllables > 1 and next_word.n_syllables == 1:  # El primer és polisíl·lab i el segon monosíl·lab: assignar nova síl·laba al primer, eliminar la del segon
                    word.stress[-1] = res
                    word.stress_index = get_index_accent(word)
                    word.n_syllables = len(word.stress)
                    del self.words[wi + 1]
                    actualitza_s_index(self)
                    resol_xoc_accentual_fusio(
                        word)  # Resol xoc accentual creat per la fusió (exemple: SE.va.O.bra > SE.VAO.bra > se.VAO.bra)
                else:
                    # ambdues polisíl·labes
                    word.stress[-1] = res
                    word.stress[-1].ends_with_vowel = word.stress[-1].vowel_end()
                    word.n_syllables = len(word.stress)
                    del next_word.stress[0]
                    word.stress_index = get_index_accent(word)
                    next_word.stress_index = get_index_accent(next_word)
                    if next_word.stress:
                        next_word.stress[0].starts_with_vowel = next_word.stress[0].vowel_start()
                        next_word.n_syllables = len(next_word.stress)
                    if not word.stress:
                        del self.words[wi]
                    actualitza_s_index(self)
                    resol_xoc_accentual_fusio(word)  # Resol xoc accentual creat per la fusió (exemple: SE.va.O.bra > SE.VAO.bra > se.VAO.bra)

                    # ajustar iterador natural de for
                # actualitzar estats globals
                self.nomes_sillabes = [s for w in self.words for s in w.stress]
                self.recompte_sillabes_metriques = recompte_metric(self)
                diff = self.recompte_sillabes_metriques - self.objectiu
                self.actualitza_w_index()
                if diff <= 0:
                    break
        attempts += 1


def resol_xoc_accentual_fusio(mot_fusionat):
    """Resol un xoc accentual creat per la fusió de síl·labes (exemple: SE.va.O.bra > SE.VAO.bra > se.VAO.bra"""

    # Detecta si hi ha dos accents consecutius en el mot_fusionat
    accents = [s for s in mot_fusionat.stress if int(s.pes) >= 2]
    if len(accents) < 2:
        return  # No hi ha xoc accentual
    # Si hi ha xoc, neutralitza l'accent de menor pes (o el primer si són iguals SS > WS)
    accents.sort(key=lambda s: (int(s.pes), s.s_index))  # Ordena per pes i després per index
    # comprova que són consecutius
    if accents[1].s_index - accents[0].s_index == 1:
        accents[0].pes = 0  # Neutralitza l'accent de menor pes (o el primer si són iguals)
        mot_fusionat.stress_index = get_index_accent(mot_fusionat)  # Actualitza l'index d'accent del mot



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


def millor_sinalefa(self) -> List[Tuple[Sillaba, Sillaba, int]]:
    """Candidats basats en sinalefa (molt similar a best_contacte_vocalic).

    La sinalefa S'HA D'APLICAR NOMÉS entre dues paraules diferents i consecutives.
    Aquesta funció filtra qualsevol contacte que estigui dins de la mateixa paraula.
    """
    candidats = []
    vers = [s for w in self.words for s in getattr(w, "stress", [])]
    n = len(vers)
    for i in range(n - 1):
        s1 = vers[i]
        s2 = vers[i + 1]
        if s1.last and s2.first and s1.ends_with_vowel and s2.starts_with_vowel:
            # obtenim la paraula que conté cada síl·laba
            w1 = next((w for w in self.words if s1 in getattr(w, "stress", [])), None)
            w2 = next((w for w in self.words if s2 in getattr(w, "stress", [])), None)
            if w1.stress[-1] == s1 and w2.stress[0] == s2:
                # Comprovar que s1 és l'última síl·laba de w1 i s2 és la primera síl·laba de w2
                pts = puntua(s1, vers) + puntua(s2, vers)
                candidats.append((s1, s2, pts))
    candidats.sort(key=lambda x: x[2], reverse=True)
    return candidats


def actualitza_s_index(self):
    """Actualitza els indexes de síl·laba (s_index) després de qualsevol canvi que afecti l'ordre o nombre de síl·labes."""
    for word in self.words:
        for i, syllable in enumerate(word.stress):
            syllable.s_index = i


def millor_sineresi(self) -> List[Tuple[Sillaba, Sillaba, int]]:
    """Candidats per sineresi."""
    candidats = []
    for w in self.words:
        for s in w.stress:
            s1 = s
            s2 = w.stress[s.s_index + 1] if s.s_index + 1 < len(w.stress) else None
            if s2 and s1.ends_with_vowel and s2.starts_with_vowel and s2.s_index == s1.s_index + 1:
                pts = puntua(s1, w.stress) + puntua(s2, w.stress) + puntua_diftong(s1, s2)
                s1.fusionable = pts
                #print('[DEBUG] Candidat potencial per sinèresi:', s1.text, s2.text, pts)
                if s1.pes > 3:  # Si la síl·laba 1 és forta, penalitza la sinèresi (és més probable en síl·labes àtones)
                    #print('[DEBUG] Penalitzant sinèresi per síl·laba 1 forta:', s1.text, s2.text)
                    pts = 0  # Candidat poc probable per sinèresi (co.llí.em, co.pé.o, se.rí.a, ma.sí.a, etc.)

                elif s2.pes > 3 and s2.fono_info.get('alta'):  # Si la síl·laba 2 és forta i és i /u, penalitza la sinèresi (ex: be.ne.ít, a.gra.ír, pa.ú.ra, di.úr.na, etc.). Permet sinèresis tipus con.di.ció
                    #print('[DEBUG] Penalitzant sinèresi entre síl·laba forta i vocal alta:', s1.text, s2.text)
                    pts = 0  # Candidat poc probable per sinèresi (ex: be.ne.ít, a.gra.ír, pa.ú.ra, di.úr.na, etc.). Permet sinèresis tipus con.di.ció

                if len(w.stress) == 2:  # Si el mot té només dues síl·labes,
                    #print('[DEBUG] Penalitzant sinèresi en mot de dues síl·labes:', s1.text, s2.text)
                    pts -= 20  # penalització forta per sinèresi en paraules de dues síl·labes (ex: pa.ís > pais)

                if pts > 0:
                    candidats.append((s1, s2, pts))
    candidats.sort(key=lambda x: x[2], reverse=True)
    return candidats
