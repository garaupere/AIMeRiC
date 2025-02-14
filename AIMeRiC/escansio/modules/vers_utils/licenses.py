"""Un mòdul per a aplicar les solucions prosòdiques forçades"""
import re

from AIMeRiC.escansio.modules.syllable import Syllable
from AIMeRiC.escansio.modules.word import Word
from .fonologia import join_syllables, split_syllable, best_sinalefa, resol_contactes_vocalics, best_contacte_vocalic, \
    best_sineresi
from .meter import recompte_metric
from .tools import seguent


def aplica_llicencies(self) -> str:
    """Aquesta funció aplica les llicències mètriques a un vers donat."""
    result = None
    if self.goal == 10 and len(self.no_words) > 2:
        self.recompte_sillabes_metriques = recompte_metric(self)
        diferencia = self.recompte_sillabes_metriques - self.goal
        if diferencia > 0:
            resol_contactes_vocalics(self, best=best_sinalefa(self.no_words))
            result = f'sinalefa {diferencia}'
            self.__actualitza__()
            diferencia = self.recompte_sillabes_metriques - self.goal
            if diferencia < 0:
                """aplica el hiat"""
                dialefa(self, abs(diferencia))
                result = f'dialefa {abs(diferencia)}'
                self.__actualitza__()
                diferencia = self.recompte_sillabes_metriques - self.goal
            elif diferencia > 0:
                sineresi2(self)
                result = f'sineresis {diferencia}'
                self.__actualitza__()
        elif diferencia < 0:
            dialefa(self, abs(diferencia))
            result = f'dialefa {abs(diferencia)}'
            self.__actualitza__()
            diferencia = self.recompte_sillabes_metriques - self.goal
            if diferencia > 0:
                resol_contactes_vocalics(self, best=best_sinalefa(self.no_words))
                result = f'sinalefa {diferencia}'
                self.__actualitza__()
                diferencia = self.recompte_sillabes_metriques - self.goal
                if diferencia > 0:
                    sineresi2(self)
                    result = f'sineresis {diferencia}'
                    self.__actualitza__()
            diferencia = self.recompte_sillabes_metriques - self.goal
            if diferencia > 0:
                sineresi2(self)
                result = f'sineresis {diferencia}'
                self.__actualitza__()
            # if diferencia < 0:
            #     self.dieresi(abs(diferencia))
            #     result = f'dieresi {abs(diferencia)}'
            #     self.__actualitza__()
            #     diferencia = self.recompte_sillabes_metriques - self.goal
    return result


def sineresi2(self):
    best = best_sineresi(self.no_words)
    if best is not None:
        diff = self.recompte_sillabes_metriques - self.goal  # Calcula la diferència
        while diff > 0 and best:  # Mentre hi hagi diferència i hi hagi contactes vocals candidats
            change = best.pop(0)  # Treu el primer contacte vocal candidat
            wi = 0
            while wi < len(self.words) - 1:
                word = self.words[wi]
                if change[0] in word.stress:
                    result = join_syllables(change[0], change[1])
                    if result:
                        syllable = change[0]
                        next_syllable = change[1]
                        if syllable in word.stress and next_syllable in word.stress:
                            word.stress.pop(word.stress.index(next_syllable))
                            word.stress_index = word.get_stress_index()
                            word.secondary_stress()
                wi += 1
            diff = self.recompte_sillabes_metriques - self.goal  # Recalcula la diferència
            self.no_words = sum([word.stress for word in self.words], [])  # Actualitza la llista de síl·labes







def sineresis(self, times):
    global nou
    counter = 0
    for syllable in self.no_words:
        next_syllable = seguent(syllable, self.no_words)
        if next_syllable is not None:
            if syllable.vowel_end and next_syllable.vowel_start:
                if syllable.fono_info['alta']:
                    nou = join_syllables(syllable, next_syllable)
                    nou.text = nou.text.replace("_", "")
                    nou = nou
                    i = 0
                    while i < len(self.words) - 1:
                        word = self.words[i]
                        next_word = self.words[i + 1]
                        if syllable in word.stress and next_syllable in word.stress:
                            word.stress.insert(word.stress.index(syllable), nou)
                            word.stress.remove(syllable)
                            word.stress.remove(next_syllable)
                            word.stress_index = word.get_stress_index()
                            word.secondary_stress()

                        elif syllable in next_word.stress and next_syllable in next_word.stress:
                            next_word.stress.insert(next_word.stress.index(syllable), nou)
                            next_word.stress.remove(syllable)
                            next_word.stress.remove(next_syllable)
                            word.stress_index = word.get_stress_index()
                            next_word.stress_index = next_word.get_stress_index()
                            word.secondary_stress()
                            next_word.secondary_stress()

                        elif syllable in word.stress and next_syllable in next_word.stress:
                            word.stress.insert(word.stress.index(syllable), nou)
                            word.stress.remove(syllable)
                            next_word.stress.remove(next_syllable)
                            if len(next_word.stress) == 0:
                                self.words.remove(next_word)
                            word.stress_index = word.get_stress_index()
                            next_word.stress_index = next_word.get_stress_index()
                            word.secondary_stress()
                            next_word.secondary_stress()
                        i += 1

                    self.no_words.insert(self.no_words.index(syllable), nou)
                    self.no_words.remove(syllable)
                    self.no_words.remove(next_syllable)
                    counter += 1
                    if counter == times:
                        return True

                if syllable.fono_info['vocal'] == next_syllable.fono_info['vocal']:
                    """Mètode 2: fusiona dues vocals idèntiques"""
                    nou = join_syllables(syllable, next_syllable)
                    if nou is not None:
                        try:
                            nou.text = nou.text.replace("_", "")
                        except AttributeError:
                            nou.text = nou.text.replace(":", "")
                        nou = nou
                        i = 0
                        while i < len(self.words) - 1:
                            word = self.words[i]
                            next_word = self.words[i + 1]
                            if syllable in word.stress and next_syllable in word.stress:
                                word.stress.insert(word.stress.index(syllable), nou)
                                word.stress.remove(syllable)
                                word.stress.remove(next_syllable)
                                word.stress_index = word.get_stress_index()

                            elif syllable in next_word.stress and next_syllable in next_word.stress:
                                next_word.stress.insert(next_word.stress.index(syllable), nou)
                                next_word.stress.remove(syllable)
                                next_word.stress.remove(next_syllable)
                                next_word.stress_index = next_word.get_stress_index()
                                word.stress_index = word.get_stress_index()

                            elif syllable in word.stress and next_syllable in next_word.stress:
                                word.stress.insert(word.stress.index(syllable), nou)
                                word.stress.remove(syllable)
                                next_word.stress.remove(next_syllable)
                                if len(next_word.stress) == 0:
                                    self.words.remove(next_word)
                                word.stress_index = word.get_stress_index()
                                next_word.stress_index = next_word.get_stress_index()
                            i += 1

                        self.no_words.insert(self.no_words.index(syllable), nou)
                        self.no_words.remove(syllable)
                        counter += 1
                        if counter == times:
                            return True


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
    self.words.append(Word("mpt", self.words[-1].cat, len(self.words), len(self.words)))
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

        elif self.words[i].stress[-1].fusion_direction == "1":
            """Mètode 1: dos mots monosil·làbics"""
            # print("Dialefa Mètode 1: dos mots monosil·làbics")
            word1_syll = self.words[i].stress[-1]
            result = split_syllable(word1_syll)
            self.words.insert(j, Word("empt", self.words[i].cat, j, len(self.words)))
            self.words[i].stress[-1] = result[0]
            self.words[j].stress[0] = result[1]

            len_words += 1
            i += 1
            j += 1
            counter += 1
            if counter == diferencia:
                del self.words[-1]
                return True


        elif self.words[i].stress[0].fusion_direction == "2":
            """Mètode 2: monosil·lab i polisil·lab"""
            # print("Dialefa Mètode 2: monosil·lab i polisil·lab")
            word1_syll = self.words[i].stress[0]
            result = split_syllable(word1_syll)
            self.words.insert(i, Word("empt", self.words[i].cat, i - 1, len(self.words)))
            self.words[i].stress[-1] = result[0]
            self.words[j].stress[0] = result[1]

            len_words += 1
            i += 1
            j += 1
            counter += 1
            if counter == diferencia:
                del self.words[-1]
                return True

        elif self.words[i].stress[-1].fusion_direction == "3":
            """Mètode 3: polisil·lab i monosil·lab"""
            word1_syll = self.words[i].stress[-1]
            result = split_syllable(word1_syll)
            # print("Dialefa Mètode 3: polisil·lab i monosil·lab")
            self.words.insert(j, Word("empt", self.words[i].cat, j - 1, len(self.words)))
            self.words[i].stress[-1] = result[0]
            self.words[j].stress[0] = result[1]
            len_words += 1
            i += 1
            j += 1
            counter += 1
            if counter == diferencia:
                del self.words[-1]
                return True

        elif self.words[i].stress[0].fusion_direction == "4":
            """Mètode 4: dos polisil·labs"""
            # print("Dialefa Mètode 4: dos polisil·labs")
            word1_syll = self.words[i].stress[0]
            result = split_syllable(word1_syll)
            if word1_syll.triftong:
                self.words.insert(i, Word("mpt", self.words[i].cat, i, len(self.words)))
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
