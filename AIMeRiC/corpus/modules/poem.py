import re
from typing import List, Dict, Optional


class Poem:
    """
    Representa un poema dins d'un llibre.

    Paràmetres:
        poem (str): Títol o identificador del poema.
        book_content (Dict): Contingut del llibre en format de diccionari.

    Atributs:
        poem (str): Identificador o títol del poema.
        book_content (Dict): Contingut del llibre.
        verses (List[str]): Llista de versos del poema.
        n_verses (int): Nombre de versos en el poema.
        page (str): Número de pàgina on es troba el poema.
    """

    def __init__(self, poem: str, book_content: Dict):
        self.poem: str = poem  # Títol o identificador del poema
        self.book_content: Dict = book_content  # Contingut del llibre
        self.verses: List[str] = []
        self.n_verses: int = 0
        self.page: Optional[str] = None

        # Carrega el contingut del poema
        self._load_poem_content()

    def _load_poem_content(self):
        """
        Carrega el contingut del poema des de `book_content`.
        Si el poema o el llibre no tenen dades, genera un error adequat.
        """
        if not self.book_content:
            raise ValueError('Error: El contingut del llibre no està disponible.')

        # Obtenim els versos del poema, eliminant els valors nuls
        self.verses = list(filter(None, self.book_content.get('poems', {}).get(self.poem, [])))

        self.n_verses = len(self.verses)
        self.page = re.sub(r"(\d+)(\.txt)", r"\1", self.poem)  # Extracció del número de pàgina del títol del poema

    def print_metadata(self) -> str:
        """
        Retorna una cadena amb la metadata del poema.

        Retorna:
            str: Cadena amb la informació bàsica del poema.
        """
        return (
            f"\t\tPoem: {self.poem}\n"
            f"\t\tVerses: {self.n_verses}\n"
        )

    def print_verses(self) -> str:
        """
        Retorna una cadena amb tots els versos del poema, separats per noves línies.

        Retorna:
            str: Tots els versos del poema en línies separades.
        """
        return '\n'.join(self.verses)

    def save_metadata(self) -> Dict[str, Dict[str, int]]:
        """
        Retorna un diccionari amb la metadata del poema, incloent-hi una estructura inicial per als versos.

        Retorna:
            Dict: Diccionari amb la informació del poema i el nombre de versos.
        """
        return {
            self.poem: {
                'verses': {},  # Estructura inicial per a guardar versos
                'n_verses': self.n_verses
                }
            }
