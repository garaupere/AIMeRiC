"""Un mòdul per gestionar funcions prosòdiques del vers"""
from .meter import recompte_metric

from dataclasses import dataclass
from typing import Optional, List, Tuple, Callable
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

        sillaba.pes = nou_pes
        for word in words:
            if sillaba in word.stress:
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
        if ctx.prev is None or ctx.next is None:
            return False

        curr, next = ctx.curr, ctx.next

        # Només per accents >= BIVALENT (3.0)
        if curr.pes < PesAccent.BIVALENT or next.pes < PesAccent.BIVALENT:
            return False

        word_curr = ctx.get_paraula(curr, words)
        word_next = ctx.get_paraula(next, words)
        word_prev = ctx.get_paraula(ctx.prev, words)

        if not word_curr or not word_next:
            return False

        # Condicions específiques per tipus de paraula
        condicions_desaccentuacio = [
            # ADJ següent
            (word_next.pos_ == "ADJ", curr, next),
            # Complement nominal (nmod + ADP)
            (word_next.dep_ == 'nmod' and word_next.pos_ == 'ADP', curr, next),
            # VERB + ADV/ADJ/NOUN
            (word_curr.pos_ == 'VERB' and word_next.pos_ in ['ADV', 'ADJ', 'NOUN'], curr, next),
            # ADJ + NOUN
            (word_curr.pos_ == 'NOUN' and word_prev and word_prev.pos_ == 'ADJ', ctx.prev, curr),
        ]

        for condicio, sil1, sil2 in condicions_desaccentuacio:
            if condicio and self._evalua_desaccentuacio(ctx, sil1, sil2, words):
                return True

        return False

    def _evalua_desaccentuacio(self, ctx: ContextSillaba, sil1, sil2, words) -> bool:
        """Avalua si cal desaccentuar en un xoc."""
        if sil1.pes > PesAccent.BIVALENT and sil2.pes > PesAccent.LLINDAR_SECUNDARI:
            # Determinar posicions (1-indexed)
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
                    if sil2.pes < PesAccent.LEXIC:
                        self.canvia_pes(ctx, sil1, PesAccent.CIM_MAXIM, words)
                        self.canvia_pes(ctx, sil2, PesAccent.DESACCENTUADA, words)
                        return True

            # Cas per defecte: desaccentuar segons pes
            target = sil1 if sil2.pes >= sil1.pes else sil2
            self.canvia_pes(ctx, target, PesAccent.DESACCENTUADA, words)
            return True
        return False


class ReglaAccentsIntermitjos(ReglaAccent):
    """Regles per a síl·labes entre dues altres."""

    def __init__(self):
        super().__init__("Accents intermitjos", prioritat=80)

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
                self.canvia_pes(ctx, next, PesAccent.ATONA, words)
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
                self.canvia_pes(ctx, curr, PesAccent.ATONA, words)
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

        # Si ambdues són funcionals o lèxiques, desaccentua la de pes més alt
        # (per mantenir el patró rítmic més natural)
        return sil1 if sil2.pes >= sil1.pes else sil2

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
            self.canvia_pes(ctx, target, PesAccent.ATONA, words)
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

        """# Dues desaccentuades abans de forta
        if (prev.pes == PesAccent.DESACCENTUADA and
                curr.pes == PesAccent.DESACCENTUADA and
                next.pes > PesAccent.DESACCENTUADA):
            self.canvia_pes(ctx, prev, PesAccent.SECUNDARI, words)
            canvis = True"""

        if (prev.pes <= PesAccent.DESACCENTUADA
                and curr.pes <= PesAccent.DESACCENTUADA):
            self.canvia_pes(ctx, curr, PesAccent.SECUNDARI, words)
            canvis = True

        # Forta + desaccentuada
        if curr.pes >= PesAccent.LLINDAR_SECUNDARI and next.pes == PesAccent.DESACCENTUADA:
            self.canvia_pes(ctx, next, PesAccent.ATONA, words)
            canvis = True

        # Desaccentuada entre àtones
        if (prev.pes == PesAccent.DESACCENTUADA and
                curr.pes == PesAccent.DESACCENTUADA and
                next.pes < PesAccent.DESACCENTUADA):
            self.canvia_pes(ctx, curr, PesAccent.SECUNDARI, words)
            canvis = True

        # Desaccentuada després d'àtona
        if curr.pes < PesAccent.DESACCENTUADA < next.pes:
            self.canvia_pes(ctx, curr, PesAccent.ATONA, words)
            canvis = True

        # xXx
        if (prev.pes < PesAccent.DESACCENTUADA and
                curr.pes == PesAccent.DESACCENTUADA and
                next.pes < PesAccent.DESACCENTUADA):
            self.canvia_pes(ctx, curr, PesAccent.SECUNDARI, words)
            canvis = True

        # Vall accentual amb paraula bivalent
        if (prev.pes < PesAccent.DESACCENTUADA and
                curr.pes < PesAccent.DESACCENTUADA and
                next.pes < PesAccent.DESACCENTUADA):
            word_curr = ctx.get_paraula(curr, words)
            if word_curr and word_curr.bivalent and word_curr.stress_index == curr.s_index:
                self.canvia_pes(ctx, curr, PesAccent.SECUNDARI, words)
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
        if next.pes != PesAccent.ATONA or nextnext.pes != PesAccent.ATONA:
            return False

        # Si la primera síl·laba ha estat desaccentuada o és àtona
        # i les dues següents són àtones, restaura a accent secundari
        if curr.pes < PesAccent.BIVALENT:  # < 3.0
            if curr.pes == PesAccent.ATONA:
                # Restaura de 0 a 2 (accent secundari)
                self.canvia_pes(ctx, curr, PesAccent.SECUNDARI, words)
                return True
            # Si ja té un accent entre 0.75 i 2.5, el manté (no fa res)
            # Això es gestiona implícitament no canviant-lo

        return False


class GestorAccentsProsodics:
    """Gestiona l'aplicació de regles d'accents prosòdics."""

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.regles: List[ReglaAccent] = []
        self.regles_finals: List = []  # Regles que necessiten accés a la llista completa
        self._inicialitza_regles()

    def _inicialitza_regles(self):
        """Inicialitza i ordena les regles per prioritat."""
        self.regles = [
            ReglaPrimeraSillaba(),
            ReglaUltimaSillaba(),
            ReglaXocAccents(),
            ReglaAccentsIntermitjos(),
            ReglaAccentsSecundaris(),
            ReglaPostProcessament(),
        ]
        self.regles.sort(key=lambda r: r.prioritat, reverse=True)

        # Regles finals que necessiten context addicional
        self.regles_finals = [
            ReglaPrimeraSillabaFinal()
        ]

    def afegeix_regla(self, regla: ReglaAccent):
        """Permet afegir regles personalitzades."""
        self.regles.append(regla)
        self.regles.sort(key=lambda r: r.prioritat, reverse=True)

    def _itera_sillabes(self, sillabes: List) -> ContextSillaba:
        """Genera contextos de síl·labes amb les adjacents."""
        for i in range(len(sillabes)):
            yield ContextSillaba(
                prevprev=sillabes[i - 2] if i > 1 else None,
                prev=sillabes[i - 1] if i > 0 else None,
                curr=sillabes[i],
                next=sillabes[i + 1] if i < len(sillabes) - 1 else None,
                index=i
            )

    def aplica_regles(self, vers):
        """Aplica totes les regles als accents prosòdics del vers."""
        sillabes = vers.nomes_sillabes

        # Primera passada: regles normals
        for ctx in self._itera_sillabes(sillabes):
            if self.debug:
                self._print_debug(ctx)

            for regla in self.regles:
                try:
                    if regla.aplica(ctx, vers.words):
                        if self.debug:
                            print(f"  ✓ Aplicada: {regla.nom}")
                except Exception as e:
                    print(f"Error aplicant regla '{regla.nom}': {e}")

        # Segona passada: regles finals amb accés complet
        for ctx in self._itera_sillabes(sillabes):
            for regla in self.regles_finals:
                try:
                    if hasattr(regla, 'aplica_amb_llista'):
                        if regla.aplica_amb_llista(ctx, vers.words, sillabes):
                            if self.debug:
                                print(f"  ✓ Aplicada (final): {regla.nom}")
                except Exception as e:
                    print(f"Error aplicant regla final '{regla.nom}': {e}")

    def _print_debug(self, ctx: ContextSillaba):
        """Imprimeix informació de debug."""
        print(f"prev: {ctx.prev.text if ctx.prev else None} "
              f"({ctx.prev.pes if ctx.prev else None}), "
              f"curr: {ctx.curr.text} ({ctx.curr.pes}), "
              f"next: {ctx.next.text if ctx.next else None} "
              f"({ctx.next.pes if ctx.next else None})")


def accents_prosodics(self, debug: bool = False):
    """
    Ajusta els accents prosòdics de les síl·labes del vers segons regles específiques.

    Args:
        self: Objecte que conté les síl·labes i paraules del vers.
        debug: Si True, mostra informació de debug.
    """
    gestor = GestorAccentsProsodics(debug=debug)
    gestor.aplica_regles(self)


def cim_maxim(self):
    """Substitutes maximum peaks (>=2) with superior peaks (5) in the last strong syllable of each colon."""
    sense_mots = self.nomes_sillabes
    last_sil = self.objectiu - 1
    try:
        if sense_mots[last_sil].pes > 2.0:
            #for word in self.words:
            if sense_mots[last_sil] in self.words[-1].stress:
                # Substitueix el pes de la síl·laba per 5.0
                self.words[-1].stress[self.words[-1].stress.index(sense_mots[last_sil])].pes = 5.0
                self.nomes_sillabes[last_sil].pes = 5.0
                self.patro[last_sil] = 5.0
            # Si hi ha més síl·labes després de last_sil (possiblement entre 0 i 3)
            if len(sense_mots) > last_sil + 1:
                # Ajusta el pes de la següent síl·laba a 0.0
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
