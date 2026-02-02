"""Un mòdul per a l'assignació de l'accent de les paraules"""
import re
from copy import deepcopy

from AIMeRiC.escansio.modules.syllable import Syllable


def bivalents(result, cat):
    """Assigna un accent especial per a mots bivalents segons la seva categoria gramatical.
    Args:
        result (list): Llista de tuples (síl·laba, pes).
        cat (str): Categoria gramatical del mot.
    Returns:
        list: Llista de tuples (síl·laba, pes) amb l'accentuació ajustada.
        """
    for syllable in result:
        if syllable[1] == 4.0: # Només modifica la síl·laba amb accent primari
            if cat in ["AUX", "NUM", "PRON", "PRONe", "INTJ", "ADP"]: # Categories amb accent bivalent (3)
                o_syllable = syllable
                syllable = (syllable[0], 3.0) # Canvia l'accent primari (4) per un accent bivalent (3)
                result[result.index(o_syllable)] = syllable
            if cat in ['ADPa', 'DET', 'CCONJ', 'SCONJ']: # Categories amb accent secundari (2)
                o_syllable = syllable
                syllable = (syllable[0], 2.0) # Canvia l'accent primari (4) per un accent secundari (2)
                result[result.index(o_syllable)] = syllable
        else: # Les altres síl·labes esdevenen àtones (0)
            o_syllable = syllable
            syllable = (syllable[0], 0.0) # Assegura que és una síl·laba àtona (0)
            result[result.index(o_syllable)] = syllable
    return result


def identify_pronom_assillabic(syllables):
    """Identifica si la darrera síl·laba conté un pronom assil·làbic i el separa.
    Args:
        syllables (list): Llista de síl·labes d'una paraula.
    Returns:
        tuple: Llista de síl·labes sense el pronom assil·làbic i el pronom separat, o None si no n'hi ha.
        """
    if syllables and "'" in syllables[-1]:
        for pronoun in ["'t", "'s", "'m", "'n", "'l", "'ls", "'ns"]:
            if pronoun in syllables[-1]:
                pronoun = "'" + ''.join(syllables[-1].split("'")[1:])
                syllables[-1] = syllables[-1].split("'")[0]
                return syllables, pronoun


def get_stress(self):
    """Aquesta funció retorna la paraula amb l'accentuació.
    Segons les regles de l'accentuació catalana:
    - Paraules amb accent gràfic: la síl·laba amb accent rep un pes de 4.0, la resta 0.0.
    - Paraules sense accent gràfic:
        - Monosíl·labes: pes 1.0.
        - Paraules amb dues o més síl·labes:
            - Si acaba en vocal, 's' o diftong ascendent: paraula aguda (última síl·laba 4.0, penúltima 0.0).
            - En cas contrari: paraula plana (penúltima síl·laba 4.0, última 0.0).
    - Mots bivalents: ajusta l'accent segons la categoria gramatical
    Returns:
        list: Llista de Syllable amb l'accentuació assignada.
    """
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
        result = [(syllable, 4.0) if re.findall(accents, syllable) else (syllable, 0.0) for syllable in stressed]
        if self.is_bivalent():
            result = bivalents(result, self.pos_)

    else:
        """Si el mot no conté accents gràfics"""
        if n == 1:
            """Si el mot és monosíl·lab"""
            result = self.monosyllabic()
            if self.word_ment is not None:
                w_ment = result + [("ment", 4.0)]
                w_ment = forced_rhythmic_alternation(self, w_ment)
                return [Syllable(0, syllable=w_ment[0], len_word=2), Syllable(1, syllable=w_ment[1], len_word=2)]
            return [Syllable(0, syllable=result[0], len_word=1)]

        elif n >= 2:
            """Si el mot té dues o més de dues síl·labes"""
            if bool(re.search(oxytone_ending, stressed[-1])):
                result = [(stressed[-2], 0.0), (stressed[-1], 4.0)]  # Paraula aguda
            else:
                result = [(stressed[-2], 4.0), (stressed[-1], 0.0)]  # Paraula plana
            result = [(syllable, 0.0) for syllable in stressed[:-2]] + result  # La resta de síl·labes àtones
            if self.is_bivalent():
                result = bivalents(result, self.pos_)
    if self.word_ment is not None:
        result = [(syllable[0], 2.0) if syllable[1] == 4.0 else (syllable[0], 0.0) for syllable in result]
        result = result + [("ment", 4.0)]
        result = forced_rhythmic_alternation(self, result)
    result = [Syllable(num, syllable, len(result)) for num, (syllable) in enumerate(result)]

    if clean:
        result[-1].text = result[-1].text + pronoun
    return result


def secondary_stress(self):
    """
        Assigna un accent secundari (2) a la síl·laba que està 2 posicions abans de la síl·laba amb l'accent primari (>1).
        A partir de les regles d'Oliva (1992).
    """
    if not self.is_compost:
        if len(self.syllables) > 2 and 'des' in self.stress[0].text.lower():
            self.stress[0] = Syllable(0, (self.stress[0].text, 2.0), len_word=len(self.stress))

        if self.word_ment is not None:
            result = deepcopy(self.stress)[:-1]
            result_end = deepcopy(self.stress)[-1]
        else:
            result = deepcopy(self.stress)
            result_end = None

        index_accent_primari = None
        for i, syl in enumerate(result):
            if syl.pes > 0:
                index_accent_primari = i
                break
        if index_accent_primari is None:
            return result + [result_end] if self.word_ment is not None else result

        posicio_actual = index_accent_primari - 2
        while posicio_actual >= 0:
            syll = result[posicio_actual]
            result[posicio_actual] = Syllable(posicio_actual, (syll.text, 2.0), len_word=len(self.stress))
            posicio_actual -= 2

        if len(self.stress) > 2 and index_accent_primari < 3:
            posicio_actual = index_accent_primari + 2
            while posicio_actual < len(result):
                syll = result[posicio_actual]
                if syll.pes < 2.0:
                    result[posicio_actual] = Syllable(posicio_actual, (syll.text, 2), len_word=len(self.stress))
                posicio_actual += 2

        self.stress = result + [result_end] if self.word_ment is not None else result


def forced_rhythmic_alternation(self, stressed):
    resta = stressed
    result = []
    if len(stressed) >= 2:
        if stressed[-2][1] > 1.0 and stressed[-1][1] > 1.0:
            result = [(stressed[-2][0], 0.25), (stressed[-1][0], 4.0)]
            resta = [(syllable[0], 0.0) for syllable in stressed[:-2]]
        elif stressed[-2][1] <= 1.0 and stressed[-1][1] <= 1.0:
            result = [(stressed[-2][0], 4.0), (stressed[-1][0], 1.0)]
            resta = [(syllable[0], 0.0) for syllable in stressed[:-2]]
    return resta + result


def get_stress_index(self):
    for i, syllable in enumerate(self.stress):
        if syllable.pes > 2.0:
            stress_index = i
            return stress_index
        elif self.monosyllabic():
            return 0
