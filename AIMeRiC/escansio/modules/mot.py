"""El mòdul de la classe 'Mot'."""
import re
import time
from copy import deepcopy

import spacy

from AIMeRiC.escansio.modules.utils.POStagger import posTagger
from AIMeRiC.escansio.modules.utils.fonologia import starts_with_vowel, ends_with_vowel
from AIMeRiC.escansio.modules.utils.accentuacio import accentua, get_index_accent, accent_secundari
from AIMeRiC.escansio.modules.utils.sillabifica import hyphenate_word as syllabify

nlp = spacy.load("ca_core_news_md", disable=["ner"])


class Mot:
    """Aquesta classe representa una paraula amb les seves característiques."""

    def __init__(self, token, length):
        self.w_index = token.i
        self.lower = token.lower_
        self.verse_wlength = length
        self.text = token.text

        # helper to read extension safely
        def ext(name):
            try:
                return getattr(token._, name)
            except Exception:
                return None

        # prefer corrected values stored in token._.* extensions, fallback to token attributes
        self.pos_ = getattr(token, "pos_", None) or ext("upos_corr")
        self.dep_ = getattr(token, "dep_", None) or ext("dep_corr")
        self.lemma_ = getattr(token, "lemma_", None) or ext("lemma_corr")
        self.head = getattr(token, "head", None) or ext("head_corr")
        # morph: prefer ext if present, else build from token.morph
        morph_ext = ext("morph_corr")
        if morph_ext:
            self.morph = morph_ext
        else:
            try:
                self.morph = token.morph
            except Exception:
                self.morph = None

        # children: prefer extension (list of strings) else build from token.children
        children_ext = ext("children_text")
        if children_ext:
            self.children = children_ext
        else:
            try:
                self.children = [child.text for child in token.children]
            except Exception:
                self.children = []
        self.syllables = syllabify(self.text)  # Mòdul independent: escansio/utils/syllabes.py
        self.correct_DET()
        self.safe_syllables()  # Aquest mòdul s'ha de fer independent i s'ha d'incloure a: escansio/utils/syllabes.py (?)
        self.word_ment = self.word_ment()
        self.n_syllables = len(self.syllables)  # Número de síl·labes
        self.stress = accentua(self)
        self.stress_index = get_index_accent(self)
        self.is_compost = False
        #if self.stress_index is not None and self.stress_index > 2:
        #    self.compost()

        #secondary_stress(self)
        accent_secundari(self)
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
        if self.pos_ in ["AUX", "NUM", "ADP", "ADPa", "PRON", "PRONe", "INTJ", "DET"]:
            return True
        else:
            return False

    def correct_DET(self):
        if self.pos_ == 'DET' and len(self.syllables) > 2:
            self.pos_ = 'NOUN'

    def print_stress(self):
        return [(syllable.text, syllable.pes) for syllable in self.stress]

    def renova(self, sillaba):
        self.stress = [sillaba]

    def safe_syllables(self):
        """Aquesta funció elimina les síl·labes que no contenen vocals."""
        for syllable in self.syllables:
            #     if '-' in syllable:
            #         print(">> SÍL·LABA FUSIONADA DETECTADA:", syllable, "en paraula:", self.text)  # Debug
            #         next_syll = self.syllables[self.syllables.index(syllable) + 1] if self.syllables.index(
            #             syllable) + 1 < len(self.syllables) else None
            #         if next_syll:
            #             self.syllables[self.syllables.index(next_syll)] = '-' + next_syll
            #             self.syllables[self.syllables.index(syllable)] = syllable.replace('-', '')
            #         else:
            #             self.syllables[self.syllables.index(syllable)] = syllable

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
        if self.pos_ is not None:
            if self.pos_ in tonics:
                response = [(solution, 4.0)]
            elif self.pos_ in semitonics:
                if self.pos_ == "PRONe":  # Gestiona els casos de pronoms febles enclítics a final de vers
                    if self.w_index == self.verse_wlength - 1:
                        response = [(solution, 0.0)]
                    else:
                        response = [(solution, 2.0)]
                elif self.pos_ == "PRON":
                    response = [(solution, 2.5)]
                elif self.pos_ == "AUX":
                    response = [(solution, 3.5)]
                else:
                    response = [(solution, 3.0)]
            elif self.pos_ in secondary:
                response = [(solution, 2.0)]
            else:
                response = [(solution, 0.0)]
        return response

    def word_ment(self):
        """Aquesta funció retorna la paraula amb l'afix -ment eliminat, preparada per poder ser accentuada"""
        if self.text.endswith("ment") and len(self.syllables) > 1:
            return syllabify(self.text.replace("ment", ""))

    def print_metadata(self):
        for attr in ["text", "lower", "w_index", "pos_", "dep_", "lemma_", "morph", "head", "word_ment",
                     "syllables", "n_syllables", "print_stress",
                     "starts_with_vowel",
                     "ends_with_vowel", "plain_syllables", "is_compost"]:
            print(f"\t\t\t\t{attr}:", getattr(self, attr))
        for syllable in self.stress:
            syllable.print_metadata()

        print("\n")

    def save_metadata(self):
        return {
            "lower": self.lower,
            "index": self.w_index,
            "text": self.text,
            "upos": self.pos_,
            "dep_": self.dep_,
            "lemma_": self.lemma_,
            "morph": self.morph.to_dict(),
            "head": self.head.i,
            "bivalent": self.is_bivalent(),
            "syllables": {
                f"{syllable.text}_{syllable.s_index}": syllable.save_metadata()
                for syllable in self.stress
            }
        }

    def compost(self):
        """Un mètode per assignar l'accent secundari als mots composts. ACTUALMENT NO S'APLICA, MASSA COSTÓS I POC EXHAUSTIU."""
        original = deepcopy(self.stress)
        # Cream un índex de divisió del mot a la meitat + una síl·laba
        div_index = round((self.n_syllables / 2))
        doc2 = nlp(''.join(self.syllables[0:div_index]))  # Dividim el mot en dues parts amb l'índex de divisió
        while div_index > 0:  # Mentre l'índex de divisió sigui vàlid
            # print(div_index, doc2[0].text, doc2[0].is_oov, doc2[0].pos_)
            if not doc2[0].is_oov and doc2[0].pos_ in ["NOUN", "VERB", "ADV",
                                                       "ADJ",
                                                       "ADP"]:  # Si el mot no és 'estrany' i és un nom, verb o adverbi (cat. que poden formar mots composts segons la GIEC)
                word_1 = Mot(''.join(self.syllables[0:div_index]),
                             doc2[0].pos_)  # Cream el primer component del mot compost.
                word_1.syllables = self.syllables[
                    0:div_index]  # Ens asseguram que el mot obeeixi la divisió sil·làbica original
                accentua(word_1)
                get_index_accent(word_1)
                # print([(syl.text, syl.pes) for syl in word_1.stress])
                for syl in word_1.stress:  # Assignam el valor d'accent secundari a l'accent primari del primer component del mot compost.
                    if int(syl.pes) > 2:
                        syl.pes = "2"
                doc3 = nlp(''.join(self.syllables[div_index::]))  # Dividim el segon component del mot compost.
                if not doc3[0].is_oov and doc3[0].pos_ in ["NOUN", "VERB", "ADV",
                                                           "ADJ",
                                                           "ADP"]:  # Si el segon component del mot compost no és 'estrany' i és un nom, verb o adverbi (cat. que poden formar mots composts segons la GIEC)
                    word_2 = Mot(''.join(self.syllables[div_index:]),
                                 doc3[0].pos_)  # Cream el segon component del mot compost.
                    word_2.syllables = self.syllables[
                        div_index::]  # Ens asseguram que el mot obeeixi la divisió sil·làbica original
                    accentua(word_2)
                    get_index_accent(word_2)
                    # print([(syl.text, syl.pes) for syl in word_2.stress])
                    self.stress = word_1.stress + word_2.stress  # Unim els dos components del mot compost en un sol mot (el mot que s'està creant).
                    self.is_compost = True
                else:
                    div_index -= 1  # Decreixem l'índex de divisió
                #print([syl.pes for syl in self.stress])
                if 2.0 not in [syl.pes for syl in self.stress]:
                    self.is_compost = False
                    self.stress = original
                    #secondary_stress(self)
                    accent_secundari(self)
                    break
                else:
                    self.is_compost = True
                    break  # Sortim de la funció.
            else:  # Si el mot és 'estrany'
                div_index -= 1  # Decreixem l'índex de divisió
                doc2 = nlp(''.join(
                    self.syllables[0:div_index]))  # Dividim el mot en dues parts de nou amb el nou índex de divisió.


if __name__ == "__main__":

    sentence = "tot senyal"
    nlp = spacy.load("ca_core_news_md", disable=["ner"])
    start = time.time()
    doc = posTagger(nlp, sentence)
    print(doc)
    for token in doc:
        word = (Mot(token, len(doc)))
        word.print_metadata()
        print(word.save_metadata())
    print(time.time() - start)
