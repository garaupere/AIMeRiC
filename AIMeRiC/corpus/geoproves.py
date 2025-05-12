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
                try:
                    comarca = feature['@relations'][0]['reltags']['name:ca']
                except:
                    comarca = feature['name:ca']
                return geometry, feature, comarca



if __name__ == "__main__":
    #print(get_city('Campos'))

    # Carrega un geojson
    with open('modules/ppcc.geojson', 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    city = info_city('Pollença', geojson_data)
    print(city[0])
    print(city[1])
    print(city[2])

    # En un mapa dibuixa l'àrea de la ciutat
    # Mapa centrat en els Països Catalans
    m = folium.Map(location=[41.5, 1.5], zoom_start=7)
    # Afegeix l'àrea de la ciutat
    folium.GeoJson(city[0]).add_to(m)

    # Afegeix l'àrea de la comarca
    #folium.GeoJson(geojson_data).add_to(m)

    m.save('map.html')


# 3 columnes: ['city', 'count', 'coords']



