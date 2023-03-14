import numpy as np
import pandas as pd

from Backend import Constantes


# Clase encargada de la construcción de las matrices necesarias para la tarea 1.
class Data_matrix:

    def __init__(self, n):
        self.matrix = pd.DataFrame(columns=['UTempDelta'] + ['estacion' + str(i) for i in range(n)])
        self.n = n
        #self.numpyData = np.array(self.matrix)
        self.lista = []


    #def add_row(self, row: list):
        #self.matrix.loc[len(self.matrix.index)] = row
    def add_row(self,row:list):
        #self.numpyData = np.vstack([self.numpyData, row])
        self.lista.append(row)

    def create_Dataframe(self):
        self.matrix = pd.DataFrame(self.lista,
            columns=['UTempDelta'] + ['estacion' + str(i) for i in range(self.n)])

    def add_row_position(self,position:int,row:list):
        #self.matrix.loc[position] = row
        if (len(self.lista) > position):
            self.lista[position] = row
        else:
            self.add_row(row)

    def colapsarEnUTempDelta(self):
        self.matrix = self.matrix.groupby("UTempDelta", as_index=False).sum()





class Desplazamientos_matrix:
    def __init__(self):
        #self.matrix = pd.DataFrame(columns=['Estacion origen', 'Estacion final', 'tipo de peticion', 'Utemporal','Cantidad_peticiones'])
        self.matrix = pd.DataFrame(
            columns=['Estacion origen', 'Estacion final', 'tipo de peticion', 'Utemporal', 'Cantidad_peticiones'])
        #self.numpyData = np.array(self.matrix)
        self.lista = []


    def add_row(self,row:list):
        #self.numpyData = np.vstack([self.numpyData , row])
        self.lista.append(row)


    def create_Dataframe(self):
        self.matrix = pd.DataFrame(self.lista,
            columns=['Estacion origen', 'Estacion final', 'tipo de peticion', 'Utemporal', 'Cantidad_peticiones'])


    def getCantidadPeticiones(self, fila:int):
        return self.matrix.iloc[fila, Constantes.MATRIZDESPLAZAMIENTOS_PETICIONES]

    def getUTemporal(self, fila:int):
        return self.matrix.iloc[fila, Constantes.MATRIZDESPLAZAMIENTOS_UTEMPORAL]


class Ocupacion_Horas:

   def __init__(self, matrizOcupacion:pd.DataFrame):

       delta_horas = (60 / Constantes.DELTA_TIME)

       matrizOcupacion.index = np.arange(0,len(matrizOcupacion))
       self.matrix = matrizOcupacion.groupby(matrizOcupacion.index // delta_horas).sum() / (60 / Constantes.DELTA_TIME)
       self.matrix = self.matrix.drop(self.matrix.columns[[0]], axis=1)
       self.matrix.insert(0, 'hora' , range(0,len(self.matrix)))
