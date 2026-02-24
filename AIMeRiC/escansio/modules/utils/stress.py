"""Un mòdul per a l'assignació de l'accent de les paraules"""
import re
from copy import deepcopy

from AIMeRiC.escansio.modules.syllable import Syllable


def bivalents(result, cat):
    """Identifica els mots bivalents i assigna el nivell accentual corresponent segons la categoria gramatical"""
    secondary = ["ADPa", "DET", 'CCONJ', 'SCONJ']
    semitonics = ["AUX", "NUM", "PRON", "PRONe", "INTJ", "ADP"]
    for syllable in result:
        if syllable[1] == 4.0:
            if cat in semitonics:
                if cat == 'PRONe':
                    o_syllable = syllable
                    syllable = (syllable[0], 2.5)
                    result[result.index(o_syllable)] = syllable
                elif cat == 'AUX':
                    o_syllable = syllable
                    syllable = (syllable[0], 3.5)
                    result[result.index(o_syllable)] = syllable
                else:
                    o_syllable = syllable
                    syllable = (syllable[0], 3.0)
                    result[result.index(o_syllable)] = syllable
            elif cat in secondary:
                o_syllable = syllable
                syllable = (syllable[0], 2.0)
                result[result.index(o_syllable)] = syllable
        else:
            o_syllable = syllable
            syllable = (syllable[0], 0.0)
            result[result.index(o_syllable)] = syllable
    return result


def identify_pronom_assillabic(syllables):
    if syllables and "'" in syllables[-1]:
        for pronoun in ["'t", "'s", "'m", "'n", "'l", "'ls", "'ns"]:
            if pronoun in syllables[-1]:
                pronoun = "'" + ''.join(syllables[-1].split("'")[1:])
                syllables[-1] = syllables[-1].split("'")[0]
                return syllables, pronoun


def resol_xoc_ment(paraula) -> list:
    """Aquesta funció resol els casos de xoc entre el sufix -ment i l'accent de la paraula"""
    if len(paraula) > 1:
        if paraula[-2][1] > 0:
            paraula[-2] = (paraula[-2][0], 0)
    return paraula


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
        r"[aeioïüy][ui]$|"  # Diftongs ascendents. # excepte grup ui final
        r"[^qg]u[ui]$|"  # Diftongs ascendents amb <qu>, <gu>. # evita detectar mots tipus tengui, detecta mots tipus avui
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
                w_ment = resol_xoc_ment(w_ment)
                return [Syllable(0, w_ment[0], 2), Syllable(1, w_ment[1], 2)]

            return [Syllable(0, result[0], 1)]

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
        result = resol_xoc_ment(result)
        self.stress = result
        #result = forced_rhythmic_alternation(self)
    result = [Syllable(num, syllable, len(result)) for num, (syllable) in enumerate(result)]

    if clean:
        result[-1].text = result[-1].text + pronoun
    return result


def secondary_stress(self):
    """
        Assigna un accent secundari (2) a la síl·laba que està 2 posicions abans de la síl·laba amb l'accent primari (>1).
        A partir de les regles d'Oliva (1992). ACTUALMENT NO S'APLICA: COSTÓS I POC EXHAUSTIU.
    """
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
                    result[posicio_actual] = Syllable(posicio_actual, (syll.text, 1.5), len_word=len(self.stress))
                posicio_actual += 2

        self.stress = result + [result_end] if self.word_ment is not None else result"""
    pass


def forced_rhythmic_alternation(self) -> list:
    """
    Alternança rítmica al llarg de tot el mot a partir de l'accent primari, amb asimetria:
      - esquerra del primari: secundari = 2.0
      - dreta del primari:   secundari = 1.5
      - distància senar (1,3,5,...) sempre 0.0
      - el primari (pes > 2.0) es manté
    """
    result = deepcopy(self.stress)

    # Trobar l'índex de l'accent primari
    idx_primary = None
    for i, syllable in enumerate(result):
        if syllable.pes > 2.0:
            idx_primary = i
            break

    if idx_primary is None:
        self.stress = result
        return result

    for i, syllable in enumerate(result):
        if i == idx_primary:
            continue  # mantenim el primari

        dist = abs(i - idx_primary)

        if dist % 2 == 1:
            new_weight = 0.0
        else:
            # distància parella: secundari
            if i < idx_primary:
                new_weight = 2.0
            else:
                new_weight = 1.5

        result[i] = Syllable(i, (syllable.text, new_weight), len(self.stress))

    self.stress = result
    return result

def aforced_rhythmic_alternation(self):
    resta = self.stress
    stressed = self.stress
    result = []
    if len(stressed) >= 2:
        if stressed[-2].pes > 1.0 and stressed[-1].pes > 1.0:
            #result = [(stressed[-2][0], 0.25), (stressed[-1][0], 4.0)]
            result = [Syllable(stressed[-2].s_index, (stressed[-2].text, 0.25), len(stressed)),
                      Syllable(stressed[-1].s_index, (stressed[-1].text, 4.0), len(stressed))]
            #resta = [(syllable[0], 0.0) for syllable in stressed[:-2]]
            resta = [Syllable(syllable.s_index, (syllable.text, 0.0), len(stressed)) for syllable in stressed[:-2]]
        elif stressed[-2].pes <= 1.0 and stressed[-1].pes <= 1.0:
            #result = [(stressed[-2][0], 4.0), (stressed[-1][0], 1.0)]
            result = [Syllable(stressed[-2].s_index, (stressed[-2].text, 4.0), len(stressed)),
                      Syllable(stressed[-1].s_index, (stressed[-1].text, 1.0), len(stressed))]
            #resta = [(syllable[0], 0.0) for syllable in stressed[:-2]]
            resta = [Syllable(syllable.s_index, (syllable.text, 0.0), len(stressed)) for syllable in stressed[:-2]]
    return resta + result


def get_stress_index(self):
    for i, syllable in enumerate(self.stress):
        if syllable.pes > 2.0:
            stress_index = i
            return stress_index
        elif self.monosyllabic():
            return 0
    return None
