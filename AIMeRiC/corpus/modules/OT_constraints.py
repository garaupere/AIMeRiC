"""Aquest mòdul conté les funcions per a detectar la violació de les restriccions de l'OT."""
import re


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

    def list_constraints(self):
        """Retorna una llista amb les restriccions de l'OT segons apareixen a la __init__"""
        cons = []
        for key in self.__dict__.items():
            if key[0] != 'pattern':
                cons.append(key[0])
        return cons


def enjambment(data):
    """ALIGN-L (Line, L, Intonational phrase, L)-lines align with intonational
    phrases (Hayes 2009: 139)"""
    if data is True:
        return 1
    else:
        return 0
