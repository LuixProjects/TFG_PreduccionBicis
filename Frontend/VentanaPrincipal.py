from Backend import Constantes
from Frontend.Ventana import Ventana
import customtkinter as tk

class VentanaPrincipal(Ventana):

    def __init__(self):
        super().__init__("Ventana principal")
        self.directorios = [None]*6
        ventana = super().getVentanaAttribute()

        self.textoDelta = tk.CTkTextbox(master=ventana, height=10)
        self.textoCapacidad = tk.CTkTextbox(master=ventana, height=10)
        self.textoCercanasIndices= tk.CTkTextbox(master=ventana, height=10)
        self.textoCercanasKms = tk.CTkTextbox(master=ventana, height=10)
        self.textoCoordenadas = tk.CTkTextbox(master=ventana, height=10)
        self.textbox_deltaTime = tk.CTkTextbox(master=ventana, height=5, width=135)
        self.textoTendencias = tk.CTkTextbox(master=ventana, height=10)
        self.establecerDeltaTime(ventana)
        self.cargarTextoDatos()
        self.botonCargarDatos(ventana)
        self.titulo(ventana)
        self.textoExplicacion(ventana)
        super().ejecutarVentana()


    def cargarTextoDatos(self):
        self.textoDelta.place(relx = 0.3,rely=0.4,anchor=tk.CENTER)
        self.textoDelta.insert("0.0" , "Sin fichero")


        self.textoCapacidad.place(relx=0.3, rely=0.5, anchor=tk.CENTER)
        self.textoCapacidad.insert("0.0", "Sin fichero")


        self.textoCercanasIndices.place(relx=0.3, rely=0.6, anchor=tk.CENTER)
        self.textoCercanasIndices.insert("0.0", "Sin fichero")


        self.textoCercanasKms.place(relx=0.3, rely=0.7, anchor=tk.CENTER)
        self.textoCercanasKms.insert("0.0", "Sin fichero")


        self.textoCoordenadas.place(relx=0.3, rely=0.8, anchor=tk.CENTER)
        self.textoCoordenadas.insert("0.0", "Sin fichero")


        self.textoTendencias.place(relx=0.3, rely=0.9, anchor=tk.CENTER)
        self.textoTendencias.insert("0.0", "Sin fichero")


    def establecerDeltaTime(self,ventana):
        titulo = tk.CTkLabel(
            master=ventana,
            text="Seleccione el delta time:",
            font=("Arial", 20),
        )
        titulo.place(relx=0.8, rely=0.3)
        self.textbox_deltaTime.place(relx=0.8, rely=0.35)


    def botonCargarDatos(self,ventana):
        ##Boton deltas:
        boton_delta = tk.CTkButton(master = ventana, text="Cargar Archivo Delta",command=lambda:self.__cargarFicheroDelta(ventana,0))
        boton_delta.place(relx=0.7,rely=0.4,anchor= tk.CENTER)

        #Boton capacidades
        boton_capacidad = tk.CTkButton(master=ventana, text="Cargar Archivo Capacidad",
                             command=lambda: self.__cargarFicheroDelta(ventana,1))
        boton_capacidad.place(relx=0.7, rely=0.5, anchor=tk.CENTER)

        #Boton cercanas_indices
        boton_cercanas_indices = tk.CTkButton(master=ventana, text="Cargar Archivo Cercanas_indices",
                             command=lambda: self.__cargarFicheroDelta(ventana,2))
        boton_cercanas_indices.place(relx=0.7, rely=0.6, anchor=tk.CENTER)

        #Boton cercanas_kms
        boton_cercanas_kms = tk.CTkButton(master=ventana, text="Cargar Archivo Cercanas_kms",
                             command=lambda: self.__cargarFicheroDelta(ventana,3))
        boton_cercanas_kms.place(relx=0.7, rely=0.7, anchor=tk.CENTER)

        #Boton coordenadas
        boton_coordenadas = tk.CTkButton(master=ventana, text="Cargar Archivo Coordenadas",
                             command=lambda: self.__cargarFicheroDelta(ventana,4))
        boton_coordenadas.place(relx=0.7, rely=0.8, anchor=tk.CENTER)
        #Boton tendencias

        boton_tendencias = tk.CTkButton(master=ventana, text="Cargar Archivo Tendencias",
                             command=lambda: self.__cargarFicheroDelta(ventana,5))
        boton_tendencias.place(relx=0.7, rely=0.9, anchor=tk.CENTER)

        #Boton_enviar_datos
        boton_enviar_datos= tk.CTkButton(master=ventana, text="Revisar y Enviar Datos",
                                        command=lambda: self.__comprobarDatos(ventana))
        boton_enviar_datos.place(relx=0.5, rely=0.95, anchor=tk.CENTER)

    def titulo(self,ventana):
        titulo = tk.CTkLabel(
            master = ventana,
            text = "Carga de datos",
            font=("Arial",70),
        )
        titulo.place(relx=0.5,rely=0.2,anchor=tk.CENTER)

    def textoExplicacion(self,ventana):
        texto = tk.CTkLabel(
            master = ventana,
            text = "Por favor, introduzca los datos",
            font = ("Arial",20))

        texto.place(relx=0.4,rely=0.3,anchor=tk.CENTER)

    def __cargarFicheroDelta(self,ventana,boton):

        directorio = tk.filedialog.askopenfilenames()
        print(directorio)
        listaTextos = [self.textoDelta,self.textoCapacidad,self.textoCercanasIndices,self.textoCercanasKms,self.textoCoordenadas,self.textoTendencias]
        listaTextos[boton].delete("0.0","end")
        listaTextos[boton].insert("0.0",directorio[0])
        self.directorios[boton] = directorio[0]
        listaTextos[boton].update()
        Constantes.DELTA_TIME= int(self.textbox_deltaTime.get("0.0",'end-1c'))

    def __comprobarDatos(self,ventana):
        listaTextos = [self.textoDelta,self.textoCapacidad,self.textoCercanasIndices,self.textoCercanasKms,self.textoCoordenadas,self.textoTendencias]
        listaRutas = []
        for texto in listaTextos:
            if not texto.get("0.0", "end").__contains__("Sin fichero"):
                listaRutas.append(texto.get("0.0", "end"))

        #Si falta algun fichero:
        if len(listaRutas) < 6:
            dialog = tk.CTkInputDialog(text="ERROR: NO SE HA INTRODUCIDO TODOS LOS DATOS", title="ERROR")
            listaRutas.clear()

        if self.textbox_deltaTime.get("0.0",'end-1c') == "":
            dialog = tk.CTkInputDialog(text="ERROR: DELTA NO INTRODUCIDA", title="ERROR")


        else:
            ventana.quit()
