import os  # Para interactuar con el sistema operativo (gestionar rutas de archivos).
import sys  # Para acceder a variables del sistema (necesario para la ruta del .exe).
import json  # Para leer y escribir archivos en formato JSON (la base de conocimiento).
import customtkinter as ctk  # La librería principal para crear la interfaz gráfica (GUI).
from tkinter import messagebox  # De tkinter, usamos los pop-ups para mensajes y errores.
from PIL import Image  # (Pillow) Para cargar y gestionar la imagen de fondo.
import pyglet  # Para cargar fuentes personalizadas (.ttf) sin necesidad de instalarlas.

# ==============================
# CONFIGURACIÓN GLOBAL DE CUSTOMTKINTER
# ==============================
"""
Establece la apariencia visual por defecto para toda la aplicación,
configurando el modo oscuro y el tema de color.
"""
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# ==============================
# DEFINICIÓN DE CONSTANTES
# ==============================
"""
Define todas las variables globales y constantes. Esto incluye:
- Determinar la ruta base (BASE_DIR) para que funcione como .py o .exe.
- Definir las rutas a los archivos (JSON, fondo, fuente).
- Cargar la fuente personalizada (pyglet) o usar una de respaldo.
- Establecer la base de conocimiento inicial (BASE_INICIAL) si el JSON no existe.
- Listar las preguntas (PREGUNTAS) y sus claves (CLAVES) asociadas.
"""
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ARCHIVO_CONOCIMIENTO = os.path.join(BASE_DIR, "hollow_knight_data.json")
FONDO_PATH = os.path.join(BASE_DIR, "fondo.jpg")
FUENTE_PATH = os.path.join(BASE_DIR, "CinzelDecorative-Regular.ttf")

try:
    if os.path.exists(FUENTE_PATH):
        pyglet.font.add_file(FUENTE_PATH)
        FONT_FAMILY = "Cinzel Decorative"
        print(f"Fuente '{FONT_FAMILY}' cargada exitosamente.")
    else:
        raise FileNotFoundError
except Exception as e:
    print(f"Advertencia: No se pudo cargar la fuente desde {FUENTE_PATH}. Error: {e}")
    print("Usando fuente 'Arial' por defecto.")
    FONT_FAMILY = "Arial"

BASE_INICIAL = {
    "Hornet": {"arma_aguijon": "Si", "arma_infeccion": "No", "rol_jefe": "Si", "es_enemigo": "No",
               "aparece_multiples": "Si"},
    "Zote": {"arma_aguijon": "Si", "arma_infeccion": "No", "rol_jefe": "Si", "es_enemigo": "Si",
             "aparece_multiples": "Si"},
    "Señores Mantis": {"arma_aguijon": "Si", "arma_infeccion": "No", "rol_jefe": "Si", "es_enemigo": "Si",
                       "aparece_multiples": "No"}
}

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
- guardar_conocimiento: Escribe el diccionario de la base en el archivo JSON.
- cargar_conocimiento: Lee el JSON y lo devuelve como diccionario. Si no existe
  o está corrupto, usa y guarda la BASE_INICIAL.
- comparar_personaje: Función de *respaldo*. Se usa solo si el motor de
  inferencia termina con varios personajes posibles (ambigüedad).
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
Define la ventana principal del juego (JuegoHollowKnight) heredando de ctk.CTk.
Esta clase gestiona la interfaz gráfica (GUI), el estado del juego (variables)
y la interacción entre los diferentes componentes y pantallas.
"""


class JuegoHollowKnight(ctk.CTk):

    def __init__(self):
        """
        Constructor de la clase. Se ejecuta al crear la ventana.
        - Configura la ventana principal (título, tamaño, centrado).
        - Define las fuentes y estilos reutilizables.
        - Carga la base de conocimiento e inicializa variables de estado.
        - Define la 'Memoria de Trabajo' (self.personajes_posibles).
        - Crea todos los widgets de la interfaz (fondo, panel, etiquetas, botones).
        - Llama a `crear_menu_principal` para mostrar la pantalla inicial.
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

        # --- MEMORIA DE TRABAJO (Working Memory) ---
        # Esta lista contiene el estado actual de los hechos (quiénes son posibles).
        self.personajes_posibles = {}

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
    Gestionan la visualización de las pantallas principales, como
    el menú de inicio y la preparación para una nueva partida.
    - crear_menu_principal: Limpia el panel y muestra los botones "Jugar" y "Salir".
    - iniciar_juego: Prepara una nueva partida. Es un paso CRÍTICO
      ya que aquí se llena la 'Memoria de Trabajo' (self.personajes_posibles)
      con el estado inicial de los hechos (todos los personajes son posibles).
    """

    def crear_menu_principal(self):
        for widget in self.frame_principal.winfo_children():
            widget.pack_forget()

        self.label.configure(text="Adivina Quién\nEdición Personajes de Hollow Knight",
                             font=self.title_font)
        self.label.pack(pady=(40, 30))

        ctk.CTkButton(
            self.frame_principal,
            text="Jugar",
            command=self.iniciar_juego,
            **self.button_style
        ).pack(pady=10, ipadx=10, ipady=5)

        ctk.CTkButton(
            self.frame_principal,
            text="Salir",
            command=self.destroy,
            **self.button_style
        ).pack(pady=10, ipadx=10, ipady=5)

    def iniciar_juego(self):
        for widget in self.frame_principal.winfo_children():
            widget.pack_forget()

        # --- Inicialización de Hechos ---
        # Hecho inicial: Todos los personajes son posibles.
        # Se copian todos los personajes a la Memoria de Trabajo.
        self.personajes_posibles = self.base.copy()
        self.respuestas = {}
        self.indice_pregunta = 0

        self.label.configure(font=self.label_font)
        self.label.pack(pady=(20, 10))
        self.frame_botones.pack(pady=5)

        self.mostrar_pregunta()

    # =========================================
    # MÉTODOS: MOTOR DE INFERENCIA (ENCADENAMIENTO ADELANTE)
    # =========================================
    """
    Esta sección es el corazón del sistema experto (Modus Ponens).
    - mostrar_pregunta: Simplemente muestra la pregunta actual en la GUI.
    - registrar_respuesta: ¡El motor de inferencia!
      1. Recibe un HECHO (la respuesta del usuario, ej: "Si").
      2. Itera la MEMORIA DE TRABAJO (self.personajes_posibles).
      3. Aplica la REGLA: "SI (Hecho_Usuario contradice Hecho_Personaje)
         ENTONCES (Personaje = Imposible)".
      4. Si la regla se "dispara" (Modus Ponens), deduce un NUEVO HECHO
         (ej: "Hornet es imposible") y lo elimina de la memoria.
      5. Llama a 'siguiente_paso_logico' para continuar el ciclo de inferencia.
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
        personajes_a_eliminar = []

        # Solo aplicamos la regla si la respuesta es definitiva (Si/No)
        if respuesta in ["Si", "No"]:
            # Itera la memoria de trabajo
            for nombre, rasgos in self.personajes_posibles.items():
                rasgo_personaje = rasgos.get(clave_actual, "No lo se")

                # REGLA: Si el rasgo guardado es diferente a la respuesta...
                if rasgo_personaje != "No lo se" and rasgo_personaje != respuesta:
                    # ...DEDUCE: El personaje es imposible
                    personajes_a_eliminar.append(nombre)

        # 3. Actualizar la memoria de trabajo con los nuevos hechos deducidos
        for nombre in personajes_a_eliminar:
            # print(f"Deducción (Hecho Nuevo): {nombre} es imposible.") # Debug
            del self.personajes_posibles[nombre]

        # 4. Pasar al siguiente estado del ciclo lógico
        self.indice_pregunta += 1
        self.siguiente_paso_logico()

    # =========================================
    # MÉTODOS: CICLO LÓGICO Y APRENDIZAJE
    # =========================================
    """
    Gestionan el estado del juego después de un ciclo de inferencia.
    - siguiente_paso_logico: Revisa la 'Memoria de Trabajo' y decide:
      - (1 posible): ¡Conclusión! Se dedujo un resultado (mostrar_resultado_prediccion).
      - (0 posibles): Fallo lógico/Contradicción (no_acerto).
      - (>1 y ?): Se necesitan más hechos (mostrar_pregunta).
      - (>1 y no ?): Ambigüedad. Usa puntaje (mostrar_resultado_puntaje).
    - mostrar_resultado_prediccion: Muestra la deducción final (caso 1).
    - mostrar_resultado_puntaje: Fallback si hay >1 al final.
    - confirmar_acierto: Si el usuario confirma la deducción.
    - no_acerto: Inicia el flujo de aprendizaje si la IA falló.
    - aprender_personaje: Guarda el nuevo personaje en el JSON.
    """

    def siguiente_paso_logico(self):
        num_posibles = len(self.personajes_posibles)

        if num_posibles == 1:
            # CONCLUSIÓN LÓGICA (Hecho final deducido)
            self.personaje_predicho = list(self.personajes_posibles.keys())[0]
            self.mostrar_resultado_prediccion()

        elif num_posibles == 0:
            # FALLO LÓGICO (Contradicción en los hechos)
            messagebox.showinfo("¡Vaya!",
                                "No tengo ningún personaje en mi base que coincida con todas esas características.")
            self.no_acerto()

        elif self.indice_pregunta < len(PREGUNTAS):
            # NECESITA MÁS DATOS (Hechos insuficientes)
            self.mostrar_pregunta()

        else:
            # FIN DE PREGUNTAS (Ambigüedad)
            self.mostrar_resultado_puntaje()

    def mostrar_resultado_prediccion(self):
        for widget in self.frame_botones.winfo_children():
            widget.destroy()

        self.label.configure(text=f"¡Lo tengo! Tu personaje es: {self.personaje_predicho}")

        ctk.CTkButton(
            self.frame_botones, text="Sí",
            command=self.confirmar_acierto, **self.button_style
        ).pack(pady=5, side="left", padx=10)

        ctk.CTkButton(
            self.frame_botones, text="No",
            command=self.no_acerto, **self.button_style
        ).pack(pady=5, side="left", padx=10)

    def mostrar_resultado_puntaje(self):
        if not self.personajes_posibles:
            messagebox.showinfo("Base vacía", "No hay personajes en la base de datos. ¡Ayúdame a aprender!")
            self.no_acerto()
            return

        # Fallback: Comparamos puntajes SOLO entre los personajes restantes
        puntajes = {nombre: comparar_personaje(self.respuestas, caract)
                    for nombre, caract in self.personajes_posibles.items()}

        self.personaje_predicho = max(puntajes, key=puntajes.get)
        mejor_puntaje = puntajes[self.personaje_predicho]

        if mejor_puntaje < 0.5:
            self.no_acerto()
        else:
            self.mostrar_resultado_prediccion()

    def confirmar_acierto(self):
        if messagebox.askyesno("¡Genial!", "¡He acertado! ¿Quieres jugar de nuevo?"):
            self.iniciar_juego()
        else:
            self.crear_menu_principal()

    def no_acerto(self):
        for widget in self.frame_botones.winfo_children():
            widget.destroy()

        self.frame_botones.pack_forget()

        self.label.configure(text="Vaya, no acerté. ¿Cuál era tu personaje?")

        self.button_aprender.pack(side="bottom", pady=(5, 20))
        self.entry_nombre.pack(side="bottom", pady=5)

    def aprender_personaje(self):
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
"""
Punto de entrada principal. Si el script se ejecuta directamente
(y no es importado como un módulo), crea una instancia de la ventana
(JuegoHollowKnight) y la mantiene abierta con `mainloop()`.
"""
if __name__ == "__main__":
    app = JuegoHollowKnight()
    app.mainloop()