import socket
import threading

import servidor
import GUI

HOST = "127.0.0.1"
PORT = 5050


def hay_servidor(host: str, port: int) -> bool:
    """Comprueba si ya hay un servidor escuchando en el host y puerto dados

    Args:
        host (str): Dirección a comprobar
        port (int): Puerto a comprobar

    Returns:
        bool: True si algo responde en ese puerto, False en caso contrario
    """
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False


def main():
    """Flujo principal del sistema con detección automática de rol
    Al arrancar comprueba si ya existe un servidor en el puerto. Si no lo hay, esta instancia levanta el servidor centraly luego abre la interfaz gráfica. 
    Si ya existe un servidor, esta instancia se conecta a él como un cliente más. Así main.py puede ejecutarse varias veces: la primera monta el servidor y las siguientes actúan como clientes.
    """
    if hay_servidor(HOST, PORT):
        print(f"Servidor detectado en {HOST}:{PORT}. Abriendo interfaz como cliente...")
        GUI.main()
        return

    print("No hay servidor activo. Iniciando servidor en segundo plano...")
    hilo_servidor = threading.Thread(target=servidor.iniciar_servidor, daemon=True)
    hilo_servidor.start()

    if not servidor.servidor_escuchando.wait(timeout=30):
        print("[ERROR] El servidor no respondió a tiempo. Abortando.")
        return

    print("Servidor listo. Abriendo interfaz gráfica...")
    GUI.main()


if __name__ == "__main__":
    main()