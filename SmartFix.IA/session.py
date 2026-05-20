from datetime import datetime

# ─── Memoria de sesión ───────────────────────────────────────────────────────
# A diferencia de Jarvis, SmartFix NO guarda datos personales.
# Solo recuerda la sesión actual del cliente para dar mejor contexto.

def new_session() -> dict:
    """Crea una sesión limpia para un nuevo cliente."""
    return {
        "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "started_at": datetime.now().isoformat(),
        "search_history": [],       # Qué buscó el cliente
        "products_shown": [],       # Productos que ya se mostraron
        "current_product": None,    # Producto en navegación activa
        "state": "greeting",        # greeting | searching | navigating | arrived
        "language_detected": "es",
        "turns": 0
    }

def update_session(session: dict, user_input: str, product_found: dict | None = None) -> dict:
    """Actualiza la memoria de sesión tras cada interacción."""
    session["turns"] += 1
    session["search_history"].append({
        "turn": session["turns"],
        "input": user_input,
        "time": datetime.now().isoformat()
    })

    if product_found:
        session["current_product"] = product_found
        session["state"] = "navigating"
        if product_found["id"] not in session["products_shown"]:
            session["products_shown"].append(product_found["id"])

    return session

def get_context_summary(session: dict) -> str:
    """Genera resumen de contexto para enviar a la IA."""
    history = session["search_history"][-3:]  # Últimas 3 búsquedas
    searches = [h["input"] for h in history]

    current = session.get("current_product")
    current_name = current["name"] if current else "ninguno"

    return (
        f"Turno: {session['turns']}\n"
        f"Estado actual: {session['state']}\n"
        f"Últimas búsquedas: {', '.join(searches) if searches else 'ninguna'}\n"
        f"Producto en navegación: {current_name}"
    )
