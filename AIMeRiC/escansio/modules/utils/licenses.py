"""Un mòdul per a aplicar les solucions prosòdiques forçades"""
import re

from AIMeRiC.escansio.modules.syllable import Syllable
from AIMeRiC.escansio.modules.word import Word
from .fonetica_sintactica import join_syllables, split_syllable, best_sinalefa, resol_contactes_vocalics, best_contacte_vocalic, \
    best_sineresi
from .stress import get_stress_index, secondary_stress


def llicencies(self) -> str:
    """
    Applies metrical licenses to a given verse.

    This function adjusts the syllable count of a verse to match a target number of syllables (self.objectiu) by applying various metrical licenses such as sinalefa, dialefa, and sineresi.

    Returns:
        str: A string indicating the last applied metrical license and the difference in syllable count.
    """
    result = None
    diff = self.recompte_sillabes_metriques - self.objectiu
    max_iterations = self.objectiu
    iterations = 0

    while diff != 0 and iterations < max_iterations:
        if diff > 0:
            resol_contactes_vocalics(self, best_mode='sinalefa')
            result = f'sinalefa {diff}'
        else:
            dialefa(self, abs(diff))
            result = f'dialefa {abs(diff)}'

        self.__actualitza__()
        diff = self.recompte_sillabes_metriques - self.objectiu

        if diff > 0:
            sineresi(self)
            result = f'sineresis {diff}'
            self.__actualitza__()
            diff = self.recompte_sillabes_metriques - self.objectiu

        iterations += 1

    return result


def sineresi(self):
    """
    Applies synaeresis to a given verse. Synaeresis combines two syllables into one within a word.
    Example: his.tò.ri.a -> his.tò.ria
    """
    best = best_sineresi(self)
    if best:
        diff = self.recompte_sillabes_metriques - self.objectiu
        while diff > 0 and best:
            change = best.pop(0)
            for word in self.words:
                if change[0] in word.stress and change[1] in word.stress:
                    result = join_syllables(change[0], change[1])
                    result.text = re.sub(r"_", "", result.text)
                    if result:
                        word.stress.remove(change[1])
                        word.stress_index = get_stress_index(word)
                        secondary_stress(word)
            diff = self.recompte_sillabes_metriques - self.objectiu
            self.nomes_sillabes = sum((word.stress for word in self.words), [])


def dieresi(self, times):
    """Aquesta funció aplica el fenomen de la dièresi a un vers donat. D'un diftong en interior de mot, en crea un hiat. Per exemple: aire > a.i.re; ai.gua > a.i.gu.a, etc."""
    counter = 0  # Comptador de vegades que s'ha aplicat el fenomen
    # for word in self.words:  # Recorre les paraules del vers

    len_words = len(self.words)
    i = 0
    while i < len_words:
        word = self.words[i]
        syl_len = len(word.stress)
        # print([syllable.text for syllable in word.stress])
        j = 0
        while j < syl_len:
            syllable = word.stress[j]
            if syllable.diftong:  # Si la síl·laba actual és un diftong
                # print(syllable.text, syllable.diftong)
                if re.findall(r"[aeiouàéèíòóú][iy]", syllable.text):  # Si la síl·laba conté una vocal tancada
                    # Crea dues síl·labes a partir del diftong
                    sillaba_split = re.sub(r"(.*[aeiouàéèíòóú])([iy].*)", r"\1@\2",
                                           syllable.text)
                    sil1 = Syllable(syllable.s_index, (sillaba_split.split("@")[0], '0'), syllable.len_word + 1)
                    sil2 = Syllable(syllable.s_index + 1, (sillaba_split.split("@")[1], syllable.pes),
                                    syllable.len_word)

                    sil1.diftong = False
                    sil2.diftong = False

                    word.stress.remove(syllable)  # Elimina la síl·laba actual (antiga síl·laba amb diftong)
                    word.stress.insert(sil1.s_index, sil1)  # Afegeix la primera síl·laba de la dièresi
                    word.stress.insert(sil2.s_index, sil2)  # Afegeix la segona síl·laba de la dièresi
                    for syllable in word.stress[
                                    sil2.s_index:]:  # Recorre les síl·labes de la paraula a partir de la segona síl·laba de la dièresi
                        syllable.s_index += 1  # __actualitza__ l'índex de síl·laba

                    syl_len += 1  # Augmenta el recompte de síl·labes de la paraula
                    counter += 1  # Augmenta el recompte de dièresis

                    if counter > 0:  # Si s'ha aplicat el nombre de dièresis desitjat
                        return True  # Retorna True i finalitza la funció

            j += 1
        i += 1


def dialefa(self, diferencia):
    # print("Dialefa")
    counter = 0
    self.words.append(Word("mpt", self.words[-1].upos, len(self.words), len(self.words)))
    # print([word.plain() for word in self.words])
    len_words = len(self.words)
    i = 0
    while i < len_words - 1:
        i = i
        if i < len_words - 1:
            j = i + 1
        else:
            j = i
        trif_in = next(
            (self.words[j].stress.index(syllable) for syllable in self.words[j].stress if syllable.triftong), None)

        if trif_in is not None:
            """Mètode 0: un triftong"""
            # print("Dialefa Mètode 0: un triftong")
            result = split_syllable(self.words[j].stress[trif_in])
            # print(result[0].text, result[1].text)
            self.words[i].stress.append(result[0])
            self.words[j].stress[0] = result[1]
            # print([w.plain() for w in self.words])

            counter += 1
            if counter == diferencia:
                del self.words[-1]
                return True

        elif self.words[i].stress and self.words[i].stress[-1].fusion_direction == "1":
            """Mètode 1: dos mots monosil·làbics"""
            word1_syll = self.words[i].stress[-1]
            result = split_syllable(word1_syll)
            self.words.insert(j, Word("empt", self.words[i].upos, j, len(self.words)))
            self.words[i].stress[-1] = result[0]
            self.words[j].stress[0] = result[1]

            len_words += 1
            i += 1
            j += 1
            counter += 1
            if counter == diferencia:
                del self.words[-1]
                return True


        elif self.words[i].stress and self.words[i].stress[0].fusion_direction == "2":
            """Mètode 2: monosil·lab i polisil·lab"""
            # print("Dialefa Mètode 2: monosil·lab i polisil·lab")
            word1_syll = self.words[i].stress[0]
            result = split_syllable(word1_syll)
            self.words.insert(i, Word("empt", self.words[i].upos, i - 1, len(self.words)))
            self.words[i].stress[-1] = result[0]
            self.words[j].stress[0] = result[1]

            len_words += 1
            i += 1
            j += 1
            counter += 1
            if counter == diferencia:
                del self.words[-1]
                return True

        elif self.words[i].stress and self.words[i].stress[-1].fusion_direction == "3":
            """Mètode 3: polisil·lab i monosil·lab"""
            word1_syll = self.words[i].stress[-1]
            result = split_syllable(word1_syll)
            # print("Dialefa Mètode 3: polisil·lab i monosil·lab")
            self.words.insert(j, Word("empt", self.words[i].upos, j - 1, len(self.words)))
            self.words[i].stress[-1] = result[0]
            self.words[j].stress[0] = result[1]
            len_words += 1
            i += 1
            j += 1
            counter += 1
            if counter == diferencia:
                del self.words[-1]
                return True

        elif self.words[i].stress and self.words[i].stress[0].fusion_direction == "4":
            """Mètode 4: dos polisil·labs"""
            # print("Dialefa Mètode 4: dos polisil·labs")
            word1_syll = self.words[i].stress[0]
            result = split_syllable(word1_syll)
            if word1_syll.triftong:
                self.words.insert(i, Word("mpt", self.words[i].upos, i, len(self.words)))
                self.words[i].stress.append(result[0])
            else:
                self.words[i - 1].stress.append(result[0])

            self.words[i].stress[0] = result[1]
            counter += 1
            if counter == diferencia:
                del self.words[-1]
                return True

        i += 1
    else:
        del self.words[-1]


def epenthesis(self):
    """Aquesta funció afegeix una vocal epentètica a un mot començat per "s" seguida de consonant."""
    # print("Epèntesi")
    for word in self.words:
        if re.findall("^[sS]ci", word.text):
            return False
        elif re.findall("^[sS][^aeiouàáèéíìyýÿóòúùïüh]", word.text):
            word.stress[0].text = re.sub("(^[sS][^aeiouàáèéíìyýÿóòúùïüh])", r"e\1", word.stress[0].text)
            word.text = re.sub("(^[sS][^aeiouàáèéíìyýÿóòúùïüh])", r"e\1", word.text)
            return True
