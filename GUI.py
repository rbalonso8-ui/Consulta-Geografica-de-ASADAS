import socket
import threading
import tkinter as tk
from tkinter import ttk, messagebox

HOST = "127.0.0.1"   # IP o nombre del servidor (cambiar si está en otro equipo)
PORT = 5050


def enviar_peticion(entrada, salida, peticion: str) -> list[str]:
    """Envía una petición al servidor y devuelve las líneas de la respuesta

    Args:
        entrada: Flujo de lectura asociado al socket
        salida: Flujo de escritura asociado al socket
        peticion (str): Petición a enviar al servidor

    Returns:
        list[str]: Líneas de la respuesta, sin incluir la línea final "FIN". Si la
            conexión falla o el servidor no responde, devuelve una respuesta de error.
    """
    try:
        salida.write(peticion + "\n")
        salida.flush()

        respuesta = []
        for línea in entrada:
            línea = línea.rstrip("\n")
            if línea == "FIN":
                break
            respuesta.append(línea)

        if not respuesta:
            return ["ERROR", "El servidor cerró la conexión o no devolvió datos."]
        return respuesta
    except (BrokenPipeError, ConnectionResetError, OSError):
        return ["ERROR", "Se perdió la conexión con el servidor."]


def construir_jerarquia(entrada, salida) -> dict:
    """Descarga del servidor la jerarquía geográfica completa y la guarda en memoria

    Construye un diccionario anidado provincia -> cantón -> [distritos] consultando
    al servidor por niveles. Esto permite que los combos dependientes se actualicen
    de forma local e instantánea sin pedir datos en cada selección.

    Args:
        entrada: Flujo de lectura asociado al socket
        salida: Flujo de escritura asociado al socket

    Returns:
        dict: Jerarquía geográfica en memoria
    """
    jerarquia = {}

    respuesta = enviar_peticion(entrada, salida, "PROVINCIAS")
    if respuesta[0] != "OK":
        return jerarquia

    for provincia in respuesta[1:]:
        jerarquia[provincia] = {}
        resp_cantones = enviar_peticion(entrada, salida, f"CANTONES|{provincia}")
        if resp_cantones[0] != "OK":
            continue

        for cantón in resp_cantones[1:]:
            resp_distritos = enviar_peticion(entrada, salida, f"DISTRITOS|{provincia}|{cantón}")
            distritos = resp_distritos[1:] if resp_distritos[0] == "OK" else []
            jerarquia[provincia][cantón] = distritos

    return jerarquia


def buscar_camino_distrito(jerarquia: dict, distrito: str) -> tuple:
    """Busca a qué provincia y cantón pertenece un distrito dado

    Args:
        jerarquia (dict): Jerarquía geográfica en memoria
        distrito (str): Nombre del distrito a localizar

    Returns:
        tuple: (provincia, cantón) del distrito, o (None, None) si no se encuentra
    """
    for provincia in jerarquia:
        for cantón in jerarquia[provincia]:
            if distrito in jerarquia[provincia][cantón]:
                return provincia, cantón
    return None, None


def buscar_camino_canton(jerarquia: dict, cantón: str) -> str:
    """Busca a qué provincia pertenece un cantón dado

    Args:
        jerarquia (dict): Jerarquía geográfica en memoria
        cantón (str): Nombre del cantón a localizar

    Returns:
        str or None: Provincia del cantón, o None si no se encuentra
    """
    for provincia in jerarquia:
        if cantón in jerarquia[provincia]:
            return provincia
    return None


class AplicacionGUI:
    """Interfaz gráfica de consulta geografíca de ASADAS conectada al servidor por sockets
    """
    def __init__(self, ventana: tk.Tk):
        """Constructor de la aplicación gráfica

        Args:
            ventana (tk.Tk): Ventana raíz de Tkinter
        """
        self.ventana = ventana
        self.ventana.title("Consulta Geografíca de ASADAS")
        self.ventana.geometry("760x620")

        self.conexión = None
        self.entrada = None
        self.salida = None
        self.jerarquia = {}
        self.actualizando = False  # evita recursión entre los combos

        self._construir_widgets()
        self._conectar()

    def _conectar(self):
        """Establece la conexión con el servidor y descarga la jerarquía geográfica"""
        try:
            self.conexión = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conexión.connect((HOST, PORT))
            self.entrada = self.conexión.makefile("r", encoding="utf-8")
            self.salida = self.conexión.makefile("w", encoding="utf-8")
            self.jerarquia = construir_jerarquia(self.entrada, self.salida)

            self.combo_provincia["values"] = sorted(self.jerarquia.keys())
            self.combo_canton["values"] = self._todos_los_cantones()
            self.combo_distrito["values"] = self._todos_los_distritos()
            self.combo_asada["values"] = self._todas_las_asadas()
        except Exception as error:
            messagebox.showerror("Error de conexión", f"No se pudo conectar al servidor:\n{error}")

    def _todos_los_cantones(self) -> list:
        """Devuelve la lista ordenada de todos los cantones de todas las provincias

        Returns:
            list: Lista de nombres de cantones
        """
        cantones = []
        for provincia in self.jerarquia:
            cantones.extend(self.jerarquia[provincia].keys())
        return sorted(set(cantones))

    def _todos_los_distritos(self) -> list:
        """Devuelve la lista ordenada de todos los distritos de todos los cantones

        Returns:
            list: Lista de nombres de distritos
        """
        distritos = []
        for provincia in self.jerarquia:
            for cantón in self.jerarquia[provincia]:
                distritos.extend(self.jerarquia[provincia][cantón])
        return sorted(set(distritos))

    def _todas_las_asadas(self) -> list:
        """Pide al servidor los códigos de todas las ASADAs de todas las provincias

        Returns:
            list: Lista de códigos de ASADA de todo el país
        """
        códigos = []
        for provincia in sorted(self.jerarquia.keys()):
            códigos.extend(self._códigos_por_peticion(f"ASADAS|{provincia}"))
        return códigos

    def _códigos_por_peticion(self, peticion: str) -> list:
        """Envía una petición de ASADAS al servidor y extrae solo los códigos

        Args:
            peticion (str): Petición ASADAS con el nivel deseado

        Returns:
            list: Lista de códigos de ASADA, o lista vacía si no hubo resultados
        """
        if not self.conexión:
            return []
        respuesta = enviar_peticion(self.entrada, self.salida, peticion)
        if respuesta[0] != "OK":
            return []
        return [fila.split(";")[0] for fila in respuesta[1:]]

    def _construir_widgets(self):
        """Crea y posiciona todos los componentes visuales de la ventana"""
        estilo = ttk.Style()
        estilo.theme_use("clam")  # "clam" sí respeta los colores de fondo en Mac
        estilo.configure("Azul.TButton", foreground="white", background="#2563eb",
                         font=("Helvetica", 11, "bold"))
        estilo.map("Azul.TButton", background=[("active", "#1e40af")])
        estilo.configure("Verde.TButton", foreground="white", background="#16a34a",
                         font=("Helvetica", 11, "bold"))
        estilo.map("Verde.TButton", background=[("active", "#15803d")])
        estilo.configure("Rojo.TButton", foreground="white", background="#dc2626",
                         font=("Helvetica", 11, "bold"))
        estilo.map("Rojo.TButton", background=[("active", "#b91c1c")])

        marco_busqueda = ttk.LabelFrame(self.ventana, text="Buscar ASADA")
        marco_busqueda.pack(fill="x", padx=10, pady=8)

        ttk.Label(marco_busqueda, text="ID de la ASADA:").grid(row=0, column=0, padx=6, pady=8, sticky="w")
        self.entrada_id = ttk.Entry(marco_busqueda, width=20)
        self.entrada_id.grid(row=0, column=1, padx=6, pady=8, sticky="w")
        ttk.Button(marco_busqueda, text="Buscar", command=self.buscar_por_id, style="Azul.TButton").grid(row=0, column=2, padx=6, pady=8)
        ttk.Button(marco_busqueda, text="Ver en mapa", command=self.ver_en_mapa, style="Verde.TButton").grid(row=0, column=3, padx=6, pady=8)

        marco_geo = ttk.LabelFrame(self.ventana, text="Buscar ASADA")
        marco_geo.pack(fill="x", padx=10, pady=8)

        ttk.Label(marco_geo, text="Provincia:").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        self.combo_provincia = ttk.Combobox(marco_geo, state="readonly", width=30)
        self.combo_provincia.grid(row=0, column=1, padx=6, pady=6, sticky="w")
        self.combo_provincia.bind("<<ComboboxSelected>>", self.al_seleccionar_provincia)

        ttk.Label(marco_geo, text="Cantón:").grid(row=1, column=0, padx=6, pady=6, sticky="w")
        self.combo_canton = ttk.Combobox(marco_geo, state="readonly", width=30)
        self.combo_canton.grid(row=1, column=1, padx=6, pady=6, sticky="w")
        self.combo_canton.bind("<<ComboboxSelected>>", self.al_seleccionar_canton)

        ttk.Label(marco_geo, text="Distrito:").grid(row=2, column=0, padx=6, pady=6, sticky="w")
        self.combo_distrito = ttk.Combobox(marco_geo, state="readonly", width=30)
        self.combo_distrito.grid(row=2, column=1, padx=6, pady=6, sticky="w")
        self.combo_distrito.bind("<<ComboboxSelected>>", self.al_seleccionar_distrito)

        ttk.Label(marco_geo, text="ASADA:").grid(row=3, column=0, padx=6, pady=6, sticky="w")
        self.combo_asada = ttk.Combobox(marco_geo, state="readonly", width=30)
        self.combo_asada.grid(row=3, column=1, padx=6, pady=6, sticky="w")
        self.combo_asada.bind("<<ComboboxSelected>>", self.al_seleccionar_asada)
        ttk.Button(marco_geo, text="Mostrar", command=self.mostrar_asada_combo, style="Azul.TButton").grid(row=3, column=2, padx=6, pady=6)
        ttk.Button(marco_geo, text="Ver en mapa", command=self.ver_en_mapa_combo, style="Verde.TButton").grid(row=3, column=3, padx=6, pady=6)

        ttk.Button(marco_geo, text="Limpiar", command=self.limpiar_combos, style="Rojo.TButton").grid(row=4, column=1, padx=6, pady=8, sticky="w")

        marco_resultado = ttk.LabelFrame(self.ventana, text="ASADAS")
        marco_resultado.pack(fill="both", expand=True, padx=10, pady=8)

        self.texto_resultado = tk.Text(marco_resultado, wrap="none", height=15)
        self.texto_resultado.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=6)
        barra = ttk.Scrollbar(marco_resultado, command=self.texto_resultado.yview)
        barra.pack(side="right", fill="y", pady=6)
        self.texto_resultado.config(yscrollcommand=barra.set)

    def _escribir_resultado(self, texto: str):
        """Reemplaza el contenido de la caja de resultados con el texto dado

        Args:
            texto (str): Texto a mostrar en la caja de resultados
        """
        self.texto_resultado.delete("1.0", "end")
        self.texto_resultado.insert("1.0", texto)

    def al_seleccionar_provincia(self, evento=None):
        """Filtra cantón, distrito y ASADA a la provincia elegida y actualiza la tabla

        Las listas inferiores se llenan con las opciones de la provincia (no se
        vacían), de modo que el usuario puede saltar directamente a elegir un
        distrito o una ASADA sin pasar por el cantón.

        Args:
            evento: Evento de selección del combo (no se usa)
        """
        if self.actualizando:
            return
        self.actualizando = True

        provincia = self.combo_provincia.get()
        self.combo_canton["values"] = sorted(self.jerarquia.get(provincia, {}).keys())
        self.combo_distrito["values"] = self._distritos_de_provincia(provincia)
        self.combo_canton.set("")
        self.combo_distrito.set("")
        self.combo_asada.set("")
        self.combo_asada["values"] = self._códigos_por_peticion(f"ASADAS|{provincia}")

        self.actualizando = False
        self._actualizar_tabla()

    def al_seleccionar_canton(self, evento=None):
        """Autocompleta la provincia y filtra distrito y ASADA al cantón elegido

        Si el usuario elige un cantón sin haber elegido provincia, esta se completa
        automáticamente a partir de la jerarquía en memoria.

        Args:
            evento: Evento de selección del combo (no se usa)
        """
        if self.actualizando:
            return
        self.actualizando = True

        cantón = self.combo_canton.get()
        provincia = self.combo_provincia.get()

        if not provincia or cantón not in self.jerarquia.get(provincia, {}):
            provincia = buscar_camino_canton(self.jerarquia, cantón)
            if provincia:
                self.combo_provincia.set(provincia)
                self.combo_canton["values"] = sorted(self.jerarquia[provincia].keys())
                self.combo_canton.set(cantón)

        self.combo_distrito["values"] = sorted(self.jerarquia.get(provincia, {}).get(cantón, []))
        self.combo_distrito.set("")
        self.combo_asada.set("")
        self.combo_asada["values"] = self._códigos_por_peticion(f"ASADAS|{provincia}|{cantón}")

        self.actualizando = False
        self._actualizar_tabla()

    def al_seleccionar_distrito(self, evento=None):
        """Autocompleta provincia y cantón, filtra la ASADA al distrito y actualiza la tabla

        Permite "brincar" niveles: si el usuario elige solo un distrito, la provincia
        y el cantón correspondientes se completan automáticamente.

        Args:
            evento: Evento de selección del combo (no se usa)
        """
        if self.actualizando:
            return
        self.actualizando = True

        distrito = self.combo_distrito.get()
        provincia, cantón = buscar_camino_distrito(self.jerarquia, distrito)

        if provincia and cantón:
            self.combo_provincia.set(provincia)
            self.combo_canton["values"] = sorted(self.jerarquia[provincia].keys())
            self.combo_canton.set(cantón)
            self.combo_distrito["values"] = sorted(self.jerarquia[provincia][cantón])
            self.combo_distrito.set(distrito)
            self.combo_asada.set("")
            self.combo_asada["values"] = self._códigos_por_peticion(f"ASADAS|{provincia}|{cantón}|{distrito}")

        self.actualizando = False
        self._actualizar_tabla()

    def al_seleccionar_asada(self, evento=None):
        """Autocompleta provincia, cantón y distrito a partir de la ASADA elegida

        Consulta al servidor los datos de la ASADA seleccionada y rellena los tres
        combos superiores con su ubicación geográfica.

        Args:
            evento: Evento de selección del combo (no se usa)
        """
        if self.actualizando:
            return
        self.actualizando = True

        id_asada = self.combo_asada.get()
        respuesta = enviar_peticion(self.entrada, self.salida, f"BUSCAR_ID|{id_asada}")

        if respuesta[0] == "OK":
            datos = {}
            for línea in respuesta[1:]:
                clave, _, valor = línea.partition("=")
                datos[clave] = valor

            provincia = datos.get("provincia", "").strip().upper()
            cantón = datos.get("canton", "").strip().upper()
            distrito = datos.get("distrito", "").strip().upper()

            if provincia in self.jerarquia:
                self.combo_provincia.set(provincia)
                self.combo_canton["values"] = sorted(self.jerarquia[provincia].keys())
                self.combo_canton.set(cantón)
                self.combo_distrito["values"] = sorted(self.jerarquia[provincia].get(cantón, []))
                self.combo_distrito.set(distrito)
                self.combo_asada["values"] = self._códigos_por_peticion(f"ASADAS|{provincia}|{cantón}|{distrito}")
                self.combo_asada.set(id_asada)

        self.actualizando = False
        self._mostrar_datos_id(id_asada)

    def _distritos_de_provincia(self, provincia: str) -> list:
        """Devuelve todos los distritos de una provincia, de todos sus cantones

        Args:
            provincia (str): Nombre de la provincia

        Returns:
            list: Lista ordenada de distritos de la provincia
        """
        distritos = []
        for cantón in self.jerarquia.get(provincia, {}):
            distritos.extend(self.jerarquia[provincia][cantón])
        return sorted(set(distritos))

    def _actualizar_tabla(self):
        """Actualiza la tabla de resultados según el nivel geográfico llenado

        Muestra las ASADAs del nivel más específico que esté seleccionado: si solo
        hay provincia, todas las de la provincia; si hay provincia y cantón, las del
        cantón; y si hay distrito, las del distrito. Si no hay nada, limpia la tabla.
        """
        if not self.conexión:
            return

        provincia = self.combo_provincia.get()
        cantón = self.combo_canton.get()
        distrito = self.combo_distrito.get()

        if distrito:
            peticion = f"ASADAS|{provincia}|{cantón}|{distrito}"
        elif cantón:
            peticion = f"ASADAS|{provincia}|{cantón}"
        elif provincia:
            peticion = f"ASADAS|{provincia}"
        else:
            self._escribir_resultado("")
            return

        respuesta = enviar_peticion(self.entrada, self.salida, peticion)
        self._mostrar_tabla(respuesta)

    def _mostrar_tabla(self, respuesta: list[str]):
        """Muestra en la caja de resultados una tabla de ASADAs a partir de la respuesta

        Args:
            respuesta (list[str]): Respuesta del servidor a una consulta de ASADAs
        """
        if respuesta[0] == "ERROR":
            self._escribir_resultado(f"[ERROR] {respuesta[1]}")
            return

        encabezado = f"{'ID':<8}{'Operador':<40}{'Cantón':<16}{'Teléfono':<14}"
        líneas = [encabezado, "-" * len(encabezado)]
        for fila in respuesta[1:]:
            id_a, operador, _provincia, canton, _distrito, telefono = fila.split(";")
            líneas.append(f"{id_a:<8}{operador[:38]:<40}{canton:<16}{telefono:<14}")
        líneas.append("")
        líneas.append(f"Total: {len(respuesta) - 1} ASADAS")
        self._escribir_resultado("\n".join(líneas))

    def limpiar_combos(self):
        """Reinicia los cuatro combos, restaura todas sus listas y limpia la tabla"""
        self.actualizando = True
        self.combo_provincia.set("")
        self.combo_canton.set("")
        self.combo_distrito.set("")
        self.combo_asada.set("")
        self.combo_provincia["values"] = sorted(self.jerarquia.keys())
        self.combo_canton["values"] = self._todos_los_cantones()
        self.combo_distrito["values"] = self._todos_los_distritos()
        self.combo_asada["values"] = self._todas_las_asadas()
        self.actualizando = False
        self._escribir_resultado("")

    def _mostrar_datos_id(self, id_asada: str):
        """Solicita al servidor los datos de una ASADA y los muestra en resultados

        Args:
            id_asada (str): Código de la ASADA a consultar
        """
        if not id_asada:
            messagebox.showwarning("Aviso", "Indique un código de ASADA.")
            return
        if not self.conexión:
            messagebox.showerror("Error", "No hay conexión con el servidor.")
            return

        respuesta = enviar_peticion(self.entrada, self.salida, f"BUSCAR_ID|{id_asada}")
        if respuesta[0] == "ERROR":
            self._escribir_resultado(f"[ERROR] {respuesta[1]}")
            return

        líneas = []
        for línea in respuesta[1:]:
            clave, _, valor = línea.partition("=")
            líneas.append(f"{clave:<14}: {valor}")
        self._escribir_resultado("\n".join(líneas))

    def _mostrar_mapa_id(self, id_asada: str):
        """Solicita al servidor que genere el mapa de una ASADA por su código

        Args:
            id_asada (str): Código de la ASADA a ubicar en el mapa
        """
        if not id_asada:
            messagebox.showwarning("Aviso", "Indique un código de ASADA para ver el mapa.")
            return
        if not self.conexión:
            messagebox.showerror("Error", "No hay conexión con el servidor.")
            return

        respuesta = enviar_peticion(self.entrada, self.salida, f"MAPA|{id_asada}")
        if respuesta[0] == "ERROR":
            self._escribir_resultado(f"[ERROR] {respuesta[1]}")
        else:
            self._escribir_resultado(respuesta[1] if len(respuesta) > 1 else "Mapa generado.")

    def buscar_por_id(self):
        """Muestra los datos de la ASADA escrita en el campo de búsqueda superior"""
        self._mostrar_datos_id(self.entrada_id.get().strip())

    def ver_en_mapa(self):
        """Genera el mapa de la ASADA escrita en el campo de búsqueda superior"""
        self._mostrar_mapa_id(self.entrada_id.get().strip())

    def mostrar_asada_combo(self):
        """Muestra los datos de la ASADA seleccionada en el combo de ASADAs"""
        self._mostrar_datos_id(self.combo_asada.get().strip())

    def ver_en_mapa_combo(self):
        """Genera el mapa de la ASADA seleccionada en el combo de ASADAs"""
        self._mostrar_mapa_id(self.combo_asada.get().strip())



def main():
    """Inicia la interfaz gráfica de consulta de ASADAS"""
    ventana = tk.Tk()
    AplicacionGUI(ventana)
    ventana.mainloop()


if __name__ == "__main__":
    main()