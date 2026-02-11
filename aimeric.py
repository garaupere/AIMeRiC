import json

import pandas as pd
from colorama import Fore
from tqdm import tqdm

from AIMeRiC.corpus.backup import backup_files
from AIMeRiC.corpus.compila import compile_corpus
from AIMeRiC.corpus.modules.dictionary_scan import escaneja_diccionari, escaneja_diccionari_frequencies
from AIMeRiC.corpus.etiqueta import etiqueta_corpus
from AIMeRiC.corpus.prosa import etiqueta_prosa
from AIMeRiC.corpus.valida import valida
from AIMeRiC.escansio.escansor import escaneja, __version__
from AIMeRiC.corpus.modules.getUSB import getUSB

__author__ = "Pere Garau Borràs"
__copyright__ = "Copyright © 2025, Pere Garau Borràs"
__version__ = __version__

import os
import time
import spacy


def compile(raw_files_path, corpus):
    """Una funció per donar l'ordre de compilar."""
    start_time = time.time()
    try:
        compile_corpus(path=raw_files_path, corpus=corpus)
        print(f'Corpus {corpus} compilat amb èxit.')
    except FileNotFoundError:
        print(f'{FileNotFoundError}: No s\'ha seleccionat cap corpus.')

    end_time = time.time()
    execution_time = end_time - start_time
    minutes = int(execution_time // 60)
    seconds = int(execution_time % 60)
    print('-' * 40)
    print(f'Temps d\'execució: {minutes} minuts i {seconds} segons')


def etiq(nlp, corpus, goal: int):
    """Etiquetar un corpus"""
    usb = getUSB()
    root = f"{usb}/corpora/"
    corpus_path = f"{root}{corpus}/sense_etiquetar/json/"
    results_path = f"{root}{corpus}/etiquetat/"
    etiqueta_corpus(corpus_path, results_path, __version__, nlp, mode=goal)


def scan(nlp, verse, goal):
    analisi = escaneja(nlp, verse, goal)
    return analisi.mostra()


def check_jsons(corpus):
    """Comprova que tots els fitxers .json d'un directori estiguin ben formats."""
    global json
    usb = getUSB()
    path = f"{usb}/corpora/{corpus}/sense_etiquetar/json/"
    for filename in os.listdir(path):
        if filename.endswith(".json"):
            file_path = os.path.join(path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    import json
                    json.load(file)
                print(f"{filename} està ben format.")
            except json.JSONDecodeError as e:
                print(f"\t >> Error de format en {filename}: {e}")


def scan_dictionary(nlp):
    """Escaneja prosòdicament els mots d'un diccionari. Parteix del catalan-dict-tools (Softcatalà, J. Ortolà)"""
    resultats = escaneja_diccionari(nlp)
    resultats.to_csv(f'{getUSB()}/corpora/diccionari/diccionari_prosodic.csv', index=False, encoding='utf-8', sep=';')
    print(f"Escansió del diccionari completada i desada a '{getUSB()}/corpora/diccionari/diccionari_prosodic.csv'.")


def help():
    print("--" * 40)
    print("Aquesta és l'ajuda de l'aplicació AIMeRiC:")
    print(Fore.CYAN, f"\t➥", Fore.RESET, "Escriviu un vers per a analitzar-lo.")
    print(Fore.CYAN, f"\t➥", Fore.RESET, "Llista de corpus disponibles (" + Fore.GREEN + "-list" + Fore.RESET + ")")
    print(Fore.CYAN, f"\t➥", Fore.RESET, "Compilar un corpus (" + Fore.GREEN + "-comp" + Fore.RED,
          "corpus" + Fore.RESET + ")")
    print(Fore.CYAN, f"\t➥", Fore.RESET, "Comprovar els fitxers JSON d'un corpus (" + Fore.GREEN + "-check" + Fore.RED,
          "corpus" + Fore.RESET + ")")
    print(Fore.CYAN, f"\t➥", Fore.RESET, "Comparar dos corpus (" + Fore.GREEN + "-compara" + Fore.RED, "corpus_1",
          Fore.RESET, Fore.BLUE + "corpus_2" + Fore.RESET + ")")
    print(Fore.CYAN, f"\t➥", Fore.RESET, "Etiquetar un corpus (" + Fore.GREEN + "-etiq", Fore.RED,
          "corpus" + Fore.RESET + ")")
    print(Fore.CYAN, f"\t➥", Fore.RESET, "Validar les dades __test (" + Fore.GREEN, "-test" + Fore.RESET + ")")
    print(Fore.CYAN, f"\t➥", Fore.RESET, "Analitza un corpus de prosa (" + Fore.GREEN + "-etiqprosa" + Fore.RESET,
          Fore.RED + "corpus" + Fore.RESET + ")")
    print(Fore.CYAN, f"\t➥", Fore.RESET, "Escaneja un diccionari (" + Fore.GREEN + "-scandic" + Fore.RESET + ")")
    print(Fore.CYAN, f"\t➥", Fore.RESET,
          "Escaneja un diccionari amb freqüències (" + Fore.GREEN + "-scandic-fq" + Fore.RESET + ")")
    print(Fore.CYAN, f"\t➥", Fore.RESET, "Còpia de seguretat del corpus (" + Fore.GREEN + "-bkp" + Fore.RESET + ")\n")
    print("Per accedir al menú d'ajuda, usau '" + Fore.GREEN + "-help" + Fore.RESET + "'.")
    print("Per tancar el programa, premeu Intro.\n")
    print("--" * 40)
    print(
        "Si necessitau més ajuda, podeu consultar el web de l'aplicació: https://github.com/garaupere/AIMeRiC, o contactar amb l'autor a p.garau@uib.cat.")
    print("Gràcies per utilitzar l'aplicació.\n Versió:", __version__)
    print("--" * 40)


def compara_corpus(corpus1, corpus2):
    root = f"{getUSB()}/corpora/"
    end = "/sense_etiquetar/json/"
    fitxers1 = set(os.listdir(root + corpus1 + end))
    fitxers2 = set(os.listdir(root + corpus2 + end))

    comuns = sorted(fitxers1 & fitxers2)
    nomes_carpeta1 = sorted(fitxers1 - fitxers2)
    nomes_carpeta2 = sorted(fitxers2 - fitxers1)

    # Crear un diccionari de dades
    dades = {
        f"Només {os.path.basename(corpus1)}": nomes_carpeta1,
        f"Només {os.path.basename(corpus2)}": nomes_carpeta2,
        "Comuns": comuns
    }

    # Crear un dataframe, omplint amb valors buits on sigui necessari
    df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in dades.items()]))

    # Escriure a Excel
    df.to_excel(f"comparison_result_{corpus1}_{corpus2}.xlsx", index=False)
    print(f"Resultat guardat a 'comparison_results_{corpus1}_{corpus2}.xlsx'")


def scan_dictionary_frequencies(nlp):
    """Escaneja prosòdicament els mots d'un diccionari amb freqüències. Parteix del catalan-dict-tools (Softcatalà, J. Ortolà)"""
    escaneja_diccionari_frequencies(nlp).to_csv(f'{getUSB()}/corpora/diccionari/FREQDCC_prosodic.csv',
                                                index=False, encoding='utf-8', sep=';')
    print(
        f"Escansió del diccionari de freqüències completada i desada a '{getUSB()}/corpora/diccionari/FREQDCC_prosodic.csv'.")


def main(nlp):
    global options
    usb = getUSB()
    raw_files_path = rf"{usb}/compile_files/"
    root = f"{usb}/corpora/"

    while True:
        option = input(f"{Fore.LIGHTGREEN_EX}AIMeRiC{Fore.RESET} > ")

        if option == "-list":
            print("Corpus disponibles per compilar:")
            for folder in os.listdir(raw_files_path):
                print(f"\t• {folder}")
        elif option == "-help":
            help()

        elif option == "-test":
            print("--" * 40)
            print("Validant les dades __test...")
            valida()
        elif option == "-bkp":
            print("--" * 40)
            start = time.time()
            backup_path = "C:\\Users\\pere\\OneDrive - Universitat de les Illes Balears\\Documents\\UIB\\Estudis oficials\\Doctorat en Filologia i Filosofia\\Tesi\\TESI ESPAI DE TREBALL NET\\DADES\\.backup\\"
            corpus_path = getUSB()
            backup_files(corpus_path, backup_path)
            elapsed_time = time.time() - start
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            print(f"Temps d'execució: {minutes} minuts i {seconds} segons")

        elif option == '-scandic':
            start = time.time()
            scan_dictionary(nlp)
            elapsed_time = time.time() - start
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            print(f"Temps d'execució: {minutes} minuts i {seconds} segons")

        elif option == '-scandic-fq':
            start = time.time()
            scan_dictionary_frequencies(nlp)
            elapsed_time = time.time() - start
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            print(f"Temps d'execució: {minutes} minuts i {seconds} segons")
        elif option == "":
            print("Sortint del programa.")
            break
        else:
            try:
                options = option.split(" ")
            except AttributeError:
                print("Opció no vàlida. Si us plau, selecciona una opció vàlida.")
                continue
            if len(options) < 3:
                if options[0] == '-comp':
                    corpus = options[1]
                    try:
                        compile(raw_files_path, corpus)
                    except FileNotFoundError:
                        print('El corpus seleccionat no existeix.')

                elif options[0] == '-etiq':
                    corpus = options[1]
                    goal = int(options[2]) if len(options) > 2 else 10
                    try:
                        start = time.time()
                        etiq(nlp, corpus, goal)
                        elapsed_time = time.time() - start
                        minutes = int(elapsed_time // 60)
                        seconds = int(elapsed_time % 60)
                        print(f"Temps d'execució: {minutes} minuts i {seconds} segons")
                    except FileNotFoundError:
                        print('El corpus seleccionat no existeix.')


                elif options[0] == '-etiqprosa':
                    corpus = options[1]
                    print(Fore.RED + "S'ha activat el mode d'etiquetatge de prosa." + Fore.RESET)
                    start = time.time()
                    corpus_path = f"{root}{corpus}/sense_etiquetar/json/"
                    results_path = f"{root}{corpus}/etiquetat/"
                    for json_file in tqdm(os.listdir(corpus_path), desc=f"Etiquetant fitxers JSON de '{corpus}'"):
                        if json_file.endswith('.json'):
                            try:
                                json_file_path = os.path.join(corpus_path, json_file)
                                name = json_file.replace('.json', '')
                                corpus_result = etiqueta_prosa(nlp, json_file_path, 10)
                                # crea la carpeta si no existeix
                                os.makedirs(f"{results_path}json/", exist_ok=True)
                                with open(f"{results_path}json/{name}.json", 'w', encoding='utf-8') as f:
                                    json.dump(corpus_result[0], f, indent=4, ensure_ascii=False)
                                # Desa un CSV amb els resultats
                                print("Desant els resultats en format CSV...")
                                print(corpus_result[1])
                                os.makedirs(f"{results_path}csv/", exist_ok=True)
                                corpus_result[1].to_csv(f"{results_path}csv/{name}.csv", index=False, sep=';',
                                                        encoding='utf-8',
                                                        lineterminator='\n', header=True, decimal=',',
                                                        float_format='%.2f')
                            except FileNotFoundError:
                                print('El corpus seleccionat no existeix.')
                    elapsed_time = time.time() - start
                    minutes = int(elapsed_time // 60)
                    seconds = int(elapsed_time % 60)
                    print(f"Temps d'execució: {minutes} minuts i {seconds} segons")
                    print("Fi de l'etiquetatge.")

                elif options[0] == "-compara":
                    try:
                        compara_corpus(options[1], options[2])
                    except FileNotFoundError:
                        print('Un dels corpus seleccionats no existeix.')

                elif options[0] == '-check':
                    corpus = options[1]
                    try:
                        check_jsons(corpus)
                    except FileNotFoundError:
                        print('El corpus seleccionat no existeix.')

            else:
                verse = ' '.join(options[0:])
                scan(nlp, verse)


if __name__ == "__main__":
    from cfonts import render

    text = render("AIMeRiC", font='chrome', colors=['system', 'gray', 'system'], align='center')
    print(text)
    print(render(
        f"Anàlisi Informatitzada del Metre i el Ritme del Català\n ©2026, Pere Garau Borràs\n\t\t\t\t\t\tv. {__version__}",
        font='console', colors=['system'], align='center'))

    # Carrega el model de Spacy en català
    print("--" * 40)
    print(f"Carregant el model de Spacy 'ca_core_news_md' (versió {spacy.__version__})...")
    nlp = spacy.load("ca_core_news_md", disable=["ner"])
    print("Model carregat correctament.")
    print("--" * 40)

    main(nlp)

    print("--" * 40)
    print("Gràcies per utilitzar l'aplicació.")
    print("--" * 40)
    print(
        f"Anàlisi Informatitzada del Metre i el Ritme del Català\n © 2022-2025, Pere Garau Borràs\n\t\t\t\t\t\tv. {__version__}")
    print("--" * 40)
