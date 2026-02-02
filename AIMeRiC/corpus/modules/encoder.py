import codecs
import os

from AIMeRiC.corpus.modules.getUSB import getUSB


def convert(path):
    for file_name in os.listdir(path):
        if file_name.endswith('.txt'):
            print('Llegint el fitxer:', file_name)
            with codecs.open(f'{path}/{file_name}', 'r', encoding='ansi') as file:
                lines = file.read()

            print('Convertint el fitxer a UTF-8:', file_name)
            with codecs.open(f'{path}/{file_name}', 'w', encoding='utf-8') as file:
                file.write(lines)
    print("Conversió finalitzada.")


if __name__ == "__main__":
    ruta_carpeta = f"{getUSB()}/compile_files/wikicorpus/files/catalan/corpus"
    convert(ruta_carpeta)
