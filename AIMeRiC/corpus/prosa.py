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
                    poem = Poem(poem_title, book.book_content)  # Crea un objecte Poema
                    poem.print_metadata()  # Imprimeix la metadata del poema
                    results_dict['books'][book_title]['poems'].update(
                        poem.save_metadata())  # Guarda la metadata del poema

                    i = 0

                    for verse in poem.verses:  # Per cada vers del poema
                        if len(verse) > 50:
                            vers = escaneja(nlp, verse, goal=mode)  # Crea un objecte Vers

                            if verse is not None:
                                results_dict['books'][book_title]['poems'][poem_title]['verses'].update(
                                    vers.desa_prosa())  # Guarda la metadata del vers format prosa
                                print(dades_prosa(vers))
                            i += 1

        os.makedirs(f"{results_path}json/", exist_ok=True)
        with open(f"{results_path}json/{author.id}.json", 'w',
                  encoding='utf-8') as f:  # Guarda els resultats en un fitxer JSON
            json.dump(results_dict, f, indent=4, ensure_ascii=False)

        os.makedirs(f"{results_path}svg/", exist_ok=True)
        os.makedirs(f"{results_path}xlsx/", exist_ok=True)

    corpus_name = corpus_path.split('/')[2]
    merge_tables(results_path, corpus_name)


def dades_prosa(vers: Vers):
    """Retorna dades sobre el ritme del fragment en prosa."""
    # Normalitza els valors accentuals del pattern: lambda x: 1 if x > 1 else 0
    vers.pattern = [1 if x > 1 else 0 for x in vers.pattern]

    pattern = ''.join([str(x) for x in vers.pattern])
    pattern = re.sub(r'01', '01.', pattern)
    pattern = re.sub(r'0\.?01', '001.', pattern)
    pattern = re.sub(r'10', '10.', pattern)
    pattern = re.sub(r'100', '100.', pattern)
    pattern = re.sub(r'\.1\.0', '.10', pattern)
    pattern = re.sub('101.', '10.1', pattern)
    pattern = re.sub(r'01', '01.', pattern)
    pattern = re.sub(r'0\.?01', '001.', pattern)
    pattern = re.sub(r'10', '10.', pattern)
    pattern = re.sub(r'100', '100.', pattern)
    pattern = re.sub('\.+', '.', pattern)

    pattern = pattern.split('.')
    # Calcula el total de síl·labes de la llista pattern

    iambe = '01'
    troqueu = '10'
    anapest = '001'
    dactil = '100'

    # Compta la freqüència de cada peu en pattern
    freq_iambe = pattern.count(iambe) / len(pattern) * 100
    freq_troqueu = pattern.count(troqueu) / len(pattern) * 100
    freq_anapest = pattern.count(anapest) / len(pattern) * 100
    freq_dactil = pattern.count(dactil) / len(pattern) * 100
    freq_altes = 100 - (freq_iambe + freq_troqueu + freq_anapest + freq_dactil)

    return {'iambe': freq_iambe, 'troqueu': freq_troqueu, 'anapest': freq_anapest, 'dactil': freq_dactil, 'altres': freq_altes}


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
