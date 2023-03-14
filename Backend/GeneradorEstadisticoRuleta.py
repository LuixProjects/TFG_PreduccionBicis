from random import random

import numpy as np
import pandas as pd

import Constantes


class GeneradorEstadisticoRuleta:

    def GeneradorEstadisticoRuleta(self,matrizDesplazamientos:pd.DataFrame,deltaTime):
        self.desplazamientos = matrizDesplazamientos
        self.nEstaciones = matrizDesplazamientos.shape[1]-1
        self.tiempoDelta = deltaTime

    def simularDatosEstadisticos(self, dias: int):

        DeltaPorHoras = 60 / self.tiempoDelta

        for num_dias in range(dias):#Para cada dia que se quiera simular.

            for num_horas in range(1,25):#Para cada hora del dia
                num_peticiones = self.__getNumPeticiones(num_dias,num_horas)  #ConsultaSQL para determinar la cantidad de peticiones existente en una hora.

                for delta in DeltaPorHoras:#Para cada delta
                    ##coger_soltar = False#Variable booleana? que indentifica si la peticion es de cojer o soltar.
                    numPeticionesHoras = num_peticiones/DeltaPorHoras

                    for i in range(numPeticionesHoras):

                        if(datosDataFrame.iloc[i,2] == Constantes.PETICION_DEJAR_BICI):

                            indice = self.__ruletaProporcional(arraymedias)  # Obtenemos una peticion a la estacion
                            nuevos_desp.append((indice, delta))

                        else:
                            indice = self.__ruletaProporcional(arraymedias)  # Obtenemos una peticion a la estacion
                            nuevos_desp.append((indice, delta))

        return nuevos_desp

    # Dado una ruleta con pesos, devuelve un índice aleatorio, este algoritmo fue encontrado en el enlace de wikipedia:
    # https://en.wikipedia.org/wiki/Fitness_proportionate_selection dado que parece facil de entender y aplicar, aunque no es
    # el algoritmo inicial de la ruleta.

    def __ruletaProporcional(self, pesos):  # Preguntar, esque esto me queda exactamente igual que mi método.

        probab = []
        prob_anterior = 0.0
        suma_fitness = np.array(pesos).sum()

        for i in range(len(pesos)):  # Recorro todos los pesos para calcular las probabilidades combinadas
            valor = prob_anterior + (pesos[i] / suma_fitness)
            prob_anterior = valor
            probab.append(valor)

        randomNumber = random()  # Numero entre 0 e 1.

        j = 0
        indice = 0
        encontrado = False
        while j < len(pesos) and encontrado == False:

            if randomNumber < probab[j]:
                encontrado = True
                indice = j
            j += 1

        return indice

    #Función auxiliar que devuelve los indices de las unidades temporales correspondientes a un día y una hora seleccionada.
    #NOTA: El primer día y la primera hora -> 0.
    def __getIntervalo(self,dia:int,hora:int):

        #Indices que hacen referencia a la unidad temporal correspondiente al inicio y final de un día seleccionado.
        dia_inicial_index = Constantes.DELTA_TIME * (dia * 24) #Delta de inicio del día.

        #Teniendo las peticiones del día, ahora necesitamos extraer las peticiones que tiene la hora en cuestión.
        hora_inicial_index = dia_inicial_index + (hora * Constantes.DELTA_TIME)
        hora_final_index = hora_inicial_index + (Constantes.DELTA_TIME)
        #Teniendo los índices deseados podemos sacar la información que deseemos.
        return hora_inicial_index,hora_final_index

    #Función encargada de devolver el número de peticiones en un día y una hora.
    def __getNumPeticiones(self,dia:int,hora:int):
        hora_inicial_index,hora_final_index = self.__getIntervalo(dia,hora)
        return (self.desplazamientos.iloc[:, 3].isin(range(hora_inicial_index,hora_final_index+1))).sum()

    #Funcion que devuelve un pd.DataFrame con los datos que están en un día y hora determinado
    def __getDatos(self,dia:int,hora:int):
        hora_inicial_index,hora_final_index = self.__getIntervalo(dia,hora)
        return self.desplazamientos.matrix.iloc[hora_inicial_index:(hora_final_index+1),:]

    #Función que calcula las peticiones medias sobre varios días del periodo elegido en cada hora de cada estación.
    #El día menor deberá estar en la primera posición, ejemplo : dias -> [0,1,2,3]
    #cogerSoltar será true en el caso de que se quiera coger una bici, o false en caso de soltarla.
    def __calcularHistograma(self,dias:list[int],hora:int,cogerSoltar:bool):

        #Array de tamaño del número de estaciones
        histograma = [0] * self.nEstaciones

        #Bucle para recorrer los días a recoger

        for i in range(len(dias)):

            hora_inicial_index,hora_final_index=self.__getIntervalo(i,hora)
            data = self.desplazamientos.iloc[hora_inicial_index:hora_final_index,:]
            if(cogerSoltar == True):
                data = data[data.iloc[:, 2] == Constantes.PETICION_SOLICITAR_BICI]
            else:
                data = data[data.iloc[:, 2] == Constantes.PETICION_DEJAR_BICI]

            #Preguntar si hacerlo sobre la estacion origen de la peticion o la final.
            #Este pseudo no tiene en cuenta que una peticion pueda contener 2 movimientos.

            for desplazamiento in range(len())


