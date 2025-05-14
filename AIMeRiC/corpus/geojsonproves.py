import ast

import matplotlib.pyplot as plt
import geopandas as gpd
import contextily as ctx
import numpy as np
import pandas as pd
from tabulate import tabulate

from AIMeRiC.corpus.modules.getUSB import getUSB

# Obre el fitxer geojson i llegeix el contingut.
usb = getUSB()
corpus = 'actual'


def mapa_estatic(usb, corpus):
    path = f'{usb}/corpora/{corpus}/etiquetat/svg/mapa.geojson'

    # Llegeix les dades del fitxer GeoJSON
    gdf = gpd.read_file(path)

    # Converteix el sistema de coordenades a Web Mercator (EPSG:3857) per a utilitzar contextily
    gdf = gdf.to_crs(epsg=3857)

    # Configura la figura
    fig, ax = plt.subplots(figsize=(15, 15))

    # Dibuixa els punts de ciutat
    gdf.plot(ax=ax, color='blue', alpha=0.4, markersize=10 * gdf['poetes'], label='Autors')

    # Afegeix un mapa base (OpenStreetMap per defecte)
    ctx.add_basemap(ax, source=ctx.providers.CartoDB.PositronNoLabels)

    # Configura el títol i les etiquetes dels eixos
    # Amaga els eixos
    ax.set_axis_off()

    # Guarda el mapa com a imatge
    plt.savefig(f'{usb}/corpora/{corpus}/etiquetat/svg/mapa_autors.svg', dpi=600, bbox_inches='tight')
    plt.close()

    # Configura la figura
    fig, ax = plt.subplots(figsize=(15, 15))

    # Dibuixa els punts de ciutat
    gdf.plot(ax=ax, color='red', alpha=0.4, markersize=0.015 * gdf['versos'], label='Versos')

    # Afegeix un mapa base (OpenStreetMap per defecte)
    ctx.add_basemap(ax, source=ctx.providers.CartoDB.PositronNoLabels)

    # Configura el títol i les etiquetes dels eixos
    # Amaga els eixos
    ax.set_axis_off()

    # Guarda el mapa com a imatge
    plt.savefig(f'{usb}/corpora/{corpus}/etiquetat/svg/mapa_versos.svg', dpi=600, bbox_inches='tight')




def dialectes(usb, corpus):
    path = f'{usb}/corpora/{corpus}/etiquetat/xlsx/metadades_autors.xlsx'
    df = pd.read_excel(path)
    df = df[['name', 'dialect', 'versos']]

    # Per a cada dialecte quantifica quants autors i quants versos hi ha

    new_df = df.groupby('dialect').agg({'name': 'count', 'versos': 'sum'}).reset_index()
    new_df.columns = ['dialect', 'autors', 'versos']

    # Gràfic autors per dialecte
    plt.figure(figsize=(6, 6))
    plt.bar(new_df['dialect'], new_df['autors'], color='blue', alpha=0.5)
    # Indica el percentage de cada dialecte
    total = new_df['autors'].sum()
    for i, v in enumerate(new_df['autors']):
        plt.text(i, v + 0.5, f'{v / total * 100:.1f}%', ha='center', va='bottom')
    plt.xticks(rotation=45)
    plt.savefig(f'{usb}/corpora/{corpus}/etiquetat/svg/dialecte_a.svg', dpi=600, bbox_inches='tight')
    plt.close()

    # Gràfic versos per dialecte
    plt.figure(figsize=(6, 6))
    plt.bar(new_df['dialect'], new_df['versos'], color='red', alpha=0.5)
    # Indica el percentage de cada dialecte
    total = new_df['versos'].sum()
    for i, v in enumerate(new_df['versos']):
        plt.text(i, v + 0.5, f'{v / total * 100:.1f}%', ha='center', va='bottom')
    plt.xticks(rotation=45)
    plt.savefig(f'{usb}/corpora/{corpus}/etiquetat/svg/dialecte_v.svg', dpi=600, bbox_inches='tight')
    plt.close()

    return new_df


def generes(usb, corpus):
    path = f'{usb}/corpora/{corpus}/etiquetat/xlsx/metadades_autors.xlsx'
    df = pd.read_excel(path)
    df = df[['name', 'gender', 'versos']]
    df['gender'] = df['gender'].replace({0: 'home', 1: 'dona', 2: 'altres'})

    # Per a cada gènere quantifica quants autors i quants versos hi ha
    new_df = df.groupby('gender').agg({'name': 'count', 'versos': 'sum'}).reset_index()
    new_df.columns = ['gender', 'autors', 'versos']

    # Gràfic autors per gènere
    plt.figure(figsize=(6, 6))
    plt.bar(new_df['gender'], new_df['autors'], color='blue', alpha=0.5)
    # Indica el percentage de cada gènere
    total = new_df['autors'].sum()
    for i, v in enumerate(new_df['autors']):
        plt.text(i, v + 0.5, f'{v / total * 100:.1f}%', ha='center', va='bottom')
    plt.xticks(rotation=45)
    plt.savefig(f'{usb}/corpora/{corpus}/etiquetat/svg/genere_a.svg', dpi=600, bbox_inches='tight')
    plt.close()

    # Gràfic versos per gènere
    plt.figure(figsize=(6, 6))
    plt.bar(new_df['gender'], new_df['versos'], color='red', alpha=0.5)
    # Indica el percentage de cada gènere
    total = new_df['versos'].sum()
    for i, v in enumerate(new_df['versos']):
        plt.text(i, v + 0.5, f'{v / total * 100:.1f}%', ha='center', va='bottom')
    plt.xticks(rotation=45)
    plt.savefig(f'{usb}/corpora/{corpus}/etiquetat/svg/genere_v.svg', dpi=600, bbox_inches='tight')
    plt.close()


def anys(usb, corpus):
    path = f'{usb}/corpora/{corpus}/etiquetat/xlsx/metadades_autors.xlsx'
    df = pd.read_excel(path)
    df = df[['name', 'born_date', 'versos']]

    # Agrupa els autors per dècada de naixement
    df['decade'] = (df['born_date'] // 10) * 10
    # Elimina els autors sense data de naixement
    df = df[df['decade'] != 0]

    # Per a cada dècada quantifica quants autors i quants versos hi ha
    new_df = df.groupby('decade').agg({'name': 'count', 'versos': 'sum'}).reset_index()

    new_df.columns = ['decade', 'autors', 'versos']

    # Calcula el percentatge d'autors i de versos que representen cada dècada
    new_df['autors_rel'] = new_df['autors'] / new_df['autors'].sum() * 100
    new_df['versos_rel'] = new_df['versos'] / new_df['versos'].sum() * 100

    # Gràfic autors per dècada
    plt.figure(figsize=(8, 6))
    # Distribueix a l'eix X les diferents dècades i fes una barra per cada dècada
    plt.bar(new_df['decade'], new_df['autors'], color='blue', alpha=0.5)
    # Indica el percentage de cada dècada a partir de la columna autors_rel
    for i in range(len(new_df)):
        plt.text(new_df['decade'][i], new_df['autors'][i] + 0.5, f'{new_df["autors_rel"][i]:.1f}%', ha='center',
                 va='bottom')
    plt.xticks(rotation=45)
    plt.savefig(f'{usb}/corpora/{corpus}/etiquetat/svg/decade_a.svg', dpi=600, bbox_inches='tight')
    plt.close()

    # Gràfic versos per dècada
    plt.figure(figsize=(8, 6))
    # Distribueix a l'eix X les diferents dècades i fes una barra per cada dècada
    plt.bar(new_df['decade'], new_df['versos'], color='red', alpha=0.5)
    # Indica el percentage de cada dècada a partir de la columna autors_rel
    for i in range(len(new_df)):
        plt.text(new_df['decade'][i], new_df['versos'][i] + 0.5, f'{new_df["versos_rel"][i]:.1f}%', ha='center',
                 va='bottom')
    plt.xticks(rotation=45)
    plt.savefig(f'{usb}/corpora/{corpus}/etiquetat/svg/decade_v.svg', dpi=600, bbox_inches='tight')
    plt.close()

    df = pd.read_excel(path)
    df = df[['name', 'born_date', 'death_date', 'versos']]

    # Fes una línia del temps amb els autors

    # Els autors sense data de mort es representen fins 2025
    df['death_date'] = df['death_date'].fillna(2025)

    # Crea una nova columna amb la durada de la vida
    df['life_duration'] = (df['death_date'] - df['born_date'])
    df['life_duration'] = df['life_duration'].fillna(0)
    df['year'] = df['born_date']

    # Ordena els autors per data de naixement
    df = df.sort_values(by=['born_date'], ascending=False)
    # Plot línia del temps
    plt.figure(figsize=(18, 25))
    plt.hlines(df['name'], df['born_date'], df['death_date'], color='blue', alpha=0.5, lw=2)
    plt.scatter(df['born_date'], df['name'], color='blue', marker='|', alpha=0.5, s=100)
    plt.scatter(df['death_date'], df['name'], color='blue', marker='|', alpha=0.5, s=100)
    plt.title('Línia del temps dels autors')
    plt.xlabel('Data')
    plt.ylabel('Autors')
    # Fes que els anys (eix X) apareguin cada 5 anys
    plt.xticks(range(1845, 2030, 5))
    plt.xticks(rotation=45)
    plt.savefig(f'{usb}/corpora/{corpus}/etiquetat/svg/linia_temps.svg', dpi=600, bbox_inches='tight')
    plt.close()


def font(usb, corpus):
    path = f'{usb}/corpora/{corpus}/etiquetat/xlsx/metadades_autors.xlsx'
    df = pd.read_excel(path)
    df = df[['name', 'font', 'versos']]

    # Imprimeix cada fila del df
    for index, row in df.iterrows():
        if type(row['font']) == str:
            if row['font'].startswith('['):
                row['font'] = ast.literal_eval(row['font'])
                for x in row['font']:
                    df._append({'name': row['name'], 'font': x, 'versos': row['versos']}, ignore_index=True)
                df = df.drop(index)


    # Elimina els autors sense font
    #df = df.dropna(subset=['font'])

    # Per a cada font quantifica quants autors i quants versos hi ha
    new_df = df.groupby('font').agg({'name': 'count', 'versos': 'sum'}).reset_index()
    new_df.columns = ['font', 'autors', 'versos']

    new_df['font'] = new_df['font'].replace({'Corpus Textual Informatitzat de la Llengua Catalana': 'CTILC', 'Corpus Literari Digital de la Càtedra Màrius Torres': 'CMT', "Donatiu de l'autor o curador": "donatiu", 'Llibre electrònic': 'ebook'})

    # Gràfic autors per font
    plt.figure(figsize=(6, 6))
    plt.bar(new_df['font'], new_df['autors'], color='blue', alpha=0.5)
    # Indica el percentage de cada font
    total = new_df['autors'].sum()
    for i, v in enumerate(new_df['autors']):
        plt.text(i, v + 0.5, f'{v / total * 100:.1f}%', ha='center', va='bottom')
    plt.xticks(rotation=45)
    plt.savefig(f'{usb}/corpora/{corpus}/etiquetat/svg/font_a.svg', dpi=600, bbox_inches='tight')
    plt.close()

    print(tabulate(new_df, headers='keys', tablefmt='psql'))
    # Gràfic versos per font
    plt.figure(figsize=(6, 6))
    plt.bar(new_df['font'], new_df['versos'], color='red', alpha=0.5)
    # Indica el percentage de cada font
    total = new_df['versos'].sum()
    for i, v in enumerate(new_df['versos']):
        plt.text(i, v + 0.5, f'{v / total * 100:.1f}%', ha='center', va='bottom')
    plt.xticks(rotation=45)
    plt.savefig(f'{usb}/corpora/{corpus}/etiquetat/svg/font_v.svg', dpi=600, bbox_inches='tight')
    plt.close()



#dialectes(usb, corpus)
#generes(usb, corpus)
#anys(usb, corpus)
#font(usb, corpus)
mapa_estatic(usb, corpus)