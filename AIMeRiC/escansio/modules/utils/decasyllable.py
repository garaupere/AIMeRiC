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


def find_tall(self, tall, detect_nonBest: bool = False) -> bool | str:
    """Aquesta funció cerca un tall en un vers donat i en substitueix el pes accentual per un cim màxim (5)."""
    result = False  # Resultat de la cerca
    if self.nomes_sillabes[tall].pes == 5.0:  # Si ja hi ha un tall, retorna'l
        result = True
        return result  # Retorna False
    if int(self.nomes_sillabes[tall].pes) > 2:  # Si el valor correspon a un accent
        next_syllable = self.nomes_sillabes[tall + 1] if tall + 1 < len(self.nomes_sillabes) else None
        if next_syllable:
            if not next_syllable.is_PRONe: # Assegura't que el mot de tall no té un pronom enclític.
                #print(">> TALL:", tall+1, self.no_words[tall].text, ':', self.no_words[tall].pes) # Debug
                if detect_nonBest:
                    if int(self.nomes_sillabes[tall].pes) < 4:  # Si l'accent no és principal
                        return 'not-best'  # Retorna 'not-best' per indicar que no és el millor cas
                for paraula in self.words:  # Recorre les paraules del vers
                    if paraula.stress:
                        if paraula.stress[-1] == self.nomes_sillabes[tall] and self.nomes_sillabes[tall].fusionada is False:  # La síl·laba del tall coincideix amb l'última de la paraula (frontera de mot)
                            paraula.stress[-1].pes = 5.0
                            self.anotat[
                                self.words.index(paraula)] = paraula.stress  # Actualitza l'estructura de l'accentuació
                            self.nomes_sillabes[tall].pes = 5.0  # Actualitza la llista de mots
                            self.patro[tall] = 5  # Actualitza el patró abstracte
                            self.words[self.words.index(paraula)].paraula_tall = True  # Indica que la paraula és frontera de tall
                            self.words[self.words.index(paraula)] = paraula  # Actualitza la paraula
                            result = True  # Indica que s'ha trobat un tall
                            return result  # Retorna True si s'ha trobat un tall
    return result  # Retorna False si no s'ha trobat cap tall


# python
def tall(self) -> int | None:
    """Aquesta funció aplica el tall al vers decasil·làbic."""
    global next_word
    pos = None  # Posició del tall, inicialment None
    if self.recompte_sillabes_metriques == 10:  # Comprova si el vers és un decasíl·lab
        talls = [3, 4, 5]  # Talls més freqüents en el decasíl·lab català (index + 1)
        for i, tall in enumerate(talls):  # Itera pels talls candidats
            # Cerca el tall. Si fallat, passa al següent candidat.
            cerca = find_tall(self, tall, True)
            if cerca is True:  # Si el tall és vàlid
                pos = tall + 1
                return pos if pos != 10 else None  # Evita retornar la darrera posició absoluta
            elif cerca == 'not-best' and i + 1 < len(talls):
                # Si no és l'opció millor, però es poden cercar més talls
                cerca = find_tall(self, talls[i + 1], True)
                if cerca is True:  # Si el següent tall és vàlid
                    next_syllable = self.nomes_sillabes[talls[i + 1] + 1] if talls[i + 1] + 1 < len(self.nomes_sillabes) else None
                    # comprova el mot següent al tall
                    for word in self.words:
                        if self.nomes_sillabes[tall] in word.stress:
                            next_word = self.words[word.w_index + 1] if word.w_index + 1 < len(self.words) else None
                    if next_word:
                        if next_word.pos_ in ["NOUN", "VERB", "ADJ", "ADV", "PROPN"]:
                            return None # Evita talls que impliquen situar un cim màxim en un mot semitònic si després ve un mot tònic (que li guanya l'accent).
                    if next_syllable and not next_syllable.is_PRONe:  #
                        pos = talls[i + 1] + 1
                        return pos if pos != 10 else None

        # Si arriba aquí, no hi ha talls clars; intenta-ho amb mots bivalents
        for tall in talls:
            cerca = find_tall(self, tall)  # Cerca el tall sense condició de millor opció
            if cerca is True:
                # obté la següent paraula i comprova si és un mot tònic
                for word in self.words:
                    if self.nomes_sillabes[tall] in word.stress:
                        next_word = self.words[word.w_index + 1] if word.w_index + 1 < len(self.words) else None
                        if next_word:
                            if next_word.pos_ in ["NOUN", "VERB", "ADJ", "ADV", "PROPN"]:
                                pos = None  # Evita talls que impliquen situar un cim màxim en un mot semitònic si després ve un mot tònic (que li guanya l'accent).
                            else:
                                pos = tall + 1
            return pos if pos != 10 else None
    # Retorna None si no es compleix cap condició o el vers no és decasíl·lab
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
                                fsubs = split_syllable(seguent(syllable, word.stress))
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
