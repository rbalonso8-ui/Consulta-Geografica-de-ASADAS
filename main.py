import socket
import threading
import time

import servidor
import GUI

HOST = "127.0.0.1"
PORT = 5050


def servidor_listo(host: str, port: int, intentos: int = 30) -> bool:
    """Espera hasta que el servidor esté aceptando conexiones en el puerto dado

    Intenta conectarse repetidamente al servidor para confirmar que ya terminó
    de preparar las estructuras y está escuchando, antes de abrir la interfaz.

    Args:
        host (str): Dirección del servidor a comprobar
        port (int): Puerto del servidor a comprobar
        intentos (int): Número máximo de comprobaciones antes de rendirse

    Returns:
        bool: True si el servidor respondió, False si se agotaron los intentos
    """
    for _ in range(intentos):
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(1)
    return False


def main():
    """Flujo principal del sistema en modo todo en uno
    """
    hilo_servidor = threading.Thread(target=servidor.iniciar_servidor, daemon=True)
    hilo_servidor.start()

    print("Iniciando servidor en segundo plano...")
    if not servidor_listo(HOST, PORT):
        print("[ERROR] El servidor no respondió a tiempo. Abortando.")
        return

    print("Servidor listo. Abriendo interfaz gráfica...")
    GUI.main()


if __name__ == "__main__":
    main()