import json
from typing import List, Dict, Any, Optional


class Author:
    """
    Representa un autor i permet carregar informació des d'un fitxer JSON.

    Paràmetres:
        path (str): Ruta al fitxer JSON amb la informació de l'autor.

    Atributs:
        path (str): Ruta al fitxer JSON.
        content (Optional[Dict[str, Any]]): Diccionari amb el contingut JSON.
        id (Optional[str]): Identificador de l'autor.
        name (Optional[str]): Nom de l'autor.
        gender (Optional[str]): Gènere de l'autor.
        born_date (Optional[str]): Data de naixement de l'autor.
        death_date (Optional[str]): Data de defunció de l'autor.
        city (Optional[str]): Ciutat de l'autor.
        dialect (Optional[str]): Dialecte de l'autor.
        viaf (Optional[str]): identificador VIAF.
        wiki_id (Optional[str]): identificador wikidata.
        books (List[str]): Llista de llibres de l'autor.

    Mètodes:
        read_corpus: Llegeix el fitxer JSON.
        n_books: Retorna el nombre de llibres de l'autor.
        print_metadata: Retorna una cadena amb la metadata de l'autor.
        save_metadata: Retorna un diccionari amb la metadata de l'autor.
    """

    def __init__(self, path: str):
        self.path = path
        self.content: Optional[Dict[str, Any]] = None
        self.id: Optional[str] = None
        self.name: Optional[str] = None
        self.gender: Optional[int] = None
        self.born_date: Optional[int] = None
        self.death_date: Optional[int] = None
        self.city: Optional[str] = None
        self.dialect: Optional[str] = None
        self.viaf: Optional[str] = None
        self.wiki_id: Optional[str] = None
        self.font: Optional[str] = None
        self.books: List[str] = []
        self._load_author_data()

    def _load_author_data(self):
        """
        Carrega les dades de l'autor des del fitxer JSON especificat en `path`.
        Gestiona els errors de fitxer no trobat i format JSON invàlid.
        """
        self.content = self.read_corpus(self.path)
        if self.content:
            self.id = self.content.get('author_id').replace('\xad', '') if self.content.get('author_id') else None
            self.name = self.content.get('name')
            self.gender = self.content.get('gender') if self.content.get('gender') else None
            self.born_date = self.content.get('born_date') if self.content.get('born_date') else None
            self.death_date = self.content.get('death_date') if self.content.get('death_date') else None
            self.city = self.content.get('city') if self.content.get('city') else None
            self.dialect = self.content.get('dialect') if self.content.get('dialect') else None
            self.viaf = self.content.get('viaf') if self.content.get('viaf') else None
            self.wiki_id = self.content.get('wiki_id') if self.content.get('wiki_id') else None
            self.font = self.content.get('font') if self.content.get('font') else None
            self.books = self.content.get('books', [])

    @staticmethod
    def read_corpus(path: str) -> Optional[Dict[str, Any]]:
        """
        Llegeix el fitxer JSON des del camí especificat.

        Retorna:
            Dict amb el contingut JSON si es carrega correctament, o None si hi ha un error.
        """
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f'Error: Fitxer no trobat a {path}.')
        except json.JSONDecodeError as e:
            print(f"Error: Format JSON invàlid en {path} (línia {e.lineno}, columna {e.colno}).")
        except Exception as e:
            print(f"Error inesperat: {e}")
        return None

    @property
    def n_books(self) -> int:
        """Retorna el nombre de llibres de l'autor."""
        return len(self.books)

    def print_metadata(self) -> str:
        """Retorna una cadena amb la metadata de l'autor."""
        return (
            f"Id: {self.id}\n"
            f"Name: {self.name}\n"
            f"Gender: {self.gender}\n"
            f"Born date: {self.born_date}\n"
            f"Death date: {self.death_date}\n"
            f"City: {self.city}\n"
            f"Dialect: {self.dialect}\n"
            f"VIAF: {self.viaf}\n"
            f"Wikidata ID: {self.wiki_id}\n"
            f"Font: {self.font}\n"
            f"Books: {self.n_books}\n"
        )

    def save_metadata(self) -> Dict[str, Any]:
        """
        Retorna un diccionari amb la metadata de l'autor, incloent una estructura buida per als llibres.

        Retorna:
            Diccionari amb la informació de l'autor, incloent-hi el nombre de llibres i una estructura inicial per a aquests.
        """
        return {
            "author_id": self.id,
            "name": self.name,
            "gender": self.gender,
            "born_date": self.born_date,
            "death_date": self.death_date,
            "city": self.city,
            "dialect": self.dialect,
            "viaf": self.viaf,
            "wiki_id": self.wiki_id,
            "font": self.font,
            "books": {},  # Estructura inicial per a guardar llibres
            "n_books": self.n_books
            }
