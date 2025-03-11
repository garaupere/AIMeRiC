import os

import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub

from AIMeRiC.corpus.modules.getUSB import getUSB


def clean_html(html_content):
    # Utilitzar BeautifulSoup per parsejar el contingut HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    # Extreure el text net de les etiquetes HTML
    clean_text = soup.get_text(separator='\n')
    return clean_text


def convert_epub_to_txt(path, file):
    # Obrir el fitxer EPUB
    file_path = os.path.join(path, file)
    book = epub.read_epub(file_path)

    # Crear un directori per a guardar els fitxers de text si no existeix
    path_txt = f"{usb}/epub_files/txt/"
    name = file.replace(".epub", "")
    txt_file_path = f"{path_txt}{name}/"
    if not os.path.exists(txt_file_path):
        os.makedirs(txt_file_path)

    # Iterar sobre cada pàgina del llibre
    for i, item in enumerate(book.get_items()):
        # Només processar els elements de tipus XHTML (pàgines de text)
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            # Extreure el text net del contingut HTML
            clean_text = clean_html(item.get_body_content().decode('utf-8'))
            # Crear un fitxer de text per a cada pàgina
            with open(txt_file_path + '/' + str(i) + '.txt', 'w', encoding='utf-8') as txt_file:
                # Escriure el text net al fitxer de text
                txt_file.write(clean_text)


def epub2txt_ctilc(path, file):
    # Obrir el fitxer EPUB
    file_path = os.path.join(path, file)
    book = epub.read_epub(file_path)
    # Crear un directori per a guardar els fitxers de text si no existeix
    path_txt = f"{usb}/epub_files/txt/"
    name = file.replace(".epub", "")
    txt_file_path = f"{path_txt}{name}/"
    if not os.path.exists(txt_file_path):
        os.makedirs(txt_file_path)

    # Iterar sobre cada pàgina del llibre
    with open(name.replace('epub', 'txt'), 'w', encoding='utf-8') as txt_file:
        for i, item in enumerate(book.get_items()):
            # Només processar els elements de tipus XHTML (pàgines de text)
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                # Extreure el text net del contingut HTML
                clean_text = clean_html(item.get_body_content().decode('utf-8'))
                # Escriure el text net al fitxer de text
                txt_file.write(clean_text)


if __name__ == "__main__":
    usb = getUSB()
    path = f"{usb}/epub_files/epub/"
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            if file.endswith(".epub"):
                convert_epub_to_txt(path, file)
