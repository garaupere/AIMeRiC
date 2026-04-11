"""
Resum
Aquest mòdul gestiona particularitats mètriques del decasíl·lab en el procés d'escansió: detecta i aplica el `tall`, calcula la subdivisió del vers i inclou una funció en desenvolupament per la cesura femenina.

## Dependències
- Mòduls interns:
  - `AIMeRiC.escansio.modules.utils.fonetica_sintactica.split_syllable`
  - `AIMeRiC.escansio.modules.utils.tools.seguent`
- Llibreria estàndard: `re`

## Propòsit
Proporcionar utilitats per:
- identificar la posició del tall en versos decasíl·labs,
- marcar la síl·laba de tall amb pes màxim (5.0),
- obtenir la subdivisió en còlons (`5+5`, etc.),
- gestionar casos especials de cesura femenina (funció en desenvolupament).
"""

import re

from .fonetica_sintactica import split_syllable
from .tools import seguent


def troba_tall_posible(self, tall, detect_nonBest: bool = False) -> str:
    """
    Avalua si una posició podria ser un tall. NO modifica res!
    Retorna 'best' si és òptim, 'not-best' si és alternatiu, 'invalid' si no serveix.
    """
    # Si ja ha estat assignat pes de tall, no és vàlid
    if self.nomes_sillabes[tall].pes == 5.0:
        return 'invalid'

    word_at_tall = _get_word_at_position(self, tall)

    # -- NOVETAT: La síl·laba no pot ser tall si NO és l'última de la paraula --
    es_ultima_de_mot = False
    for paraula in self.words:
        if paraula.stress and paraula.stress[-1] == self.nomes_sillabes[tall] and self.nomes_sillabes[
            tall].fusionada is False and paraula.has_PRONe is False and tall != 10:
            es_ultima_de_mot = True
            break
    if not es_ultima_de_mot:
        return 'invalid'
    # -- FI NOVETAT --

    if self.nomes_sillabes[tall].pes > 2:
        if not word_at_tall.has_PRONe:
            if detect_nonBest:
                if 4 > self.nomes_sillabes[tall].pes > 2:
                    return 'not-best'
            return 'best'
    return 'invalid'


def aplica_tall(self, tall):
    """
    Aplica efectivament el tall (pes=5.0, marques) a la posició indicada.
    Retorna True si s'ha aplicat, False si no s'han complert les condicions.
    """
    word_at_tall = _get_word_at_position(self, tall)

    # Comprovacions de seguretat: la síl·laba ha de ser l'última de la paraula,
    # no estar fusionada i la paraula no haver de pronom enclític.
    if not word_at_tall:
        return False

    syl = self.nomes_sillabes[tall]
    if not getattr(syl, 'fusionada', False) and word_at_tall.stress and word_at_tall.stress[-1] == syl and not getattr(word_at_tall, 'has_PRONe', False):
        word_at_tall.stress[-1].pes = 5.0
        # actualitzem anotacions i patró
        try:
            self.anotat[self.words.index(word_at_tall)] = word_at_tall.stress
        except Exception:
            pass
        syl.pes = 5.0
        try:
            self.patro[tall] = 5
        except Exception:
            # patro podria ser més curt; ignorem si no existeix
            pass
        word_at_tall.paraula_tall = True
        # assegurem la coherència en la llista
        try:
            self.words[self.words.index(word_at_tall)] = word_at_tall
        except Exception:
            pass
        return True

    return False


def tall(self) -> int | None:
    """Aplica el tall mètric segons criteris prioritaris, evitant assignació prematura."""
    if self.recompte_sillabes_metriques != 10:
        return None

    talls = [3, 5, 4]  # Preferències de talls

    # === PRIMERA PASSADA: 'best' ===
    for tall_actual in talls:
        result = troba_tall_posible(self, tall_actual, True)
        if result == 'best':
            pos = tall_actual + 1
            aplica_tall(self, tall_actual)
            return pos

    # === SEGONA PASSADA: 'not-best'/alternatius ===
    for tall_actual in talls:
        result = troba_tall_posible(self, tall_actual, False)
        if result == 'not-best':
            pos = tall_actual + 1
            word_at_tall = _get_word_at_position(self, tall_actual)
            next_word = _get_next_word_at_position(self, tall_actual)
            if word_at_tall and next_word:
                if (word_at_tall.pos_ in ["NOUN", "VERB", "PRON", "ADJ", "PROPN"] and
                        next_word.pos_ in ["VERB"]):
                    aplica_tall(self, tall_actual)
                    return pos
                elif next_word.pos_ in ["NOUN", "VERB", "ADJ", "ADV", "PROPN"]:
                    continue
                else:
                    aplica_tall(self, tall_actual)
                    return pos
            else:
                aplica_tall(self, tall_actual)
                return pos
    return None  # No s'ha trobat tall vàlid


def _get_word_at_position(self, pos: int):
    """Retorna la paraula que conté la síl·laba a la posició donada."""
    if pos >= len(self.nomes_sillabes):
        return None

    for word in self.words:
        if self.nomes_sillabes[pos] in word.stress:
            return word
    return None


def _get_next_word_at_position(self, pos: int):
    """Retorna la paraula següent a la que conté la síl·aba a la posició donada."""
    word_at_pos = _get_word_at_position(self, pos)

    if word_at_pos and word_at_pos.w_index + 1 < len(self.words):
        return self.words[word_at_pos.w_index + 1]
    return None


def subdivideix(self):
    """Aquesta funció subdivideix el vers en còlons si conté un tall.

    Observacions i millores aplicades:
    - Si `self.posicio_tall` no existeix (o és None), intentem obtenir-la cridant
      `tall(self)` i l'assignem explícitament. Això evita que `subdivideix` retornï
      sempre `None` quan abans no s'hagi calculat el tall.
    - Fem comprovacions robustes dels tipus (int) i del recompte de síl·labes
      mètriques abans de fer l'operació aritmètica.
    - Si no es pot determinar el recompte mètric, retornem una cadena indicativa
      en lloc de llançar una excepció.
    """
    # Intentem usar l'atribut existent
    pos = getattr(self, 'posicio_tall', None)

    # Si no existeix, provem de calcular-lo cridant tall(self)
    if pos is None:
        try:
            pos = tall(self)
        except Exception:
            pos = None
        # Assignem si l'hem obtingut
        if pos is not None:
            self.posicio_tall = pos
        else:
            return None

    # Assegurem-nos que és un enter vàlid
    try:
        pos_int = int(pos)
    except Exception:
        return None

    # Obtenim el recompte de síl·labes mètriques (int) de forma segura
    recompte = getattr(self, 'recompte_sillabes_metriques', None)
    if recompte is None:
        # Intentem recalcular-lo sense importar la dependència exterior si ja existeix
        try:
            from AIMeRiC.escansio.modules.utils.metre import recompte_metric
            recompte = recompte_metric(self)
            self.recompte_sillabes_metriques = recompte
        except Exception:
            # No podem obtenir el recompte, retornem una forma parcial
            return f'{pos_int}+?'

    try:
        right = int(recompte) - pos_int
    except Exception:
        return f'{pos_int}+?'

    return f'{pos_int}+{right}'


def cesura_femenina(self):
    """Aquesta funció aplica la cesura femenina al vers. [FUNCIÓ EN DESENVOLUPAMENT, INACTIVA]"""
    if len(self.sillables_metriques) == 11:
        # if len(re.findall("[_:]", ''.join([x.text for x in self.no_words[4:6]]))) < 0:
        if int(self.nomes_sillabes[4].pes) >= 4:
            for word in self.words:
                for syllable in word.stress:
                    if syllable == self.nomes_sillabes[4]:
                        if seguent(syllable, word.stress) is not None:
                            if re.findall("[:_]", seguent(syllable, word.stress).text):
                                # Gestiona els casos de sinalefa en la cesura, ex.: *jo som la page<sa_amb> els records honrats
                                fsubs = split_syllable(self, seguent(syllable, word.stress))
                                syl1 = fsubs[0]
                                syl2 = fsubs[1]
                                word.stress[syllable.s_index + 1] = syl1
                                self.words[word.w_index + 1].stress.insert(0, syl2)
                                break
                            syllable.pes = 5.0
                            self.nomes_sillabes[4].pes = 5.0
                            self.patro[4] = 5
                            ignore_syll = word.stress[word.stress.index(syllable) + 1]
                            del word.stress[word.stress.index(syllable) + 1:]
                            self.actualitza()
                            self.subdivisio = "5'+5"
                            self.string = '#'.join(
                                ['.'.join([syllable.text for syllable in word.stress]) for word in
                                 self.words[:word.w_index + 1]]) + ".<" + ignore_syll.text + '>#' + '#'.join(
                                ['.'.join([syllable.text for syllable in word.stress]) for word in
                                 self.words[word.w_index + 1:]])
                            self.escansio_text = '#'.join(
                                [word.plain() for word in
                                 self.words[:word.w_index + 1]]) + ".<" + ignore_syll.text + '>#' + '#'.join(
                                [word.plain() for word in self.words[word.w_index + 1:]])
