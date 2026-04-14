"""Un mòdul per a l'assignació de l'accent de les paraules"""
import re
from copy import deepcopy

from AIMeRiC.escansio.modules.sillaba import Sillaba


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


def identifica_pronom_assillabic(syllables):
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


def accentua(self):
    """Aquesta funció retorna la paraula amb l'accentuació"""
    stressed = self.syllables.copy()
    clean = identifica_pronom_assillabic(stressed)
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
                return [Sillaba(0, w_ment[0], 2), Sillaba(1, w_ment[1], 2)]

            return [Sillaba(0, result[0], 1)]

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
    result = [Sillaba(num, syllable, len(result)) for num, (syllable) in enumerate(result)]

    if clean:
        result[-1].text = result[-1].text + pronoun
    return result


def accent_secundari(self) -> list:
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

        result[i] = Sillaba(i, (syllable.text, new_weight), len(self.stress))

    self.stress = result
    return result


def get_index_accent(self):
    for i, syllable in enumerate(self.stress):
        if syllable.pes > 2.0:
            stress_index = i
            return stress_index
        elif self.monosyllabic():
            return 0
    return None
