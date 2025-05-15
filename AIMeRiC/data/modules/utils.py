"""Un mòdul amb eines usades en l'etiquetatge del corpus"""
import pandas as pd


def aplica_filtre(dades, filtre):
    """Selecciona només les dades que presenten la subdivisió indicada"""
    return dades[dades['subdivisió'] == filtre]

def read_csv(path):
    """Carrega un fitxer csv a un DataFrame"""
    data = pd.read_csv(path, sep=';', encoding='utf-8', lineterminator='\n', header=0, low_memory=False)
    return data