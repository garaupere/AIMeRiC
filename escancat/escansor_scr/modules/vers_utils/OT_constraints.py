"""Aquest mòdul conté les funcions per a detectar la violació de les restriccions de l'OT."""
import re


def clash(pattern):
    """Compta les violacions de *CLASH, Jiménez (2019)"""
    if pattern is not None:
        return len(re.findall('SS', pattern)) + len((re.findall('SSS', pattern)))
    else:
        return 0


def lapse(pattern):
    """Compta les violacions de *LAPSE, Jiménez (2019)"""
    if pattern is not None:
        return len(re.findall('WWW', pattern)) + len(re.findall('WWWW', pattern))
    else:
        return 0


def ws_hl(pattern):
    """Compta les violacions de *WS-HL, Jiménez (2019)"""
    if pattern is not None:
        return len(re.findall('SS$', pattern))
    else:
        return 0


def non_initial(pattern):
    """Compta les violacions de *NON-INITIAL, Jiménez (2019)"""
    if pattern is not None:
        return len(re.findall('^S', pattern))
    else:
        return 0


def symetry(pattern):
    """Compta les violacions de *SYMETRY, Jiménez (2019)"""
    if pattern is not None:
        part_1 = pattern[:len(pattern) // 2]
        part_2 = pattern[len(pattern) // 2:]
        if part_1 == part_2:
            return 0
        else:
            return 1
    else:
        return 0


def analyze_OT(pattern):
    """Analitza les violacions de les restriccions de l'OT"""
    return clash(pattern), lapse(pattern), ws_hl(pattern), non_initial(pattern), symetry(pattern)
