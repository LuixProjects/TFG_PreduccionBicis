import numpy as np
import pandas as pd

from sqlalchemy import create_engine

from Backend import Constantes
from Backend.Auxiliares import auxiliar_representacion, auxiliar_tiempo


#En proceso de eliminación.
class estadisticasOcupacion:

    def __init__(self, matrizOcupacion:pd.DataFrame):
        self.matrizOcupacion = matrizOcupacion
        self.engine = create_engine('sqlite://', echo=False)
        self.matrizOcupacion.to_sql('ocupaciones', con=self.engine)

    def HistogramaPorEstacion(self,estacion:int,dia:int):
        lista_horas = self.__getOcupacionPorHora(estacion,dia,dia)
        auxiliar_representacion.pintarHistograma(lista_horas, range(0, 24))

    def HistogramaPorDia(self,dia):
        estaciones = self.__getOcupacionDiaria(dia,dia)
        auxiliar_representacion.pintarHistograma(estaciones, range(0, self.matrizOcupacion.shape[1] - 1))

    def __getOcupacionDiaria(self,diaComienzo:int,diaFinal:int):
        tupla_dia = auxiliar_tiempo.diaToDelta(diaComienzo, diaFinal)
        peticionSQL = self.engine.execute(
            "Select *  from ocupaciones Where hora between " + str(
                tupla_dia[0]) + " and " + str(tupla_dia[1])).fetchall()
        np_peticiones = np.delete(np.array(peticionSQL),[0,1],1)
        np_estaciones = np.sum(np_peticiones,axis=0)/len(peticionSQL)
        return np_estaciones.tolist()

    #Funcion que devuelve la ocupacion media por horas de la estacion seleccionada en el espacio temporal de
    # diaComienzo-diaFinal incluyendo dicho dia final. (es decir 0,0 devolvería el día 0 y 0,1 devolvería ambos).
    #NOTA: SOLO FUNCIONA CON UN DIA YA QUE VA AGREGANDO AL ARRAY DE 60/DELTATIME.
    #NOTA: PARA QUE FUNCIONE BIEN DEBE TENER ALMENOS LAS 24H PETICIONES.
    def __getOcupacionPorHora(self,estacion:int,diaComienzo:int,diaFinal:int):

        tupla_dia = auxiliar_tiempo.diaToDelta(diaComienzo, diaFinal)

        peticionSQL = self.engine.execute("Select estacion"+ str(estacion) + " from ocupaciones Where hora between " + str(tupla_dia[0]) + " and " + str(tupla_dia[1])).fetchall()

        sumatorio = 0
        lista_Horas = []
        contador = 1
        for i in range(len(peticionSQL)):
            sumatorio += peticionSQL[i][0]
            contador += 1
            if contador == (60 / Constantes.DELTA_TIME):
                lista_Horas.append(sumatorio)
                sumatorio = 0
                contador = 0
        lista_Horas = np.array(lista_Horas) / (60 / Constantes.DELTA_TIME)
        return lista_Horas.tolist()



