import random

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import Backend.Constantes as Constantes
from Backend.Auxiliares import auxiliar_calculos_kilometros
from Backend.EstructurasDatos.BiciTransition import BiciTransition
from Backend.EstructurasDatos.data_matrix import Data_matrix, Desplazamientos_matrix, Ocupacion_Horas

from Backend.Representacion.mapas_calor import MapaCalor


class bike_simulator4:

    # CLASES PÚBLICAS;:

    # Función que carga los datos
    # entrada: Dirección del path con los 3 archivos csv.
    # SALIDA:
    # nearest_stations_idx -> Matriz de cercanas_indices.csv
    # nearest_stations_distance -> Matriz de cercanas_kms.csv
    # initial_movements -> Lista con el estado inicial de las bicicletas, sacado de deltas_5m.csv, de la fila 2(estado inicial).
    # real_movements -> Lista de cantidad de movimientos producido en cada estación, no podemos diferenciar el tiempo,
    # No entiendo porqué la cantidad demovimientos puede ser negativa.

    def load_data(self, directorios: list[str] = None, basepath="data"):

        if (directorios == None):
            nearest_stations_idx = pd.read_csv(basepath + "/cercanas_indices.csv").to_numpy()
            nearest_stations_distance = pd.read_csv(basepath + "/cercanas_kms.csv").to_numpy()
            movements_matrix = pd.read_csv(basepath + "/deltas_15m.csv").to_numpy()
            capacidad_inicial = pd.read_csv(basepath + "/capacidades.csv").to_numpy()
            coordenadas = pd.read_csv(basepath + "/coordenadas.csv").to_numpy()
            tendencia = pd.read_csv(basepath + "/tendencia_media.csv").to_numpy()
        else:
            nearest_stations_idx = pd.read_csv(directorios[2]).to_numpy()
            nearest_stations_distance = pd.read_csv(directorios[3]).to_numpy()
            movements_matrix = pd.read_csv(directorios[0]).to_numpy()
            capacidad_inicial = pd.read_csv(directorios[1]).to_numpy()
            coordenadas = pd.read_csv(directorios[4]).to_numpy()
            Constantes.COORDENADAS = coordenadas
            tendencia = pd.read_csv(directorios[5]).to_numpy()

        bicicle_movements = []
        # movements_matrix[1:, ] = movements_matrix[1:, ] * 2  # Quito esto para pruba fake datos

        for row in range(len(movements_matrix)):
            for col in range(len(movements_matrix[0])):  # Hacer aleatorio.

                if movements_matrix[row, col] != 0:
                    bicicle_movements.append(
                        BiciTransition(index=col, amount=int(movements_matrix[row, col]), time=row, real=True))
                else:
                    if row == 0:
                        bicicle_movements.append(
                            BiciTransition(index=col, amount=0, time=row, real=True)
                        )
                if tendencia[row, col] != 0:
                    bicicle_movements.append(
                        BiciTransition(index=col, amount=int(tendencia[row, col]), time=row, real=False))

        initial_movements = bicicle_movements[:len(movements_matrix[0])]
        # deltas = bicicle_movements[len(movements_matrix[0]):]
        deltas = bicicle_movements

        return nearest_stations_idx, nearest_stations_distance, initial_movements, deltas, \
               capacidad_inicial.transpose()[0], coordenadas

    # Función que asigna a una estación más cercana con capacidad.
    def __get_nearest_station_with_capacity(self, current_station, drop_bikes, solution, occupation,
                                            indiceInicioBusqueda,
                                            nearest_stations_idx=None,
                                            nearest_stations_distance=None):
        if drop_bikes:
            available_bike_or_spot = solution - occupation
        else:
            available_bike_or_spot = occupation
        for i in range(indiceInicioBusqueda,len(nearest_stations_idx[current_station])):
            if available_bike_or_spot[nearest_stations_idx[current_station, i]] > 0:
                return nearest_stations_idx[current_station, i], nearest_stations_distance[current_station, i], \
                       available_bike_or_spot[
                           nearest_stations_idx[current_station, i]]
        print(solution)
        print(occupation)
        print(solution - occupation)
        raise Exception("No available spot found to collect or drop bikes!")

    ##Evalua una posible solucion con respecto a los movimientos y estaciones.
    # Entradas -> Solucion
    # Movimientos iniciales
    # Movimientos reales
    # Matriz de estaciones cercanas
    def evaluate_solution(self, solution, initial_movements, deltas, nearest_stations_idx,
                          nearest_stations_distance):

        # El array de ocupación será un array con el tamaño de solucion.
        occupation = np.zeros(solution.shape)
        total_cost = 0  # coste total (kms) para buscar o dejar una bici.
        bici_sum = 0
        nEstaciones = occupation.shape[0]
        matrices = {

            Constantes.KMS_DEJAR_BICI: Data_matrix(nEstaciones),
            # Matriz que contiene los kms recorridos al dejar las bicicletas de cada instante/peticion
            Constantes.KMS_COGER_BICI: Data_matrix(nEstaciones),
            Constantes.PETICIONES_NORESUELTAS_COGER_BICI: Data_matrix(nEstaciones),
            Constantes.PETICIONES_RESUELTAS_COGER_BICI: Data_matrix(nEstaciones),
            Constantes.PETICIONES_NORESUELTAS_SOLTAR_BICI: Data_matrix(nEstaciones),
            Constantes.PETICIONES_RESUELTAS_SOLTAR_BICI: Data_matrix(nEstaciones),
            ##PREGUNTAR QUE SON LAS MATRICES RESUELTAS, COMO TAL, SE RESUELVEW TODO, SON LAS QUE SE RESUELVEN SIN CONFLICTOS???
            Constantes.OCUPACION: Data_matrix(nEstaciones),
            Constantes.DESPLAZAMIENTOS: Desplazamientos_matrix(),
            Constantes.OCUPACION_HORAS: Data_matrix(nEstaciones),
            Constantes.OCUPACION_RELATIVA: Data_matrix(nEstaciones),
            Constantes.OCUPACION_RELATIVA_HORAS: Data_matrix(nEstaciones),
            Constantes.KMS_COGER_BICI_HORAS: Data_matrix(nEstaciones),
            Constantes.KMS_DEJAR_BICI_HORAS: Data_matrix(nEstaciones),
            Constantes.KMS_FICTICIOS_COGER: Data_matrix(nEstaciones),
            Constantes.KMS_FICTICIOS_DEJAR: Data_matrix(nEstaciones),
            Constantes.PETICIONES_NORESUELTAS_FICTICIAS_COGER_BICI: Data_matrix(nEstaciones),
            Constantes.PETICIONES_NORESUELTAS_FICTICIAS_DEJAR_BICI: Data_matrix(nEstaciones),

        }

        # Calculo de bicicletas totales y ocupación inicial
        for start_occupation in initial_movements:  # Los movimientos se tratan como movimientos reales, esto de aqui solo sirve para
            # calcular el bici_sum, sin el cual, peta.
            # occupation[start_occupation.index] = start_occupation.amount
            bici_sum += start_occupation.amount

        # Introducimos en el instante 0 el array de la ocupación inicial.
        # matrices[Constantes.OCUPACION].add_row_position(0, [0] + occupation.tolist())

        contador = 0
        # Estas variables son utilizadas para detectar cuando hay un salto de instante de tiempo para generar la ocupación.
        horaPrevia = 0  # Tiempo del movimiento anterior

        for movement in deltas:  # Para cada movimiento.

            dado = random.Random.uniform(0,1)
            if dado < Constantes.PORCENTAJE_ESTRES:
                None

            contador += 1
            horaActual = movement.time  # Tiempo actual.
            tipoPeticion = Constantes.PETICION_DEJAR_BICI if movement.amount > 0 else Constantes.PETICION_SOLICITAR_BICI  # Declaramos el tipo de petición.
            estacionFinal = 0
            # Insertaremos la misma ocupación que la de la delta anterior.
            diferenciaDelta = horaActual - horaPrevia
            if (diferenciaDelta > 1):  # Esto simboliza que se ha saltado la hora.
                for i in range(1, diferenciaDelta):
                    nuevaHora = horaPrevia + i
                    horaPrevia = nuevaHora
                    matrices[Constantes.OCUPACION].add_row_position(int(nuevaHora),
                                                                    [int(nuevaHora)] + occupation.tolist())

            # Variables auxiliares para la insercción de arrays en sus matrices correspondientes
            listakms = [0] * nEstaciones
            nPeticionesNoResueltas = [0] * nEstaciones
            nPeticionesResueltas = [0] * nEstaciones

            if movement.real == False:

                amount_to_move = abs(movement.amount)
                primeraIteracion = True
                # Estas variables se asignan en la primera iteración del bucle.
                nPeticionesNoResueltas = 0
                listakms = [0] * nEstaciones  # Esta lista irá actualizandose con los kms para coger/soltar bicis
                while amount_to_move > 0:
                    # Calculamos la estación mas cerca disponible y obtenemos la información relacionada.
                    nearest_station, distance, available_spots_or_bikes \
                        = self.__get_nearest_station_with_capacity(movement.index,
                                                                   tipoPeticion==Constantes.PETICION_DEJAR_BICI,
                                                                   solution,
                                                                   occupation,
                                                                   estacionFinal,
                                                                   nearest_stations_idx,
                                                                   nearest_stations_distance)

                    asignadas = min(amount_to_move, available_spots_or_bikes)  # Variable con los movimientos a realizar
                    cost = distance * asignadas
                    if tipoPeticion==Constantes.PETICION_SOLICITAR_BICI:  # Si lo que quieres es dejar la bici, recorreras los kms en la bici, si lo que quieres es
                        cost *= Constantes.COSTE_ANDAR
                    amount_to_move -= asignadas  # Restamos los movimientos a realizar
                    listakms[movement.index] += cost
                    if primeraIteracion == True:
                        nPeticionesNoResueltas = amount_to_move
                        primeraIteracion = False
                    estacionFinal += 1
                #End while
                if tipoPeticion == Constantes.PETICION_DEJAR_BICI:
                    #Hacer peticiones resueltas.
                    if nPeticionesNoResueltas > 0:#Si existen peticiones no resueltas
                        lista_NoResueltas = [0] * nEstaciones
                        lista_NoResueltas[movement.index] = nPeticionesNoResueltas
                        matrices[Constantes.PETICIONES_NORESUELTAS_FICTICIAS_DEJAR_BICI].add_row(
                            [int(movement.time)] + lista_NoResueltas)  # Insertamos presult

                    if np.array(listakms).sum() > 0:#Si se han realizado kilómetros
                        matrices[Constantes.KMS_FICTICIOS_DEJAR].add_row([int(movement.time)] + listakms)
                else:#Para coger bicicletas.

                    if nPeticionesNoResueltas > 0:  # Si existen peticiones no resueltas
                        lista_NoResueltas = [0] * nEstaciones
                        lista_NoResueltas[movement.index] = nPeticionesNoResueltas
                        matrices[Constantes.PETICIONES_NORESUELTAS_FICTICIAS_COGER_BICI].add_row(
                            [int(movement.time)] + lista_NoResueltas)  # Insertamos presult

                    if np.array(listakms).sum() > 0:  # Si se han realizado kilómetros
                        matrices[Constantes.KMS_FICTICIOS_COGER].add_row([int(movement.time)] + listakms)

            else:#Movimientos reales:


                amount_to_move = abs(movement.amount)  # Cantidad de movimientos a realizar.

                primeraIteracion = True
                #Estas variables se asignan en la primera iteración del bucle.
                nPeticionesResueltas = 0
                nPeticionesNoResueltas = 0
                listakms = [0]*nEstaciones#Esta lista irá actualizandose con los kms para coger/soltar bicis

                while amount_to_move > 0:  # Mientras existan movimientos a realizar:

                    # Calculamos la estación mas cerca disponible y obtenemos la información relacionada.
                    nearest_station, distance, available_spots_or_bikes \
                        = self.__get_nearest_station_with_capacity(movement.index,
                                                                   tipoPeticion==Constantes.PETICION_DEJAR_BICI,
                                                                   solution,
                                                                   occupation,
                                                                   estacionFinal,
                                                                   nearest_stations_idx,
                                                                   nearest_stations_distance)

                    # Calculo del coste considerando que andar cuesta más que ir en bicicleta a otra estación
                    asignadas = min(amount_to_move, available_spots_or_bikes)  # Variable con los movimientos a realizar
                    cost = distance * asignadas

                    if tipoPeticion==Constantes.PETICION_SOLICITAR_BICI:  # Si lo que quieres es dejar la bici, recorreras los kms en la bici, si lo que quieres es
                        cost *= Constantes.COSTE_ANDAR

                    amount_to_move -= asignadas  # Restamos los movimientos a realizar

                    listakms[movement.index] += cost

                    if primeraIteracion == True:
                        nPeticionesResueltas = asignadas
                        nPeticionesNoResueltas = amount_to_move
                        primeraIteracion = False

                    matrices[Constantes.DESPLAZAMIENTOS].add_row([movement.index, nearest_station, tipoPeticion, movement.time, abs(asignadas)])

                    if tipoPeticion == Constantes.PETICION_DEJAR_BICI:  # Si la acción es dejar la bicicleta, aumentamos las bicis de la ocupacion de la estación.
                        occupation[nearest_station] += asignadas
                    else:
                        occupation[
                            nearest_station] -= asignadas  # Si no, pues sencillamente cogemos la bici en las cantidades solicitadas,
                        # porque hay suficientes.
                    estacionFinal +=1
                #End while.
                #Comprobacion
                if nPeticionesResueltas + nPeticionesNoResueltas != abs(movement.amount):
                    raise Exception("Se han creado peticiones de la nada!")
                #Introducimos los datos recolectados:
                if tipoPeticion == Constantes.PETICION_DEJAR_BICI:
                    if nPeticionesResueltas > 0:#Si existen peticiones resueltas
                        lista_Resueltas = [0]*nEstaciones
                        lista_Resueltas[movement.index] = nPeticionesResueltas
                        matrices[Constantes.PETICIONES_RESUELTAS_SOLTAR_BICI].add_row([int(movement.time)] + lista_Resueltas)#Insertamos presult

                    if nPeticionesNoResueltas > 0:#Si existen peticiones no resueltas
                        lista_NoResueltas = [0] * nEstaciones
                        lista_NoResueltas[movement.index] = nPeticionesNoResueltas
                        matrices[Constantes.PETICIONES_NORESUELTAS_SOLTAR_BICI].add_row(
                            [int(movement.time)] + lista_NoResueltas)  # Insertamos presult

                    if np.array(listakms).sum() > 0:#Si se han realizado kilómetros
                        matrices[Constantes.KMS_DEJAR_BICI].add_row([int(movement.time)] + listakms)
                else:#Para coger bicicletas.
                    if nPeticionesResueltas > 0:  # Si existen peticiones resueltas
                        lista_Resueltas = [0] * nEstaciones
                        lista_Resueltas[movement.index] = nPeticionesResueltas
                        matrices[Constantes.PETICIONES_RESUELTAS_COGER_BICI].add_row(
                            [int(movement.time)] + lista_Resueltas)  # Insertamos presult

                    if nPeticionesNoResueltas > 0:  # Si existen peticiones no resueltas
                        lista_NoResueltas = [0] * nEstaciones
                        lista_NoResueltas[movement.index] = nPeticionesNoResueltas
                        matrices[Constantes.PETICIONES_NORESUELTAS_COGER_BICI].add_row(
                            [int(movement.time)] + lista_NoResueltas)  # Insertamos presult

                    if np.array(listakms).sum() > 0:  # Si se han realizado kilómetros
                        matrices[Constantes.KMS_COGER_BICI].add_row([int(movement.time)] + listakms)

                matrices[Constantes.OCUPACION].add_row_position(int(movement.time),
                                                                [int(movement.time)] + occupation.tolist())
            bici_sum += movement.amount
            horaPrevia = horaActual

            # if np.sum(occupation) != bici_sum:
            #   raise Exception("Bici sum wrong")

        # CREAR LOS DATAFRAMES CON LOS NUMPY.

        matrices[Constantes.DESPLAZAMIENTOS].create_Dataframe()
        matrices[Constantes.KMS_COGER_BICI].create_Dataframe()
        matrices[Constantes.KMS_DEJAR_BICI].create_Dataframe()
        matrices[Constantes.PETICIONES_NORESUELTAS_COGER_BICI].create_Dataframe()
        matrices[Constantes.PETICIONES_RESUELTAS_COGER_BICI].create_Dataframe()
        matrices[Constantes.PETICIONES_NORESUELTAS_SOLTAR_BICI].create_Dataframe()
        matrices[Constantes.PETICIONES_RESUELTAS_SOLTAR_BICI].create_Dataframe()
        matrices[Constantes.OCUPACION].create_Dataframe()
        matrices[Constantes.OCUPACION_HORAS] = Ocupacion_Horas(matrices[Constantes.OCUPACION].matrix)
        matrices[Constantes.PETICIONES_NORESUELTAS_FICTICIAS_DEJAR_BICI].create_Dataframe()
        matrices[Constantes.PETICIONES_NORESUELTAS_FICTICIAS_COGER_BICI].create_Dataframe()

        matrices[Constantes.OCUPACION_RELATIVA].lista = np.insert(
            matrices[Constantes.OCUPACION].matrix.iloc[:, 1:].to_numpy() * (100 / np.array(solution)), 0,
            list(range(1, matrices[Constantes.OCUPACION].matrix.shape[0] + 1)), 1)
        matrices[Constantes.OCUPACION_RELATIVA_HORAS].lista = np.insert(
            matrices[Constantes.OCUPACION_HORAS].matrix.iloc[:, 1:].to_numpy() * (100 / np.array(solution)), 0,
            list(range(1, matrices[Constantes.OCUPACION_HORAS].matrix.shape[0] + 1)), 1)

        matrices[Constantes.OCUPACION_RELATIVA].create_Dataframe()
        matrices[Constantes.OCUPACION_RELATIVA_HORAS].create_Dataframe()

        matrices[Constantes.KMS_FICTICIOS_DEJAR].create_Dataframe()
        matrices[Constantes.KMS_FICTICIOS_COGER].create_Dataframe()

        # COLAPSARLOS

        # Preguntar a M.A las definiciones de cada matriz para estar seguro de que todo es correcto y dar por finalizada esta parte.
        matrices[Constantes.KMS_COGER_BICI].colapsarEnUTempDelta()
        matrices[Constantes.KMS_DEJAR_BICI].colapsarEnUTempDelta()
        matrices[Constantes.PETICIONES_NORESUELTAS_COGER_BICI].colapsarEnUTempDelta()
        matrices[Constantes.PETICIONES_NORESUELTAS_SOLTAR_BICI].colapsarEnUTempDelta()
        matrices[Constantes.PETICIONES_RESUELTAS_COGER_BICI].colapsarEnUTempDelta()
        matrices[Constantes.PETICIONES_RESUELTAS_SOLTAR_BICI].colapsarEnUTempDelta()
        matrices[Constantes.KMS_COGER_BICI_HORAS].matrix = auxiliar_calculos_kilometros.getDfKmsHorarios(
            matrices[Constantes.KMS_COGER_BICI].matrix)
        matrices[Constantes.KMS_DEJAR_BICI_HORAS].matrix = auxiliar_calculos_kilometros.getDfKmsHorarios(matrices[
                                                                                                             Constantes.KMS_DEJAR_BICI].matrix)

        matrices[Constantes.PETICIONES_NORESUELTAS_FICTICIAS_DEJAR_BICI].colapsarEnUTempDelta()
        matrices[Constantes.PETICIONES_NORESUELTAS_FICTICIAS_COGER_BICI].colapsarEnUTempDelta()

        # estOc = estadisticasOcupacionHorarias(matrices[Constantes.OCUPACION_HORAS].matrix, 60)
        # estOc.HistogramaPorEstacion(0,[0])
        # estOc.HistogramaOcupacionMedia([0,1,2])
        # estOc.HistogramaCompararEstaciones([0, 0], [[0], [1]])
        # estOc.HistogramaAcumulacion(0,[0,1,2])
        # estOc.HistogramaPorDia(0)

        # Tengo que transformar: KMS_COGER/DEJAR_BICI

        mc = MapaCalor(matrices[Constantes.OCUPACION_HORAS].matrix.loc[:, matrices[
                                                                              Constantes.OCUPACION_HORAS].matrix.columns != 'hora'])
        mc.representar()

        return total_cost, matrices

    def __print_statistics_over_solution(self, solution_values, evaluation_calls, name=""):
        print(
            f"{name}: average kms: {np.mean(solution_values):.3f}, std kms: {np.std(solution_values):.3f}, min kms: {np.min(solution_values):.3f} "
            f"average evaluation calls: {np.mean(evaluation_calls):.3f}, std evaluation calls: {np.std(evaluation_calls):.3f}, min evaluation calls: {np.min(evaluation_calls):.3f}")

    def __plot_and_safe_values(self, values, title=""):
        plt.plot(values)
        plt.title(title)
        plt.xlabel("iteration")
        plt.ylabel("kilometers")
        plt.savefig(f"plots/{title}.png")
        plt.show()
