"""Aquest mòdul conté les funcions per a detectar la violació de les restriccions de l'OT."""
import re


def group_feet(pattern):
    feet = re.sub('01', '.01.', pattern)
    feet = re.sub('11', '.1.1.', feet)
    feet = re.sub(r'\.+', '.', feet)
    feet = re.sub('(001|\.?0.01)', '.001.', feet)
    feet = re.sub(r'\.+', '.', feet)
    feet = [x for x in feet.split('.') if x != '']
    return feet

def enjambment(encavalcament):
    """ALIGN-L (Line, L, Intonational phrase, L)-lines align with intonational
    phrases (Hayes 2009: 139)"""
    if encavalcament is True:
        return 1
    else:
        return 0


def extrametrical(sillabes_extrametriques):
    return sillabes_extrametriques


class OT_constraints:
    def __init__(self, pattern):
        self.pattern = pattern
        self.feet = group_feet(self.pattern)
        self.clash = self.clash()
        self.extra_clash = self.extra_clash()
        self.lapse = self.lapse()
        self.extra_lapse = self.extra_lapse()
        self.ws_hl = self.ws_hl()
        self.non_initial = self.non_initial()
        self.symetry = self.symetry()
        self.foot_bin = self.foot_bin()
        self.colon_bin = self.colon_bin()
        self.verse_bin = self.verse_bin()
        self.fit = self.fit()
        self.interest = self.interest()
        self.long_last = self.long_last()

    def eval(self):
        """Aquesta funció avalua les restriccions OT per a cada patró"""
        eval = []
        cons = self.list_constraints()
        for con in cons:
            eval.append(getattr(self, con))
        return eval

    def weigth(self, frequency):
        """Calcula el pes de cada restricció"""

        # Per a cada argument de la funció, multiplica el valor de la restricció per la freqüència del patró
        cons = self.list_constraints()
        weigth = {con: getattr(self, con) * frequency for con in cons}
        return weigth




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
        cons = 0
        for foot in self.feet:
            if len(foot) > 2 or len(foot) < 2:
                cons += 1
        return cons

    def colon_bin(self):
        """Els hemistiquis han de contenir dos peus mètrics. (Violat pels hemistiquis ternaris o pels hemistiquis amb un únic peu, i. e., amb una sola posició tònica.)"""
        bin_col = len(re.findall('0101', self.pattern))
        if bin_col < 4:
            return int(abs((len(self.pattern) / 5) - bin_col))
        else:
            return int(abs((len(self.pattern) / 5) - (bin_col / 2)))

    def verse_bin(self):
        """Els versos han de contenir dos hemistiquis. (Violat pels dodecasíl·labs continus, sense particions, i pels alexandrins trimembres amb tres còlons.)"""
        colon_part = [3, 4,
                      5]  # Talls més freqüents en el decasíl·lab català (cal sumar-los-hi 1) = [4, 5, 6] (ordenats per freqüència d'ús)
        for position in colon_part:
            if self.pattern != '' and list(self.pattern)[position] == '1':
                return 0
            elif not '|' in self.pattern:
                return 1

    def fit(self):
        """Les llengües seleccionen metres en què el vocabulari complet pot ser usat en una varietat més gran de formes.
        Assumim que el peu mètric prototipic del català és el troqueu (Lloret). Comptam l'ocurrència de troqueus en el patró i restam l'ocurrència de peus."""
        # Divideix el pattern en grups de dos
        pattern = [self.pattern[i:i + 2] for i in range(0, len(self.pattern), 2)]
        # Compta el nombre de troqueus
        trochees = len(re.findall('01', self.pattern))
        # Compta el nombre de peus
        feet = len(re.findall('1', self.pattern))
        return feet - trochees

    def interest(self):
        """"Els paràmetres del vers es configuren de manera que es maximitze l’interès estètic del vers. Plantejat com: el vers no ha de presentar l'estructura tipificada del decasíl·lab"""
        tipic = ['0101010101', '0101001001', '0010010101']  # Segons Oliva (2008)
        if self.pattern in tipic:
            return 1
        else:
            return 0

    def long_last(self):
        """"En una seqüència de grups de llargària desigual, els membres més llargs han d’anar els últims."""
        cons = [x for x in re.findall(r'^(001001|000001|0010001|0001001|)', self.pattern) if x != '']
        return len(cons)

    def list_constraints(self):
        """Retorna una llista amb les restriccions de l'OT segons apareixen a la __init__"""
        cons = []
        for key in self.__dict__.items():
            if key[0] not in ['pattern', 'feet']:
                cons.append(key[0])
        return cons
