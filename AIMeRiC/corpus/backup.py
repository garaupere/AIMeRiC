"""Un mòdul per a gestionar les còpies de seguretat del corpus."""

import os
import time
import zipfile
from datetime import datetime
from tqdm import tqdm


def backup_files(corpus_path, backup_path):
    dia = datetime.today().strftime('%Y-%m-%d')
    with zipfile.ZipFile(f'{backup_path}backup_{dia}.zip', 'w') as ziph:
        for root, dirs, files in tqdm(os.walk(corpus_path), desc='Comprimint la còpia de seguretat', ncols=80):
            if '.backup' in dirs:
                dirs.remove('.backup')
            if 'System Volume Information' in dirs:
                dirs.remove('System Volume Information')

            for file in files:
                ziph.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file),
                                           os.path.join(corpus_path, '..')))


if __name__ == '__main__':
    start = time.time()
    backup_path = "C:\\Users\\pere\\OneDrive - Universitat de les Illes Balears\\Documents\\UIB\\Estudis oficials\\Doctorat en Filologia i Filosofia\\Tesi\\TESI ESPAI DE TREBALL NET\\DADES\\.backup\\"
    corpus_path = "E:/"
    backup_files(corpus_path, backup_path)
    elapsed_time = time.time() - start
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    print(f"Temps d'execució: {minutes} minuts i {seconds} segons")
