import logging
from flask import Blueprint, jsonify, request
from flask_login import current_user
from src.models.servicio import Servicio

# Configurar logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Crear Blueprint para la funcionalidad de calificación
calificar_bp = Blueprint('calificar_bp', __name__)

@calificar_bp.route('/calificar/<int:servicio_id>', methods=['GET'])
def get_calificar(servicio_id):
    """
    Endpoint para obtener la información de un contrato asociado a un servicio,
    validando que el usuario autenticado tenga acceso al contrato. Devuelve los 
    detalles del contrato en formato JSON.
    """
    logger.info(f"Procesando solicitud GET para calificar el servicio con ID: {servicio_id}")

    try:
        # Obtener el contrato específico basado en el servicio_id
        contrato = Servicio.query.get_or_404(servicio_id)
        logger.debug(f"Contrato obtenido: {contrato}")

        # Validar que el usuario esté relacionado con el contrato
        if contrato.id_contratante != current_user.id_usuario and contrato.id_contratado != current_user.id_usuario:
            logger.warning(f"Acceso denegado para el usuario {current_user.id_usuario} al contrato {servicio_id}.")
            return jsonify({"error": "No tienes acceso a este contrato."}), 403

        # Log de éxito
        logger.debug(f"Contrato cargado correctamente: ID Servicio {contrato.id_servicio}, Contratante {contrato.id_contratante}, Contratado {contrato.id_contratado}")

        # Responder con los detalles del contrato
        return jsonify({
            "id_servicio": contrato.id_servicio,
            "id_contratante": contrato.id_contratante,
            "id_contratado": contrato.id_contratado,
            "estado": contrato.estado
        }), 200

    except Exception as e:
        logger.exception("Error al procesar la solicitud para obtener información del contrato.")
        return jsonify({"error": "Hubo un problema al cargar el contrato."}), 500