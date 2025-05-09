import folium
from opencage.geocoder import OpenCageGeocode
import pandas as pd

def get_city(ciutat):
    API_KEY = '4049fae64f4042aeb9395f098dbd95d3'

    # Inicialitza el geocodificador
    geocoder = OpenCageGeocode(API_KEY)


    # Prepara un diccionari per a les dades
    dades = {'ciutat': [], 'latitud': [], 'longitud': []}

    # Obté les coordenades per a cada ciutat

    resultat = geocoder.geocode(ciutat, no_annotations='1')
    if resultat:
        # Agafa les coordenades del primer resultat
        coordenades = resultat[0]['geometry']
        dades['ciutat'].append(ciutat)
        dades['latitud'].append(coordenades['lat'])
        dades['longitud'].append(coordenades['lng'])
        #print(f"{ciutat}: {coordenades['lat']}, {coordenades['lng']}")
    else:
        print(f"No s'han trobat coordenades per a {ciutat}")

    return dades['latitud'][0], dades['longitud'][0]

if __name__ == "__main__":
    #print(get_city('Palma'))

    cities_df = pd.DataFrame({'ciutat': 'Alaró', 'poetes': 1, 'latitud': 39.7061528, 'longitud': 2.7907216}, index=[0])

    mapa = folium.Map(location=[39.5, 2.5], zoom_start=6)  # Centrat als Països Catalans

    # Afegir punts al mapa
    for index, row in cities_df.iterrows():
        folium.CircleMarker(
            location=(row['latitud'], row['longitud']),
            radius=row['poetes'] * 2,  # Escala proporcional al nombre de poetes
            popup=f"{row['ciutat']}: {row['poetes']} poetes",
            color="blue",
            fill=True,
            fill_color="blue"
        ).add_to(mapa)

    # Guardar el mapa com a fitxer HTML
    mapa.save("mapa.html")
