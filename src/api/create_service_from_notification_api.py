import logging
from datetime import datetime
from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from src.models.notification import Notification
from src.models.servicio import Servicio
from src.models.database import db

# Configurar logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Crear Blueprint para la funcionalidad de creación de servicios desde notificaciones
create_service_bp = Blueprint('create_service_bp', __name__)

@create_service_bp.route('/notification/<int:notification_id>/create_service', methods=['POST'])
@login_required
def create_service_from_notification_api(notification_id):
    """
    API para crear un servicio a partir de una notificación específica.
    Valida la existencia de la notificación y del remitente, y guarda el servicio en la base de datos.
    """
    logger.info(f"Procesando solicitud POST para crear un servicio desde la notificación {notification_id}.")

    try:
        # Obtener la notificación
        notification = Notification.query.get_or_404(notification_id)
        logger.debug(f"Notificación obtenida: ID: {notification.id}, Receptor (user_id): {notification.user_id}, Remitente (sender_id): {notification.sender_id}")

        # Verificar existencia del remitente
        sender = db.session.query(current_user.__class__).get(notification.sender_id)
        if not sender:
            logger.error(f"No se encontró el remitente con ID {notification.sender_id}.")
            return jsonify({"error": f"No se encontró el remitente con ID {notification.sender_id}."}), 404
        logger.debug(f"Remitente obtenido: {sender}")

        # Crear el servicio
        servicio = Servicio(
            nombre_servicio=notification.message,
            fecha_solicitud=notification.timestamp.date(),
            fecha_aceptacion=datetime.utcnow().date(),
            fecha_inicio=datetime.utcnow().date(),
            fecha_fin=(datetime.utcnow().replace(year=datetime.utcnow().year + 1)).date(),
            nombre_contratante=sender.nombre,  # Usando el nombre del remitente
            id_contratante=sender.id_usuario,
            id_usuario=current_user.id_usuario
        )
        logger.debug(f"Servicio preparado para guardar: {servicio}")

        # Guardar el servicio en la base de datos
        db.session.add(servicio)
        db.session.commit()
        logger.info(f"Servicio creado con éxito: {servicio}")

        # Devolver respuesta exitosa
        return jsonify({"message": "Servicio creado exitosamente.", "servicio_id": servicio.id_servicio}), 200

    except Exception as e:
        logger.exception(f"Error al crear el servicio desde la notificación {notification_id}.")
        db.session.rollback()
        return jsonify({"error": "Hubo un problema al crear el servicio."}), 500
