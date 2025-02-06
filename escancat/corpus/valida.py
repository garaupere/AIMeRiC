"""Un mòdul per a la validació de les dades __test que compara l'etiquetatge automàtic amb l'etiquetatge manual."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from escancat.corpus.modules.getUSB import getUSB

plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams["font.family"] = "Times New Roman"



def valida():
    """Una funció per validar les dades __test."""
    usb = getUSB()
    automatic = normalitza(read_csv(f'{usb}/corpora/__test/etiquetat/__test.csv'))
    manual = read_csv('corpus/fitxers_validacio/__test_manual.csv')
    manual = manual[['text del vers', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']]

    df = compare(automatic, manual)
    plot_comparison(df)

def read_csv(path):
    """Carrega un fitxer csv a un DataFrame"""
    data = pd.read_csv(path, sep=';', encoding='utf-8', lineterminator='\n', header=0)
    return data


def normalitza(data):
    sillabes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']

    data[sillabes] = data[sillabes].applymap(
        lambda x: 1 if x > 1 else 0)  # 1 si és major que 1, 0 si no ho és

    # Selecciona les columnes pertinents: autor, text del vers, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
    data = data[['text del vers', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']]

    return data


def compare(automatic: pd.DataFrame, manual: pd.DataFrame) -> pd.DataFrame:
    sillabes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']

    print('--' * 40)
    # Imprimeix el valor de cada fila del df la columna 'text del vers'
    df_comp = pd.DataFrame(
        columns=['text del vers'] + ['1_auto', '2_auto', '3_auto', '4_auto', '5_auto', '6_auto', '7_auto', '8_auto',
                                     '9_auto', '10_auto'] + ['1_manual', '2_manual', '3_manual', '4_manual', '5_manual',
                                                             '6_manual', '7_manual', '8_manual', '9_manual',
                                                             '10_manual'])

    for i in range(len(automatic)):
        vers = automatic.iloc[i]['text del vers']

        if vers in manual['text del vers'].values:
            # print(">>", vers)
            sill_autom = automatic.iloc[i][sillabes].values
            sill_manual = manual[manual['text del vers'] == vers][sillabes].values[0]
            # print(vers, sill_autom, sill_manual)

            row = pd.Series([vers] + list(sill_autom) + list(sill_manual), index=df_comp.columns)
            df_comp = pd.concat([df_comp, row.to_frame().T], ignore_index=True)
    return df_comp


def plot_comparison(comparison_df):
    """Una funció per comparar els valors de tonicitat de les síl·labes automàtiques i manuals."""
    auto = comparison_df[
        ['1_auto', '2_auto', '3_auto', '4_auto', '5_auto', '6_auto', '7_auto', '8_auto', '9_auto', '10_auto']]
    manual = comparison_df[
        ['1_manual', '2_manual', '3_manual', '4_manual', '5_manual', '6_manual', '7_manual', '8_manual', '9_manual',
         '10_manual']]

    # Normalitza els noms de les columnes a 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
    auto.columns = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    manual.columns = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    # Mean scatter plot without lines
    auto_mean = auto.mean() * 100
    manual_mean = manual.mean() * 100
    plt.figure(figsize=(5, 5))
    plt.xticks(np.arange(0, 11))
    plt.plot(auto_mean, 'o', color='red', label='Automàtic')
    plt.plot(manual_mean, '^', color='blue', label='Manual')
    plt.grid(False)
    plt.tight_layout()
    plt.legend()
    plt.savefig('corpus/fitxers_validacio/comparison.svg')
    plt.close()

    # Calcula la distància total entre els valors automàtics i manuals
    total_distance = np.abs(auto_mean - manual_mean).mean()
    print(f'\t > Precisió de l\'etiquetatge: {100 - total_distance:.2f}%')

    # Desa les dades de la comparació en un fitxer xlsx
    difference = abs(auto_mean - manual_mean)
    df = pd.DataFrame({'Automàtic': auto_mean, 'Manual': manual_mean, 'Diferència': difference})
    df.to_excel('corpus/fitxers_validacio/comparison.xlsx', index=False)
    plt.figure(figsize=(5, 5))
    plt.bar(df.index, df['Diferència'], color='skyblue')
    # Difference mean
    plt.axhline(difference.mean(), color='red', linestyle='--', label='Mitjana')
    plt.text(9.8, difference.mean() + 0.02, f'{difference.mean():.2f}', fontsize=12, color='red')
    plt.xticks(np.arange(0, 11))
    plt.grid(False)
    plt.tight_layout()
    plt.savefig('corpus/fitxers_validacio/difference.svg')


if __name__ == '__main__':
    print('Validació de les dades __test.')
    usb = getUSB()
    automatic = normalitza(read_csv(f'{usb}/corpora/__test/etiquetat/__test.csv'))
    manual = read_csv('corpus/fitxers_validacio/__test_manual.csv')
    manual = manual[['text del vers', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']]

    df = compare(automatic, manual)
    plot_comparison(df)
