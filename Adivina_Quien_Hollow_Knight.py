import os
import sys
import json
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import pyglet

# ==============================
# CONFIGURACIÓN GLOBAL DE CUSTOMTKINTER
# ==============================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


# ==============================
# DEFINICIÓN DE CONSTANTES
# ==============================

def get_resource_path(relative_path):
    """
    Obtiene la ruta absoluta al RECURSO (para LEER assets).
    Funciona para desarrollo (.py) y para el .exe compilado.
    """
    if getattr(sys, 'frozen', False):
        # Si es .exe, busca en la carpeta temporal _MEIPASS
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            # Fallback por si acaso
            base_path = os.path.dirname(sys.executable)
    else:
        # Si es .py, busca en la carpeta del script
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)


def get_writable_path(relative_path):
    """
    Obtiene la ruta absoluta a un archivo ESCRIBIBLE (para GUARDAR el JSON).
    Funciona para desarrollo (.py) y para el .exe compilado.
    """
    if getattr(sys, 'frozen', False):
        # Si es .exe, guarda el archivo AL LADO del .exe
        base_path = os.path.dirname(sys.executable)
    else:
        # Si es .py, guarda el archivo al lado del script
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)


# --- Rutas a los archivos ---
# Crea la ruta completa a los archivos que usaremos

# ARCHIVO_CONOCIMIENTO usa la ruta ESCRIBIBLE
# Se creará/guardará junto al .exe
ARCHIVO_CONOCIMIENTO = get_writable_path("hollow_knight_data.json")

# FONDO_PATH y FUENTE_PATH usan la ruta de RECURSO
# Los leerá desde dentro del .exe
FONDO_PATH = get_resource_path("fondo.jpg")
FUENTE_PATH = get_resource_path("CinzelDecorative-Regular.ttf")

# --- Carga de la Fuente Personalizada ---
try:
    if os.path.exists(FUENTE_PATH):
        # Le dice a pyglet que cargue este archivo de fuente
        pyglet.font.add_file(FUENTE_PATH)
        # Este es el nombre "interno" de la fuente, que usaremos más abajo
        FONT_FAMILY = "Cinzel Decorative"
        print(f"Fuente '{FONT_FAMILY}' cargada exitosamente.")
    else:
        # Si no encuentra el archivo, usa una fuente de respaldo
        raise FileNotFoundError
except Exception as e:
    print(f"Advertencia: No se pudo cargar la fuente desde {FUENTE_PATH}. Error: {e}")
    print("Usando fuente 'Arial' por defecto.")
    FONT_FAMILY = "Arial"  # Fuente de respaldo

# --- Base de Conocimiento Inicial ---
# (El resto de tu código de constantes sigue igual)
BASE_INICIAL = {
    "Hornet": {"arma_aguijon": "Si", "arma_infeccion": "No", "rol_jefe": "Si", "es_enemigo": "No",
               "aparece_multiples": "Si"},
    "Zote": {"arma_aguijon": "Si", "arma_infeccion": "No", "rol_jefe": "Si", "es_enemigo": "Si",
             "aparece_multiples": "Si"},
    "Señores Mantis": {"arma_aguijon": "Si", "arma_infeccion": "No", "rol_jefe": "Si", "es_enemigo": "Si",
                       "aparece_multiples": "No"}
}

# --- Preguntas y Claves ---
PREGUNTAS = [
    "¿El arma que utiliza es un aguijón?",
    "¿El arma que utiliza es parte de la infección?",
    "¿El rol del personaje es de Jefe?",
    "¿Tu personaje es un enemigo?",
    "¿Tu personaje aparece múltiples veces en el juego?"
]
CLAVES = ["arma_aguijon", "arma_infeccion", "rol_jefe", "es_enemigo", "aparece_multiples"]

# =========================================
# FUNCIONES DE UTILIDAD (Manejo de Archivos y Lógica)
# =========================================
"""
Contiene las funciones auxiliares que manejan la persistencia de datos
y la lógica de comparación de respaldo.
"""


def guardar_conocimiento(base):
    try:
        with open(ARCHIVO_CONOCIMIENTO, "w", encoding="utf-8") as f:
            json.dump(base, f, indent=4, ensure_ascii=False)
    except IOError as e:
        messagebox.showerror("Error al guardar", f"No se pudo guardar el archivo de conocimiento:\n{e}")


def cargar_conocimiento():
    if not os.path.exists(ARCHIVO_CONOCIMIENTO):
        guardar_conocimiento(BASE_INICIAL)
    try:
        with open(ARCHIVO_CONOCIMIENTO, "r", encoding="utf-8") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        messagebox.showerror("Error al cargar",
                             f"No se pudo cargar el archivo de conocimiento:\n{e}\nSe usará la base inicial.")
        return BASE_INICIAL.copy()


def comparar_personaje(respuestas_usuario, caracteristicas_personaje):
    coincidencias = 0
    for clave in CLAVES:
        if clave not in caracteristicas_personaje:
            caracteristicas_personaje[clave] = "No lo se"

    for clave in respuestas_usuario:
        if respuestas_usuario[clave] == caracteristicas_personaje[clave]:
            coincidencias += 1
        elif respuestas_usuario[clave] in ["Probablemente", "No lo se"]:
            coincidencias += 0.5
    return coincidencias / len(respuestas_usuario)


# =========================================
# CLASE PRINCIPAL DE LA APLICACIÓN
# =========================================
"""
Define la ventana principal del juego (JuegoHollowKnight).
Gestiona la GUI, el estado del juego y el motor de inferencia.
"""


class JuegoHollowKnight(ctk.CTk):

    def __init__(self):
        """
        Constructor de la clase.
        - Configura la ventana principal.
        - Define las fuentes y estilos.
        - Carga la base de conocimiento e inicializa variables de estado.
        - Define la 'Memoria de Trabajo' (self.personajes_posibles).
        - Define el estado de 'fallo_logico' para el nuevo flujo de aprendizaje.
        - Crea todos los widgets de la interfaz.
        """
        super().__init__()

        self.title("Adivina Quién - Hollow Knight Edition")
        ancho_ventana = 1280
        alto_ventana = 768
        self.geometry(f"{ancho_ventana}x{alto_ventana}")
        self.resizable(False, False)

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (ancho_ventana // 2)
        y = (self.winfo_screenheight() // 2) - (alto_ventana // 2)
        self.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")

        self.title_font = ctk.CTkFont(family=FONT_FAMILY, size=28, weight="bold")
        self.label_font = ctk.CTkFont(family=FONT_FAMILY, size=20)
        self.button_font = ctk.CTkFont(family=FONT_FAMILY, size=16)

        self.button_style = {
            "corner_radius": 20,
            "fg_color": "#B0B0B0",
            "hover_color": "#8F8F8F",
            "text_color": "black",
            "font": self.button_font
        }

        self.base = cargar_conocimiento()
        self.respuestas = {}
        self.indice_pregunta = 0
        self.personaje_predicho = ""

        self.personajes_posibles = {}

        # --- NUEVA VARIABLE DE ESTADO ---
        # Registra si el motor se quedó sin opciones
        self.fallo_logico = False

        # --- CREACIÓN DE WIDGETS ---

        self.bg_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bg_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        if os.path.exists(FONDO_PATH):
            try:
                self.bg_image = ctk.CTkImage(Image.open(FONDO_PATH), size=(1280, 768))
                self.bg_label = ctk.CTkLabel(self.bg_frame, image=self.bg_image, text="")
                self.bg_label.place(relx=0.5, rely=0.5, anchor="center")
            except Exception as e:
                print(f"Error al cargar imagen de fondo: {e}")
        else:
            print(f"Advertencia: No se encontró la imagen de fondo en {FONDO_PATH}")

        PANEL_COLOR = "#21232A"
        PANEL_WIDTH = 700
        PANEL_HEIGHT = 300
        MARGEN_INFERIOR = 30

        self.frame_principal = ctk.CTkFrame(self.bg_frame,
                                            fg_color=PANEL_COLOR,
                                            width=PANEL_WIDTH,
                                            height=PANEL_HEIGHT,
                                            corner_radius=15)

        self.frame_principal.place(relx=0.5, rely=1.0, y=-MARGEN_INFERIOR, anchor="s")
        self.frame_principal.pack_propagate(False)

        self.label = ctk.CTkLabel(self.frame_principal, text="",
                                  font=self.label_font,
                                  wraplength=650,
                                  text_color="#E5E5E5",
                                  fg_color="transparent")
        self.label.pack(pady=(20, 10))

        self.frame_botones = ctk.CTkFrame(self.frame_principal, fg_color="transparent")
        self.frame_botones.pack(pady=5)

        self.entry_nombre = ctk.CTkEntry(self.frame_principal,
                                         placeholder_text="Escribe aquí el nombre...",
                                         font=self.button_font,
                                         width=300)

        self.button_aprender = ctk.CTkButton(self.frame_principal,
                                             text="Guardar y Aprender",
                                             command=self.aprender_personaje,
                                             **self.button_style)

        self.crear_menu_principal()

    # =========================================
    # MÉTODOS: NAVEGACIÓN Y MENÚ
    # =========================================
    """
    Gestionan la visualización de las pantallas principales y la
    preparación de una nueva partida.
    - iniciar_juego: Reinicia todas las variables de estado para
      una nueva partida, incluyendo 'self.fallo_logico'.
    """

    def crear_menu_principal(self):
        for widget in self.frame_principal.winfo_children():
            widget.pack_forget()

        self.label.configure(text="Adivina Quién\nEdición Personajes de Hollow Knight",
                             font=self.title_font)
        self.label.pack(pady=(40, 30))

        ctk.CTkButton(self.frame_principal, text="Jugar",
                      command=self.iniciar_juego, **self.button_style
                      ).pack(pady=10, ipadx=10, ipady=5)

        ctk.CTkButton(self.frame_principal, text="Salir",
                      command=self.destroy, **self.button_style
                      ).pack(pady=10, ipadx=10, ipady=5)

    def iniciar_juego(self):
        for widget in self.frame_principal.winfo_children():
            widget.pack_forget()

        # --- Inicialización de Hechos y Estado ---
        self.personajes_posibles = self.base.copy()
        self.respuestas = {}
        self.indice_pregunta = 0
        self.fallo_logico = False  # <--- CAMBIO: Reinicia el estado de fallo

        self.label.configure(font=self.label_font)
        self.label.pack(pady=(20, 10))
        self.frame_botones.pack(pady=5)

        self.mostrar_pregunta()

    # =========================================
    # MÉTODOS: MOTOR DE INFERENCIA (ENCADENAMIENTO ADELANTE)
    # =========================================
    """
    Esta sección es el corazón del sistema experto (Modus Ponens).
    - registrar_respuesta: Es el motor de inferencia.
      1. Recibe un HECHO (la respuesta del usuario).
      2. Aplica MODUS PONENS para eliminar personajes incompatibles
         de la 'Memoria de Trabajo' (self.personajes_posibles).
      3. Llama a 'siguiente_paso_logico' para continuar el ciclo.
    """

    def mostrar_pregunta(self):
        self.label.configure(text=PREGUNTAS[self.indice_pregunta])

        for widget in self.frame_botones.winfo_children():
            widget.destroy()

        opciones = ["Si", "No", "No lo se", "Probablemente"]
        for opcion in opciones:
            ctk.CTkButton(
                self.frame_botones,
                text=opcion,
                command=lambda o=opcion: self.registrar_respuesta(o),
                **self.button_style
            ).pack(pady=5, ipadx=5, ipady=2)

    def registrar_respuesta(self, respuesta):
        # 1. Guardar el hecho (respuesta) para el aprendizaje futuro
        clave_actual = CLAVES[self.indice_pregunta]
        self.respuestas[clave_actual] = respuesta

        # 2. MOTOR DE INFERENCIA (Aplicación de Modus Ponens)
        # Solo se aplica la regla si la respuesta es definitiva (Si/No)
        # y si el fallo lógico no ha ocurrido ya (optimiz.)
        if respuesta in ["Si", "No"] and not self.fallo_logico:
            personajes_a_eliminar = []
            for nombre, rasgos in self.personajes_posibles.items():
                rasgo_personaje = rasgos.get(clave_actual, "No lo se")

                # REGLA: Si el rasgo guardado contradice la respuesta...
                if rasgo_personaje != "No lo se" and rasgo_personaje != respuesta:
                    # ...DEDUCE: El personaje es imposible
                    personajes_a_eliminar.append(nombre)

            # 3. Actualizar la memoria de trabajo con los nuevos hechos
            for nombre in personajes_a_eliminar:
                del self.personajes_posibles[nombre]

        # 4. Pasar al siguiente estado del ciclo lógico
        self.indice_pregunta += 1
        self.siguiente_paso_logico()

    # =========================================
    # MÉTODOS: CICLO LÓGICO Y APRENDIZAJE
    # =========================================
    """
    Gestionan el estado del juego después de un ciclo de inferencia.
    - siguiente_paso_logico: ¡LÓGICA CRÍTICA MODIFICADA!
      1. Revisa si la 'Memoria de Trabajo' se vació (num_posibles == 0).
      2. Si es así, activa el flag 'self.fallo_logico' e informa al usuario.
      3. Revisa si quedan preguntas (índice < total).
      4. SI QUEDAN PREGUNTAS: Llama a 'mostrar_pregunta' y sale.
         (Esto asegura que se sigan haciendo preguntas incluso si 'fallo_logico' es True).
      5. SI NO QUEDAN PREGUNTAS (fin del juego):
         - Si 'fallo_logico' es True -> Llama a 'no_acerto' (aprender).
         - Si 'num_posibles == 1' -> Llama a 'mostrar_resultado_prediccion' (éxito).
         - Si 'num_posibles > 1' -> Llama a 'mostrar_resultado_puntaje' (ambiguo).
    """

    def siguiente_paso_logico(self):
        # --- LÓGICA MODIFICADA ---

        num_posibles = len(self.personajes_posibles)

        # 1. Revisa el estado de fallo lógico
        if num_posibles == 0:
            if not self.fallo_logico:  # Solo se activa la primera vez
                self.fallo_logico = True
                messagebox.showinfo("¡Personaje nuevo!",
                                    "No conozco ese personaje. Déjame terminar las preguntas para aprender.")

        # 2. Revisa si quedan preguntas
        if self.indice_pregunta < len(PREGUNTAS):
            # Si quedan preguntas, SIEMPRE las muestra,
            # incluso si ya falló (para recopilar datos)
            self.mostrar_pregunta()
            return  # Sale de la función aquí

        # --- FIN DEL JUEGO (Solo se llega aquí si no quedan preguntas) ---

        # 3. Decide el resultado final
        if self.fallo_logico:
            # Si falló en cualquier punto, pasa a aprender
            self.no_acerto()

        elif num_posibles == 1:
            # CONCLUSIÓN LÓGICA (Hecho final deducido)
            self.personaje_predicho = list(self.personajes_posibles.keys())[0]
            self.mostrar_resultado_prediccion()

        else:  # num_posibles > 1
            # FIN DE PREGUNTAS (Ambigüedad)
            self.mostrar_resultado_puntaje()

    def mostrar_resultado_prediccion(self):
        # Muestra la deducción final (caso 1 posible)
        for widget in self.frame_botones.winfo_children():
            widget.destroy()

        self.label.configure(text=f"¡Lo tengo! Tu personaje es: {self.personaje_predicho}")

        ctk.CTkButton(self.frame_botones, text="Sí",
                      command=self.confirmar_acierto, **self.button_style
                      ).pack(pady=5, side="left", padx=10)

        ctk.CTkButton(self.frame_botones, text="No",
                      command=self.no_acerto, **self.button_style
                      ).pack(pady=5, side="left", padx=10)

    def mostrar_resultado_puntaje(self):
        # Muestra el resultado por puntaje (caso >1 posible)
        if not self.personajes_posibles:
            # Este caso no debería ocurrir con la nueva lógica,
            # pero es un buen seguro.
            self.no_acerto()
            return

        puntajes = {nombre: comparar_personaje(self.respuestas, caract)
                    for nombre, caract in self.personajes_posibles.items()}

        self.personaje_predicho = max(puntajes, key=puntajes.get)
        mejor_puntaje = puntajes[self.personaje_predicho]

        if mejor_puntaje < 0.5:
            self.no_acerto()
        else:
            self.mostrar_resultado_prediccion()

    def confirmar_acierto(self):
        # Si el usuario confirma la deducción
        if messagebox.askyesno("¡Genial!", "¡He acertado! ¿Quieres jugar de nuevo?"):
            self.iniciar_juego()
        else:
            self.crear_menu_principal()

    def no_acerto(self):
        # Muestra la UI para aprender un personaje nuevo
        for widget in self.frame_botones.winfo_children():
            widget.destroy()
        self.frame_botones.pack_forget()

        self.label.configure(text="Vaya, no acerté. ¿Cuál era tu personaje?")

        self.button_aprender.pack(side="bottom", pady=(5, 20))
        self.entry_nombre.pack(side="bottom", pady=5)

    def aprender_personaje(self):
        # Guarda el nuevo personaje en el JSON
        nombre = self.entry_nombre.get().strip().title()
        if not nombre:
            messagebox.showerror("Error", "Debes ingresar un nombre.")
            return

        if nombre in self.base:
            if not messagebox.askyesno("Confirmar",
                                       f"'{nombre}' ya existe. ¿Deseas sobrescribir sus características con las respuestas actuales?"):
                return

        self.base[nombre] = self.respuestas
        guardar_conocimiento(self.base)

        messagebox.showinfo("Aprendido", f"¡He aprendido sobre {nombre}! Gracias.")

        self.entry_nombre.pack_forget()
        self.button_aprender.pack_forget()
        self.entry_nombre.delete(0, 'end')

        self.crear_menu_principal()


# ==============================
# EJECUCIÓN DEL PROGRAMA
# ==============================
if __name__ == "__main__":
    app = JuegoHollowKnight()
    app.mainloop()