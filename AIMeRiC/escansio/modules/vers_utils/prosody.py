"""Un mòdul per gestionar funcions prosòdiques del vers"""
from .decasyllable import tall
from .meter import recompte_metric


def adjust_pes(self):
    """""Un mètode per a ajustar els xocs i les valls accentuals amb elements semitònics implicats.
    Semitònic = T; WTW = WSW, WTS = WWS, STW = SWW, etc."""""
    # print('in:', [(syl.text, syl.pes) for syl in self.no_words])
    #if int(self.words[0].stress[0].pes) < 4:
    #    self.words[0].stress[0].pes = '0'

    def iterate_no_words(self):
        for i in range(len(self.no_words)):
            current_value = self.no_words[i]
            previous_value = self.no_words[i - 1] if i > 0 else None
            next_value = self.no_words[i + 1] if i < len(self.no_words) - 1 else None
            yield previous_value, current_value, next_value

    def change_pes(current_value, pes: str):
        current_value.pes = '4'
        for word in self.words:
            if current_value in word.stress:
                word.stress[word.stress.index(current_value)].pes = pes

    for previous_value, current_value, next_value in iterate_no_words(self):
        if len(self.no_words) <= 3 or self.no_words[3] == current_value and int(self.no_words[3].pes) > 2:
            continue

        if self.words[-1].stress_index is not None and current_value == self.words[-1].stress[
            self.words[-1].stress_index] and current_value.pes == '3':
            if previous_value is not None and int(previous_value.pes) > 3:
                change_pes(previous_value, '1')

        if current_value.pes in ['2', '3']:
            if previous_value is not None and next_value is not None:
                if current_value.pes == '3' and previous_value.pes == '0' and next_value.pes == '0':
                    change_pes(current_value, '3') # Això no fa res
                elif current_value.pes == '2' and previous_value.pes == '0' and next_value.pes == '0':
                    change_pes(current_value, '2') # Això no fa res.
                else:
                    if current_value.pes == '3' and (int(previous_value.pes) > 3 or int(next_value.pes) > 1):
                        change_pes(current_value, '1')
                    elif current_value.pes == '2' and (int(previous_value.pes) > 1 or int(next_value.pes) > 1):
                        change_pes(current_value, '1')
            elif next_value is not None:
                if current_value.pes == '3' and int(next_value.pes) > 1:
                    change_pes(current_value, '1')
                elif current_value.pes == '2' and int(next_value.pes) > 1:
                    change_pes(current_value, '1')
            elif previous_value is not None:
                if current_value.pes == '3' and int(previous_value.pes) > 1:
                    change_pes(current_value, '1')
                elif current_value.pes == '2' and int(previous_value.pes) > 1:
                    change_pes(current_value, '1')
        if current_value.pes == '1':
            if previous_value is not None and next_value is not None:
                if int(previous_value.pes) < 2 and int(next_value.pes) < 2:
                    change_pes(current_value, '2')
            elif previous_value is None and next_value is not None: # Principi de vers
                if int(next_value.pes) < 2:
                    change_pes(current_value, '2')

#----------------------------------------------------------------------------------------------
    # for previous_value, current_value, next_value in iterate_no_words(self):
    #     if len(self.no_words) > 3:
    #         if self.no_words[3] != current_value: # Comprova si és la síl·laba del tall (4+6)
    #             if self.words[-1].stress_index is not None: #
    #                 if current_value == self.words[-1].stress[self.words[-1].stress_index] and current_value.pes == '3':
    #                     if previous_value is not None:
    #                         if int(previous_value.pes) > 3:
    #                             change_pes(previous_value, '1')
    #             if previous_value is not None and next_value is not None:
    #                 if current_value.pes == '3':
    #                     if previous_value.pes == '0' and next_value.pes == '0':
    #                         change_pes(current_value, '3')  # No fa res
    #                 if current_value.pes == '2':
    #                     if previous_value.pes == '0' and next_value.pes == '0':
    #                         change_pes(current_value, '2')  # Això no fa res.
    #                 if current_value.pes == '3':
    #                     if int(previous_value.pes) > 3 or int(next_value.pes) > 2:
    #                         change_pes(current_value, '0')
    #                 if current_value.pes == '2':
    #                     if int(previous_value.pes) > 2 or int(next_value.pes) > 1:
    #                         change_pes(current_value, '0')
    #             elif next_value is not None:
    #                 if current_value.pes == '3':
    #                     if int(next_value.pes) > 2:
    #                         change_pes(current_value, '0')
    #                 if current_value.pes == '2':
    #                     if int(next_value.pes) > 1:
    #                         change_pes(current_value, '0')
    #             elif previous_value is not None and next_value is not None:
    #                 if current_value.pes == '3':
    #                     if int(previous_value.pes) > 2:
    #                         change_pes(current_value, '0')
    #                 if current_value.pes == '2':
    #                     if int(previous_value.pes) > 1:
    #                         change_pes(current_value, '0')
        # print('out:', [(syl.text, syl.pes) for syl in self.no_words])


def cim_maxim(self):
    """Aquesta funció substitueix els cims màxims (>=2) per cims superiors (5) en l'última síl·laba S de cada còlon."""
    # sense_mots = sum([word.stress for word in self.words], []) # Crea una llista amb totes les síl·labes del vers sense fronteres de mot
    # posicio_cim = self.goal - 1 # Defineix la posició del cim a partir del tipus de vers objecte, ex. decasíl·lab, sil. 10
    # try:
    #     if int(sense_mots[posicio_cim].pes) > 1: # Comprova si el valor de la síl·laba que defineix el vers és tòncic
    #         syll = sense_mots[posicio_cim] # Desa la síl·laba que defineix el vers
    #         sense_mots[posicio_cim].pes = '5' # Assigna el valor màxim a la síl·laba que defineix el vers
    #         self.no_words[posicio_cim].pes = '5' # Assigna el valor màxim a la síl·laba que defineix el vers
    #         self.words[-1].stress[syll.s_index].pes = '5' # Assigna el valor màxim a la síl·laba que defineix el vers
    #         self.pattern = [syl.pes for syl in sense_mots] # Actualitza el patró del vers
    #         self.comparative_pattern = ''.join([str(x) for x in self.pattern]).rstrip('0')
    #         self.maxpattern()
    #         self.recompte_sillabes_metriques = recompte_metric(self) # Recalcula el recompte de síl·labes mètriques
    #         self.recompte_sillabes_extrametriques = len(self.pattern) - self.recompte_sillabes_metriques # Recalcula el recompte de síl·labes extramètriques
    #         self.posicio_tall = tall(self) # Recalcula la posició del tall
    #         self.subdivision = f"{self.posicio_tall}+{self.recompte_sillabes_metriques - self.posicio_tall}" if self.posicio_tall is not None else None # Recalcula la subdivisió
    # except IndexError:
    #     pass
    sense_mots = sum([word.stress for word in self.words], [])
    try:
        if int(sense_mots[self.goal - 1].pes) > 1:
            for w in range(0, len(self.words)):
                if sense_mots[self.goal - 1] in self.words[w].stress:
                    self.words[w].stress[self.words[w].stress.index(sense_mots[self.goal - 1])].pes = '5'
                    self.no_words[self.goal - 1].pes = '5'
                    self.pattern[self.goal - 1] = 5
                    if len(sense_mots[self.goal - 1].pes) > 1:
                        if w + 1 == len(self.words) - 1:
                            self.words[w + 1].stress[0].pes = '0'
                            self.no_words[(self.goal - 1) + 1].pes = '0'
                            self.pattern[(self.goal - 1) + 1] = 0
            self.recompte_sillabes_metriques = recompte_metric(self)
            self.recompte_sillabes_extrametriques = len(self.pattern) - self.recompte_sillabes_metriques
            self.posicio_tall = tall(self)
            self.subdivision = f"{self.posicio_tall}+{self.recompte_sillabes_metriques - self.posicio_tall}" if self.posicio_tall is not None else None

    except IndexError:
       pass
