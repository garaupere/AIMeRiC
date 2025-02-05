"""Un mòdul per a compliar el corpus de cada autor."""
import os
import time

from utils.parse import *


def compile_corpus(path: str = 'new_files', mode=None) -> None:
    """Finds the files in the new_files folders and compiles a corpus in JSON format."""
    if mode is None:
        for folder_subcorpus in [x for x in os.listdir(path) if x != '__test']:
            print(f'> {folder_subcorpus} autors trobats en new_files.')
            for folder in os.listdir(path + '/' + folder_subcorpus):
                author_meta = read_metadata(f'{path}/{folder_subcorpus}/{folder}', "author")
                corpus = author_meta
                print(
                    f'\t>> {len(os.listdir(f"{path}/{folder_subcorpus}/{folder}"))} llibres de l\'autor \'{folder.upper()}\'.')
                for subfolder in os.listdir(f'{path}/{folder_subcorpus}/{folder}'):
                    if not subfolder.endswith('.info'):
                        book_meta = read_metadata(f'{path}/{folder_subcorpus}/{folder}/{subfolder}', "book")
                        corpus['books'].update({subfolder: book_meta})
                        print(
                            f'\t\t>>> {len(os.listdir(f"{path}/{folder_subcorpus}/{folder}/{subfolder}"))} pàgines del llibre \'{subfolder}\'.')
                        for file in os.listdir(f'{path}/{folder_subcorpus}/{folder}/{subfolder}'):
                            if file.endswith('.txt'):
                                poem = extract_poem(f'{path}/{folder_subcorpus}/{folder}/{subfolder}/{file}')
                                corpus['books'][subfolder]['poems'].update({file: poem})

                # Crea una carpeta dins la carpeta 'corpora' amb el nom de la carpeta del path, si no existeix.
                if not os.path.exists(f'../corpora/{path}/'):
                    os.makedirs(f'../corpora/{path}/')
                    print(f'La carpeta \'{path}\' ha estat creada.')

                # Fes que el directori tengui aquesta estructura:
                # corpora/{path}/sense_etiquetar/json/{folder}.json
                if not os.path.exists(f'../corpora/{path}/sense_etiquetar/json/'):
                    os.makedirs(f'../corpora/{path}/sense_etiquetar/json/')
                    print(f'La carpeta \'{path}/sense_etiquetar/json\' ha estat creada.')
                with open(f"../corpora/{path}/sense_etiquetar/json/{folder}.json", "w", encoding="utf-8") as json_file:
                    json.dump(corpus, json_file, ensure_ascii=False, indent=2)
                    print('-' * 50)
                    print(f'{folder}.json desat.')

    print('Corpus compilat amb èxit.')
    print(f'{len(os.listdir(f"../corpora/{path}/sense_etiquetar/json"))} autors compilats.')


if __name__ == "__main__":
    start_time = time.time()
    print('Aquests són els corpus disponibles:')
    opcions = [x for x in os.listdir('../compilador') if x != 'utils' and os.path.isdir(x)]
    for opcio in opcions:
        print(f"\t-- {opcio}")

    ordre = input('Quin corpus voleu compilar?\t')
    if ordre != "":
        compile_corpus(path=ordre)
    else:
        compile_corpus()
    end_time = time.time()
    execution_time = end_time - start_time

    minutes = int(execution_time // 60)
    seconds = int(execution_time % 60)

    print(f'El programa ha tardat {minutes} minuts i {seconds} segons en executar-se.')
