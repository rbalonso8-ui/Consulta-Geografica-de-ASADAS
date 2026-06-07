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



