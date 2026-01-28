import os
import re
import json
import time
import spacy
import pandas as pd
from datetime import datetime

from thinc.layers import reduce_first
from tqdm import tqdm

from AIMeRiC.corpus.modules.getUSB import getUSB
from AIMeRiC.corpus.modules.author import Author
from AIMeRiC.corpus.modules.book import Book
from AIMeRiC.corpus.modules.poem import Poem
from AIMeRiC.escansio.escansor import escaneja, escaneja_minim
from AIMeRiC.escansio.modules.utils import prose
from AIMeRiC.escansio.modules.verse import Vers


def nucli_escansio_prosa(sring, goal):
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

    if first_10_line is not None:
        first_10_scan = escaneja(nlp, first_10_line, goal=10, permet_llicencies=True)
        if first_10_scan is not None:
            if first_10_scan.recompte_sillabes_metriques == goal:
                dict_first.update(first_10_scan.desa_prosa())
                dict_first[first_10_scan.text].update({'position': 'first'})
                row_first = [first_10_scan.text] + first_10_scan.prosa_to_csv() + ['first']

    if last_10_line is not None:
        last_10_scan = escaneja(nlp, last_10_line, goal=10, permet_llicencies=True)
        if last_10_scan is not None:
            if last_10_scan.recompte_sillabes_metriques == goal:
                dict_last.update(last_10_scan.desa_prosa())
                dict_last[last_10_scan.text].update({'position': 'last'})
                row_last = [last_10_scan.text] + last_10_scan.prosa_to_csv() + ['last']

    if medial_10_line is not None:
        medial_10_scan = escaneja(nlp, medial_10_line, goal=10, permet_llicencies=True)
        if medial_10_scan is not None:
            if medial_10_scan.recompte_sillabes_metriques == goal:
                dict_medial.update(medial_10_scan.desa_prosa())
                dict_medial[medial_10_scan.text].update({'position': 'medial'})
                row_medial = [medial_10_scan.text] + medial_10_scan.prosa_to_csv() + ['medial']

    return (dict_first, dict_medial, dict_last), (row_first, row_medial, row_last)


def paragrafs_prosa(nlp, text, goal):
    paragrafs = re.split(r'[.?!:;]', text)  # Separa els paràgrafs en enunciats més curts
    results = {'first_10': {}, 'medial_10': {}, 'last_10': {}}
    rows = []
    for paragraf in paragrafs:
        if len(paragraf) > 20:
            escaneig = escaneja_minim(nlp, paragraf, goal, permet_llicencies=False)
            if paragraf is not None:
                try:
                    res_first, res_medial, res_last = nucli_escansio_prosa(paragraf, goal)[0]
                    if res_first:
                        results['first_10'].update(res_first)
                        rows.append(nucli_escansio_prosa(paragraf, goal)[1][0])
                    if res_last:
                        results['last_10'].update(res_last)
                        rows.append(nucli_escansio_prosa(paragraf, goal)[1][2])
                    if res_medial:
                        results['medial_10'].update(res_medial)
                        rows.append(nucli_escansio_prosa(paragraf, goal)[1][1])
                except Exception as e:
                    print(f"Error en l'escaneig del paràgraf: {e}")

    return results, rows


def itera_narrativa(nlp, file_path, goal):
    global corpus_dict, rows
    for file in os.listdir(file_path):
        author = Author(os.path.join(file_path, file))  # Crea un objecte Autor
        corpus_dict = author.save_metadata()  # Guarda la metadata de l'autor
        rows = []
        for book_title in author.books:  # Per a cada llibre de l'autor
            book = Book(book_title, author.content)  # Crea un objecte Llibre
            corpus_dict['books'].update(book.save_metadata())  # Guarda la metadata del llibre
            for poem_title in book.poems:  # Per cada poema del llibre
                if book.poems[poem_title]:  # Si el poema no és buit
                    pagina = Poem(poem_title, book.book_content)  # Crea un objecte Poema
                    corpus_dict['books'][book_title]['poems'].update(pagina.save_metadata())
                    for paragraf in pagina.verses:  # Per cada vers del poema
                        if isinstance(paragraf, str) and len(paragraf) > 20:
                            page_results = paragrafs_prosa(nlp, paragraf, goal)
                            dict_results = page_results[0]
                            csv_results = page_results[1]
                            for dict_result in dict_results.values():
                                corpus_dict['books'][book_title]['poems'][poem_title]['verses'].update(dict_result)
                            for csv_result in csv_results:
                                rows.append([author.id, author.name, author.born_date, author.death_date, author.gender, author.city,
                             author.dialect, author.wiki_id, author.viaf,
                             book.title, book.year, book.translation, book.font,
                             pagina.verses.index(paragraf)] + csv_result)

    head = (['autor_id', 'autor', 'naixement', 'defunció', 'gènere', 'ciutat', 'dialecte', 'wiki_id', 'viaf',
             'obra', 'any', 'traducció', 'font', 'poema',
             'núm. de vers', 'text del vers',
             'escansió plana', 'síl·labes mètriques', 'síl·labes extramètriques', 'subdivisió', 'llicències',
             'mots al còlon 1', 'mots al còlon 2',
             'patró', 'patró_rítmic', 'encavalcament', 'metronome', 'posició'])

    corpus_csv = pd.DataFrame(rows, columns=head)

    return corpus_dict, corpus_csv


def prosa(nlp):
    corpus_path = f"{getUSB()}/corpora/prosa/sense_etiquetar/json/"
    results_path = f"{getUSB()}/corpora/prosa/etiquetat/"
    versio = datetime.now().strftime('%Y.%m.%d')
    etiqueta_narrativa(corpus_path, results_path, versio, nlp, mode=100)


def etiqueta_narrativa(corpus_path: str, results_path: str, versio: str, nlp, mode: int = 10):
    global rows
    os.makedirs(f"{results_path}", exist_ok=True)

    head = ['id', 'autor', 'book', 'year', 'text', 'string_stress', 'recompte_sillabes_metriques',
            'recompte_sillabes_extrametriques', 'pattern', 'maxpattern', 'clash', 'lapse', 'ws_hl', 'non_initial',
            'symetry',
            'metronome', 'iambes', 'troqueus', 'anapests', 'dàctils', 'peus']
    head_syl = ['id', 'autor', 'book', 'year', 'text', 'patró', 'max_patró', 'recompte_sillabes_metriques',
                'controrn accentual', 'metronome']

    for file in tqdm(os.listdir(corpus_path), desc="Etiquetant el corpus", leave=True, position=0,
                     ncols=80):  # Per cada autor del corpus
        author = Author(os.path.join(corpus_path, file))  # Crea un objecte Autor
        results_dict = author.save_metadata()  # Guarda la metadata de l'autor
        syll_dict_L = author.save_metadata()
        syll_dict_R = author.save_metadata()

        rows = []
        rowsL = []
        rowsR = []
        for book_title in author.books:  # Per a cada llibre de l'autor
            linies_temp = []  # llista temporal per desar les líneis escanejades
            book = Book(book_title, author.content)  # Crea un objecte Llibre
            results_dict['books'].update(book.save_metadata())  # Guarda la metadata del llibre
            syll_dict_L['books'].update(book.save_metadata())
            syll_dict_R['books'].update(book.save_metadata())

            for poem_title in book.poems:  # Per cada poema del llibre
                if book.poems[poem_title]:  # Si el poema no és buit
                    pagina = Poem(poem_title, book.book_content)  # Crea un objecte Poema
                    results_dict['books'][book_title]['poems'].update(
                        pagina.save_metadata())  # Guarda la metadata del poema
                    syll_dict_L['books'][book_title]['poems'].update(pagina.save_metadata())
                    syll_dict_R['books'][book_title]['poems'].update(pagina.save_metadata())

                    i = 1

                    for paragraf in pagina.verses:  # Per cada vers del poema
                        if len(paragraf) > 50:
                            paragrafs = re.split(r'[.?!:;]', paragraf)  # Separa els paràgrafs en enunciats més curts
                            sub_i = 1
                            for paragraf in paragrafs:

                                if len(paragraf) > 40:
                                    linia = escaneja(nlp, paragraf, goal=40)  # Crea un objecte Vers

                                    if paragraf is not None:
                                        results_dict['books'][book_title]['poems'][poem_title]['verses'].update(
                                            linia.desa_prosa())  # Guarda la metadata del vers format prosa

                                        syL = linia.desa_syll(10,
                                                              'l')  # Guarda la metadata del vers format síl·labic a l'esquerra
                                        syR = linia.desa_syll(10,
                                                              'r')  # Guarda la metadata del vers format síl·labic a la dreta

                                        if syL is not None:
                                            syll_dict_L['books'][book_title]['poems'][poem_title]['verses'].update(
                                                syL[0])
                                            syll_row_L = [f"{i}.{sub_i}", author.name, book_title,
                                                          book.year] + syL[1]
                                            rowsL.append(syll_row_L)
                                        if syR is not None:
                                            syll_dict_R['books'][book_title]['poems'][poem_title]['verses'].update(
                                                syR[0])
                                            syll_row_R = [f"{i}.{sub_i}", author.name, book_title,
                                                          book.year] + syR[1]
                                            rowsR.append(syll_row_R)

                                        row = [f"{i}.{sub_i}", author.name, book_title,
                                               book.year] + linia.prosa_to_csv() + dades_prosa(linia)

                                        rows.append(row)
                                        sub_i += 1

                            i += 1

        os.makedirs(f"{results_path}json/", exist_ok=True)
        with open(f"{results_path}json/{author.id}.json", 'w',
                  encoding='utf-8') as f:  # Guarda els resultats en un fitxer JSON
            json.dump(results_dict, f, indent=4, ensure_ascii=False)

        with open(f"{results_path}json/{author.id}_syll_L.json", 'w',
                  encoding='utf-8') as f:
            json.dump(syll_dict_L, f, indent=4, ensure_ascii=False)
        with open(f"{results_path}json/{author.id}_syll_R.json", 'w',
                  encoding='utf-8') as f:
            json.dump(syll_dict_R, f, indent=4, ensure_ascii=False)

        os.makedirs(f"{results_path}csv/", exist_ok=True)
        #with open(f"{results_path}csv/{author.id}.csv", 'w',
        #encoding='utf-8') as f:  # Guarda els resultats en un fitxer CSV
        #df = pd.DataFrame(rows, columns=head)
        #df.to_csv(f, index=False, sep=';', encoding='utf-8', lineterminator='\n', header=True, decimal=',', float_format='%.2f')

        with open(f"{results_path}csv/{author.id}_syll_L.csv", 'w',
                  encoding='utf-8') as f:
            dfL = pd.DataFrame(rowsL, columns=head_syl)
            dfL.to_csv(f, index=False, sep=';', encoding='utf-8', lineterminator='\n', header=True, decimal=',',
                       float_format='%.2f')
        with open(f"{results_path}csv/{author.id}_syll_R.csv", 'w',
                  encoding='utf-8') as f:
            dfR = pd.DataFrame(rowsR, columns=head_syl)
            dfR.to_csv(f, index=False, sep=';', encoding='utf-8', lineterminator='\n', header=True, decimal=',',
                       float_format='%.2f')

        os.makedirs(f"{results_path}svg/", exist_ok=True)
        os.makedirs(f"{results_path}xlsx/", exist_ok=True)

    corpus_name = corpus_path.split('/')[2]
    #merge_tables(results_path, corpus_name)


def dades_prosa(vers: Vers):
    """Retorna dades sobre el ritme del fragment en prosa."""
    # Normalitza els valors accentuals del pattern: lambda x: 1 if x > 1 else 0
    vers.patro = [1 if x > 1 else 0 for x in vers.patro]

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

    iambes, troqueus, anapests, dactyls, ordered_groups = group_syllables(vers.patro)

    iambes = len(iambes) / len(vers.patro) * 100
    troqueus = len(troqueus) / len(vers.patro) * 100
    anapests = len(anapests) / len(vers.patro) * 100
    dactyls = len(dactyls) / len(vers.patro) * 100
    ordered_groups = sum(len(x) for x in ordered_groups) == len(vers.patro)

    return [iambes, troqueus, anapests, dactyls, ordered_groups]


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
            print("S'ha activat el mode d'etiquetatge de prosa.")
            corpus_path = f"{root}{corpus_folder}/sense_etiquetar/json/"
            results_path = f"{root}{corpus_folder}/etiquetat/"
            corpus_result = itera_narrativa(nlp, corpus_path, goal)
            # crea la carpeta si no existeix
            os.makedirs(f"{results_path}json/", exist_ok=True)
            with open(f"{results_path}json/prosa.json", 'w', encoding='utf-8') as f:
                json.dump(corpus_result[0], f, indent=4, ensure_ascii=False)
            # Desa un CSV amb els resultats
            print("Desant els resultats en format CSV...")
            print(corpus_result[1])
            os.makedirs(f"{results_path}csv/", exist_ok=True)
            corpus_result[1].to_csv(f"{results_path}csv/prosa.csv", index=False, sep=';', encoding='utf-8',
                      lineterminator='\n', header=True, decimal=',', float_format='%.2f')

    elapsed_time = time.time() - start
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    print(f"Temps d'execució: {minutes} minuts i {seconds} segons")
    print("Fi de l'etiquetatge.")
