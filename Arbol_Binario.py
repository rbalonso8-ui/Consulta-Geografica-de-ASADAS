class Provincia:
    def __init__(self, nombre):
        self.nombre = nombre
        self.sig_provincia = None
        self.cantón = None

class Cantón:
    def __init__(self, nombre):
        self.nombre = nombre
        self.sig_cantón = None
        self.distrito = None
        
class Distrito:
    def __init__(self, nombre):
        self.nombre = nombre
        self.sig_distrito = None
        self.asada = None
        
class ASADA:
    def __init__(self, id_asada, posicion):
        self.id_asada = id_asada    
        self.posicion = posicion
        self.sig_asada = None