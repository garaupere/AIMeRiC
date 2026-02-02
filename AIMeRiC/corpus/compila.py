"""Un mòdul per a compilar el corpus de cada autor."""

from tqdm import tqdm
from AIMeRiC.corpus.modules.getUSB import getUSB
from AIMeRiC.corpus.modules.parse import *
from AIMeRiC.corpus.wikidata import get_person_info, get_wikidata_id
import time

usb = getUSB()


def ctilc(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        autor_name = re.findall(r'<AUTOR>(.*?)</AUTOR>', ''.join(lines), re.DOTALL)[0]
        autor_name_original = autor_name
        reverse_name = autor_name.split(",")
        if len(reverse_name) > 1:
            autor_name = reverse_name[1] + ' ' + reverse_name[0]
        autor_name = re.sub(r'\s+', ' ', autor_name).strip()
        get_info = get_person_info(get_wikidata_id(autor_name))
        if get_info:
            corpus_dict = get_info
            corpus_dict['author_id'] = autor_name_original
            corpus_dict['fast_tag'] = 'ctilc'


        else:
            corpus_dict = {
                'author_id': autor_name.replace('\xad', ''),
                'name': autor_name,
                'books': {}
            }
        book_title = re.findall(r'<TÍTOL>(.*?)</TÍTOL>', ''.join(lines), re.DOTALL)
        book_date = re.findall(r'<ANY>(.*?)</ANY>', ''.join(lines), re.DOTALL)

        book_meta = {
            'title': book_title[0],
            'date': book_date[0],
            'poems': {}
        }
        corpus_dict['books'].update({book_title[0]: book_meta})

        text = ''.join(re.findall(r'<TEXT>(.*?)</TEXT>', ''.join(lines), re.DOTALL))

        poem = list(filter(None, text.split('\n')))
        corpus_dict['books'][book_title[0]]['poems'].update({'text': poem})
        return corpus_dict


def compile_corpus(path: str, corpus: str) -> None:
    """Finds the files in the new_files folders and compiles a corpus in JSON format."""
    drive = path
    corpus_path = drive + corpus
    print(f'Compilant el corpus \'{corpus}\'...')

    if corpus == 'ctilc':
        # print(f'Compilant el corpus \'{corpus}\'...')
        print("HA SELECCIONAT TORNAR A COMPILAR EL CTILC.")
        input_sing = input("Això sobreescriurà els fitxers .json existents. Voleu continuar? (s/n): ")
        if input_sing.lower() != 's':
            print("Operació cancel·lada. No s'han fet canvis.")
            return
        else:
            print("Continuant amb la recompilació del corpus CTILC...")
            for file in os.listdir(corpus_path + '/'):
                if file.endswith('.xml'):
                    corpus_dict = ctilc(corpus_path + '/' + file)
                    if not os.path.exists(f'{usb}/corpora/'):
                        os.makedirs(f'{usb}/corpora/')
                    #    print(f'>> La carpeta \'{usb}/corpora\' ha estat creada.')
                    if not os.path.exists(f'{usb}/corpora/{corpus}/'):
                        os.makedirs(f'{usb}/corpora/{corpus}/')
                    #    print(f'\t>> La carpeta \'{usb}corpora/{corpus}\' ha estat creada.')

                    # Fes que el directori tengui aquesta estructura:
                    # corpora/{path}/sense_etiquetar/json/{folder}.json
                    if not os.path.exists(f'{usb}/corpora/{corpus}/sense_etiquetar/json/'):
                        os.makedirs(f'{usb}/corpora/{corpus}/sense_etiquetar/json/')
                    #    print(f'\t\t>> La carpeta \'{usb}/corpora/{corpus}/sense_etiquetar/json\' ha estat creada.')
                    name = corpus_dict['name']
                    with open(f"{usb}/corpora/{corpus}/sense_etiquetar/json/{name}.json", "w",
                              encoding="utf-8") as json_file:
                        json.dump(corpus_dict, json_file, ensure_ascii=False, indent=2)
                    #    print('-' * 40)
                    #    print(f"\t>> '{folder}.json' desat.")
        return

    for folder_subcorpus in [x for x in os.listdir(corpus_path) if x != '__test']:
        # print(f'> {folder_subcorpus} autors trobats en new_files.')
        for folder in tqdm(os.listdir(corpus_path + '/' + folder_subcorpus), desc='Compilant el corpus'):
            subcorpus_path = corpus_path + '/' + folder_subcorpus
            author_meta = read_metadata(subcorpus_path + '/' + folder, "author")
            corpus_dict = author_meta
            # print(f'\t> {folder} autor trobat en new_files.')

            for subfolder in os.listdir(subcorpus_path + '/' + folder):
                if not subfolder.endswith('.info'):
                    book_path = subcorpus_path + '/' + folder + '/' + subfolder
                    book_meta = read_metadata(book_path, "book")
                    corpus_dict['books'].update({subfolder: book_meta})
                    # print(
                    #    f'\t\t>>> {len(os.listdir(book_path))} pàgines del llibre \'{subfolder}\'.')

                    for file in os.listdir(book_path):
                        if file.endswith('.txt'):
                            file_path = book_path + '/' + file
                            poem = extract_poem(file_path, corpus)
                            corpus_dict['books'][subfolder]['poems'].update({file: poem})

            # Crea la carpeta 'corpora'
            # print('-' * 40)
            if not os.path.exists(f'{usb}/corpora/'):
                os.makedirs(f'{usb}/corpora/')
            #    print(f'>> La carpeta \'{usb}/corpora\' ha estat creada.')
            if not os.path.exists(f'{usb}/corpora/{corpus}/'):
                os.makedirs(f'{usb}/corpora/{corpus}/')
            #    print(f'\t>> La carpeta \'{usb}corpora/{corpus}\' ha estat creada.')

            # Fes que el directori tengui aquesta estructura:
            # corpora/{path}/sense_etiquetar/json/{folder}.json
            if not os.path.exists(f'{usb}/corpora/{corpus}/sense_etiquetar/json/'):
                os.makedirs(f'{usb}/corpora/{corpus}/sense_etiquetar/json/')
            #    print(f'\t\t>> La carpeta \'{usb}/corpora/{corpus}/sense_etiquetar/json\' ha estat creada.')

            with open(f"{usb}/corpora/{corpus}/sense_etiquetar/json/{folder}.json", "w", encoding="utf-8") as json_file:
                json.dump(corpus_dict, json_file, ensure_ascii=False, indent=2)
            #    print('-' * 40)
            #    print(f"\t>> '{folder}.json' desat.")

    # print('-' * 40)
    # print(f"\t>> Corpus compilat amb èxit i desat a '{usb}/corpora/{corpus}'.")
    # print(f'\t>> {len(os.listdir(f"{usb}/corpora/{corpus}/sense_etiquetar/json"))} autors compilats dins el corpus.')
    # print('-' * 40)


if __name__ == "__main__":
    print('Aquests són els corpus disponibles:')

    raw_files_path = rf"{usb}/compile_files/"

    for folder in os.listdir(raw_files_path):
        print(f'\t• {folder}')

    enter = input('Quin corpus voleu compilar?\t')

    start_time = time.time()
    try:
        compile_corpus(path=raw_files_path, corpus=enter)
    except FileNotFoundError:
        print(f'{FileNotFoundError}: No s\'ha seleccionat cap corpus.')

    end_time = time.time()
    execution_time = end_time - start_time

    minutes = int(execution_time // 60)
    seconds = int(execution_time % 60)

    print('-' * 40)
    print(f'El programa ha tardat {minutes} minuts i {seconds} segons en executar-se.')
