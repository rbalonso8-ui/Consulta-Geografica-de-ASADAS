
import socket
import threading
import os
import json

import arbol_binario as ab
import archivo_binario as arc
import Listas_enlazadas as le
import Mapa as mp

HOST = "0.0.0.0"   
PORT = 5050

arbol = None

lock = threading.Lock()


def preparar_estructuras():
    """Garantiza que existan los archivos binarios necesarios y carga
    el árbol binario en memoria. Si algún archivo binario no existe
    todavía, se construye a partir de 'asadas.json'.
    """
    global arbol

    if not os.path.exists("asadas.json"):
        raise FileNotFoundError(
            "No se encontró 'asadas.json'. Es necesario para construir las estructuras."
        )

    with open("asadas.json", "r", encoding="utf-8") as f:
        datos = json.load(f)

    lista_asadas = datos["value"]

    # Árbol binario + archivo principal (búsqueda por ID)
    if not os.path.exists("asadas_principal.bin"):
        arc.escribir_texto_binario(lista_asadas)

    if not os.path.exists("arbol_binario.bin"):
        ab.construir(lista_asadas)

    arbol = ab.cargar_árbol()

    # Listas enlazadas de división política (Provincia/Cantón/Distrito/ASADA)
    archivos_division = ("provincias.bin", "cantones.bin", "distritos.bin", "ASADAS.bin")
    if not all(os.path.exists(f) for f in archivos_division):
        le.construir(lista_asadas)

    print("[SERVIDOR] Estructuras de datos cargadas correctamente en memoria.")


# ------------------------------------------------------------------
#  Funciones de consulta (envuelven a los módulos ya existentes)
# ------------------------------------------------------------------
def buscar_id(id_asada: str):
    """Busca una ASADA por su ID usando el árbol binario + archivo principal.

    Returns:
        dict | None: datos completos de la ASADA, o None si no existe
    """
    with lock:
        posición = ab.buscar(arbol, id_asada.strip())
        if posición == -1:
            return None
        return arc.leer_texto_binario(posición)

def manejar_peticion(linea: str) -> list[str]:
    """Interpreta una línea de petición del cliente y devuelve la
    lista de líneas que conforman la respuesta (incluyendo "FIN").
    """
    partes = linea.strip().split("|")
    comando = partes[0].strip().upper() if partes else ""

    try:
        if comando == "BUSCAR_ID" and len(partes) == 2:
            datos = buscar_id(partes[1])
            if datos is None:
                return ["ERROR", f"No se encontró ninguna ASADA con ID {partes[1]}", "FIN"]

            respuesta = ["OK"]
            for campo, valor in datos.items():
                respuesta.append(f"{campo}={valor}")
            respuesta.append("FIN")
            return respuesta

        elif comando == "PROVINCIAS" and len(partes) == 1:
            with lock:
                provincias = le.obtener_provincias()
            if not provincias:
                return ["ERROR", "No hay provincias registradas", "FIN"]
            return ["OK", *provincias, "FIN"]

        elif comando == "CANTONES" and len(partes) == 2:
            with lock:
                cantones = le.obtener_cantones(partes[1])
            if not cantones:
                return ["ERROR", f"No se encontraron cantones para la provincia '{partes[1]}'", "FIN"]
            return ["OK", *cantones, "FIN"]

        elif comando == "DISTRITOS" and len(partes) == 3:
            with lock:
                distritos = le.obtener_distritos(partes[1], partes[2])
            if not distritos:
                return ["ERROR", f"No se encontraron distritos para '{partes[1]}' / '{partes[2]}'", "FIN"]
            return ["OK", *distritos, "FIN"]

        elif comando == "ASADAS" and len(partes) == 4:
            with lock:
                ids = le.obtener_asadas(partes[1], partes[2], partes[3])

            if not ids:
                return ["ERROR", f"No se encontraron ASADAS para '{partes[1]}' / '{partes[2]}' / '{partes[3]}'", "FIN"]

            respuesta = ["OK"]
            for id_asada in ids:
                datos = buscar_id(id_asada)
                if datos:
                    respuesta.append(
                        f"{datos['id_Asada']};{datos['operador']};{datos['provincia']};"
                        f"{datos['canton']};{datos['distrito']};{datos['telefono']}"
                    )
            respuesta.append("FIN")
            return respuesta

        else:
            return ["ERROR", f"Comando inválido o mal formado: '{linea.strip()}'", "FIN"]

    except Exception as error:
        return ["ERROR", f"Error interno del servidor: {error}", "FIN"]

def atender_cliente(conexión: socket.socket, dirección):
    """Atiende a un cliente remoto en un hilo independiente.

    Lee peticiones línea por línea, las procesa y devuelve la
    respuesta correspondiente, hasta que el cliente cierra la conexión.
    """
    print(f"[SERVIDOR] Cliente conectado desde {dirección}")

    try:
        with conexión:
            entrada = conexión.makefile("r", encoding="utf-8")
            salida = conexión.makefile("w", encoding="utf-8")

            for línea in entrada:
                if not línea.strip():
                    continue

                print(f"[SERVIDOR] {dirección} -> {línea.strip()}")
                respuesta = manejar_peticion(línea)

                for línea_respuesta in respuesta:
                    salida.write(línea_respuesta + "\n")
                salida.flush()

    except (ConnectionResetError, BrokenPipeError):
        pass
    finally:
        print(f"[SERVIDOR] Cliente desconectado: {dirección}")

def iniciar_servidor():
    preparar_estructuras()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((HOST, PORT))
        servidor.listen()
        print(f"[SERVIDOR] Escuchando conexiones en {HOST}:{PORT} ...")

        while True:
            conexión, dirección = servidor.accept()
            hilo = threading.Thread(
                target=atender_cliente,
                args=(conexión, dirección),
                daemon=True,
            )
            hilo.start()


if __name__ == "__main__":
    iniciar_servidor()