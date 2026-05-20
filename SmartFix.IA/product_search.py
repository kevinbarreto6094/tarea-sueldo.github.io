import json
import os

# ─── Cargar base de datos ───────────────────────────────────────────────────
def load_products():
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, "products.json"), "r", encoding="utf-8") as f:
        return json.load(f)

# ─── Buscar producto por texto libre ────────────────────────────────────────
def search_product(user_query: str) -> list[dict]:
    """
    Devuelve lista de productos que coinciden con la búsqueda.
    Ordena por relevancia (más coincidencias de keywords primero).
    """
    data = load_products()
    query_words = user_query.lower().split()
    results = []

    for product in data["products"]:
        score = 0
        keywords = product["keywords"]
        name_words = product["name"].lower().split()

        for word in query_words:
            # Coincidencia en keywords
            if any(word in kw for kw in keywords):
                score += 2
            # Coincidencia en nombre
            if any(word in nw for nw in name_words):
                score += 3

        if score > 0:
            results.append({"product": product, "score": score})

    # Ordenar por relevancia
    results.sort(key=lambda x: x["score"], reverse=True)
    return [r["product"] for r in results[:3]]  # Top 3 resultados

# ─── Obtener sección de un producto ─────────────────────────────────────────
def get_section(section_id: str) -> dict | None:
    data = load_products()
    for section in data["sections"]:
        if section["id"] == section_id:
            return section
    return None

# ─── Formatear producto para mostrar al cliente ──────────────────────────────
def format_product_info(product: dict) -> str:
    section = get_section(product["section_id"])
    section_name = section["name"] if section else "Sección desconocida"

    return (
        f"Producto: {product['name']}\n"
        f"Marca: {product['brand']}\n"
        f"Precio: S/ {product['price']:.2f}\n"
        f"Sección: {section_name}\n"
        f"Pasillo: {product['aisle']}, Estante: {product['shelf']}\n"
        f"Stock disponible: {product['stock']} unidades\n"
        f"Descripción: {product['description']}"
    )
