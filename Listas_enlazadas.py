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
 
    for i_prov, nombre_prov in enumerate(sorted(jerarquia.keys())):
        nodo_prov = Provincia(nombre_prov)
        nodo_prov.sig_provincia = len(nodos_provincias) + 1 if i_prov + 1 < len(jerarquia) else -1
        nodo_prov.primer_canton = len(nodos_cantones)
        nodos_provincias.append(nodo_prov)
 
        cantones_ordenados = sorted(jerarquia[nombre_prov].keys())
        for i_cant, nombre_cant in enumerate(cantones_ordenados):
            nodo_cant = Cantón(nombre_cant)
            nodo_cant.sig_canton      = len(nodos_cantones) + 1 if i_cant + 1 < len(cantones_ordenados) else -1
            nodo_cant.primer_distrito = len(nodos_distritos)
            nodos_cantones.append(nodo_cant)
 
            distritos_ordenados = sorted(jerarquia[nombre_prov][nombre_cant].keys())
            for i_dist, nombre_dist in enumerate(distritos_ordenados):
                nodo_dist = Distrito(nombre_dist)
                nodo_dist.sig_distrito  = len(nodos_distritos) + 1 if i_dist + 1 < len(distritos_ordenados) else -1
                nodo_dist.primera_asada = len(nodos_asadas_geo)
                nodos_distritos.append(nodo_dist)
 
                asadas_del_distrito = jerarquia[nombre_prov][nombre_cant][nombre_dist]
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
 
    print("Archivos geográficos creados:")
    print(f"provincias.bin: {len(nodos_provincias)} provincias")
    print(f"cantones.bin: {len(nodos_cantones)} cantones")
    print(f"distritos.bin: {len(nodos_distritos)} distritos")
    print(f"ASADAS.bin: {len(nodos_asadas_geo)} nodos ASADA")
 
if __name__ == "__main__":
    with open("asadas.json", "r", encoding="utf-8") as f:
        datos = json.load(f)
    construir(datos["value"])