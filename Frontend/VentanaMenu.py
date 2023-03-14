from tkinter import Menu

from Backend import Constantes
from Frontend.Ventana import Ventana
import customtkinter as tk

from Frontend.VentanaEstadisticas import VentanaEstadisticas
from Frontend.VentanaMapa import VentanaMapa


class VentanaMenu(Ventana):

    def __init__(self,soluciones:dict,matrices:dict):
        super().__init__("Centro de mando")
        self.soluciones = soluciones
        self.matrices = matrices
        ventana = super().getVentanaAttribute()
        self.__titulo(ventana)
        self.__ResumenEjecucion(ventana)
        self.__menu(ventana)
        super().ejecutarVentana()

    def __titulo(self,ventana):
        titulo = tk.CTkLabel(
            master = ventana,
            text = "Centro de control",
            font=("Arial",70),
        )
        titulo.place(relx=0.5,rely=0.2,anchor=tk.CENTER)

    def __ResumenEjecucion(self,ventana):

        cadena = "Resumen de la ejecución\n" \
            "Kilómetros recorridos para coger una bicicleta : " + str(self.soluciones[Constantes.KMS_COGER_BICI])+"\n" \
            "Kilómetros recorridos para dejar una bicicleta : " + str(self.soluciones[Constantes.KMS_DEJAR_BICI])+"\n" \
            "Kilómetros ficticios recorridos para coger una bicicleta : " + str(self.soluciones[Constantes.KMS_FICTICIOS_COGER])+"\n" \
            "Kilómetros ficticios recorridos para dejar una bicicleta : " + str(self.soluciones[Constantes.KMS_FICTICIOS_DEJAR]) + "\n" \
            "Peticiones resueltas Reales para coger una bicicleta : " + str(self.soluciones[Constantes.PETICIONES_RESUELTAS_COGER_BICI]) + "\n" \
            "Peticiones resueltas Reales para dejar una bicicleta : " + str(self.soluciones[Constantes.PETICIONES_RESUELTAS_SOLTAR_BICI])+ "\n" \
            "Peticiones no resueltas Reales para coger una bicicleta : " + str(self.soluciones[Constantes.PETICIONES_NORESUELTAS_COGER_BICI] )+ "\n" \
            "Peticiones no resueltas Reales para dejar una bicicleta : " + str(self.soluciones[Constantes.PETICIONES_NORESUELTAS_SOLTAR_BICI]) + "\n" \
            "Peticiones no resueltas Ficticias para coger una bicicleta : " + str(self.soluciones[Constantes.PETICIONES_NORESUELTAS_FICTICIAS_COGER_BICI]) + "\n" \
            "Peticiones no resueltas Ficticias para dejar una bicicleta : " + str(self.soluciones[Constantes.PETICIONES_NORESUELTAS_FICTICIAS_DEJAR_BICI]) + "\n"
        texto = tk.CTkLabel(
        master = ventana,
        text = cadena,
        font = ("Arial",20),
        justify = tk.LEFT)

        texto.place(relx=0.5,rely=0.5,anchor=tk.CENTER)

    def __menu(self,ventana):
        menubar = Menu(ventana)

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=donothing)
        filemenu.add_command(label="Open", command=donothing)
        filemenu.add_command(label="Save", command=donothing)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=ventana.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        mapas_menu = Menu(menubar, tearoff=0)
        mapas_menu.add_command(label="Mapa de Calor", command=lambda:self.__abrirVentanaMapa())
        mapas_menu.add_command(label="Mapa Voronoi", command=donothing)

        estadisticas_menu = Menu(menubar,tearoff=0)
        estadisticas_menu.add_command(label="Estadisticas", command=lambda:self.__abrirVentenaEstadistica())

        menubar.add_cascade(label="Estadisticas",menu=estadisticas_menu)
        menubar.add_cascade(label="Mapas", menu=mapas_menu)
        ventana.config(menu=menubar)

    def __abrirVentanaMapa(self):
        VentanaMapa(self.matrices)

    def __abrirVentenaEstadistica(self):
        VentanaEstadisticas(self.matrices)

def donothing():
    x=0