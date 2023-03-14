import numpy as np
import pandas as pd
from sqlalchemy import create_engine

from Backend.Auxiliares import auxiliar_representacion, auxiliar_tiempo


class estadisticasOcupacionHorarias:

    def __init__(self, matrizOcupacionHoraria:pd.DataFrame, deltaTime:int):
        self.matrizOcupacionHoraria = matrizOcupacionHoraria
        self.nombreTiempo = matrizOcupacionHoraria.columns[0]
        self.engine = create_engine('sqlite://', echo=False)
        self.matrizOcupacionHoraria.to_sql('ocupacionesHoras', con=self.engine)
        self.deltaTime = deltaTime

    #Funcion dado una estacion y un rango de dias, muestra un histograma con los datos de ocupación media en varios dias.
    def HistogramaPorEstacion(self, estacion:int , dias:list[int]):
        lista_horas = self.__getOcupacionEstacion(estacion,dias)
        auxiliar_representacion.pintarHistograma(lista_horas, range(0, 24))

    #Función que dado un rango de dias muestra el histograma con las ocupaciones medias de cada día de todas las estaciones.
    def HistogramaOcupacionMedia(self,dias:list[int]):
        lista_estaciones = self.__getOcupacionTodasEstaciones(dias)
        n = self.matrizOcupacionHoraria.shape[1] - 1
        auxiliar_representacion.pintarHistograma(lista_estaciones, range(0, n))

    def HistogramaAcumulacion(self,estacion,dias:list[int]):
        lista_horas = np.array([0]*24)
        for i in range(len(dias)):
            lista_aux = self.__getOcupacionEstacion(estacion,[dias[i]])
            lista_horas = lista_horas + lista_aux
        auxiliar_representacion.pintarHistograma(lista_horas.tolist(), range(0, 24))

    #Función dado una estación y un dia determinado lo muestra en un histograma de lineas la trayectoria de la ocupación
    #del día, permitiendo comparar varias estaciones y varios días a la vez.
    #Estaciones-> Array de estaciones a comparar.
    #Dias -> Array que contiene los arrays de dias para realizar la comparación.
    #El array Estaciones y el Array de Días DEBEN de tener el mismo tamaño
    def HistogramaCompararEstaciones(self,estaciones:list[int],diasPorEstacion:list[list[int]]):

        listaHistogramas = [] #Array de los n histogramas.
        listaNombres = []
        for i in range(len(estaciones)):#Para cada estación conseguimos su histograma.
            listaHistogramas.append(self.__getOcupacionEstacion(estaciones[i],diasPorEstacion[i]))
            listaNombres.append("Estacion " + str(estaciones[i]) + " en los dias: " + str(diasPorEstacion[i]))

        auxiliar_representacion.pintarVariosHistogramas(listaHistogramas, listaNombres)

    #Función privada que realiza una consulta SQL para obtener las ocupaciones medias diarias de cada estación.
    def __getOcupacionTodasEstaciones(self,dias:list[int]):
        n = self.matrizOcupacionHoraria.shape[1] - 1
        lista_estaciones = np.array([0] * n)

        for dia in dias:
            index_inicio_dia, index_final_dia = auxiliar_tiempo.diaToDelta(dia, dia, self.deltaTime)
            peticionSQL = self.engine.execute(
                "Select *  FROM ocupacionesHoras Where " + self.nombreTiempo+" between " + str(index_inicio_dia) + " and " + str(index_final_dia)).fetchall()

            lista_estaciones = lista_estaciones + np.sum(np.array(peticionSQL)[:, 2:], axis=0) / 24

        return lista_estaciones / len(dias)

    #Función privada que realiza una consulta SQL para obtener las ocupaciones por horas de una estación indicada en un periodo
    #determinado.
    def __getOcupacionEstacion(self,estacion,dias:list[int]):

        lista_horas = np.array([0]*24)
        for dia in dias:
            index_inicio_dia, index_final_dia = auxiliar_tiempo.diaToDelta(dia, dia, self.deltaTime)
            peticionSQL = self.engine.execute("Select estacion"+ str(estacion) + " FROM ocupacionesHoras Where " + self.nombreTiempo+" between " +
                                              str(index_inicio_dia) + " and " + str(index_final_dia)).fetchall()
            lista_horas = lista_horas + np.transpose(np.array(peticionSQL))[0]

        lista_horas = lista_horas / len(dias)
        return lista_horas



