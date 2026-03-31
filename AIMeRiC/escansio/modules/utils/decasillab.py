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


def troba_tall(self, tall, detect_nonBest: bool = False) -> bool | str:
    """Aquesta funció cerca un tall en un vers donat i en substitueix el pes accentual per un cim màxim (5)."""

    result = False  # Resultat de la cerca
    if self.nomes_sillabes[tall].pes == 5.0:  # Si ja hi ha un tall, retorna'l
        result = True
        return result  # Retorna False

    word_at_tall = _get_word_at_position(self, tall)

    if self.nomes_sillabes[tall].pes > 2:  # Si el valor correspon a un accent

        if not word_at_tall.has_PRONe:  # Assegura't que el mot de tall no té un pronom enclític ni és una síl·laba fusionada

            if detect_nonBest:

                if 4 > self.nomes_sillabes[tall].pes >= 3:  # Si l'accent no és principal

                    return 'not-best'  # Retorna 'not-best' per indicar que no és el millor cas

            for paraula in self.words:  # Recorre les paraules del vers
                if paraula.stress:
                    if paraula.stress[-1] == self.nomes_sillabes[tall] and self.nomes_sillabes[
                        tall].fusionada is False:  # La síl·laba del tall coincideix amb l'última de la paraula (frontera de mot)
                        paraula.stress[-1].pes = 5.0
                        self.anotat[
                            self.words.index(paraula)] = paraula.stress  # Actualitza l'estructura de l'accentuació
                        self.nomes_sillabes[tall].pes = 5.0  # Actualitza la llista de mots
                        self.patro[tall] = 5  # Actualitza el patró abstracte
                        self.words[self.words.index(
                            paraula)].paraula_tall = True  # Indica que la paraula és frontera de tall
                        self.words[self.words.index(paraula)] = paraula  # Actualitza la paraula
                        result = True  # Indica que s'ha trobat un tall

                        return result  # Retorna True si s'ha trobat un tall
    return result  # Retorna False si no s'ha trobat cap tall


def tall(self) -> int | None:
    """Aquesta funció aplica el tall al vers decasil·làbic."""

    if self.recompte_sillabes_metriques != 10:
        return None  # No és un decasíl·lab

    talls = [3, 5, 4]  # Talls més freqüents en el decasíl·lab català

    # PRIMERA PASSADA: Cerca talls amb best=True
    i = 0
    while i < len(talls):
        tall_actual = talls[i]
        cerca = troba_tall(self, tall_actual, True)
        if cerca is True:
            # Tall vàlid trobat
            pos = tall_actual + 1
            return pos if pos != 10 else None

        elif cerca == 'not-best' and i < len(talls):
            # No és el millor tall, prova el següent
            cerca_nonBest = troba_tall(self, tall_actual, False)

            if cerca_nonBest is True:

                # Evita talls amb mot tònic després
                #if next_word and next_word.pos_ in ["NOUN", "VERB", "ADJ", "ADV", "PROPN"]:
                #    return None
                word_at_tall = _get_word_at_position(self, tall_actual)
                if not word_at_tall.has_PRONe: # Assegura't que el mot de tall no té un pronom enclític
                    pos = tall_actual + 1
                    return pos if pos != 10 else None

        i += 1  # Passa al següent tall candidat

    # SEGONA PASSADA: Cerca talls amb mots bivalents (best=False)
    i = 0
    while i < len(talls):
        tall_actual = talls[i]
        cerca = troba_tall(self, tall_actual, False)
        if cerca is True:
            word_at_tall = _get_word_at_position(self, tall_actual)
            next_word = _get_next_word_at_position(self, tall_actual)

            if word_at_tall and next_word:
                # Cas especial: NOUN/VERB/PRON/ADJ/PROPN + VERB
                if (word_at_tall.pos_ in ["NOUN", "VERB", "PRON", "ADJ", "PROPN"]
                        and next_word.pos_ in ["VERB"]):
                    pos = tall_actual + 1
                    return pos if pos != 10 else None

                # Evita talls amb mot tònic després
                elif next_word.pos_ in ["NOUN", "VERB", "ADJ", "ADV", "PROPN"]:
                    i += 1  # Continua cercant
                    continue

                else:
                    pos = tall_actual + 1
                    return pos if pos != 10 else None

        i += 1  # Passa al següent tall candidat

    return None  # No s'ha trobat cap tall vàlid


def _get_word_at_position(self, pos: int):
    """Retorna la paraula que conté la síl·laba a la posició donada."""
    if pos >= len(self.nomes_sillabes):
        return None

    for word in self.words:
        if self.nomes_sillabes[pos] in word.stress:
            return word
    return None


def _get_next_word_at_position(self, pos: int):
    """Retorna la paraula següent a la que conté la síl·laba a la posició donada."""
    word_at_pos = _get_word_at_position(self, pos)

    if word_at_pos and word_at_pos.w_index + 1 < len(self.words):
        return self.words[word_at_pos.w_index + 1]
    return None


def subdivideix(self):
    """Aquesta funció subdivideix el vers en còlons si conté un tall."""
    return f'{self.posicio_tall}+{self.recompte_sillabes_metriques - self.posicio_tall}' if self.posicio_tall is not None else None


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
