import logging
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# 🔥 Cargar variables de entorno
load_dotenv('gemini1.env')

# 🔗 Configurar la API Key de Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("❌ GEMINI_API_KEY no configurada en las variables de entorno.")
else:
    genai.configure(api_key=GEMINI_API_KEY)

# 📌 Diccionario de rutas según `nombre_plantilla`
TEMPLATES_PATHS = {
    "Herbal": "src/templates/Herbal/index.html",
    "Pleeness": "src/templates/Pleenessi/index.html", # Assuming Pleeness maps to Pleenessi folder
    "sb_Landing_page": "src/templates/sb_Landing_page/index.html",
    "start_level": "src/templates/public_html/index.html"
}

def generar_html_con_gemini(nombre_plantilla, datos_usuario):
    """
    Genera HTML y extrae datos de contenido_editado usando un modelo Gemini.
    """
    if not GEMINI_API_KEY:
        logger.error("❌ API Key de Gemini no disponible. No se puede generar HTML.")
        return None

    logger.info(f"🧠 Procesando con Gemini para plantilla: {nombre_plantilla}")

    template_path = TEMPLATES_PATHS.get(nombre_plantilla)
    
    if not template_path or not os.path.exists(template_path):
        logger.error(f"❌ No se encontró el archivo HTML base en la ruta esperada: {template_path}")
        return None

    logger.info(f"📂 Leyendo contenido de {template_path}")
    try:
        with open(template_path, "r", encoding="utf-8") as file:
            html_base_content = file.read()
        logger.info("✅ Archivo HTML base leído correctamente.")
    except Exception as e:
        logger.error(f"⚠ Error al leer el archivo HTML base: {e}")
        return None

    edited_content = datos_usuario.get("contenido_editado", "")
    if not edited_content:
        logger.warning("⚠️ No se encontró 'contenido_editado' en datos_usuario. Solo se generará HTML base con datos existentes.")
        # Aquí podrías decidir si generar HTML solo con los datos existentes o retornar None
        # Por ahora, continuamos para generar HTML base si no hay edited_content

    prompt = f"""
Analiza cuidadosamente el siguiente objeto JSON, que contiene todos los datos proporcionados por el usuario a través de un formulario:
    ---
    {edited_content}
    ---

Tu tarea es doble:

1.  **Extracción de Datos Estructurados:** Extrae la siguiente información clave de este JSON y formatéala como un nuevo objeto JSON con las claves especificadas. Si un dato no se encuentra o está vacío en el JSON de entrada, usa una cadena vacía "" (para strings) o un array vacío [] (para listas/arrays).

    *   **keywords:** Palabras clave relevantes basadas en el contenido proporcionado (de campos como `businessDescription`, `aboutYouDescription`, etc.). Formato: array de strings.
    *   **description:** Una descripción concisa para meta tags (de campos como `businessDescription`, `aboutYouDescription`). Formato: string.
    *   **author:** El nombre completo del usuario (`fullName`). Formato: string.
    *   **title:** Un título sugerido para la página (puede basarse en `company_name`, `profession`, `fullName`). Formato: string.
    *   **company_name:** El nombre de la compañía (`company_name`). Formato: string.
    *   **testimonials_data:** Un array de objetos con claves `name` y `text` (tomar directamente del array `testimonials` si existe). Formato: array de objetos.
    *   **contact_email:** El email de contacto (`email`). Formato: string.

    Envuelve este objeto JSON extraído entre las etiquetas <extracted_data> y </extracted_data>.

2.  **Generación de Contenido HTML:** Utilizando **todos** los datos proporcionados en el JSON anterior y el siguiente HTML base, modifica y personaliza el HTML base para reflejar la información del usuario.

    HTML Base:
    HTML Base:
    ---
    {html_base_content}
    ---

    Genera el HTML final con el contenido modificado. Asegúrate de que el HTML generado sea completo y válido.
    Asegúrate de:
    *   Rellenar los meta tags (title, description, keywords, author) con los datos extraídos.
    *   Insertar dinámicamente textos (nombres, descripciones, títulos de secciones, textos de botones) y URLs (enlaces sociales, enlaces de navegación, enlaces de contacto) del JSON en los lugares apropiados del HTML.
    *   Integrar el contenido de texto libre (como `businessDescription`, `aboutYouDescription`, descripciones de servicios) en las secciones relevantes del HTML.
    *   Formatear y mostrar correctamente el array de testimonios (`testimonials`) en la sección designada.
    *   Adaptar cualquier otra sección del HTML base basándote en los datos del JSON.
    *   **Mantener la estructura general del HTML base.** No elimines secciones principales a menos que los datos indiquen que una sección está vacía e irrelevante. No añadas nuevas secciones principales.
    *   El HTML generado debe ser un documento completo y válido.

    Envuelve el HTML generado entre las etiquetas <generated_html> y </generated_html>.

Tu respuesta debe contener *solamente* el bloque <extracted_data>...</extracted_data> seguido inmediatamente por el bloque <generated_html>...</generated_html>. No incluyas texto adicional fuera de estas etiquetas.

    <extracted_data>
    {{
 "keywords": [...],
      "description": "...",
      "author": "...",
      "title": "...",
      "company_name": "..."
    }}
    </extracted_data>
    <!-- HTML generado -->
    """

    logger.info("🚀 Enviando prompt a Gemini para procesar...")
    try:
        # Lógica para llamar a la API de Gemini
        model = genai.GenerativeModel("gemini-1.5-flash-latest") # Usando un modelo más rápido
        response = model.generate_content(prompt)
        response_text = response.text
        logger.info("✅ Respuesta de Gemini recibida.")

        # 📌 Parsear la respuesta para extraer JSON y HTML
        extracted_data = {}
        generated_html = ""

        # Find the start and end of the JSON and HTML blocks
        json_start = response_text.find("<extracted_data>")
        json_end = response_text.find("</extracted_data>")
        html_start = response_text.find("<generated_html>")
        html_end = response_text.find("</generated_html>")

        # 📌 Parsear la respuesta para extraer JSON y HTML

        # Check if JSON tags are found
        if json_start != -1 and json_end != -1 and json_end > json_start:
            # Extract and parse JSON
            json_string = response_text[json_start + len("<extracted_data>"):json_end].strip()
            try:
                extracted_data = json.loads(json_string)
                logger.info("✅ Datos extraídos (JSON) parseados exitosamente.")
            except json.JSONDecodeError as e:
                logger.error(f"❌ Error al parsear el JSON dentro de <extracted_data>: {e}")
                extracted_data = {} # Reiniciar si el parseo JSON falló

        # Check if HTML tags are found
        if html_start != -1 and html_end != -1 and html_end > html_start:
            # Extract HTML
            generated_html = response_text[html_start + len("<generated_html>"):html_end].strip()
            logger.info("✅ HTML generado extraído exitosamente.")

        # Handle cases where one or both tags are missing
        # If no tags were found at all, assume the whole response is HTML
        if not extracted_data and not generated_html:
             # Case 4: No tags found, assume whole response is HTML
             logger.warning("⚠ No se encontraron las etiquetas esperadas (<extracted_data>, <generated_html>). Asumiendo que toda la respuesta es HTML generado.")
             generated_html = response_text.strip()
             extracted_data = {} # Ensure extracted_data is empty
        # If only HTML tags were found (JSON missing or parse failed)
        elif not extracted_data and generated_html:
             # Case 3: Only HTML tags found (JSON missing or parse failed)
            logger.warning("⚠ No se encontraron las etiquetas <extracted_data> en la respuesta de Gemini. Asumiendo que toda la respuesta es HTML generado.")
        # If only JSON tags were found (HTML missing)
        elif extracted_data and not generated_html:
             # Case 2: Only JSON tags found (HTML missing)
             logger.warning("⚠ No se encontraron las etiquetas <generated_html> en la respuesta de Gemini.")

        # Final check before returning
        if not generated_html:
            logger.error("❌ Gemini no devolvió HTML generado válido.")
            return None

        return {"extracted_data": extracted_data, "generated_html": generated_html}

    except Exception as e:
        # Este except ahora está correctamente asociado al try de la API call
        logger.error(f"❌ Error general al interactuar con Gemini: {e}")
        return None