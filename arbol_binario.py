class Nodo:
    """Representa un nodo del árbol binario de busqueda de la memoria
    """
    def __init__(self, id_asada: str, posición: int):
        """Constructor del Nodo del arbol binario

        Args:
            id_asada (str): Identificador de la ASADA a almacenar en el nodo
            posición (int): Posición del nodo en asadas_principal.bin
        """
        self.id_asada = id_asada
        self.posición = posición
        self.izquierda = -1
        self.derecha = -1

class ArbolBinario:
    """Representa el árbol binario de busqueda de la memoria
    """
    def __init__(self):
        """Constructor del ArbolBinario
        """
        self.nodos: list[Nodo] = []
        self.raíz = None



def texto_a_bytes(texto: str, tamaño: int) -> bytes:
    """Convierte un texto a bytes con tamaño especifico

    Args:
        texto (str): Texto a convertir a bytes
        tamaño (int): Tamaño fijo en bytes para el campo

    Returns:
        bytes: Bytes resultantes de la conversión
    """
    return str(texto or "").encode('utf-8').ljust(tamaño, b'\x00')[:tamaño]

def entero_a_bytes(entero: int) -> bytes:
    """Convierte un entero a bytes

    Args:
        entero (int): Entero a convertir a bytes

    Returns:
        bytes: Bytes resultantes de la conversión
    """
    return entero.to_bytes(4, byteorder='big', signed=True)

def bytes_a_entero(bytes: bytes) -> int:
    """Convierte bytes a un entero

    Args:
        bytes (bytes): Bytes a convertir a entero

    Returns:
        int: Entero resultante de la conversión
    """
    return int.from_bytes(bytes, byteorder='big', signed=True)

