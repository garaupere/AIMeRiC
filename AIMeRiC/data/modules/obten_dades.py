import json
import os

import geopandas
import matplotlib.pyplot as plt
import kaleido
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import folium
from plotly.offline import iplot, init_notebook_mode
from tabulate import tabulate
from tqdm import tqdm
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram

from AIMeRiC.corpus.modules.getUSB import getUSB
from AIMeRiC.data.modules.geoproves import get_city
from AIMeRiC.data.modules.utils import aplica_filtre, read_csv

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



def normalitza(data):
    sillabes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    data[sillabes] = data[sillabes].map(
        lambda x: 1 if int(x) > 1 else 0)  # 1 si és major que 1, 0 si no ho és

    return data


def contorn_ritmic(data, name):
    """Genera un DataFrame amb el contorn rítmic de cada autor i fes-ne un gràfic interactiu."""
    sillabes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    df = data.groupby('autor')[sillabes].mean()
    # Desa el DataFrame en un fitxer xlsx
    df.to_excel(f'{usb}/corpora/{name}/etiquetat/xlsx/contorn_ritmic.xlsx')

    # Genera un gràfic interactiu amb Plotly
    fig = go.Figure()

    # Afegir línies per a cada autor
    x_values = list(range(1, 11))
    for autor in df.index:
        fig.add_trace(go.Scatter(
            x=x_values,
            y=df.loc[autor],
            mode='lines+markers',
            name=autor,
            line=dict(dash='dash')
        ))

    # Afegir la línia de la mitjana
    autors_mean = df.mean()
    fig.add_trace(go.Scatter(
        x=x_values,
        y=autors_mean,
        mode='lines+markers',
        name='Mitjana',
        line=dict(color='red', width=2)
    ))

    # Configuració del gràfic
    fig.update_layout(
        title="Contorn Rítmic per Autor",
        xaxis_title="Síl·labes",
        yaxis_title="Freqüència (%)",
        xaxis=dict(tickmode='linear', tick0=1, dtick=1),
        yaxis=dict(range=[0, 1]),
        legend_title="Autors",
        template="plotly_white"
    )

    # Emmarca el gràfic només en els valors de 1-10 a X i 0-100 a Y
    fig.update_xaxes(range=[1, 10])
    fig.update_yaxes(range=[0, 1])

    # Autoscale
    fig.update_yaxes(autorange=True)
    fig.update_xaxes(autorange=True)

    # Desa el gràfic com a fitxer HTML
    fig.write_html(f'{usb}/corpora/{name}/etiquetat/svg/contorn_ritmic.html')

    init_notebook_mode()
    iplot(fig)
    # Desa el gràfic com a fitxer SVG
    fig.write_image(f'{usb}/corpora/{name}/etiquetat/svg/contorn_ritmic.svg')



def distancia_iambe(data, name):
    # Calcula la distància respecte del model per a cada síl·laba
    sillabes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    df = data.groupby('autor')[sillabes].mean() * 100
    model = [0, 100, 0, 100, 0, 100, 0, 100, 0, 100]
    distancies = pd.DataFrame()
    new_columns = {autor: np.abs(df.loc[autor] - model) for autor in df.index}
    distancies = pd.concat([distancies, pd.DataFrame(new_columns)], axis=1)
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

    new_columns = {autor: np.abs(df.loc[autor] - model) for autor in df.index}
    distancies = pd.concat([distancies, pd.DataFrame(new_columns)], axis=1)

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
        plt.annotate(f'{dst.iloc[i]:.2f}', (i + 1, mean.iloc[i] + dst.iloc[i] + 1), ha='center', va='bottom')
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





def cartografies(metadades, corpus):
    cities_df = metadades.groupby('city').size().reset_index(name='count')

    # Afegeix les coordenades de cada ciutat amb geoproves.get_city(city)
    coords = cities_df['city'].apply(lambda x: get_city(x))

    # El dataframe ha de tenir les columnes ['ciutat', 'poetes', 'latitud', 'longitud', 'noms_poetes']
    cities_df['ciutat'] = cities_df['city']
    cities_df['poetes'] = cities_df['count']
    cities_df['latitud'] = coords.apply(lambda x: x[0])
    cities_df['longitud'] = coords.apply(lambda x: x[1])
    cities_df['província'] = coords.apply(lambda x: x[2])
    cities_df['país'] = coords.apply(lambda x: x[3])
    cities_df['versos'] = cities_df['ciutat'].apply(lambda x: metadades[metadades['city'] == x]['versos'].sum())
    # Afegeix una columna amb els noms dels poetes de cada ciutat
    cities_df['noms_poetes'] = cities_df['city'].apply(lambda x: ', '.join(
        metadades[metadades['city'] == x]['name'].tolist()))
    cities_df = cities_df[['ciutat', 'poetes', 'latitud', 'longitud', 'província', 'país', 'noms_poetes', 'versos']]

    # Calcula el percentatge de poetes i versos per ciutat
    cities_df['poetes_rel'] = (cities_df['poetes'] / cities_df['poetes'].sum()) * 100
    cities_df['versos_rel'] = (cities_df['versos'] / cities_df['versos'].sum()) * 100

    # Desa el df en un fitxer xlsx
    cities_df.to_excel(f'{usb}/corpora/{corpus}/etiquetat/xlsx/cities.xlsx')

    # Genera un mapa
    mapa = folium.Map(location=[39.5, 2.5], zoom_start=6)  # Centrat als Països Catalans
    autors = folium.FeatureGroup("Autors")
    versos = folium.FeatureGroup("Versos")

    # Afegir punts al mapa
    for index, row in cities_df.iterrows():
        folium.CircleMarker(
            location=(row['latitud'], row['longitud']),
            radius=row['poetes'] * 0.5,  # Escala proporcional al nombre de poetes
            popup=folium.Popup(
                f"<b>{row['ciutat']}</b><br>"
                f"Poetes: {row['poetes']}<br>"
                f"Noms: {row['noms_poetes']}",
                max_width=300  # Amplada màxima del popup
            ),
            color="blue",
            fill=True,
            fill_color="blue"
        ).add_to(autors)

        folium.CircleMarker(
            location=(row['latitud'], row['longitud']),
            radius=row['versos'] * 0.001,  # Escala proporcional al nombre de versos
            popup=folium.Popup(
                f"<b>{row['ciutat']}</b><br>"
                f"Versos: {row['versos']}<br>",
                max_width=300  # Amplada màxima del popup
            ),
            color="red",
            fill=True,
            fill_color="red"
        ).add_to(versos)

    mapa.add_child(autors)
    mapa.add_child(versos)

    folium.LayerControl().add_to(mapa)
    # Guardar el mapa com a fitxer HTML
    mapa.save(f"{usb}/corpora/{corpus}/etiquetat/svg/mapa.html")

    gdf = geopandas.GeoDataFrame(cities_df, geometry=geopandas.points_from_xy(cities_df.longitud, cities_df.latitud))
    gdf.crs = "EPSG:4326"  # Defineix el sistema de coordenades
    # Desam el geodataframe com a geojson
    gdf.to_file(f'{usb}/corpora/{corpus}/etiquetat/svg/mapa.geojson', driver='GeoJSON')

    print("Mapa generat i desat!")


def metadades_autors(corpus):
    """Un mòdul per explorar les metadades dels autors"""
    metadades = pd.DataFrame()
    for autor in os.listdir(f'{usb}/corpora/{corpus}/etiquetat/json/'):
        if autor.endswith('.json'):
            # Obre el fitxer json
            with open(f'{usb}/corpora/{corpus}/etiquetat/json/{autor}', encoding='utf-8') as f:
                data = json.load(f)
                versos = len(
                    pd.read_csv(f'{usb}/corpora/{corpus}/etiquetat/csv/{autor.replace(".json", "")}.csv', sep=';',
                                encoding='utf-8', lineterminator='\n', header=0, low_memory=False)) - 1
                meta = {"author_id": data["author_id"],
                        "name": data["name"],
                        "gender": data["gender"] if data["gender"] else 0,
                        "born_date": data["born_date"] if data["born_date"] else None,
                        "death_date": data["death_date"] if data["death_date"] else None,
                        "city": data["city"],
                        "dialect": data["dialect"],
                        "viaf": data["viaf"],
                        "wiki_id": data["wiki_id"],
                        "font": [data['font']],
                        "versos": versos}
                # Afegeix les metadades a un DataFrame
                metadades = pd.concat([metadades, pd.DataFrame(meta, index=[0])], ignore_index=True)

    # Desa les metadades en un fitxer xlsx
    metadades.to_excel(f'{usb}/corpora/{corpus}/etiquetat/xlsx/metadades_autors.xlsx')
    print("Metadades extretes!")
    return metadades



if __name__ == '__main__':
    root = fr"{usb}/corpora/"
    corpus = "actual"
    #metadades_autors(corpus)

    metadades = f'{usb}/corpora/{corpus}/etiquetat/xlsx/metadades_autors.xlsx'
    metadades = pd.read_excel(metadades, index_col=0)
    cartografies(metadades, corpus)
