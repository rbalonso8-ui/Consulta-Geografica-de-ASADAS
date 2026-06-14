import webbrowser
import os
import folium
from pyproj import Transformer
import arbol_binario as ab
import archivo_binario as arc

transformador = Transformer.from_crs(
    "EPSG:5367", 
    "EPSG:4326",  
    always_xy=True
)

def convertir_coordenadas(x_crtm05: str, y_crtm05: str) -> tuple:
    """Convierte coordenadas CRTM05 a WGS84 (latitud, longitud).

    Args:
        x_crtm05 (str): Coordenada X en sistema CRTM05
        y_crtm05 (str): Coordenada Y en sistema CRTM05

    Returns:
        tuple: (latitud, longitud) en sistema WGS84,
               o (None, None) si las coordenadas son inválidas
    """
    try:
        longitud, latitud = transformador.transform(float(x_crtm05), float(y_crtm05))
        return latitud, longitud
    except Exception:
        return None, None


def generar_mapa(datos_asada: dict, nombre_archivo: str = "mapa.html"):
    """Genera un archivo HTML con el mapa de una ASADA y lo abre en el navegador.
    
    Args:
        datos_asada (dict): Diccionario con los datos de la ASADA, con las claves coordenadaX, coordenadaY, id_Asada, operador, provincia, canton, distrito
        nombre_archivo (str): Nombre del archivo HTML a generar
    """
    latitud, longitud = convertir_coordenadas(
        datos_asada.get("coordenadaX", "0"),
        datos_asada.get("coordenadaY", "0")
    )

    if latitud is None:
        print("Error: coordenadas inválidas para esta ASADA")
        return

    mapa = folium.Map(
        location=[latitud, longitud],
        zoom_start=15
    )

    información = (
        f"<b>ID:</b> {datos_asada.get('id_Asada', '')}<br>"
        f"<b>Operador:</b> {datos_asada.get('operador', '')}<br>"
        f"<b>Provincia:</b> {datos_asada.get('provincia', '')}<br>"
        f"<b>Cantón:</b> {datos_asada.get('canton', '')}<br>"
        f"<b>Distrito:</b> {datos_asada.get('distrito', '')}<br>"
        f"<b>Teléfono:</b> {datos_asada.get('telefono', '')}"
    )

    folium.Marker(
        location=[latitud, longitud],
        popup=folium.Popup(información, max_width=300),
        tooltip=f"ASADA {datos_asada.get('id_Asada', '')}"
    ).add_to(mapa)

    mapa.save(nombre_archivo)
    ruta = os.path.abspath("mapa.html")
    webbrowser.open(f"file://{ruta}")
    print(f"Mapa generado y abierto: {ruta}")


def mostrar_asada(id_asada: str):
    """Busca una ASADA por id y muestra su ubicación en el mapa.

    Args:
        id_asada (str): Identificador de la ASADA a visualizar
    """

    árbol   = ab.cargar_árbol()
    posición = ab.buscar(árbol, id_asada.strip())

    if posición == -1:
        print(f"No se encontró ninguna ASADA con ID {id_asada}")
        return

    datos = arc.leer_texto_binario(posición)
    generar_mapa(datos)

if __name__ == "__main__":
    id_buscar = input("Ingrese el ID de la ASADA a visualizar: ")
    mostrar_asada(id_buscar)