"""Un mòdul per gestionar particularitats mètriques del decasíl·lab"""
import re

from .fonologia import force_subs
from .tools import seguent


def find_tall(self, tall) -> bool:
    """Aquesta funció cerca un tall en un vers donat i en substitueix el pes accentual per un cim màxim (5)."""
    result = False  # Resultat de la cerca
    if int(self.no_words[tall].pes) > 1:  # Si el valor correspon a un accent
        for paraula in self.words:  # Recorre les paraules del vers
            if paraula.stress[-1] == self.no_words[tall]:  # La síl·laba del tall coincideix amb l'última de la paraula (frontera de mot)
                paraula.stress[-1].pes = '5'
                self.annotated[
                    self.words.index(paraula)] = paraula.stress  # Actualitza l'estructura de l'accentuació
                self.no_words[tall].pes = '5'  # Actualitza la llista de mots
                self.pattern[tall] = 5  # Actualitza el patró abstracte
                self.words[
                    self.words.index(paraula)].paraula_tall = True  # Indica que la paraula és frontera de tall
                self.words[self.words.index(paraula)] = paraula  # Actualitza la paraula
                result = True  # Indica que s'ha trobat un tall
                return result  # Retorna True si s'ha trobat un tall
    return result  # Retorna False si no s'ha trobat cap tall


def tall(self) -> int or None:
    """Aquesta funció aplica la cesura al vers."""
    if self.recompte_sillabes_metriques == 10:  # Si el vers és decasíl·lab
        talls = [3, 4, 5]  # Talls més freqüents en el decasíl·lab català (cal sumar-los-hi 1) = [4, 5, 6] (ordenats per freqüència d'ús)
        tall = talls[0]
        cerca = find_tall(self, tall)  # Cerca el primer tall
        hist = [cerca]  # Històric de cerques
        i = 0  # Índex de tall
        while cerca is not True and i < len(talls) - 1:  # Mentre no s'hagi trobat cap tall i no s'hagin provat tots
            i += 1  # Següent tall
            tall = talls[i]  # Següent tall
            hist.append(cerca)  # Històric de cerques
            cerca = find_tall(self, tall)  # Cerca el següent tall
        hist.append(cerca)  # Històric de cerques
        if True in hist:  # Si s'ha trobat un tall
            return tall + 1  # Retorna la posició del tall
        else:  # Si no s'ha trobat cap tall
            return None  # Retorna None
    else:
        return None


def subdivideix(self):
    """Aquesta funció subdivideix el vers en còlons si conté un tall."""
    return f'{self.recompte_sillabes_metriques - self.posicio_tall}+{self.posicio_tall}' if self.posicio_tall is not None else None


def cesura_femenina(self):
    """Aquesta funció aplica la cesura femenina al vers."""
    if len(self.sillables_metriques) == 11:
        # if len(re.findall("[_:]", ''.join([x.text for x in self.no_words[4:6]]))) < 0:
        if int(self.no_words[4].pes) >= 4:
            for word in self.words:
                for syllable in word.stress:
                    if syllable == self.no_words[4]:
                        if seguent(syllable, word.stress) is not None:
                            if re.findall("[:_]", seguent(syllable, word.stress).text):
                                # Gestiona els casos de sinalefa en la cesura, ex.: *jo som la page<sa_amb> els records honrats
                                fsubs = force_subs(seguent(syllable, word.stress))
                                syl1 = fsubs[0]
                                syl2 = fsubs[1]
                                word.stress[syllable.s_index + 1] = syl1
                                self.words[word.w_index + 1].stress.insert(0, syl2)
                                break
                            syllable.pes = '5'
                            self.no_words[4].pes = '5'
                            self.pattern[4] = 5
                            ignore_syll = word.stress[word.stress.index(syllable) + 1]
                            del word.stress[word.stress.index(syllable) + 1:]
                            self.actualitza()
                            self.subdivision = "5'+5"
                            self.string = '#'.join(
                                ['.'.join([syllable.text for syllable in word.stress]) for word in
                                 self.words[:word.w_index + 1]]) + ".<" + ignore_syll.text + '>#' + '#'.join(
                                ['.'.join([syllable.text for syllable in word.stress]) for word in
                                 self.words[word.w_index + 1:]])
                            self.string_stress = '#'.join(
                                [word.plain() for word in
                                 self.words[:word.w_index + 1]]) + ".<" + ignore_syll.text + '>#' + '#'.join(
                                [word.plain() for word in self.words[word.w_index + 1:]])
