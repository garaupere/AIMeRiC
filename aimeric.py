from colorama import Fore
from AIMeRiC.corpus.backup import backup_files
from AIMeRiC.corpus.compila import compile_corpus
from AIMeRiC.corpus.modules.getUSB import getUSB
from AIMeRiC.corpus.etiqueta import etiqueta
from AIMeRiC.corpus.obten_dades import analitza_corpus, descriu
from AIMeRiC.corpus.prosa import prosa
from AIMeRiC.corpus.valida import valida
from AIMeRiC.corpus.analyse_OT import ot_analysis
from AIMeRiC.escansio.escansor import escaneja, __version__

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


def etiq(corpus):
    """Etiquetar un corpus"""
    usb = getUSB()
    root = f"{usb}/corpora/"
    corpus_path = f"{root}{corpus}/sense_etiquetar/json/"
    results_path = f"{root}{corpus}/etiquetat/"
    etiqueta(corpus_path, results_path, __version__, nlp, mode=10)


def explota(corpus, filtre=None):
    """Exploració estadística del corpus"""
    usb = getUSB()
    root = f"{usb}/corpora/"
    results_path = f"{root}{corpus}/etiquetat/"
    analitza_corpus(corpus, filtre)


def scan(nlp, verse, goal: int = 10):
    analisi = escaneja(nlp, verse, goal)
    return analisi.mostra()


def help():
    print("--" * 40)
    print("Aquesta és l'ajuda de l'aplicació AIMeRiC:")
    print(Fore.CYAN, f"\t➥", Fore.RESET, "Llista de corpus disponibles", Fore.GREEN, "(-list)", Fore.RESET)
    print(Fore.CYAN, f"\t➥", Fore.RESET, "Compilar un corpus", Fore.GREEN, "(-comp", Fore.RED, "corpus)",
          Fore.RESET)
    print(Fore.CYAN, f"\t➥", Fore.RESET, "Etiquetar un corpus", Fore.GREEN, "(-etiq", Fore.RED, "corpus)",
          Fore.RESET)
    print(Fore.CYAN, f"\t➥", Fore.RESET, "Descripció estadística del corpus", Fore.GREEN, "(-desc", Fore.RED,
          "corpus)", Fore.RESET)
    print(Fore.CYAN, f"\t➥", Fore.RESET, "Exploració estadística del corpus", Fore.GREEN, "(-expl", Fore.RED,
          "corpus)", Fore.RESET)
    print(Fore.CYAN, f"\t➥", Fore.RESET, "Avaluació de les restriccions OT", Fore.GREEN, "(-ot", Fore.RED,
          "corpus)", Fore.RESET)
    print(Fore.CYAN, f"\t➥", Fore.RESET, "Validar les dades __test", Fore.GREEN, "(-test)", Fore.RESET)
    print(Fore.CYAN, f"\t➥", Fore.RESET, "Analitzar un vers", Fore.GREEN, "(-scan", Fore.RED, "vers)", Fore.RESET)
    print(Fore.CYAN, f"\t➥", Fore.RESET, "Analitza un corpus de prosa", Fore.GREEN, "(-prosa)", Fore.RESET)
    print(Fore.CYAN, f"\t➥", Fore.RESET, " Còpia de seguretat del corpus", Fore.GREEN, "(-bkp)", Fore.RESET, "\n")
    print("Per accedir al menú d'ajuda, usau '-help'.")
    print("Per tancar el programa, premeu Intro.\n")
    print("--" * 40)
    print(
        "Si necessitau més ajuda, podeu consultar el web de l'aplicació: https://github.com/garaupere/AIMeRiC, o contactar amb l'autor a p.garau@uib.cat.")
    print("Gràcies per utilitzar l'aplicació.")
    print("--" * 40)


def main():
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
        elif option == '-prosa':
            try:
                prosa(nlp)
            except FileNotFoundError:
                print("No disposau d'un corpus de prosa compilat.")

        elif option == "":
            print("Sortint del programa.")
            break

        else:
            try:
                options = option.split(" ")
            except AttributeError:
                print("Opció no vàlida. Si us plau, selecciona una opció vàlida.")
                continue

            if options[0] == '-comp':
                corpus = options[1]
                try:
                    compile(raw_files_path, corpus)
                except FileNotFoundError:
                    print('El corpus seleccionat no existeix.')

            elif options[0] == '-etiq':
                corpus = options[1]
                try:
                    start = time.time()
                    etiq(corpus)
                    elapsed_time = time.time() - start
                    minutes = int(elapsed_time // 60)
                    seconds = int(elapsed_time % 60)
                    print(f"Temps d'execució: {minutes} minuts i {seconds} segons")
                except FileNotFoundError:
                    print('El corpus seleccionat no existeix.')

            elif options[0] == '-desc':
                corpus = options[1]
                filtre = None
                if len(options) > 2:
                    filtre = options[2]
                try:
                    descriu(corpus, filtre)
                except FileNotFoundError:
                    print('El corpus seleccionat no existeix.')

            elif options[0] == '-expl':
                corpus = options[1]
                filtre = None
                if len(options) > 2:
                    filtre = options[2]
                try:
                    explota(corpus, filtre)
                except FileNotFoundError:
                    print('El corpus seleccionat no existeix.')

            elif options[0] == '-scan':
                verse = ' '.join(options[1:])
                scan(nlp, verse)

            elif options[0] == '-ot':
                corpus = options[1]
                filtre = None
                if len(options) > 2:
                    filtre = options[2]
                try:
                    ot_analysis(corpus, filtre)
                except FileNotFoundError:
                    print('El corpus seleccionat no existeix.')


if __name__ == "__main__":
    from cfonts import render

    text = render("AIMeRiC", font='chrome', colors=['system', 'gray', 'system'], align='center')
    print(text)
    print(render(
        f"Anàlisi Informatitzada del Metre i el Ritme del Català\n © 2022-2025, Pere Garau Borràs\n\t\t\t\t\t\tv. {__version__}",
        font='console', colors=['system'], align='center'))

    # Carrega el model de Spacy en català
    print("--" * 40)
    print(f"Carregant el model de Spacy 'ca_core_news_md' (versió {spacy.__version__})...")
    nlp = spacy.load("ca_core_news_md", disable=["ner"])
    print("Model carregat correctament.")
    print("--" * 40)

    main()

    print("--" * 40)
    print("Gràcies per utilitzar l'aplicació.")
    print("--" * 40)
    print(text)
    print(render(
        f"Anàlisi Informatitzada del Metre i el Ritme del Català\n © 2022-2025, Pere Garau Borràs\n\t\t\t\t\t\tv. {__version__}",
        font='console', colors=['system'], align='center'))
    print("--" * 40)
