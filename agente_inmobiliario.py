import os
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import errors

# Cargar variables desde un archivo .env en desarrollo/local
load_dotenv()

# Leemos la clave del entorno del servidor e inicializamos el cliente pasándosela directamente
api_key_gemini = os.environ.get("GEMINI_API_KEY")
serper_api_key = os.environ.get("SERPER_API_KEY")

client = genai.Client(api_key=api_key_gemini) # <--- Ahora le pasamos la clave de forma explícita
# 2. HERRAMIENTA DE BÚSQUEDA
def buscar_en_google(query: str) -> str:
    url = "https://google.serper.dev/search"
    payload = {"q": query, "gl": "ar", "hl": "es"}
    headers = {'X-API-KEY': serper_api_key, 'Content-Type': 'application/json'}
    response = requests.post(url, json=payload, headers=headers)
    
    resultados = response.json().get('organic', [])
    lineas = []
    for r in resultados[:7]: # Subimos a 7 resultados para tener más opciones
        lineas.append(f"Título: {r.get('title')}\nLink: {r.get('link')}\nDescripción: {r.get('snippet')}\n---")
    return "\n".join(lineas)


# DISEÑO VISUAL: Le ordenamos al agente estructurar todo en una tabla Markdown limpia
instrucciones_html = (
    "Sos un Analista Inmobiliario experto en La Plata.\n\n"
    "Tu objetivo es armar una tabla HTML (<tr>) con un máximo de 5 propiedades individuales "
    "que funcionen como oportunidades (idealmente abajo de U$S 60.000, urgencias, o a refaccionar).\n\n"
    "REGLA DE ENLACES (ACTUALIZADA):\n"
    "Sabemos que la herramienta 'buscar_en_google' suele devolver links a listados de grandes portales "
    "(Zonaprop, MercadoLibre, Argenprop, Remax, etc.). EN LUGAR DE RECHAZARLOS, hacé lo siguiente:\n"
    "1. Leé los fragmentos de texto (snippets) que acompañan a esos links en la búsqueda.\n"
    "2. Si el fragmento describe una casa o terreno específico con su precio (ej: 'Casa en Los Hornos U$S 45.000...'), "
    "TOMÁ ese resultado como válido.\n"
    "3. Usá el link que te provee la herramienta (aunque sea el del listado filtrado del portal) para la celda de enlace. "
    "Es preferible que el usuario llegue al listado filtrado de esa zona antes que dejar la tabla vacía.\n\n"
    "FORMATO DE CELDAS:\n"
    "- Celda 1 (Título): Descripción de la casa/lote del fragmento (ej: 'Casa a refaccionar en Los Hornos').\n"
    "- Celda 2 (Ubicación/Precio): Zona y precio estimado/exacto según el texto leído.\n"
    "- Celda 3 (Justificación): Por qué destaca (ej: 'Excelente precio para la zona, ideal inversión').\n"
    "- Celda 4 (Link): <a class='btn-link' href='LINK_PROVISTO' target='_blank'>Ver Zona/Publicación</a>."
)

orden_usuario = (
    "Realizá múltiples búsquedas en La Plata usando términos como: "
    "'remate dueño directo casas en venta La Plata', 'oportunidad urgente departamento La Plata', "
    "'casa a refaccionar barata La Plata'. "
    "Analizá a fondo los resultados encontrados, descartá los precios inflados y armá la tabla "
    "Que no supere por mucho los 60000 dólares"
    "solo con las mejores 5 oportunidades reales del mercado actual."
)

print("🤖 El agente está analizando el mercado y armando el reporte visual...")

try:

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=orden_usuario,
        config={
            "system_instruction": instrucciones_html,
            "tools": [buscar_en_google]
        }
    )
    filas_html = response.text

except errors.ClientError as e:
    filas_html = (
            "<tr><td colspan='4' style='text-align: center; padding: 30px; color: #721c24; background-color: #f8d7da; font-weight: bold;'>"
            "🛑 LÍMITE DE CUOTA ALCANZADO: El agente inmobiliario no pudo consultar a Gemini porque se agotaron los créditos gratuitos "
            "diarios. El reporte se actualizará automáticamente mañana a las 08:00 AM."
            "</td></tr>"
        )
    

# 2. PLANTILLA HTML CON ESTILOS PROFESIONALES
# Aquí definimos el diseño visual (colores, fuentes, bordes)
plantilla_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Reporte Inmobiliario Automatizado</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            color: #1e293b;
            background-color: #f8fafc;
            margin: 0; padding: 30px;
            line-height: 1.6;
        }}
        .header {{
            background-color: #1e3a8a;
            color: white;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 25px;
        }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .header p {{ margin: 5px 0 0 0; color: #bfdbfe; }}
        h2 {{ color: #1e3a8a; border-left: 5px solid #3b82f6; padding-left: 10px; margin-top: 30px; }}
        table {{
            width: 100%; border-collapse: collapse; margin-top: 15px;
            background: white; border-radius: 8px; overflow: hidden;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
        th {{ background-color: #3b82f6; color: white; font-weight: bold; }}
        tr:nth-child(even) {{ background-color: #f1f5f9; }}
        .btn-link {{
            display: inline-block; padding: 6px 12px; background-color: #2563eb;
            color: white !important; text-decoration: none; border-radius: 4px;
            font-size: 13px; font-weight: bold;
        }}
        .btn-link:hover {{ background-color: #1d4ed8; }}
        .analysis-box {{
            background-color: #eff6ff; border-left: 4px solid #2563eb;
            padding: 20px; border-radius: 0 8px 8px 0; margin-top: 15px;
        }}
        .tag-oportunidad {{
            background-color: #dcfce7; color: #15803d;
            padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;
        }}
    </style>
</head>
<body>

    <div class="header">
        <h1>📍 Reporte de Oportunidades Inmobiliarias</h1>
        <p>Agente de Inteligencia Artificial - Datos en Tiempo Real</p>
    </div>

    <h2>🏠 Propiedades y Terrenos Detectados</h2>
    <table>
        <thead>
            <tr>
                <th>Propiedad / Título</th>
                <th>Ubicación Aproximada</th>
                <th>Destacado / Oportunidad</th>
                <th>Enlace Directo</th>
            </tr>
        </thead>
        <tbody>
            {filas_html}
        </tbody>
    </table>

</body>
</html>
"""

# 3. GUARDAR EL ARCHIVO HTML
nombre_archivo = "index.html"
with open(nombre_archivo, "w", encoding="utf-8") as f:
    f.write(plantilla_html)

print(f"\n✅ ¡Página web generada con éxito!")
print(f"📂 Buscá el archivo '{nombre_archivo}' en tu carpeta y hacéle doble clic para abrirlo en tu navegador.")