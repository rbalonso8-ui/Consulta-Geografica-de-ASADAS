import requests
import json
import os

import archivo_binario as arc
import arbol_binario as ab
import Listas_enlazadas as le

URL = "https://datos.aresep.go.cr/ws.datosabiertos/Services/IA/Asadas.svc/ObtenerInformacionUbicacionAsadas"

ARCHIVO_META = "sincronizacion.txt"  # Archivo que almacena la cantidad de registros de la última sincronización, si cambia la cantidad se actualizan los archivos binarios.


def contar_registros(datos: dict) -> int:
    """Cuenta cuántos registros de ASADA contiene el diccionario de datos

    Args:
        datos (dict): Diccionario con la información de las ASADAs

    Returns:
        int: Cantidad de registros en la clave "value"
    """
    return len(datos.get("value", []))


def leer_conteo_local() -> int:
    """Lee el número de registros de la última sincronización registrada en disco

    Returns:
        int: Cantidad de registros sincronizados, o -1 si nunca se ha sincronizado
    """
    if not os.path.exists(ARCHIVO_META):
        return -1
    with open(ARCHIVO_META, "r", encoding="utf-8") as archivo:
        contenido = archivo.read().strip()
        return int(contenido) if contenido.isdigit() else -1


def guardar_conteo_local(cantidad: int):
    """Guarda el número de registros de la sincronización actual en disco

    Args:
        cantidad (int): Cantidad de registros a registrar como última sincronización
    """
    with open(ARCHIVO_META, "w", encoding="utf-8") as archivo:
        archivo.write(str(cantidad))


def descargar_datos() -> dict:
    """Descarga la información de las ASADAs desde el endpoint de ARESEP

    Returns:
        dict: Diccionario con la información de las ASADAs en formato JSON
    """
    respuesta = requests.get(URL)
    respuesta.raise_for_status()
    return respuesta.json()


def regenerar_estructuras(datos: dict):
    """Regenera completamente los tres archivos binarios del sistema Reconstruye el archivo principal de registros, el árbol binario indexado y la estructura geográfica de listas enlazadas a partir de los datos dados

    Args:
        datos (dict): Diccionario con la información de las ASADAs descargada del endpoint
    """
    lista_asadas = datos["value"]

    arc.escribir_texto_binario(lista_asadas)
    ab.construir(lista_asadas)
    le.construir(lista_asadas)

    with open("asadas.json", "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)

    print("Estructuras regeneradas correctamente.")


def estructuras_completas() -> bool:
    """Verifica que existan todos los archivos binarios del sistema

    Returns:
        bool: True si existen los seis archivos binarios, False en caso contrario
    """
    archivos = (
        "asadas_principal.bin",
        "arbol_binario.bin",
        "provincias.bin",
        "cantones.bin",
        "distritos.bin",
        "ASADAS.bin",
    )
    return all(os.path.exists(archivo) for archivo in archivos)


def actualizar(forzar: bool = False) -> bool:
    """Verifica si los datos remotos cambiaron y regenera las estructuras solo si es necesario
    
    Args:
        forzar (bool): Si es True, regenera las estructuras aunque no se detecten cambios

    Returns:
        bool: True si se regeneraron las estructuras, False si ya estaban actualizadas
    """
    print("Verificando cambios en el endpoint de ARESEP...")
    datos = descargar_datos()

    conteo_remoto = contar_registros(datos)
    conteo_local = leer_conteo_local()

    if not forzar and conteo_remoto == conteo_local and estructuras_completas():
        print(f"Los datos locales ya están actualizados ({conteo_local} registros). No se regenera nada.")
        return False

    if forzar:
        print("Actualización forzada: regenerando estructuras...")
    elif not estructuras_completas():
        print("Faltan archivos binarios. Regenerando estructuras...")
    else:
        print(f"Se detectaron cambios: local={conteo_local}, remoto={conteo_remoto}. Regenerando...")

    regenerar_estructuras(datos)
    guardar_conteo_local(conteo_remoto)
    return True