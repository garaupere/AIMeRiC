"""Un mòdul per gestionar funcions prosòdiques del vers"""
from .metre import recompte_metric

from dataclasses import dataclass
from typing import Optional, List, Tuple, Callable, Any, Generator, Dict
from enum import Enum


# Constants configurables
class PesAccent:
    """Constants per als diferents nivells d'accent."""
    ATONA = 0.0
    SECUNDARI_DESACCENTUADA = 0.75
    DESACCENTUADA = 1.0
    SECUNDARI = 2.0
    SECUNDARI_FORT = 2.5
    BIVALENT = 3.0
    LEXIC = 4.0
    CIM_MAXIM = 5.0

    # Rangs per a comparacions
    LLINDAR_SECUNDARI = 2.5
    LLINDAR_BIVALENT = 3.0
    LLINDAR_LEXIC = 4.0


TALLS_FREQUENTS = [4, 6, 5]  # decasíl·lab català

# Prioritats dels talls (més alt = més prioritari)
# Ordre de preferència: 4 > 6 > 5
PRIORITAT_TALLS = {
    4: 3,  # Posició 4 (tall a la 3a síl·laba) - prioritat més alta
    6: 2,  # Posició 6 (tall a la 5a síl·laba) - prioritat mitjana
    5: 1,  # Posició 5 (tall a la 4a síl·laba) - prioritat més baixa
}


def prioritat_tall(posicio: int) -> int:
    """
    Retorna la prioritat d'una posició de tall.
    Més alt = més prioritari. 0 = no és tall.
    """
    return PRIORITAT_TALLS.get(posicio, 0)


@dataclass
class ContextSillaba:
    """Encapsula el context d'una síl·laba amb les adjacents."""
    prevprev: Optional[object] = None
    prev: Optional[object] = None
    curr: object = None
    next: Optional[object] = None
    index: int = 0

    def get_paraula(self, sillaba, words) -> Optional[object]:
        """Obté la paraula a la qual pertany una síl·laba."""
        if sillaba is None:
            return None
        for word in words:
            if sillaba in word.stress:
                return word
        return None


class ReglaAccent:
    """Classe base per a regles d'accent."""

    def __init__(self, nom: str, prioritat: int = 0):
        self.nom = nom
        self.prioritat = prioritat

    def aplica(self, ctx: ContextSillaba, words: List) -> bool:
        """
        Retorna True si s'ha aplicat algun canvi.
        Ha de ser implementat per les subclasses.
        """
        raise NotImplementedError

    def canvia_pes(self, ctx: ContextSillaba, sillaba, nou_pes: float, words: List):
        """Canvia el pes d'una síl·laba i actualitza les paraules."""
        if sillaba is None:
            return

        # Protecció centralitzada per evitar assignacions indegudes de CIM_MAXIM (5.0)
        if nou_pes == PesAccent.CIM_MAXIM:
            # Si tenim referència al vers, validem el candidat de tall amb les mateixes regles
            vers_obj = getattr(self, '_vers', None)
            if vers_obj is not None:
                try:
                    from AIMeRiC.escansio.modules.utils.decasillab import troba_tall_posible
                    idx = vers_obj.nomes_sillabes.index(sillaba)
                    # Només assignem 5 si troba_tall_posible diu 'best'
                    if troba_tall_posible(vers_obj, idx, True) != 'best':
                        return
                except Exception:
                    # Si no podem validar, no assignem el cim
                    return
            # La síl·laba ha de ser l'última del mot, no fusionada i la paraula no ha de tenir pronom enclític
            word_found = None
            for w in words:
                if sillaba in getattr(w, 'stress', []):
                    word_found = w
                    break
            if word_found is None:
                # No podem determinar la paraula, no assignem el cim
                return
            # comprovar condicions
            if not getattr(sillaba, 'fusionada', False) and word_found.stress and word_found.stress[-1] == sillaba and not getattr(word_found, 'has_PRONe', False):
                sillaba.pes = nou_pes
                # reflectim el canvi també a la representació dins de la paraula
                try:
                    word_found.stress[word_found.stress.index(sillaba)].pes = nou_pes
                except Exception:
                    pass
            else:
                # Si no es compleixen les condicions, no assignem 5.0
                return
        else:
            # Assignacions normals (altres pesos)
            sillaba.pes = nou_pes
            for word in words:
                if sillaba in getattr(word, 'stress', []):
                    word.stress[word.stress.index(sillaba)].pes = nou_pes


# === REGLES ESPECÍFIQUES ===

class ReglaPrimeraSillaba(ReglaAccent):
    """Regles per a la primera síl·laba del vers."""

    def __init__(self):
        super().__init__("Primera síl·laba", prioritat=100)

    def aplica(self, ctx: ContextSillaba, words: List) -> bool:
        if ctx.prev is not None or ctx.next is None:
            return False

        curr, next = ctx.curr, ctx.next
        canvis = False

        # xX amb igual pes
        if curr.pes == next.pes:
            self.canvia_pes(ctx, curr, PesAccent.ATONA, words)
            canvis = True

        # Pes massa baix (< BIVALENT)
        if curr.pes < PesAccent.BIVALENT:
            self.canvia_pes(ctx, curr, PesAccent.ATONA, words)
            canvis = True

        # Entre 1 i 5
        if PesAccent.DESACCENTUADA < curr.pes < PesAccent.CIM_MAXIM:
            if next.pes > PesAccent.SECUNDARI:
                sillaba_target = next if curr.pes >= next.pes else curr
                self.canvia_pes(ctx, sillaba_target, PesAccent.DESACCENTUADA, words)
            elif next.pes <= PesAccent.SECUNDARI:
                sillaba_target = next if curr.pes >= next.pes else curr
                self.canvia_pes(ctx, sillaba_target, PesAccent.ATONA, words)
            canvis = True

        return canvis


class ReglaUltimaSillaba(ReglaAccent):
    """Regles per a l'última síl·laba del vers."""

    def __init__(self):
        super().__init__("Última síl·laba", prioritat=100)

    def aplica(self, ctx: ContextSillaba, words: List) -> bool:
        if ctx.next is not None or ctx.prev is None:
            return False

        curr, prev = ctx.curr, ctx.prev

        if PesAccent.DESACCENTUADA < curr.pes < PesAccent.CIM_MAXIM:
            sillaba_target = curr if prev.pes > curr.pes else prev
            self.canvia_pes(ctx, sillaba_target, PesAccent.DESACCENTUADA, words)
            return True

        return False


class ReglaXocAccents(ReglaAccent):
    """Resol xocs entre accents consecutius (cims màxims)."""

    def __init__(self):
        super().__init__("Xoc d'accents", prioritat=90)

    def aplica(self, ctx: ContextSillaba, words: List) -> bool:
        # XOCS ENTRE CURR I NEXT
        if ctx.next is not None:
            curr, next = ctx.curr, ctx.next

            if curr.pes >= PesAccent.BIVALENT and next.pes >= PesAccent.BIVALENT:
                word_curr = ctx.get_paraula(curr, words)
                word_next = ctx.get_paraula(next, words)

                if word_curr and word_next:
                    condicions_desaccentuacio = [
                        (word_next.pos_ == "ADJ", curr, next),
                        (word_next.dep_ == 'nmod' and word_next.pos_ == 'ADP', curr, next),
                        (word_curr.pos_ == 'VERB' and word_next.pos_ in ['ADV', 'ADJ', 'NOUN'], curr, next),
                    ]

                    aplicat = False
                    for condicio, sil1, sil2 in condicions_desaccentuacio:
                        if condicio and self._evalua_desaccentuacio(ctx, sil1, sil2, words):
                            aplicat = True
                            break

                    # Si no s'ha aplicat cap condició específica, aplicar lògica per defecte
                    if not aplicat:
                        if self._evalua_desaccentuacio(ctx, curr, next, words):
                            return True

        # XOCS ENTRE PREV I CURR
        if ctx.prev is not None:
            prev, curr = ctx.prev, ctx.curr

            if prev.pes >= PesAccent.BIVALENT and curr.pes >= PesAccent.BIVALENT:
                word_prev = ctx.get_paraula(prev, words)
                word_curr = ctx.get_paraula(curr, words)

                if word_prev and word_curr:
                    condicions_desaccentuacio = [
                        (word_curr.pos_ == "ADJ", prev, curr),
                        (word_curr.dep_ == 'nmod' and word_curr.pos_ == 'ADP', prev, curr),
                        (word_prev.pos_ == 'VERB' and word_curr.pos_ in ['ADV', 'ADJ', 'NOUN'], prev, curr),
                    ]

                    aplicat = False
                    for condicio, sil1, sil2 in condicions_desaccentuacio:
                        if condicio and self._evalua_desaccentuacio(ctx, sil1, sil2, words):
                            aplicat = True
                            break

                    # Si no s'ha aplicat cap condició específica, aplicar lògica per defecte
                    if not aplicat:
                        if self._evalua_desaccentuacio(ctx, prev, curr, words):
                            return True

        return False

    def _evalua_desaccentuacio(self, ctx: ContextSillaba, sil1, sil2, words) -> bool:
        """Avalua si cal desaccentuar en un xoc."""
        # Simplificar: si ambdues són >= BIVALENT, desaccentuar
        if sil1.pes >= PesAccent.BIVALENT and sil2.pes >= PesAccent.BIVALENT:
            # Determinar posicions (1-indexed) per a lògica de talls
            pos_sil1 = None
            pos_sil2 = None

            if sil1 == ctx.curr and sil2 == ctx.next:
                pos_sil1 = ctx.index + 1
                pos_sil2 = ctx.index + 2
            elif sil1 == ctx.prev and sil2 == ctx.curr:
                pos_sil1 = ctx.index
                pos_sil2 = ctx.index + 1

            # Cas especial: ambdues síl·labes són LEXIC o superiors (xoc fort)
            if sil1.pes >= PesAccent.LEXIC and sil2.pes >= PesAccent.LEXIC:
                sil1_en_tall = pos_sil1 in TALLS_FREQUENTS if pos_sil1 else False
                sil2_en_tall = pos_sil2 in TALLS_FREQUENTS if pos_sil2 else False

                prioritat_sil1 = prioritat_tall(pos_sil1) if pos_sil1 else 0
                prioritat_sil2 = prioritat_tall(pos_sil2) if pos_sil2 else 0

                # Si ambdues estan en tall, prioritzar segons l'ordre de preferència
                if sil1_en_tall and sil2_en_tall:
                    if sil1.pes == 5.0:
                        if prioritat_sil1 > prioritat_sil2:
                            # sil1 té tall més prioritari
                            self.canvia_pes(ctx, sil1, PesAccent.CIM_MAXIM, words)
                            self.canvia_pes(ctx, sil2, PesAccent.DESACCENTUADA, words)
                            return True
                        else:
                            # sil2 té tall més prioritari o igual
                            self.canvia_pes(ctx, sil2, PesAccent.CIM_MAXIM, words)
                            self.canvia_pes(ctx, sil1, PesAccent.DESACCENTUADA, words)
                            return True
                # Només una està en tall
                elif sil2_en_tall and not sil1_en_tall and sil2.pes == 5.0:
                    self.canvia_pes(ctx, sil2, PesAccent.CIM_MAXIM, words)
                    self.canvia_pes(ctx, sil1, PesAccent.DESACCENTUADA, words)
                    return True
                elif sil1_en_tall and not sil2_en_tall:
                    # Abans d'assignar el cim, comprovem condicions de paraula i síl·labes
                    try:
                        word1 = ctx.get_paraula(sil1, words)
                    except Exception:
                        word1 = None

                    cond_word_ok = False
                    if word1 and getattr(word1, 'stress', None):
                        # Ha de ser l'última síl·laba del mot, no fusionada i no tenir pronom enclític
                        if word1.stress and word1.stress[-1] == sil1 and getattr(sil1, 'fusionada', False) is False and getattr(word1, 'has_PRONe', False) is False:
                            cond_word_ok = True

                    if cond_word_ok and sil2.pes < PesAccent.LEXIC:
                        self.canvia_pes(ctx, sil1, PesAccent.CIM_MAXIM, words)
                        self.canvia_pes(ctx, sil2, PesAccent.DESACCENTUADA, words)
                        return True

            # Cas per defecte: desaccentuar la síl·laba de pes més baix
            target = sil1 if sil2.pes >= sil1.pes else sil2
            self.canvia_pes(ctx, target, PesAccent.DESACCENTUADA, words)
            return True
        return False


class ReglaXocAccentsSecundaris(ReglaAccent):
    """Resol xocs entre accents secundaris (2.0, 2.5, 1.5)."""

    def __init__(self):
        super().__init__("Xoc d'accents secundaris", prioritat=65)

    def aplica(self, ctx: ContextSillaba, words: List) -> bool:
        # XOCS ENTRE CURR I NEXT
        if ctx.next is not None:
            curr, next = ctx.curr, ctx.next

            # Detectar xocs d'accents secundaris: 2-2, 2.5-2.5, 2.5-2, 2-2.5, 2-1.5, 1.5-2
            if self._es_xoc_secundari(curr.pes, next.pes):
                # Conservar l'accent de major pes
                # Si tenen el mateix pes, conservar el de la dreta (desaccentuar curr)
                if curr.pes < next.pes:
                    target = curr  # curr és més petit, desaccentuar curr
                elif curr.pes > next.pes:
                    target = next  # next és més petit, desaccentuar next
                else:
                    # Mateix pes: conservar el de la dreta (next), desaccentuar l'esquerra (curr)
                    target = curr

                self.canvia_pes(ctx, target, PesAccent.ATONA, words)
                return True


        # XOCS ENTRE PREV I CURR
        if ctx.prev is not None:
            prev, curr = ctx.prev, ctx.curr

            if self._es_xoc_secundari(prev.pes, curr.pes):
                # Conservar l'accent de major pes
                # Si tenen el mateix pes, conservar el de la dreta (curr), desaccentuar prev
                if prev.pes < curr.pes:
                    target = prev  # prev és més petit, desaccentuar prev
                elif prev.pes > curr.pes:
                    target = curr  # curr és més petit, desaccentuar curr
                else:
                    # Mateix pes: conservar el de la dreta (curr), desaccentuar l'esquerra (prev)
                    target = prev

                self.canvia_pes(ctx, target, PesAccent.ATONA, words)
                return True

        return False

    def _es_xoc_secundari(self, pes1: float, pes2: float) -> bool:
        """Comprova si és un xoc d'accents secundaris."""
        pesos_secundaris = {1.5, 2.0, 2.5}

        # Arrodonir per evitar problemes de precisió
        pes1_round = round(pes1, 1)
        pes2_round = round(pes2, 1)

        # Tots dos han de ser accents secundaris
        return pes1_round in pesos_secundaris and pes2_round in pesos_secundaris

class ReglaAccentsIntermedis(ReglaAccent):
    """Regles per a síl·labes entre dues altres."""

    def __init__(self):
        super().__init__("Accents intermedis", prioritat=80)

    def aplica(self, ctx: ContextSillaba, words: List) -> bool:
        if ctx.prev is None or ctx.next is None:
            return False

        curr, prev, next = ctx.curr, ctx.prev, ctx.next
        canvis = False

        # Pes entre 2.5 i 5 (SECUNDARI_FORT i CIM_MAXIM)
        if PesAccent.LLINDAR_SECUNDARI < curr.pes < PesAccent.CIM_MAXIM:
            if next.pes > PesAccent.LLINDAR_SECUNDARI:
                # Obtenir paraules per prioritzar segons categoria gramatical
                word_curr = ctx.get_paraula(curr, words)
                word_next = ctx.get_paraula(next, words)

                target = self._selecciona_target_xoc(curr, next, word_curr, word_next)
                self.canvia_pes(ctx, target, PesAccent.DESACCENTUADA, words)
                canvis = True
            elif PesAccent.LLINDAR_SECUNDARI < prev.pes < PesAccent.CIM_MAXIM:
                word_curr = ctx.get_paraula(curr, words)
                word_prev = ctx.get_paraula(prev, words)

                target = self._selecciona_target_xoc(prev, curr, word_prev, word_curr)
                self.canvia_pes(ctx, target, PesAccent.DESACCENTUADA, words)
                canvis = True
            elif next.pes <= PesAccent.LLINDAR_SECUNDARI:
                self.canvia_pes(ctx, next, PesAccent.SECUNDARI_DESACCENTUADA, words)
                canvis = True

        # Pes entre 1 i 2.5 (DESACCENTUADA fins SECUNDARI_FORT)
        elif PesAccent.DESACCENTUADA < curr.pes <= PesAccent.LLINDAR_SECUNDARI:
            canvis = self._gestiona_pes_baix(ctx, words)

        # Casos especials
        elif curr.pes == PesAccent.LEXIC and next.pes == PesAccent.CIM_MAXIM:
            # Cas especial: 4 i 5 consecutius
            word_curr = ctx.get_paraula(curr, words)
            word_next = ctx.get_paraula(next, words)
            target = self._selecciona_target_xoc(curr, next, word_curr, word_next)
            self.canvia_pes(ctx, target, PesAccent.DESACCENTUADA, words)
            canvis = True
        elif curr.pes == PesAccent.CIM_MAXIM:
            canvis = self._gestiona_cim_maxim(ctx, words)
        elif PesAccent.DESACCENTUADA < curr.pes <= PesAccent.LLINDAR_SECUNDARI:
            if next.pes > curr.pes or prev.pes > curr.pes:
                self.canvia_pes(ctx, curr, PesAccent.SECUNDARI_DESACCENTUADA, words)
                canvis = True

        return canvis

    def _selecciona_target_xoc(self, sil1, sil2, word1, word2):
        """
        Selecciona quina síl·laba desaccentuar en un xoc, prioritzant
        segons la categoria gramatical de les paraules.

        Prioritat (de més a menys important prosòdicament):
        1. VERB, NOUN, PROPN, ADJ - Paraules lèxiques (mantenir accent)
        2. NUM, PRON - Paraules semi-funcionals
        3. ADV, ADP, DET, AUX, CONJ, PART, SCONJ - Paraules funcionals (desaccentuar)
        """
        # Categories lèxiques (prioritat alta)
        categories_lexiques = {'VERB', 'NOUN', 'PROPN', 'ADJ'}
        # Categories funcionals (prioritat baixa)
        categories_funcionals = {'ADV', 'ADP', 'DET', 'AUX', 'CCONJ', 'SCONJ', 'PRON', 'PRONe', 'ADPa'}

        pos1 = word1.pos_ if word1 else None
        pos2 = word2.pos_ if word2 else None

        # Si una és funcional i l'altra lèxica, desaccentua la funcional
        if pos2 in categories_funcionals and pos1 in categories_lexiques:
            return sil2  # Desaccentua la paraula funcional (ex: "ben")
        elif pos1 in categories_funcionals and pos2 in categories_lexiques:
            return sil1

        # Si ambdues són funcionals o lèxiques, desaccentua la de pes més baix
        # (per mantenir el patró rítmic més natural)
        return sil2 if sil2.pes < sil1.pes else sil1

    def _gestiona_pes_baix(self, ctx: ContextSillaba, words: List) -> bool:
        """Gestiona síl·labes amb pes entre 1 i 2.5."""
        curr, prev, next = ctx.curr, ctx.prev, ctx.next

        if curr.pes == next.pes:
            self.canvia_pes(ctx, curr, PesAccent.SECUNDARI_DESACCENTUADA, words)
            return True
        elif curr.pes == prev.pes:
            self.canvia_pes(ctx, prev, PesAccent.SECUNDARI_DESACCENTUADA, words)
            return True
        elif PesAccent.DESACCENTUADA < next.pes < PesAccent.LLINDAR_SECUNDARI:
            target = curr if next.pes >= curr.pes else next
            self.canvia_pes(ctx, target, PesAccent.ATONA, words)
            return True
        elif PesAccent.DESACCENTUADA < prev.pes < PesAccent.LLINDAR_SECUNDARI:
            target = curr if next.pes >= curr.pes else next
            self.canvia_pes(ctx, target, PesAccent.SECUNDARI_DESACCENTUADA, words)
            return True
        elif next.pes >= PesAccent.LLINDAR_SECUNDARI:
            self.canvia_pes(ctx, curr, PesAccent.SECUNDARI_DESACCENTUADA, words)
            return True
        elif prev.pes >= PesAccent.LLINDAR_SECUNDARI:
            self.canvia_pes(ctx, curr, PesAccent.ATONA, words)
            return True

        return False

    def _gestiona_cim_maxim(self, ctx: ContextSillaba, words: List) -> bool:
        """Gestiona síl·labes amb pes màxim (5.0)."""
        curr, prev, next = ctx.curr, ctx.prev, ctx.next

        # Entre LEXIC (4.0) i CIM_MAXIM (5.0)
        if PesAccent.LEXIC < next.pes < PesAccent.CIM_MAXIM:
            self.canvia_pes(ctx, next, PesAccent.DESACCENTUADA, words)
            return True
        elif PesAccent.LEXIC < prev.pes < PesAccent.CIM_MAXIM:
            self.canvia_pes(ctx, prev, PesAccent.DESACCENTUADA, words)
            return True
        elif next.pes <= PesAccent.BIVALENT:
            self.canvia_pes(ctx, next, PesAccent.ATONA, words)
            return True
        elif prev.pes <= PesAccent.BIVALENT:
            self.canvia_pes(ctx, prev, PesAccent.ATONA, words)
            return True

        return False


class ReglaAccentsSecundaris(ReglaAccent):
    """Afegeix accents secundaris per evitar valls accentuals."""

    def __init__(self):
        super().__init__("Accents secundaris", prioritat=70)

    def aplica(self, ctx: ContextSillaba, words: List) -> bool:
        if ctx.prev is None or ctx.next is None:
            return False

        curr, prev, next = ctx.curr, ctx.prev, ctx.next
        canvis = False

        # Tres desaccentuades seguides amb prevprev
        if (ctx.prevprev is not None and next is not None and
                ctx.prevprev.pes == PesAccent.DESACCENTUADA and
                prev.pes == PesAccent.DESACCENTUADA and
                curr.pes == PesAccent.DESACCENTUADA and
                next.pes < PesAccent.DESACCENTUADA):
            self.canvia_pes(ctx, curr, PesAccent.SECUNDARI, words)
            canvis = True

        # Dues desaccentuades abans de forta
        if (prev.pes <= PesAccent.DESACCENTUADA
                and curr.pes <= PesAccent.DESACCENTUADA and curr.pes > PesAccent.ATONA
        and next.pes <= PesAccent.DESACCENTUADA):
            self.canvia_pes(ctx, curr, PesAccent.SECUNDARI, words)
            canvis = True

        # Forta + desaccentuada
        if (PesAccent.ATONA < curr.pes <= PesAccent.DESACCENTUADA
                and next.pes < PesAccent.LLINDAR_SECUNDARI):
            if curr.pes > next.pes:
                self.canvia_pes(ctx, next, PesAccent.SECUNDARI_DESACCENTUADA, words)
            else:
                self.canvia_pes(ctx, curr, PesAccent.SECUNDARI_DESACCENTUADA, words)
            canvis = True

        # Desaccentuada entre àtones
        if (prev.pes <= PesAccent.DESACCENTUADA and
                curr.pes == PesAccent.DESACCENTUADA and
                next.pes <= PesAccent.DESACCENTUADA):
            self.canvia_pes(ctx, curr, PesAccent.SECUNDARI, words)
            canvis = True

        # Desaccentuada després d'àtona
        if curr.pes < PesAccent.DESACCENTUADA < next.pes:
            self.canvia_pes(ctx, curr, PesAccent.SECUNDARI_DESACCENTUADA, words)
            canvis = True

        # xXx
        if (prev.pes < PesAccent.DESACCENTUADA <= curr.pes < PesAccent.SECUNDARI and
                next.pes < PesAccent.DESACCENTUADA):
            self.canvia_pes(ctx, curr, PesAccent.SECUNDARI, words)
            canvis = True

        # Vall accentual amb paraula bivalent
        if (prev.pes < PesAccent.DESACCENTUADA and
                curr.pes < PesAccent.DESACCENTUADA and curr.pes >
                next.pes < PesAccent.DESACCENTUADA):
            word_curr = ctx.get_paraula(curr, words)
            if word_curr and word_curr.bivalent and word_curr.stress_index == curr.s_index:
                self.canvia_pes(ctx, curr, PesAccent.SECUNDARI, words)
                canvis = True

        # Secundari seguit de fort
        if (curr.pes == PesAccent.SECUNDARI
                and next.pes >= PesAccent.LLINDAR_SECUNDARI):
            self.canvia_pes(ctx, curr, PesAccent.SECUNDARI_DESACCENTUADA, words)
            canvis = True

        return canvis


class ReglaPostProcessament(ReglaAccent):
    """Regles finals de neteja i ajustament."""

    def __init__(self):
        super().__init__("Post-processament", prioritat=60)

    def aplica(self, ctx: ContextSillaba, words: List) -> bool:
        curr, prev, next = ctx.curr, ctx.prev, ctx.next
        canvis = False

        # Última síl·laba
        if next is None and prev is not None:
            if prev.pes < PesAccent.DESACCENTUADA and curr.pes == PesAccent.DESACCENTUADA:
                self.canvia_pes(ctx, curr, PesAccent.ATONA, words)
                canvis = True

        # Desaccentuada entre àtones (segona passada)
        elif prev is not None and next is not None:
            if (curr.pes == PesAccent.DESACCENTUADA and
                    prev.pes < PesAccent.DESACCENTUADA and
                    next.pes < PesAccent.DESACCENTUADA):
                self.canvia_pes(ctx, curr, PesAccent.SECUNDARI, words)
                canvis = True

            # SECUNDARI_DESACCENTUADA (0.75) -> SECUNDARI (2.0)
            if (prev.pes < PesAccent.DESACCENTUADA and
                    curr.pes == PesAccent.SECUNDARI_DESACCENTUADA and
                    next.pes < PesAccent.LLINDAR_SECUNDARI):
                self.canvia_pes(ctx, curr, PesAccent.SECUNDARI, words)
                canvis = True

            if curr.pes >= PesAccent.BIVALENT and (next.pes < PesAccent.BIVALENT and next.pes > PesAccent.ATONA):
                self.canvia_pes(ctx, next, PesAccent.SECUNDARI_DESACCENTUADA, words)
                ReglaAccentsSecundaris()
                canvis = True

        return canvis


class ReglaPrimeraSillabaFinal(ReglaAccent):
    """
    Regla final: Permet que la primera síl·laba conservi un accent inferior a 3
    si les dues síl·labes següents són àtones.
    Patró: X-0-0 (on X < 3) → Manté X o restaura a accent secundari
    """

    def __init__(self):
        super().__init__("Primera síl·laba (final)", prioritat=50)

    def aplica(self, ctx: ContextSillaba, words: List) -> bool:
        """Mètode base (no s'utilitza per aquesta regla)."""
        return False

    def aplica_amb_llista(self, ctx: ContextSillaba, words: List, sillabes: List) -> bool:
        """Versió amb accés a la llista completa de síl·labes."""
        # Només per a la primera síl·laba
        if ctx.prev is not None:
            return False

        curr, next = ctx.curr, ctx.next

        # Necessitem almenys 2 síl·labes després
        if next is None or ctx.index + 2 >= len(sillabes):
            return False

        nextnext = sillabes[ctx.index + 2]

        # Comprova si les dues següents són àtones
        if curr.pes < PesAccent.BIVALENT and next.pes == PesAccent.ATONA and nextnext.pes >= PesAccent.SECUNDARI:
            self.canvia_pes(ctx, curr, PesAccent.ATONA, words)
        elif curr.pes < PesAccent.BIVALENT and next.pes < PesAccent.SECUNDARI <= nextnext.pes:
            self.canvia_pes(ctx, curr, PesAccent.SECUNDARI_DESACCENTUADA, words)
        elif next.pes != PesAccent.ATONA or nextnext.pes != PesAccent.ATONA:
            return False

        # Si la primera síl·laba ha estat desaccentuada o és àtona
        # i les dues següents són àtones, restaura a accent secundari
        elif curr.pes == PesAccent.DESACCENTUADA:  # < 3.0
            #if curr.pes == PesAccent.ATONA:
                # Restaura de 0 a 2 (accent secundari)
            self.canvia_pes(ctx, curr, PesAccent.SECUNDARI, words)
            return True
            # Si ja té un accent entre 0.75 i 2.5, el manté (no fa res)
            # Això es gestiona implícitament no canviant-lo

        return False


class GestorAccentsProsodics:
    """Gestiona l'aplicació de regles d'accents prosòdics."""

    def __init__(self, subdividit, debug: bool = False):
        self.subdividit = subdividit
        self.debug = debug
        self.regles_xocs: List[ReglaAccent] = []
        self.regles_secundaris: List[ReglaAccent] = []
        self.regles_xocs_secundaris: List[ReglaAccent] = []
        self.regles_finals: List = []
        self._inicialitza_regles()

    def _inicialitza_regles(self):
        """Inicialitza i separa les regles per passades."""
        # Regles per resoldre xocs accentuals (primera passada)
        self.regles_xocs = [
            ReglaPrimeraSillaba(),
            ReglaUltimaSillaba(),
            ReglaXocAccents(),
            ReglaAccentsIntermedis(),
        ]

        # Regles per assignar accents secundaris (segona passada)
        self.regles_secundaris = [
            ReglaAccentsSecundaris(),
            ReglaPostProcessament()
        ]

        # Regles per resoldre xocs d'accents secundaris (tercera passada)
        self.regles_xocs_secundaris = [
            ReglaXocAccentsSecundaris()
        ]

        # Regles finals
        self.regles_finals = [
            ReglaPrimeraSillabaFinal()
        ]

    def _itera_sillabes(self, sillabes: List) -> Generator[ContextSillaba, Any, None]:
        """Genera contextos de síl·labes amb les adjacents."""
        for i in range(len(sillabes)):
            yield ContextSillaba(
                prevprev=sillabes[i - 2] if i > 1 else None,
                prev=sillabes[i - 1] if i > 0 else None,
                curr=sillabes[i],
                next=sillabes[i + 1] if i < len(sillabes) - 1 else None,
                index=i
            )

    def _captura_estat(self, ctx: ContextSillaba) -> Dict[str, Tuple[str, float]]:
        """Captura l'estat actual dels pesos de les síl·labes en el context."""
        estat = {}
        if ctx.prevprev:
            estat['prevprev'] = (ctx.prevprev.text, ctx.prevprev.pes)
        if ctx.prev:
            estat['prev'] = (ctx.prev.text, ctx.prev.pes)
        if ctx.curr:
            estat['curr'] = (ctx.curr.text, ctx.curr.pes)
        if ctx.next:
            estat['next'] = (ctx.next.text, ctx.next.pes)
        return estat

    def _detecta_canvis(self, estat_abans: Dict, estat_despres: Dict) -> Dict[str, Tuple]:
        """Detecta quines síl·labes han canviat de pes."""
        canvis = {}
        for clau in estat_abans:
            if clau in estat_despres:
                text_abans, pes_abans = estat_abans[clau]
                text_despres, pes_despres = estat_despres[clau]
                if pes_abans != pes_despres:
                    canvis[clau] = (text_despres, pes_abans, pes_despres)
        return canvis

    def _print_debug_header(self, ctx: ContextSillaba):
        """Imprimeix la capçalera de debug amb el context actual."""
        parts = []
        if ctx.prev:
            parts.append(f"{ctx.prev.text}({ctx.prev.pes})")
        parts.append(f"[{ctx.curr.text}({ctx.curr.pes})]")
        if ctx.next:
            parts.append(f"{ctx.next.text}({ctx.next.pes})")

        print(f"\n{'=' * 60}")
        print(f"Posició {ctx.index + 1}: {' '.join(parts)}")
        print(f"{'=' * 60}")

    def _print_canvis(self, regla_nom: str, canvis: Dict[str, Tuple]):
        """Imprimeix els canvis aplicats per una regla."""
        if not canvis:
            return

        print(f"\n  ✓ REGLA APLICADA: {regla_nom}")
        print(f"  {'-' * 56}")
        for clau, (text, pes_abans, pes_despres) in canvis.items():
            fletxa = "→"
            posicio_label = {
                'prevprev': 'prev-prev',
                'prev': 'anterior',
                'curr': 'ACTUAL  ',
                'next': 'següent '
            }.get(clau, clau)

            print(f"  {posicio_label}: '{text}' "
                  f"{pes_abans:4.2f} {fletxa} {pes_despres:4.2f}")

    def _te_xoc_accentual(self, ctx: ContextSillaba, pes1: float, pes2: float) -> bool:
        """
        Comprova si hi ha un xoc accentual específic entre síl·labes adjacents.

        Args:
            ctx: Context de la síl·laba actual
            pes1: Pes de la primera síl·laba del xoc
            pes2: Pes de la segona síl·laba del xoc

        Returns:
            True si existeix el xoc especificat
        """
        # Arrodonir a 1 decimal per evitar problemes de precisió
        curr_pes = round(ctx.curr.pes, 1)
        next_pes = round(ctx.next.pes, 1) if ctx.next else None
        prev_pes = round(ctx.prev.pes, 1) if ctx.prev else None

        # Comprovar xoc curr-next
        if next_pes is not None:
            if round(pes1, 1) == curr_pes and round(pes2, 1) == next_pes:
                return True

        # Comprovar xoc prev-curr (per casos com 5-3, 5-2)
        if prev_pes is not None:
            if round(pes1, 1) == prev_pes and round(pes2, 1) == curr_pes:
                return True

        return False

    def aplica_regles(self, vers):
        """Aplica totes les regles als accents prosòdics del vers en tres passades."""
        sillabes = vers.nomes_sillabes

        # Assignem referència al vers a cada regla perquè `canvia_pes` pugui validar
        totes_regles = self.regles_xocs + self.regles_secundaris + self.regles_xocs_secundaris + self.regles_finals
        for regla in totes_regles:
            try:
                regla._vers = vers
            except Exception:
                pass

        if self.debug:
            print(f"\n{'#' * 60}")
            print(f"# INICI PROCESSAMENT: {len(sillabes)} síl·labes")
            print(f"# Patró inicial: {' '.join(str(s.pes) for s in sillabes)}")
            print(f"{'#' * 60}")

        # ===== PRIMERA PASSADA: RESOLUCIÓ DE XOCS ACCENTUALS =====
        if self.debug:
            print(f"\n{'#' * 60}")
            print(f"# PRIMERA PASSADA: Resolució de xocs accentuals")
            print(f"{'#' * 60}")

        # Ordre dels xocs a resoldre amb tots els valors intermitjos (3.5, 2.5, 1.5)
        grup1 = [
            # Grup 1: Xocs amb 5 (inclou 4, 3.5, 3, 2.5, 2, 1.5)
            (4.0, 5.0, "4-5"),
            (3.5, 5.0, "3-5"),
            (3.0, 5.0, "3-5"),
            (2.5, 5.0, "2-5"),
            (2.0, 5.0, "2-5"),
            (1.5, 5.0, "2-5"),
            #(5.0, 4.0, "5-4"),
            (5.0, 3.5, "5-3"),
            (5.0, 3.0, "5-3"),
            (5.0, 2.5, "5-2"),
            (5.0, 2.0, "5-2"),
            (5.0, 1.5, "5-2")
            ]

        grup2 = [
            # Grup 2: Xocs amb 4 (inclou 3.5, 3, 2.5, 2, 1.5)
            (4.0, 4.0, "4-4"),
            (3.5, 4.0, "3-4"),
            (3.0, 4.0, "3-4"),
            (2.5, 4.0, "2-4"),
            (2.0, 4.0, "2-4"),
            (1.5, 4.0, "2-4"),
            (4.0, 3.5, "4-3"),
            (4.0, 3.0, "4-3"),
            (4.0, 2.5, "4-2"),
            (4.0, 2.0, "4-2"),
            (4.0, 1.5, "4-2")
        ]
        grup3 = [
            # Grup 3: Xocs amb 3.5 i 3 (inclou 2.5, 2, 1.5)
            (3.5, 3.5, "3-3"),
            (3.5, 3.0, "3-3"),
            (3.0, 3.5, "3-3"),
            (3.0, 3.0, "3-3"),
            (3.5, 2.5, "3-2"),
            (3.5, 2.0, "3-2"),
            (3.5, 1.5, "3-2"),
            (3.0, 2.5, "3-2"),
            (3.0, 2.0, "3-2"),
            (3.0, 1.5, "3-2")
            ]
        grup4 = [
            # Grup 4: Xocs amb 2.5, 2 i 1.5
            (2.5, 5.0, "2-5"),
            (2.5, 4.0, "2-4"),
            (2.5, 3.5, "2-3"),
            (2.5, 3.0, "2-3"),
            (2.5, 2.5, "2-2"),
            (2.5, 2.0, "2-2"),
            (2.5, 1.5, "2-2"),
            (2.0, 5.0, "2-5"),
            (2.0, 4.0, "2-4"),
            (2.0, 3.5, "2-3"),
            (2.0, 3.0, "2-3"),
            (2.0, 2.5, "2-2"),
            (2.0, 2.0, "2-2"),
            (2.0, 1.5, "2-2"),
            (1.5, 5.0, "2-5"),
            (1.5, 4.0, "2-4"),
            (1.5, 3.5, "2-3"),
            (1.5, 3.0, "2-3"),
            (1.5, 2.5, "2-2"),
            (1.5, 2.0, "2-2"),
            (1.5, 1.5, "2-2")
        ]

        #if self.subdividit:
        ordre_xocs = grup1 + grup2 + grup3 + grup4
        #else:
        #    ordre_xocs = grup3 + grup4

        for pes1, pes2, nom_xoc in ordre_xocs:
            if self.debug:
                print(f"\n{'-' * 60}")
                print(f"Resolent xocs: {nom_xoc} ({pes1}-{pes2})")
                print(f"{'-' * 60}")

            # Iterar amb límit màxim de 100 iteracions per evitar bucles infinits
            canvis_iteracio = True
            num_iteracio = 0
            while canvis_iteracio and num_iteracio < 100:
                num_iteracio += 1
                canvis_iteracio = False

                for ctx in self._itera_sillabes(sillabes):
                    # Comprovar si hi ha aquest tipus de xoc
                    if not self._te_xoc_accentual(ctx, pes1, pes2):
                        continue

                    if self.debug:
                        self._print_debug_header(ctx)
                        print(f"  → Detectat xoc {nom_xoc} ({pes1}-{pes2}) (iteració {num_iteracio})")

                    # Aplicar regles de xocs
                    for regla in self.regles_xocs:
                        try:
                            if self.debug:
                                estat_abans = self._captura_estat(ctx)

                            aplicat = regla.aplica(ctx, vers.words)

                            if self.debug and aplicat:
                                estat_despres = self._captura_estat(ctx)
                                canvis = self._detecta_canvis(estat_abans, estat_despres)
                                self._print_canvis(regla.nom, canvis)

                            if aplicat:
                                canvis_iteracio = True
                                break  # Sortir del bucle de regles

                        except Exception as e:
                            print(f"  ✗ Error aplicant regla '{regla.nom}': {e}")

                # Advertir si s'ha arribat al límit
                if num_iteracio >= 100:
                    print(f"  ⚠ ADVERTÈNCIA: S'ha arribat al límit de 100 iteracions per al xoc {nom_xoc}")

        # ===== SEGONA PASSADA: ACCENTS SECUNDARIS =====
        if self.debug:
            print(f"\n{'#' * 60}")
            print(f"# SEGONA PASSADA: Assignació d'accents secundaris")
            print(f"{'#' * 60}")

        for ctx in self._itera_sillabes(sillabes):
            if self.debug:
                self._print_debug_header(ctx)

            for regla in self.regles_secundaris:
                try:
                    if self.debug:
                        estat_abans = self._captura_estat(ctx)

                    aplicat = regla.aplica(ctx, vers.words)

                    if self.debug and aplicat:
                        estat_despres = self._captura_estat(ctx)
                        canvis = self._detecta_canvis(estat_abans, estat_despres)
                        self._print_canvis(regla.nom, canvis)

                except Exception as e:
                    print(f"  ✗ Error aplicant regla '{regla.nom}': {e}")

        # ===== TERCERA PASSADA: RESOLUCIÓ DE XOCS D'ACCENTS SECUNDARIS =====
        if self.debug:
            print(f"\n{'#' * 60}")
            print(f"# TERCERA PASSADA: Resolució de xocs d'accents secundaris")
            print(f"{'#' * 60}")

        # Xocs a resoldre: 2-2, 2.5-2.5, 2.5-2, 2-2.5, 2-1.5, 1.5-2
        ordre_xocs_secundaris = [
            (2.5, 2.5, "2.5-2.5"),
            (2.5, 2.0, "2.5-2"),
            (2.0, 2.5, "2-2.5"),
            (2.0, 2.0, "2-2"),
            (2.0, 1.5, "2-1.5"),
            (1.5, 2.0, "1.5-2"),
        ]

        for pes1, pes2, nom_xoc in ordre_xocs_secundaris:
            if self.debug:
                print(f"\n{'-' * 60}")
                print(f"Resolent xocs secundaris: {nom_xoc} ({pes1}-{pes2})")
                print(f"{'-' * 60}")

            # Iterar amb límit màxim de 10 iteracions
            canvis_iteracio = True
            num_iteracio = 0
            while canvis_iteracio and num_iteracio < 10:
                num_iteracio += 1
                canvis_iteracio = False

                for ctx in self._itera_sillabes(sillabes):
                    # Comprovar si hi ha aquest tipus de xoc
                    if not self._te_xoc_accentual(ctx, pes1, pes2):
                        continue

                    if self.debug:
                        self._print_debug_header(ctx)
                        print(f"  → Detectat xoc secundari {nom_xoc} ({pes1}-{pes2}) (iteració {num_iteracio})")

                    # Aplicar regles de xocs secundaris
                    for regla in self.regles_xocs_secundaris:
                        try:
                            if self.debug:
                                estat_abans = self._captura_estat(ctx)

                            aplicat = regla.aplica(ctx, vers.words)

                            if self.debug and aplicat:
                                estat_despres = self._captura_estat(ctx)
                                canvis = self._detecta_canvis(estat_abans, estat_despres)
                                self._print_canvis(regla.nom, canvis)

                            if aplicat:
                                canvis_iteracio = True
                                break  # Sortir del bucle de regles

                        except Exception as e:
                            print(f"  ✗ Error aplicant regla '{regla.nom}': {e}")

        # ===== PASSADA FINAL: AJUSTAMENTS GLOBALS =====
        if self.debug:
            print(f"\n{'#' * 60}")
            print(f"# PASSADA FINAL: Ajustaments globals")
            print(f"{'#' * 60}")

        for ctx in self._itera_sillabes(sillabes):
            for regla in self.regles_finals:
                try:
                    if hasattr(regla, 'aplica_amb_llista'):
                        if self.debug:
                            estat_abans = self._captura_estat(ctx)

                        aplicat = regla.aplica_amb_llista(ctx, vers.words, sillabes)

                        if self.debug and aplicat:
                            estat_despres = self._captura_estat(ctx)
                            canvis = self._detecta_canvis(estat_abans, estat_despres)
                            if canvis:
                                self._print_debug_header(ctx)
                                self._print_canvis(f"{regla.nom} (final)", canvis)
                except Exception as e:
                    print(f"  ✗ Error aplicant regla final '{regla.nom}': {e}")

        if self.debug:
            print(f"\n{'#' * 60}")
            print(f"# FI PROCESSAMENT")
            print(f"# Patró final: {' '.join(str(s.pes) for s in sillabes)}")
            print(f"{'#' * 60}\n")


def accents_prosodics(self, subdividit=False, debug: bool = False):
    """
    Ajusta els accents prosòdics de les síl·labes del vers segons regles específiques.

    Args:
        self: Objecte que conté les síl·labes i paraules del vers.
        debug: Si True, mostra informació de debug.
    """
    gestor = GestorAccentsProsodics(subdividit, debug=debug)
    gestor.aplica_regles(self)


def cim_maxim(self):
    """Substitutes maximum peaks (>=2) with superior peaks (5) in the last strong syllable of each colon."""
    sense_mots = self.nomes_sillabes
    last_sil = self.objectiu - 1
    try:
        if sense_mots[last_sil].pes >= 2.5:
            if sense_mots[last_sil] in self.words[-1].stress:
                # Substitueix el pes de la síl·laba per 5.0
                self.words[-1].stress[self.words[-1].stress.index(sense_mots[last_sil])].pes = 5.0
                self.nomes_sillabes[last_sil].pes = 5.0
                self.patro[last_sil] = 5.0
            # Si hi ha més síl·labes després de last_sil (possiblement entre 0 i 3)
            if len(sense_mots) > last_sil + 1:
                word_index = None
                for word in self.words:
                    if sense_mots[last_sil] in word.stress:
                        word_index = self.words.index(word)
                        break
                if word_index is not None and word_index + 1 < len(self.words):
                    next_word = self.words[word_index + 1]
                    if next_word.stress:
                        if next_word.stress[0].pes < 2.0:  # Si la següent síl·laba és àtona o secundària
                            next_word.stress[0].pes = 0.0
                            self.nomes_sillabes[last_sil + 1].pes = 0.0
                            self.patro[last_sil + 1] = 0.0

            # Actualitza els recomptes mètrics i extramètrics
            self.recompte_sillabes_metriques = recompte_metric(self)
            self.recompte_sillabes_extrametriques = len(self.patro) - self.recompte_sillabes_metriques

        elif sense_mots[last_sil].pes == 1.0:
            for word in self.words:
                if sense_mots[last_sil] in word.stress:
                    # Assigna un pes de 0.0 (àtona) a la síl·laba
                    word.stress[word.stress.index(sense_mots[last_sil])].pes = 0.0
                    self.nomes_sillabes[last_sil].pes = 0.0
                    self.patro[last_sil] = 0.0

            # Actualitza els recomptes mètrics i extramètrics
            self.recompte_sillabes_metriques = recompte_metric(self)
            self.recompte_sillabes_extrametriques = len(self.patro) - self.recompte_sillabes_metriques
    except IndexError:
        pass