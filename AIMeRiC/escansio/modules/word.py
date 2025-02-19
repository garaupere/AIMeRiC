"""A module for the Word class."""
import re
import time
from copy import deepcopy

import spacy

from AIMeRiC.escansio.modules.syllable import Syllable
from AIMeRiC.escansio.modules.word_utils.syllabify import hyphenate_word

nlp = spacy.load("ca_core_news_md", disable=["ner"])


def bivalents(result, cat):
    for syllable in result:
        if syllable[1] == "4":
            if cat in ["AUX", "NUM", "PRON", "PRONE", "INTJ", "ADP"]:
                o_syllable = syllable
                syllable = (syllable[0], "3")
                result[result.index(o_syllable)] = syllable
            if cat in ['ADPa']:
                o_syllable = syllable
                syllable = (syllable[0], "2")
                result[result.index(o_syllable)] = syllable
        else:
            o_syllable = syllable
            syllable = (syllable[0], "0")
            result[result.index(o_syllable)] = syllable
    return result

    # self.stress = [(syllable[0], "3") if syllable[1] == "4" else (syllable[0], "0") for syllable in self.stress]


class Word:
    """Aquesta classe representa una paraula amb les seves característiques."""

    def __init__(self, word, word_pos, index, verse_wlength: int = 0):
        self.w_index = index
        self.verse_wlength = verse_wlength
        self.text = word.lower()
        self.upos = word_pos
        self.syllables = hyphenate_word(self.text)  # Mòdul independent: escansio/utils/syllabes.py
        self.safe_syllables()  # Aquest mòdul s'ha de fer independent i s'ha d'incloure a: escansio/utils/syllabes.py (?, no ho sé)
        self.word_ment = self.word_ment()  # Crear un mòdul independent: escansio/utils/stress.py
        self.n_syllables = len(self.syllables)  # Número de síl·labes
        self.stress = self.get_stress()  # Afegir a un mòdul independent: escansio/utils/stress.py
        self.stress_index = self.get_stress_index()  # Afegir a un mòdul independent: escansio/utils/stress.py
        if self.stress_index is not None and self.stress_index > 2:
            self.compost()
        self.is_compost = False

        self.secondary_stress()  # Afegir a un mòdul independent: escansio/utils/stress.py
        self.starts_with_vowel = self.starts_with_vowel()  # Afegir a un mòdul independent: escansio/utils/phonology.py
        self.ends_with_vowel = self.ends_with_vowel()  # Afegir a un mòdul independent: escansio/utils/phonology.py
        self.plain_syllables = self.plain()  # Afegir a un mòdul independent: escansio/utils/representation.py
        self.fusionada = False
        self.monosyllable = [True if self.n_syllables == 1 else False][0]
        self.paraula_tall = False
        self.print_stress = self.print_stress()  # Mantenir dins el mòdul de la classe.

    def print_stress(self):
        return [(syllable.text, syllable.pes) for syllable in self.stress]

    def renova(self, sillaba):
        self.stress = [sillaba]

    def starts_with_vowel(self):
        if re.search("^-?h?[aeiouàáèéíìóòúùïüy]", self.text):
            if not re.search("^[iuy][aeiouàáèéíìóòúùïüy]", self.text):
                return True
            else:
                return False
        else:
            return False

    def ends_with_vowel(self):
        list = ['per', 'llur']
        if self.text in list:
            self.stress[0].ends_with_vowel = False
            return False
        if self.text[-1] == 'r':
            if len(self.stress) > 2:
                if int(self.stress[-3].pes) > 1:  # Esdrúixola acabada en -r
                    return False
            if len(self.stress) > 1:
                if int(self.stress[-2].pes) > 1:  # Plana acabada en -r
                    return False

        if re.search("([^aeiouàáèéíìóòúùïü]*[aeiouàáèéíìóòúùïüy]|[qg]u[aeioàáèéíìóòúùïü]|^y)r?-?$", self.text):
            if self.text[-1] == "r" and self.upos == "ADP":
                return False
            else:
                if len(self.text) > 1:
                    if self.text[-1] == "y" and self.text[-2] == "n":
                        return False
                    elif re.search("([aeiouàáèéíìóòúùïüy][iuy])$", self.text):
                        if re.search("[qg]u[aeiouàáèéíìóòúùïüy]$", self.text):
                            return True
                        else:
                            return False
            return True
        if re.search("[aeiouàáèéíìóòúùïü]yr$", self.text):
            return False
        else:
            return False

    def safe_syllables(self):
        """Aquesta funció elimina les síl·labes que no contenen vocals."""
        for syllable in self.syllables:
            if not re.search("[aeiouàáèéíìóòúùïüâêîôûy]", syllable.lower()):
                self.syllables.remove(syllable)
        return True

    def plain(self):
        return '.'.join([syll.text.upper() if int(syll.pes) > 1 else syll.text.lower() for syll in self.stress])

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
                                                      len_word=len(self.stress))  # Assignam l'accent secundari (+dèbil)
                    posicio_actual += 2  # Continuam amb la següent posició vàlida (x+4, x+6...)

            self.stress = result + [
                result_end] if self.word_ment is not None else result  # Actualitzam el mot amb els accents secundaris assignats (i el sufix -ment si n'hi ha)

    def monosyllabic(self):
        """Aquesta funció retorna l'accentuació de monosíl·labs"""
        solution = self.syllables[0]
        response = []
        tonics = ["NOUN", "VERB", "ADJ", "ADV", "PROPN"]
        secondary = ["ADPa", "DET", 'CCONJ', 'SCONJ']
        semitonics = ["AUX", "NUM", "PRON", "PRONe", "INTJ", "ADP"]
        if self.upos is not None:
            if self.upos in tonics:
                response = [(solution, "4")]
            elif self.upos in semitonics:
                if self.upos == "PRONe":  # Gestiona els casos de pronoms febles enclítics a final de vers
                    if self.w_index == self.verse_wlength - 1:
                        response = [(solution, "0")]
                    else:
                        response = [(solution, "3")]
                else:
                    response = [(solution, "3")]
            elif self.upos in secondary:
                response = [(solution, "2")]
            else:
                response = [(solution, "0")]
        return response

    def is_bivalent(self):
        if self.upos in ["AUX", "NUM", "ADP", "ADPa", "PRON", "PRONE", "INTJ", "CCONJ", "SCONJ"]:
            return True
        else:
            return False

    def get_stress(self):
        """Aquesta funció retorna la paraula amb l'accentuació"""
        stressed = self.syllables.copy()
        result = []
        oxytone_ending = re.compile(
            r"(?:[àáèéíìóòúùâêîôûý]|"  # Vocals accentuades.
            r"[aeiouïüy][ui]$|"  # Diftongs ascendents.
            r"[aouïü][^'aeiuos]+|"  # Vocals (a, o, u) + consonants excepte <s>.
            r"[^qg]?[aouïü][^aeouïü][^aouïüs]|"  # Vocals (a, o, u) + consonants  + consonant (tipus: rebost).
            r"[eiy]([^'aeiuons]|[^'aeiuo]+[^'aeiuo]))"  # Vocals (e, i) + consonants, excepte <s> i  <en>, <in>.
            r"s?(?:$|-)"  # s opcional + final o guionet.
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

            elif n >= 2:
                """Si el mot té més o dues síl·labes"""
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
            result = self.forced_rhythmic_alternation(result)
        result = [Syllable(num, syllable, len(result)) for num, (syllable) in enumerate(result)]
        return result

    def word_ment(self):
        """Aquesta funció retorna la paraula amb l'afix -ment eliminat, preparada per poder ser accentuada"""
        if self.text.endswith("ment") and len(self.syllables) > 1:
            return hyphenate_word(self.text.replace("ment", ""))

    def print_metadata(self):
        for attr in ["text", "upos", "word_ment", "syllables", "n_syllables", "print_stress",
                     "starts_with_vowel",
                     "ends_with_vowel", "plain_syllables", "is_compost"]:
            print(f"\t\t\t\t{attr}:", getattr(self, attr))
        print("\n")

    def compost(self):
        """Un mètode per assignar l'accent secundari als mots composts."""
        original = deepcopy(self.stress)
        # Cream un índex de divisió del mot a la meitat + una síl·laba
        div_index = round((self.n_syllables / 2))
        doc2 = nlp(''.join(self.syllables[0:div_index]))  # Dividim el mot en dues parts amb l'índex de divisió
        while div_index > 0:  # Mentre l'índex de divisió sigui vàlid
            # print(div_index, doc2[0].text, doc2[0].is_oov, doc2[0].pos_)
            if not doc2[0].is_oov and doc2[0].pos_ in ["NOUN", "VERB", "ADV",
                                                       "ADJ",
                                                       "ADP"]:  # Si el mot no és 'estrany' i és un nom, verb o adverbi (cat. que poden formar mots composts segons la GIEC)
                w1 = Word(''.join(self.syllables[0:div_index]), doc2[0].pos_,
                          0)  # Cream el primer component del mot compost.
                w1.syllables = self.syllables[
                               0:div_index]  # Ens asseguram que el mot obeeixi la divisió sil·làbica original
                w1.get_stress()
                w1.get_stress_index()
                #print([(syl.text, syl.pes) for syl in w1.stress])
                for syl in w1.stress:  # Assignam el valor d'accent secundari a l'accent primari del primer component del mot compost.
                    if int(syl.pes) > 2:
                        syl.pes = "2"
                doc3 = nlp(''.join(self.syllables[div_index::]))  # Dividim el segon component del mot compost.
                if not doc3[0].is_oov and doc3[0].pos_ in ["NOUN", "VERB", "ADV",
                                                           "ADJ",
                                                           "ADP"]:  # Si el segon component del mot compost no és 'estrany' i és un nom, verb o adverbi (cat. que poden formar mots composts segons la GIEC)
                    w2 = Word(''.join(self.syllables[div_index:]), doc3[0].pos_,
                              0)  # Cream el segon component del mot compost.
                    w2.syllables = self.syllables[
                                   div_index::]  # Ens asseguram que el mot obeeixi la divisió sil·làbica original
                    w2.get_stress()
                    w2.get_stress_index()
                    #print([(syl.text, syl.pes) for syl in w2.stress])
                    self.stress = w1.stress + w2.stress  # Unim els dos components del mot compost en un sol mot (el mot que s'està creant).
                    self.is_compost = True
                else:
                    div_index -= 1  # Decreixem l'índex de divisió
                # print([syl.pes for syl in self.stress])
                if "2" not in [syl.pes for syl in self.stress]:
                    self.is_compost = False
                    self.stress = original
                    self.secondary_stress()
                    break
                # elif "2" in [syl.pes for syl in self.stress]:
                #     self.stress = [Syllable(i, (x[0], x[1]), len(self.stress)) for i, x in enumerate(self.forced_rhythmic_alternation([(syl.text, syl.pes) for syl in self.stress]))]
                #     break
                else:
                    self.is_compost = True
                    break  # Sortim de la funció.
            else:  # Si el mot és 'estrany'
                div_index -= 1  # Decreixem l'índex de divisió
                doc2 = nlp(''.join(self.syllables[
                                   0:div_index]))  # Dividim el mot en dues parts de nou amb el nou índex de divisió.

    def get_stress_index(self):
        for i, syllable in enumerate(self.stress):
            if int(syllable.pes) > 2:
                stress_index = i
                return stress_index
            elif self.monosyllabic():
                return 0


if __name__ == "__main__":
    start = time.time()
    sentence = ("i")
    nlp = spacy.load("ca_core_news_md", disable=["ner"])
    doc = nlp(sentence)
    doc = [tok.pos_ for tok in doc]
    for mot in sentence.split():
        mot = Word(mot, doc[sentence.split().index(mot)], 0)
        mot.print_metadata()

    print(time.time() - start)
