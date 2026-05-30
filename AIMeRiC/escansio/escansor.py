__author__ = "Pere Garau Borràs"
__copyright__ = "Copyright © 2025, Pere Garau Borràs"
__version__ = "0.8.5"

import spacy
import traceback

from AIMeRiC.escansio.modules.vers import Vers


def escaneja(nlp, verse: str, goal: int, permet_llicencies: bool = True) -> Vers | None:
    """Aquesta funció etiqueta un vers i retorna un objecte de la classe Verse.
    Si hi ha una excepció, retorna None però registra el motiu per ajudar a depurar.
    """
    debug = False
    try:
        return Vers(nlp, verse, goal, permet_llicencies)
    except Exception as e:
        if debug:
            print("\n" + "[ERROR] Excepció en escanejar el vers:")
            print(f"	Vers: {verse!r}")
            print(f"	Tipus d'excepció: {type(e).__name__}: {e}")
            traceback.print_exc()
            return None


def escaneja_minim(nlp, verse: str, goal: int, permet_llicencies: bool = False) -> Vers | None:
    """Aquesta funció etiqueta un vers i retorna un objecte de la classe Verse amb informació mínima."""
    try:
        return Vers(nlp, verse, goal, permet_llicencies, minimal=True)
    except Exception as e:
#        print("\n" + "[ERROR] Excepció en escanejar (mínim) el vers:")
#        print(f"	Vers: {verse!r}")
#        print(f"	Tipus d'excepció: {type(e).__name__}: {e}")
#        traceback.print_exc()
        return None


if __name__ == "__main__":
    nlp = spacy.load('ca_core_news_lg')
    exemple = "em commou aquest altre que és més gran,"
    doc = nlp(exemple)

    escaner = escaneja(nlp, exemple, 10)
    escaner.mostra()

    escaner = escaneja_minim(nlp, exemple, 10)
    escaner.mostra_minimal()
