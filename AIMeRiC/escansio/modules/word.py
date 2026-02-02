"""
Mòdul: word.py

Classe principal:
- Word: representa una paraula amb les seves propietats lèxiques i sil·làbiques,
  s'encarrega de la divisió en síl·labes, càlcul d'accentuació, tractament de
  mots composts i exportació de metadades.

"""
__author__ = "Pere Garau"
__all__ = ["Word"]

import re
import time
from copy import deepcopy

import spacy

from AIMeRiC.escansio.modules.utils.fonologia import starts_with_vowel, ends_with_vowel
from AIMeRiC.escansio.modules.utils.stress import get_stress, get_stress_index, secondary_stress
from AIMeRiC.escansio.modules.utils.syllabify import hyphenate_word as syllabify


class Word:
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
        # Compute word_ment and keep as attribute; avoid clobbering method name.
        self.word_ment = self.compute_word_ment()
        self.n_syllables = len(self.syllables)  # Número de síl·labes
        self.stress = get_stress(self)
        self.stress_index = get_stress_index(self)
        self.is_compost = False
        if self.stress_index is not None and self.stress_index > 2:
            self.compost()


        secondary_stress(self)
        self.starts_with_vowel = starts_with_vowel(self)
        self.ends_with_vowel = ends_with_vowel(self)
        self.plain_syllables = self.plain()  # Afegir a un mòdul independent: escansio/utils/representation.py
        self.fusionada = False
        # Simpler, clearer monosyllable flag
        self.monosyllable = (self.n_syllables == 1)
        self.paraula_tall = False
        # Decide bivalent robustly
        if self.monosyllable:
            # Si és monosil·làbic, mirem el pes de l'única síl·laba (si existeix)
            try:
                pes_val = float(self.stress[0].pes)
            except Exception:
                # si pes no està disponible, caiguem a False
                pes_val = 0.0
            self.bivalent = True if pes_val > 1.0 else False
        else:
            self.bivalent = self.is_bivalent()
        # assegurem una última neteja de síl·labes
        self.safe_syllables()
        # Compute printable stress snapshot; avoid clobbering method name.
        self.print_stress = self.compute_print_stress()

    def is_bivalent(self):
        if self.pos_ in ["AUX", "NUM", "ADP", "ADPa", "PRON", "PRONe", "INTJ", "DET"]:
            return True
        else:
            return False

    def correct_DET(self):
        if self.pos_ == 'DET' and len(self.syllables) > 2:
            self.pos_ = 'NOUN'


    def compute_print_stress(self):
        """Return list of (text, pes) for each stress entry, handling objects, tuples and strings."""
        result = []
        for syll in (self.stress or []):
            # determine text
            if hasattr(syll, "text"):
                text = getattr(syll, "text")
            elif isinstance(syll, (tuple, list)) and len(syll) >= 1:
                text = syll[0]
            else:
                text = str(syll)

            # determine pes
            if hasattr(syll, "pes"):
                pes = getattr(syll, "pes")
            elif isinstance(syll, (tuple, list)) and len(syll) >= 2:
                pes = syll[1]
            else:
                pes = None

            result.append((text, pes))
        return result

    def renova(self, sillaba):
        self.stress = [sillaba]

    def safe_syllables(self):
        """Aquesta funció elimina les síl·labes que no contenen vocals.
        Millora: no modifiquem la llista mentre iterem (bug fix) i suportem objectes amb .text o simples strings.
        """
        vowels_re = re.compile("[aeiouàáèéíìóòúùïüâêîôûy]", re.IGNORECASE)
        filtered = []
        for syllable in self.syllables:
            # Suportar objectes que tenen .text o simples strings
            text = getattr(syllable, "text", syllable)
            if vowels_re.search(text):
                filtered.append(syllable)
        self.syllables = filtered
        return True

    def plain(self):
        return '.'.join([getattr(syll, "text", syll).upper() if float(getattr(syll, "pes", 1)) > 1 else getattr(syll, "text", syll).lower() for syll in self.stress])

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
                        response = [(solution, 3.0)]
                else:
                    response = [(solution, 3.0)]
            elif self.pos_ in secondary:
                response = [(solution, 2.0)]
            else:
                response = [(solution, 0.0)]
        return response

    # Rename to compute_ to avoid collision with attribute word_ment
    def compute_word_ment(self):
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
        # Protecció contra morph None i head sense atribut .i
        morph_dict = None
        try:
            morph_dict = self.morph.to_dict() if self.morph else None
        except Exception:
            morph_dict = None
        try:
            head_idx = self.head.i if self.head and hasattr(self.head, "i") else None
        except Exception:
            head_idx = None

        return {
            "lower": self.lower,
            "index": self.w_index,
            "text": self.text,
            "upos": self.pos_,
            "dep_": self.dep_,
            "lemma_": self.lemma_,
            "morph": morph_dict,
            "head": head_idx,
            "bivalent": self.is_bivalent(),
            "syllables": {
                f"{getattr(syllable,'text', syllable)}_{getattr(syllable,'s_index', idx)}": syllable.save_metadata()
                for idx, syllable in enumerate(self.stress)
            }
        }

    def compost(self):
        """Un mètode per assignar l'accent secundari als mots composts.
        Millora:
        - Utilitza get_nlp() (lazy load)
        - No intenta instanciar Word amb strings/pos incorrectament.
        - Fa servir un wrapper temporal per calcular accentuacions dels components.
        """
        original = deepcopy(self.stress)
        # Cream un índex de divisió del mot a la meitat + una síl·laba
        div_index = round((self.n_syllables / 2))
        nlp = get_nlp()
        doc2 = nlp(''.join(getattr(s, "text", s) for s in self.syllables[0:div_index]))  # Dividim el mot en dues parts amb l'índex de divisió
        while div_index > 0:  # Mentre l'índex de divisió sigui vàlid
            # print(div_index, doc2[0].text, doc2[0].is_oov, doc2[0].pos_)
            if not doc2[0].is_oov and doc2[0].pos_ in ["NOUN", "VERB", "ADV", "ADJ", "ADP"]:
                # Creem un wrapper temporal per al primer component
                class _TempWord:
                    pass

                word_1 = _TempWord()
                word_1.text = ''.join(getattr(s, "text", s) for s in self.syllables[0:div_index])
                word_1.syllables = self.syllables[0:div_index]
                word_1.pos_ = doc2[0].pos_
                word_1.n_syllables = len(word_1.syllables)
                # Calcular accent per al component
                get_stress(word_1)
                get_stress_index(word_1)
                # Assignam el valor d'accent secundari a l'accent primari del primer component del mot compost.
                for syl in word_1.stress:
                    try:
                        if float(getattr(syl, "pes", syl[1] if isinstance(syl, tuple) else 0)) > 2:
                            syl.pes = "2"
                    except Exception:
                        pass
                doc3 = nlp(''.join(getattr(s, "text", s) for s in self.syllables[div_index::]))  # Dividim el segon component del mot compost.
                if not doc3[0].is_oov and doc3[0].pos_ in ["NOUN", "VERB", "ADV", "ADJ", "ADP"]:
                    word_2 = _TempWord()
                    word_2.text = ''.join(getattr(s, "text", s) for s in self.syllables[div_index:])
                    word_2.syllables = self.syllables[div_index:]
                    word_2.pos_ = doc3[0].pos_
                    word_2.n_syllables = len(word_2.syllables)
                    get_stress(word_2)
                    get_stress_index(word_2)
                    # Unim els dos components
                    self.stress = word_1.stress + word_2.stress
                    self.is_compost = True
                else:
                    div_index -= 1  # Decreixem l'índex de divisió
                # Si no hi ha accent secundari adequat revertim
                try:
                    pes_list = [float(getattr(syl, "pes", syl[1] if isinstance(syl, tuple) else 0)) for syl in self.stress]
                except Exception:
                    pes_list = []
                if 2.0 not in pes_list:
                    self.is_compost = False
                    self.stress = original
                    secondary_stress(self)
                    break
                else:
                    self.is_compost = True
                    break  # Sortim de la funció.
            else:  # Si el mot és 'estrany'
                div_index -= 1  # Decreixem l'índex de divisió
                doc2 = nlp(''.join(getattr(s, "text", s) for s in self.syllables[0:div_index]))  # Dividim el mot en dues parts de nou amb el nou índex de divisió.


if __name__ == "__main__":

    def get_nlp():
        """Retorna un objecte nlp singleton (carrega lazy)."""
        global _nlp
        if _nlp is None:
            _nlp = spacy.load("ca_core_news_md", disable=["ner"])
        return _nlp

    start = time.time()
    sentence = "destra"
    nlp = get_nlp()
    doc = nlp(sentence)
    print(doc)
    for token in doc:
        word = (Word(token, len(doc)))
        word.print_metadata()
        print(word.save_metadata())

    print(time.time() - start)
