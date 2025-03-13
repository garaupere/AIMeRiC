"""Un mòdul per a realitzar les anàlisis OT del corpus AIMeRiC."""
import os

import pandas as pd
from tabulate import tabulate
from tqdm import tqdm

from AIMeRiC.corpus.modules.OT_constraints import OT_constraints, enjambment
from AIMeRiC.corpus.modules.getUSB import getUSB


def ot_analysis(corpus):
    rankings = []
    for author in tqdm(os.listdir(fr'{getUSB()}\corpora\{corpus}\etiquetat\csv\\'),
                       desc='Avaluant les dades del corpus'):
        data = read_csv(fr'{getUSB()}\corpora\{corpus}\etiquetat\csv\\' + author)
        data = normalitza(data)
        patrons = patterns(data)
        OT_avaluacio = OT_eval(patrons)
        jerarquia = ranking(OT_avaluacio)
        rankings.append(jerarquia)
        author_tableau = generate_tableau(OT_avaluacio, jerarquia)
        # Desa el tableau en un Excel
        author_tableau.to_excel(
            fr'{getUSB()}\corpora\{corpus}\etiquetat\ot\ot.' + author.replace('.csv', '.tableau.xlsx'),
            index=False)

        # Desa OT_avaluacio en un Excel
        OT_avaluacio.to_excel(fr'{getUSB()}\corpora\{corpus}\etiquetat\ot\ot.' + author.replace('.csv', '.xlsx'),
                              index=False)

    # Desa els rankings en un Excel [autor, ranking]
    rankings = pd.DataFrame(rankings)
    rankings['autor'] = [x.replace('.csv', '') for x in os.listdir(fr'{getUSB()}\corpora\{corpus}\etiquetat\csv\\')]
    rankings = rankings[['autor'] + list(rankings.columns)[:-1]]
    rankings.to_excel(fr'{getUSB()}\corpora\{corpus}\etiquetat\ot\rankings.xlsx', index=False)

    # Obté les dades globals i avalua les restriccions OT
    glob_data = global_data(fr'{getUSB()}\corpora\{corpus}\etiquetat\{corpus}.csv')
    glob_data = OT_eval(glob_data)

    # Desa les dades globals en un Excel
    glob_data.to_excel(fr'{getUSB()}\corpora\{corpus}\etiquetat\ot\ot.{corpus}.xlsx', index=False)

    # Calcula el ranking global
    ranking_global = ranking(glob_data, fr'{getUSB()}\corpora\{corpus}\etiquetat\{corpus}.csv')
    # Desa el ranking global en un Excel
    pd.DataFrame(ranking_global.items(), columns=['restricció', 'violacions']).to_excel(
        fr'{getUSB()}\corpora\{corpus}\etiquetat\ot\ranking_global.xlsx', index=False)

    taleau = generate_tableau(glob_data, ranking_global)
    # Desa el tableau en un Excel
    taleau.to_excel(fr'{getUSB()}\corpora\{corpus}\etiquetat\ot\tableau.xlsx', index=False)
    print(tabulate(taleau, headers='keys', tablefmt='grid'))
    print("Anàlisi OT completada. Jerarquia detectada:", ' >> '.join([f'{k}({v})' for k, v in ranking_global.items()]))


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


def ranking(data, path=None):
    """Aquesta funció genera un ranking de les restriccions OT: les restriccions ordenades de menys violada a més violada"""
    # Calcula el ranking de cada patró

    ranking = {}
    rankings = {k: 0 for k in OT_constraints('').list_constraints()}
    for pattern, fq in data[['patró', 'freqüència']].values:
        ot = OT_constraints(pattern)
        ranking[pattern] = ot.weigth(fq)
        rankings = rankings = {k: v + ranking[pattern].get(k, 0) for k, v in rankings.items()}

    # Suma les violacions de cada restricció
    ranking = {k: v for k, v in sorted(rankings.items(), key=lambda item: item[1])}

    # Afegeix alignL al ranking global
    if path:
        ranking['alignL'] = alignL(path)[0]
        ranking['extrametricallity'] = extrametric(path)

    # Ordena el ranking de restricció menys violada a més violada
    ranking = {k: v for k, v in sorted(ranking.items(), key=lambda item: item[1])}

    return ranking


def alignL(path):
    data = read_csv(path)
    data = normalitza(data)

    enjambments = []
    for row in data['encavalcament']:
        enjambments.append(enjambment(row))
    return sum(enjambments), sum(enjambments) / len(enjambments) * 100


def extrametric(path):
    data = read_csv(path)
    data = normalitza(data)
    return data['síl·labes extramètriques'].sum()


def generate_tableau(eval, ranking):
    """Genera un tableau amb les dades de l'anàlisi OT"""
    if 'alignL' in ranking:
        ranking.pop('alignL')
    if 'extrametricallity' in ranking:
        ranking.pop('extrametricallity')
    jerarquia = list(ranking.keys())
    eval = eval.loc[:, ['patró', 'freqüència', 'freqüència relativa'] + jerarquia]

    # Canvia els valors numèrics de les restriccions per * i ** segons el valor en el dataframe
    for con in jerarquia:
        eval[con] = eval[con].map(lambda x: '*' * x if x > 0 else '')
    return eval


if __name__ == '__main__':
    ot_analysis('__test')
