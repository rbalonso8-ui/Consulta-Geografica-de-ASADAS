import json

TAMAÑO = 58
TAMAÑO_ASADA = 18


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
 
 
        
def texto_a_bytes(texto: str, tamaño: int)-> bytes:
    """Convierte un texto a bytes con un tamaño específico

    Args:
        texto (str): El texto a convertir
        tamaño (int): El tamaño en bytes que debe ocupar el texto

    Returns:
        bytes: El texto convertido a bytes con el tamaño especificado
    """
    return texto.encode('utf-8').ljust(tamaño, b'\x00') [:tamaño]

def entero_a_bytes(entero: int)-> bytes:
    """Convierte un entero a bytes

    Args:
        entero (int): El entero a convertir

    Returns:
        bytes: El entero convertido a bytes
    """
    return entero.to_bytes(4, byteorder='big', signed=True)

def bytes_a_entero(bytes: bytes)-> int:
    """Convierte 4 bytes a entero

    Args:
        bytes (bytes): Los bytes a convertir

    Returns:
        int: El entero convertido desde bytes, puede ser -1 si no hay más nodos
    """
    return int.from_bytes(bytes, byteorder='big', signed=True)

def bytes_a_texto(bytes: bytes)-> str:
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
    archivo.write(entero_a_bytes(nodo.cantón))
 
def escribir_cantón(archivo: str, nodo: Cantón):
    """Escribe el nodo de cantón en un archivo en la posicion actual

    Args:
        archivo (str): nombre del archivo donde se va a escribir el nodo
        nodo (Cantón): cantón a escribir en el archivo
    """
    archivo.write(texto_a_bytes(nodo.nombre, 50))
    archivo.write(entero_a_bytes(nodo.sig_cantón))
    archivo.write(entero_a_bytes(nodo.distrito)) 
 
def escribir_distrito(archivo: str, nodo: Distrito):
    """Escribe el nodo de distrito en un archivo en la posicion actual

    Args:
        archivo (str): nombre del archivo donde se va a escribir el nodo
        nodo (Distrito): distrito a escribir en el archivo
    """
    archivo.write(texto_a_bytes(nodo.nombre, 50))
    archivo.write(entero_a_bytes(nodo.sig_distrito))
    archivo.write(entero_a_bytes(nodo.asada))
 
def escribir_asada(archivo: str, nodo: ASADA):
    """Escribe el nodo ASADA en un archivo en la posición actual

    Args:
        archivo (str): nombre del archivo donde se va a escribir el nodo
        nodo (ASADA): ASADA a escribir en el archivo
    """
    archivo.write(texto_a_bytes(nodo.id_asada, 10))
    archivo.write(entero_a_bytes(nodo.posicion))
    archivo.write(entero_a_bytes(nodo.sig_asada))
    


def construir(lista_asadas: list):
    """Recibe una lista de ASADAS y construye los archivos binarios para provincias, cantones, distritos y ASADAS geográficas

    Args:
        lista_asadas (list): Lista de ASADAS, cada ASADA es un diccionario con las claves "id_asada", "provincia", "canton" y "distrito"
    """
    
    jerarquia = {}
 
    for posición, asada in enumerate(lista_asadas):
        provincia = (asada.get("provincia") or "SIN PROVINCIA").strip().upper()
        cantón = (asada.get("canton")    or "SIN CANTON").strip().upper()
        distrito = (asada.get("distrito")  or "SIN DISTRITO").strip().upper()
        id_asada = str(asada.get("id_Asada") or "").strip()

        posición_principal = posición
 
        if provincia not in jerarquia:
            jerarquia[provincia] = {}
        if cantón not in jerarquia[provincia]:
            jerarquia[provincia][cantón] = {}
        if distrito not in jerarquia[provincia][cantón]:
            jerarquia[provincia][cantón][distrito] = []
 
        jerarquia[provincia][cantón][distrito].append((id_asada, posición_principal))

    for provincia in jerarquia:
        for cantón in jerarquia[provincia]:
            for distrito in jerarquia[provincia][cantón]:
                jerarquia[provincia][cantón][distrito].sort(key=lambda x: x[0])

    nodos_provincias = []
    nodos_cantones   = []
    nodos_distritos  = []
    nodos_asadas_geo = []
 
    for i_prov, nombre_provincia in enumerate(sorted(jerarquia.keys())):
        nodo_provincia = Provincia(nombre_provincia)
        nodo_provincia.sig_provincia = len(nodos_provincias) + 1 if i_prov + 1 < len(jerarquia) else -1
        nodo_provincia.cantón = len(nodos_cantones)
        nodos_provincias.append(nodo_provincia)
 
        cantones_ordenados = sorted(jerarquia[nombre_provincia].keys())
        for i_cant, nombre_cantón in enumerate(cantones_ordenados):
            nodo_cantón = Cantón(nombre_cantón)
            nodo_cantón.sig_cantón = len(nodos_cantones) + 1 if i_cant + 1 < len(cantones_ordenados) else -1
            nodo_cantón.distrito = len(nodos_distritos)
            nodos_cantones.append(nodo_cantón)
 
            distritos_ordenados = sorted(jerarquia[nombre_provincia][nombre_cantón].keys())
            for i_dist, nombre_distrito in enumerate(distritos_ordenados):
                nodo_distrito = Distrito(nombre_distrito)
                nodo_distrito.sig_distrito  = len(nodos_distritos) + 1 if i_dist + 1 < len(distritos_ordenados) else -1
                nodo_distrito.asada = len(nodos_asadas_geo)
                nodos_distritos.append(nodo_distrito)
 
                asadas_del_distrito = jerarquia[nombre_provincia][nombre_cantón][nombre_distrito]
                for i_a, (id_a, pos_ppal) in enumerate(asadas_del_distrito):
                    nodo_a = ASADA(id_a, pos_ppal)
                    nodo_a.sig_asada = len(nodos_asadas_geo) + 1 if i_a + 1 < len(asadas_del_distrito) else -1
                    nodos_asadas_geo.append(nodo_a)

    with open("provincias.bin", "wb") as f:
        for nodo in nodos_provincias:
            escribir_provincia(f, nodo)
 
    with open("cantones.bin", "wb") as f:
        for nodo in nodos_cantones:
            escribir_cantón(f, nodo)
 
    with open("distritos.bin", "wb") as f:
        for nodo in nodos_distritos:
            escribir_distrito(f, nodo)
 
    with open("ASADAS.bin", "wb") as f:
        for nodo in nodos_asadas_geo:
            escribir_asada(f, nodo)
 
    print("Archivos creados:")
    print(f"provincias.bin: {len(nodos_provincias)} provincias")
    print(f"cantones.bin: {len(nodos_cantones)} cantones")
    print(f"distritos.bin: {len(nodos_distritos)} distritos")
    print(f"ASADAS.bin: {len(nodos_asadas_geo)} nodos ASADA")



def leer_provincia(archivo:str, posición:int) -> Provincia:
    """Lee un nodo de provincia desde un archivo en una posición específica

    Args:
        archivo(str): Archivo abierto en modo lectura binaria
        posición(int): Posición del nodo a leer (en bytes)

    Returns:
        Provincia(Provincia): El nodo de provincia leído desde el archivo
    """
    archivo.seek(posición * TAMAÑO)
    nodo = Provincia(archivo.read(50).decode("utf-8").rstrip("\x00").rstrip())
    nodo.sig_provincia = bytes_a_entero(archivo.read(4))
    nodo.cantón = bytes_a_entero(archivo.read(4))
    return nodo
 
def leer_cantón(archivo:str, posición:int) -> Cantón:
    """Lee un nodo de cantón desde un archivo en una posición específica

    Args:
        archivo(str): Archivo abierto en modo lectura binaria
        posición(int): Posición del nodo a leer (en bytes)

    Returns:
        Cantón(Cantón): El nodo de cantón leído desde el archivo
    """
    archivo.seek(posición * TAMAÑO)
    nodo = Cantón(archivo.read(50).decode("utf-8").rstrip("\x00").rstrip())
    nodo.sig_cantón = bytes_a_entero(archivo.read(4))
    nodo.distrito = bytes_a_entero(archivo.read(4))
    return nodo

def leer_distrito(archivo:str, posición:int) -> Distrito:
    """Lee un nodo de distrito desde un archivo en una posición específica

    Args:
        archivo(str): Archivo abierto en modo lectura binaria
        posición(int): Posición del nodo a leer (en bytes)

    Returns:
        Distrito(Distrito): El nodo de distrito leído desde el archivo
    """
    archivo.seek(posición * TAMAÑO)
    nodo = Distrito(archivo.read(50).decode("utf-8").rstrip("\x00").rstrip())
    nodo.sig_distrito = bytes_a_entero(archivo.read(4))
    nodo.asada = bytes_a_entero(archivo.read(4))
    return nodo

def leer_asada(archivo:str, posición:int) -> ASADA:
    """Lee un nodo de ASADA desde un archivo en una posición específica

    Args:
        archivo(str): Archivo abierto en modo lectura binaria
        posición(int): Posición del nodo a leer (en bytes)

    Returns:
        ASADA(ASADA): El nodo de ASADA leído desde el archivo
    """
    archivo.seek(posición * TAMAÑO_ASADA)
    id_asada = archivo.read(10).decode("utf-8").rstrip("\x00").rstrip()
    posicion = bytes_a_entero(archivo.read(4))
    nodo = ASADA(id_asada, posicion)
    nodo.sig_asada = bytes_a_entero(archivo.read(4))
    return nodo

def obtener_provincias() -> list[str]:
    """Obtiene los nombres de todas las provincias registradas."""
    provincias = []
    with open("provincias.bin", "rb") as doc:
        indice = 0
        while True:
            nodo = leer_provincia(doc, indice)
            provincias.append(nodo.nombre)
            if nodo.sig_provincia == -1:
                break
            indice = nodo.sig_provincia
    return provincias
    
def obtener_cantones(nombre_provincia: str)-> list[str]:
    """Obtiene todos los cantones guardados dentro de una Provincia

    Args:
        nombre_provincia (str): nombre de la provincia de la cual se quieren obtener los cantones

    Returns:
        list[str]: Lista de nombres de cantones, o lista vacía si no existe
    """
    nombre_provincia = nombre_provincia.strip().upper()
    cantones = []
 
    with open("provincias.bin", "rb") as doc_1, open("cantones.bin", "rb") as doc_2:
        indice = 0
        while True:
            nodo_provincia = leer_provincia(doc_1, indice)
            if nodo_provincia.nombre == nombre_provincia:
                indice_cantón = nodo_provincia.cantón
                while indice_cantón != -1:
                    nodo_cant = leer_cantón(doc_2, indice_cantón)
                    cantones.append(nodo_cant.nombre)
                    indice_cantón = nodo_cant.sig_cantón
                break
            if nodo_provincia.sig_provincia == -1:
                break
            indice = nodo_provincia.sig_provincia
    return cantones

def obtener_distritos(nombre_provincia: str, nombre_cantón: str)-> list[str]:
    """Obtiene todos los distritos guardados dentro de un Cantón específico

    Args:
        nombre_provincia (str): nombre de la provincia a la que pertenece el cantón
        nombre_cantón (str): nombre del cantón del cual se quieren obtener los distritos

    Returns:
        list[str]: Lista de nombres de distritos, o lista vacía si no existe
    """
    nombre_provincia = nombre_provincia.strip().upper()
    nombre_cantón = nombre_cantón.strip().upper()
    distritos = []
 
    with open("provincias.bin", "rb") as doc_1, open("cantones.bin", "rb") as doc_2, open("distritos.bin", "rb") as doc_3:
        indice_provincia = 0
        while True:
            nodo_provincia = leer_provincia(doc_1, indice_provincia)
            if nodo_provincia.nombre == nombre_provincia:
                indice_cantón = nodo_provincia.cantón
                while indice_cantón != -1:
                    nodo_cant = leer_cantón(doc_2, indice_cantón)
                    if nodo_cant.nombre == nombre_cantón:
                        indice_distrito = nodo_cant.distrito
                        while indice_distrito != -1:
                            nodo_dist = leer_distrito(doc_3, indice_distrito)
                            distritos.append(nodo_dist.nombre)
                            indice_distrito = nodo_dist.sig_distrito
                        break
                    indice_cantón = nodo_cant.sig_cantón
                break
            if nodo_provincia.sig_provincia == -1:
                break
            indice_provincia = nodo_provincia.sig_provincia
    return distritos

def obtener_asadas(nombre_provincia: str, nombre_cantón: str, nombre_distrito: str)-> list[str]:
    """Obtiene todas las ASADAS guardadas dentro de un Distrito específico

    Args:
        nombre_provincia (str): nombre de la provincia a la que pertenece el distrito
        nombre_cantón (str): nombre del cantón al que pertenece el distrito
        nombre_distrito (str): nombre del distrito del cual se quieren obtener las ASADAS

    Returns:
        list[str]: Lista de IDs de ASADAS, o lista vacía si no existe
    """
    nombre_provincia = nombre_provincia.strip().upper()
    nombre_cantón = nombre_cantón.strip().upper()
    nombre_distrito = nombre_distrito.strip().upper()
    asadas = []
 
    with open("provincias.bin", "rb") as doc_1, open("cantones.bin", "rb") as doc_2, open("distritos.bin", "rb") as doc_3, open("ASADAS.bin", "rb") as doc_4:
        indice_provincia = 0
        while True:
            nodo_provincia = leer_provincia(doc_1, indice_provincia)
            if nodo_provincia.nombre == nombre_provincia:
                indice_cantón = nodo_provincia.cantón
                while indice_cantón != -1:
                    nodo_cantón = leer_cantón(doc_2, indice_cantón)
                    if nodo_cantón.nombre == nombre_cantón:
                        indice_distrito = nodo_cantón.distrito
                        while indice_distrito != -1:
                            nodo_distrito = leer_distrito(doc_3, indice_distrito)
                            if nodo_distrito.nombre == nombre_distrito:
                                indice_asada = nodo_distrito.asada
                                while indice_asada != -1:
                                    nodo_asada = leer_asada(doc_4, indice_asada)
                                    asadas.append(nodo_asada.id_asada)
                                    indice_asada = nodo_asada.sig_asada
                                break
                            indice_distrito = nodo_distrito.sig_distrito
                        break
                    indice_cantón = nodo_cantón.sig_cantón
                break
            if nodo_provincia.sig_provincia == -1:
                break
            indice_provincia = nodo_provincia.sig_provincia
    return asadas

if __name__ == "__main__":
    with open("asadas.json", "r", encoding="utf-8") as f:
        datos = json.load(f)
    construir(datos["value"])

    print("\nPrueba cantones de Alajuela:")
    for cantón in obtener_cantones("ALAJUELA"):
        print(" ", cantón)

    print("\nPrueba distritos de San Carlos:")
    for distrito in obtener_distritos("ALAJUELA", "SAN CARLOS"):
        print(" ", distrito)

    print("\nPrueba ASADAS de Quesada:")
    for asada in obtener_asadas("ALAJUELA", "SAN CARLOS", "QUESADA"):
        print(" ", asada)