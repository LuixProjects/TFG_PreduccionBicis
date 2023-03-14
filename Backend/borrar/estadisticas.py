from datetime  import datetime
from random  import seed, random

import pandas as pd
from sqlalchemy  import create_engine

import numpy as np

import matplotlib.pyplot as plt
from Backend import Constantes
from Backend.EstructurasDatos.data_matrix import Desplazamientos_matrix


class Estadisticas:

    def __init__(self):
        seed(datetime.now())
    # No se muy bien como tiene que quedar el histograma.
    def generarHistogramaDesplazamientos(self, matrizDesplazamientos: Desplazamientos_matrix, dias: int):
        listaMedia = self.__peticionesMediasHora(matrizDesplazamientos, dias)
        horasDia = list(range(0, 24))

        fig = plt.figure()
        ax = fig.add_axes([0, 0, 1, 1])
        ax.bar(horasDia, listaMedia)
        self.simularDatosEstadisticos(1,matrizDesplazamientos)

        plt.show()


    def generarHistogramaDiario(self,matrizOcupacion:pd.DataFrame ,estacion:int,dia:int):
        listaMedia = self.ocupacionEstacionDiario(matrizOcupacion,estacion,dia)
        horasDia = list(range(0, 24))

        fig = plt.figure()
        ax = fig.add_axes([0, 0, 1, 1])
        ax.bar(horasDia, listaMedia)

        plt.show()

    def generarHistogramaOcupacionesDiarias(self,matrizOcupacion:pd.DataFrame ,dia:int):

        nEstaciones = matrizOcupacion.shape[1] -1
        listaHoras = np.array([0]*24)
        for i in range(nEstaciones):
            listaHoras = listaHoras + np.array(self.ocupacionEstacionDiario(matrizOcupacion,i,dia))
        horasDia = list(range(0, 24))

        fig = plt.figure()
        ax = fig.add_axes([0, 0, 1, 1])
        ax.bar(horasDia, listaHoras)

        plt.show()

    #Función que devuelve un array de 0--nEstaciones con la ocupacion media.
    def histogramaRuleta(self,matrizOcupacion:pd.DataFrame, dia):

        engine = create_engine('sqlite://', echo=False)
        matrizOcupacion.to_sql('ocupaciones', con=engine)

        TiempoPrincipioDia = (((60 / Constantes.DELTA_TIME) * 24) * dia) + 1
        TiempoFinalDia = TiempoPrincipioDia + ((60 / Constantes.DELTA_TIME) * 24) - 1

        ocupacion = engine.execute("Select * from ocupaciones Where hora between " + str(TiempoPrincipioDia) + " and " + str(TiempoFinalDia)).fetchall()

        ocupacion = np.array(ocupacion)
        np.delete(ocupacion, [0,1], 1)




    #Devuelve la ocupacion de una estacion en concreto durante un dia 0-n
    def ocupacionEstacionDiario(self, matrizOcupacion:pd.DataFrame ,estacion:int,dia:int):

        engine = create_engine('sqlite://', echo=False)
        matrizOcupacion.to_sql('ocupaciones', con=engine)

        TiempoPrincipioDia = (((60 / Constantes.DELTA_TIME) * 24) * dia) + 1
        TiempoFinalDia = TiempoPrincipioDia + ((60 / Constantes.DELTA_TIME) * 24) - 1

        ocupacion = engine.execute("Select hora,estacion" + str(estacion) +" from ocupaciones Where hora >= " + str(TiempoPrincipioDia) + " and hora <= " + str(TiempoFinalDia) ).fetchall()

        ##Como en ocupacion se repite las horas, me las tengo que ingeniar para quitar repetidos.

        horaPrevia = 0
        valorPrevio = 0

        i = 0
        z = 0
        contadorHoras = 0
        listaOcupacionHoras = [0]*24
        while i < (len(ocupacion)):#Para quitar ocupaciones duplicadas

            if ocupacion[i][0] == horaPrevia:

                if ocupacion[i][1] != valorPrevio: ##Si coincide la hora pero no el valor, significa que esta es la actualizacion buena, por tanto, elimino la anterior..
                    del ocupacion[(i-1)]

                    print("estoy : " + str(valorPrevio+1))
                    valorPrevio = ocupacion[i][1] #Actualizo el valor previo

                else:   ##Si no coincide, puedo eliminar esta
                    del ocupacion[i]

            else:
                print(str(i))
                horaPrevia = ocupacion[i][0]
                valorPrevio = ocupacion[i][1]
                i += 1
                z += 1

                listaOcupacionHoras[contadorHoras] += valorPrevio
                if  z == (60 / Constantes.DELTA_TIME):
                    contadorHoras += 1
                    z = 0

        np_ocupacion = (np.array(listaOcupacionHoras) / (60 / Constantes.DELTA_TIME))
        return np_ocupacion.tolist()


    def __peticionesMediasHora(self, matrizDesplazamientos: Desplazamientos_matrix, dias: int):
        peticionesMedias = np.array([0] * 24)
        for i in range(dias):  # Para cada dia
            listaHoras = self.__getPeticionesHora(matrizDesplazamientos,i)  # Para cada día obtengo un array con las peticiones en cada hora.
            peticionesMedias = peticionesMedias + np.array(listaHoras)
        return (peticionesMedias / dias).tolist()

    # Funcion que dado el dataset de desplazamientos y un día 0-23, devuelve un array de 24 posiciones con la suma total de peticiones en cada hora.
    #MAL.NO PUEDO MANEJAR ASI LOS DIAS, YA QUE LAS PETICIONES SON INDEPENDIENTES Y PUEDEN SER BASTANTE MAS QUE PETICIONES_POR_DIA , YA QUE ESO ES DE DELTA_5M
    def __getPeticionesHora(self, matrizDesplazamientos: Desplazamientos_matrix, dia: int):
        peticionesHora = [0] * 24

        nUtemporalesHora = 60 / Constantes.DELTA_TIME
        #Como las deltas son cada 5m :
        TiempoPrincipioDia = (((60 / Constantes.DELTA_TIME) * 24) * dia) + 1
        TiempoFinalDia = TiempoPrincipioDia + ((60 / Constantes.DELTA_TIME) * 24) - 1
        copia_Desplazamientos = matrizDesplazamientos.matrix.copy()

        engine = create_engine('sqlite://', echo=False)
        copia_Desplazamientos.to_sql('desplazamientos', con=engine)

        peticionesXuTemporal = engine.execute("Select sum(Cantidad_peticiones) from( SELECT * FROM desplazamientos  Where Utemporal Between " + str(TiempoPrincipioDia) + " and " + str(TiempoFinalDia)+") GROUP BY UTEMPORAL" ).fetchall()

        nUtemporalesXhora = len(peticionesXuTemporal) / 24
        contador = 0
        index = 0
        for i in range(len(peticionesXuTemporal)):
            print(index)
            print(i)
            peticionesHora[index] += peticionesXuTemporal[i][0]
            contador += 1
            if contador == nUtemporalesXhora:
                index += 1
                contador = 0

        return peticionesHora



    def simularDatosEstadisticos(self, dias: int, matrizDesplazamientos:Desplazamientos_matrix):

        DeltasPorHoras = 12
        arraymedias = self.__peticionesMediasHora(matrizDesplazamientos, dias)
        desplazamientos = matrizDesplazamientos.matrix
        nuevos_desp = []
        peticionesPorDelta = 2#?

        for num_dias in range(dias):#Para cada dia que se quiera simular.
            for num_horas in range(1,25):#Para cada hora del dia
                for delta in (range(int((60 / Constantes.DELTA_TIME)))):#Para cada delta
                    for i in range( peticionesPorDelta ):

                        indice = self.ruletaProporcional(arraymedias) #Obtenemos una peticion a la estacion
                        nuevos_desp.append((indice,delta))
                        print("indice:" + str(indice))

        return nuevos_desp
    # Dado una ruleta con pesos, devuelve un índice aleatorio, este algoritmo fue encontrado en el enlace de wikipedia:
    # https://en.wikipedia.org/wiki/Fitness_proportionate_selection dado que parece facil de entender y aplicar, aunque no es
    # el algoritmo inicial de la ruleta.

    def ruletaProporcional(self, pesos):  # Preguntar, esque esto me queda exactamente igual que mi método.

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
