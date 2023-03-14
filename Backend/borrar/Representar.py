import branca
import numpy as np
import pandas as pd

import plotly.express as px
from folium.plugins import HeatMap, HeatMapWithTime
import folium
import plotly.graph_objects as go
from Backend.EstructurasDatos import data_matrix
from Backend.Auxiliares import auxiliaresCalculos
from Backend.Voronoi import VoronoiPersonalizado
from selenium import webdriver
import os
import moviepy.video.io.ImageSequenceClip
import branca.colormap as cm
from mlxtend.preprocessing import minmax_scaling

#Clase para la representacion con folium
class Representar:

    def __init__(self,coordenadas:np.ndarray):
        self.ocupaciones = pd.DataFrame()
        self.coordenadas = pd.DataFrame(coordenadas,columns=["Estacion","Lat","Long"])
        self.nombreMapa = ""
        self.mapa = folium.Map([coordenadas[172][1],coordenadas[172][2]], zoom_start=13)


    def cargarDatos(self, ocupaciones:pd.DataFrame,nombreMapa:str):
        self.ocupaciones=ocupaciones
        self.nombreMapa = nombreMapa

    #Función que representa un mapa con círculos que representan las estaciones.
    def representacionBasica(self):

        for i in range(len(self.coordenadas)):
            self.__dibujarCirculo(self.coordenadas.loc[i][1],self.coordenadas.loc[i][2],50,"red","Estacion "+ str(i))
        self.mapa.save("mapa.html")

    #Función auxiliar que representa un circulo dado sus coordenadas, el radio y el color deseado.
    def __dibujarCirculo(self,lat,long,radio,color,label="error"):
        folium.Circle(
            radius=radio,
            location=[lat,long],
            color=color,
            fill=True
        ).add_child(folium.Popup(label)).add_to(self.mapa)

    def representarHeatmap(self,instante,fichero:str):
        datos = self.coordenadas.iloc[:,[1,2]].to_numpy()
        if not self.ocupaciones.empty:
            ##Cargar pesos
            pesos = auxiliaresCalculos.realizarMediaPesos(self.ocupaciones.iloc[instante, :].values.tolist())
            datos = np.c_[datos, pesos]
        #Representar en el mapa.
        HeatMap(datos).add_to(self.mapa)
        self.mapa.save(fichero + ".html")

    #Función de pruba para mostrar un histograma con leyenda.
    def representarHeatmapConLeyenda(self,instante,fichero:str,max_val=0,min_val=0):
        datos = self.coordenadas.iloc[:, [1, 2]].to_numpy()


        ##Cargar pesos
        pesos = self.ocupaciones.iloc[instante, :].values.tolist()
        datos = np.c_[datos, pesos]
        datos = np.c_[datos, list(range(len(pesos)))]
        datos = pd.DataFrame(datos)

        datos.columns= ["Latitud","Longitud","Medida","Estacion"]

        # Representar en el mapa.
        fig = px.density_mapbox(datos, lat="Latitud", lon="Longitud", z="Medida", radius=14,
                                center=dict(lat=self.coordenadas.iloc[172][1], lon=self.coordenadas.iloc[172][2]), zoom=12,
                                mapbox_style="stamen-terrain",
                                hover_data={'Prueba': True})


        fig.show()


    def representarHeatmapCapas(self, instante, matrices: data_matrix):#No funciona ahora mismo.

        for i in matrices:
            datos = self.coordenadas.iloc[:,[1,2]].to_numpy()
            if not matrices[i].matrix.empty:
            ##Cargar pesos
                pesos = auxiliaresCalculos.realizarMediaPesos(matrices[i].matrix.iloc[instante, :].values.tolist())
                datos = np.c_[datos, pesos]
            #Representar en el mapa.
            feature_group = folium.FeatureGroup(name=i)
            feature_group.add_child(HeatMap(datos))
            self.mapa.add_child(feature_group)
        self.mapa.add_child(folium.LayerControl())
        self.mapa.save("mapa.html")

    def videoHeatmap(self):
        listaDatos = []
        datos = self.coordenadas.iloc[:, [1, 2]].to_numpy()
        for i in range(self.coordenadas.shape[0]):
            pesos = auxiliaresCalculos.realizarMediaPesos(self.ocupaciones.iloc[i, :].values.tolist())
            datos_conpeso = np.c_[datos, pesos]
            listaDatos.append(datos_conpeso)
        HeatMapWithTime(listaDatos,index=list(range(0,(datos.shape[0])))).add_to(self.mapa)
        self.mapa.save("mapa.html")
#[datos.tolist()]
#HeatMapWithTime([datos.tolist()], index=[0]).add_to(self.mapa)
    def crearVideo(self,indice_inicio,indice_final):

        DRIVER = 'cromedriver'
        driver = webdriver.Chrome(DRIVER)
        driver.set_window_size(1000, 9000)  # choose a resolution
        driver.get("http://localhost:63342/TFG/mapa.html")

        for i in range(indice_inicio,indice_final+1):#Para cada tiempo t.
            self.mapa = folium.Map([self.coordenadas.iloc[172][1], self.coordenadas.iloc[172][2]],zoom_start=13)  # Limpio mapa.
            ##self.representacionVoronoi(index=i)
            self.representacionBasica()
            self.representarHeatmap(i,"mapa")
            driver.refresh()
            screenshot = driver.save_screenshot('Fotos/imagen'+ str(i) +'.png')

        image_folder = 'Fotos'
        fps = 1

        image_files = [os.path.join(image_folder, img)
                       for img in os.listdir(image_folder)
                       if img.endswith(".png")]
        clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(image_files, fps=fps)
        clip.write_videofile("my_video.mp4")

        driver.quit()

    #Función que representa un mapa de Voronoi.
    def representacionVoronoi(self,index=0):

        for i in range(len(self.coordenadas)):
            self.__dibujarCirculo(self.coordenadas.loc[i][1],self.coordenadas.loc[i][2],5,"red")

        vor = VoronoiPersonalizado(self.coordenadas.iloc[:, [1, 2]],self.mapa)
        vor.calcularVoronoi()

        if not self.ocupaciones.empty:
            vor.cargarColoresOcupacion(self.ocupaciones,index)
        vor.representarVoronoi()

        self.mapa.save("mapa.html")






#folium.Circle(radius=50,location=(37.41292,-5.98891),color = "blue")