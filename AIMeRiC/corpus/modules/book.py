from typing import Dict, List, Optional


class Book:
    """
    Representa un llibre de l'autor.

    Paràmetres:
        book (str): Títol o identificador del llibre.
        author_content (Dict): Contingut de l'autor en format de diccionari.

    Atributs:
        number (str): Identificador o títol del llibre.
        book_content (Optional[Dict]): Contingut del llibre en format de diccionari.
        title (Optional[str]): Títol del llibre.
        year (Optional[str]): Any de publicació.
        publisher (Optional[str]): Editorial del llibre.
        poems (List[Dict]): Llista de poemes dins del llibre.
        n_poems (int): Nombre de poemes en el llibre.
        n_verses (int): Nombre total de versos en el llibre.
    """

    def __init__(self, book: str, author_content: Dict):
        self.number: str = book  # Títol o identificador del llibre
        self.author_content: Dict = author_content  # Contingut de l'autor en format de diccionari
        self.book_content: Optional[Dict] = None
        self.title: Optional[str] = None
        self.year: Optional[int] = None
        self.translation: Optional[bool] = None
        self.publisher: Optional[str] = None
        self.poems: List[Dict] = []
        self.n_poems: int = 0
        self.n_verses: int = 0

        # Carrega el contingut del llibre
        self._load_book_content()

    def _load_book_content(self):
        """
        Carrega el contingut del llibre des de `author_content`.
        Si el llibre o l'autor no existeixen, mostra un missatge d'error adequat.
        """
        if not self.author_content:
            print(f'Error: El contingut de l\'autor no està disponible.')
            return

        self.book_content = self.author_content.get('books', {}).get(self.number)
        if self.book_content:
            self.title = self.book_content.get('title')
            self.year = self.book_content.get('year')
            self.publisher = self.book_content.get('publisher')
            self.translation = self.book_content.get('translation', False) is True
            self.poems = self.book_content.get('poems', [])
            self.n_poems = len(self.poems)
            self.n_verses = sum(len(poem) for poem in self.poems)  # Nombre total de versos
        else:
            print(f'Error: "{self.number}" no és un títol vàlid de l\'autor.')

    def print_metadata(self) -> str:
        """
        Retorna una cadena amb la metadata del llibre.

        Retorna:
            str: Cadena amb la informació bàsica del llibre.
        """
        return (
            f"\tBook: {self.number}\n"
            f"\tTitle: {self.title}\n"
            f"\tYear: {self.year}\n"
            f"\tPublisher: {self.publisher}\n"
            f"\tTranslation: {self.translation}\n"
            f"\tPoems: {self.n_poems}\n"
        )

    def save_metadata(self) -> Dict[str, any]:
        """
        Retorna un diccionari amb la metadata del llibre, incloent una estructura inicial per als poemes.

        Retorna:
            Dict: Diccionari amb la informació del llibre i el nombre de poemes i versos.
        """
        return {
            self.number: {
                "title": self.title,
                "year": self.year,
                "publisher": self.publisher,
                "translation": self.translation,
                "poems": {},  # Estructura inicial per a guardar poemes
                "n_poems": self.n_poems,
                },
            "n_verses": self.n_verses
            }
