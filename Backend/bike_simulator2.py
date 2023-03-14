import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import Backend.Constantes as Constantes
from Backend.Auxiliares import auxiliar_calculos_kilometros
from Backend.EstructurasDatos.BiciTransition import BiciTransition
from Backend.EstructurasDatos.data_matrix import Data_matrix, Desplazamientos_matrix, Ocupacion_Horas

from Backend.Representacion.mapas_calor import MapaCalor


class bike_simulator2:

    # CLASES PÚBLICAS;:

    # Función que carga los datos
    # entrada: Dirección del path con los 3 archivos csv.
    # SALIDA:
    # nearest_stations_idx -> Matriz de cercanas_indices.csv
    # nearest_stations_distance -> Matriz de cercanas_kms.csv
    # initial_movements -> Lista con el estado inicial de las bicicletas, sacado de deltas_5m.csv, de la fila 2(estado inicial).
    # real_movements -> Lista de cantidad de movimientos producido en cada estación, no podemos diferenciar el tiempo,
    # No entiendo porqué la cantidad demovimientos puede ser negativa.

    def load_data(self, directorios:list[str]=None,basepath="data"):

        if(directorios == None):
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
        #movements_matrix[1:, ] = movements_matrix[1:, ] * 2  # Quito esto para pruba fake datos

        for row in range(len(movements_matrix)):
            for col in range(len(movements_matrix[0])):#Hacer aleatorio.

                if movements_matrix[row, col] != 0:
                    bicicle_movements.append(
                        BiciTransition(index=col, amount=int(movements_matrix[row, col]), time=row, real=True))
                else:
                    if row == 0:
                        bicicle_movements.append(
                            BiciTransition(index = col,amount=0,time=row,real=True)
                        )
                if tendencia[row, col] != 0:
                    bicicle_movements.append(
                        BiciTransition(index=col, amount=int(tendencia[row, col]), time=row, real=False))

        initial_movements = bicicle_movements[:len(movements_matrix[0])]
        #real_movements = bicicle_movements[len(movements_matrix[0]):]
        real_movements = bicicle_movements

        return nearest_stations_idx, nearest_stations_distance, initial_movements, real_movements, capacidad_inicial.transpose()[0],coordenadas


    #Función que asigna a una estación más cercana con capacidad.
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
            Constantes.OCUPACION_HORAS : Data_matrix(nEstaciones),
            Constantes.OCUPACION_RELATIVA : Data_matrix(nEstaciones),
            Constantes.OCUPACION_RELATIVA_HORAS : Data_matrix(nEstaciones),
            Constantes.KMS_COGER_BICI_HORAS : Data_matrix(nEstaciones),
            Constantes.KMS_DEJAR_BICI_HORAS: Data_matrix(nEstaciones),
            Constantes.KMS_FICTICIOS_COGER:Data_matrix(nEstaciones),
            Constantes.KMS_FICTICIOS_DEJAR:Data_matrix(nEstaciones),
            Constantes.PETICIONES_NORESUELTAS_FICTICIAS_COGER_BICI:Data_matrix(nEstaciones),
            Constantes.PETICIONES_NORESUELTAS_FICTICIAS_DEJAR_BICI: Data_matrix(nEstaciones),

        }
        '''
        #Calculo de bicicletas totales y ocupación inicial
        for start_occupation in initial_movements: #Los movimientos se tratan como movimientos reales, esto de aqui solo sirve para
             #calcular el bici_sum, sin el cual, peta.
            occupation[start_occupation.index] = start_occupation.amount
            bici_sum += start_occupation.amount'''

        # Calculo de bicicletas totales y ocupación inicial
        for start_occupation in initial_movements:  # Los movimientos se tratan como movimientos reales, esto de aqui solo sirve para
            # calcular el bici_sum, sin el cual, peta.
            #occupation[start_occupation.index] = start_occupation.amount
            bici_sum += start_occupation.amount


        #Introducimos en el instante 0 el array de la ocupación inicial.
        #matrices[Constantes.OCUPACION].add_row_position(0, [0] + occupation.tolist())

        contador = 0
        #Estas variables son utilizadas para detectar cuando hay un salto de instante de tiempo para generar la ocupación.
        horaPrevia = 0 #Tiempo del movimiento anterior

        for movement in real_movements:  # Para cada movimiento.
            contador +=1
            horaActual = movement.time#Tiempo actual.

            #Insertaremos la misma ocupación que la de la delta anterior.
            diferenciaDelta = horaActual - horaPrevia
            if(diferenciaDelta > 1):#Esto simboliza que se ha saltado la hora.
                for i in range(1,diferenciaDelta):
                    nuevaHora = horaPrevia + i
                    horaPrevia = nuevaHora
                    matrices[Constantes.OCUPACION].add_row_position(int(nuevaHora), [int(nuevaHora)] + occupation.tolist())


            #Variables auxiliares para la insercción de arrays en sus matrices correspondientes
            listakms = [0] * nEstaciones
            nPeticionesNoResueltas = [0] * nEstaciones
            nPeticionesResueltas = [0]*nEstaciones
            estacionOrigen = movement.index
            #Variables auxiliares para determinar la estación final y el tipo de petición
            estacionFinal = -1

            tipoPeticion = Constantes.PETICION_DEJAR_BICI if movement.amount > 0 else Constantes.PETICION_SOLICITAR_BICI  # Declaramos el tipo de petición.

            capacity_after_movement = occupation[movement.index] + movement.amount  #Calculamos la capacidad que tendrá la estación solicitada de la petición
            # con la idea de comprobar si esta se ha pasado de su capacidad máxima y determinar y existe la necesidad de asignar otra estación al cliente.

            # Meter if con ficticios

            if movement.real == False:

                amount_to_move = abs(movement.amount)
                drop_bikes = False#ESTA VARIABLE SIRVE ÚNICAMENTE PARA SABER SI BUSCAMOS COGER O SOLTAR BICI EN EL CASO
                #DE QUE NECESITAMOS REAGRUPAR, PERO NO SIRVE PARA SABER EL TIPO DE PETICION.
                if capacity_after_movement > 0:
                    drop_bikes = True



                while amount_to_move > 0:
                    # Calculamos la estación mas cerca disponible y obtenemos la información relacionada.
                    nearest_station, distance, available_spots_or_bikes \
                        = self.__get_nearest_station_with_capacity(movement.index,
                                                                   drop_bikes,
                                                                   solution,
                                                                   occupation,
                                                                   nearest_stations_idx,
                                                                   nearest_stations_distance)

                    # Calculo del coste considerando que andar cuesta más que ir en bicicleta a otra estación
                    cost = distance * min(amount_to_move, available_spots_or_bikes)

                    # Fin calculo coste
                    listakms[movement.index] += cost

                    if cost > 0:
                        peticionesNoResueltas = [0]*nEstaciones
                        peticionesNoResueltas[movement.index] = max(abs(movement.amount) - available_spots_or_bikes,0)
                        if tipoPeticion:
                            matrices[Constantes.KMS_FICTICIOS_DEJAR].add_row([int(movement.time)] + listakms)
                            if peticionesNoResueltas[movement.index] != 0:
                                matrices[Constantes.PETICIONES_NORESUELTAS_FICTICIAS_DEJAR_BICI].add_row([int(movement.time)] + peticionesNoResueltas)
                        else:
                            matrices[Constantes.KMS_FICTICIOS_COGER].add_row([int(movement.time)] + listakms)
                            if peticionesNoResueltas[movement.index] != 0:
                                matrices[Constantes.PETICIONES_NORESUELTAS_FICTICIAS_COGER_BICI].add_row([int(movement.time)] + peticionesNoResueltas)
                    amount_to_move -= available_spots_or_bikes




                continue  # Explicar esto, ensucia mucho el código.

            ##AQUI EMPIEZAN LOS MOV REALES:
            if capacity_after_movement > solution[movement.index] or capacity_after_movement < 0:  #En el caso de que no existiese hueco o bicicletas

                #drop_bikes es una variable booleana auxiliar usada para declarar si queremos realizar una operación de extracción de bicicletas
                #o de subtracción de estas.
                drop_bikes = False
                if capacity_after_movement > 0:
                    drop_bikes = True
                amount_to_move = abs(movement.amount)  #Cantidad de movimientos a realizar.

                while amount_to_move > 0:  #Mientras existan movimientos a realizar:

                    # Calculamos la estación mas cerca disponible y obtenemos la información relacionada.
                    nearest_station, distance, available_spots_or_bikes \
                        = self.__get_nearest_station_with_capacity(movement.index,
                                                                   drop_bikes,
                                                                   solution,
                                                                   occupation,
                                                                   nearest_stations_idx,
                                                                   nearest_stations_distance)

                    # Calculo del coste considerando que andar cuesta más que ir en bicicleta a otra estación
                    cost = distance * min(amount_to_move,available_spots_or_bikes)
                    #if not drop_bikes:
                    #    cost *= 3
                    total_cost += cost

                    # Fin calculo coste

                    listakms[movement.index] += cost

                    if distance > 0:#Es decir, no estoy en el caso de que se ingresen a la misma estacion que el origen.
                        nPeticionesNoResueltas[movement.index] += min(amount_to_move,available_spots_or_bikes)

                    if available_spots_or_bikes >= amount_to_move:  # Si hay hueco para realizar una acción

                        estacionFinal = nearest_station
                        tipoPeticion = Constantes.PETICION_DEJAR_BICI if movement.amount > 0 else Constantes.PETICION_SOLICITAR_BICI
                        matrices[Constantes.DESPLAZAMIENTOS].add_row([estacionOrigen, estacionFinal, tipoPeticion, movement.time, abs(movement.amount)])

                        if tipoPeticion:  # Si la acción es dejar la bicicleta, aumentamos las bicis de la ocupacion de la estación.
                            occupation[nearest_station] += amount_to_move
                        else:
                            occupation[nearest_station] -= amount_to_move  # Si no, pues sencillamente cogemos la bici en las cantidades solicitadas,
                            # porque hay suficientes.


                        amount_to_move = 0
                    else:  # Si no hay hueco.

                        if tipoPeticion:  # Si ibamos a dejar bicicletas
                            occupation[nearest_station] += available_spots_or_bikes  # Dejamos las que podamos
                            amount_to_move -= available_spots_or_bikes  # Actualizamos las que debemos reorganizar y seguimos iterando en el bucle.

                        else:
                            occupation[nearest_station] -= available_spots_or_bikes  # Tomamos las que existan en la estación
                            amount_to_move -= available_spots_or_bikes  # Actualizamos y seguimos iterando


                if tipoPeticion:
                    matrices[Constantes.KMS_DEJAR_BICI].add_row([int(movement.time)] + listakms)
                    matrices[Constantes.PETICIONES_NORESUELTAS_SOLTAR_BICI].add_row(
                        [int(movement.time)] + nPeticionesNoResueltas)
                else:
                    matrices[Constantes.KMS_COGER_BICI].add_row([int(movement.time)] + listakms)
                    matrices[Constantes.PETICIONES_NORESUELTAS_COGER_BICI].add_row(
                        [int(movement.time)] + nPeticionesNoResueltas)

            else:  # Si se puede satisfacer la petición:

                occupation[movement.index] += movement.amount #Calculamos la ocupación
                estacionFinal = movement.index #La estación final será la estación solicitada, ya que existe la capacidad para atender la petición.
                tipoPeticion = Constantes.PETICION_DEJAR_BICI if movement.amount > 0 else Constantes.PETICION_SOLICITAR_BICI #Declaramos el tipo de petición.

                #Agregamos a la matriz de despazamientos el movimiento realizado.
                matrices[Constantes.DESPLAZAMIENTOS].add_row([estacionOrigen, estacionFinal, tipoPeticion, movement.time, abs(movement.amount)])

                #Ya que la petición ha sido resuelta, necesitaremos introducirla en su respectiva matriz de peticiones resueltas:
                nPeticionesResueltas[movement.index] = movement.amount #Introducimos el movimiento en su estación correspondiente.
                if(tipoPeticion == Constantes.PETICION_DEJAR_BICI):
                    matrices[Constantes.PETICIONES_RESUELTAS_SOLTAR_BICI].add_row([int(movement.time)] + nPeticionesResueltas)
                else:
                    matrices[Constantes.PETICIONES_RESUELTAS_COGER_BICI].add_row([int(movement.time)] + nPeticionesResueltas)

            matrices[Constantes.OCUPACION].add_row_position(int(movement.time), [int(movement.time)] + occupation.tolist())
            bici_sum += movement.amount
            horaPrevia = horaActual





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

        #COLAPSARLOS

        #Preguntar a M.A las definiciones de cada matriz para estar seguro de que todo es correcto y dar por finalizada esta parte.
        matrices[Constantes.KMS_COGER_BICI].colapsarEnUTempDelta()
        matrices[Constantes.KMS_DEJAR_BICI].colapsarEnUTempDelta()
        matrices[Constantes.PETICIONES_NORESUELTAS_COGER_BICI].colapsarEnUTempDelta()
        matrices[Constantes.PETICIONES_NORESUELTAS_SOLTAR_BICI].colapsarEnUTempDelta()
        matrices[Constantes.PETICIONES_RESUELTAS_COGER_BICI].colapsarEnUTempDelta()
        matrices[Constantes.PETICIONES_RESUELTAS_SOLTAR_BICI].colapsarEnUTempDelta()
        matrices[Constantes.KMS_COGER_BICI_HORAS].matrix = auxiliar_calculos_kilometros.getDfKmsHorarios(matrices[Constantes.KMS_COGER_BICI].matrix)
        matrices[Constantes.KMS_DEJAR_BICI_HORAS].matrix = auxiliar_calculos_kilometros.getDfKmsHorarios(matrices[
                                                                                                             Constantes.KMS_DEJAR_BICI].matrix)

        matrices[Constantes.PETICIONES_NORESUELTAS_FICTICIAS_DEJAR_BICI].colapsarEnUTempDelta()
        matrices[Constantes.PETICIONES_NORESUELTAS_FICTICIAS_COGER_BICI].colapsarEnUTempDelta()


        #estOc = estadisticasOcupacionHorarias(matrices[Constantes.OCUPACION_HORAS].matrix, 60)
        #estOc.HistogramaPorEstacion(0,[0])
        #estOc.HistogramaOcupacionMedia([0,1,2])
        #estOc.HistogramaCompararEstaciones([0, 0], [[0], [1]])
        #estOc.HistogramaAcumulacion(0,[0,1,2])
        #estOc.HistogramaPorDia(0)

    #Tengo que transformar: KMS_COGER/DEJAR_BICI

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
