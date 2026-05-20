"""
SmartFix — Cliente de prueba en terminal
=========================================
Úsalo para testear la IA sin necesitar el mapa 3D.
Simula exactamente lo que haría la tablet del cliente.

Ejecutar:
  1. Primero: python smartfix_server.py
  2. Luego:   python test_client.py
"""

import asyncio
import json
import websockets

SERVER_URL = "ws://localhost:8765"

async def test_chat():
    async with websockets.connect(SERVER_URL) as ws:

        # Identificarse como cliente
        await ws.send(json.dumps({"type": "client_connect"}))

        # Recibir saludo
        msg = await ws.recv()
        data = json.loads(msg)
        print(f"\nSmartFix > {data['text']}\n")

        # Loop de conversación
        while True:
            user_input = input("Tú > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["salir", "exit", "adios"]:
                print("Hasta luego.")
                break

            # Enviar mensaje
            await ws.send(json.dumps({"type": "message", "text": user_input}))

            # Recibir todas las respuestas (puede ser texto + product_info)
            while True:
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=4.0)
                    resp = json.loads(raw)

                    if resp["type"] == "response":
                        print(f"\nSmartFix > {resp['text']}")
                    elif resp["type"] == "product_info":
                        print(f"\n{'─'*40}")
                        print(resp["data"])
                        print(f"{'─'*40}")
                    elif resp["type"] == "warning":
                        print(f"\n[!] {resp['text']}")
                    elif resp["type"] == "navigate":
                        print(f"\n[MAPA] Navegando a coordenadas: {resp.get('coords')}")

                except asyncio.TimeoutError:
                    break  # No hay más mensajes, esperar input del usuario

            print()

if __name__ == "__main__":
    asyncio.run(test_chat())