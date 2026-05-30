__author__ = "Pere Garau Borràs"
__copyright__ = "Copyright © 2025, Pere Garau Borràs"
__version__ = "0.9.1"

import spacy
import traceback
from AIMeRiC.escansio.modules.vers import Vers

# Constant de debug
DEBUG = False


def escaneja(nlp, verse: str, goal: int, permet_llicencies: bool = True) -> Vers | None:
    """Aquesta funció etiqueta un vers i retorna un objecte de la classe Verse.
    Si hi ha una excepció, retorna None però registra el motiu per ajudar a depurar.
    """
    try:
        return Vers(nlp, verse, goal, permet_llicencies)
    except Exception as e:
        if DEBUG:
            print(f"\n[ERROR] Excepció en escanejar el vers:\n\tVers: {verse!r}\n\tTipus: {type(e).__name__}: {e}")
            traceback.print_exc()
        return None


def escaneja_minim(nlp, verse: str, goal: int, permet_llicencies: bool = False) -> Vers | None:
    """Aquesta funció etiqueta un vers i retorna un objecte de la classe Verse amb informació mínima."""
    try:
        return Vers(nlp, verse, goal, permet_llicencies, minimal=True)
    except Exception:
        return None


if __name__ == "__main__":
    nlp = spacy.load('ca_core_news_lg')
    exemple = "Que jo sóc Dionís i sóc Narcís."

    escaner = escaneja(nlp, exemple, 10)
    escaner.mostra()

    escaner = escaneja_minim(nlp, exemple, 10)
    escaner.mostra_minimal()