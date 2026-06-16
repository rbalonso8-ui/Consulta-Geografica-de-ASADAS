import socket
from time import time

HOST = "127.0.0.1"   # IP o nombre del servidor (cambiar si está en otro equipo)
PORT = 5050


def enviar_peticion(entrada, salida, peticion: str) -> list[str]:
    """Envía una petición al servidor y devuelve las líneas de la respuesta
 
    Args:
        entrada: Flujo de lectura asociado al socket
        salida: Flujo de escritura asociado al socket
        peticion (str): Petición a enviar al servidor
 
    Returns:
        list[str]: Líneas de la respuesta, sin incluir la línea final "FIN"
    """
    salida.write(peticion + "\n")
    salida.flush()

    respuesta = []
    for línea in entrada:
        línea = línea.rstrip("\n")
        if línea == "FIN":
            break
        respuesta.append(línea)
    return respuesta


def mostrar_asada(respuesta: list[str]):
    """Muestra en pantalla los datos de una ASADA recibida del servidor

    Args:
        respuesta (list[str]): Lineas de la respuesta del servidor para una busqueda por ID
    """
    if respuesta[0] == "ERROR":
        print(f"\n[ERROR] {respuesta[1]}")
        return

    print("\n" + "-" * 45)
    for línea in respuesta[1:]:
        clave, _, valor = línea.partition("=")
        print(f"{clave:<12}: {valor}")
    print("-" * 45)
    time.sleep(1)  # Pequeña pausa para mejorar la legibilidad


def mostrar_lista(respuesta: list[str], titulo: str):
    """Muestra en pantalla una lista simple de elementos recibida del servidor
 
    Args:
        respuesta (list[str]): Líneas de respuesta del servidor
        titulo (str): Título a mostrar encima de la lista
    """
    if respuesta[0] == "ERROR":
        print(f"\n[ERROR] {respuesta[1]}")
        return

    print(f"\n{titulo}:")
    for item in respuesta[1:]:
        print(f"  - {item}")


def mostrar_asadas_division(respuesta: list[str]):
    """Muestra en pantalla una tabla con las ASADAs de una división geográfica
 
    Args:
        respuesta (list[str]): Líneas de respuesta del servidor para una consulta por distrito
    """
    if respuesta[0] == "ERROR":
        print(f"\n[ERROR] {respuesta[1]}")
        return

    print("\n" + "-" * 75)
    print(f"{'ID':<8}{'Operador':<38}{'Cantón':<15}{'Teléfono':<12}")
    print("-" * 75)
    for fila in respuesta[1:]:
        id_a, operador, _provincia, canton, _distrito, telefono = fila.split(";")
        print(f"{id_a:<8}{operador[:36]:<38}{canton:<15}{telefono:<12}")
    print("-" * 75)


def menu() -> str:
    """Muestra el menú principal y solicita la opción al usuario
 
    Returns:
        str: Opción seleccionada por el usuario
    """
    print("\n=== Consulta remota de ASADAS ===")
    print("1. Buscar ASADA por identificador")
    print("2. Ver provincias disponibles")
    print("3. Ver cantones de una provincia")
    print("4. Ver distritos de un cantón")
    print("5. Ver ASADAS de un distrito")
    print("6. Salir")
    return input("Seleccione una opción: ").strip()


def main():
    """Conecta con el servidor y hace el ciclo de consulta por consola
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conexión:
        conexión.connect((HOST, PORT))
        entrada = conexión.makefile("r", encoding="utf-8")
        salida = conexión.makefile("w", encoding="utf-8")

        print(f"Conectado al servidor en {HOST}:{PORT}")

        while True:
            opción = menu()

            if opción == "1":
                id_asada = input("ID de la ASADA: ").strip()
                respuesta = enviar_peticion(entrada, salida, f"BUSCAR_ID|{id_asada}")
                mostrar_asada(respuesta)

            elif opción == "2":
                respuesta = enviar_peticion(entrada, salida, "PROVINCIAS")
                mostrar_lista(respuesta, "Provincias disponibles")

            elif opción == "3":
                provincia = input("Provincia: ").strip()
                respuesta = enviar_peticion(entrada, salida, f"CANTONES|{provincia}")
                mostrar_lista(respuesta, f"Cantones de {provincia.upper()}")

            elif opción == "4":
                provincia = input("Provincia: ").strip()
                cantón = input("Cantón: ").strip()
                respuesta = enviar_peticion(entrada, salida, f"DISTRITOS|{provincia}|{cantón}")
                mostrar_lista(respuesta, f"Distritos de {cantón.upper()}, {provincia.upper()}")

            elif opción == "5":
                provincia = input("Provincia: ").strip()
                cantón = input("Cantón: ").strip()
                distrito = input("Distrito: ").strip()
                respuesta = enviar_peticion(entrada, salida, f"ASADAS|{provincia}|{cantón}|{distrito}")
                mostrar_asadas_division(respuesta)

            elif opción == "6":
                print("Cerrando conexión...")
                break

            else:
                print("Opción inválida.")


if __name__ == "__main__":
    main()