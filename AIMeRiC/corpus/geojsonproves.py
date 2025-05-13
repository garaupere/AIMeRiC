import matplotlib.pyplot as plt
import geopandas as gpd
import contextily as ctx

from AIMeRiC.corpus.modules.getUSB import getUSB

# Obre el fitxer geojson i llegeix el contingut.
usb = getUSB()
corpus = 'actual'
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
plt.legend()

# Guarda el mapa com a imatge
plt.savefig('mapa_autors.png', dpi=600, bbox_inches='tight')
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
plt.legend()

# Guarda el mapa com a imatge
plt.savefig('mapa_versos.png', dpi=600, bbox_inches='tight')