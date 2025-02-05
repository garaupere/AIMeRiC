"""Un mòdul per a compliar el corpus de cada autor."""

import json
import os
from modules.parse import *
import time


def compile_corpus(path: str, corpus: str) -> None:
    """Finds the files in the new_files folders and compiles a corpus in JSON format."""
    drive = path
    corpus_path = drive + corpus
    print(f'Compilant el corpus \'{corpus}\'...')

    for folder_subcorpus in [x for x in os.listdir(corpus_path) if x != '__test']:
        print(f'> {folder_subcorpus} autors trobats en new_files.')
        for folder in os.listdir(corpus_path + '/' + folder_subcorpus):
            subcorpus_path = corpus_path + '/' + folder_subcorpus
            author_meta = read_metadata(subcorpus_path + '/' + folder, "author")
            corpus_dict = author_meta
            print(f'\t> {folder} autor trobat en new_files.')

            for subfolder in os.listdir(subcorpus_path + '/' + folder):
                if not subfolder.endswith('.info'):
                    book_path = subcorpus_path + '/' + folder + '/' + subfolder
                    book_meta = read_metadata(book_path, "book")
                    corpus_dict['books'].update({subfolder: book_meta})
                    print(
                        f'\t\t>>> {len(os.listdir(book_path))} pàgines del llibre \'{subfolder}\'.')

                    for file in os.listdir(book_path):
                        if file.endswith('.txt'):
                            file_path = book_path + '/' + file
                            poem = extract_poem(file_path)
                            corpus_dict['books'][subfolder]['poems'].update({file: poem})

            # Crea la carpeta 'corpora'
            print('-' * 60)
            if not os.path.exists('E:/corpora/'):
                os.makedirs('E:/corpora/')
                print('>> La carpeta \'E:/corpora\' ha estat creada.')
            else:
                print('>> La carpeta \'E:/corpora\' ja existeix.')

            if not os.path.exists(f'E:/corpora/{corpus}/'):
                os.makedirs(f'E:/corpora/{corpus}/')
                print(f'\t>> La carpeta \'E:corpora/{corpus}\' ha estat creada.')
            else:
                print(f'\t>> La carpeta \'E:/corpora/{corpus}\' ja existeix.')

            # Fes que el directori tengui aquesta estructura:
            # corpora/{path}/sense_etiquetar/json/{folder}.json
            if not os.path.exists(f'E:/corpora/{corpus}/sense_etiquetar/json/'):
                os.makedirs(f'E:/corpora/{corpus}/sense_etiquetar/json/')
                print(f'\t\t>> La carpeta \'E:/corpora/{corpus}/sense_etiquetar/json\' ha estat creada.')

            with open(f"E:/corpora/{corpus}/sense_etiquetar/json/{folder}.json", "w", encoding="utf-8") as json_file:
                json.dump(corpus_dict, json_file, ensure_ascii=False, indent=2)
                print('-' * 60)
                print(f"\t>> '{folder}.json' desat.")

    print('-' * 60)
    print(f"\t>> Corpus compilat amb èxit i desat a 'E:/corpora/{corpus}'.")
    print(f'\t>> {len(os.listdir(f"E:/corpora/{corpus}/sense_etiquetar/json"))} autors compilats dins el corpus.')
    print('-' * 60)


if __name__ == "__main__":
    print('Aquests són els corpus disponibles:')

    raw_files_path = r"E:/compile_files/"

    for folder in os.listdir(raw_files_path):
        print(f'\t-- {folder}')

    enter = input('Quin corpus voleu compilar?\t')

    if enter == "tots":
        start_time = time.time()
        for folder in os.listdir(raw_files_path):
            compile_corpus(path=raw_files_path, corpus=folder)
            print(f'Corpus {folder} compilat amb èxit.')

    else:
        start_time = time.time()
        try:
            compile_corpus(path=raw_files_path, corpus=enter)
        except FileNotFoundError:
           print(f'{FileNotFoundError}: No s\'ha seleccionat cap corpus.')

    end_time = time.time()
    execution_time = end_time - start_time

    minutes = int(execution_time // 60)
    seconds = int(execution_time % 60)

    print('-' * 60)
    print(f'El programa ha tardat {minutes} minuts i {seconds} segons en executar-se.')
