import requests
import json
import os
import time as t

TAMAÑO_REGISTRO = 6 + 170 + 12 + 22 + 27 + 22 + 22 + 17 + 40 + 17 + 4

url = "https://datos.aresep.go.cr/ws.datosabiertos/Services/IA/Asadas.svc/ObtenerInformacionUbicacionAsadas"
    
def campo_texto(valor: str, n: int) -> bytes:
    """Convierte un valor de bytes de longitud exacta n

    Args:
        valor (str): texto a convertir
        n (int): tamaño exacto en bytes

    Returns:
        bytes: bytes de longitud exacta n
    """
    return str(valor or "").encode("utf-8").ljust(n, b'\x00')[:n]

def leer_campo(bytes_campo: bytes) -> str:
    """Convierte un campo de bytes a texto, eliminando el relleno de nulos
 
    Args:
        bytes_campo (bytes): Bytes a convertir
 
    Returns:
        str: Texto sin los caracteres de relleno
    """
    return bytes_campo.decode("utf-8").rstrip('\x00').rstrip()

def buscar_asada_por_id(datos: dict, id_asada: str) -> dict:
    """Busca ASADA por su id recorriendo la lista

    Args:
        datos (dict): Diccionario con la información de las ASADAs
        id_asada (str): ID de la ASADA a buscar

    Returns:
        dict or None: Datos de la ASADA encontrada o None si no existe
    """
    registros = datos.get("value", [])
    for asada in registros:
        if str(asada.get("id_Asada")) == str(id_asada):
            return asada
    return None


def escribir_texto_binario(lista_asadas: list):
    """Crea asdas_principal.bin con un tamaño fijo

    Args:
        lista_asadas (list): Lista de diccionarios con los datos de cada ASADA
    """
    
    with open("asadas_principal.bin", "wb") as archivo:
        for asada in lista_asadas:
            archivo.write(campo_texto(asada.get("id_Asada"), 6))
            archivo.write(campo_texto(asada.get("operador"), 170))
            archivo.write(campo_texto(asada.get("provincia"), 12))
            archivo.write(campo_texto(asada.get("canton"), 22))
            archivo.write(campo_texto(asada.get("distrito"), 27))
            archivo.write(campo_texto(asada.get("coordenadaX"), 22))
            archivo.write(campo_texto(asada.get("coordenadaY"), 22))
            archivo.write(campo_texto(asada.get("telefono"), 17))
            archivo.write(campo_texto(asada.get("correo"), 40))
            archivo.write(campo_texto(asada.get("tipoSistema"), 17))
            archivo.write((int(asada.get("codigoDTA") or 0)).to_bytes(4, byteorder='big'))
 
    print(f"asadas_principal.bin creado — {len(lista_asadas)} registros de {TAMAÑO_REGISTRO} bytes c/u")

def leer_texto_binario(posicion: int) -> dict:
    """Lee el registro en la posición dada y devuelve sus datos

    Args:
        posicion (int): Índice del registro a leer

    Returns:
        dict: Datos del registro leído
    """
    with open("asadas_principal.bin", "rb") as archivo:
        archivo.seek(posicion * TAMAÑO_REGISTRO)
        return {
            "id_Asada": leer_campo(archivo.read(6)),
            "operador": leer_campo(archivo.read(170)),
            "provincia": leer_campo(archivo.read(12)),
            "canton": leer_campo(archivo.read(22)),
            "distrito": leer_campo(archivo.read(27)),
            "coordenadaX": leer_campo(archivo.read(22)),
            "coordenadaY": leer_campo(archivo.read(22)),
            "telefono": leer_campo(archivo.read(17)),
            "correo": leer_campo(archivo.read(40)),
            "tipoSistema": leer_campo(archivo.read(17)),
            "codigoDTA": int.from_bytes(archivo.read(4), byteorder='big')
    }

def descargar_json()-> dict:
    if "asadas.json" not in os.listdir():
        respuesta = requests.get(url)
        datos = respuesta.json()
        with open("asadas.json", "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)
        print("Archivo JSON guardado correctamente.")
    else:
        with open("asadas.json", "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        print("Archivo JSON cargado desde disco.")
    return datos
    
if __name__ == "__main__":
    datos = descargar_json()
    escribir_texto_binario(datos["value"])
 
    id_buscar = input("Ingrese el ID de la ASADA a buscar: ")
    resultado = buscar_asada_por_id(datos, id_buscar)
    if resultado:
        print(f"Operador   | {resultado['operador']}")
        print(f"Provincia  | {resultado['provincia']}")
        print(f"Cantón     | {resultado['canton']}")
        print(f"Distrito   | {resultado['distrito']}")
        print(f"Teléfono   | {resultado['telefono']}")
        print(f"Correo     | {resultado['correo']}")
        print(f"Tipo Sistema: {resultado['tipoSistema']}")
        print(f"Coordenadas: X={resultado['coordenadaX'].strip()}, Y={resultado['coordenadaY'].strip()}")
    else:
        print(f"No se encontró ninguna ASADA con ID {id_buscar}")