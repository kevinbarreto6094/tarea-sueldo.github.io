# SmartFix.guía — IA de navegación para Promart

## Estructura del proyecto

```
smartfix/
├── smartfix_server.py   ← SERVIDOR PRINCIPAL (ejecutar primero)
├── brain.py             ← La mente: orquesta IA + búsqueda + mapa
├── product_search.py    ← Motor de búsqueda de productos
├── session.py           ← Memoria de sesión del cliente
├── products.json        ← Base de datos de productos Promart
├── map_connector.py     ← Para los compañeros del mapa 3D (Blender)
└── test_client.py       ← Prueba la IA desde la terminal
```

## Cómo ejecutar

### 1. Instalar dependencias
```bash
pip install websockets requests
```

### 2. Configurar la IA
Abre `brain.py` y elige tu proveedor:
```python
AI_PROVIDER = "ollama"    # Si tienes Ollama instalado (gratis, local)
AI_PROVIDER = "openai"    # Si tienes API Key de OpenAI
AI_PROVIDER = "claude"    # Si tienes API Key de Claude (Anthropic)
```

### 3. Arrancar el servidor
```bash
python smartfix_server.py
```

### 4. Probar con el cliente de terminal
```bash
python test_client.py
```

### 5. Conectar el mapa 3D (compañeros)
Ver instrucciones detalladas en `map_connector.py`.

## Protocolo WebSocket

| Dirección          | Tipo mensaje     | Contenido                                    |
|--------------------|------------------|----------------------------------------------|
| Cliente → Servidor | `client_connect` | Identificación inicial                       |
| Cliente → Servidor | `message`        | `{"type": "message", "text": "busco focos"}` |
| Servidor → Cliente | `response`       | Respuesta de texto de la IA                  |
| Servidor → Cliente | `product_info`   | Datos del producto encontrado                |
| Servidor → Mapa    | `navigate`       | Coordenadas 3D + ID del producto             |
| Mapa → Servidor    | `map_connect`    | Identificación del mapa                      |

## Agregar productos
Edita `products.json` y agrega entradas siguiendo el mismo formato.
Las coordenadas `map_coords` deben coincidir con las del mapa 3D de Blender.

## Próximos pasos
- [ ] Conectar con el mapa 3D real de los compañeros
- [ ] Agregar todos los productos de Promart
- [ ] Crear interfaz web (el cuarto compañero)
- [ ] Agregar reconocimiento de voz (hablar en lugar de escribir)
- [ ] Panel de administración para agregar/editar productos
