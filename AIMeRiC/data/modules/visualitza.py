import ast

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
from plotly.offline import iplot
import plotly.express as px
import contextily as ctx

from AIMeRiC.corpus.modules.getUSB import getUSB

# Obre el fitxer geojson i llegeix el contingut.
usb = getUSB()
corpus = 'actual'


def desctiptives(data_set, name):
    """Un mòdul per mostrar informacions descriptives de les dades"""
    # 1. Imprimeix en un df el nombre d'autors de les dades, amb el nombre de versos i síl·labes per a cada autor
    # El df ha de tenir les columnes= ['Autor', 'Versos', 'Síl·labes']
    versos = data_set.groupby('autor')['1'].count()
    silabes = data_set.groupby('autor')['síl·labes mètriques'].sum()
    silabes_extra = data_set.groupby('autor')['síl·labes extramètriques'].sum()
    silabes = silabes + silabes_extra
    df = pd.DataFrame({'Versos': versos, 'Síl·labes': silabes})
    # Compta quants de llibres hi ha per autor
    df['Llibres'] = data_set.groupby('autor')['obra'].nunique()
    # Compta quants de poemes hi ha per autor
    # df['Poemes'] = data_set.groupby('autor')['poema'].nunique()
    # Afegeix el valor total del corpus
    df.loc['Total'] = df.sum()
    df = df.reset_index()
    df = df.rename(columns={'index': 'Autor'})
    # Desa les dades en un full de càlcul
    df.to_excel(f'{usb}/corpora/{name}/etiquetat/xlsx/descriptives.xlsx')
    return df


def mapa_dinamic(geojson):
    # Converteix el sistema de coordenades a WGS84 (EPSG:4326) per a Plotly
    gdf = geojson.to_crs(epsg=4326)

    # Mapa per autors
    fig_autors = px.scatter_mapbox(
        gdf,
        lat=gdf.geometry.y,
        lon=gdf.geometry.x,
        size=gdf['poetes'],
        color_discrete_sequence=["blue"],
        opacity=0.5,
        hover_name="ciutat",
        hover_data={"poetes": True, "versos": False},
        title="Mapa d'Autors"
        )
    fig_autors.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=5.5,
        mapbox_center={"lat": 39.5, "lon": 2.5},
        height=800
        )
    iplot(fig_autors)
    fig_autors.write_html(f'{usb}/corpora/{corpus}/etiquetat/svg/mapa_autors.html')
    fig_autors.write_image(f'{usb}/corpora/{corpus}/etiquetat/svg/mapa_autors.svg')

    # Mapa per versos
    fig_versos = px.scatter_mapbox(
        gdf,
        lat=gdf.geometry.y,
        lon=gdf.geometry.x,
        size=gdf['versos'],
        color_discrete_sequence=["red"],
        opacity=0.5,
        hover_name="ciutat",
        hover_data={"versos": True, "poetes": False},
        title="Mapa de Versos"
        )
    fig_versos.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=5.5,
        mapbox_center={"lat": 39.5, "lon": 2.5},
        height=800
        )
    iplot(fig_versos)
    fig_versos.write_html(f'{usb}/corpora/{corpus}/etiquetat/svg/mapa_versos.html')
    fig_versos.write_image(f'{usb}/corpora/{corpus}/etiquetat/svg/mapa_versos.svg')


def mapa_static(geojson):
    # Converteix el sistema de coordenades a WGS84 (EPSG:4326)
    gdf = geojson.to_crs(epsg=4326)

    # Mapa per autors
    fig, ax = plt.subplots(figsize=(15, 10))
    gdf.plot(
        ax=ax,
        marker='o',
        color='blue',
        markersize=gdf['poetes'] * 10,  # Adjust marker size based on 'poetes'
        alpha=0.5,
        label="Autors"
    )

    ctx.add_basemap(ax, crs=gdf.crs.to_string(), source=ctx.providers.CartoDB.PositronNoLabels, zoom=8)
    ax.axis('off')  # Remove axes for a cleaner look
    plt.savefig(f'{usb}/corpora/{corpus}/etiquetat/svg/mapa_autors_static.svg', bbox_inches='tight', dpi=600)
    plt.close()

    # Mapa per versos
    fig, ax = plt.subplots(figsize=(15, 10))
    gdf.plot(
        ax=ax,
        marker='o',
        color='red',
        markersize=gdf['versos'] * 0.05,  # Adjust marker size based on 'versos'
        alpha=0.5,
        edgecolor='none',  # Remove marker perimeter
        label="Versos"
    )
    ctx.add_basemap(ax, crs=gdf.crs.to_string(), source=ctx.providers.CartoDB.PositronNoLabels, zoom=8)
    ax.axis('off')  # Remove axes for a cleaner look
    plt.savefig(f'{usb}/corpora/{corpus}/etiquetat/svg/mapa_versos_static.svg', bbox_inches='tight', dpi=600)
    plt.close()



def dialectes(df):
    df = df[['name', 'dialect', 'versos']]

    # Per a cada dialecte quantifica quants autors i quants versos hi ha
    new_df = df.groupby('dialect').agg({'name': 'count', 'versos': 'sum'}).reset_index()
    new_df.columns = ['dialect', 'autors', 'versos']

    # Gràfic autors per dialecte
    total_autors = new_df['autors'].sum()
    fig_autors = go.Figure()
    fig_autors.add_trace(go.Bar(
        x=new_df['dialect'],
        y=new_df['autors'],
        marker_color='blue',
        opacity=0.5,
        text=[f'{v / total_autors * 100:.1f}%' for v in new_df['autors']],
        textposition='outside'
        ))
    fig_autors.update_layout(
        title="Autors per Dialecte",
        xaxis_title="Dialecte",
        yaxis_title="Nombre d'Autors",
        xaxis=dict(tickangle=45),
        template="plotly_white"
        )

    iplot(fig_autors)
    fig_autors.write_html(f'{usb}/corpora/{corpus}/etiquetat/svg/dialecte_a.html')

    # Gràfic versos per dialecte
    total_versos = new_df['versos'].sum()
    fig_versos = go.Figure()
    fig_versos.add_trace(go.Bar(
        x=new_df['dialect'],
        y=new_df['versos'],
        marker_color='red',
        opacity=0.5,
        text=[f'{v / total_versos * 100:.1f}%' for v in new_df['versos']],
        textposition='outside'
        ))
    fig_versos.update_layout(
        title="Versos per Dialecte",
        xaxis_title="Dialecte",
        yaxis_title="Nombre de Versos",
        xaxis=dict(tickangle=45),
        template="plotly_white"
        )

    iplot(fig_versos)
    fig_versos.write_html(f'{usb}/corpora/{corpus}/etiquetat/svg/dialecte_v.html')

    plt.figure(figsize=(6, 6))
    plt.bar(new_df['dialect'], new_df['autors'], color='blue', alpha=0.5)
    plt.xticks(rotation=45)
    for i, v in enumerate(new_df['autors']):
        plt.text(i, v + 0.5, f'{v / total_autors * 100:.1f}%', ha='center', va='bottom', color='gray', alpha=0.8)
    plt.savefig(f'{usb}/corpora/{corpus}/etiquetat/svg/dialecte_a.svg', bbox_inches='tight', dpi=600)
    plt.close()

    plt.figure(figsize=(6, 6))
    plt.bar(new_df['dialect'], new_df['versos'], color='red', alpha=0.5)
    plt.xticks(rotation=45)
    for i, v in enumerate(new_df['versos']):
        plt.text(i, v + 0.5, f'{v / total_versos * 100:.1f}%', ha='center', va='bottom', color='gray', alpha=0.8)
    plt.savefig(f'{usb}/corpora/{corpus}/etiquetat/svg/dialecte_v.svg', bbox_inches='tight', dpi=600)
    plt.close()


    return new_df


def generes(df):
    df = df[['name', 'gender', 'versos']]

    # Ensure df is a copy, not a view
    df = df.copy()

    df['gender'] = df['gender'].astype(str)
    # Perform the operation
    df.loc[:, 'gender'] = df['gender'].replace({'0': 'home', '1': 'dona', '2': 'altres'})

    # Per a cada gènere quantifica quants autors i quants versos hi ha
    new_df = df.groupby('gender').agg({'name': 'count', 'versos': 'sum'}).reset_index()
    new_df.columns = ['gender', 'autors', 'versos']

    # Gràfic autors per gènere
    total_autors = new_df['autors'].sum()
    fig_autors = go.Figure()
    fig_autors.add_trace(go.Bar(
        x=new_df['gender'],
        y=new_df['autors'],
        marker_color='blue',
        opacity=0.5,
        text=[f'{v / total_autors * 100:.1f}%' for v in new_df['autors']],
        textposition='outside'
        ))
    fig_autors.update_layout(
        title="Autors per Gènere",
        xaxis_title="Gènere",
        yaxis_title="Nombre d'Autors",
        xaxis=dict(tickangle=45),
        template="plotly_white"
        )

    iplot(fig_autors)
    fig_autors.write_html(f'{usb}/corpora/{corpus}/etiquetat/svg/genere_a.html')

    # Gràfic versos per gènere
    total_versos = new_df['versos'].sum()
    fig_versos = go.Figure()
    fig_versos.add_trace(go.Bar(
        x=new_df['gender'],
        y=new_df['versos'],
        marker_color='red',
        opacity=0.5,
        text=[f'{v / total_versos * 100:.1f}%' for v in new_df['versos']],
        textposition='outside'
        ))
    fig_versos.update_layout(
        title="Versos per Gènere",
        xaxis_title="Gènere",
        yaxis_title="Nombre de Versos",
        xaxis=dict(tickangle=45),
        template="plotly_white"
        )

    iplot(fig_versos)
    fig_versos.write_html(f'{usb}/corpora/{corpus}/etiquetat/svg/genere_v.html')

    plt.figure(figsize=(6, 6))
    plt.bar(new_df['gender'], new_df['autors'], color='blue', alpha=0.5)
    plt.xticks(rotation=45)
    for i, v in enumerate(new_df['autors']):
        plt.text(i, v + 0.5, f'{v / total_autors * 100:.1f}%', ha='center', va='bottom', color='gray', alpha=0.8)
    plt.savefig(f'{usb}/corpora/{corpus}/etiquetat/svg/genere_a.svg', bbox_inches='tight', dpi=600)
    plt.close()

    plt.figure(figsize=(6, 6))
    plt.bar(new_df['gender'], new_df['versos'], color='red', alpha=0.5)
    plt.xticks(rotation=45)
    for i, v in enumerate(new_df['versos']):
        plt.text(i, v + 0.5, f'{v / total_versos * 100:.1f}%', ha='center', va='bottom', color='gray', alpha=0.8)
    plt.savefig(f'{usb}/corpora/{corpus}/etiquetat/svg/genere_v.svg', bbox_inches='tight', dpi=600)
    plt.close()

    return new_df


def anys(df):
    df = df[['name', 'born_date', 'death_date', 'versos']]

    # Ensure df is a copy, not a view
    df = df.copy()

    # Elimina els autors sense data de naixement
    df = df.dropna(subset=['born_date'])
    # Perform the operation
    df.loc[:, 'decade'] = (df['born_date'] // 10) * 10
    # Elimina els autors sense data de naixement
    df = df[df['decade'] != 0]

    # Per a cada dècada quantifica quants autors i quants versos hi ha
    new_df = df.groupby('decade').agg({'name': 'count', 'versos': 'sum'}).reset_index()

    new_df.columns = ['decade', 'autors', 'versos']

    # Calcula el percentatge d'autors i de versos que representen cada dècada
    new_df['autors_rel'] = new_df['autors'] / new_df['autors'].sum() * 100
    new_df['versos_rel'] = new_df['versos'] / new_df['versos'].sum() * 100

    # Gràfic autors per dècada
    fig_autors = go.Figure()
    fig_autors.add_trace(go.Bar(
        x=new_df['decade'],
        y=new_df['autors'],
        marker_color='blue',
        opacity=0.5,
        text=[f'{v:.1f}%' for v in new_df['autors_rel']],
        textposition='outside'
        ))
    fig_autors.update_layout(
        title="Autors per Dècada",
        xaxis_title="Dècada",
        yaxis_title="Nombre d'Autors",
        xaxis=dict(tickangle=45),
        template="plotly_white"
        )

    iplot(fig_autors)
    fig_autors.write_html(f'{usb}/corpora/{corpus}/etiquetat/svg/decade_a.html')

    # Gràfic versos per dècada
    fig_versos = go.Figure()
    fig_versos.add_trace(go.Bar(
        x=new_df['decade'],
        y=new_df['versos'],
        marker_color='red',
        opacity=0.5,
        text=[f'{v:.1f}%' for v in new_df['versos_rel']],
        textposition='outside'
        ))
    fig_versos.update_layout(
        title="Versos per Dècada",
        xaxis_title="Dècada",
        yaxis_title="Nombre de Versos",
        xaxis=dict(tickangle=45),
        template="plotly_white"
        )

    iplot(fig_versos)
    fig_versos.write_html(f'{usb}/corpora/{corpus}/etiquetat/svg/decade_v.html')

    # Línia del temps dels autors
    df['death_date'] = df['death_date'].fillna(2025)
    df['life_duration'] = (df['death_date'] - df['born_date']).fillna(0)
    df = df.sort_values(by=['born_date'], ascending=False)

    fig_timeline = go.Figure()
    for _, row in df.iterrows():
        fig_timeline.add_trace(go.Scatter(
            x=[row['born_date'], row['death_date']],
            y=[row['name'], row['name']],
            mode='lines+markers',
            line=dict(color='blue', width=2),
            opacity=0.5,
            marker=dict(size=8),
            name=row['name']
            ))
    fig_timeline.update_layout(
        title="Línia del Temps dels Autors",
        xaxis_title="Any",
        yaxis_title="Autors",
        xaxis=dict(tickmode='linear', dtick=5, range=[1845, 2030]),
        template="plotly_white",
        height=800
        )

    iplot(fig_timeline)
    fig_timeline.write_html(f'{usb}/corpora/{corpus}/etiquetat/svg/linia_temps.html')
    fig_timeline.write_image(f'{usb}/corpora/{corpus}/etiquetat/svg/linia_temps.svg')

    plt.figure(figsize=(6, 6))
    plt.bar(new_df['decade'], new_df['autors'], color='blue', alpha=0.5)
    plt.xticks(rotation=45)
    plt.savefig(f'{usb}/corpora/{corpus}/etiquetat/svg/decade_a.svg')
    plt.close()

    plt.figure(figsize=(6, 6))
    plt.bar(new_df['decade'], new_df['versos'], color='red', alpha=0.5)
    plt.xticks(rotation=45)
    plt.savefig(f'{usb}/corpora/{corpus}/etiquetat/svg/decade_v.svg', bbox_inches='tight', dpi=600)
    plt.close()

    # Genera un any de producció per a cada autor. Per obtenir-lo es fa la mitjana entre la data de naixement i la de mort
    total_versos = df['versos'].sum()
    # Elimina els autors sense data de naixement
    df = df.dropna(subset=['born_date'])
    # Els autors sense data de mort se'ls assigna el 2025
    df['death_date'] = df['death_date'].fillna(2025)

    # Calcula l'any de producció
    df['produccio'] = (df['born_date'] + df['death_date']) / 2

    # Dècades de producció
    df['prod_decade'] = (df['produccio'] // 10) * 10

    df = df.groupby('decade').agg({'name': 'count', 'versos': 'sum'}).reset_index()

    # Plot dècades de producció
    fig_prod = go.Figure()
    fig_prod.add_trace(go.Bar(
        x=df['prod_decade'],
        y=df['versos'],
        marker_color='green',
        opacity=0.5,
        text=[f'{v / total_versos * 100:.1f}%' for v in df['versos']],
        textposition='outside'
    ))
    fig_prod.update_layout(
        title="Producció per dècada",
        xaxis_title="Dècada",
        yaxis_title="Nombre de Versos",
        xaxis=dict(tickangle=45),
        template="plotly_white"
    )
    fig_prod.write_html(f'{usb}/corpora/{corpus}/etiquetat/svg/prod_decade.html')
    iplot(fig_prod)

    print(df['prod_decade'])
    plt.figure(figsize=(6, 6))
    plt.bar(df['prod_decade'], df['versos'], color='green', alpha=0.5)
    plt.xticks(rotation=45)
    plt.savefig(f'{usb}/corpora/{corpus}/etiquetat/svg/prod_decade.svg', bbox_inches='tight', dpi=600)
    plt.close()

    return new_df


def font(df):
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
    # df = df.dropna(subset=['font'])

    # Per a cada font quantifica quants autors i quants versos hi ha
    new_df = df.groupby('font').agg({'name': 'count', 'versos': 'sum'}).reset_index()
    new_df.columns = ['font', 'autors', 'versos']

    new_df['font'] = new_df['font'].replace({'Corpus Textual Informatitzat de la Llengua Catalana': 'CTILC',
                                             'Corpus Literari Digital de la Càtedra Màrius Torres': 'CMT',
                                             "Donatiu de l'autor o curador": "donatiu", 'Llibre electrònic': 'ebook'})

    total_autors = new_df['autors'].sum()
    fig_autors = go.Figure()
    fig_autors.add_trace(go.Bar(
        x=new_df['font'],
        y=new_df['autors'],
        marker_color='blue',
        opacity=0.5,
        text=[f'{v / total_autors * 100:.1f}%' for v in new_df['autors']],
        textposition='outside'
        ))
    fig_autors.update_layout(
        title="Autors per Font",
        xaxis_title="Font",
        yaxis_title="Nombre d'Autors",
        xaxis=dict(tickangle=45),
        template="plotly_white"
        )
    fig_autors.write_html(f'{usb}/corpora/{corpus}/etiquetat/svg/font_a.html')

    # Gràfic versos per font
    total_versos = new_df['versos'].sum()
    fig_versos = go.Figure()
    fig_versos.add_trace(go.Bar(
        x=new_df['font'],
        y=new_df['versos'],
        marker_color='red',
        opacity=0.5,
        text=[f'{v / total_versos * 100:.1f}%' for v in new_df['versos']],
        textposition='outside'
        ))
    fig_versos.update_layout(
        title="Versos per Font",
        xaxis_title="Font",
        yaxis_title="Nombre de Versos",
        xaxis=dict(tickangle=45),
        template="plotly_white"
        )
    fig_versos.write_html(f'{usb}/corpora/{corpus}/etiquetat/svg/font_v.html')



    iplot(fig_autors)
    iplot(fig_versos)

    plt.figure(figsize=(6, 6))
    plt.bar(new_df['font'], new_df['autors'], color='blue', alpha=0.5)
    plt.xticks(rotation=45)
    for i, v in enumerate(new_df['autors']):
        plt.text(i, v + 0.5, f'{v / total_autors * 100:.1f}%', ha='center', va='bottom', color='gray', alpha=0.8)
    plt.savefig(f'{usb}/corpora/{corpus}/etiquetat/svg/font_a.svg', bbox_inches='tight', dpi=600)
    plt.close()

    plt.figure(figsize=(6, 6))
    plt.bar(new_df['font'], new_df['versos'], color='red', alpha=0.5)
    plt.xticks(rotation=45)
    for i, v in enumerate(new_df['versos']):
        plt.text(i, v + 0.5, f'{v / total_versos * 100:.1f}%', ha='center', va='bottom', color='gray', alpha=0.8)
    plt.savefig(f'{usb}/corpora/{corpus}/etiquetat/svg/font_v.svg', bbox_inches='tight', dpi=600)
    plt.close()

    return new_df




if __name__ == '__main__':
    # Executa les funcions
    corpus = 'actual'
    usb = getUSB()
    data = pd.read_csv(f'{usb}/corpora/{corpus}/etiquetat/{corpus}.csv', encoding='utf-8', lineterminator='\n', sep=';')
    desctiptives(data, corpus)
    # Genera el mapa
    path = f'{usb}/corpora/{corpus}/etiquetat/svg/mapa.geojson'
    # Llegeix les dades del fitxer GeoJSON
    gdf = gpd.read_file(path)

    #mapa_dinamic(dgf)

    #mapa_static(gdf)
    metadades = pd.read_excel(f'{usb}/corpora/{corpus}/etiquetat/xlsx/metadades_autors.xlsx')
    # Genera els gràfics
    #dialectes(metadades)
    #generes(metadades)
    anys(metadades)
    #font(metadades)

