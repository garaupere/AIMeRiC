import os
import json

from AIMeRiC.corpus.modules.getUSB import getUSB


def form_book(path: str):
    for folder in os.listdir(path):
        print(folder)
        book_dict = {}
        book_title = folder.split('--')[0].strip()
        print(book_title)
        year = folder.split('--')[2].strip() if len(folder.split('--')) > 2 else None
        book_dict[book_title] = {
            "title": book_title,
            'year': year,
            'publisher': '-',
            'font': 'Llibre electrònic',
            'poems': {}
        }
        folder_path = os.path.join(path, folder)
        for file in os.listdir(folder_path):
            with open(os.path.join(folder_path, file), 'r', encoding='utf-8') as f:
                content = f.read().splitlines()
                book_dict[book_title]['poems'].update({file: content})

        with open(f'{path}{book_title.replace(" ", "_")}.json', 'w', encoding='utf-8') as json_file:
            json.dump(book_dict, json_file, ensure_ascii=False, indent=4)

        print(f"Desat el llibre {book_title} en format JSON.")


if __name__ == "__main__":
    path = f'{getUSB()}/epub_files/txt/'
    form_book(path)
