"""Un mòdul per gestionar funcions mètriques del vers"""
import re


def recompte_metric(self):
    """Retorna la longitud de la llista fins a l'últim element més fort, que pot ser >=2."""
    count = 0
    llista = [int(value.pes) for value in self.nomes_sillabes]
    for value in reversed(llista):
        if value >= 2:
            break
        count += 1
    return len(llista) - count


def metre_ajustat(self):
    return True if self.recompte_sillabes_metriques == self.objectiu and int(self.patro_ritmic[
                                                                                 self.objectiu - 1]) > 1 else False


def abstract_pattern(words):
    """Retorna el patró abstracte del vers."""
    pattern = []  # Patró abstracte
    for word in words:  # Recorre les paraules del vers
        pattern.extend(
            [int(syllable.pes) for syllable in word.stress])  # Afegeix l'abstracció de cada síl·laba
    return pattern  # Retorna el patró abstracte


def maximal_comparison_pattern(self) -> str:
    result = self.patro_ritmic
    if self.objectiu == 10 and self.recompte_sillabes_metriques == self.objectiu:
        if self.recompte_sillabes_metriques == self.objectiu:
            dictionary = {r"5[43]": "5c",
                          r"[56789]": "4", r"[23]4": "04", r"4[23](.)": r"40\1", r"[43]2": "40", "2[34]": "04",
                          r"1([2345])": r"0\g<1>", r"([2345])1": r"\g<1>0",
                          r"0[23]0": "040", r"4[23]": "40",
                          r"0$": "4", r"[01]": "0", r"[432]": "1", r"c": "1"}
            for pattern, solution in dictionary.items():
                result = re.sub(pattern, solution, result)
            return result[0:self.objectiu]
        return result
    else:
        dictionary = {r"[56789]": "4", r"[23]4": "04", r"4[23](.)": r"40\1", r"[43]2": "40", "2[34]": "04",
                      r"1([2345])": r"0\g<1>", r"([2345])1": r"\g<1>0",
                      r"0[23]0": "040", r"4[23]": "40",
                      r"0$": "4", r"[01]": "0", r"[432]": "1"}
        for pattern, solution in dictionary.items():
            result = re.sub(pattern, solution, result)
        return result


def patro_metric_jerarquic(seq, model):
    from functools import lru_cache
    peus = [
        ('(001)', "001", 1),  # anapest
        ('(01)', "01", 2),  # iambe
        ('(10)', "10", 3),  # troqueu
        ('(010)', "010", 4),  # amfíbrac
        ('(100)', "100", 5),  # dàctil
        ('(1)', "1", 6),  # degenerat
    ]
    prio_dict = {p[0]: p[2] for p in peus}

    def sil_labes(u):
        if u == "0": return 1
        return sum(1 for c in u if c in "01")

    def totes_les_agrupacions(bits):
        @lru_cache(maxsize=None)
        def rec(i):
            if i == len(bits): return [([], 0, 0, ())]
            opcions = []
            for nom, patro, prio in peus:
                l = len(patro)
                if i + l <= len(bits) and bits[i:i + l] == patro:
                    for llista, z, m, seq in rec(i + l):
                        opcions.append(([nom] + llista, z, m + (1 if nom == '(1)' else 0), (prio,) + seq))
            if bits[i] == "0":
                for llista, z, m, seq in rec(i + 1):
                    opcions.append((["0"] + llista, z + 1, m, (99,) + seq))
            return opcions

        tot = rec(0)
        if not tot:
            return []
        # Restricció mínima: zeros, monosil·làbics
        min_zeros = min(x[1] for x in tot)
        tot = [x for x in tot if x[1] == min_zeros]
        min_mono = min(x[2] for x in tot)
        tot = [x for x in tot if x[2] == min_mono]
        # Aquí pots tenir diverses agrupacions igualment bones però que es diferencien en l’ordre (10) vs (01)
        # Per preferir lexicogràficament per la dreta (p.ex. [1,6,2] < [1,3,6]) cal ordenar per prio[::-1]
        tot.sort(key=lambda x: x[3][::-1])
        return tot

    # Troba el tall sil·làbic
    if model == "4+6":
        n1, n2 = 4, 6
    elif model == "6+4":
        n1, n2 = 6, 4
    elif model == "5+5":
        n1, n2 = 5, 5
    else:
        raise ValueError("Estructura desconeguda")

    compte, tall = 0, None
    for i, c in enumerate(seq):
        compte += 1
        if compte == n1:
            tall = i + 1
            break
    if tall is None:
        raise ValueError("No es troba el tall mètric.")

    bits1 = seq[:tall]
    bits2 = seq[tall:]

    opcions1 = totes_les_agrupacions(bits1)
    if not opcions1: raise ValueError("Cap agrupació en peus vàlida pel còlon 1")
    u1 = opcions1[0][0]

    opcions2 = totes_les_agrupacions(bits2)
    if not opcions2: raise ValueError("Cap agrupació en peus vàlida pel còlon 2")
    u2 = opcions2[0][0]

    patro = f"[{''.join(u1)}][{''.join(u2)}]"
    return patro


def extreu_peus(patro):
    """Extreu els peus (text entre parèntesis) d'un patró mètric"""
    try:
        peus = re.findall(r'\(([^)]+)\)', patro)
        return peus
    except TypeError:
        return None

def identifica_xocs(patro):
    try:
        return len(re.findall(r'[1-5][1-5]', patro))
    except TypeError:
        return None

def identifica_valls(patro):
    try:
        return len(re.findall(r'[0-1][0-1][0-1]', patro))
    except TypeError:
        return None