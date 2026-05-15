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
    return True if self.recompte_sillabes_metriques == self.objectiu else False


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


def patro_metric_PC(seq, subdivisio):
    """
    Donada una seqüència (ex: '0101010101' o '4040200405') i una subdivisió tipus '4+6',
    retorna un patró mètric tancant entre claudàtors cada còlón
    i entre parèntesis cada peu (amb almenys una tònica).
    - Les síl·labes àtones són '0' (simbol_w), les altres es consideren potencialment tòniques.
    - Si un peu és '0001', s'escriu com '0(001)'.

    Aquesta implementació és tolerant: accepta seqüències amb dígits diferents
    de '0'/'1' i també seqüències prefixades amb apòstrof ("'...").
    """

    simbol_w = '0'
    # Normalització de l'entrada: si ve amb apòstrof al davant (p.ex. export CSV), el retirem
    if isinstance(seq, str) and seq.startswith("'"):
        seq = seq[1:]
    # Convertir seq a llista de caràcters (ja sigui string o llistes d'elements)
    seq = [str(c) for c in seq]
    n_sil = len(seq)

    # Si no hi ha subdivisió vàlida, considerem tota la seq com un sol grup
    if not subdivisio or not isinstance(subdivisio, str) or '+' not in subdivisio:
        subdivisio = str(n_sil)

    talls_raw = [x.strip() for x in subdivisio.split('+') if x.strip()]
    out = []
    idx = 0
    for raw in talls_raw:
        try:
            t = int(raw)
        except Exception:
            # si no podem interpretar el tall, saltem-lo
            continue
        if t <= 0 or idx >= n_sil:
            continue

        grup = seq[idx:idx + t]
        # Indica les posicions de les tòniques dins del grup de subdivisió
        # Tolerant: considerem tòniques qualsevol caràcter diferent de simbol_w ('0')
        s_idx = [i for i, x in enumerate(grup) if x != simbol_w]
        if not s_idx:
            # si no hi ha tòniques dins del grup, saltem (mantindrem el grup amb àtones si cal)
            idx += t
            continue

        peus = []
        i = 0
        s_prox = list(s_idx)
        while i < len(grup):
            # Talla per peu: peu mínim 2, màxim fins a la següent tònica +1
            # (igual que patro_metric)
            # Troba la següent tònica
            next_s = None
            for s in s_prox:
                if s >= i:
                    next_s = s
                    break
            if next_s is not None:
                j = max(i + 2, next_s + 1)
            else:
                j = len(grup)
            if j > len(grup):
                j = len(grup)
            # Ara agafa el peu
            peu = grup[i:j]
            # Cas especial (qualsevol combinació que acabi en tònica amb 4 àtones prèvies)
            if len(peu) == 4 and all(p == simbol_w for p in peu[:3]) and peu[3] != simbol_w:
                peus.append(simbol_w + '(' + ''.join(peu[1:]) + ')')
            else:
                peus.append('(' + ''.join(peu) + ')')
            i = j
            # Neteja tòniques cobertes
            while s_prox and i > s_prox[0]:
                s_prox.pop(0)
        out.append('[' + ''.join(peus) + ']')
        idx += t
    return ''.join(out)
