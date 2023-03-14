import folium
import numpy as np
import pandas as pd
from geovoronoi import voronoi_regions_from_coords
from shapely.geometry import Polygon

from Backend.EstructurasDatos.Poligonos import Poligonos
import seaborn as sns

class VoronoiPersonalizado:

    def __init__(self, coordenadas, mapa: folium):
        self.coordenadas = coordenadas
        self.mapa = mapa
        self.arrayPoligonos: list[Poligonos] = []

    #Funcion que calcula las regiones de Voronoi
    def calcularVoronoi(self):
        maxLat = self.coordenadas.iloc[:, 0].max()
        maxLong = self.coordenadas.iloc[:, 1].max()
        minLat = self.coordenadas.iloc[:, 0].min()
        minLong = self.coordenadas.iloc[:, 1].min()

        folium.Polygon([(minLat, maxLong), (maxLat, maxLong), (maxLat, minLong), (minLat, minLong)],
                       color="blue").add_to(self.mapa)

        region_polys, region_pts = voronoi_regions_from_coords(self.coordenadas.to_numpy(), geo_shape=Polygon(
            [(minLat, maxLong), (maxLat, maxLong), (maxLat, minLong), (minLat, minLong)]))
        for i in range(len(region_polys)):
            poligono = region_polys[i].boundary.coords[:]
            self.arrayPoligonos.append(Poligonos(region_pts[i], poligono))

            # folium.Polygon(poligono, color="blue", fill=True, fill_color="orange", fill_opacity=0.4).add_to(self.mapa)

    #Función que carga los colores para representarlo en un instante i de tiempo.

    #PREGUNTAR SI LOS COLORES LOS QUIERE CON RESPECTO AL TOTAL O LA HORA EN SÍ.
    def cargarColoresOcupacion(self,ocupaciones:pd.DataFrame,index):
        np_ocupaciones = np.array(ocupaciones)

        #array_indices_menorAmayor = np.argsort(np_ocupaciones)
        paleta = sns.color_palette("flare",len(np.unique(ocupaciones))).as_hex()
        valorMax = np_ocupaciones.max()
        for i in self.arrayPoligonos:
            valorPunto = ocupaciones.iloc[index,i.indicePunto][0]
            i.ocupacion = valorPunto
            i.color = paleta[round(valorPunto * (len(paleta)-1) / valorMax)]

    #Funcion encargada de representar el diagrama, haya o no colores
    def representarVoronoi(self):

        for i in self.arrayPoligonos:

            if i.color == None:
                folium.Polygon(i.poligono, color="blue", fill=False,popup=str("Estacion" + str(i.indicePunto))).add_to(self.mapa)
            else:
                folium.Polygon(i.poligono,color="black", fill=True, fill_color=i.color, fill_opacity=0.6,popup=str("Estacion" + str(i.indicePunto) +"\n" + "Ocupacion: " + str(i.ocupacion)) ).add_to(
                    self.mapa)
