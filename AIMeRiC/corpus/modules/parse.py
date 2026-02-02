"""Un mòdul per gestionar la lectura dels fitxers txt del corpus."""
import json
import os
import re
from json import JSONDecodeError


def should_ignore_page(content: str) -> bool:
    """Determines if a page should bé ignored based on the presence of keywords."""
    keywords = ['....', '---', 'taula de continguts', 'TAULA DE CONTINGUTS', 'ÍNDEX', 'INDEX', 'PRÒLEG', 'PROLEG',
                'Pròleg', 'Proleg', 'EPÍLEG', 'EPILEG', 'Epíleg', 'Epileg', 'NOTES']
    for keyword in keywords:
        if keyword in content:
            return True
    return False


def read_metadata(folder, level: str) -> dict:
    """Reads the metadata from the .info file in folder."""
    author_info = folder + "/" + level + ".info"
    with open(author_info, 'r', encoding='utf-8') as file:
        try:
            content = file.read()
            metadata = json.loads(content)
        except JSONDecodeError:
            print(f'Error: {JSONDecodeError}, en el fitxer: {author_info}')
            return {}
        if level == "author":
            metadata['books'] = dict()
        elif level == "book":
            metadata['poems'] = dict()
        return metadata


def extract_poem(txt_file: str, corpus: str) -> list[str]:
    """Extracts the poem from the text file."""
    with open(txt_file, 'r', encoding='utf-8') as file:
        content = file.read()
        if corpus != 'viquipedia':
            # Comprova si el contingut està buit o només conté espais en blanc
            if content.isspace():
                #print(f'\t\t\tSkipping file {txt_file} due to empty content or whitespaces only.')
                if os.stat(txt_file).st_size == 0:
                    #print("\t\t\t\tRemoving ", txt_file)
                    os.remove(txt_file)
                return []

            if should_ignore_page(content):
                #print(f'\t\t\tSkipping file {txt_file} due to table of contents or index.')
                return []
        poem = re.sub(r"\d+", "", content)  # Removes numbers
        poem = re.sub(r"<[ib]>.*</[ib]>", "", poem)  # Removes italicized text
        poem = re.sub(r"(</?[ib>]|[<>])", "", poem)
        poem = re.sub(r"(<.*>|ENDOFARTICLE)", "", poem)  # Removes <doc> tags
        poem = list(filter(None, poem.split('\n')))
        return poem
