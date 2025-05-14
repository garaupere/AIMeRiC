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
    if ciutat != 'Selva':
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
    else:
        resultat = geocoder.geocode('Selva, Balearic Islands, Spain', country='Spain', state_code='IB', no_annotations='1')
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


if __name__ == "__main__":
    print(get_city('Selva'))
