import pandas as pd


#Función encargada de agrupar un conjunto de matrices. El único requisito es que estas matrices tengan el mismo delta y mismo tamaño.
def agruparMatrices(matriz1:pd.DataFrame,matriz2:pd.DataFrame):
    nuevoDataframe = matriz1.iloc[:,1:] + abs(matriz2.iloc[:,1:])
    nuevoDataframe.insert(0,"UTemporal",range(nuevoDataframe.shape[0]),True)
    return nuevoDataframe

#Funcion encargada de colapsar una matriz y pasar de un delta a otro.
def colapsarDeltasMedia(matriz:pd.DataFrame,deltaActual,deltaDeseado):
    colapsarCadaDelta = deltaDeseado / deltaActual #Numero de deltas a colapsar.
    matrizColapsada = matriz.iloc[:,1:].groupby(matriz.index // colapsarCadaDelta).sum()/colapsarCadaDelta
    matrizColapsada.insert(0, "UTemporal", range(matrizColapsada.shape[0]), True)
    return matrizColapsada
#np.logical_and(Agrupador.colapsarDeltasMedia(matrices[Constantes.OCUPACION].matrix, 15, 60).iloc[:,1:].to_numpy(),matrices[Constantes.OCUPACION_HORAS].matrix.iloc[:,1:].to_numpy())
def colapsarDeltasAcumulacion(matriz:pd.DataFrame,deltaActual,deltaDeseado):
    colapsarCadaDelta = deltaDeseado / deltaActual  # Numero de deltas a colapsar.
    matrizColapsada = matriz.iloc[:, 1:].groupby(matriz.index // colapsarCadaDelta).sum()
    matrizColapsada.insert(0, "UTemporal", range(matrizColapsada.shape[0]), True)
    return matrizColapsada