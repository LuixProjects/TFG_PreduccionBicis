import os

import pandas

from Backend import Constantes

from Backend.Manipuladores import Agrupador
from Backend.Manipuladores.Filtrador import Filtrador

from Frontend.VentanaMenu import VentanaMenu
from Frontend.VentanaPrincipal import VentanaPrincipal
from Backend.bike_simulator3 import bike_simulator3
from bike_simulator4 import bike_simulator4


def guardarArchivos(matrices:list[pandas.DataFrame]):
    path = os.getcwd() + "/Soluciones/"
    matrices[Constantes.OCUPACION].matrix.to_csv(path + "ocupacion_Resultado.csv")

    matrices[Constantes.KMS_FICTICIOS_COGER].matrix.to_csv(path + "kms_ficticios_coger.csv")
    matrices[Constantes.KMS_FICTICIOS_DEJAR].matrix.to_csv(path + "kms_ficticios_dejar.csv")

    matrices[Constantes.PETICIONES_NORESUELTAS_FICTICIAS_COGER_BICI].matrix.to_csv(path + "PeticionesNoResueltasFicticias_Coger.csv")
    matrices[Constantes.PETICIONES_NORESUELTAS_FICTICIAS_DEJAR_BICI].matrix.to_csv(
        path + "PeticionesNoResueltasFicticias_Coger.csv")
    matrices[Constantes.DESPLAZAMIENTOS].matrix.to_csv(path + "desplazamientos_Resultado.csv")
    matrices[
        Constantes.PETICIONES_RESUELTAS_COGER_BICI].matrix.to_csv(path + "peticionesResueltasCogerBici_Resultado.csv")
    matrices[
        Constantes.PETICIONES_RESUELTAS_SOLTAR_BICI].matrix.to_csv(path + "peticionesResueltasDejarBici_Resultado.csv")
    matrices[
        Constantes.PETICIONES_NORESUELTAS_COGER_BICI].matrix.to_csv(path + "peticionesNoResueltasCogerBici_Resultado.csv")
    matrices[
        Constantes.PETICIONES_NORESUELTAS_SOLTAR_BICI].matrix.to_csv(path + "peticionesNoResueltasSoltarBici_Resultado.csv")
    matrices[Constantes.KMS_DEJAR_BICI].matrix.to_csv(path + "peticionesKMSDejarBici_Resultado.csv")
    matrices[Constantes.KMS_COGER_BICI].matrix.to_csv(path + "peticionesKMSCogerBici_Resultado.csv")

def main():

    ventanaPrincipal = VentanaPrincipal()

    bs = bike_simulator4()
    nearest_stations_idx, nearest_stations_distance, initial_movements, real_movements,capacidadInicial,coordenadas = bs.load_data(directorios=ventanaPrincipal.directorios)

    coste,matrices = bs.evaluate_solution(capacidadInicial, initial_movements, real_movements,nearest_stations_idx, nearest_stations_distance)
    #guardarArchivos(matrices)
    ##Temporal, meter esto en otro lado

    Kms_coger = matrices[Constantes.KMS_COGER_BICI].matrix.iloc[:, 1:].sum().sum()
    Kms_dejar = matrices[Constantes.KMS_DEJAR_BICI].matrix.iloc[:, 1:].sum().sum()

    Kms_ficticios_coger = matrices[Constantes.KMS_FICTICIOS_COGER].matrix.iloc[:,1:].sum().sum()
    Kms_ficticios_dejar = matrices[Constantes.KMS_FICTICIOS_DEJAR].matrix.iloc[:, 1:].sum().sum()

    N_Peticiones_Resueltas_coger = matrices[Constantes.PETICIONES_RESUELTAS_COGER_BICI].matrix.iloc[:,1:].sum().sum()
    N_Peticiones_Resueltas_dejar = matrices[Constantes.PETICIONES_RESUELTAS_SOLTAR_BICI].matrix.iloc[:,1:].sum().sum()

    N_Peticiones_noResueltas_coger = matrices[Constantes.PETICIONES_NORESUELTAS_COGER_BICI].matrix.iloc[:,1:].sum().sum()
    N_Peticiones_noResueltas_dejar= matrices[Constantes.PETICIONES_NORESUELTAS_SOLTAR_BICI].matrix.iloc[:,1:].sum().sum()

    N_Peticiones_Ficticias_noResueltas_coger = matrices[Constantes.PETICIONES_NORESUELTAS_FICTICIAS_COGER_BICI].matrix.iloc[:,1:].sum().sum()
    N_Peticiones_Ficticias_noResueltas_dejar = matrices[Constantes.PETICIONES_NORESUELTAS_FICTICIAS_DEJAR_BICI].matrix.iloc[:,1:].sum().sum()

    soluciones = {
        Constantes.KMS_COGER_BICI:Kms_coger,
        Constantes.KMS_DEJAR_BICI:Kms_dejar,
        Constantes.KMS_FICTICIOS_COGER:Kms_ficticios_coger,
        Constantes.KMS_FICTICIOS_DEJAR:Kms_ficticios_dejar,
        Constantes.PETICIONES_NORESUELTAS_COGER_BICI:N_Peticiones_noResueltas_coger,
        Constantes.PETICIONES_NORESUELTAS_SOLTAR_BICI:N_Peticiones_noResueltas_dejar,
        Constantes.PETICIONES_NORESUELTAS_FICTICIAS_COGER_BICI:N_Peticiones_Ficticias_noResueltas_coger,
        Constantes.PETICIONES_NORESUELTAS_FICTICIAS_DEJAR_BICI:N_Peticiones_Ficticias_noResueltas_dejar,
        Constantes.PETICIONES_RESUELTAS_COGER_BICI:N_Peticiones_Resueltas_coger,
        Constantes.PETICIONES_RESUELTAS_SOLTAR_BICI:N_Peticiones_Resueltas_dejar

    }
    #End temporal


    matrices = VentanaMenu(soluciones=soluciones,matrices=matrices)


    #repre.cargarDatos(matrices[Constantes.OCUPACION_RELATIVA_HORAS].matrix.iloc[:,1:])
    #repre.representarHeatmap(0)
    #repre.realizarVideoHeatmap(0,120)
    filtrador = Filtrador(matrices[Constantes.OCUPACION_RELATIVA_HORAS].matrix,60)
    filtrador.consultarPorcentajeTiempoEstacionSuperiorAUnValor([0,1,2],50)

    Agrupador.agruparMatrices(matrices[Constantes.OCUPACION].matrix,matrices[Constantes.OCUPACION_RELATIVA].matrix)

    #FILTRADOR:
    ''' 
    filtrador = Filtrador(matrices[Constantes.OCUPACION].matrix,15)
    filtrador.consultarEstacionesSuperioresAUnValor(10,5,0)
    filtrador.consultarHorasEstacionesSuperioresAUnValor(2,20)
    '''
    #END FILTRADOR.

    #repre.cargarDatos(matrices[Constantes.OCUPACION_RELATIVA].matrix.iloc[:, 1:], "nombreMapa")
    #No funciona. repre.representarHeatmapCapas(0,matrices)
    #repre.representarHeatmap(0, "mapaInstente1")
    #repre.representarHeatmap(100, "mapaInstente100")
    #repre.crearVideo(0,96)
    ''' 
    repre.cargarDatos(matrices[Constantes.OCUPACION_HORAS].matrix.iloc[:, 1:],"ocupaciones")
    repre.representacionBasica()
    repre.representarHeatmap(0)
    repre.cargarDatos(matrices[Constantes.KMS_COGER_BICI].matrix.iloc[:, 1:], "kmsCogerBici")
    repre.representarHeatmap(0)
    repre.mapa.add_child(folium.LayerControl())
    repre.mapa.save("mapa.html")
    #repre.videoHeatmap()
   # repre.representacionVoronoi()
   # repre.crearVideo()
'''

if __name__ == '__main__':
    main()

