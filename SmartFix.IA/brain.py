import requests
import json
import traceback
import os
from product_search import search_product, get_section, format_product_info
from session import get_context_summary

# ─── Configuración ───────────────────────────────────────────────────────────
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip()

load_env()
AI_MODEL     = "llama-3.1-8b-instant"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# ─── Catálogo de productos con marcas ────────────────────────────────────────
CATALOG = {
    "taladro":      {"ids": ["P003"], "marcas": ["dewalt"], "nombre": "Taladro"},
    "pintura":      {"ids": ["P001", "P002"], "marcas": ["vencedor", "tekno"], "nombre": "Pintura"},
    "amoladora":    {"ids": ["P004"], "marcas": ["bosch"], "nombre": "Amoladora"},
    "inodoro":      {"ids": ["P005"], "marcas": ["trebol", "trébol"], "nombre": "Inodoro"},
    "ducha":        {"ids": ["P006"], "marcas": ["corona"], "nombre": "Ducha eléctrica"},
    "foco":         {"ids": ["P007", "P008"], "marcas": ["philips", "osram"], "nombre": "Foco LED"},
    "porcelanato":  {"ids": ["P009"], "marcas": ["san lorenzo"], "nombre": "Porcelanato"},
    "manguera":     {"ids": ["P010"], "marcas": ["hidro"], "nombre": "Manguera"},
}

# Palabras que mapean a categorías
CATEGORY_KEYWORDS = {
    "taladro":     ["taladro", "taladros", "drill", "broca", "brocas", "perforar", "dewalt", "percutor"],
    "pintura":     ["pintura", "pintar", "látex", "latex", "esmalte", "paint", "pared", "color"],
    "amoladora":   ["amoladora", "esmeril", "grinder", "disco", "cortar", "bosch"],
    "inodoro":     ["inodoro", "water", "wc", "sanitario", "toilet", "trebol", "trébol"],
    "ducha":       ["ducha", "terma", "agua caliente", "shower", "heater", "corona"],
    "foco":        ["foco", "focos", "luz", "led", "lámpara", "bulb", "lamp", "iluminación", "philips", "osram"],
    "porcelanato": ["porcelanato", "piso", "cerámica", "ceramic", "baldosa", "tile", "floor", "san lorenzo"],
    "manguera":    ["manguera", "jardín", "riego", "hose", "garden", "hidro"],
}

# Respuestas afirmativas
AFFIRMATIVES = ["si", "sí", "yes", "ok", "dale", "claro", "por favor", "guiame", "guíame", "quiero", "adelante", "aver", "a ver", "bueno", "yeah", "yep", "sure", "va", "vamos", "porfa", "please", "hazlo", "listo", "perfecto", "genial", "okey", "oke", "oke"]

# ─── Detectar categoría ───────────────────────────────────────────────────────
def detect_category(text: str):
    text = text.lower()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return cat
    return None

# ─── Detectar marca mencionada ────────────────────────────────────────────────
def detect_brand(text: str, category: str):
    text = text.lower()
    if category not in CATALOG:
        return None
    for marca in CATALOG[category]["marcas"]:
        if marca in text:
            return marca
    return None

# ─── Obtener producto por categoría y marca ───────────────────────────────────
def get_product_by_brand(category: str, brand: str):
    from product_search import load_products
    products = load_products()["products"]
    brand = brand.lower()
    for pid in CATALOG[category]["ids"]:
        p = next((x for x in products if x["id"] == pid), None)
        if p and brand in p["brand"].lower():
            return p
    return None

def get_products_by_category(category: str):
    from product_search import load_products
    products = load_products()["products"]
    result = []
    for pid in CATALOG[category]["ids"]:
        p = next((x for x in products if x["id"] == pid), None)
        if p:
            result.append(p)
    return result

# ─── Llamada a la IA (solo para preguntas generales) ─────────────────────────
SYSTEM_PROMPT_ES = """Eres SmartFix, asistente de Promart. Responde en español, muy corto y amigable.
Solo haz UNA pregunta a la vez. No navegues ni menciones productos específicos."""

SYSTEM_PROMPT_EN = """You are SmartFix, Promart assistant. Respond in English, very short and friendly.
Only ask ONE question at a time. Do not navigate or mention specific products."""

def call_ai(user_input: str, lang: str = "es") -> str:
    if not GROQ_API_KEY or GROQ_API_KEY == "TU_GROQ_API_KEY_AQUI":
        return "¿En qué te puedo ayudar?" if lang == "es" else "How can I help you?"
    try:
        system = SYSTEM_PROMPT_ES if lang == "es" else SYSTEM_PROMPT_EN
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": AI_MODEL,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user_input}
                ],
                "max_tokens": 80,
                "temperature": 0.4
            },
            timeout=10
        )
        data = res.json()
        print(f"[Groq] status={res.status_code}")
        if "error" in data:
            print(f"[Groq] ERROR: {data['error'].get('message')}")
            return "¿En qué te puedo ayudar?" if lang == "es" else "How can I help you?"
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        traceback.print_exc()
        return "¿En qué te puedo ayudar?" if lang == "es" else "How can I help you?"

# ─── Función principal de la mente ───────────────────────────────────────────
def think(user_input: str, session: dict, lang: str = "es"):
    from product_search import get_section, format_product_info
    from session import update_session

    text      = user_input.lower().strip()
    state     = session.get("state", "greeting")
    category  = session.get("pending_category", None)
    map_cmd   = None

    # ── ESTADO: esperando confirmación para navegar ───────────────────────
    if state == "confirm_navigate":
        if any(a in text for a in AFFIRMATIVES):
            # Navegar al producto pendiente
            pid     = session.get("pending_pid")
            product = None
            if pid:
                from product_search import load_products
                product = next((p for p in load_products()["products"] if p["id"] == pid), None)

            if product:
                sec     = get_section(product["section_id"])
                map_cmd = {
                    "accion":       "navegar",
                    "producto_id":  pid,
                    "coords":       product["map_coords"],
                    "section":      sec["name"] if sec else "",
                    "product_info": format_product_info(product)
                }
                msg = f"¡Perfecto! Te guío ahora. 🗺️" if lang == "es" else "Perfect! Guiding you now. 🗺️"
                session["state"] = "navigating"
                session = update_session(session, user_input, product)
                return msg, map_cmd, session
        else:
            msg = "¡Entendido! Si necesitas ayuda con otro producto, con gusto te asisto. 😊" if lang == "es" else "Got it! If you need help with another product, I'm here to assist. 😊"
            session["state"] = "greeting"
            session["pending_category"] = None
            session["pending_pid"] = None
            session = update_session(session, user_input)
            return msg, None, session

    # ── ESTADO: esperando marca ───────────────────────────────────────────
    if state == "waiting_brand" and category:
        brand = detect_brand(text, category)
        cat_data = CATALOG.get(category, {})
        marcas_disponibles = cat_data.get("marcas", [])
        nombre_cat = cat_data.get("nombre", category)

        if brand:
            # Marca encontrada en catálogo
            product = get_product_by_brand(category, brand)
            if product:
                if lang == "es":
                    msg = f"¡Encontré el {product['name']}! ¿Te guío hacia él? 😊"
                else:
                    msg = f"Found the {product['name']}! Shall I guide you there? 😊"
                session["state"]        = "confirm_navigate"
                session["pending_pid"]  = product["id"]
                session = update_session(session, user_input)
                return msg, None, session
        else:
            # Marca no encontrada — ver si dijeron algo desconocido
            # Verificar si mencionaron una marca que no tenemos
            palabras = text.split()
            marca_mencionada = None
            marcas_conocidas_generales = ["bosch", "makita", "stanley", "black", "decker", "milwaukee", "ryobi", "hitachi", "hilti"]
            for p in palabras:
                if p in marcas_conocidas_generales or (len(p) > 3 and p not in ["para", "quiero", "busco", "tengo", "necesito"]):
                    marca_mencionada = p
                    break

            marcas_str = ", ".join([m.capitalize() for m in marcas_disponibles])
            if lang == "es":
                msg = f"Lo siento, no tenemos esa marca. Solo disponemos de: {marcas_str}.\n¿Te guío a alguna de ellas?"
            else:
                msg = f"Sorry, we don't carry that brand. We only have: {marcas_str}.\nShall I guide you to one of them?"

            # Usar primer producto de la categoría como destino
            products_cat = get_products_by_category(category)
            if products_cat:
                session["state"]       = "confirm_navigate"
                session["pending_pid"] = products_cat[0]["id"]
            session = update_session(session, user_input)
            return msg, None, session

    # ── DETECCIÓN DE CATEGORÍA (estado normal) ────────────────────────────
    detected_cat = detect_category(text)

    if detected_cat:
        cat_data = CATALOG.get(detected_cat, {})
        marcas   = cat_data.get("marcas", [])
        nombre   = cat_data.get("nombre", detected_cat)
        marcas_str = ", ".join([m.capitalize() for m in marcas])

        session["state"]            = "waiting_brand"
        session["pending_category"] = detected_cat
        session = update_session(session, user_input)

        if lang == "es":
            msg = f"¡Claro! Tenemos {nombre}. ¿De qué marca lo estás buscando?\nDisponemos de: {marcas_str}."
        else:
            msg = f"Sure! We have {nombre}. What brand are you looking for?\nWe carry: {marcas_str}."
        return msg, None, session

    # ── Sin detección → IA responde ───────────────────────────────────────
    session["state"] = "greeting"
    session = update_session(session, user_input)
    msg = call_ai(user_input, lang)
    return msg, None, session