"""A module for the Word class."""
import re
import time
from copy import deepcopy

import spacy

from AIMeRiC.escansio.modules.utils.fonologia import starts_with_vowel, ends_with_vowel
from AIMeRiC.escansio.modules.utils.stress import get_stress, get_stress_index, secondary_stress
from AIMeRiC.escansio.modules.utils.syllabify import hyphenate_word as syllabify

nlp = spacy.load("ca_core_news_md", disable=["ner"])





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


class Word:
    """Aquesta classe representa una paraula amb les seves característiques."""

    def __init__(self, word, word_pos, index, verse_wlength: int = 0):
        self.w_index = index
        self.verse_wlength = verse_wlength
        self.text = word.lower()
        self.upos = word_pos
        self.syllables = syllabify(self.text)  # Mòdul independent: escansio/utils/syllabes.py
        self.correct_DET()
        self.safe_syllables()  # Aquest mòdul s'ha de fer independent i s'ha d'incloure a: escansio/utils/syllabes.py (?, no ho sé)
        self.word_ment = self.word_ment()
        self.n_syllables = len(self.syllables)  # Número de síl·labes
        self.stress = get_stress(self)
        self.stress_index = get_stress_index(self)
        if self.stress_index is not None and self.stress_index > 2:
            self.compost()
        self.is_compost = False

        secondary_stress(self)
        self.starts_with_vowel = starts_with_vowel(self)
        self.ends_with_vowel = ends_with_vowel(self)
        self.plain_syllables = self.plain()  # Afegir a un mòdul independent: escansio/utils/representation.py
        self.fusionada = False
        self.monosyllable = [True if self.n_syllables == 1 else False][0]
        self.paraula_tall = False
        self.bivalent = self.is_bivalent() if not self.monosyllable else True if int(self.stress[0].pes) > 1 else False
        self.safe_syllables()
        self.print_stress = self.print_stress()

    def is_bivalent(self):
        if self.upos in ["AUX", "NUM", "ADP", "ADPa", "PRON", "PRONe", "INTJ", "DET"]:
            return True
        else:
            return False

    def correct_DET(self):
        if self.upos == 'DET' and len(self.syllables) > 2:
            self.upos = 'NOUN'

    def print_stress(self):
        return [(syllable.text, syllable.pes) for syllable in self.stress]

    def renova(self, sillaba):
        self.stress = [sillaba]

    def safe_syllables(self):
        """Aquesta funció elimina les síl·labes que no contenen vocals."""
        for syllable in self.syllables:
            if not re.search("[aeiouàáèéíìóòúùïüâêîôûy]", syllable.lower()):
                self.syllables.remove(syllable)
        return True

    def plain(self):
        return '.'.join([syll.text.upper() if int(syll.pes) > 1 else syll.text.lower() for syll in self.stress])



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

    def word_ment(self):
        """Aquesta funció retorna la paraula amb l'afix -ment eliminat, preparada per poder ser accentuada"""
        if self.text.endswith("ment") and len(self.syllables) > 1:
            return syllabify(self.text.replace("ment", ""))

    def print_metadata(self):
        for attr in ["text", "upos", "word_ment", "syllables", "n_syllables", "print_stress",
                     "starts_with_vowel",
                     "ends_with_vowel", "plain_syllables", "is_compost"]:
            print(f"\t\t\t\t{attr}:", getattr(self, attr))
        for syllable in self.stress:
            syllable.print_metadata()

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
                word_1 = Word(''.join(self.syllables[0:div_index]), doc2[0].pos_,
                          0)  # Cream el primer component del mot compost.
                word_1.syllables = self.syllables[
                               0:div_index]  # Ens asseguram que el mot obeeixi la divisió sil·làbica original
                get_stress(word_1)
                get_stress_index(word_1)
                # print([(syl.text, syl.pes) for syl in word_1.stress])
                for syl in word_1.stress:  # Assignam el valor d'accent secundari a l'accent primari del primer component del mot compost.
                    if int(syl.pes) > 2:
                        syl.pes = "2"
                doc3 = nlp(''.join(self.syllables[div_index::]))  # Dividim el segon component del mot compost.
                if not doc3[0].is_oov and doc3[0].pos_ in ["NOUN", "VERB", "ADV",
                                                           "ADJ",
                                                           "ADP"]:  # Si el segon component del mot compost no és 'estrany' i és un nom, verb o adverbi (cat. que poden formar mots composts segons la GIEC)
                    word_2 = Word(''.join(self.syllables[div_index:]), doc3[0].pos_,
                              0)  # Cream el segon component del mot compost.
                    word_2.syllables = self.syllables[
                                   div_index::]  # Ens asseguram que el mot obeeixi la divisió sil·làbica original
                    get_stress(word_2)
                    get_stress_index(word_2)
                    # print([(syl.text, syl.pes) for syl in word_2.stress])
                    self.stress = word_1.stress + word_2.stress  # Unim els dos components del mot compost en un sol mot (el mot que s'està creant).
                    self.is_compost = True
                else:
                    div_index -= 1  # Decreixem l'índex de divisió
                # print([syl.pes for syl in self.stress])
                if "2" not in [syl.pes for syl in self.stress]:
                    self.is_compost = False
                    self.stress = original
                    secondary_stress(self)
                    break
                else:
                    self.is_compost = True
                    break  # Sortim de la funció.
            else:  # Si el mot és 'estrany'
                div_index -= 1  # Decreixem l'índex de divisió
                doc2 = nlp(''.join(self.syllables[
                                   0:div_index]))  # Dividim el mot en dues parts de nou amb el nou índex de divisió.


if __name__ == "__main__":
    start = time.time()
    sentence = ("deliquis")
    nlp = spacy.load("ca_core_news_md", disable=["ner"])
    doc = nlp(sentence)
    doc = [tok.pos_ for tok in doc]
    for mot in sentence.split():
        mot = Word(mot, doc[sentence.split().index(mot)], 0)
        mot.print_metadata()

    print(time.time() - start)
