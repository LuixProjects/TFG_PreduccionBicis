from itertools import compress

import pandas

from Backend.Auxiliares import auxiliar_tiempo


#Clase encargada de realizar consultas estándares a los datos.

class Filtrador:

    def __init__(self,datos:pandas.DataFrame, uTemporal:int):
        self.datos = datos#Los datos deberán de estar en formato: filas -> utemporal columnas -> estaciones
        self.uTemporal = uTemporal#Se debe de tener en cuenta que podemos trabajar con datos con distinta frecuencia al delta time.

    #Función encargada de obtener una lista de estaciones que cumplan la condición de que estén por encima de un valor
    #mas de X veces al día.
    #Nota: Para realizar “averiguar cuantas estaciones están por encima del 90% más de un 10% de un día” se deberá de
    #cargar las ocupaciones relativas y calcular segun el delta cuantas peticiones son un día.
    def consultarEstacionesSuperioresAUnValor(self, valor:int, veces:int, dia:int):

        index_dia_inicio,index_dia_final = auxiliar_tiempo.diaToDelta(dia, dia, self.uTemporal)
        #Obtenemos el día deseado.
        filtradoDia = self.datos.loc[(self.datos[self.datos.columns[0]].between(index_dia_inicio,index_dia_final))].iloc[:,1:]#No nos quedamos con las horas.
        numeroPeticiones = filtradoDia.shape[0]
        #Obtenemos La matriz de valores que cumplen la condicion
        filtradoValor = filtradoDia >= valor
        #Para que se cumpla la condición de frecuencia, calculamos el porcentaje.
        porcentajeNecesario = numeroPeticiones * veces / 100
        #Realizamos los calculos.
        listaCondicion = (filtradoValor.sum() > porcentajeNecesario).to_list() #Lista de las estaciones que cumplen la condicion.
        listaIndices = list(compress(range(len(listaCondicion)), listaCondicion))#Lista de indices que cumplen una condicion
        return listaIndices

    #Función que devuelve las horas en las que hay un porcentaje de estaciones superiores o iguales a un valor.
    #Consultar si esto lo filtro por día o no.
    #Considerando que no se filtra por día.
    def consultarHorasEstacionesSuperioresAUnValor(self,porcentajeEstaciones,valor):

        datosSinUTemp = self.datos.iloc[:,1:]
        #Obtenemos una matriz booleana con los valores que cumplan la condición.
        filtradoValor = datosSinUTemp >= valor
        #Sumamos por fila.
        sumaFila = filtradoValor.sum(axis=1)
        #Calculamos el número de veces que necesitamos para tomar una hora.
        nEstaciones = datosSinUTemp.shape[1]
        frecuenciaMinima = porcentajeEstaciones * nEstaciones/100
        listaCondicion = (sumaFila >= frecuenciaMinima).to_list()
        listaIndices = list(compress(range(len(listaCondicion)), listaCondicion))
        return listaIndices

    #Función que devuelve el porcentaje del tiempo donde las estaciones de la lista de estaciones se encuentran superiores
    # a un valor.
    #Considerando que no se filtra por día.
    def consultarPorcentajeTiempoEstacionSuperiorAUnValor(self,listaEstaciones:list[int],valor):
        datosSinUTemp = self.datos.iloc[:, 1:].iloc[:,listaEstaciones]#Filtramos las estaciones que querramos.
        # Obtenemos una matriz booleana con los valores que cumplan la condición.
        filtradoValor = datosSinUTemp >= valor
        #Vamos a comprobar que TODAS las estaciones son true ( Es decir, cumplen el filtradoValor).
        listaTemporalCondicion = filtradoValor.sum(axis=1) == len(listaEstaciones)

        return listaTemporalCondicion.sum() * 100 / len(listaTemporalCondicion)

