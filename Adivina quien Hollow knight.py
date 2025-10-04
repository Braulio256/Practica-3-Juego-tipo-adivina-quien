import json
import os
import time

# =========================================
# CONFIGURACIÓN
# =========================================

ARCHIVO_CONOCIMIENTO = "hollow_knight_data.json"

# Base inicial con tus personajes
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
        "es_enemigo": "No",
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

# Claves asociadas a cada pregunta
claves = ["arma_aguijon", "arma_infeccion", "rol_jefe", "es_enemigo", "aparece_multiples"]

# ======================================================
# FUNCIONES DE UTILIDAD
# ======================================================

def guardar_conocimiento(base):
    """Guarda la base de conocimiento en el archivo JSON."""
    with open(ARCHIVO_CONOCIMIENTO, "w", encoding="utf-8") as f:
        json.dump(base, f, indent=4, ensure_ascii=False)

def cargar_conocimiento():
    """Carga la base de conocimiento desde el archivo.
    Si no existe, crea el archivo con la base inicial."""
    if not os.path.exists(ARCHIVO_CONOCIMIENTO):
        guardar_conocimiento(base_inicial)
    with open(ARCHIVO_CONOCIMIENTO, "r", encoding="utf-8") as f:
        return json.load(f)

# ======================================================
# FUNCIONES DE INTERACCIÓN
# ======================================================

def mostrar_menu_respuesta(pregunta):
    """Muestra una pregunta con un menú de opciones tipo switch y devuelve la respuesta seleccionada."""
    print(f"\n{pregunta}")
    print("1. Si")
    print("2. No")
    print("3. No lo sé")
    print("4. Probablemente")

    while True:
        try:
            opcion = int(input("Selecciona una opción (1-4): "))
            if opcion == 1:
                return "Si"
            elif opcion == 2:
                return "No"
            elif opcion == 3:
                return "No lo se"
            elif opcion == 4:
                return "Probablemente"
            else:
                print("⚠️ Opción fuera de rango. Intenta de nuevo.")
        except ValueError:
            print("⚠️ Debes ingresar un número entre 1 y 4.")

def menu_confirmacion(pregunta):
    """Muestra un menú tipo switch (1–2) para preguntas de confirmación como '¿Adiviné?' o '¿Jugar de nuevo?'."""
    print(f"\n{pregunta}")
    print("1. Si")
    print("2. No")
    while True:
        try:
            opcion = int(input("Selecciona una opción (1-2): "))
            if opcion == 1:
                return "Si"
            elif opcion == 2:
                return "No"
            else:
                print("⚠️ Opción fuera de rango. Intenta de nuevo.")
        except ValueError:
            print("⚠️ Debes ingresar un número (1 o 2).")

def obtener_respuestas():
    """Realiza las 5 preguntas al usuario y devuelve sus respuestas."""
    respuestas = {}
    for i, pregunta in enumerate(preguntas):
        respuesta = mostrar_menu_respuesta(pregunta)
        respuestas[claves[i]] = respuesta
    return respuestas

def comparar_personaje(respuestas_usuario, caracteristicas_personaje):
    """Devuelve un puntaje de coincidencia (0 a 1) entre las respuestas del usuario y un personaje."""
    coincidencias = 0
    for clave in respuestas_usuario:
        if respuestas_usuario[clave] == caracteristicas_personaje[clave]:
            coincidencias += 1
        elif respuestas_usuario[clave] in ["Probablemente", "No lo se"]:
            coincidencias += 0.5
    return coincidencias / len(respuestas_usuario)

# ======================================================
# LÓGICA PRINCIPAL DEL JUEGO
# ======================================================

"""Ejecución principal del juego."""
while True:
    base = cargar_conocimiento()

    print("\n🎮 Bienvenido a '¿Quién soy? - Hollow Knight Edition' 🦋")
    print("Piensa en un personaje del juego. Yo intentaré adivinarlo.")
    input("Presiona ENTER cuando estés listo...\n")

    # El jugador responde las 5 preguntas
    respuestas = obtener_respuestas()

    # Calcular coincidencias con la base de conocimiento
    puntajes = {}
    for nombre, caracteristicas in base.items():
        puntajes[nombre] = comparar_personaje(respuestas, caracteristicas)

    # Obtener el personaje más probable
    mejor = max(puntajes, key=puntajes.get)
    valor = puntajes[mejor]

    print("\n🤔 Estoy pensando...")
    time.sleep(1.5)

    # Mostrar resultado
    print(f"\nCreo que tu personaje es: 🕵️‍♂️ {mejor} (confianza: {round(valor * 100, 1)}%)")

    # Confirmación del usuario con menú
    confirmacion = menu_confirmacion("¿Adiviné tu personaje?")

    if confirmacion == "Si":
        # Si adivina correctamente, preguntar si desea jugar otra vez
        jugar_nuevamente = menu_confirmacion("¿Quieres jugar de nuevo?")
        if jugar_nuevamente == "Si":
            continue
        else:
            print("\n¡Gracias por jugar! 🌙")
            break
    else:
        # Si no adivina, aprender un nuevo personaje
        print("\nVaya, parece que no acerté 😕")
        nombre_nuevo = input("¿Cuál era tu personaje?: ").strip()
        print(f"\nVamos a aprender sobre {nombre_nuevo}. Responde las siguientes preguntas:")

        nuevo_info = {}
        for clave, pregunta in zip(claves, preguntas):
            nuevo_info[clave] = mostrar_menu_respuesta(pregunta)

        base[nombre_nuevo] = nuevo_info
        guardar_conocimiento(base)
        print(f"\n✅ He aprendido sobre {nombre_nuevo} para la próxima vez.")

        jugar_nuevamente = menu_confirmacion("\n¿Quieres jugar otra vez?")
        if jugar_nuevamente == "Si":
            continue
        else:
            print("\n¡Gracias por ayudarme a aprender! 🌟")
            break
