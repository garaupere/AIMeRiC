"""Un mòdul per gestionar funcions prosòdiques del vers"""
from .decasyllable import tall
from .meter import recompte_metric


def accents_prosodics(self):
    """
    Adjusts the prosodic accents of the syllables in the verse.
    """

    def iterate_no_words(self):
        """
        Generator function to iterate through syllables without words.

        Yields:
            tuple: Previous, current, and next syllable values.
        """
        for i in range(len(self.nomes_sillabes)):
            current_value = self.nomes_sillabes[i]
            previous_value = self.nomes_sillabes[i - 1] if i > 0 else None
            next_value = self.nomes_sillabes[i + 1] if i < len(self.nomes_sillabes) - 1 else None
            yield previous_value, current_value, next_value

    def change_pes(current_value, pes: str):
        """
        Changes the weight (pes) of the given syllable and updates the corresponding word stress.

        Args:
            current_value: The current syllable whose weight is to be changed.
            pes (str): The new weight to be assigned.
        """
        current_value.pes = pes
        for word in self.words:
            if current_value in word.stress:
                word.stress[word.stress.index(current_value)].pes = pes

    # Iterate through the syllables without words
    for prev, curr, next in iterate_no_words(self):
        # If the current syllable is the first one and there is a next syllable
        if prev is None and next is not None:
            if 0 < int(curr.pes) < 5:
                # Change the weight of the syllable with the higher weight to '0'
                change_pes(next if int(curr.pes) > int(next.pes) else curr, '0')
        # If the current syllable is the last one and there is a previous syllable
        elif next is None and prev is not None:
            if 1 < int(curr.pes) < 5:
                # Change the weight of the syllable with the higher weight to '0'
                change_pes(curr if int(prev.pes) > int(curr.pes) else prev, '0')
        # If the current syllable is between two other syllables
        elif prev is not None and next is not None:
            if 0 < int(curr.pes) < 4:
                if int(curr.pes) == int(next.pes):
                    # Change the weight of the current syllable to '0' if it equals the next syllable's weight
                    change_pes(curr, '0')
                elif int(curr.pes) > int(next.pes):
                    # Change the weight of the next syllable to '0' if the current syllable's weight is higher
                    change_pes(next, '0')
                elif int(curr.pes) < int(next.pes) or int(prev.pes) > int(curr.pes):
                    # Change the weight of the current syllable to '0' if it is lower than the next syllable's weight
                    change_pes(curr, '0')
            elif int(curr.pes) > 4:
                if int(next.pes) < 4:
                    # Change the weight of the next syllable to '0' if it is lower than 4
                    change_pes(next, '0')
                elif int(prev.pes) < 4:
                    # Change the weight of the previous syllable to '0' if it is lower than 4
                    change_pes(prev, '0')
            elif int(curr.pes) == 4:
                if int(next.pes) < 4:
                    # Change the weight of the next syllable to '0' if it is lower than 4
                    change_pes(next, '0')
                elif int(prev.pes) < 4:
                    # Change the weight of the previous syllable to '0' if it is lower than 4
                    change_pes(prev, '0')


def cim_maxim(self):
    """Substitutes maximum peaks (>=2) with superior peaks (5) in the last strong syllable of each colon."""
    sense_mots = sum([word.stress for word in self.words], [])
    try:
        if int(sense_mots[self.objectiu - 1].pes) > 2:
            for word in self.words:
                if sense_mots[self.objectiu - 1] in word.stress:
                    word.stress[word.stress.index(sense_mots[self.objectiu - 1])].pes = '5'
                    self.nomes_sillabes[self.objectiu - 1].pes = '5'
                    self.patro[self.objectiu - 1] = 5
                    if len(sense_mots[self.objectiu - 1].pes) > 1 and self.words.index(word) + 1 == len(self.words) - 1:
                        self.words[self.words.index(word) + 1].stress[0].pes = '0'
                        self.nomes_sillabes[self.objectiu].pes = '0'
                        self.patro[self.objectiu] = 0
            self.recompte_sillabes_metriques = recompte_metric(self)
            self.recompte_sillabes_extrametriques = len(self.patro) - self.recompte_sillabes_metriques
            self.posicio_tall = tall(self)
            self.subdivisio = f"{self.posicio_tall}+{self.recompte_sillabes_metriques - self.posicio_tall}" if self.posicio_tall is not None else None
        elif int(sense_mots[self.objectiu-1].pes) == 1:
            for word in self.words:
                if sense_mots[self.objectiu - 1] in word.stress:
                    word.stress[word.stress.index(sense_mots[self.objectiu - 1])].pes = '0'
                    self.nomes_sillabes[self.objectiu - 1].pes = '0'
                    self.patro[self.objectiu - 1] = 0
                    if len(sense_mots[self.objectiu - 1].pes) > 1 and self.words.index(word) + 1 == len(self.words) - 1:
                        self.words[self.words.index(word) + 1].stress[0].pes = '0'
                        self.nomes_sillabes[self.objectiu].pes = '0'
                        self.patro[self.objectiu] = 0
            self.recompte_sillabes_metriques = recompte_metric(self)
            self.recompte_sillabes_extrametriques = len(self.patro) - self.recompte_sillabes_metriques
            self.posicio_tall = tall(self)
            self.subdivisio = f"{self.posicio_tall}+{self.recompte_sillabes_metriques - self.posicio_tall}" if self.posicio_tall is not None else None
    except IndexError:
        pass
