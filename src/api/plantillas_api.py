import logging
import requests
from flask import Blueprint, request, jsonify
from src.models.plantilla_personalizada import PlantillaPersonalizada
import os
from src.utils.ia_processor import generar_html_con_gemini  
from src.models.database import db

# 📌 Configurar logger
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

plantillas_bp = Blueprint("plantillas_api", __name__, url_prefix="/plantillas")

@plantillas_bp.route("/editar/<int:id_usuario>", methods=["POST"])
def editar_plantilla(id_usuario):
    logger.info(f"🧠 Iniciando edición de plantilla para usuario {id_usuario}...")

    plantilla = PlantillaPersonalizada.query.filter_by(id_usuario=id_usuario).first()

    if not plantilla:
        logger.error(f"❌ No se encontró la plantilla asociada al usuario {id_usuario}.")
        return jsonify({"error": "No se encontró la plantilla para este usuario"}), 404

    # 📌 Si `contenido_editado` tiene datos, disparar generación de HTML con IA
    if plantilla.contenido_editado:
        logger.info(f"🔍 Contenido editado detectado para usuario {id_usuario}. Comenzando generación de HTML con IA...")

        # 📌 Diccionario de rutas según `nombre_plantilla`
        template_paths = {
            "Herbal": "src/templates/Herbal/index.html",
            "Pleeness": "src/templates/Pleenessi/index.html",
            "sb_Landing_page": "src/templates/sb_Landing_page/index.html",
            "start_level": "src/templates/public_html/index.html"
        }

        template_path = template_paths.get(plantilla.nombre_plantilla)

        if not template_path or not os.path.exists(template_path):
            logger.error(f"❌ No se encontró la plantilla base para {plantilla.nombre_plantilla}. Ruta: {template_path}")
            return jsonify({"error": f"Plantilla base no encontrada para {plantilla.nombre_plantilla}"}), 500

        logger.info(f"📂 Leyendo contenido base de la plantilla desde {template_path}...")
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                base_html_content = f.read()
            logger.info("✅ Archivo HTML base leído correctamente.")
        except Exception as e:
            logger.error(f"⚠ Error al leer el archivo HTML: {e}")
            return jsonify({"error": "No se pudo leer el archivo HTML"}), 500

        # 📌 Generación de HTML con IA
        logger.info(f"🚀 Enviando contenido a Gemini para modificar el HTML...")
        resultado_ia = generar_html_con_gemini(plantilla.nombre_plantilla, {"contenido_editado": plantilla.contenido_editado})

        if resultado_ia and resultado_ia.get("generated_html"):
            logger.info("✅ HTML generado exitosamente con Gemini.")
            
            extracted_data = resultado_ia.get("extracted_data", {})

            # 📌 Manejo especial de palabras clave
            keywords_data = extracted_data.get("keywords")
            if isinstance(keywords_data, list):
                plantilla.keywords = ", ".join(keywords_data)
            elif isinstance(keywords_data, str):
                plantilla.keywords = keywords_data
            else:
                plantilla.keywords = ""  # Default si no es lista o string

            plantilla.description = extracted_data.get("description", "")
            plantilla.full_name = extracted_data.get("author", "")  # Mapea `author` a `full_name`
            plantilla.title = extracted_data.get("title", "")
            plantilla.company_name = extracted_data.get("company_name", "")
            plantilla.testimonials = extracted_data.get("testimonials_data", [])  # Testimonials en JSON
            plantilla.email = extracted_data.get("contact_email", "")  # Mapea `contact_email` a `email`
            plantilla.html_generado = resultado_ia.get("generated_html")

            logger.info(f"✅ Datos actualizados correctamente en la BD para usuario {id_usuario}.")
        else:
            logger.error("❌ La IA no generó el HTML o datos correctamente.")
            return jsonify({"error": "Error al procesar el contenido editado con IA"}), 500

        # 📌 Limpiar `contenido_editado` después de procesarlo
        plantilla.contenido_editado = None
        db.session.commit()
        logger.info(f"🗑 `contenido_editado` limpiado después de la generación de HTML para usuario {id_usuario}.")
        return jsonify({"mensaje": "HTML generado exitosamente con IA"}), 200

    logger.warning(f"⚠ No hay contenido editado pendiente de actualización para usuario {id_usuario}.")
    return jsonify({"mensaje": "No hay contenido editado pendiente de actualización."}), 400
