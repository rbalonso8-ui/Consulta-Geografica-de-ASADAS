import json

TAMAÑO = 18

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
        self.izquierda = None
        self.derecha = None

class ArbolBinario:
    """Representa el árbol binario de busqueda de la memoria
    """
    def __init__(self):
        """Constructor del ArbolBinario
        """
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



def insertar(raíz: Nodo, inicio: int, fin: int, lista: list):
    """Inserta los elementos de la lista en el árbol de forma balanceada.
 
    Args:
        raíz (Nodo): Nodo raíz del subárbol actual
        inicio (int): Índice de inicio del rango actual
        fin (int): Índice de fin del rango actual
        lista (list): Lista de tuplas (id_asada, posición) ordenada por id
    """
    if inicio < raíz.índice:
        medio_izquierda = (inicio + raíz.índice - 1) // 2
        id_asada, posición = lista[medio_izquierda]
        raíz.izquierda = Nodo(id_asada, posición)
        raíz.izquierda.índice = medio_izquierda
        insertar(raíz.izquierda, inicio, raíz.índice - 1, lista)
 
    if raíz.índice < fin:
        medio_derecha = (raíz.índice + 1 + fin) // 2
        id_asada, posición = lista[medio_derecha]
        raíz.derecha = Nodo(id_asada, posición)
        raíz.derecha.índice = medio_derecha
        insertar(raíz.derecha, raíz.índice + 1, fin, lista)
 
 
 
def buscar(árbol: ArbolBinario, id_asada: str) -> int:
    """Busca una ASADA por su id en el árbol cargado en memoria.
 
    Args:
        árbol (ArbolBinario): El árbol donde se va a buscar
        id_asada (str): Identificador de la ASADA a buscar
 
    Returns:
        int: Posición física en asadas_principal.bin, o -1 si no existe
    """
    nodo_actual = árbol.raíz
 
    while nodo_actual is not None:
        if id_asada == nodo_actual.id_asada:
            return nodo_actual.posición
        elif id_asada < nodo_actual.id_asada:
            nodo_actual = nodo_actual.izquierda
        else:
            nodo_actual = nodo_actual.derecha
    return -1
 
 
 
def guardar_árbol(árbol: ArbolBinario, nombre_archivo: str = "arbol_binario.bin"):
    """Escribe el árbol completo en un archivo binario.

    Args:
        árbol (ArbolBinario): El árbol a guardar
        nombre_archivo (str): Nombre del archivo de salida
    """
    nodos_ordenados = []
    índices = {}
 
    def asignar_índices(nodo):
        if nodo is None:
            return
        índices[id(nodo)] = len(nodos_ordenados)
        nodos_ordenados.append(nodo)
        asignar_índices(nodo.izquierda)
        asignar_índices(nodo.derecha)
 
    asignar_índices(árbol.raíz)
 
    with open(nombre_archivo, "wb") as archivo:
        for nodo in nodos_ordenados:
            idx_izquierda = índices[id(nodo.izquierda)] if nodo.izquierda else -1
            idx_derecha = índices[id(nodo.derecha)]   if nodo.derecha   else -1
 
            archivo.write(texto_a_bytes(nodo.id_asada, 6))
            archivo.write(entero_a_bytes(nodo.posición))
            archivo.write(entero_a_bytes(idx_izquierda))
            archivo.write(entero_a_bytes(idx_derecha))
 
    print(f"árbol_binario.bin creado: {len(nodos_ordenados)} nodos de {TAMAÑO} bytes c/u")
 
 
 
 
def cargar_árbol(nombre_archivo: str = "arbol_binario.bin") -> ArbolBinario:
    """Lee arbol_binario.bin y reconstruye el árbol de objetos en memoria.

    Args:
        nombre_archivo (str): Nombre del archivo a leer
 
    Returns:
        ArbolBinario: El árbol reconstruido con objetos apuntándose entre sí
    """
    nodos = []
 
    with open(nombre_archivo, "rb") as archivo:
        while True:
            bloque = archivo.read(TAMAÑO)
            if not bloque:
                break
 
            id_asada = bloque[0:6].decode("utf-8").rstrip('\x00').rstrip()
            posición = bytes_a_entero(bloque[6:10])
            idx_izquierda  = bytes_a_entero(bloque[10:14])
            idx_derecha  = bytes_a_entero(bloque[14:18])
 
            nodo          = Nodo(id_asada, posición)
            nodo.index_izquierda = idx_izquierda
            nodo.index_derecha = idx_derecha
            nodos.append(nodo)
 
    for nodo in nodos:
        nodo.izquierda = nodos[nodo.index_izquierda] if nodo.index_izquierda != -1 else None
        nodo.derecha = nodos[nodo.index_derecha] if nodo.index_derecha != -1 else None
 
    árbol = ArbolBinario()
    árbol.raíz = nodos[0] if nodos else None
 
    print(f"arbol_binario.bin cargado — {len(nodos)} nodos")
    return árbol
 
 
 
def construir(lista_asadas: list) -> ArbolBinario:
    """Construye el árbol binario balanceado desde la lista de ASADAs y guarda arbol_binario.bin.
 
    Args:
        lista_asadas (list): Lista de dicts con los datos de cada ASADA
 
    Returns:
        ArbolBinario: El árbol construido y guardado en arbol_binario.bin
    """
    lista = sorted(
        [(str(a.get("id_Asada") or "").strip(), i) for i, a in enumerate(lista_asadas)],
        key=lambda x: x[0]
    )
 
    árbol = ArbolBinario()
    if not lista:
        return árbol
 
    medio = len(lista) // 2
    id_asada, posición = lista[medio]
    árbol.raíz = Nodo(id_asada, posición)
    árbol.raíz.índice = medio
 
    insertar(árbol.raíz, 0, len(lista) - 1, lista)
 
    guardar_árbol(árbol)
    return árbol
 

 
if __name__ == "__main__":
    with open("asadas.json", "r") as f:
        datos = json.load(f)

    árbol = construir(datos["value"])
    
    print("\nPrueba buscar id 1790:")
    print(f"\tposición = {buscar(árbol, '1790')}")
 
    print("\nPrueba buscar id 9999 (no existe):")
    print(f"\tposición = {buscar(árbol, '9999')}")
 
    print("\nPrueba cargar desde archivo y buscar:")
    árbol2 = cargar_árbol()
    print(f"\tposición desde archivo = {buscar(árbol2, '1790')}")
 
    print("\nRaíz del árbol:")
    print(f"\tid = {árbol.raíz.id_asada}")
    print(f"\tizquierda = {árbol.raíz.izquierda.id_asada if árbol.raíz.izquierda else None}")
    print(f"\tderecha = {árbol.raíz.derecha.id_asada   if árbol.raíz.derecha   else None}")