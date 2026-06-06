import json

class Provincia:
    """Representa una Provincia como una lista enlazada
    """
    def __init__(self, nombre):
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
    def __init__(self, nombre):
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
    def __init__(self, nombre):
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
    def __init__(self, id_asada, posicion):
        """Constructor del nodo ASADA

        Args:
            id_asada (int): ID de la ASADA
            posicion (tuple): Posición de la ASADA
        """
        self.id_asada = id_asada    
        self.posicion = posicion
        self.sig_asada: ASADA = -1
 
 
        
def texto_a_bytes(texto, tamaño):
    """Convierte un texto a bytes con un tamaño específico

    Args:
        texto (str): El texto a convertir
        tamaño (int): El tamaño en bytes que debe ocupar el texto

    Returns:
        bytes: El texto convertido a bytes con el tamaño especificado
    """
    return texto.encode('utf-8').ljust(tamaño, b'\x00')

def entero_a_bytes(entero):
    """Convierte un entero a bytes

    Args:
        entero (int): El entero a convertir

    Returns:
        bytes: El entero convertido a bytes
    """
    return entero.to_bytes(4, byteorder='big', signed=True)

def bytes_a_entero(bytes):
    """Convierte 4 bytes a entero

    Args:
        bytes (bytes): Los bytes a convertir

    Returns:
        int: El entero convertido desde bytes, puede ser -1 si no hay más nodos
    """
    return int.from_bytes(bytes, byteorder='big', signed=True)

