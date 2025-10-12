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

# ==============================
# FUNCIONES
# ==============================
def guardar_conocimiento(base):
    with open(ARCHIVO_CONOCIMIENTO, "w", encoding="utf-8") as f:
        json.dump(base, f, indent=4, ensure_ascii=False)

def cargar_conocimiento():
    if not os.path.exists(ARCHIVO_CONOCIMIENTO):
        guardar_conocimiento(base_inicial)
    with open(ARCHIVO_CONOCIMIENTO, "r", encoding="utf-8") as f:
        return json.load(f)

def comparar_personaje(respuestas_usuario, caracteristicas_personaje):
    coincidencias = 0
    for clave in respuestas_usuario:
        if respuestas_usuario[clave] == caracteristicas_personaje[clave]:
            coincidencias += 1
        elif respuestas_usuario[clave] in ["Probablemente", "No lo se"]:
            coincidencias += 0.5
    return coincidencias / len(respuestas_usuario)

# ==============================
# CLASE PRINCIPAL
# ==============================
class JuegoHollowKnight(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Adivina Quién - Hollow Knight Edition")
        self.geometry("1280x768")
        self.resizable(False, False)

        # Fondo
        if os.path.exists(FONDO_PATH):
            self.bg_image = ctk.CTkImage(Image.open(FONDO_PATH), size=(1280, 768))
            self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
            self.bg_label.place(relx=0.5, rely=0.5, anchor="center")

        self.base = cargar_conocimiento()
        self.respuestas = {}
        self.indice_pregunta = 0

        self.frame_principal = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_principal.place(relx=0.5, rely=0.5, anchor="center")

        self.crear_menu_principal()

    # ==========================
    # MENÚ PRINCIPAL
    # ==========================
    def crear_menu_principal(self):
        for widget in self.frame_principal.winfo_children():
            widget.destroy()

        titulo = ctk.CTkLabel(
            self.frame_principal,
            text="Adivina Quién\nEdición Personajes de Hollow Knight",
            font=("Cinzel Decorative", 22, "bold"),
            text_color="#E5E5E5",
            justify="center"
        )
        titulo.pack(pady=40)

        ctk.CTkButton(
            self.frame_principal,
            text="Jugar",
            corner_radius=20,
            fg_color="#B0B0B0",
            hover_color="#8F8F8F",
            text_color="black",
            command=self.iniciar_juego
        ).pack(pady=10, ipadx=10, ipady=5)

        ctk.CTkButton(
            self.frame_principal,
            text="Salir",
            corner_radius=20,
            fg_color="#B0B0B0",
            hover_color="#8F8F8F",
            text_color="black",
            command=self.destroy
        ).pack(pady=10, ipadx=10, ipady=5)

    # ==========================
    # JUEGO
    # ==========================
    def iniciar_juego(self):
        for widget in self.frame_principal.winfo_children():
            widget.destroy()

        self.respuestas = {}
        self.indice_pregunta = 0

        self.label = ctk.CTkLabel(self.frame_principal, text=preguntas[0],
                                  font=("Cinzel Decorative", 18), wraplength=500)
        self.label.pack(pady=30)

        self.frame_botones = ctk.CTkFrame(self.frame_principal, fg_color="transparent")
        self.frame_botones.pack()

        self.mostrar_pregunta()

    def mostrar_pregunta(self):
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
        self.respuestas[claves[self.indice_pregunta]] = respuesta
        self.indice_pregunta += 1
        self.mostrar_pregunta()

    def mostrar_resultado(self):
        puntajes = {nombre: comparar_personaje(self.respuestas, caract)
                    for nombre, caract in self.base.items()}
        mejor = max(puntajes, key=puntajes.get)
        self.personaje_predicho = mejor

        for widget in self.frame_botones.winfo_children():
            widget.destroy()

        self.label.configure(text=f"Creo que tu personaje es: {mejor}")

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
        if messagebox.askyesno("Jugar otra vez", "¡Genial! ¿Quieres jugar de nuevo?"):
            self.iniciar_juego()
        else:
            self.crear_menu_principal()

    def no_acerto(self):
        for widget in self.frame_botones.winfo_children():
            widget.destroy()
        self.label.configure(text="¿Cuál era tu personaje?")
        self.entry_nombre = ctk.CTkEntry(self.frame_principal, placeholder_text="Escribe aquí el nombre...")
        self.entry_nombre.pack(pady=10)
        ctk.CTkButton(self.frame_principal, text="Continuar",
                      corner_radius=20, fg_color="#B0B0B0", hover_color="#8F8F8F",
                      text_color="black", command=self.aprender_personaje).pack(pady=5)

    def aprender_personaje(self):
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
        self.respuestas_aprendizaje[claves[self.indice_aprendizaje]] = respuesta
        self.indice_aprendizaje += 1
        self.preguntar_aprendizaje()

# ==============================
# EJECUCIÓN
# ==============================
app = JuegoHollowKnight()
app.mainloop()
