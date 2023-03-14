from _random import Random
from datetime import time

import joblib
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from random import Random
import time
from Backend import Constantes
from Backend.EstructurasDatos.BiciTransition import BiciTransition
from Backend.EstructurasDatos.data_matrix import Data_matrix, Desplazamientos_matrix, Ocupacion_Horas
from Backend.estadisticasOcupacionHorarias import estadisticasOcupacionHorarias
from Backend.Representacion.mapas_calor import MapaCalor


class bike_simulator:

    # CLASES PÚBLICAS;:

    # Función que carga los datos
    # entrada: Dirección del path con los 3 archivos csv.
    # SALIDA:
    # nearest_stations_idx -> Matriz de cercanas_indices.csv
    # nearest_stations_distance -> Matriz de cercanas_kms.csv
    # initial_movements -> Lista con el estado inicial de las bicicletas, sacado de deltas_5m.csv, de la fila 2(estado inicial).
    # real_movements -> Lista de cantidad de movimientos producido en cada estación, no podemos diferenciar el tiempo,
    # No entiendo porqué la cantidad demovimientos puede ser negativa.
    def load_data(self, basepath="data"):
        nearest_stations_idx = pd.read_csv(basepath + "/cercanas_indices.csv").to_numpy()
        nearest_stations_distance = pd.read_csv(basepath + "/cercanas_kms.csv").to_numpy()
        movements_matrix = pd.read_csv(basepath + "/deltas_5m.csv").to_numpy()
        capacidad_inicial = pd.read_csv(basepath + "/capacidades.csv").to_numpy()
        coordenadas = pd.read_csv(basepath + "/coordenadas.csv").to_numpy()

        bicicle_movements = []
        #movements_matrix[1:, ] = movements_matrix[1:, ] * 2  # Quito esto para pruba fake datos

        for row in range(len(movements_matrix)):
            for col in range(len(movements_matrix[0])):
                if movements_matrix[row, col] != 0:
                    bicicle_movements.append(
                        BiciTransition(index=col, amount=int(movements_matrix[row, col]), time=row))
                else:
                    if row == 0:
                        bicicle_movements.append(
                            BiciTransition(index = col,amount=0,time=row) #chanchullo.
                        )

        initial_movements = bicicle_movements[:len(movements_matrix[0])]
        real_movements = bicicle_movements[len(movements_matrix[0]):]

        return nearest_stations_idx, nearest_stations_distance, initial_movements, real_movements, capacidad_inicial.transpose()[0],coordenadas

    def evaluate_solutions(self, solutions, initial_movements, real_movements, nearest_stations_idx,
                           nearest_stations_distance):
        values = joblib.Parallel(n_jobs=4)(
            joblib.delayed(self.evaluate_solution(solutions[i], initial_movements, real_movements, nearest_stations_idx,
                                                  nearest_stations_distance) for i in range(len(solutions))))
        return values

    def random_search(self, nearest_stations_idx, nearest_stations_distance, initial_movements, real_movements):
        # use longer precision seeds to imply more variety
        random_seeds = [42, 3, 69, 0, 16]
        solutions = []
        solution_values = []
        for seed in random_seeds:
            random_generator = Random(seed)
            best_solution = None
            best_solution_value = None
            for i in range(100):
                current_solution = self.__generate_initial_solution(random_generator, 30, 220, 220)
                current_solution = self.__conform_to_initial_placement(current_solution, initial_movements,
                                                                       nearest_stations_idx,
                                                                       nearest_stations_distance)
                current_solution_value = self.__evaluate_solution(current_solution, initial_movements, real_movements,
                                                                  nearest_stations_idx, nearest_stations_distance)
                # print(f"cost: {current_solution_value:7.3f}, sol: {current_solution}")
                if best_solution is None or current_solution_value < best_solution_value:
                    best_solution = current_solution
                    best_solution_value = current_solution_value
            solutions.append(best_solution)
            solution_values.append(best_solution_value)
        for i in range(len(random_seeds)):
            print(
                f"[RANDOM] Best solution with seed {random_seeds[i]:3d}: v: {solution_values[i]:7.3f}, s: {solutions[i]}")
        self.__print_statistics_over_solution(solution_values, [100], "Random search")

    def generate_greedy_solution(self, initial_movements, desired_amount_bici=220):
        initial_amount_bici = 0
        current_amount_bici = 0

        for i in initial_movements:
            initial_amount_bici = i.amount + initial_amount_bici

        greedy_solution = []
        for i in initial_movements:
            share = i.amount / initial_amount_bici
            nr_bike_places = round(share * desired_amount_bici)
            greedy_solution.append(nr_bike_places)

            current_amount_bici += nr_bike_places

        # prüfen, ob desired_amount_bici oder nicht
        if current_amount_bici <= desired_amount_bici:
            greedy_solution[0] += (desired_amount_bici - current_amount_bici)

        else:
            i = 0
            while current_amount_bici > desired_amount_bici:
                if greedy_solution[i] > 0:
                    if greedy_solution[i] > current_amount_bici - desired_amount_bici:
                        greedy_solution[i] -= current_amount_bici - desired_amount_bici
                        current_amount_bici = desired_amount_bici
                    else:
                        current_amount_bici -= greedy_solution[i]
                        greedy_solution[i] = 0

                i += 1
        return np.array(greedy_solution)

    # CLASES PRIVADAS:

    def __generate_initial_solution(self, random_generator, max_bikes_at_station=30, stations_min=205, stations_max=220,
                                    amount_bike_stations=16):
        solution = np.zeros(amount_bike_stations)
        available_stations = stations_max
        for i in range(amount_bike_stations):
            stations = random_generator.randint(0, max_bikes_at_station)
            stations = stations % available_stations
            available_stations -= stations
            solution[i] = stations

        while available_stations > stations_max - stations_min:
            solution[random_generator.randint(0, amount_bike_stations - 1)] += 1
            available_stations -= 1
        random_generator.shuffle(solution)
        return solution

    def __get_nearest_station_with_capacity(self, current_station, drop_bikes, solution, occupation,
                                            nearest_stations_idx=None,
                                            nearest_stations_distance=None):
        if drop_bikes:
            available_bike_or_spot = solution - occupation
        else:
            available_bike_or_spot = occupation
        for i in range(len(nearest_stations_idx[current_station])):
            if available_bike_or_spot[nearest_stations_idx[current_station, i]] > 0:
                return nearest_stations_idx[current_station, i], nearest_stations_distance[current_station, i], \
                       available_bike_or_spot[
                           nearest_stations_idx[current_station, i]]
        print(solution)
        print(occupation)
        print(solution - occupation)
        raise Exception("No available spot found to collect or drop bikes!")

    def __conform_to_initial_placement(self, solution, initial_movements, nearest_stations_idx,
                                       nearest_stations_distance):
        expected_occupation = np.zeros(len(solution))
        for movement in initial_movements:
            expected_occupation[movement.index] = movement.amount
            missing_bike_places = movement.amount - solution[movement.index]
            while missing_bike_places > 0:
                nearest_station, _, available_spots = self.__get_nearest_station_with_capacity(movement.index, True,
                                                                                               solution,
                                                                                               expected_occupation,
                                                                                               nearest_stations_idx,
                                                                                               nearest_stations_distance)
                if available_spots >= missing_bike_places:
                    solution[movement.index] += missing_bike_places
                    solution[nearest_station] -= missing_bike_places
                    missing_bike_places = 0
                else:
                    solution[movement.index] += available_spots
                    solution[nearest_station] -= available_spots
                    missing_bike_places -= available_spots
        return solution

    ##Evalua una posible solucion con respecto a los movimientos y estaciones.
    # Entradas -> Solucion
    # Movimientos iniciales
    # Movimientos reales
    # Matriz de estaciones cercanas
    def evaluate_solution(self, solution, initial_movements, real_movements, nearest_stations_idx,
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
            Constantes.PETICIONES_RESUELTAS_SOLTAR_BICI: Data_matrix(nEstaciones), ##PREGUNTAR QUE SON LAS MATRICES RESUELTAS, COMO TAL, SE RESUELVEW TODO, SON LAS QUE SE RESUELVEN SIN CONFLICTOS???
            Constantes.OCUPACION: Data_matrix(nEstaciones),
            Constantes.DESPLAZAMIENTOS : Desplazamientos_matrix(),
            Constantes.OCUPACION_HORAS : Data_matrix(nEstaciones)
        }
        # La solución debe contemplar las 220 posibles bicis.PREGUNTAR ESTO
        #if np.sum(solution) != Constantes.CAPACIDAD_MAXIMA_INICIAL:
         #   raise Exception("Solution invalid")
        # Para cada ocupacion inicial de cada estación.
        for start_occupation in initial_movements:
            occupation[start_occupation.index] = start_occupation.amount  # Básicamente, ocupación va a ser Delta0
            bici_sum += start_occupation.amount

        matrices[Constantes.OCUPACION].add_row_position(0, [0] + occupation.tolist())

        #crep qie deberia poner la ocupacion inicial.
        for movement in real_movements:  # Para cada movimiento.

            listakms = [0] * nEstaciones
            nPeticionesNoResueltas = [0] * nEstaciones
            nPeticionesResueltas = [0]*nEstaciones
            estacionOrigen = movement.index
            estacionFinal = -1
            tipoPeticion = -1


            capacity_after_movement = occupation[movement.index] + movement.amount  # calculamos la nueva ocupación.

            if capacity_after_movement > solution[movement.index] or capacity_after_movement < 0:  # Si no hay hueco o bicis.
                drop_bikes = False  # Iniciamos a falso la opcion de soltar bicis.
                if capacity_after_movement > 0:
                    drop_bikes = True  # Si la nueva ocupacion es positiva(además de ser mayor que la solucion), necesitamos soltar bicis
                amount_to_move = abs(movement.amount)  # Cantidad de movimientos a realizar.

            #si yo aqui meto las peticiones no resueltas?


                while amount_to_move > 0:  # Cuando se satisfagan todas las peticiones:
                    # Calculamos la estación mas cerca disponible.
                    nearest_station, distance, available_spots_or_bikes \
                        = self.__get_nearest_station_with_capacity(movement.index,
                                                                   drop_bikes,
                                                                   solution,
                                                                   occupation,
                                                                   nearest_stations_idx,
                                                                   nearest_stations_distance)

                    # Calculo del coste
                    cost = distance * min(amount_to_move,
                                          available_spots_or_bikes)  # El coste será la distancia por ????
                    if not drop_bikes:  # Si lo que quieres es dejar la bici, recorreras los kms en la bici, si lo que quieres es
                        # buscarla, tendrás que hacer los kms a pata, que cuesta el triple.
                        cost *= 3
                    total_cost += cost
                    # Fin calculo coste

                    if available_spots_or_bikes >= amount_to_move:  # Si hay hueco para realizar una acción

                        #INTRODUCCION DE CODIGO
                        estacionFinal = nearest_station
                        tipoPeticion = Constantes.PETICION_DEJAR_BICI if movement.amount > 0 else Constantes.PETICION_SOLICITAR_BICI
                        matrices[Constantes.DESPLAZAMIENTOS].add_row([estacionOrigen, estacionFinal, tipoPeticion, movement.time, abs(movement.amount)])

                        if drop_bikes:  # Si la acción es dejar la bicicleta, aumentamos las bicis de la ocupacion de la estación.
                            occupation[nearest_station] += amount_to_move
                            ##INTRODUCCION DE CODIGO

                            listakms[movement.index] += cost
                            matrices[Constantes.KMS_DEJAR_BICI].add_row([int(movement.time)] + listakms)


                        else:
                            occupation[nearest_station] -= amount_to_move  # Si no, pues sencillamente cogemos la bici en las cantidades solicitadas,porque hay suficientes.

                            ##INTRODUCCION DE CODIGO
                            listakms[movement.index] += cost
                            matrices[Constantes.KMS_COGER_BICI].add_row([int(movement.time)] + listakms)

                        amount_to_move = 0
                    else:  # Si no hay hueco.

                        if drop_bikes:  # Si ibamos a dejar bicicletas
                            occupation[nearest_station] += available_spots_or_bikes  # Dejamos las que podamos
                            amount_to_move -= available_spots_or_bikes  # Actualizamos las que debemos reorganizar y seguimos iterando en el bucle.

                            #INTRODUCCION DE CODIGO
                            nPeticionesNoResueltas[movement.index] = amount_to_move

                            matrices[Constantes.PETICIONES_NORESUELTAS_SOLTAR_BICI].add_row([int(movement.time)] + nPeticionesNoResueltas)

                        else:
                            occupation[nearest_station] -= available_spots_or_bikes  # Tomamos las que existan en la estación
                            amount_to_move -= available_spots_or_bikes  # Actualizamos y seguimos iterando

                            #INTRODUCCION DE CODIGO
                            nPeticionesNoResueltas[movement.index] = amount_to_move
                            matrices[Constantes.PETICIONES_NORESUELTAS_COGER_BICI].add_row([int(movement.time)] + nPeticionesNoResueltas)


            else:  # Si existe hueco se actualiza y para alante.

                start_time = time.time()

                occupation[movement.index] += movement.amount
                estacionFinal = movement.index
                tipoPeticion = Constantes.PETICION_DEJAR_BICI if movement.amount > 0 else Constantes.PETICION_SOLICITAR_BICI


                matrices[Constantes.DESPLAZAMIENTOS].add_row([estacionOrigen, estacionFinal, tipoPeticion, movement.time, abs(movement.amount)])

                nPeticionesResueltas[movement.index] = movement.amount
                if(tipoPeticion == Constantes.PETICION_DEJAR_BICI):

                    matrices[Constantes.PETICIONES_RESUELTAS_SOLTAR_BICI].add_row([int(movement.time)] + nPeticionesResueltas)
                else:
                    matrices[Constantes.PETICIONES_RESUELTAS_COGER_BICI].add_row(
                        [int(movement.time)] + nPeticionesResueltas)

                print("--- %s seconds ---" % (time.time() - start_time))


            #matrices[Constantes.OCUPACION].add_row([int(movement.time)] + occupation.tolist())
            matrices[Constantes.OCUPACION].add_row_position(int(movement.time), [int(movement.time)] + occupation.tolist())


            bici_sum += movement.amount
            if np.sum(occupation) != bici_sum:
                raise Exception("Bici sum wrong")


        #CREAR LOS DATAFRAMES CON LOS NUMPY.

        matrices[Constantes.DESPLAZAMIENTOS].create_Dataframe()
        matrices[Constantes.KMS_COGER_BICI].create_Dataframe()
        matrices[Constantes.KMS_DEJAR_BICI].create_Dataframe()
        matrices[Constantes.PETICIONES_NORESUELTAS_COGER_BICI].create_Dataframe()
        matrices[Constantes.PETICIONES_RESUELTAS_COGER_BICI].create_Dataframe()
        matrices[Constantes.PETICIONES_NORESUELTAS_SOLTAR_BICI].create_Dataframe()
        matrices[Constantes.PETICIONES_RESUELTAS_SOLTAR_BICI].create_Dataframe()
        matrices[Constantes.OCUPACION].create_Dataframe()
        matrices[Constantes.OCUPACION_HORAS] = Ocupacion_Horas(matrices[Constantes.OCUPACION].matrix)

        #COLAPSARLOS

        #Preguntar a M.A las definiciones de cada matriz para estar seguro de que todo es correcto y dar por finalizada esta parte.
        matrices[Constantes.KMS_COGER_BICI].colapsarEnUTempDelta()
        matrices[Constantes.KMS_DEJAR_BICI].colapsarEnUTempDelta()
        matrices[Constantes.PETICIONES_NORESUELTAS_COGER_BICI].colapsarEnUTempDelta()
        matrices[Constantes.PETICIONES_NORESUELTAS_SOLTAR_BICI].colapsarEnUTempDelta()
        matrices[Constantes.PETICIONES_RESUELTAS_COGER_BICI].colapsarEnUTempDelta()
        matrices[Constantes.PETICIONES_RESUELTAS_SOLTAR_BICI].colapsarEnUTempDelta()

        estOc = estadisticasOcupacionHorarias(matrices[Constantes.OCUPACION_HORAS].matrix)
        estOc.HistogramaPorEstacion(0,[0,1,2])
        estOc.HistogramaOcupacionMedia([0,1,2])
        #estOc.HistogramaPorDia(0)



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
