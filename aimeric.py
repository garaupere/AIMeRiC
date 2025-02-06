import os
import time
import spacy
from datetime import datetime

from AIMeRiC.corpus.backup import backup_files
from AIMeRiC.corpus.compila import compile_corpus
from AIMeRiC.corpus.modules.getUSB import getUSB
from AIMeRiC.corpus.etiqueta import etiqueta
from AIMeRiC.corpus.obten_dades import analitza_corpus
from AIMeRiC.corpus.valida import valida
from AIMeRiC.escansor.escansor import escaneja


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
    versio = datetime.now().strftime('%Y.%m.%d')
    usb = getUSB()
    root = f"{usb}/corpora/"
    corpus_path = f"{root}{corpus}/sense_etiquetar/json/"
    results_path = f"{root}{corpus}/etiquetat/"
    etiqueta(corpus_path, results_path, versio, nlp, mode=10)


def explota(corpus):
    """Explotació estadística del corpus"""
    usb = getUSB()
    root = f"{usb}/corpora/"
    results_path = f"{root}{corpus}/etiquetat/"
    analitza_corpus(corpus)


def scan(nlp, verse, goal:int = 10):
    analisi = escaneja(nlp, verse, goal)
    return analisi.mostra()


def help():
    print("--" * 40)
    print("Aquesta és l'ajuda de l'aplicació AIMeRiC:")
    print("Si necessitau ajuda, podeu consultar la web de l'aplicació: https://github.com/garaupere/escancat, o contactar amb l'autor a p.garau@uib.cat.")
    print("Gràcies per utilitzar l'aplicació.")
    print("--" * 40)


def main():
    usb = getUSB()
    raw_files_path = rf"{usb}/compile_files/"
    root = f"{usb}/corpora/"

    while True:
        print("--" * 40)
        print("Opcions disponibles:")
        print("\t1. Compilar un corpus")
        print("\t2. Etiquetar un corpus")
        print("\t3. Explotació estadística del corpus")
        print("\t4. Validar les dades __test")
        print("\t5. Analitzar un vers")
        print("\t6. Còpia de seguretat del corpus")
        print("\tPer accedir al menú d'ajuda, premeu 'h'.")
        print("\tPer tancar el programa, premeu Intro.")
        option = input("Seleccionau una opció (1/2/3/4/5/6): ")

        if option == "1":
            print("--" * 40)
            print("Corpus disponibles per compilar:")
            for folder in os.listdir(raw_files_path):
                print(f"\t• {folder}")
            enter = input("Quin corpus voleu compilar?\t")
            if enter:
                compile(raw_files_path, enter)
                etiq_option = input("Vols etiquetar el corpus compilat? (s/n): ")
                if etiq_option.lower() == 's':
                    etiq(enter)
            else:
                print("No s'ha seleccionat cap corpus per compilar.")
        elif option == "2":
            print("--" * 40)
            print("Corpus disponibles per etiquetar:")
            for folder in os.listdir(root):
                print(f"\t• {folder}")
            enter = input("Quin corpus voleu etiquetar?\t")
            if enter:
                etiq(enter)
            else:
                print("No s'ha seleccionat cap corpus per etiquetar.")
        elif option == "3":
            print("--" * 40)
            print("Corpus disponibles per explotació estadística:")
            for folder in os.listdir(root):
                print(f"\t• {folder}")
            enter = input("Quin corpus voleu explotar?\t")
            if enter:
                explota(enter)
            else:
                print("No s'ha seleccionat cap corpus per explotació estadística.")
        elif option == "4":
            print("--" * 40)
            print("Validant les dades __test...")
            valida()
        elif option == "5":
            print("--" * 40)
            verse = input("Introdueix un vers a analitzar: ")
            scan(nlp, verse)

        elif option == "6":
            print("--" * 40)
            start = time.time()
            backup_path = "C:\\Users\\pere\\OneDrive - Universitat de les Illes Balears\\Documents\\UIB\\Estudis oficials\\Doctorat en Filologia i Filosofia\\Tesi\\TESI ESPAI DE TREBALL NET\\DADES\\.backup\\"
            corpus_path = getUSB()
            backup_files(corpus_path, backup_path)
            elapsed_time = time.time() - start
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            print(f"Temps d'execució: {minutes} minuts i {seconds} segons")
        elif option == "h":
            help()
        elif option == "":
            print("Sortint del programa.")
            break
        else:
            print("Opció no vàlida. Si us plau, selecciona una opció vàlida.")


if __name__ == "__main__":
    from cfonts import render, say
    text = render("AIMeRiC", font='chrome', colors=['system', 'gray', 'system'], align='center')
    print(text)
    print(render("Anàlisi Informatitzada del Metre i el Ritme del Català\n © 2022-2025, Pere Garau Borràs", font='console', colors=['system'], align='center'))

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
    print(render("Anàlisi Informatitzada del Metre i el Ritme del Català\n © 2022-2025, Pere Garau Borràs", font='console', colors=['system'], align='center'))
    print("--" * 40)
