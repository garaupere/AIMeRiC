"""Escaneja prosòdicament els mots d'un diccionari. Parteix del catalan-dict-tools (Softcatalà, J. Ortolà): https://github.com/Softcatala/catalan-dict-tools"""
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
            prosodia = escaneja(nlp, mot, goal=2)
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
    diccionari = pd.read_csv(f'{getUSB()}/corpora/diccionari/frequencies-dict-forms.txt', sep=',', encoding='utf-8')
    diccionari.columns = ['mot', 'freqüència']
    resultats = []
    for index, row in tqdm(diccionari.iterrows(), desc="Etiquetant el diccionari", total=len(diccionari)):
        mot = row['mot']
        try:
            prosodia = escaneja(nlp, mot, goal=2)
            resultats.append({
                'mot': mot,
                'frequencia': row['freqüència'],
                'escansio': prosodia.escansio_text,
                'contorn_cru': prosodia.patro,
                'contorn': prosodia.contorn_accentual
            })
        except:
            resultats.append({
                'mot': mot,
                'frequencia': row['freqüència'] if 'freqüència' in row else np.nan,
                'escansio': np.nan,
                'contorn_cru': np.nan,
                'contorn': np.nan
            })

    resultats = pd.DataFrame(resultats)
    return resultats


if __name__ == "__main__":
    nlp = spacy.load('ca_core_news_lg')
    diccionari = pd.read_csv('diccionari.txt', sep=' ', dtype=str, encoding='utf-8')
    diccionari.columns = ['mot', 'mot2', 'categoria']
    resultats = escaneja_diccionari(nlp, diccionari.tail(20))
    resultats.columns = ['mot', 'escansio', 'contorn_cru', 'contorn']
    #print(resultats.to_string)
    resultats.to_csv('diccionari_escansionat.csv', index=False, encoding='utf-8', sep=';')
    print("Escansió del diccionari completada i desada a 'diccionari_escansionat.csv'.")
