import json
import os
import re
import time

import pandas as pd
import spacy

from AIMeRiC.corpus.modules.autor import Autor
from AIMeRiC.corpus.modules.obra import Obra
from AIMeRiC.corpus.modules.getUSB import getUSB
from AIMeRiC.corpus.modules.poema import Poema
from AIMeRiC.escansio.escansor import escaneja, escaneja_minim
from AIMeRiC.escansio.modules.utils import prose


def nucli_escansio_prosa(nlp, sring, goal) -> dict:
    dict_first = {}
    dict_last = {}
    dict_medial = {}
    row_first = []
    row_last = []
    row_medial = []
    escaneig = escaneja_minim(nlp, sring, goal, permet_llicencies=False)

    first_10_line = prose.cut_first10_to_text(escaneig.escansio_text)
    last_10_line = prose.cut_last10_to_text(escaneig.escansio_text)
    medial_10_line = prose.extreure_10_sillabes_medials(escaneig.escansio_text)

    if first_10_line == last_10_line:
        last_10_line = None
    if first_10_line == medial_10_line:
        medial_10_line = None
    if last_10_line == medial_10_line:
        medial_10_line = None

    if first_10_line is not None:
        first_10_scan = escaneja(nlp, first_10_line, goal=10, permet_llicencies=True)
        if first_10_scan is not None:
            if first_10_scan.recompte_sillabes_metriques == goal:
                dict_first.update(first_10_scan.desa)
                dict_first[first_10_scan.text].update({'position': 'first'})
                row_first = [first_10_scan.text] + first_10_scan.to_csv() + ['first']

    if last_10_line is not None:
        last_10_scan = escaneja(nlp, last_10_line, goal=10, permet_llicencies=True)
        if last_10_scan is not None:
            if last_10_scan.recompte_sillabes_metriques == goal:
                dict_last.update(last_10_scan.desa)
                dict_last[last_10_scan.text].update({'position': 'last'})
                row_last = [last_10_scan.text] + last_10_scan.to_csv() + ['last']

    if medial_10_line is not None:
        medial_10_scan = escaneja(nlp, medial_10_line, goal=10, permet_llicencies=True)
        if medial_10_scan is not None:
            if medial_10_scan.recompte_sillabes_metriques == goal:
                dict_medial.update(medial_10_scan.desa)
                dict_medial[medial_10_scan.text].update({'position': 'medial'})
                row_medial = [medial_10_scan.text] + medial_10_scan.to_csv() + ['medial']

    return {
        "dict_first": dict_first,
        "dict_medial": dict_medial,
        "dict_last": dict_last,
        "row_first": row_first,
        "row_medial": row_medial,
        "row_last": row_last}


def paragrafs_prosa(nlp, text, goal):
    paragrafs = re.split(r'[.?!:;]', text)  # Separa els paràgrafs en enunciats més curts
    results = {'first_10': {}, 'medial_10': {}, 'last_10': {}}
    rows = []
    for paragraf in paragrafs:
        if len(paragraf) > 20:
            if paragraf is not None:
                try:
                    scan = nucli_escansio_prosa(nlp, paragraf, goal)
                    if isinstance(scan, dict):  # Assegura que el retorn és un diccionari
                        if 'dict_first' in scan and scan['dict_first']:
                            results['first_10'].update(scan['dict_first'])
                            rows.append(scan['row_first'])
                        if 'dict_last' in scan and scan['dict_last']:
                            results['last_10'].update(scan['dict_last'])
                            rows.append(scan['row_last'])
                        if 'dict_medial' in scan and scan['dict_medial']:
                            results['medial_10'].update(scan['dict_medial'])
                            rows.append(scan['row_medial'])
                    else:
                        raise ValueError("El resultat de nucli_escansio_prosa no és el format esperat.")
                except Exception as e:
                    #print(f"Error en l'escaneig del paràgraf: {e}")
                    continue  # Si hi ha un error en l'escaneig, salta aquest paràgraf

    return results, rows


def etiqueta_prosa(nlp, file_path, goal) -> tuple[dict, pd.DataFrame]:
    global corpus_dict, rows
    author = Autor(file_path)  # Crea un objecte Autor
    corpus_dict = author.save_metadata()  # Guarda la metadata de l'autor
    rows = []
    for book_title in author.books:  # Per a cada llibre de l'autor
        book = Obra(book_title, author.content)  # Crea un objecte Llibre
        corpus_dict['books'].update(book.save_metadata())  # Guarda la metadata del llibre
        for poem_title in book.poems:  # Per cada poema del llibre
            if book.poems[poem_title]:  # Si el poema no és buit
                pagina = Poema(poem_title, book.book_content)  # Crea un objecte Poema
                corpus_dict['books'][book_title]['poems'].update(pagina.save_metadata())
                for paragraf in pagina.verses:  # Per cada vers del poema
                    if isinstance(paragraf, str) and len(paragraf) > 20:
                        page_results = paragrafs_prosa(nlp, paragraf, goal)
                        dict_results = page_results[0]
                        csv_results = page_results[1]
                        for dict_result in dict_results.values():
                            corpus_dict['books'][book_title]['poems'][poem_title]['verses'].update(dict_result)
                        for csv_result in csv_results:
                            rows.append([author.id, author.name, author.born_date, author.death_date, author.gender,
                                         author.city,
                                         author.dialect, author.wiki_id, author.viaf,
                                         book.title, book.year, book.translation, book.font,
                                         pagina.verses.index(paragraf)] + csv_result)

    scansion_cols = [str(s) for s in range(1, goal + 1)]
    head = (['autor_id', 'autor', 'naixement', 'defunció', 'gènere', 'ciutat', 'dialecte', 'wiki_id', 'viaf',
             'obra', 'any', 'traducció', 'font', 'poema',
             'núm. de vers', 'text del vers',
             'escansió'] + scansion_cols +
            ['síl·labes mètriques', 'síl·labes extramètriques', 'subdivisió', 'llicències', 'mots', 'l_mots',
             'mots al còlon 1', 'mots al còlon 2',
             'patró', 'patró_rítmic', 'encavalcament', 'metronome', 'posició'])

    # Crea el DataFrame i assegura que les columnes d'escansió i de patró siguin strings
    df = pd.DataFrame(rows, columns=head)

    # Força les columnes d'escansió (1..goal) a cadenes per evitar que pandas les converteixi a int
    try:
        df[scansion_cols] = df[scansion_cols].astype(str)
    except Exception:
        # Si falla per alguna raó, ignora i continua; no hauria de passar en condicions normals
        pass

    # Assegura també que els camps de patró es guardin com a cadena
    for col in ['patró', 'patró_rítmic', 'subdivisió', 'posició']:
        if col in df.columns:
            try:
                df[col] = df[col].astype(str)
            except Exception:
                continue

    return corpus_dict, df


if __name__ == "__main__":
    # Carrega el model de Spacy en català
    print("--" * 40)
    print(f"Carregant el model de Spacy 'ca_core_news_md' (versió {spacy.__version__})...")
    nlp = spacy.load("ca_core_news_md", disable=["ner"])
    print("Model carregat correctament.")
    print("--" * 40)
    start = time.time()
    usb = getUSB()
    root = f"{usb}/corpora/"
    goal = 10


    print("--" * 40)
    for corpus_folder in os.listdir(root):
        if corpus_folder == 'prosa':
            for file in os.listdir(f"{root}{corpus_folder}/sense_etiquetar/json/"):
                # comprova si els fitxers json són vàlids
                file_path = f"{root}{corpus_folder}/sense_etiquetar/json/{file}"
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json.load(f)
                except json.JSONDecodeError as e:
                    print(f"Error: Format JSON invàlid en {file_path} (línia {e.lineno}, columna {e.colno}).")
                    continue  # Salta aquest fitxer i continua amb el següent
            into = input("Voleu continuar amb l'etiquetatge del corpus de prosa? (s/n): ")
            if into.lower() == 's':
                print("S'ha activat el mode d'etiquetatge de prosa.")
                corpus_path = f"{root}{corpus_folder}/sense_etiquetar/json/"
                results_path = f"{root}{corpus_folder}/etiquetat/"
                corpus_result = etiqueta_prosa(nlp, corpus_path, goal)
                # crea la carpeta si no existeix
                os.makedirs(f"{results_path}json/", exist_ok=True)
                with open(f"{results_path}json/prosa.json", 'w', encoding='utf-8') as f:
                    json.dump(corpus_result[0], f, indent=4, ensure_ascii=False)
                # Desa un CSV amb els resultats
                print("Desant els resultats en format CSV...")
                print(corpus_result[1])
                os.makedirs(f"{results_path}csv/", exist_ok=True)
                import csv
                corpus_result[1].to_csv(f"{results_path}csv/prosa.csv", index=False, sep=';', encoding='utf-8',
                                        lineterminator='\n', header=True, decimal=',', quoting=csv.QUOTE_ALL)

    elapsed_time = time.time() - start
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    print(f"Temps d'execució: {minutes} minuts i {seconds} segons")
    print("Fi de l'etiquetatge.")
