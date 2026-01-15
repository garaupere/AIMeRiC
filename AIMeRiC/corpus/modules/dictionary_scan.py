"""Escaneja prosòdicament els mots d'un diccionari. Parteix del catalan-dict-tools (Softcatalà, J. Ortolà): https://github.com/Softcatala/catalan-dict-tools"""
import re

import numpy as np
import pandas as pd
import spacy
from AIMeRiC.corpus.modules.getUSB import getUSB

from AIMeRiC.escansio.escansor import escaneja
from tqdm import tqdm


def escaneja_diccionari(nlp):
    diccionari = pd.read_csv(f'{getUSB()}/corpora/diccionari/diccionari.txt', sep=' ', dtype=str, encoding='utf-8')
    diccionari.columns = ['mot', 'mot2', 'categoria']
    resultats = []
    for index, row in tqdm(diccionari.iterrows(), desc="Etiquetant el diccionari", total=len(diccionari)):
        mot = row['mot']
        try:
            prosodia = escaneja(nlp, mot, goal=10, permet_llicencies=False)
            resultats.append({
                'mot': mot,
                'escansio': prosodia.escansio_text,
                'contorn_cru': prosodia.patro,
                'contorn': prosodia.contorn_accentual
            })
        except:
            resultats.append({
                'mot': mot,
                'escansio': np.nan,
                'contorn_cru': np.nan,
                'contorn': np.nan
            })

    resultats = pd.DataFrame(resultats)
    return resultats


def escaneja_diccionari_frequencies(nlp):
    diccionari = pd.read_csv(f'{getUSB()}/corpora/diccionari/FREQDCC.csv', sep='\t', dtype=str, encoding='ansi')
    diccionari.columns = ['mot', 'categoria', 'freqüència']
    resultats = []
    for index, row in tqdm(diccionari.iterrows(), desc="Etiquetant el diccionari", total=len(diccionari)):
        mot = row['mot']
        try:
            prosodia = escaneja(nlp, mot, goal=2, permet_llicencies=False)
            contorn = ''.join([str(x) for x in prosodia.patro])
            contorn = re.sub(r'[012]', '0', contorn)
            contorn = re.sub(r'[345]', '1', contorn)
            if not prosodia.patro:
                continue
            resultats.append({
                'mot': mot,
                'categoria': row['categoria'],
                'frequencia': row['freqüència'],
                'escansio': prosodia.escansio_text,
                'contorn_cru': prosodia.patro,
                'contorn': contorn
            })
        except:
            continue  # en cas d'error no desam la paraula

    resultats = pd.DataFrame(resultats)
    return resultats

if __name__ == "__main__":
    nlp = spacy.load('ca_core_news_lg')
    resultat = escaneja_diccionari_frequencies(nlp)
    print(resultat.to_string())
