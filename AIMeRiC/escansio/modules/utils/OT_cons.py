"""Aquest mòdul conté les funcions per a detectar la violació de les restriccions de l'OT."""
import re


def enjambment(encavalcament):
    """ALIGN-L (Line, L, Intonational phrase, L)-lines align with intonational
    phrases (Hayes 2009: 139)"""
    if encavalcament is True:
        return 1
    else:
        return 0


class OT_constraints:
    def __init__(self, pattern):
        self.pattern = pattern
        self.clash = self.clash()
        self.extra_clash = self.extra_clash()
        self.lapse = self.lapse()
        self.extra_lapse = self.extra_lapse()
        self.ws_hl = self.ws_hl()
        self.non_initial = self.non_initial()
        self.symetry = self.symetry()

    def eval(self):
        """Aquesta funció avalua les restriccions OT per a cada patró"""
        eval = []
        eval.append(self.clash)
        eval.append(self.extra_clash)
        eval.append(self.lapse)
        eval.append(self.extra_lapse)
        eval.append(self.ws_hl)
        eval.append(self.non_initial)
        eval.append(self.symetry)
        return eval

    def weigth(self, frequency):
        """Calcula el pes de cada restricció"""

        # Per a cada argument de la funció, multiplica el valor de la restricció per la freqüència del patró
        clash = self.clash * frequency
        extra_clash = self.extra_clash * frequency
        lapse = self.lapse * frequency
        extra_lapse = self.extra_lapse * frequency
        ws_hl = self.ws_hl * frequency
        non_initial = self.non_initial * frequency
        symetry = self.symetry * frequency
        return {'clash': clash, 'extra-clash': extra_clash, 'lapse': lapse, 'extra-lapse': extra_lapse, 'ws-hl': ws_hl,
                'non-initial': non_initial, 'symetry': symetry}

    def clash(self):
        """Compta les violacions de *CLASH, Jiménez (2019)"""
        if self.pattern is not None:
            return len(re.findall('11', self.pattern))
        else:
            return 0

    def extra_clash(self):
        """Compta les violacions de *EXTRA-CLASH, Jiménez (2019)"""
        if self.pattern is not None:
            return len((re.findall('111', self.pattern)))
        else:
            return 0

    def lapse(self):
        """Compta les violacions de *LAPSE, Jiménez (2019)"""
        if self.pattern is not None:
            return len(re.findall('000', self.pattern))
        else:
            return 0

    def extra_lapse(self):
        """Compta les violacions de *EXTRA-LAPSE, Jiménez (2019)"""
        if self.pattern is not None:
            return len(re.findall('0000', self.pattern))
        else:
            return 0

    def ws_hl(self):
        """Compta les violacions de *WS-HL, Jiménez (2019)"""
        if self.pattern is not None:
            return len(re.findall('11$', self.pattern))
        else:
            return 0

    def non_initial(self):
        """Compta les violacions de *NON-INITIAL, Jiménez (2019)"""
        if self.pattern is not None:
            return len(re.findall('^1', self.pattern))
        else:
            return 0

    def symetry(self):
        """Compta les violacions de *SYMETRY, Jiménez (2019)"""
        if self.pattern is not None:
            part_1 = self.pattern[:len(self.pattern) // 2]
            part_2 = self.pattern[len(self.pattern) // 2:]
            if part_1 == part_2:
                return 0
            else:
                return 1
        else:
            return 0

    def foot_bin(self):
        """Els peus han de contenir dues síl·labes. (Violat pels peus ternaris i els peus degenerats.)"""
        iambs = len(re.findall('01', self.pattern))
        return (len(self.pattern) / 2) - iambs

    def colon_bin(self):
        """Els hemistiquis han de contenir dos peus mètrics. (Violat pels hemistiquis ternaris o pels hemistiquis amb un únic peu, i. e., amb una sola posició tònica.)"""
        bin_col = len(re.findall('0101', self.pattern))
        if bin_col < 4:
            return abs((len(self.pattern) / 5) - bin_col)
        else:
            return abs((len(self.pattern) / 5) - (bin_col / 2))

    def verse_bin(self):
        """Els versos han de contenir dos hemistiquis. (Violat pels dodecasíl·labs continus, sense particions, i pels alexandrins trimembres amb tres còlons.)"""
        colon_part = [3, 4, 5]  # Talls més freqüents en el decasíl·lab català (cal sumar-los-hi 1) = [4, 5, 6] (ordenats per freqüència d'ús)
        for position in colon_part:
            if self.pattern[position] == '1':
                return 0
        return 1

    def fit(self):
        """Les llengües seleccionen metres en què el vocabulari complet pot ser usat en una varietat més gran de formes."""


    def list_constraints(self):
        """Retorna una llista amb les restriccions de l'OT segons apareixen a la __init__"""
        cons = []
        for key in self.__dict__.items():
            if key[0] != 'pattern':
                cons.append(key[0])
        return cons
