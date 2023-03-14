import io
import os
import sys
import imageio
import numpy as np
import pandas as pd
import plotly.express as px
from PIL import Image
import plotly.io as pio
from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets

#Clase para la representacion con folium
class Representar2:

    def __init__(self,coordenadas:np.ndarray):
        self.datos = pd.DataFrame()
        self.coordenadas = pd.DataFrame(coordenadas,columns=["Estacion","Lat","Long"])
        self.textBox = QtWidgets.QSpinBox()
        self.textBox.setMaximum(2**31-1)
        self.mainWindow = None
        self.mainApp = None

        self.instanteActual = 0

    def interfazWeb(self, fig,instancias_max=None):
        html = pio.to_html(fig, full_html=False)
        fig.write_html('density_mapbox.html', auto_open=False)
        app = QtWidgets.QApplication(sys.argv)
        self.mainApp=app

        view = QtWebEngineWidgets.QWebEngineView()
        view.load(QtCore.QUrl().fromLocalFile(
            os.getcwd() + "\\density_mapbox.html"
        ))
        view.resize(800, 800)

        view.show()

        main_window = QtWidgets.QMainWindow()
        main_window.resize(800,800)
        main_window.setCentralWidget(view)
        main_window.show()

        control_frame = QtWidgets.QFrame()
        control_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        control_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        control_layout = QtWidgets.QHBoxLayout()
        control_frame.setLayout(control_layout)

        #----------------------#

        if instancias_max != None:
            label = QtWidgets.QLabel("/"+instancias_max)
        else:
            label = QtWidgets.QLabel("/")

        self.textBox.setValue(self.instanteActual)
        button = QtWidgets.QPushButton("Recargar Mapa")
        button.clicked.connect(lambda: self.botonPulsado())
        # Agregar los widgets al frame

        control_layout.addWidget(self.textBox)
        control_layout.addWidget(label)
        control_layout.addWidget(button)

        # Agregar el frame al dock widget
        dock = QtWidgets.QDockWidget("Controles", main_window)
        dock.setWidget(control_frame)
        main_window.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock)

        self.mainWindow = view
        app.exec_()


    def botonPulsado(self):
        mapa = self.__getMapFigure(int(self.textBox.text()),12)
        mapa.write_html('density_mapbox2.html', auto_open=False)

        self.mainWindow.load(QtCore.QUrl().fromLocalFile(
            os.getcwd() + "\\density_mapbox2.html"
        ))



    def cargarDatos(self, datos:pd.DataFrame):
        self.datos= datos

    # Función de pruba para mostrar un histograma con leyenda.
    def __getMapFigure(self,instante,zoom):
        datos = self.coordenadas.copy()
        datos.insert(3, "Datos", self.datos.iloc[instante, :].values.tolist())
        # Representar en el mapa.
        fig = px.density_mapbox(datos, lat="Lat", lon="Long", z="Datos", radius=25,
                                center=dict(lat=self.coordenadas.iloc[172][1], lon=self.coordenadas.iloc[172][2]),
                                zoom=zoom,
                                mapbox_style="stamen-terrain",

                                hover_data={'Estacion': True})
        fig.update_layout(mapbox=dict(center=dict(lat=self.coordenadas.iloc[172][1], lon=self.coordenadas.iloc[172][2]), zoom=zoom),
                          width=800, height=600, margin={"r": 0, "t": 0, "l": 0, "b": 0})
        return fig

    def representarHeatmap(self, instante=None , instancias_max = None):
        if instante == None:
            instante = self.instanteActual
        else:
            self.instanteActual = instante
        fig = self.__getMapFigure(instante,12)
        ##self.pruebaInterfaz(fig)
        self.interfazWeb(fig,instancias_max)
        fig.show()


    def realizarVideoHeatmap(self,indice_inicio,indice_final):

        # Genera los frames del video
        listaImagenes = []
        for i in range(indice_inicio,indice_final+1):##Check this.

            fig = self.__getMapFigure(i,12)
            # Agrega el frame actual al video
            fig_bytes = fig.to_image(format='png')
            listaImagenes.append(np.array(Image.open(io.BytesIO(fig_bytes))))

        writer = imageio.get_writer('video.mp4',fps=2)
        for imagen in listaImagenes:
            writer.append_data(imagen)
        writer.close()

