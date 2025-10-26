import glob
import json
import os
import re
import time

import winsound
from tqdm import tqdm
from datetime import datetime

import pandas as pd

import spacy

from AIMeRiC.corpus.modules.getUSB import getUSB
from AIMeRiC.corpus.modules.author import Author
from AIMeRiC.corpus.modules.book import Book
from AIMeRiC.corpus.modules.poem import Poem

from AIMeRiC.escansio.escansor import escaneja

usb = getUSB()


def merge_tables(results_path, file_name):
    data = []
    for csvfile in glob.glob(os.path.join(results_path + '/csv/', "*.csv")):
        df = pd.read_csv(csvfile, encoding="utf-8", delimiter=";")
        data.append(df)

    data = pd.concat(data, ignore_index=True)
    data.to_csv(f"{results_path}/{file_name}.csv", sep=';', decimal=',', encoding='utf-8',
                header=True, index=True)
    print(f"Corpus '{file_name}' etiquetat i compilat!")


def clean_results_folders(results_path):
    if os.path.exists(f"{results_path}/json/"):
        files = glob.glob(f"{results_path}/json/*")
        for f in files:
            if f.endswith(".json"):
                os.remove(f)
    if os.path.exists(f"{results_path}/csv/"):
        files = glob.glob(f"{results_path}/csv/*")
        for f in files:
            if f.endswith(".csv"):
                os.remove(f)
    if os.path.exists(f"{results_path}/log/"):
        files = glob.glob(f"{results_path}/log/*")
        for f in files:
            if f.endswith(".log"):
                os.remove(f)
    if os.path.exists(f"{results_path}/svg/"):
        files = glob.glob(f"{results_path}/svg/*")
        for f in files:
            if f.endswith(".svg"):
                os.remove(f)
    if os.path.exists(f"{results_path}/xlsx/"):
        files = glob.glob(f"{results_path}/xlsx/*")
        for f in files:
            if f.endswith(".xlsx"):
                os.remove(f)


def etiqueta(corpus_path: str, results_path: str, versio: str, nlp, mode: int = 10):
    global rows, df
    corpus_name = corpus_path.split('/')[2]
    os.makedirs(f"{results_path}", exist_ok=True)

    clean_results_folders(results_path)

    with open(f"{results_path}sumari.sum", 'w', encoding='utf-8') as sumari:
        sumari.write("Data;Versió;Autor;Versos;4+6;5+5;6+4;No classificats;Outsiders\n")

    for file in tqdm(os.listdir(corpus_path), desc="Etiquetant el corpus", leave=True, position=0,
                     ncols=80):  # Per cada autor del corpus
        #print(f'> Etiquetant el corpus de l\'autor {file}...')
        outsiders = []
        author = Author(os.path.join(corpus_path, file))  # Crea un objecte Autor
        author.print_metadata()  # Imprimeix la metadata de l'autor
        results_dict = author.save_metadata()  # Guarda la metadata de l'autor
        processed_verses = set()  # Conjunt de versos processats, per evitar duplicats
        scansion_cols = [str(col + 1) for col in range(0, mode)]
        head = (['autor_id', 'autor', 'naixement', 'defunció', 'gènere', 'ciutat', 'dialecte', 'wiki_id', 'viaf',
                 'obra', 'any', 'traducció', 'font',
                 'poema', 'núm. de vers', 'text del vers',
                 'escansió plana'] + scansion_cols +
                ['síl·labes mètriques', 'síl·labes extramètriques', 'subdivisió', 'llicències',
                 'mots al còlon 1', 'mots al còlon 2',
                 'patró comparatiu', 'encavalcament', 'metronome'])

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
                        try:
                            if 110 > len(str(verse)) > 20 and re.search(r"[a-zA-Z]", verse):
                                processed_verses.add(verse)  # Afegeix el vers al conjunt de versos processats

                                vers = escaneja(nlp, verse, goal=mode)  # Crea un objecte Vers
                                if verse is not None:
                                    try:
                                        if vers.recompte_sillabes_metriques == mode:  # Si el vers té el recompte de síl·labes correcte
                                            #vers.mostra()  # Imprimeix la metadata del vers
                                            results_dict['books'][book_title]['poems'][poem_title]['verses'].update(
                                                vers.save)  # Guarda la metadata del vers
                                            rows.append(
                                                [author.id, author.name, author.born_date, author.death_date, author.gender, author.city, author.dialect, author.wiki_id, author.viaf,
                                                 book.title, book.year, book.translation, book.font,
                                                 poem_title, i + 1] + vers.to_csv())
                                            i += 1
                                        else:
                                            outsiders.append(verse)
                                    except Exception as e:
                                        print(f"Error: {e}")
                                        print(verse)
                                        outsiders.append(verse)
                                        i += 1
                        except Exception as e:
                            print(verse)
                            print(f"Error: {e}")
                            outsiders.append(verse)
                            i += 1

        if len(rows) > 99:
            os.makedirs(f"{results_path}json/", exist_ok=True)
            # Revisa si el fitxer f'{results_path}json/{author.id}.json ja existeix
            if os.path.exists(f"{results_path}json/{author.id}.json"):
                # Si ja existeix, afegeix el nou book als books
                with open(f"{results_path}json/{author.id}.json", 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    existing_data['books'].update(results_dict['books'])
                with open(f"{results_path}json/{author.id}.json", 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, indent=4, ensure_ascii=False)
            else:
                with open(f"{results_path}json/{author.id}.json", 'w',
                          encoding='utf-8') as f:  # Guarda els resultats en un fitxer JSON
                    json.dump(results_dict, f, indent=4, ensure_ascii=False)

            # Comprova si ja existeix el fitxer CSV
            if os.path.exists(f"{results_path}csv/{author.id}.csv"):
                # Si ja existeix concatena el nou dataframe amb el dataframe existent (sense encapçalat)
                existing_df = pd.read_csv(f"{results_path}csv/{author.id}.csv", encoding="utf-8", sep=';')
                new_df = pd.DataFrame(rows, columns=head)
                df = pd.concat([existing_df, new_df], ignore_index=True)
                df.to_csv(f"{results_path}csv/{author.id}.csv", index=False, sep=';', encoding='utf-8',
                          lineterminator='\n')
            else:
                os.makedirs(f"{results_path}csv/", exist_ok=True)
                with open(f"{results_path}csv/{author.id}.csv", 'w',
                          encoding='utf-8') as f:
                    df = pd.DataFrame(rows, columns=head)
                    df.to_csv(f, index=False, sep=';', encoding='utf-8', lineterminator='\n', header=True)

            os.makedirs(f"{results_path}log/", exist_ok=True)
            with open(f"{results_path}log/{author.id}_outsiders.log", 'a', encoding='utf-8') as f:
                for verse in outsiders:
                    f.write(str(verse) + '\n')
            os.makedirs(f"{results_path}svg/", exist_ok=True)
            os.makedirs(f"{results_path}xlsx/", exist_ok=True)
            os.makedirs(f"{results_path}ot/", exist_ok=True)

            counts = {}
            for value in df['subdivisió']:
                counts[value] = counts.get(value, 0) + 1
            #print(counts)
            if '4+6' not in counts:
                counts['4+6'] = 0
            if '5+5' not in counts:
                counts['5+5'] = 0
            if "5'+5'" not in counts:
                counts["5'+5"] = 0
            if '6+4' not in counts:
                counts['6+4'] = 0
            if None not in counts:
                counts[None] = 0

            now = datetime.now()

            with open(f"{results_path}sumari.sum", 'a', encoding='utf-8') as sumari:
                sumari.write(
                    f"{now.strftime('%d/%m/%Y %H:%M:%S')};{versio};{author.id};{len(rows)};{counts['4+6']};{counts['5+5']};{counts['6+4']};{counts[None]};{len(outsiders)}\n")

            with open(f'{results_path}dades_autors.csv', 'a', encoding='utf-8') as dades_autors:
                dades_autors.write(
                    f"{author.id};{author.gender};{author.born_date};{author.death_date};{author.city};{author.dialect};{len(rows)}\n")

            #print(f"Resultats de l'autor {author.id} desats en {results_path}json/{author.id}.json")
            #print(f"Resultats de l'autor {author.id} desats en {results_path}csv/{author.id}.csv")
            #print(f"Versos no processats de l'autor {author.id} desats en {results_path}log/outsiders_log.log")

    merge_tables(results_path, corpus_name)

if __name__ == "__main__":
    # Carrega el model de Spacy en català
    print("--" * 40)
    print(f"Carregant el model de Spacy 'ca_core_news_md' (versió {spacy.__version__})...")
    nlp = spacy.load("ca_core_news_md", disable=["ner"])
    print("Model carregat correctament.")
    print("--" * 40)
    versio = datetime.now().strftime('%Y.%m.%d')
    print(f"Versió de l'etiquetador: {versio}")

    root = f"{usb}/corpora/"

    print("--" * 40)
    print("Corpus disponibles:")
    for corpus_folder in os.listdir(root):
        print(f"\t• {corpus_folder}")
    print("--" * 40)

    enter = input("Quin corpus voleu etiquetar?\t")

    if enter != "":
        start = time.time()
        corpus_path = f"{root}{enter}/sense_etiquetar/json/"
        results_path = f"{root}{enter}/etiquetat/"
        etiqueta(corpus_path, results_path, versio, nlp, mode=10)
    else:
        start = time.time()
        for corpus_folder in os.listdir(root):
            start = time.time()
            corpus_path = f"{root}{corpus_folder}/sense_etiquetar/json/"
            results_path = f"{root}{corpus_folder}/etiquetat/"
            etiqueta(corpus_path, results_path, versio, nlp, mode=10)

    elapsed_time = time.time() - start
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    print(f"Temps d'execució: {minutes} minuts i {seconds} segons")
    print("Fi de l'etiquetatge.")
