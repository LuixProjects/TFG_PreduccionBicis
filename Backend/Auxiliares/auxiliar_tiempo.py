#Función que devuelve en que delta corresponde el inicio de un dia de comienzo y el dinal de un dia final.
def diaToDelta(diaComienzo:int,diaFinal:int,delta:int):

    delta_dia = (60/delta) * 24
    return ( (diaComienzo*delta_dia), (diaFinal * delta_dia) + delta_dia - 1)