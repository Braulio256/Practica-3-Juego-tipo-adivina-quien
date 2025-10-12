import os
import sys
import json
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image

# ==============================
# CONFIGURACIÓN INICIAL
# ==============================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ARCHIVO_CONOCIMIENTO = os.path.join(BASE_DIR, "hollow_knight_data.json")
FONDO_PATH = os.path.join(BASE_DIR, "fondo.jpg")
FUENTE_PATH = os.path.join(BASE_DIR, "CinzelDecorative-Regular.ttf")

base_inicial = {
    "Hornet": {"arma_aguijon": "Si", "arma_infeccion": "No", "rol_jefe": "Si", "es_enemigo": "No", "aparece_multiples": "Si"},
    "Zote": {"arma_aguijon": "Si", "arma_infeccion": "No", "rol_jefe": "Si", "es_enemigo": "Si", "aparece_multiples": "Si"},
    "Señores Mantis": {"arma_aguijon": "Si", "arma_infeccion": "No", "rol_jefe": "Si", "es_enemigo": "Si", "aparece_multiples": "No"}
}

preguntas = [
    "¿El arma que utiliza es un aguijón?",
    "¿El arma que utiliza es parte de la infección?",
    "¿El rol del personaje es de Jefe?",
    "¿Tu personaje es un enemigo?",
    "¿Tu personaje aparece múltiples veces en el juego?"
]
claves = ["arma_aguijon", "arma_infeccion", "rol_jefe", "es_enemigo", "aparece_multiples"]

# =========================================
# FUNCIONES DE UTILIDAD
# =========================================
def guardar_conocimiento(base):
    """Guarda la base de conocimiento en un archivo JSON."""
    with open(ARCHIVO_CONOCIMIENTO, "w", encoding="utf-8") as f:
        json.dump(base, f, indent=4, ensure_ascii=False)

def cargar_conocimiento():
    """Carga la base de conocimiento desde el archivo, si no existe lo crea."""
    if not os.path.exists(ARCHIVO_CONOCIMIENTO):
        guardar_conocimiento(base_inicial)
    with open(ARCHIVO_CONOCIMIENTO, "r", encoding="utf-8") as f:
        return json.load(f)

def comparar_personaje(respuestas_usuario, caracteristicas_personaje):
    """Calcula la coincidencia entre las respuestas del usuario y un personaje."""
    coincidencias = 0
    for clave in respuestas_usuario:
        if respuestas_usuario[clave] == caracteristicas_personaje[clave]:
            coincidencias += 1
        elif respuestas_usuario[clave] in ["Probablemente", "No lo se"]:
            coincidencias += 0.5
    return coincidencias / len(respuestas_usuario)

# =========================================
# CLASE PRINCIPAL DEL JUEGO
# =========================================
class JuegoHollowKnight(ctk.CTk):
    def __init__(self):
        super().__init__()

        # =========================================
        # CONFIGURACIÓN DE LA VENTANA
        # =========================================
        self.title("Adivina Quién - Hollow Knight Edition")
        self.geometry("1280x768")   # Resolución deseada
        self.resizable(False, False)

        # Centrar la ventana en la pantalla
        self.update_idletasks()
        ancho_ventana = 1280
        alto_ventana = 768
        x = (self.winfo_screenwidth() // 2) - (ancho_ventana // 2)
        y = (self.winfo_screenheight() // 2) - (alto_ventana // 2)
        self.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")

        # =========================================
        # CARGA DE IMAGEN DE FONDO
        # =========================================
        if os.path.exists(FONDO_PATH):
            self.bg_image = ctk.CTkImage(Image.open(FONDO_PATH), size=(1280, 768))
            self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
            self.bg_label.place(relx=0.5, rely=0.5, anchor="center")

        # =========================================
        # VARIABLES DEL JUEGO
        # =========================================
        self.base = cargar_conocimiento()
        self.respuestas = {}
        self.indice_pregunta = 0

        # Frame principal para mostrar botones, títulos y entradas
        self.frame_principal = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_principal.place(relx=0.5, rely=0.5, anchor="center")

        # Crear menú principal
        self.crear_menu_principal()

    # =========================================
    # MENÚ PRINCIPAL
    # =========================================
    def crear_menu_principal(self):
        """Genera el menú con título, botón Jugar y Salir."""
        for widget in self.frame_principal.winfo_children():
            widget.destroy()

        # Título en la parte superior con fondo transparente
        titulo = ctk.CTkLabel(
            self.frame_principal,
            text="Adivina Quién\nEdición Personajes de Hollow Knight",
            font=("Cinzel Decorative", 28, "bold"),
            text_color="#E5E5E5",
            fg_color="transparent",
            justify="center"
        )
        titulo.pack(pady=(20, 60))  # Separación superior para que quede en la parte alta

        # Botón Jugar
        ctk.CTkButton(
            self.frame_principal,
            text="Jugar",
            corner_radius=20,
            fg_color="#B0B0B0",
            hover_color="#8F8F8F",
            text_color="black",
            command=self.iniciar_juego
        ).pack(pady=10, ipadx=10, ipady=5)

        # Botón Salir
        ctk.CTkButton(
            self.frame_principal,
            text="Salir",
            corner_radius=20,
            fg_color="#B0B0B0",
            hover_color="#8F8F8F",
            text_color="black",
            command=self.destroy
        ).pack(pady=10, ipadx=10, ipady=5)

    # =========================================
    # INICIO DEL JUEGO
    # =========================================
    def iniciar_juego(self):
        """Inicializa las variables y muestra la primera pregunta."""
        for widget in self.frame_principal.winfo_children():
            widget.destroy()

        self.respuestas = {}
        self.indice_pregunta = 0

        # Label para la pregunta
        self.label = ctk.CTkLabel(self.frame_principal, text=preguntas[0],
                                  font=("Cinzel Decorative", 20), wraplength=1000)
        self.label.pack(pady=30)

        # Frame para botones de respuestas
        self.frame_botones = ctk.CTkFrame(self.frame_principal, fg_color="transparent")
        self.frame_botones.pack()

        self.mostrar_pregunta()

    def mostrar_pregunta(self):
        """Muestra la pregunta actual y sus opciones de respuesta."""
        if self.indice_pregunta < len(preguntas):
            self.label.configure(text=preguntas[self.indice_pregunta])
            for widget in self.frame_botones.winfo_children():
                widget.destroy()

            opciones = ["Si", "No", "No lo se", "Probablemente"]
            for opcion in opciones:
                ctk.CTkButton(
                    self.frame_botones, text=opcion,
                    corner_radius=20,
                    fg_color="#B0B0B0",
                    hover_color="#8F8F8F",
                    text_color="black",
                    command=lambda o=opcion: self.registrar_respuesta(o)
                ).pack(pady=5, ipadx=5, ipady=2)
        else:
            self.mostrar_resultado()

    def registrar_respuesta(self, respuesta):
        """Registra la respuesta del usuario y pasa a la siguiente pregunta."""
        self.respuestas[claves[self.indice_pregunta]] = respuesta
        self.indice_pregunta += 1
        self.mostrar_pregunta()

    # =========================================
    # RESULTADO
    # =========================================
    def mostrar_resultado(self):
        """Calcula el personaje más probable y muestra opciones de confirmación."""
        puntajes = {nombre: comparar_personaje(self.respuestas, caract)
                    for nombre, caract in self.base.items()}
        mejor = max(puntajes, key=puntajes.get)
        self.personaje_predicho = mejor

        for widget in self.frame_botones.winfo_children():
            widget.destroy()

        self.label.configure(text=f"Creo que tu personaje es: {mejor}")

        # Botones de confirmación
        ctk.CTkButton(
            self.frame_botones, text="Sí", corner_radius=20,
            fg_color="#B0B0B0", hover_color="#8F8F8F", text_color="black",
            command=self.confirmar_acierto
        ).pack(pady=5)
        ctk.CTkButton(
            self.frame_botones, text="No", corner_radius=20,
            fg_color="#B0B0B0", hover_color="#8F8F8F", text_color="black",
            command=self.no_acerto
        ).pack(pady=5)

    def confirmar_acierto(self):
        """Si el personaje fue acertado, pregunta si desea jugar de nuevo o volver al menú."""
        if messagebox.askyesno("Jugar otra vez", "¡Genial! ¿Quieres jugar de nuevo?"):
            self.iniciar_juego()
        else:
            self.crear_menu_principal()

    def no_acerto(self):
        """Si el personaje no fue acertado, permite al usuario agregar un nuevo personaje."""
        for widget in self.frame_botones.winfo_children():
            widget.destroy()
        self.label.configure(text="¿Cuál era tu personaje?")
        self.entry_nombre = ctk.CTkEntry(self.frame_principal, placeholder_text="Escribe aquí el nombre...")
        self.entry_nombre.pack(pady=10)
        ctk.CTkButton(self.frame_principal, text="Continuar",
                      corner_radius=20, fg_color="#B0B0B0", hover_color="#8F8F8F",
                      text_color="black", command=self.aprender_personaje).pack(pady=5)

    def aprender_personaje(self):
        """Inicia la secuencia de aprendizaje de un nuevo personaje."""
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            messagebox.showerror("Error", "Debes ingresar un nombre.")
            return

        self.entry_nombre.destroy()
        self.respuestas_aprendizaje = {}
        self.indice_aprendizaje = 0
        self.nuevo_personaje = nombre
        self.preguntar_aprendizaje()

    def preguntar_aprendizaje(self):
        """Pregunta las características del nuevo personaje para aprender."""
        if self.indice_aprendizaje < len(preguntas):
            self.label.configure(text=preguntas[self.indice_aprendizaje])
            for widget in self.frame_botones.winfo_children():
                widget.destroy()
            opciones = ["Si", "No", "No lo se", "Probablemente"]
            for opcion in opciones:
                ctk.CTkButton(
                    self.frame_botones, text=opcion,
                    corner_radius=20, fg_color="#B0B0B0",
                    hover_color="#8F8F8F", text_color="black",
                    command=lambda o=opcion: self.registrar_aprendizaje(o)
                ).pack(pady=5)
        else:
            self.base[self.nuevo_personaje] = self.respuestas_aprendizaje
            guardar_conocimiento(self.base)
            messagebox.showinfo("Aprendido", f"He aprendido sobre {self.nuevo_personaje}. ¡Gracias!")
            self.crear_menu_principal()

    def registrar_aprendizaje(self, respuesta):
        """Registra la respuesta del nuevo personaje y pasa a la siguiente pregunta."""
        self.respuestas_aprendizaje[claves[self.indice_aprendizaje]] = respuesta
        self.indice_aprendizaje += 1
        self.preguntar_aprendizaje()

# ==============================
# EJECUCIÓN
# ==============================
app = JuegoHollowKnight()
app.mainloop()
