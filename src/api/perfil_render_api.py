import logging
import requests
from flask import Blueprint, render_template, jsonify
from src.models.plantilla_personalizada import PlantillaPersonalizada
from src.models.database import db

# Configuración básica del logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

perfil_render_bp = Blueprint("perfil_render_api", __name__, url_prefix="/perfil/render")

@perfil_render_bp.route("/<int:id_usuario>")
def renderizar_perfil(id_usuario):
    logger.info(f"⏳ Intentando renderizar perfil para usuario {id_usuario}")
    
    ia_triggered = False # Flag to indicate if AI generation was triggered in this request

    try:
        # Consulta directa a la base de datos
        plantilla = PlantillaPersonalizada.query.filter_by(id_usuario=id_usuario).first()
        logger.info(f"🔍 Consulta de plantilla para usuario {id_usuario}: {'Encontrada' if plantilla else 'No encontrada'}")

        if not plantilla:
            logger.error(f"❌ Perfil del usuario {id_usuario} no encontrado (404)")
            return jsonify({"error": "Perfil no encontrado"}), 404

        # Verificar si hay contenido editado para disparar la generación de HTML
        logger.info(f"✨ Verificando contenido_editado para usuario {id_usuario}...")
        if plantilla.contenido_editado:
            logger.info(f"➡️ Contenido editado encontrado. Disparando generación de HTML para usuario {id_usuario} a /api/plantillas/editar/{id_usuario}")
            generate_html_url = f"http://127.0.0.1:5000/api/plantillas/editar/{id_usuario}"
            ia_triggered = True # Set flag
            try:
                # Making a POST request to trigger the IA process. Adjust to GET if that's what the endpoint expects.
                requests.post(generate_html_url, timeout=1) # Use a short timeout as we don't need to wait for the response
                logger.info("POST a /api/plantillas/editar/ completado (disparo asíncrono).")
            except requests.exceptions.RequestException as ia_req_err:
                # Log the error but don't fail the render request
                logger.error(f"❌ Error al disparar la generación de HTML para usuario {id_usuario}: {ia_req_err}")

        # Prepare data for JSON response
        datos_respuesta = {
            "id": plantilla.id,
            "id_usuario": plantilla.id_usuario,
            "nombre_plantilla": plantilla.nombre_plantilla,
            "html_generado": plantilla.html_generado,
            "contenido_editado": plantilla.contenido_editado,
            "url_preview": plantilla.url_preview,
            "url_final": plantilla.url_final,
            # Add other relevant fields as needed
            # "metadatos": plantilla.metadatos,
            # "informacion_contacto": plantilla.informacion_contacto,
        }

        # Add flag if AI was triggered in this request
        if ia_triggered:
            datos_respuesta["generando_html"] = True
            logger.info(f"✅ Respondiendo con datos JSON para usuario {id_usuario}. IA disparada.")
        else:
             logger.info(f"✅ Respondiendo con datos JSON para usuario {id_usuario}. IA no disparada.")

        return jsonify(datos_respuesta), 200

    except requests.exceptions.ConnectionError as conn_err:
        logger.error(f"❌ Error de conexión a la base de datos u otro recurso: {conn_err}")
        return jsonify({"error": "Error de conexión interno"}), 500

    except requests.exceptions.Timeout as timeout_err:
        logger.error(f"⏳ La solicitud interna excedió el tiempo límite: {timeout_err}")
        return jsonify({"error": "Tiempo de espera excedido"}), 500

    except requests.exceptions.RequestException as req_err:
        logger.error(f"❌ Error general al obtener perfil para usuario {id_usuario}: {req_err}")
        return jsonify({"error": "Error al obtener el perfil"}), 500
