"""Un mòdul per a l'assignació de l'accent de les paraules"""
import re
from copy import deepcopy

from AIMeRiC.escansio.modules.syllable import Syllable


def bivalents(result, cat):
    for syllable in result:
        if syllable[1] == "4":
            if cat in ["AUX", "NUM", "PRON", "PRONe", "INTJ", "ADP"]:
                o_syllable = syllable
                syllable = (syllable[0], "3")
                result[result.index(o_syllable)] = syllable
            if cat in ['ADPa', 'DET', 'CCONJ', 'SCONJ']:
                o_syllable = syllable
                syllable = (syllable[0], "2")
                result[result.index(o_syllable)] = syllable
        else:
            o_syllable = syllable
            syllable = (syllable[0], "0")
            result[result.index(o_syllable)] = syllable
    return result


def identify_pronom_assillabic(syllables):
    if syllables and "'" in syllables[-1]:
        for pronoun in ["'t", "'s", "'m", "'n", "'l", "'ls", "'ns"]:
            if pronoun in syllables[-1]:
                pronoun = "'" + ''.join(syllables[-1].split("'")[1:])
                syllables[-1] = syllables[-1].split("'")[0]
                return syllables, pronoun


def get_stress(self):
    """Aquesta funció retorna la paraula amb l'accentuació"""
    stressed = self.syllables.copy()
    clean = identify_pronom_assillabic(stressed)
    if clean:
        stressed, pronoun = clean
    else:
        pronoun = ""

    result = []
    oxytone_ending = re.compile(
        r"(?:[àáèéíìóòúùâêîôûý]|"  # Vocals accentuades.
        r"[aeiouïüy][ui]$|"  # Diftongs ascendents.
        r"[aouïü][^'aeiuos]+|"  # Vocals (a, o, u) + consonants excepte <s>.
        r"[^qg]?[aouïü][^aeouïü][^aouïüs]|"  # Vocals (a, o, u) + consonants  + consonant (tipus: rebost).
        r"[eiy]([^'aeiuons]|[^'aeiuo]+[^'aeiuo])|"  # Vocals (e, i) + consonants, excepte <s> i  <en>, <in>.
        r"[^qg][aeiou][iu]s)"  # vocal + i/u + s (maqueis, belais, antiherois, etc.)
        r"s?(?:$|-')"  # s opcional + final o guionet.
    )

    accents = re.compile("[àáèéíìóòúù]")

    if self.word_ment is not None:
        stressed = self.word_ment

    n = len(stressed)  # Número de síl·labes
    if re.search(accents, self.text):
        """Si el mot conté accents gràfics"""
        result = [(syllable, "4") if re.findall(accents, syllable) else (syllable, "0") for syllable in stressed]
        if self.is_bivalent():
            result = bivalents(result, self.upos)

    else:
        """Si el mot no conté accents gràfics"""
        if n == 1:
            """Si el mot és monosíl·lab"""
            result = self.monosyllabic()
            if self.word_ment is not None:
                w_ment = result + [("ment", "4")]
                w_ment = forced_rhythmic_alternation(self, w_ment)
                return [Syllable(0, w_ment[0], 1), Syllable(1, w_ment[1], 4)]
            return [Syllable(0, result[0], 1)]

        elif n >= 2:
            """Si el mot té dues o més de dues síl·labes"""
            if bool(re.search(oxytone_ending, stressed[-1])):
                result = [(stressed[-2], "0"), (stressed[-1], "4")]  # Paraula aguda
            else:
                result = [(stressed[-2], "4"), (stressed[-1], "0")]  # Paraula plana
            result = [(syllable, "0") for syllable in stressed[:-2]] + result  # La resta de síl·labes àtones
            if self.is_bivalent():
                result = bivalents(result, self.upos)
    if self.word_ment is not None:
        result = [(syllable[0], "2") if syllable[1] == "4" else (syllable[0], "0") for syllable in result]
        result = result + [("ment", "4")]
        result = forced_rhythmic_alternation(self, result)
    result = [Syllable(num, syllable, len(result)) for num, (syllable) in enumerate(result)]

    if clean:
        result[-1].text = result[-1].text + pronoun
    return result


def secondary_stress(self):
    """
        Assigna un accent secundari (2) a la síl·laba que està 2 posicions abans de la síl·laba amb l'accent primari (>1).
        A partir de les regles d'Oliva (1992).

        :param mot: Llista de tuples, on cada tuple conté una síl·laba i el seu pes (ex. [("re", 0), ("cor", 0), ("dar", 4)])
        :return: Llista de tuples amb l'accent secundari assignat (ex. [("re", 2), ("cor", 0), ("dar", 4)])
        """

    if not self.is_compost:
        if self.word_ment is not None:  # Si el mot té un sufix -ment, eliminam aquest sufix per a l'assignació de l'accent secundari
            result = deepcopy(self.stress)[:-1]  # Eliminam l'última síl·laba (el sufix -ment)
            result_end = deepcopy(self.stress)[-1]  # Guardam l'última síl·laba (el sufix -ment)
        else:  # Si no té sufix -ment, mantenim el mot tal com està
            result = deepcopy(self.stress)  # Copiam el mot
            result_end = None  # No hi ha sufix -ment

        index_accent_primari = None  # Índex de la primera síl·laba amb accent primari
        for i, syl in enumerate(result):  # Cercam la primera síl·laba amb accent primari
            if int(syl.pes) > 1:  # Si la síl·laba té accent primari
                index_accent_primari = i  # Guardam la posició de la síl·laba amb accent primari
                break  # Sortim del bucle
        # Si no hi ha accent primari o no hi ha suficients síl·labes abans, retornam el mot sense canvis
        if index_accent_primari is None:  # or index_accent_primari < 2:
            return result + [
                result_end] if self.word_ment is not None else result  # Retornam el mot sense canvis

        # Assignam els accents secundaris a totes les posicions vàlides (x-2, x-4, ...)
        posicio_actual = index_accent_primari - 2  # Posició actual
        while posicio_actual >= 0:  # Mentre la posició actual sigui vàlida
            syll = result[posicio_actual]  # Síl·laba actual
            result[posicio_actual] = Syllable(posicio_actual, (syll.text, "2"),
                                              len_word=len(self.stress))  # Assignam l'accent secundari
            posicio_actual -= 2  # Continuam amb la següent posició vàlida (x-4, x-6...)

        # Assignam l'accent secundari als mots esdrúixols: accents binaris a la dreta de l'accent primari (Oliva, 1992: 74)
        if len(self.stress) > 2 and index_accent_primari < 3:  # Si el mot és esdrúixol
            posicio_actual = index_accent_primari + 2  # Posició actual
            while posicio_actual < len(result):  # Mentre la posició actual sigui vàlida
                syll = result[posicio_actual]
                if int(syll.pes) < 2:
                    result[posicio_actual] = Syllable(posicio_actual, (syll.text, "1"),
                                                      len_word=len(
                                                          self.stress))  # Assignam l'accent secundari (+dèbil)
                posicio_actual += 2  # Continuam amb la següent posició vàlida (x+4, x+6...)

        self.stress = result + [
            result_end] if self.word_ment is not None else result  # Actualitzam el mot amb els accents secundaris assignats (i el sufix -ment si n'hi ha)


def forced_rhythmic_alternation(self, stressed):
    """Aplica el PAR forçat als casos d'accents secundaris"""
    resta = stressed
    result = []
    if len(stressed) >= 2:
        if int(stressed[-2][1]) > 1 and int(stressed[-1][1]) > 1:
            result = [(stressed[-2][0], "1"), (stressed[-1][0], "4")]
            resta = [(syllable[0], "0") for syllable in stressed[:-2]]
        elif int(stressed[-2][1]) <= 1 and int(stressed[-1][1]) <= 1:
            result = [(stressed[-2][0], "4"), (stressed[-1][0], "1")]
            resta = [(syllable[0], "0") for syllable in stressed[:-2]]
    return resta + result


def get_stress_index(self):
    for i, syllable in enumerate(self.stress):
        if int(syllable.pes) > 2:
            stress_index = i
            return stress_index
        elif self.monosyllabic():
            return 0

