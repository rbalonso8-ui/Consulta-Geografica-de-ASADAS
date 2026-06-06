import json

class Provincia:
    """Representa una Provincia como una lista enlazada
    """
    def __init__(self, nombre: str):
        """Constructor del nodo provincia

        Args:
            nombre (str): nombre de la provincia
        """
        self.nombre = nombre
        self.sig_provincia: Provincia = -1
        self.cantón: Cantón = -1

class Cantón:
    """Representa un Canton como una lista enlazada
    """
    def __init__(self, nombre: str):
        """Constructor del nodo cantón

        Args:
            nombre (str): nombre del cantón
        """
        self.nombre = nombre
        self.sig_cantón: Cantón = -1
        self.distrito: Distrito = -1

class Distrito:
    """Representa un distrito como una lista enlazada
    """
    def __init__(self, nombre: str):
        """Constructor del nodo distrito

        Args:
            nombre (str): nombre del distrito
        """
        self.nombre = nombre
        self.sig_distrito: Distrito = -1
        self.asada: ASADA = -1
        
class ASADA:
    """Representa una ASADA como una lista enlazada
    """
    def __init__(self, id_asada: int, posicion: tuple):
        """Constructor del nodo ASADA

        Args:
            id_asada (int): ID de la ASADA
            posicion (tuple): Posición de la ASADA
        """
        self.id_asada = id_asada    
        self.posicion = posicion
        self.sig_asada: ASADA = -1
 
 
        
def texto_a_bytes(texto: str, tamaño: int):
    """Convierte un texto a bytes con un tamaño específico

    Args:
        texto (str): El texto a convertir
        tamaño (int): El tamaño en bytes que debe ocupar el texto

    Returns:
        bytes: El texto convertido a bytes con el tamaño especificado
    """
    return texto.encode('utf-8').ljust(tamaño, b'\x00')

def entero_a_bytes(entero: int):
    """Convierte un entero a bytes

    Args:
        entero (int): El entero a convertir

    Returns:
        bytes: El entero convertido a bytes
    """
    return entero.to_bytes(4, byteorder='big', signed=True)

def bytes_a_entero(bytes: bytes):
    """Convierte 4 bytes a entero

    Args:
        bytes (bytes): Los bytes a convertir

    Returns:
        int: El entero convertido desde bytes, puede ser -1 si no hay más nodos
    """
    return int.from_bytes(bytes, byteorder='big', signed=True)

def bytes_a_texto(bytes: bytes):
    """Convierte bytes a texto, eliminando los caracteres de relleno

    Args:
        bytes (bytes): Los bytes a convertir

    Returns:
        str: El texto convertido desde bytes, sin los caracteres de relleno
    """
    return bytes.decode('utf-8').rstrip('\x00')




def escribir_provincia(archivo: str, nodo: Provincia):
    """Escribe el nodo de provincia en un archivo en la posicion actual

    Args:
        archivo (str): nombre del archivo donde se va a escribir el nodo
        nodo (Provincia): provincia a escribir en el archivo
    """
    archivo.write(texto_a_bytes(nodo.nombre, 50))
    archivo.write(entero_a_bytes(nodo.sig_provincia))
    archivo.write(entero_a_bytes(nodo.primer_canton))
 
def escribir_cantón(archivo: str, nodo: Cantón):
    """Escribe el nodo de cantón en un archivo en la posicion actual

    Args:
        archivo (str): nombre del archivo donde se va a escribir el nodo
        nodo (Cantón): cantón a escribir en el archivo
    """
    archivo.write(texto_a_bytes(nodo.nombre, 50))
    archivo.write(entero_a_bytes(nodo.sig_canton))
    archivo.write(entero_a_bytes(nodo.primer_distrito)) 
 
def escribir_distrito(archivo: str, nodo: Distrito):
    """Escribe el nodo de distrito en un archivo en la posicion actual

    Args:
        archivo (str): nombre del archivo donde se va a escribir el nodo
        nodo (Distrito): distrito a escribir en el archivo
    """
    archivo.write(texto_a_bytes(nodo.nombre, 50))
    archivo.write(entero_a_bytes(nodo.sig_distrito))
    archivo.write(entero_a_bytes(nodo.primera_asada))
 
def escribir_asada(archivo: str, nodo: ASADA):
    """Escribe el nodo ASADA en un archivo en la posición actual

    Args:
        archivo (str): nombre del archivo donde se va a escribir el nodo
        nodo (ASADA): ASADA a escribir en el archivo
    """
    archivo.write(texto_a_bytes(nodo.id_asada, 10))
    archivo.write(entero_a_bytes(nodo.pos_principal))
    archivo.write(entero_a_bytes(nodo.sig_asada))
    
