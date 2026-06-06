import requests
import json
import os
import time as t
url = "https://datos.aresep.go.cr/ws.datosabiertos/Services/IA/Asadas.svc/ObtenerInformacionUbicacionAsadas"
if "asadas.json" not in os.listdir():
    respuesta = requests.get(url)
    datos = respuesta.json()
    with open("asadas.json", "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)
    print("Archivo JSON guardado correctamente.")
else:
    with open("asadas.json", "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)
    print("Archivo JSON cargado desde disco.")

def escribir_texto_binario(datos, nombre_archivo):
    with open(nombre_archivo, 'wb') as archivo:
        contenido_bytes = json.dumps(datos, ensure_ascii=False).encode('utf-8')
        archivo.write(contenido_bytes)
    print(f"Archivo binario guardado: {nombre_archivo}")

def leer_texto_binario(nombre_archivo):
    with open(nombre_archivo, 'rb') as archivo:
        contenido_bytes = archivo.read()
        datos = json.loads(contenido_bytes.decode('utf-8'))
    return datos
def buscar_asada_por_id(datos, id_asada):
    registros = datos.get("value", [])
    for asada in registros:
        if str(asada.get("id_Asada")) == str(id_asada):
            return asada
    return None
t.sleep(1.5)
print("\033c")
id_buscar = input("Ingrese el ID de la ASADA a buscar: ")
resultado = buscar_asada_por_id(datos, id_buscar)

if resultado:
    print(f"Operador   | {resultado['operador']}")
    print(f"Provincia  | {resultado['provincia']}")
    print(f"Cantón     | {resultado['canton']}")
    print(f"Distrito   | {resultado['distrito']}")
    print(f"Teléfono   | {resultado['telefono']}")
    print(f"Correo     | {resultado['correo']}")
    print(f"Tipo Sistema: {resultado['tipoSistema']}")
    print(f"Coordenadas: X={resultado['coordenadaX'].strip()}, Y={resultado['coordenadaY'].strip()}")
else:
    print(f"No se encontró ninguna ASADA con ID {id_buscar}")

escribir_texto_binario(datos, "asadas.bin")