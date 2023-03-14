import numpy as np


def realizarMediaPesos(lista:list):

    np_lista = np.array(lista)
    sumaTotal = np_lista.sum()

    return (np_lista/sumaTotal).tolist()

