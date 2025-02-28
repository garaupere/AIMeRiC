__author__ = "Pere Garau Borràs"
__copyright__ = "Copyright © 2025, Pere Garau Borràs"
__version__ = "0.4.3"

import spacy
from AIMeRiC.escansio.modules.verse import Vers


def escaneja(nlp, verse: str, goal: int):
    """Aquesta funció etiqueta un vers i retorna un objecte de la classe Verse."""
    return Vers(nlp, verse, goal)



if __name__ == "__main__":
    nlp = spacy.load('ca_core_news_lg')
    exemple = "A Ella els cors en la justa futura."
    escaner = escaneja(nlp, exemple, 10)
    escaner.mostra()
