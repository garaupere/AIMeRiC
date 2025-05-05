import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tabulate import tabulate
from tqdm import tqdm
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram

from AIMeRiC.corpus.modules.getUSB import getUSB
from AIMeRiC.corpus.modules.utils import aplica_filtre

plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams["font.family"] = "Times New Roman"

usb = getUSB()


def analitza_corpus(corpus, filtre=None):
    p_bar = tqdm(range(11))
    root = fr"{usb}/corpora/"
    data = read_csv(f'{root}{corpus}/etiquetat/{corpus}.csv')
    if filtre:
        data = aplica_filtre(data, filtre)
    p_bar.update(1)
    data = normalitza(data)
    p_bar.update(1)
    contorn_ritmic(data, corpus)
    p_bar.update(1)
    distancia_iambe(data, corpus)
    p_bar.update(1)
    mitjana(data, corpus)
    p_bar.update(1)
    cmap_accents(data, corpus)
    p_bar.update(1)
    cmap_subdivisions(data, corpus)
    p_bar.update(1)
    index_binarietat(data, corpus)
    p_bar.update(1)
    if corpus != '__test':
        dendrograma(data, corpus)
        dendrograma_lang(data, corpus)
    p_bar.update(2)
    autors_individuals(data, corpus)
    p_bar.update(1)


def read_csv(path):
    """Carrega un fitxer csv a un DataFrame"""
    data = pd.read_csv(path, sep=';', encoding='utf-8', lineterminator='\n', header=0)
    return data


def normalitza(data):
    sillabes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    data[sillabes] = data[sillabes].applymap(
        lambda x: 1 if int(x) > 1 else 0)  # 1 si és major que 1, 0 si no ho és

    return data


def contorn_ritmic(data, name):
    """Genera un DataFrame amb el contorn rítmic de cada autor i fes-ne un gràfic."""
    sillabes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    df = data.groupby('autor')[sillabes].mean() * 100
    # Desa el DataFrame en un fitxer xlsx
    df.to_excel(f'{usb}/corpora/{name}/etiquetat/xlsx/contorn_ritmic.xlsx')
    # Genera un gràfic amb el contorn rítmic de cada autor

    x_values = range(1, 11)
    for autor in df.index:
        plt.plot(x_values, df.loc[autor], marker='o', linestyle='--', label=autor)
    autors_mean = df.mean()

    plt.plot(x_values, autors_mean, marker='x', linestyle='-', color='red', label='Mitjana')
    plt.axhline(50, color='gray', linestyle='-', alpha=0.2)
    plt.xticks(np.arange(0, 11))
    plt.legend()
    plt.grid(False)
    plt.tight_layout()
    # Desa el gràfic en svg
    plt.savefig(f'{usb}/corpora/{name}/etiquetat/svg/contorn_ritmic.svg')

    # Desa el gràfic en svg
    plt.savefig(f'{usb}/corpora/{name}/etiquetat/svg/distancia_iambe.svg')
    plt.close()


def distancia_iambe(data, name):
    # Calcula la distància respecte del model per a cada síl·laba
    sillabes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    df = data.groupby('autor')[sillabes].mean() * 100
    model = [0, 100, 0, 100, 0, 100, 0, 100, 0, 100]
    distancies = pd.DataFrame()
    for autor in df.index:
        distancies[autor] = np.abs(df.loc[autor] - model)
    distancies.T.to_excel(f'{usb}/corpora/{name}/etiquetat/xlsx/distancia_iambe.xlsx')

    # Genera un gràfic amb la distància respecte del model per a cada síl·laba
    x_values = range(1, 11)
    for autor in distancies.columns:
        plt.plot(x_values, distancies[autor], marker='o', linestyle='--', label=autor)
    plt.plot(x_values, [0] * 10, marker='x', linestyle='-', color='gray', label='Iàmbic')
    plt.axhline(50, color='gray', linestyle='-', alpha=0.2)
    plt.xticks(np.arange(0, 11))
    plt.legend()
    plt.grid(False)
    plt.tight_layout()
    # Desa el gràfic en svg
    plt.savefig(f'{usb}/corpora/{name}/etiquetat/svg/distancia_iambe.svg')
    plt.close()


def autors_individuals(data, name):
    """Una funció per a cada autor"""
    sillabes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    df = data.groupby('autor')[sillabes].mean() * 100
    # Calcula la distància respecte del model per a cada síl·laba
    model = [0, 100, 0, 100, 0, 100, 0, 100, 0, 100]
    distancies = pd.DataFrame()
    for autor in df.index:
        distancies[autor] = np.abs(df.loc[autor] - model)

    # Itera cada autor del DataFrame
    if not os.path.exists(f'{usb}/corpora/{name}/etiquetat/svg/autors/'):
        os.makedirs(f'{usb}/corpora/{name}/etiquetat/svg/autors/')
    for autor in df.index:
        # Comprova si l'autor té una carpeta al directori 'gràfics'
        if not os.path.exists(f'{usb}/corpora/{name}/etiquetat/svg/autors/{autor}'):
            os.makedirs(f'{usb}/corpora/{name}/etiquetat/svg/autors/{autor}')
        # Genera un gràfic amb el contorn rítmic de cada autor
        plt.plot(range(1, 11), df.loc[autor], marker='o', linestyle='--')
        plt.axhline(50, color='gray', linestyle='-', alpha=0.2)
        plt.xticks(np.arange(0, 11))
        plt.grid(False)
        plt.tight_layout()
        # Desa el gràfic en svg
        plt.savefig(f'{usb}/corpora/{name}/etiquetat/svg/autors/{autor}/contorn_ritmic.svg')
        plt.close()

        # Gràfic
        plt.plot(range(1, 11), distancies[autor], marker='o', linestyle='--')
        plt.plot(range(1, 11), [0] * 10, marker='x', linestyle='-', color='gray')
        plt.axhline(50, color='gray', linestyle='-', alpha=0.2)
        plt.xticks(np.arange(0, 11))
        plt.grid(False)
        plt.tight_layout()
        # Desa el gràfic en svg
        plt.savefig(f'{usb}/corpora/{name}/etiquetat/svg/autors/{autor}/distancia_iambe.svg')
        plt.close()


def index_binarietat(data, name):
    """Una funció per a calcular l'índex de binarietat de cada autor i fer-ne un gràfic."""
    sillabes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    df = data.groupby('autor')[sillabes].mean() * 100

    # Model de binarietat ideal
    ideal = np.array([0, 100, 0, 100, 0, 100, 0, 100, 0, 100])

    # Funció per calcular la distància euclidiana
    def calc_bin_index(author_values):
        author_values = np.array(author_values)
        return np.sqrt(np.sum((author_values - ideal) ** 2))

    # Afegir el Model al DataFrame
    model = [0, 100, 0, 100, 0, 100, 0, 100, 0, 100]
    df.loc['Iàmbic'] = model

    # Aplicar la funció a cada fila del DataFrame
    df['binarietat'] = df.apply(calc_bin_index, axis=1)

    # Normalitzar els valors de binarietat
    min_bin = df['binarietat'].min()
    max_bin = df['binarietat'].max()

    df['binarietat_normalitzada'] = (df['binarietat'] - min_bin) / (max_bin - min_bin) * 100

    # Invertir l'índex de binarietat normalitzada
    df['binarietat_invertida'] = 100 - df['binarietat_normalitzada']

    # Desar el DataFrame en un fitxer xlsx
    df.to_excel(f'{usb}/corpora/{name}/etiquetat/xlsx/index_binarietat.xlsx')

    # Ordenar el DataFrame per l'índex de binarietat invertida
    df = df.sort_values('binarietat_invertida')

    # Dibuixar un gràfic de barres amb l'índex de binarietat per autor
    plt.figure(figsize=(8, 4))
    plt.bar(df.index, df['binarietat_invertida'], color='skyblue')
    # Afegeix el valor de la mitjana de binarietat al gràfic de barres
    plt.axhline(df['binarietat_invertida'].mean(), color='red', linestyle='dashed',
                label=f'Mitjana ({df["binarietat_invertida"].mean():.2f})')
    plt.legend()
    plt.xticks(rotation=90)
    plt.grid(False)
    plt.tight_layout()
    # Desa el gràfic en svg
    plt.savefig(f'{usb}/corpora/{name}/etiquetat/svg/index_binarietat.svg')
    plt.close()


def dendrograma(data, name):
    """Fes un dendrograma de semblança dels contorns rítmics dels autors."""
    sillabes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    df = data.groupby('autor')[sillabes].mean() * 100

    # Calcula la distància euclidiana entre els autors
    dist = pdist(df, metric='euclidean')
    dist = squareform(dist)
    Z = linkage(dist, 'ward')

    # Dibuixa el dendrograma
    plt.figure(figsize=(10, 5))
    dendrogram(Z,
               orientation='top',
               labels=df.index,
               leaf_rotation=90,
               distance_sort='descending',
               show_leaf_counts=True)

    # Personalitzar el gràfic: eliminar el marc i només mostrar l'eix Y
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(False)
    ax.get_xaxis().set_visible(True)

    plt.tight_layout()
    # Desa el gràfic en svg
    plt.savefig(f'{usb}/corpora/{name}/etiquetat/svg/dendrograma.svg')
    plt.close()

    # Desa les dades del dendrograma en un fitxer xlsx
    pd.DataFrame(Z).to_excel(f'{usb}/corpora/{name}/etiquetat/xlsx/dendrograma.xlsx')


def dendrograma_lang(data, name):
    """Un dendrograma que considera dades d'altres tradicions poètiques."""
    sillabes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    df = data.groupby('autor')[sillabes].mean() * 100

    # Afegeix altres llengües
    df.loc['Carpasso (ITA)'] = [50, 40, 30, 70, 10, 75, 20, 75, 5, 100]
    df.loc['Tansillo (ITA)'] = [30, 40, 25, 65, 5, 75, 20, 75, 3, 100]
    df.loc['Petrarca (ITA)'] = [30, 40, 27, 65, 2, 65, 18, 60, 2, 100]

    df.loc['De La Torre (CAST)'] = [40, 35, 35, 60, 3, 75, 5, 45, 3, 100]
    df.loc['Garcilaso (CAST)'] = [40, 57, 28, 60, 2, 77, 10, 56, 2, 100]
    # Calcula la distància euclidiana entre els autors
    dist = pdist(df, metric='euclidean')
    dist = squareform(dist)
    Z = linkage(dist, 'ward')

    # Dibuixa el dendrograma
    plt.figure(figsize=(10, 5))
    dendrogram(Z,
               orientation='top',
               labels=df.index,
               leaf_rotation=90,
               distance_sort='descending',
               show_leaf_counts=True)

    # Personalitzar el gràfic: eliminar el marc i només mostrar l'eix Y
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(False)
    ax.get_xaxis().set_visible(True)

    plt.tight_layout()
    # Desa el gràfic en svg
    plt.savefig(f'{usb}/corpora/{name}/etiquetat/svg/dendrograma_lang.svg')
    plt.close()

    # Desa les dades del dendrograma en un fitxer xlsx
    pd.DataFrame(Z).to_excel(f'{usb}/corpora/{name}/etiquetat/xlsx/dendrograma_lang.xlsx')


def mitjana(data, name):
    """Calcula la mitjana de cada síl·laba del contorn accentual per al conjunt d'autors"""
    sillabes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    df = data.groupby('autor')[sillabes].mean() * 100
    mean = df.mean()
    dst = df.std()

    plt.plot(range(1, 11), mean, marker='o', linestyle='-', color='blue')
    if name != '__test':
        plt.errorbar(range(1, 11), mean, yerr=dst, fmt='o', color='black', capsize=5)
    # Afegeix els valors de std als caps superiors
    for i, txt in enumerate(dst):
        plt.annotate(f'{dst[i]:.2f}', (i + 1, mean[i] + dst[i] + 1), ha='center', va='bottom')
    plt.xticks(np.arange(0, 11))
    plt.grid(False)
    plt.tight_layout()
    # Desa el gràfic en svg
    plt.savefig(f'{usb}/corpora/{name}/etiquetat/svg/mitjana.svg')
    plt.close()


def cmap_accents(data, name):
    """Una funció per fer un mapa de colors amb les freqüències de tonicitat de les síl·labes 1-9 de cada autor"""
    sillabes = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    df = data.groupby('autor')[sillabes].mean() * 100

    plt.figure(figsize=(8, 8))
    # L'eix X és el nombre de síl·labes i l'eix Y cada autor
    plt.figure(figsize=(8, 8))
    plt.imshow(df, cmap='Blues', aspect='auto')

    plt.yticks(range(len(df.index)), df.index)
    plt.xticks(range(len(df.columns)), df.columns)

    # Afegeix el valor de cada cel·la
    for i in range(len(df.index)):
        for j in range(len(df.columns)):
            # Si el color de la cel·la és clar, fes el text negre, sinó blanc
            color = 'black' if df.iloc[i, j] < 50 else 'white'
            plt.text(j, i, f'{df.iloc[i, j]:.2f}', ha='center', va='center', color=color)
    plt.colorbar(label='Freqüència (%)')
    plt.tight_layout()

    # Desa el gràfic svg
    plt.savefig(f'{usb}/corpora/{name}/etiquetat/svg/cmap_accents.svg')
    plt.close()

    # Desa les dades en un full de càlcul
    df.to_excel(f'{usb}/corpora/{name}/etiquetat/xlsx/cmap_accents.xlsx')


def cmap_subdivisions(data, name):
    """Fes un cmap amb les subdivisions usades pels autors"""
    df = data.groupby('autor')['subdivisió'].value_counts(normalize=True).unstack().fillna(
        0) * 100
    plt.figure(figsize=(8, 8))
    plt.imshow(df, cmap='Blues', aspect='auto')

    plt.yticks(range(len(df.index)), df.index)
    plt.xticks(range(len(df.columns)), df.columns)
    # Afegeix el valor de cada cel·la
    for i in range(len(df.index)):
        for j in range(len(df.columns)):
            color = 'black' if df.iloc[i, j] < 50 else 'white'
            plt.text(j, i, f'{df.iloc[i, j]:.2f}', ha='center', va='center', color=color)
    plt.colorbar(label='Freqüència (%)')
    plt.tight_layout()
    plt.savefig(f'{usb}/corpora/{name}/etiquetat/svg/cmap_subdivisions.svg')
    plt.close()

    # Desa les dades en un full de càlcul
    df.to_excel(f'{usb}/corpora/{name}/etiquetat/xlsx/cmap_subdivisions.xlsx')


def print_desctiptives(data_set, name):
    """Un mòdul per mostrar informacions descriptives de les dades"""
    # 1. Imprimeix en un df el nombre d'autors de les dades, amb el nombre de versos i síl·labes per a cada autor
    # El df ha de tenir les columnes= ['Autor', 'Versos', 'Síl·labes']
    print("--" * 20, "Nombre d'autors", "--" * 20)
    versos = data_set.groupby('autor')['1'].count()
    silabes = data_set.groupby('autor')['síl·labes mètriques'].sum()
    silabes_extra = data_set.groupby('autor')['síl·labes extramètriques'].sum()
    silabes = silabes + silabes_extra
    df = pd.DataFrame({'Versos': versos, 'Síl·labes': silabes})
    # Compta quants de llibres hi ha per autor
    df['Llibres'] = data_set.groupby('autor')['obra'].nunique()
    # Compta quants de poemes hi ha per autor
    df['Poemes'] = data_set.groupby('autor')['poema'].nunique()
    # Afegeix el valor total del corpus
    df.loc['Total'] = df.sum()
    df = df.reset_index()
    df = df.rename(columns={'index': 'Autor'})

    print(tabulate(df, headers='keys', tablefmt='fancy_grid'))
    print("--" * 40)
    # Desa les dades en un full de càlcul
    df.to_excel(f'{usb}/corpora/{name}/etiquetat/xlsx/descriptives.xlsx')


def descriu(corpus, filtre=None):
    data = read_csv(f'{usb}/corpora/{corpus}/etiquetat/{corpus}.csv')
    if filtre:
        data = aplica_filtre(data, filtre)
    print_desctiptives(data, corpus)


if __name__ == '__main__':
    root = fr"{usb}/corpora/"
    print("--" * 40)
    print("Corpus disponibles:")
    for corpus_folder in os.listdir(root):
        print(f"\t• {corpus_folder}")
    print("--" * 40)
    enter = input("Quin corpus voleu explorar?\t")
    if enter != "":
        analitza_corpus(enter)
    else:
        for corpus in os.listdir(root):
            analitza_corpus(corpus)
