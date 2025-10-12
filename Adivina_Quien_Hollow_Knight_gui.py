import json
import os
import sys
import tkinter as tk
from tkinter import messagebox

# =========================================
# RUTAS Y ARCHIVOS
# =========================================
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ARCHIVO_CONOCIMIENTO = os.path.join(BASE_DIR, "hollow_knight_data.json")

# =========================================
# BASE DE CONOCIMIENTO INICIAL
# =========================================
base_inicial = {
    "Hornet": {
        "arma_aguijon": "Si",
        "arma_infeccion": "No",
        "rol_jefe": "Si",
        "es_enemigo": "No",
        "aparece_multiples": "Si"
    },
    "Señores Mantis": {
        "arma_aguijon": "Si",
        "arma_infeccion": "No",
        "rol_jefe": "Si",
        "es_enemigo": "Si",
        "aparece_multiples": "No"
    },
    "Zote": {
        "arma_aguijon": "Si",
        "arma_infeccion": "No",
        "rol_jefe": "Si",
        "es_enemigo": "Si",
        "aparece_multiples": "Si"
    },
    "Último Ciervo": {
        "arma_aguijon": "No",
        "arma_infeccion": "No",
        "rol_jefe": "No",
        "es_enemigo": "No",
        "aparece_multiples": "Si"
    },
    "Rey Pálido": {
        "arma_aguijon": "No",
        "arma_infeccion": "No",
        "rol_jefe": "No",
        "es_enemigo": "No",
        "aparece_multiples": "No"
    }
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

# =========================================
# CLASE PRINCIPAL DEL JUEGO (INTERFAZ)
# =========================================
class JuegoAdivinaQuien:
    def __init__(self, root):
        self.root = root
        self.root.title("¿Adivina Quién? - Hollow Knight Edition")
        self.root.geometry("550x400")
        self.root.resizable(False, False)

        self.base = cargar_conocimiento()
        self.respuestas = {}
        self.indice_pregunta = 0

        self.label = tk.Label(root, text="Bienvenido a ¿Adivina Quién?\nPresiona 'Comenzar' para jugar",
                              font=("Arial", 14), wraplength=500, justify="center")
        self.label.pack(pady=40)

        self.frame_botones = tk.Frame(root)
        self.frame_botones.pack()

        self.boton_comenzar = tk.Button(root, text="Comenzar", font=("Arial", 12, "bold"), command=self.iniciar_juego)
        self.boton_comenzar.pack(pady=20)

    def iniciar_juego(self):
        self.boton_comenzar.pack_forget()
        self.mostrar_pregunta()

    def mostrar_pregunta(self):
        if self.indice_pregunta < len(preguntas):
            self.label.config(text=preguntas[self.indice_pregunta])
            for widget in self.frame_botones.winfo_children():
                widget.destroy()
            opciones = ["Si", "No", "No lo se", "Probablemente"]
            for opcion in opciones:
                tk.Button(self.frame_botones, text=opcion, width=20, height=2,
                          command=lambda o=opcion: self.registrar_respuesta(o)).pack(pady=5)
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
        self.label.config(text=f"Creo que tu personaje es: {mejor}")

        tk.Button(self.frame_botones, text="Sí", width=20, height=2,
                  command=self.confirmar_acierto).pack(pady=5)
        tk.Button(self.frame_botones, text="No", width=20, height=2,
                  command=self.no_acerto).pack(pady=5)

    def confirmar_acierto(self):
        if messagebox.askyesno("Jugar otra vez", "¡Genial! ¿Quieres jugar de nuevo?"):
            self.reiniciar_juego()
        else:
            self.root.destroy()

    def no_acerto(self):
        for widget in self.frame_botones.winfo_children():
            widget.destroy()
        self.label.config(text="¿Cuál era tu personaje?")
        self.entry_nombre = tk.Entry(self.root, font=("Arial", 12))
        self.entry_nombre.pack(pady=10)
        tk.Button(self.root, text="Continuar", command=self.aprender_personaje).pack(pady=5)

    def aprender_personaje(self):
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            messagebox.showerror("Error", "Debes ingresar un nombre.")
            return
        self.entry_nombre.pack_forget()
        for widget in self.frame_botones.winfo_children():
            widget.destroy()
        self.entry_nombre.destroy()
        self.nuevo_personaje = nombre
        self.respuestas_aprendizaje = {}
        self.indice_aprendizaje = 0
        self.preguntar_aprendizaje()

    def preguntar_aprendizaje(self):
        if self.indice_aprendizaje < len(preguntas):
            self.label.config(text=preguntas[self.indice_aprendizaje])
            for widget in self.frame_botones.winfo_children():
                widget.destroy()
            opciones = ["Si", "No", "No lo se", "Probablemente"]
            for opcion in opciones:
                tk.Button(self.frame_botones, text=opcion, width=20, height=2,
                          command=lambda o=opcion: self.registrar_aprendizaje(o)).pack(pady=5)
        else:
            self.base[self.nuevo_personaje] = self.respuestas_aprendizaje
            guardar_conocimiento(self.base)
            messagebox.showinfo("Aprendido", f"He aprendido sobre {self.nuevo_personaje}. ¡Gracias!")
            self.reiniciar_juego()

    def registrar_aprendizaje(self, respuesta):
        self.respuestas_aprendizaje[claves[self.indice_aprendizaje]] = respuesta
        self.indice_aprendizaje += 1
        self.preguntar_aprendizaje()

    def reiniciar_juego(self):
        self.respuestas = {}
        self.indice_pregunta = 0
        self.label.config(text="Presiona 'Comenzar' para jugar nuevamente")
        for widget in self.frame_botones.winfo_children():
            widget.destroy()
        self.boton_comenzar.pack(pady=20)


# =========================================
# EJECUCIÓN
# =========================================

root = tk.Tk()
app = JuegoAdivinaQuien(root)
root.mainloop()
