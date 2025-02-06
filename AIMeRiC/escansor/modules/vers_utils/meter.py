"""Un mòdul per gestionar funcions mètriques del vers"""
import re


def recompte_metric(self):
    """Retorna la longitud de la llista fins a l'últim element més fort, que pot ser >=2."""
    count = 0
    llista = [int(value.pes) for value in self.no_words]
    for value in reversed(llista):
        if value > 2:
            break
        count += 1
    return len(llista) - count


def metre_ajustat(self):
    return True if self.recompte_sillabes_metriques == self.goal else False


def abstract_pattern(words):
    """Retorna el patró abstracte del vers."""
    pattern = []  # Patró abstracte
    for word in words:  # Recorre les paraules del vers
        pattern.extend(
            [int(syllable.pes) for syllable in word.stress])  # Afegeix l'abstracció de cada síl·laba

    return pattern  # Retorna el patró abstracte


def words_abstract_pattern(words):
    """Retorna el patró abstracte del vers amb les fronteres de mot."""
    pattern = []  # Patró abstracte
    for word in words:  # Recorre les paraules del vers
        word = [int(syllable.pes) for syllable in word.stress]
        pattern.append(word)
    return pattern  # Retorna el patró abstracte


def maximal_comparison_pattern(self):
    if self.recompte_sillabes_metriques == self.goal:
        result = self.comparative_pattern
        dictionary = {r"[56789]": "4", r"[23]4": "04", r"4[23](.)": r"40\1", r"[43]2": "40", "2[34]": "04",
                      r"1([2345])": r"0\g<1>", r"([2345])1": r"\g<1>0",
                      r"0[23]0": "040", r"4[23]": "40",
                      r"0$": "4", r"[01]": "W", r"[432]": "S"}
        for pattern, solution in dictionary.items():
            result = re.sub(pattern, solution, result)
        return result[0:10]