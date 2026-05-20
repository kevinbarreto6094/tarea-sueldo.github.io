"""
SmartFix — Guía de integración para el mapa 3D
================================================
Este archivo es para los compañeros que trabajan en Blender.
Muestra cómo conectar el mapa 3D al servidor de SmartFix.

PASO 1: Instalar la librería websockets en tu entorno Blender:
  En la terminal de Blender: pip install websockets

PASO 2: Copiar este script en un Text Editor dentro de Blender
  y ejecutarlo con "Run Script".

PASO 3: El mapa recibirá comandos de navegación con este formato:
  {
    "type": "navigate",
    "product_id": "P003",
    "coords": {"x": 25, "y": 0, "z": 5},
    "section": "Herramientas eléctricas"
  }

  Con esos datos, el mapa 3D debe:
  - Mover la cámara (o un marcador) a las coordenadas x, y, z
  - Mostrar el nombre de la sección
  - Animar la ruta desde la entrada hasta el producto
"""

import asyncio
import json
import threading

# Si estás en Blender, importa bpy:
# import bpy

try:
    import websockets
except ImportError:
    print("ERROR: Instala websockets con: pip install websockets")
    raise

SERVER_URL = "ws://localhost:8765"  # Cambia si el servidor está en otra IP

# ─── Función que recibe los comandos de navegación ───────────────────────────
async def connect_to_smartfix():
    async with websockets.connect(SERVER_URL) as ws:
        print("[Mapa 3D] Conectado a SmartFix.")

        # Identificarse como el mapa
        await ws.send(json.dumps({"type": "map_connect"}))

        # Esperar confirmación
        ack = await ws.recv()
        print(f"[Mapa 3D] {json.loads(ack)['msg']}")

        # Escuchar comandos de navegación
        async for raw_msg in ws:
            data = json.loads(raw_msg)

            if data["type"] == "navigate":
                product_id = data["product_id"]
                coords     = data["coords"]       # {"x": 25, "y": 0, "z": 5}
                section    = data["section"]

                print(f"\n[Mapa 3D] NAVEGAR → Producto {product_id}")
                print(f"          Sección: {section}")
                print(f"          Coords:  x={coords['x']}, y={coords['y']}, z={coords['z']}")

                # ─── AQUÍ VA EL CÓDIGO DE BLENDER ──────────────────────────
                # Ejemplo de lo que deben hacer los compañeros:
                #
                # import bpy
                # camera = bpy.data.objects["Camera"]
                # camera.location.x = coords["x"]
                # camera.location.y = coords["y"]
                # camera.location.z = coords["z"] + 5  # un poco arriba
                # bpy.context.view_layer.update()
                #
                # También pueden mover un marcador o avatar:
                # marker = bpy.data.objects["PlayerMarker"]
                # marker.location = (coords["x"], coords["y"], coords["z"])
                # ───────────────────────────────────────────────────────────

                navigate_in_blender(coords, section, product_id)

# ─── Función placeholder para Blender ────────────────────────────────────────
def navigate_in_blender(coords: dict, section: str, product_id: str):
    """
    REEMPLAZA este código con la lógica real de Blender.
    Los compañeros deben implementar aquí la animación del mapa 3D.
    """
    print(f"[Blender] Animando navegación a {section} ({product_id})")
    print(f"[Blender] Posición destino: {coords}")
    # TODO: Implementar animación real en Blender

# ─── Ejecutar en hilo separado (compatible con Blender) ──────────────────────
def run_in_background():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(connect_to_smartfix())

if __name__ == "__main__":
    # Modo standalone (prueba sin Blender)
    asyncio.run(connect_to_smartfix())

# Para Blender, usar:
# thread = threading.Thread(target=run_in_background, daemon=True)
# thread.start()
