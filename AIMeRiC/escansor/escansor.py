import spacy
from AIMeRiC.escansor.modules.verse import Vers


def escaneja(nlp, verse: str, goal: int) -> Vers:
    """Aquesta funció etiqueta un vers i retorna un objecte de la classe Verse."""
    from AIMeRiC.escansor.modules.verse import Vers
    return Vers(nlp, verse, goal)


if __name__ == "__main__":
    nlp = spacy.load('ca_core_news_lg')
    exemple = "A Ella els cors en la justa futura."
    escaner = escaneja(nlp, exemple, 10)
    escaner.mostra()
