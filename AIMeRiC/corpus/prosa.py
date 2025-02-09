import os
import re
import json
import time
import spacy
import pandas as pd
from datetime import datetime
from tqdm import tqdm

from AIMeRiC.corpus.etiqueta import merge_tables
from AIMeRiC.corpus.modules.getUSB import getUSB
from AIMeRiC.corpus.modules.author import Author
from AIMeRiC.corpus.modules.book import Book
from AIMeRiC.corpus.modules.poem import Poem
from AIMeRiC.escansor.escansor import escaneja
from AIMeRiC.escansor.modules.verse import Vers


def prosa(nlp):
    corpus_path = f"{getUSB()}/corpora/prosa/sense_etiquetar/json/"
    results_path = f"{getUSB()}/corpora/prosa/etiquetat/"
    versio = datetime.now().strftime('%Y.%m.%d')
    etiqueta(corpus_path, results_path, versio, nlp, mode=100)


def etiqueta(corpus_path: str, results_path: str, versio: str, nlp, mode: int = 10):
    global rows
    os.makedirs(f"{results_path}", exist_ok=True)

    head = ['id', 'autor', 'book', 'year', 'text', 'string_stress', 'recompte_sillabes_metriques', 'recompte_sillabes_extrametriques', 'pattern', 'maxpattern', 'clash', 'lapse', 'ws_hl', 'non_initial', 'symetry',
            'metronome', 'iambes', 'troqueus', 'anapests', 'dàctils', 'peus']

    for file in tqdm(os.listdir(corpus_path), desc="Etiquetant el corpus", leave=True, position=0,
                     ncols=80):  # Per cada autor del corpus
        author = Author(os.path.join(corpus_path, file))  # Crea un objecte Autor
        author.print_metadata()  # Imprimeix la metadata de l'autor
        results_dict = author.save_metadata()  # Guarda la metadata de l'autor

        rows = []
        for book_title in author.books:  # Per a cada llibre de l'autor
            book = Book(book_title, author.content)  # Crea un objecte Llibre
            book.print_metadata()  # Imprimeix la metadata del llibre
            results_dict['books'].update(book.save_metadata())  # Guarda la metadata del llibre

            for poem_title in book.poems:  # Per cada poema del llibre
                if book.poems[poem_title]:  # Si el poema no és buit
                    pagina = Poem(poem_title, book.book_content)  # Crea un objecte Poema
                    pagina.print_metadata()  # Imprimeix la metadata del poema
                    results_dict['books'][book_title]['poems'].update(
                        pagina.save_metadata())  # Guarda la metadata del poema

                    i = 1

                    for paragraf in pagina.verses:  # Per cada vers del poema
                        if len(paragraf) > 50:
                            paragrafs = re.split(r'[.?!:;]', paragraf) # Separa els paràgrafs en enunciats més curts
                            sub_i = 1
                            for paragraf in paragrafs:

                                if len(paragraf) > 40:
                                    linia = escaneja(nlp, paragraf, goal=40)  # Crea un objecte Vers

                                    if paragraf is not None:
                                        results_dict['books'][book_title]['poems'][poem_title]['verses'].update(linia.desa_prosa())  # Guarda la metadata del vers format prosa
                                        row = [f"{i}.{sub_i}", author.name, book_title, book.year] + linia.prosa_to_csv() + dades_prosa(linia)
                                        print(row)
                                        rows.append(row)
                                        sub_i += 1

                            i += 1

        os.makedirs(f"{results_path}json/", exist_ok=True)
        with open(f"{results_path}json/{author.id}.json", 'w',
                  encoding='utf-8') as f:  # Guarda els resultats en un fitxer JSON
            json.dump(results_dict, f, indent=4, ensure_ascii=False)

        os.makedirs(f"{results_path}csv/", exist_ok=True)
        with open(f"{results_path}csv/{author.id}.csv", 'w',
                  encoding='utf-8') as f:  # Guarda els resultats en un fitxer CSV
            df = pd.DataFrame(rows, columns=head)
            df.to_csv(f, index=False, sep=';', encoding='utf-8', lineterminator='\n', header=True, decimal=',', float_format='%.2f')

        os.makedirs(f"{results_path}svg/", exist_ok=True)
        os.makedirs(f"{results_path}xlsx/", exist_ok=True)

    corpus_name = corpus_path.split('/')[2]
    merge_tables(results_path, corpus_name)


def dades_prosa(vers: Vers):
    """Retorna dades sobre el ritme del fragment en prosa."""
    # Normalitza els valors accentuals del pattern: lambda x: 1 if x > 1 else 0
    vers.pattern = [1 if x > 1 else 0 for x in vers.pattern]

    def group_syllables(syllables):
        iambes = []
        troqueus = []
        anapests = []
        dactyls = []
        ordered_groups = []

        i = 0
        while i < len(syllables):
            if i + 1 < len(syllables) and syllables[i:i + 2] == [0, 1]:
                iambes.append([0, 1])
                ordered_groups.append([0, 1])
                i += 2
            elif i + 1 < len(syllables) and syllables[i:i + 2] == [1, 0]:
                troqueus.append([1, 0])
                ordered_groups.append([1, 0])
                i += 2
            elif i + 2 < len(syllables) and syllables[i:i + 3] == [0, 0, 1]:
                anapests.append([0, 0, 1])
                ordered_groups.append([0, 0, 1])
                i += 3
            elif i + 2 < len(syllables) and syllables[i:i + 3] == [1, 0, 0]:
                dactyls.append([1, 0, 0])
                ordered_groups.append([1, 0, 0])
                i += 3
            else:
                ordered_groups.append([syllables[i]])
                i += 1

        return iambes, troqueus, anapests, dactyls, ordered_groups

    iambes, troqueus, anapests, dactyls, ordered_groups = group_syllables(vers.pattern)

    iambes = len(iambes) / len(vers.pattern) * 100
    troqueus = len(troqueus) / len(vers.pattern) * 100
    anapests = len(anapests) / len(vers.pattern) * 100
    dactyls = len(dactyls) / len(vers.pattern) * 100
    ordered_groups = sum(len(x) for x in ordered_groups) == len(vers.pattern)

    return [iambes, troqueus, anapests, dactyls, ordered_groups]


if __name__ == "__main__":
    # Carrega el model de Spacy en català
    print("--" * 40)
    print(f"Carregant el model de Spacy 'ca_core_news_md' (versió {spacy.__version__})...")
    nlp = spacy.load("ca_core_news_md", disable=["ner"])
    print("Model carregat correctament.")
    print("--" * 40)
    versio = datetime.now().strftime('%Y.%m.%d')
    print(f"Versió de l'etiquetador: {versio}")

    usb = getUSB()
    root = f"{usb}/corpora/"

    print("--" * 40)
    for corpus_folder in os.listdir(root):
        if corpus_folder == 'prosa':
            print("S'ha activat el mode d'etiquetatge de prosa.")
            corpus_path = f"{root}{corpus_folder}/sense_etiquetar/json/"
            results_path = f"{root}{corpus_folder}/etiquetat/"
            start = time.time()
            etiqueta(corpus_path, results_path, versio, nlp, mode=7)

    elapsed_time = time.time() - start
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    print(f"Temps d'execució: {minutes} minuts i {seconds} segons")
    print("Fi de l'etiquetatge.")
