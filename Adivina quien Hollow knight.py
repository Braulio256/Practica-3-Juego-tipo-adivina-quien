import json
import os

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

# Claves que se asocian a cada pregunta (en orden)
claves = ["arma_aguijon", "arma_infeccion", "rol_jefe", "es_enemigo", "aparece_multiples"]

# =========================================
# FUNCIONES DE CONOCIMIENTO
# =========================================

def cargar_conocimiento():
    """Carga el conocimiento previo o usa la base inicial si no existe."""
    if os.path.exists(ARCHIVO_CONOCIMIENTO):
        with open(ARCHIVO_CONOCIMIENTO, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return base_inicial.copy()

def guardar_conocimiento(base):
    """Guarda el conocimiento actualizado."""
    with open(ARCHIVO_CONOCIMIENTO, "w", encoding="utf-8") as f:
        json.dump(base, f, indent=4, ensure_ascii=False)

# =========================================
# FUNCIONES DEL JUEGO
# =========================================

def obtener_respuestas():
    """Realiza las 5 preguntas al usuario."""
    respuestas = {}
    print("\nResponde con: Si / No / No lo se / Probablemente\n")
    for i, pregunta in enumerate(preguntas):
        while True:
            resp = input(f"{pregunta} ").strip().capitalize()
            if resp in ["Si", "No", "No lo se", "Probablemente"]:
                respuestas[claves[i]] = resp
                break
            else:
                print("⚠️ Respuesta no válida. Usa: Si, No, No lo se o Probablemente.")
    return respuestas

def comparar_personaje(respuestas_usuario, caracteristicas_personaje):
    """Devuelve una puntuación de coincidencia entre 0 y 1."""
    coincidencias = 0
    for clave in respuestas_usuario:
        if respuestas_usuario[clave] == caracteristicas_personaje[clave]:
            coincidencias += 1
        elif respuestas_usuario[clave] in ["Probablemente", "No lo se"]:
            coincidencias += 0.5  # valor intermedio
    return coincidencias / len(respuestas_usuario)

def jugar():
    base = cargar_conocimiento()

    print("🎮 Bienvenido a '¿Quién soy? - Hollow Knight Edition'")
    print("Piensa en un personaje de Hollow Knight. Yo intentaré adivinarlo.")
    input("Presiona ENTER cuando estés listo...")

    respuestas = obtener_respuestas()

    # Calcular coincidencias
    puntajes = {}
    for nombre, caracteristicas in base.items():
        puntajes[nombre] = comparar_personaje(respuestas, caracteristicas)

    # Buscar el personaje con mayor coincidencia
    mejor = max(puntajes, key=puntajes.get)
    valor = puntajes[mejor]

    print("\n🤔 Estoy pensando...")

    if valor >= 0.8:
        print(f"¡Creo que tu personaje es {mejor}! 😄")
    else:
        print("No estoy seguro de quién es tu personaje 😕")
        print(f"Mis mejores opciones eran: {sorted(puntajes.items(), key=lambda x: x[1], reverse=True)[:3]}")
        nombre_nuevo = input("\n¿Cuál era tu personaje?: ").strip()

        # Aprender nuevo personaje
        print("Vamos a aprender sobre él...")
        nuevo_info = {}
        for clave, pregunta in zip(claves, preguntas):
            nuevo_info[clave] = input(f"{pregunta} (Si / No / No lo se / Probablemente): ").strip().capitalize()

        base[nombre_nuevo] = nuevo_info
        guardar_conocimiento(base)
        print(f"✅ He aprendido sobre {nombre_nuevo} para la próxima vez.")

    print("\nFin del juego. 🦋")

# =========================================
# EJECUCIÓN
# =========================================

if __name__ == "__main__":
    jugar()
