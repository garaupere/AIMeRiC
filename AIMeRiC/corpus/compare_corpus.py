import pandas as pd
from tabulate import tabulate

from AIMeRiC.corpus.modules.getUSB import getUSB
from AIMeRiC.corpus.obten_dades import read_csv


def compare(corpus_1, corpus_2):
    """Compara dos corpus i retorna les diferències entre ells."""
    print("--" * 20, "Nombre d'autors", "--" * 20)
    versos = corpus_1.groupby('autor')['1'].count()
    df_1 = pd.DataFrame({'Versos': versos})

    versos = corpus_2.groupby('autor')['1'].count()
    df_2 = pd.DataFrame({'Versos': versos})

    # Crea un DF amb els dos corpus i indica quins autors són comuns
    compare_df = pd.merge(df_1, df_2, how='outer', left_index=True, right_index=True)
    compare_df.columns = ['CTILC', 'actual']
    compare_df = compare_df.fillna(0)
    compare_df['Diferència'] = compare_df['CTILC'] - compare_df['actual']
    compare_df['Diferència'] = compare_df['Diferència'].abs()
    compare_df['Diferència'] = compare_df['Diferència'].astype(int)
    compare_df = compare_df.sort_values(by='Diferència', ascending=False)
    compare_df = compare_df.reset_index()

    print(tabulate(compare_df, headers='keys', tablefmt='psql'))
    # Desa-ho en un fitxer Excel
    compare_df.to_excel("compared_corpus.xlsx", index=False)


if __name__ == "__main__":
    usb = getUSB()
    corpus_1 = read_csv(f'{usb}/corpora/ctilc/etiquetat/ctilc.csv')
    corpus_2 = read_csv(f'{usb}/corpora/actual/etiquetat/actual.csv')

    compare(corpus_1, corpus_2)
