__author__ = "Pere Garau Borràs"
__copyright__ = "Copyright © 2025, Pere Garau Borràs"
__version__ = "0.6.2"

import spacy
from AIMeRiC.escansio.modules.verse import Vers


def escaneja(nlp, verse: str, goal: int, permet_llicencies: bool = True):
    """Aquesta funció etiqueta un vers i retorna un objecte de la classe Verse."""
    try:
        return Vers(nlp, verse, goal, permet_llicencies)
    except ValueError:
        print(f"Error: {ValueError}, en el vers: {verse}")


def escaneja_minim(nlp, verse: str, goal: int, permet_llicencies: bool = False):
    """Aquesta funció etiqueta un vers i retorna un objecte de la classe Verse amb informació mínima."""
    try:
        return Vers(nlp, verse, goal, permet_llicencies, minimal=True)
    except ValueError:
        print(f"Error: {ValueError}, en el vers: {verse}")


if __name__ == "__main__":
    nlp = spacy.load('ca_core_news_lg')
    exemple = "La Viquipèdia és part de la família de projectes sense ànim de lucre, multilingües i de contingut obert."
    escaner = escaneja(nlp, exemple, 10)
    escaner.mostra()

    escaner = escaneja_minim(nlp, exemple, 10)
    escaner.mostra_minimal()
