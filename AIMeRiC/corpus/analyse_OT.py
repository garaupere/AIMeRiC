"""Un mòdul per a realitzar les anàlisis OT del corpus AIMeRiC."""
import os

import pandas as pd
from tqdm import tqdm

from AIMeRiC.corpus.modules.OT_constraints import OT_constraints
from AIMeRiC.corpus.modules.getUSB import getUSB


def ot_analysis(corpus):

    rankings = []
    for author in tqdm(os.listdir(fr'{getUSB()}\corpora\{corpus}\etiquetat\csv\\'), desc='Avaluant les dades del corpus'):
        data = read_csv(fr'{getUSB()}\corpora\{corpus}\etiquetat\csv\\' + author)
        data = normalitza(data)
        patrons = patterns(data)
        OT_avaluacio = OT_eval(patrons)
        jerarquia = ranking(OT_avaluacio)
        rankings.append(jerarquia)

        # Desa OT_avaluacio en un Excel
        OT_avaluacio.to_excel(fr'{getUSB()}\corpora\{corpus}\etiquetat\ot\ot.' + author.replace('.csv', '.xlsx'),
                              index=False)

    # Desa els rankings en un Excel [autor, ranking]
    rankings = pd.DataFrame(rankings, columns=['ranking'])
    rankings['autor'] = [x.replace('.csv', '') for x in os.listdir(fr'{getUSB()}\corpora\{corpus}\etiquetat\csv\\')]
    rankings = rankings[['autor', 'ranking']]
    rankings.to_excel(fr'{getUSB()}\corpora\{corpus}\etiquetat\ot\rankings.xlsx', index=False)

    # Obté les dades globals i avalua les restriccions OT
    glob_data = global_data(fr'{getUSB()}\corpora\{corpus}\etiquetat\{corpus}.csv')
    glob_data = OT_eval(glob_data)

    # Desa les dades globals en un Excel
    glob_data.to_excel(fr'{getUSB()}\corpora\{corpus}\etiquetat\ot\ot.{corpus}.xlsx', index=False)

    # Calcula el ranking global
    ranking_global = ranking(glob_data)
    # Desa el ranking global en un fitxer de text
    with open(fr'{getUSB()}\corpora\{corpus}\etiquetat\ot\ranking_global.txt', 'w') as file:
        file.write(ranking_global)
    print("Anàlisi OT completada. Jerarquia detectada:", ranking_global)


def global_data(data):
    """Obté tots els patrons del corpus quantificats"""
    data = read_csv(data)
    data = normalitza(data)
    pattern_colum = data[['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']].apply(
        lambda x: ''.join(x.astype(str)), axis=1)
    patterns = []
    for pattern in pattern_colum:
        patterns.append(pattern)

    # Compta les repeticions de cada patró i genera un DataFrame amb els resultats
    patterns = pd.Series(patterns).value_counts().reset_index()
    patterns.columns = ['patró', 'freqüència']
    patterns = patterns.sort_values(by='freqüència', ascending=False)

    # Afegeix la freqüència relativa
    patterns['freqüència relativa'] = patterns['freqüència'] / patterns['freqüència'].sum() * 100

    return patterns


def read_csv(path):
    """Carrega un fitxer csv a un DataFrame"""
    data = pd.read_csv(path, sep=';', encoding='utf-8', lineterminator='\n', header=0)
    return data


def normalitza(data):
    sillabes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    data[sillabes] = data[sillabes].map(
        lambda x: 1 if x > 1 else 0)  # 1 si és major que 1, 0 si no ho és

    return data


def patterns(data):
    """Aquesta funció genera una llista amb els diferents patrons del corpus quantificats"""
    pattern_colum = data[['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']].apply(
        lambda x: ''.join(x.astype(str)), axis=1)
    patterns = []
    for pattern in pattern_colum:
        patterns.append(pattern)

    # Compta les repeticions de cada patró i genera un DataFrame amb els resultats
    patterns = pd.Series(patterns).value_counts().reset_index()
    patterns.columns = ['patró', 'freqüència']
    patterns = patterns.sort_values(by='freqüència', ascending=False)

    # Afegeix la freqüència relativa
    patterns['freqüència relativa'] = patterns['freqüència'] / patterns['freqüència'].sum() * 100

    return patterns


def OT_eval(data):
    """Aquesta funció avalua les restriccions OT per a cada patró"""
    evals = []
    for pattern in data['patró']:
        eval = OT_constraints(pattern).eval()
        evals.append(eval)
    # Disposa l'avaluació en el DataFrame
    cons = OT_constraints('').list_constraints()
    data = pd.concat([data, pd.DataFrame(evals, columns=cons)], axis=1)

    return data


def ranking(data):
    """Aquesta funció genera un ranking de les restriccions OT: les restriccions ordenades de menys violada a més violada"""
    # Calcula el ranking de cada patró

    ranking = {}
    rankings = {'clash': 0, 'extra-clash': 0, 'lapse': 0, 'extra-lapse': 0, 'ws-hl': 0, 'non-initial': 0, 'symetry': 0}
    for pattern, fq in data[['patró', 'freqüència']].values:
        ot = OT_constraints(pattern)
        ranking[pattern] = ot.weigth(fq)
        rankings = {k: v + ranking[pattern][k] for k, v in rankings.items()}

    # Suma les violacions de cada restricció
    ranking = {k: v for k, v in sorted(rankings.items(), key=lambda item: item[1])}

    # Ordena el ranking de restricció menys violada a més violada
    ranking = {k: v for k, v in sorted(ranking.items(), key=lambda item: item[1])}

    # Disposem el ranking en una llista
    ranking = ' >> '.join([f'{key} ({value})' for key, value in ranking.items()])

    return ranking


if __name__ == '__main__':
    ot_analysis('actual')
