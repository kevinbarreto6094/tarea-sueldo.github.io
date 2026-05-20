import asyncio
import json
import websockets
from brain import think
from session import new_session

# Coordenadas 3D de cada producto en el mapa inline
PRODUCT_COORDS = {
    "P001": {"x": 34.7, "z": 13.0},  # Pinturas P15
    "P002": {"x": 34.7, "z": 13.0},  # Esmalte P15
    "P003": {"x": 8.3,  "z": 13.0},  # Taladro P10
    "P004": {"x": 8.3,  "z": 13.0},  # Amoladora P10
    "P005": {"x": 5.1,  "z": 13.0},  # Inodoro P8
    "P006": {"x": 5.1,  "z": 13.0},  # Ducha P8
    "P007": {"x": 24.0, "z": 33.6},  # Foco LED P5
    "P008": {"x": 24.0, "z": 33.6},  # Foco frio P5
    "P009": {"x": 11.5, "z": 13.0},  # Porcelanato P12
    "P010": {"x": 1.9,  "z": 13.0},  # Manguera P6
    "P011": {"x": 28.3, "z": 13.0},  # Electricidad P11
    "P012": {"x": 28.3, "z": 13.0},
    "P013": {"x": 31.5, "z": 13.0},  # Limpieza P13
    "P014": {"x": 25.1, "z": 13.0},  # Tech P9
    "P015": {"x": 34.7, "z": 13.0},  # Pinturas P15
}

chat_clients = {}

async def handler(websocket):
    try:
        first_msg = await websocket.recv()
        data = json.loads(first_msg)
    except Exception:
        return

    # ── Cliente (tablet/kiosko) ───────────────────────────────────────────
    if data.get("type") == "client_connect":
        session    = new_session()
        session_id = session["session_id"]
        lang       = data.get("lang", "es")
        chat_clients[session_id] = websocket
        print(f"[SmartFix] Cliente conectado — sesión {session_id} — idioma: {lang}")

        try:
            async for raw_msg in websocket:
                msg = json.loads(raw_msg)

                if msg.get("type") == "set_lang":
                    lang = msg.get("lang", "es")
                    continue

                if msg.get("type") != "message":
                    continue

                user_text = msg.get("text", "").strip()
                if not user_text:
                    continue

                if msg.get("lang"):
                    lang = msg.get("lang")

                print(f"[Cliente {session_id}] [{lang.upper()}] {user_text}")

                response_text, map_command, session = think(user_text, session, lang)

                await websocket.send(json.dumps({
                    "type": "response",
                    "text": response_text
                }))

                # Si hay comando de navegación
                if map_command:
                    pid    = map_command.get("producto_id", "")
                    coords = PRODUCT_COORDS.get(pid, map_command.get("coords", {"x": 19, "z": 15}))
                    section= map_command.get("section", "")
                    pinfo  = map_command.get("product_info", "")

                    # 1. Primero enviar product_info
                    if pinfo:
                        await websocket.send(json.dumps({
                            "type": "product_info",
                            "data": pinfo
                        }))

                    # 2. Luego enviar navigate (con info incluida)
                    await websocket.send(json.dumps({
                        "type":         "navigate",
                        "product_id":   pid,
                        "coords":       coords,
                        "section":      section,
                        "product_info": pinfo,
                    }))
                    print(f"[Mapa inline] → {pid} coords={coords}")

        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            chat_clients.pop(session_id, None)
            print(f"[SmartFix] Cliente {session_id} desconectado.")

async def main():
    print("=" * 50)
    print("  SmartFix IA — Servidor WebSocket")
    print("  Puerto: 8765")
    print("  Mapa: INLINE en el chat")
    print("  Esperando conexiones...")
    print("=" * 50)
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())