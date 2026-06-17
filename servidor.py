import socket
import threading

import arbol_binario as ab
import archivo_binario as arc
import Listas_enlazadas as le
import actualizacion as act
import Mapa as mp

HOST = "0.0.0.0"
PORT = 5050

arbol = None

lock = threading.Lock()

contador_clientes = 0

servidor_escuchando = threading.Event()


def preparar_estructuras():
    """Garantiza que existan los archivos binarios y carga el árbol en memoria Verifica los datos remotos mediante el módulo de actualización incremental:
    si hay cambios o faltan archivos, regenera las estructuras. Si no hay conexión con el endpoint, intenta trabajar con los archivos binarios existentes en disco.
    """
    global arbol

    try:
        act.actualizar()
    except Exception as error:
        print(f"[SERVIDOR] No se pudo verificar la actualización remota: {error}")
        if not act.estructuras_completas():
            raise FileNotFoundError(
                "No hay estructuras locales ni conexión con el endpoint. "
                "Ejecute la actualización desde un equipo con acceso a internet."
            )
        print("[SERVIDOR] Se usarán las estructuras locales existentes.")

    arbol = ab.cargar_árbol()
    print("[SERVIDOR] Estructuras de datos cargadas correctamente en memoria.")


def buscar_id(id_asada: str):
    """Busca una ASADA por su ID usando el árbol binario y el archivo principal

    Args:
        id_asada (str): Identificador de la ASADA a buscar

    Returns:
        dict | None: Datos completos de la ASADA, o None si no existe
    """
    with lock:
        posición = ab.buscar(arbol, id_asada.strip())
        if posición == -1:
            return None
        return arc.leer_texto_binario(posición)


def manejar_peticion(linea: str) -> list[str]:
    """Interpreta una línea de petición del cliente y devuelve la respuesta

    Args:
        linea (str): Línea de petición recibida del cliente

    Returns:
        list[str]: Lista de líneas de respuesta, incluyendo la línea final "FIN"
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

        elif comando == "ASADAS" and 2 <= len(partes) <= 4:
            with lock:
                if len(partes) == 2:
                    ids = le.obtener_asadas_de_provincia(partes[1])
                elif len(partes) == 3:
                    ids = le.obtener_asadas_de_canton(partes[1], partes[2])
                else:
                    ids = le.obtener_asadas(partes[1], partes[2], partes[3])

            if not ids:
                return ["ERROR", "No se encontraron ASADAS para la selección indicada", "FIN"]

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

        elif comando == "MAPA" and len(partes) == 2:
            datos = buscar_id(partes[1])
            if datos is None:
                return ["ERROR", f"No se encontró ninguna ASADA con ID {partes[1]}", "FIN"]
            with lock:
                mp.generar_mapa(datos)
            return ["OK", "Mapa generado en el servidor", "FIN"]

        else:
            return ["ERROR", f"Comando inválido o mal formado: '{linea.strip()}'", "FIN"]

    except Exception as error:
        return ["ERROR", f"Error interno del servidor: {error}", "FIN"]


def etiqueta_cliente(numero: int) -> str:
    """Devuelve el nombre con que se identifica una conexión en los registros

    La primera conexión (la del equipo que levantó el servidor) se identifica
    como "Host"; de la segunda en adelante son "Cliente 1", "Cliente 2", etc.

    Args:
        numero (int): Número secuencial de la conexión (1 es el primero)

    Returns:
        str: Etiqueta legible para los registros del servidor
    """
    return "Host" if numero == 1 else f"Cliente {numero - 1}"


def atender_cliente(conexión: socket.socket, dirección):
    """Atiende a un cliente remoto en un hilo independiente

    El número de cliente se asigna solo cuando la conexión envía su primera
    petición real, de modo que las conexiones de prueba (las que comprueban si
    el servidor existe y se cierran sin enviar nada) no consuman un número.

    Args:
        conexión (socket.socket): Socket de la conexión con el cliente
        dirección: Dirección (IP, puerto) del cliente conectado
    """
    global contador_clientes
    nombre = None

    try:
        with conexión:
            entrada = conexión.makefile("r", encoding="utf-8")
            salida = conexión.makefile("w", encoding="utf-8")

            for línea in entrada:
                if not línea.strip():
                    continue

                if nombre is None:  # primera petición real: ahora sí se cuenta
                    with lock:
                        contador_clientes += 1
                        numero = contador_clientes
                    nombre = etiqueta_cliente(numero)
                    print(f"[SERVIDOR] {nombre} conectado desde {dirección}")

                print(f"[SERVIDOR] {nombre} -> {línea.strip()}")
                respuesta = manejar_peticion(línea)

                for línea_respuesta in respuesta:
                    salida.write(línea_respuesta + "\n")
                salida.flush()

    except (ConnectionResetError, BrokenPipeError):
        pass
    finally:
        if nombre is not None:
            print(f"[SERVIDOR] {nombre} desconectado ({dirección})")


def iniciar_servidor():
    """Inicia el servidor: prepara las estructuras y atiende clientes con hilos"""
    preparar_estructuras()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if hasattr(socket, "SO_REUSEPORT"):
            servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        servidor.bind((HOST, PORT))
        servidor.listen()
        print(f"[SERVIDOR] Escuchando conexiones en {HOST}:{PORT} ...")
        servidor_escuchando.set()

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