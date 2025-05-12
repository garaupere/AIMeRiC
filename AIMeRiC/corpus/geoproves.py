import json

import folium
from matplotlib import pyplot as plt
from opencage.geocoder import OpenCageGeocode
import pandas as pd


def get_city(ciutat):
    API_KEY = '4049fae64f4042aeb9395f098dbd95d3'

    # Inicialitza el geocodificador
    geocoder = OpenCageGeocode(API_KEY)

    # Prepara un diccionari per a les dades
    dades = {'ciutat': [], 'latitud': [], 'longitud': [], 'província': [], 'país': []}

    # Obté les coordenades per a cada ciutat

    resultat = geocoder.geocode(ciutat, continent='Europe', no_annotations='1')
    if resultat:
        for x in range(0, len(resultat)):
            if resultat[x]['components']['continent'] == 'Europe':
                coordenades = resultat[x]['geometry']
                dades['ciutat'].append(ciutat)
                dades['latitud'].append(coordenades['lat'])
                dades['longitud'].append(coordenades['lng'])
                components = resultat[x]['components']
                provincia = components.get('state', 'Desconeguda')
                pais = components.get('country', 'Desconegut')
                dades['província'].append(provincia)
                dades['país'].append(pais)
                # print(f"{ciutat}: {coordenades['lat']}, {coordenades['lng']}")
    return dades['latitud'][0], dades['longitud'][0], dades['província'][0], dades['país'][0]

def info_city(ciutat, geojson_data):
    # Extreu la info d'una ciutat a partir del geojson
    for feature in geojson_data['features']:
        if 'name:ca' in feature['properties']:
            if feature['properties']['name:ca'] == ciutat:
                geometry = feature['geometry']
                feature = feature['properties']
                return geometry, feature



if __name__ == "__main__":
    #print(get_city('Campos'))

    # Carrega un geojson
    with open('modules/ppcc2.geojson', 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    city = info_city('Barcelona', geojson_data)

    # Fes un mapa
    m = folium.Map(location=[city[0]['coordinates'][1], city[0]['coordinates'][0]], zoom_start=10)

    folium.Polygon(
        locations=city[0][0]['coordinates'][0],
        color='blue',
        fill=True,
        fill_opacity=0.5,
        popup=city[1]['name:ca']
    ).add_to(m)

    # Mostra el mapa
    m.save('mapa.html')




