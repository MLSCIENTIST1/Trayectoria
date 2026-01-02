import logging
import json
from flask import Blueprint, request, jsonify
from src.models.database import db
from src.models.plantilla_personalizada import PlantillaPersonalizada
from src.models.usuarios import Usuario  # 📌 Se agregó si necesitas validar usuario
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

formulario_bp = Blueprint("formulario_api", __name__, url_prefix="/formulario")

@formulario_bp.route("/guardar_todo_en_editado/<int:id_usuario>", methods=["POST"])
def guardar_todo_en_editado(id_usuario):
    logger.info(f"📝 Recibiendo datos de formulario para usuario {id_usuario}...")

    try:
        datos_formulario = request.get_json()
        if not datos_formulario:
            logger.error("❌ No se recibieron datos JSON válidos en la solicitud.")
            return jsonify({"error": "No se recibieron datos JSON válidos"}), 400
    except Exception as e:
        logger.error(f"⚠ Error al parsear datos JSON: {e}")
        return jsonify({"error": "Formato JSON inválido"}), 400

    # ✅ Opcional: Verificar si el usuario existe
    usuario = Usuario.query.get(id_usuario)
    if not usuario:
        logger.error(f"⚠ Usuario con ID {id_usuario} no encontrado.")
        return jsonify({"error": f"Usuario con ID {id_usuario} no encontrado"}), 404

    try:
        plantilla = PlantillaPersonalizada.query.filter_by(id_usuario=id_usuario).first()
        datos_formulario_str = json.dumps(datos_formulario, indent=2)

        if plantilla:
            logger.info(f"🔄 Plantilla existente encontrada para usuario {id_usuario}. Actualizando contenido_editado.")
            plantilla.contenido_editado = datos_formulario_str
        else:
            logger.info(f"➕ No se encontró plantilla para usuario {id_usuario}. Creando una nueva...")
            nueva_plantilla = PlantillaPersonalizada(
                id_usuario=id_usuario,
                nombre_plantilla=datos_formulario.get('nombre_plantilla', 'DefaultTemplate'),
                contenido_editado=datos_formulario_str,
                url_preview=datos_formulario.get('url_preview', f'/preview/{id_usuario}'),
                url_final=datos_formulario.get('url_final', f'/final/{id_usuario}')
            )
            db.session.add(nueva_plantilla)

        db.session.commit()
        logger.info(f"✅ Datos del formulario guardados correctamente en contenido_editado para usuario {id_usuario}.")
        return jsonify({"mensaje": "Datos del formulario guardados en contenido_editado"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"❌ Error SQL al guardar datos en la base de datos para usuario {id_usuario}: {e}")
        return jsonify({"error": "Error interno al guardar los datos"}), 500

    except Exception as e:
        db.session.rollback()
        logger.error(f"⚠ Error inesperado al guardar datos para usuario {id_usuario}: {e}")
        return jsonify({"error": "Error interno al guardar los datos"}), 500
