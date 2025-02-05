import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.stats import ttest_ind, pearsonr

import seaborn as sns
import scipy.cluster.hierarchy as sch

cols_to_sum = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']


def llegir_dades(path):
    fitxers_csv = [fitxer for fitxer in os.listdir(path) if fitxer.endswith('.csv')]
    dfs = []
    for fitxer in fitxers_csv:
        try:
            df = pd.read_csv(path + fitxer, delimiter=';', encoding='utf-8')
            dfs.append(df)
        except pd.errors.ParserError:
            print(f"Error en llegir el fitxer {fitxer}. Es passarà a l'arxiu següent.")

    return pd.concat(dfs)


def prepara_dades(dades):
    # Seleccionar només les columnes "1"-"9"
    # cols_to_sum = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

    # Modifica els valors de les cols_to_sum si l'integer és major que 1 per 1 i si no per 0:
    dades_totals[cols_to_sum] = dades_totals[cols_to_sum].applymap(
        lambda x: 1 if x > 1 else 0)  # 1 si és major que 1, 0 si no ho és

    return dades_totals


def plot_stress(dades):
    """Una funció per fer un gràfic amb les freqüències de tonicitat de les síl·labes 1-9 per a cada autor"""
    total_values_per_column = dades_totals.groupby('autor')[cols_to_sum].count()
    tonicitat_per_column = dades_totals.groupby('autor')[cols_to_sum].sum()
    frequencia_tonicitat_per_column = tonicitat_per_column.div(total_values_per_column) * 100

    plt.figure(figsize=(8, 6))
    # Mostra tots els valors de l'1 al 10 a l'eix X
    x_values = range(1, 11)
    plt.xticks(np.arange(0, 11))
    colors = plt.cm.tab10.colors[:len(frequencia_tonicitat_per_column)]  # Agafa tants colors com autors
    for i, (author, percent) in enumerate(frequencia_tonicitat_per_column.iterrows()):
        plt.plot(x_values, percent, label=author,
                 color=colors[i % len(colors)])  # Utilitza % per repetir colors si n'hi ha menys que autors

    plt.legend(title='Autors', bbox_to_anchor=(0.5, -0.2), loc='upper center', ncol=5)
    plt.grid(False)
    plt.tight_layout()
    plt.savefig('graphics/stress.png', dpi=600, bbox_inches='tight')

    # Desa les dades en un full de càlcul
    frequencia_tonicitat_per_column.to_excel('xlsx/stress_01.xlsx')


def plot_one_author(dades, autor):
    """Mostra un gràfic amb el contorn rítmic d'un sol autor"""
    total_values_per_column = dades.groupby('autor')[cols_to_sum].count()
    tonicitat_per_column = dades.groupby('autor')[cols_to_sum].sum()
    frequencia_tonicitat_per_column = tonicitat_per_column.div(total_values_per_column) * 100

    autor_d = frequencia_tonicitat_per_column.loc[autor]

    mean = autor_d.mean()
    std = autor_d.std()

    plt.figure(figsize=(8, 6))
    x_values = range(1, 11)  # Valors per a l'eix X
    plt.xticks(np.arange(0, 11))
    plt.plot(x_values, mean, marker='o', color='skyblue')
    plt.errorbar(x_values, mean, yerr=std, fmt='o', color='grey', capsize=5)
    # Afegeix les etiquetes amb el valor de std:
    for x, y, s in zip(x_values, mean, std):
        plt.text(x, y + s, f'{s:.2f}', ha='center', va='bottom', color='black')

    plt.grid(False)
    plt.tight_layout()
    plt.savefig('graphics/one_author_stress.png', dpi=600, bbox_inches='tight')
    print(f'Gràfic de l\'accentuació de l\'autor {autor} creat correctament.')


def mean_stress(dades):
    """Una funció per fer un gràfic que contengui la mitjana dels valors d'accentuació de cada síl·laba 1-10 i la seva desviació estàndard en un scatter plot"""
    total_values_per_column = dades.groupby('autor')[cols_to_sum].count()
    tonicitat_per_column = dades.groupby('autor')[cols_to_sum].sum()
    frequencia_tonicitat_per_column = tonicitat_per_column.div(total_values_per_column) * 100

    # Calcula la mitjana i la desviació estàndard de les freqüències de tonicitat de les síl·labes 1-10 de tots els autors
    mean = frequencia_tonicitat_per_column.mean()
    std = frequencia_tonicitat_per_column.std()

    plt.figure(figsize=(8, 6))
    x_values = range(1, 11)  # Valors per a l'eix X
    plt.xticks(np.arange(0, 11))
    plt.plot(x_values, mean, marker='o', color='blue')
    plt.errorbar(x_values, mean, yerr=std, fmt='o', color='grey', capsize=5)
    # Afegeix les etiquetes amb el valor de std:
    for x, y, s in zip(x_values, mean, std):
        plt.text(x, y + s, f'{s:.2f}', ha='center', va='bottom', color='black')

    plt.grid(False)
    plt.tight_layout()
    plt.savefig('graphics/mean_stress.png', dpi=600, bbox_inches='tight')
    print('Gràfic de la mitjana de l\'accentuació de les síl·labes 1-10 creat correctament.')

    # Ara mostra la distància entre la mitjana i el model
    model = [0, 100, 0, 100, 0, 100, 0, 100, 0, 100]
    distance = [abs(d - m) for d, m in zip(mean, model)]
    plt.figure(figsize=(8, 6))
    x_values = range(1, 11)  # Valors per a l'eix X
    plt.xticks(np.arange(0, 11))
    plt.plot(x_values, distance, marker='o', color='blue')
    plt.plot(x_values, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], label='Iàmbic', color='grey', marker='o')
    plt.grid(False)
    plt.tight_layout()
    plt.savefig('graphics/mean_stress_distance.png', dpi=600, bbox_inches='tight')

    return mean, std


def compare_authors_set(dades, set, title):
    """Compara un conjunt d'autors"""
    total_values_per_column = dades.groupby('autor')[cols_to_sum].count()
    tonicitat_per_column = dades.groupby('autor')[cols_to_sum].sum()
    frequencia_tonicitat_per_column = tonicitat_per_column.div(total_values_per_column) * 100

    set_authors = frequencia_tonicitat_per_column.loc[set]

    plt.figure(figsize=(8, 6))
    x_values = range(1, 11)  # Valors per a l'eix X
    plt.xticks(np.arange(0, 11))
    colors = plt.cm.tab10.colors[:len(set_authors)]  # Agafa tants colors com autors
    for i, (author, percent) in enumerate(set_authors.iterrows()):
        plt.plot(x_values, percent, label=author,
                 color=colors[i % len(colors)], alpha=0.3)

    mean = set_authors.mean()
    std = set_authors.std()
    plt.plot(x_values, mean, marker='o', color='black')
    plt.errorbar(x_values, mean, yerr=std, fmt='o', color='black', capsize=5)
    # Afegeix les etiquetes amb el valor de std:
    for x, y, s in zip(x_values, mean, std):
        plt.text(x, y + s, f'{s:.2f}', ha='center', va='bottom', color='black')

    plt.legend(title='Autors', bbox_to_anchor=(0.5, -0.2), loc='upper center', ncol=5)
    plt.grid(False)
    plt.tight_layout()
    plt.savefig(f'graphics/compare_stress_set_{title}.png', dpi=600, bbox_inches='tight')

    plt.close()

    # Compara la mitjana dels autors del conjunt amb la mitjana global de tots els autors menys els del conjunt
    mean_glob = frequencia_tonicitat_per_column.mean()
    mean_set = set_authors.mean()
    std_set = set_authors.std()

    plt.figure(figsize=(8, 6))

    # Concatena els autors en una cadena (separada per coma  i el darrer valor per i).
    set_str = ', '.join(set_authors.index[:-1]) + ' i ' + set_authors.index[-1] if len(set_authors) > 1 else \
        set_authors.index[0]
    print("> " + set_str)
    plt.plot(x_values, mean_glob, label='Mitjana global', color='red')
    plt.plot(x_values, mean_set, label=f'Mitjana del conjunt {title}', color='green')
    plt.errorbar(x_values, mean_set, yerr=std_set, fmt='o', color='green', capsize=5)
    # Afegeix els valors de std al gràfic
    # Omple l'espai entre les mitjanes del conjunt i la mitjana global
    plt.fill_between(x_values, mean_glob, mean_set, color='skyblue', alpha=0.4)
    # Mostra la distància entre els punts dels autors
    distance = [d - m for d, m in zip(mean_set, mean_glob)]
    for x, y, s, z in zip(x_values, mean_set, std_set, distance):
        plt.text(x, y + s + 2.5, f'std={s:.2f}', ha='center', va='bottom', color='green', bbox=dict(facecolor='white'))
        plt.text(x, y + s + 9, f'd={z:.2f}', ha='center', va='bottom', color='blue', bbox=dict(facecolor='white'))

    # Anàlisi exploratòria de les dades: Test de t de Student
    ttest = ttest_ind(set_authors, frequencia_tonicitat_per_column.drop(set), axis=0)

    plt.xticks(np.arange(0, 11))

    # Afegeix a la llegenda el valor de t de Student
    plt.plot([], [], ' ', label=f'd= distància entre els valors', color='blue')
    plt.plot([], [], ' ', label=f'std= desviació estàndard', color='green')
    plt.plot([], [], ' ', label=f'p= valor-p')
    # Afegeix els valors de p de t de Student al gràfic davall la llegenda per a cada síl·laba
    for x, p in zip(x_values, ttest.pvalue):
        if p < 0.01:
            p = 'p<0.01'
        else:
            p = f'p={p:.2f}'
        plt.text(x, 2, p, ha='center', va='bottom', color='black')

    plt.legend()
    plt.tight_layout()
    plt.savefig(f'graphics/compare_stress_set_mean_{title}.png', dpi=600, bbox_inches='tight')

    # Desa les dades en un full de càlcul
    pd.DataFrame({'Mitjana global': mean_glob, f'Mitjana del conjunt {title}': mean_set}).to_excel(
        f'xlsx/compare_stress_set_mean_{title}.xlsx')
    plt.close()
    print('Gràfic de la comparació de la mitjana de l\'accentuació de les síl·labes 1-10 creat correctament.')
    return mean_set, std_set


def compare_authors(dades, author_1, author_2):
    """Una funció per comparar els contorns rímtics de dos autors"""
    total_values_per_column = dades.groupby('autor')[cols_to_sum].count()
    tonicitat_per_column = dades.groupby('autor')[cols_to_sum].sum()
    frequencia_tonicitat_per_column = tonicitat_per_column.div(total_values_per_column) * 100

    author_1_d = frequencia_tonicitat_per_column.loc[author_1]
    author_2_d = frequencia_tonicitat_per_column.loc[author_2]

    plt.figure(figsize=(8, 6))
    x_values = range(1, 11)  # Valors per a l'eix X
    plt.xticks(np.arange(0, 11))
    plt.plot(x_values, author_1_d, label=author_1, color='red')
    plt.plot(x_values, author_2_d, label=author_2, color='green')
    plt.fill_between(x_values, author_1_d, author_2_d, color='skyblue', alpha=0.4)
    # Mostra la distància entre els punts dels autors
    for x, y1, y2 in zip(x_values, author_1_d, author_2_d):
        plt.text(x, (y1 + y2) / 2, f'{abs(y1 - y2):.2f}', ha='center', va='top', color='black')

    plt.legend(title='Autors', bbox_to_anchor=(0.5, -0.2), loc='upper center', ncol=5)
    plt.grid(False)
    plt.tight_layout()
    plt.savefig('graphics/compare_stress.png', dpi=600, bbox_inches='tight')


def deviance_from_iambic(dades):
    """Una funció per calcular la desviació de cada autor respecte del model binari pur"""

    # Agrupar les dades per autor i calcular la mitjana de les columnes seleccionades
    grouped_data = dades.groupby('autor')[cols_to_sum].mean()

    # Calcular la desviació de cada autor respecte del model binari pur
    model = [0, 100, 0, 100, 0, 100, 0, 100, 0, 100]
    absolute_deviations = {author: [abs(d - m) for d, m in zip(values, model)] for author, values in
                           grouped_data.iterrows()}

    # Fes un plot amb les dades
    plt.figure(figsize=(8, 6))
    x_values = range(1, 11)  # Valors per a l'eix X
    plt.xticks(np.arange(0, 11))
    for author, deviation in absolute_deviations.items():
        plt.plot(x_values, deviation, label=author, color='black')
        plt.plot(x_values, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], label='Model binari pur', color='gray')
        plt.fill_between(x_values, deviation, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], color='skyblue', alpha=0.4)

    # Mostra 50 d'Y
    plt.axhline(y=50, color='gray', alpha=0.2)

    plt.legend(title='Autors', bbox_to_anchor=(0.5, -0.2), loc='upper center', ncol=5)
    plt.grid(False)
    plt.tight_layout()
    plt.savefig('graphics/deviance_stress.png', dpi=600, bbox_inches='tight')

    # Calcula el valor de desiviació total per a cada autor
    total_deviation = {key: sum(values) / 9 for key, values in absolute_deviations.items()}

    # Afegeix-ho a les dades amb el títol 'Distància total'
    dev_t = pd.DataFrame(total_deviation, index=['Distància total'])
    absolute_deviations = pd.concat([pd.DataFrame(absolute_deviations), dev_t])

    # Desa les dades en un full de càlcul
    absolute_deviations.T.to_excel('xlsx/deviance_stress.xlsx')


def deviance_from_iambic_set_of_autors(dades, authors):
    """Una funció per calcular la desviació d'uns autors respecte del model binari pur"""
    total_values_per_column = dades.groupby('autor')[cols_to_sum].count()
    tonicitat_per_column = dades.groupby('autor')[cols_to_sum].sum()
    frequencia_tonicitat_per_column = tonicitat_per_column.div(total_values_per_column) * 100
    set_authors = frequencia_tonicitat_per_column.loc[authors]

    model = [0, 100, 0, 100, 0, 100, 0, 100, 0, 100]

    deviation_from_model = {author: [abs(d - m) for d, m in zip(values, model)] for author, values in
                            set_authors.iterrows()}

    # Fes un plot amb subplots per a cada autor i disposa'ls en una matriu de quatre columnes
    # Seguint el dibuix:
    # [1] [2] [3] [4]
    # [5] [6] [7] [8]
    # [9] [10] [11] [12]

    # Calcula la distribució òptima a partir del total d'autors:
    n_rows = len(authors) // 4 + 1

    fig, axs = plt.subplots(n_rows, 4, figsize=(15, 15))
    axs = axs.flatten()

    for i, (author, deviation) in enumerate(deviation_from_model.items()):
        x_values = range(1, 11)
        plt.xticks(np.arange(0, 11))
        axs[i].plot(x_values, deviation, label=author, color='black')
        axs[i].plot(x_values, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], label='Model binari pur', color='gray')
        axs[i].fill_between(x_values, deviation, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], color='skyblue', alpha=0.4)
        # Mostra la desviació absoluta entre els punts de l'autor i el model
        axs[i].set_title(author)
        axs[i].set_xlabel('Síl·labes')
        axs[i].set_ylabel('Distància')

        axs[i].grid(False)

        # Afegeix el valor de la desviació total de cada autor al gràfic en el format 'DT= x' devora el títol del gràfic alineat a la dreta
        axs[i].text(0.95, 0.95, f'DT={sum(deviation) / 9:.2f}', ha='right', va='top', transform=axs[i].transAxes)

    # Elimina els subplots que no s'han utilitzat
    for i in range(len(authors), len(axs)):
        fig.delaxes(axs[i])

    plt.tight_layout()
    plt.savefig('graphics/deviance_stress_set_of_authors.png', dpi=600, bbox_inches='tight')

    # Calcula el valor de desviació total per a cada autor
    total_deviation = {key: sum(values) / 9 for key, values in deviation_from_model.items()}

    # Afegeix-ho a les dades amb el títol 'Distància total'
    deviation_from_model = pd.DataFrame(deviation_from_model).append(pd.Series(total_deviation, name='Distància total'))

    # Desa les dades en un full de càlcul
    deviation_from_model.T.to_excel('xlsx/deviance_stress_set_of_authors.xlsx')

    # Retorna la desviació total
    return total_deviation


def mean_deviation_from_iambic(dades):
    """Calcula i fes un gràfic de la desviació mitjana del valor te tonicitat de les síl·labes de tots els autors respecte del model"""

    # Obté la mitjana de les freqüències de tonicitat de les síl·labes 1-9 de tots els autors
    total_values_per_column = dades.groupby('autor')[cols_to_sum].count()
    tonicitat_per_column = dades.groupby('autor')[cols_to_sum].sum()
    mitjana = tonicitat_per_column.div(total_values_per_column) * 100
    mitjana_total = mitjana.mean()

    # Calcula la desviació de la mitjana respecte del model binari pur
    model = [0, 100, 0, 100, 0, 100, 0, 100, 0, 100]
    desviacio = [abs(d - m) for d, m in zip(mitjana_total, model)]

    plt.figure(figsize=(8, 6))
    x_values = range(1, 11)  # Valors per a l'eix X
    plt.xticks(np.arange(0, 11))
    plt.plot(x_values, desviacio, marker='o', color='black')
    plt.plot(x_values, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], label='Model binari pur', color='gray')
    plt.fill_between(x_values, desviacio, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], color='skyblue', alpha=0.4)
    # Mostra la desviació absoluta entre els punts de l'autor i el model
    for x, y1, y2 in zip(x_values, desviacio, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]):
        plt.text(x, (y1 + y2) / 2, f'{abs(y1 - y2):.2f}', ha='center', va='top', color='black')

    plt.grid(False)
    plt.tight_layout()

    plt.savefig('graphics/mean_deviance_stress.png', dpi=600, bbox_inches='tight')


def deviance_from_iambic_epoch(dades):
    """"Una funció que agrupa els autors per època i calcula la desviació de cada autor del grup respecte del model."""

    # Defineix les èpoques com a períodes de temps (anys) compresos entre dos valors
    epochs = [(1301, 1400), (1401, 1450), (1451, 1500), (1501, 1600), (1601, 1700)]

    # Agrupa els autors per època
    epochs_authors = {}
    for epoch in epochs:
        any = dades['any'] + 25
        epochs_authors[epoch] = dades[any.between(epoch[0], epoch[1])]['autor'].unique()

    # Per a cada època aconsegueix fer un gràfic amb els autors d'aquesta època i el càlcul de la desviació de cada valor 1-9 de cada autor respecte el model binari pur sense recórrer a funcions externes
    # El gràfic ha de ser només un i ha de contenir tants subplots com èpoques hi hagi. En cada subplot hi ha d'haver els autors de l'època amb la seva desviació respecte el model binari pur
    # Els subplots han de ser disposats en una matriu de 2 columnes i 2 files

    # Crea una matriu de subplots amb 3 columnes i 2 files
    fig, axs = plt.subplots(2, 3, figsize=(30, 15))
    axs = axs.flatten()

    # Per a cada època crea un subplot amb la desviació de cada autor (identificat amb un color diferent) respecte del model binari pur i inclou una llegenda amb els autors
    for i, (epoch, authors) in enumerate(epochs_authors.items()):
        total_values_per_column = dades.groupby('autor')[cols_to_sum].count()
        tonicitat_per_column = dades.groupby('autor')[cols_to_sum].sum()
        frequencia_tonicitat_per_column = tonicitat_per_column.div(total_values_per_column) * 100
        set_authors = frequencia_tonicitat_per_column.loc[authors]

        model = [0, 100, 0, 100, 0, 100, 0, 100, 0, 100]

        deviation_from_model = {author: [abs(d - m) for d, m in zip(values, model)] for author, values in
                                set_authors.iterrows()}

        # Elimina els autors repetits
        deviation_from_model = {author: values for author, values in deviation_from_model.items() if author in authors}
        # Impriu els autors que s'han eliminat
        if len(deviation_from_model) < len(authors):
            print(f'Eliminats els autors {set(authors) - set(deviation_from_model.keys())}')

        x_values = range(1, 11)
        plt.xticks(np.arange(0, 11))
        cmap = dict(zip(deviation_from_model.keys(), sns.color_palette('hls', n_colors=len(deviation_from_model))))

        for author, deviation in deviation_from_model.items():
            axs[i].plot(x_values, deviation, label=author, color=cmap[author], linestyle='dashed', marker='o')
            # axs[i].fill_between(x_values, deviation, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], color='skyblue', alpha=0.4)
            axs[i].set_title(f'{epoch[0]}-{epoch[1]}')
            # axs[i].set_xlabel('Síl·labes')
            # axs[i].set_ylabel('Distància')
            # Valor 50 de Y
            axs[i].axhline(y=50, color='gray', alpha=0.2)
            axs[i].grid(False)
        # Inclou el model binari pur al gràfic
        axs[i].plot(x_values, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], label='Model binari pur', color='gray',
                    linestyle='dashed', marker='o')
        # Inclou la llegenda del subplot
        # axs[i].legend(title='Autors', loc='center left', bbox_to_anchor=(1, 0.5))
        axs[i].legend()

    # Elimina els subplots que no s'han utilitzat
    for i in range(len(epochs_authors), len(axs)):
        fig.delaxes(axs[i])

    plt.tight_layout()
    plt.savefig('graphics/deviance_stress_epoch.png', dpi=600, bbox_inches='tight')

    # Ara farem un únic gràfic per comparar els valors mitjans de les síL·labes 1-9 de cada època amb el model binari pur
    # Per a cada època, calcula la mitjana de les freqüències de tonicitat de les síl·labes 1-9 de tots els autors
    total_values_per_column = dades.groupby('autor')[cols_to_sum].count()
    tonicitat_per_column = dades.groupby('autor')[cols_to_sum].sum()
    frequencia_tonicitat_per_column = tonicitat_per_column.div(total_values_per_column) * 100

    # Crea un diccionari amb les mitjanes de cada època
    epochs_means = {epoch: frequencia_tonicitat_per_column.loc[authors].mean() for epoch, authors in
                    epochs_authors.items()}

    # Calcula la desviació de la mitjana respecte del model binari pur per a cada època
    model = [0, 100, 0, 100, 0, 100, 0, 100, 0, 100]
    epochs_deviations = {epoch: [abs(d - m) for d, m in zip(mean, model)] for epoch, mean in epochs_means.items()}

    # Dibuixa un gràfic amb les desviacions de cada època respecte del model binari pur
    plt.figure(figsize=(8, 6))
    x_values = range(1, 11)  # Valors per a l'eix X
    plt.xticks(np.arange(0, 11))
    for epoch, deviation in epochs_deviations.items():
        plt.plot(x_values, deviation, label=f'{epoch[0]}-{epoch[1]}', linestyle='dashed', marker='o')

    # Afegeix el model binari pur al gràfic
    plt.plot(x_values, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], label='Model binari pur', color='gray', linestyle='dashed',
             marker='o')

    # Valor 50 de Y
    plt.axhline(y=50, color='gray', alpha=0.2)

    # Afegeix el valor de la mitjana de desviació de tots els autors al gràfic
    total_values_per_column = dades.groupby('autor')[cols_to_sum].count()
    tonicitat_per_column = dades.groupby('autor')[cols_to_sum].sum()
    mitjana = tonicitat_per_column.div(total_values_per_column) * 100
    mitjana_total = mitjana.mean()

    # Calcula la desviació de la mitjana respecte del model binari pur
    model = [0, 100, 0, 100, 0, 100, 0, 100, 0, 100]
    desviacio = [abs(d - m) for d, m in zip(mitjana_total, model)]

    plt.plot(x_values, desviacio, label='Mitjana', color='red', linestyle='dashed', marker='x')

    # Afegeix el valor de la Mitjana a les dades
    epochs_deviations[('Mitjana', '')] = desviacio

    # plt.legend(title='Període', bbox_to_anchor=(0.5, -0.2), loc='upper center', ncol=5)
    plt.legend()
    plt.grid(False)
    plt.tight_layout()
    plt.savefig('graphics/mean_deviance_stress_epoch.png', dpi=600, bbox_inches='tight')

    # Desa les dades en un full de càlcul
    pd.DataFrame(epochs_deviations).T.to_excel('xlsx/mean_deviance_stress_epoch.xlsx')


def mean_stress_epoch(dades, mean):
    """Aquesta funció genera un gràfic amb les mitjanes de tonicitat de les síl·labes 1-9 de cada època"""
    # Primer genera un gràfic amb els subplots per a cada època amb els seus autors
    # Defineix les èpoques com a períodes de temps (anys) compresos entre dos valors
    epochs = [(1301, 1400), (1401, 1450), (1451, 1500), (1501, 1600), (1601, 1700)]

    # Agrupa els autors per època
    epochs_authors = {}
    for epoch in epochs:
        any = dades['any'] + 25
        epochs_authors[epoch] = dades[any.between(epoch[0], epoch[1])]['autor'].unique()

    # Crea una matriu de subplots amb 2 columnes i 2 files
    fig, axs = plt.subplots(2, 3, figsize=(30, 15))
    axs = axs.flatten()

    # Per a cada època crea un subplot i mostra-hi els valors de la freqüència de tonicitat de les síl·labes 1-9 de cada autor
    for i, (epoch, authors) in enumerate(epochs_authors.items()):
        total_values_per_column = dades.groupby('autor')[cols_to_sum].count()
        tonicitat_per_column = dades.groupby('autor')[cols_to_sum].sum()
        frequencia_tonicitat_per_column = tonicitat_per_column.div(total_values_per_column) * 100
        set_authors = frequencia_tonicitat_per_column.loc[authors]

        x_values = range(1, 11)
        plt.xticks(np.arange(0, 11))
        cmap = dict(zip(set_authors.index, sns.color_palette('hls', n_colors=len(set_authors))))

        for author, values in set_authors.iterrows():
            axs[i].plot(x_values, values, label=author, color=cmap[author])
            axs[i].plot(x_values, mean, label='Mitjana', linestyle='dashed', color='gray')
            axs[i].set_title(f'{epoch[0]}-{epoch[1]}')
            axs[i].set_xlabel('Síl·labes')
            axs[i].set_ylabel('Freq.')

            axs[i].grid(False)
        # Inclou la llegenda del subplot
        axs[i].legend(title='Autors', loc='center left', bbox_to_anchor=(1, 0.5))

    # Elimina els subplots que no s'han utilitzat
    for i in range(len(epochs_authors), len(axs)):
        fig.delaxes(axs[i])

    plt.tight_layout()
    plt.savefig('graphics/stress_epoch.png', dpi=600, bbox_inches='tight')

    # Ara farem un únic gràfic per comparar els valors mitjans de les síL·labes 1-9 de cada època
    # Per a cada època, calcula la mitjana de les freqüències de tonicitat de les síl·labes 1-9 de tots els autors
    total_values_per_column = dades.groupby('autor')[cols_to_sum].count()
    tonicitat_per_column = dades.groupby('autor')[cols_to_sum].sum()
    frequencia_tonicitat_per_column = tonicitat_per_column.div(total_values_per_column) * 100

    # Crea un diccionari amb les mitjanes de cada època
    epochs_means = {epoch: frequencia_tonicitat_per_column.loc[authors].mean() for epoch, authors in
                    epochs_authors.items()}

    # Dibuixa un gràfic amb les mitjanes de cada època
    plt.figure(figsize=(8, 6))
    x_values = range(1, 11)  # Valors per a l'eix X
    plt.xticks(np.arange(0, 11))
    for epoch, mean in epochs_means.items():
        plt.plot(x_values, mean, label=f'{epoch[0]}-{epoch[1]}', marker='o')

    plt.legend(title='Període', bbox_to_anchor=(0.5, -0.2), loc='upper center', ncol=5)

    plt.grid(False)
    plt.tight_layout()
    plt.savefig('graphics/mean_stress_epoch.png', dpi=600, bbox_inches='tight')


def epochs_mean_and_one_author(dades, autor_name):
    # Agrupa els autors per època
    epochs = [(1301, 1400), (1401, 1450), (1451, 1500), (1501, 1600), (1601, 1700)]
    epochs_authors = {}
    for epoch in epochs:
        any = dades['any'] + 25
        epochs_authors[epoch] = dades[any.between(epoch[0], epoch[1])]['autor'].unique()

    df_or = dades.groupby('autor')[cols_to_sum].mean()

    # Elimina l'autor seleccionat
    df = df_or.drop(autor_name)
    epochs_authors = {epoch: [author for author in authors if author != autor_name] for epoch, authors in
                      epochs_authors.items()}

    # Crea un diccionari amb les mitjanes de cada època
    epochs_means = {epoch: df.loc[authors].mean() * 100 for epoch, authors in
                    epochs_authors.items()}

    # Dibuixa un gràfic amb les mitjanes de cada època
    plt.figure(figsize=(8, 6))
    x_values = range(1, 11)  # Valors per a l'eix X
    plt.xticks(np.arange(0, 11))
    for epoch, mean in epochs_means.items():
        plt.plot(x_values, mean, label=f'{epoch[0]}-{epoch[1]}', linestyle='dashed', marker='o', alpha=0.5)

    # Afegeix la mitjana de l'autor seleccionat
    autor = dades.groupby('autor')[cols_to_sum].mean().loc[autor_name]
    plt.plot(x_values, autor * 100, label=autor_name, color='red', linestyle='dashed', marker='o')
    plt.legend()
    plt.grid(False)
    plt.tight_layout()
    plt.savefig(f'graphics/mean_stress_epoch_{autor_name}.png', dpi=600, bbox_inches='tight')


def plot_subdivisions(dades):
    """Fes un cmap amb les subdivisions usades pels autors"""
    total_values_per_column = dades.groupby('autor')['subdivisió'].count()
    subdivisions_per_column = dades.groupby('autor')['subdivisió'].value_counts(normalize=True).unstack().fillna(
        0) * 100

    plt.figure(figsize=(8, 8))
    plt.imshow(subdivisions_per_column, cmap='viridis', aspect='auto')

    plt.yticks(range(len(subdivisions_per_column.index)), subdivisions_per_column.index)
    plt.xticks(range(len(subdivisions_per_column.columns)), subdivisions_per_column.columns)
    # Afegeix el valor de cada cel·la
    for i in range(len(subdivisions_per_column.index)):
        for j in range(len(subdivisions_per_column.columns)):
            plt.text(j, i, f'{subdivisions_per_column.iloc[i, j]:.2f}', ha='center', va='center', color='white')
    plt.colorbar(label='Freqüència (%)')
    plt.tight_layout()
    plt.savefig('graphics/cmap_subdivisions.png', dpi=600, bbox_inches='tight')

    # Desa els valors a un full de càlcul
    subdivisions_per_column.to_excel('xlsx/subdivisions.xlsx')


def list_authors(dades):
    """Una funció per llistar els autors del corpus amb les següents informacions:
        - Nom de l'autor
        - Període de l'autor
        - Nombre de versos
        - Percentatge de versos dins el corpus
        - Percentatge de versos dins el període"""

    epochs = [(1301, 1400), (1401, 1450), (1451, 1500), (1501, 1600), (1601, 1700)]

    # Agrupa els autors per època
    epochs_authors = {}
    for epoch in epochs:
        any = dades['any'] + 25
        epochs_authors[epoch] = dades[any.between(epoch[0], epoch[1])]['autor'].unique()

    # Compta el nombre de versos per autor
    verses_per_author = dades['autor'].value_counts()

    # Compta el nombre total de versos
    total_verses = len(dades)

    # Compta el total de versos per cada època
    total_verses_per_epoch = {epoch: len(dades[dades['autor'].isin(authors)]) for epoch, authors in
                              epochs_authors.items()}

    # Compta el percentatge de versos de cada autor respecte el nombre total de versos
    verses_percentages = verses_per_author / total_verses * 100

    # Compta el percentatge de versos de cada autor respecte el nombre total de versos de la seva època
    verses_percentages_per_epoch = {author: verses / total_verses_per_epoch[epoch] * 100 for epoch, authors in
                                    epochs_authors.items() for author, verses in verses_per_author.items() if
                                    author in authors}

    # Crea un DataFrame amb les dades
    authors_data = pd.DataFrame({'Període': [f'{epoch[0]}-{epoch[1]}' for epoch in epochs for author in
                                             epochs_authors[epoch] if author in verses_per_author.index],
                                 'Autor': [author for epoch in epochs for author in epochs_authors[epoch] if
                                           author in verses_per_author.index],
                                 'Nombre de versos': [verses_per_author[author] for epoch in epochs for author in
                                                      epochs_authors[epoch] if author in verses_per_author.index],
                                 'Percentatge de versos': [verses_percentages[author] for epoch in epochs for author in
                                                           epochs_authors[epoch] if author in verses_per_author.index],
                                 'Percentatge de versos per període': [verses_percentages_per_epoch[author] for epoch in
                                                                       epochs for author in epochs_authors[epoch] if
                                                                       author in verses_per_author.index]})

    # Desa les dades en un full de càlcul en format de taula
    authors_data.to_excel('xlsx/authors_data.xlsx')

    # Fes dos plots que contenguin:
    # - Un gràfic de barres amb el percentatge de versos per autor respecte del total i del període
    # - Un gràfic de barres amb el percentatge de versos per període

    # Genera un gràfic de barres amb el percentatge de versos per autor respecte del total i del període
    # Afegeix al gràfic un gràfic sobreposat que representi la suma del percentatge de versos de cada època

    # Cal sumar els versos per període
    period_data = authors_data.groupby('Període')['Percentatge de versos'].sum().reset_index()
    period_data['Posició_inici'] = period_data['Període'].map(
        lambda p: authors_data[authors_data['Període'] == p]['Autor'].index.min())
    period_data['Posició_final'] = period_data['Període'].map(
        lambda p: authors_data[authors_data['Període'] == p]['Autor'].index.max())

    # Crear el gràfic
    plt.figure(figsize=(10, 6))

    # Dibuixar rectangles com a fons per representar les sumes per període
    for _, row in period_data.iterrows():
        plt.gca().add_patch(plt.Rectangle(
            (row['Posició_inici'] - 0.5, 0),  # Coordenades de la cantonada inferior esquerra
            row['Posició_final'] - row['Posició_inici'] + 1,  # Amplada del rectangle
            row['Percentatge de versos'],  # Alçada del rectangle
            color='lightgrey',
            alpha=0.4,
            zorder=0
        ))

    # Dibuixar el gràfic original
    sns.barplot(data=authors_data, x='Autor', y='Percentatge de versos', hue='Període', dodge=False, zorder=1)

    # Personalització

    plt.xticks(rotation=90)
    plt.grid(False)
    plt.tight_layout()
    plt.legend()

    # Guardar el gràfic
    plt.savefig('graphics/authors_data_with_totals_updated.png', dpi=600, bbox_inches='tight')

    # Gràfic de barres amb el percentatge de versos per període
    plt.figure(figsize=(8, 8))
    plt.bar(authors_data['Període'].unique(), authors_data.groupby('Període')['Percentatge de versos'].sum(),
            color='blue')

    plt.xticks(rotation=45)
    plt.grid(False)
    plt.tight_layout()
    plt.savefig('graphics/authors_data_per_epoch.png', dpi=600, bbox_inches='tight')


def quantify_centuries(dades):
    """Una funció per quantificar la distribució dels autors per segles"""
    epochs = [(1301, 1400), (1401, 1450), (1451, 1500), (1501, 1600), (1601, 1700)]

    # Agrupa els autors per època
    epochs_authors = {}
    for epoch in epochs:
        any = dades['any'] + 25
        epochs_authors[epoch] = dades[any.between(epoch[0], epoch[1])]['autor'].unique()

    # Compta el nombre d'autors per època
    epochs_counts = {f'{epoch[0]}-{epoch[1]}': len(authors) for epoch, authors in epochs_authors.items()}

    # Compta el percentatge d'autors de cada època
    total_authors = len(dades['autor'].unique())
    epochs_counts = {key: value / total_authors * 100 for key, value in epochs_counts.items()}
    print(epochs_counts)
    plt.figure(figsize=(8, 8))
    plt.bar(epochs_counts.keys(), epochs_counts.values(), color='blue')

    plt.xticks(rotation=45)
    plt.grid(False)
    plt.tight_layout()
    plt.savefig('graphics/centuries.png', dpi=600, bbox_inches='tight')


def cmap_stress(dades):
    """Una funció per fer un mapa de colors amb les freqüències de tonicitat de les síl·labes 1-9 de cada autor"""
    total_values_per_column = dades.groupby('autor')[cols_to_sum].count()
    tonicitat_per_column = dades.groupby('autor')[cols_to_sum].sum()
    frequencia_tonicitat_per_column = tonicitat_per_column.div(total_values_per_column) * 100

    plt.figure(figsize=(8, 8))
    # L'eix X serà el nombre de síl·labes i l'eix Y serà cada autor
    plt.imshow(frequencia_tonicitat_per_column, cmap='viridis', aspect='auto')

    plt.yticks(range(len(frequencia_tonicitat_per_column.index)), frequencia_tonicitat_per_column.index)
    plt.xticks(ticks=np.arange(10), labels=np.arange(1, 10 + 1))
    # Afegeix el valor de cada cel·la
    for i in range(len(frequencia_tonicitat_per_column.index)):
        for j in range(10):
            plt.text(j, i, f'{frequencia_tonicitat_per_column.iloc[i, j]:.2f}', ha='center', va='center', color='white')

    plt.colorbar(label='Freqüència (%)')
    plt.tight_layout()
    plt.savefig('graphics/cmap_stress.png', dpi=600, bbox_inches='tight')

    # Desa les dades en un full de càlcul
    frequencia_tonicitat_per_column.to_excel('xlsx/cmap_stress.xlsx')


def spectral_comparison(a, b, mean):
    plt.figure()
    plt.xticks(np.arange(0, 11))
    max_a, min_a = a[0] - a[1], a[0] + a[1]
    plt.fill_between(range(1, 11), max_a, min_a, color='skyblue', alpha=0.4)
    max_b, min_b = b[0] - b[1], b[0] + b[1]
    plt.fill_between(range(1, 11), max_b, min_b, color='lightgreen', alpha=0.4)
    plt.plot(range(1, 11), a[0], label='Conjunt 1', color='blue', linestyle='dashed', marker='o')
    plt.plot(range(1, 11), b[0], label='Conjunt 2', color='green', linestyle='dashed', marker='o')
    # Afegeix la mitjana
    plt.plot(range(1, 11), mean, label='Mitjana', color='red', linestyle='dashed')
    plt.grid(False)
    plt.tight_layout()
    plt.legend()
    plt.savefig('graphics/spectral_comparison.png', dpi=600, bbox_inches='tight')

    # Desa les dades en un full de càlcul
    pd.DataFrame({'Conjunt 1': a[0], 'Conjunt 2': b[0], 'Mitjana': mean}).to_excel('xlsx/spectral_comparison.xlsx')


def extrametricallity(dades):
    """Una funció per obtenir gràfics sobre l'extrametricitat dels autors"""
    # Fes un gràfic de barres amb el valor mitjà de síl·labes extramètriques per autor

    # Normalitza els valors de síl·labes extramètriques per autor ( x <0 = 0; x > 0 = 1)
    dades['síl·labes extramètriques'] = dades['síl·labes extramètriques'].apply(lambda x: 1 if x > 0 else 0)
    probabilitat = dades['síl·labes extramètriques'].mean() * 100
    print(f'Probabilitat de vers extramètric: {probabilitat:.2f}')
    extrametricallity_per_column = (dades.groupby('autor')['síl·labes extramètriques'].sum() / dades.groupby('autor')[
        'síl·labes extramètriques'].count()) * 100
    extrametricallity_per_column = extrametricallity_per_column.sort_values(ascending=True)
    print(extrametricallity_per_column)

    plt.figure(figsize=(8, 4))
    plt.bar(extrametricallity_per_column.index, extrametricallity_per_column, color='skyblue')
    # Afegeix una línia horitzontal que representi la mitjana de síl·labes extramètriques per a tots els autors
    plt.axhline(extrametricallity_per_column.mean(), color='red', linestyle='dashed',
                label=f"Mitjana ({extrametricallity_per_column.mean():.2f})")
    plt.xticks(rotation=90)
    plt.grid(False)
    plt.tight_layout()
    plt.legend()
    plt.savefig('graphics/extrametricallity.png', dpi=600, bbox_inches='tight')

    # Ara calcula la probabilitat per època de vers extramètric i fes-ne un gràfic de barres

    # Defineix les èpoques com a períodes de temps (anys) compresos entre dos valors
    epochs = [(1301, 1400), (1401, 1450), (1451, 1500), (1501, 1600), (1601, 1700)]

    # Agrupa els autors per època
    epochs_authors = {}
    for epoch in epochs:
        any = dades['any'] + 25
        epochs_authors[epoch] = dades[any.between(epoch[0], epoch[1])]['autor'].unique()

    # Calcula la probabilitat de vers extramètric per època i fes-ne un DF:
    # - Una columna amb la probabilitat (recompte de versos extramètrics dividit pel total de versos * 100) per cada època
    # - Cada fila ha de ser una època
    epochs_extrametricallity = {epoch: (dades[dades['autor'].isin(authors)]['síl·labes extramètriques'].sum() /
                                        dades[dades['autor'].isin(authors)]['síl·labes extramètriques'].count()) * 100
                                for epoch, authors in epochs_authors.items()}
    epochs_extrametricallity = pd.DataFrame(epochs_extrametricallity.items(), columns=['Període', 'Probabilitat'])
    # Indexa
    print(epochs_extrametricallity)

    # Fes un gràfic de barres amb la probabilitat de vers extramètric per època
    plt.figure(figsize=(8, 4))
    x = np.array(range(len(epochs_extrametricallity)))
    plt.bar(x, epochs_extrametricallity['Probabilitat'], color='skyblue')
    # Afegeix les etiquetes d'X
    plt.xticks(x, epochs_extrametricallity['Període'])
    # Afegeix una línia de tendència
    coeficents = np.polyfit(x, epochs_extrametricallity['Probabilitat'], 1)
    poly = np.poly1d(coeficents)
    trend = poly(x)
    plt.plot(x, trend, color='blue', linestyle='dashed', label='Tendència')

    plt.xticks(rotation=45)
    plt.grid(False)
    plt.tight_layout()
    plt.legend()
    plt.savefig('graphics/extrametricallity_per_epoch.png', dpi=600, bbox_inches='tight')

    return extrametricallity_per_column


def binarity_index(dades):
    df = dades.groupby('autor')[cols_to_sum].mean() * 100

    # Seqüència ideal
    ideal = np.array([0, 100, 0, 100, 0, 100, 0, 100, 0, 100])

    # Funció per calcular la distància euclidiana
    def calc_bin_index(author_values):
        author_values = np.array(author_values)
        return np.sqrt(np.sum((author_values - ideal) ** 2))

    # Afegir el Model al DataFrame
    model = [0, 100, 0, 100, 0, 100, 0, 100, 0, 100]
    df.loc['Iàmbic'] = model

    print(df)

    # Aplicar la funció a cada fila del DataFrame
    df['binarietat'] = df.apply(calc_bin_index, axis=1)

    # Normalitzar els valors de binarietat
    min_bin = df['binarietat'].min()
    max_bin = df['binarietat'].max()

    df['binarietat_normalitzada'] = (df['binarietat'] - min_bin) / (max_bin - min_bin) * 100

    # Invertir l'índex de binarietat normalitzada
    df['binarietat_invertida'] = 100 - df['binarietat_normalitzada']

    # Mostrar el DataFrame resultant amb l'índex de binarietat
    print(df)

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
    plt.savefig('graphics/binarity_index.png', dpi=600, bbox_inches='tight')

    # Desa les dades en un full de càlcul
    df.to_excel('xlsx/binarity_index.xlsx')

    # Afegir l'índex de binarietat al nom de cada autor
    # df.index = df.index + ' (' + df['binarietat_invertida'].map('{:.2f}'.format) + ')'

    # Calcular les distàncies utilitzant la binarietat invertida
    dist_matrix = df.drop(columns=['binarietat', 'binarietat_normalitzada', 'binarietat_invertida']).values

    # Generar l'enllaç de jerarquia
    linked = linkage(dist_matrix, 'ward')

    # Afegeix els valors al df
    df['cluster'] = sch.fcluster(linked, 2, criterion='maxclust')

    # Generar el dendrograma
    plt.figure(figsize=(10, 5))
    dendrogram(linked,
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

    plt.savefig('graphics/dendrogram_binarity.png', dpi=600, bbox_inches='tight')

    # Desa les dades en un full de càlcul
    df.to_excel('xlsx/dendrogram.xlsx')

    # Retorna l'índex de binarietat de cada autor
    return df['binarietat_invertida']


def set_authors_from_group(dades):
    # Compara un conjunt d'autors respecte d'un altre

    # Defineix els grups d'autors
    periodes = []
    epochs = [(1301, 1450)]
    for epoch in epochs:
        any = dades['any'] + 25
        periodes.append(dades[any.between(epoch[0], epoch[1])]['autor'].unique())

    # Calcula les mitjanes de cada època
    total_values_per_column = dades.groupby('autor')[cols_to_sum].mean()

    # Crea un diccionari amb les mitjanes de cada època
    epochs_means = {epoch: total_values_per_column.loc[authors].mean() for epoch, authors in zip(epochs, periodes)}

    grup = ['Jordi de Sant Jordi', 'Andreu Febrer', 'Pere Torroella', 'Joan Roís de Corella', 'Narcís Vinyoles',
            'Pere Serafí']

    # Crea un DataFrame amb les dades dels autors del grup
    df = dades[dades['autor'].isin(grup)]
    print(df)

    # Calcula la freqüència de tonicitat de les síl·labes 1-9 de cada autor del grup
    total_values_per_column = df.groupby('autor')[cols_to_sum].mean()

    # Crea un gràfic per comparar els autors del grup i les mitjanes de les èpoques.
    plt.figure(figsize=(8, 6))
    x_values = range(1, 11)  # Valors per a l'eix X
    plt.xticks(np.arange(0, 11))
    for epoch, mean in epochs_means.items():
        plt.plot(x_values, mean, label=f'{epoch[0]}-{epoch[1]}', marker='o', linestyle='dashed')

    for author, values in total_values_per_column.iterrows():
        plt.plot(x_values, values, label=author, marker='o', linestyle='dashed')

    plt.legend()
    plt.grid(False)
    plt.tight_layout()
    plt.savefig('graphics/comprare_set_authors_group.png', dpi=600, bbox_inches='tight')


def compare_languages(dades):
    df = dades.groupby('autor')[cols_to_sum].mean() * 100

    # Seqüència ideal
    ideal = np.array([0, 100, 0, 100, 0, 100, 0, 100, 0, 100])

    # Funció per calcular la distància euclidiana
    def calc_bin_index(author_values):
        author_values = np.array(author_values)
        return np.sqrt(np.sum((author_values - ideal) ** 2))

    # Afegir el Model al DataFrame
    model = [0, 100, 0, 100, 0, 100, 0, 100, 0, 100]
    df.loc['Iàmbic'] = model

    # Afegeix altres llengües
    df.loc['Carpasso (ITA)'] = [50, 40, 30, 70, 10, 75, 20, 75, 5, 100]
    df.loc['Tansillo (ITA)'] = [30, 40, 25, 65, 5, 75, 20, 75, 3, 100]
    df.loc['Petrarca (ITA)'] = [30, 40, 27, 65, 2, 65, 18, 60, 2, 100]

    df.loc['De La Torre (CAST)'] = [40, 35, 35, 60, 3, 75, 5, 45, 3, 100]
    df.loc['Garcilaso (CAST)'] = [40, 57, 28, 60, 2, 77, 10, 56, 2, 100]

    print(df)

    # Aplicar la funció a cada fila del DataFrame
    df['binarietat'] = df.apply(calc_bin_index, axis=1)

    # Normalitzar els valors de binarietat
    min_bin = df['binarietat'].min()
    max_bin = df['binarietat'].max()

    df['binarietat_normalitzada'] = (df['binarietat'] - min_bin) / (max_bin - min_bin) * 100

    # Invertir l'índex de binarietat normalitzada
    df['binarietat_invertida'] = 100 - df['binarietat_normalitzada']

    # Mostrar el DataFrame resultant amb l'índex de binarietat
    print(df)

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
    plt.savefig('graphics/lang_binarity_index.png', dpi=600, bbox_inches='tight')

    # Desa les dades en un full de càlcul
    df.to_excel('xlsx/lang_binarity_index.xlsx')

    # Afegir l'índex de binarietat al nom de cada autor
    df.index = df.index + ' (' + df['binarietat_invertida'].map('{:.2f}'.format) + ')'

    # Calcular les distàncies utilitzant la binarietat invertida
    dist_matrix = df.drop(columns=['binarietat', 'binarietat_normalitzada', 'binarietat_invertida']).values

    # Generar l'enllaç de jerarquia
    linked = linkage(dist_matrix, 'ward')

    # Afegeix els valors al df
    df['cluster'] = sch.fcluster(linked, 2, criterion='maxclust')

    # Generar el dendrograma
    plt.figure(figsize=(10, 5))
    dendrogram(linked,
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

    plt.savefig('graphics/lang_dendrogram_binarity.png', dpi=600, bbox_inches='tight')

    # Desa les dades en un full de càlcul
    df.to_excel('xlsx/lang_dendrogram.xlsx')

    # Retorna l'índex de binarietat de cada autor
    return df['binarietat_invertida']


def plot_authors_subdivision_set(dades):
    """Mostra els contorns accentuals d'un grup d'autors segons la seva subdivisió"""
    authors = ['Francesc Vicent Garcia', 'Francesc Fontanella']
    dades = dades.groupby('autor').filter(lambda x: x['autor'].iloc[0] in authors)

    df = dades[['autor', 'subdivisió', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']]
    df = pd.DataFrame(df.groupby(['autor', 'subdivisió'])[cols_to_sum].mean() * 100)

    # Calcula la mitjana dels valors de col_sum segons el tipus de subdivisió juntant els dos autors.
    df = df.reset_index()
    df = df.groupby('subdivisió')[cols_to_sum].mean()

    print(df)

    plt.figure(figsize=(8, 6))
    x_values = range(1, 11)  # Valors per a l'eix X
    plt.xticks(np.arange(0, 11))
    for subdivision, values in df.iterrows():
        plt.plot(x_values, values, label=subdivision, marker='o', linestyle='dashed')
    plt.legend()
    plt.grid(False)
    plt.tight_layout()
    plt.savefig('graphics/authors_subdivision_set.png', dpi=600, bbox_inches='tight')

    print(df)

    # El mateix però calculant la distància respecte del model ideal
    model = [0, 100, 0, 100, 0, 100, 0, 100, 0, 100]

    plt.figure(figsize=(8, 6))
    x_values = range(1, 11)  # Valors per a l'eix X
    plt.xticks(np.arange(0, 11))
    for subdivision, values in df.iterrows():
        desviacio = [abs(d - m) for d, m in zip(values, model)]
        plt.plot(x_values, desviacio, label=subdivision, marker='o', linestyle='dashed')
    plt.plot(x_values, [0] * 10, label='Iàmbic', color='grey', linestyle='dashed')
    # Valor 50 de Y
    plt.axhline(50, color='grey', alpha=0.2)
    plt.legend()
    plt.grid(False)
    plt.tight_layout()
    plt.savefig('graphics/authors_subdivision_set_deviation.png', dpi=600, bbox_inches='tight')


def extrametricity_binarity(dades):
    """Una funció per mostrar els valors d'extrametricitat i binarietat per a cada autor i establir-ne una relació"""
    extrametricitat = extrametricallity(dades)
    binarity = binarity_index(dades).drop('Iàmbic')

    # Cerca una correlació entre els valors d'extrametricitat i binarietat per a cada autor. La hipòtesi és que a major extrametricitat, major binarietat. Fes-ne un df
    df = pd.DataFrame({'Extrametricitat': extrametricitat, 'Binarietat': binarity})
    # Correlació de Pearson
    correlacio = df['Extrametricitat'].corr(df['Binarietat'])

    # Calcula el valor-p de la correlació
    _, p_value = pearsonr(df['Binarietat'], df['Extrametricitat'])

    print('-----------------------------------------------------')
    print(f'Correlació entre extrametricitat i binarietat: {correlacio:.2f}')
    print(f'Valor-p: {p_value:.2f}')
    print('-----------------------------------------------------')


if __name__ == '__main__':
    enter = input('Quin corpus vols mostrar?')
    path = f'../corpus/corpora/{enter}/etiquetat/csv/'
    cols_to_sum = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    dades_totals = llegir_dades(path)
    dades_totals = prepara_dades(dades_totals)

    plot_authors_subdivision_set(dades_totals)

    global_mean = mean_stress(dades_totals)[0]
    global_std = mean_stress(dades_totals)[1]

    # binarity_index(dades_totals)
    compare_languages(dades_totals)

    # extrametricallity(dades_totals)
    extrametricity_binarity(dades_totals)
    plot_stress(dades_totals)

    set_authors_from_group(dades_totals)

    mean_stress_epoch(dades_totals, global_mean)
    epochs_mean_and_one_author(dades_totals, 'Ausiàs March')
    list_authors(dades_totals)

    mean_deviation_from_iambic(dades_totals)

    autors = ['Joan Roís de Corella', 'Francesc Ferrer', 'Narcís Vinyoles', 'Blai Assenci', 'Pere Serafí',
              'Francesc Vicent Garcia', 'Francesc Fontanella']
    a = compare_authors_set(dades_totals, autors, '1')
    # Elimina aquests autors de les dades
    n_dades = dades_totals[~dades_totals['autor'].isin(autors)]
    # Una llista amb els noms autors que no queden:
    autors_c2 = n_dades['autor'].unique()
    b = compare_authors_set(n_dades, autors_c2, '2')
    spectral_comparison(a, b, global_mean)

    compare_authors(dades_totals, 'Ausiàs March', 'Dionís Guiot')
    deviance_from_iambic(dades_totals)
    deviance_from_iambic_epoch(dades_totals)
    quantify_centuries(dades_totals)
    cmap_stress(dades_totals)
    plot_subdivisions(dades_totals)
