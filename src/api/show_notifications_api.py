import logging
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from src.models.notification import Notification
from src.models.database import db

# Configurar logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Crear Blueprint para mostrar notificaciones
show_notifications_bp = Blueprint('show_notifications_bp', __name__)

@show_notifications_bp.route('/notifications', methods=['GET', 'POST'])
@login_required
def show_notifications_api():
    """
    API para mostrar notificaciones asociadas al usuario autenticado.
    En el método GET, devuelve las notificaciones en formato JSON.
    En el método POST, confirma la recepción de la solicitud.
    """
    logger.info(f"Procesando solicitud {request.method} para mostrar notificaciones.")

    if request.method == 'POST':
        logger.debug("Solicitud POST recibida. Respondiendo con confirmación.")
        return jsonify({"message": "Solicitud POST recibida."}), 200

    try:
        # Obtener notificaciones donde el usuario es receptor o remitente
        notifications = Notification.query.filter(
            (Notification.user_id == current_user.id_usuario) |  # Receptor
            (Notification.sender_id == current_user.id_usuario)  # Remitente
        ).order_by(Notification.timestamp.desc()).all()
        logger.debug(f"Notificaciones obtenidas para el usuario {current_user.id_usuario}: {[n.id for n in notifications]}")

        # Marcar como leídas las notificaciones donde el usuario es receptor
        Notification.query.filter_by(user_id=current_user.id_usuario, is_read=False).update({'is_read': True})
        db.session.commit()
        logger.debug("Notificaciones no leídas marcadas como leídas.")

        # Formatear las notificaciones
        notifications_data = [
            {
                "id": notification.id,
                "timestamp": notification.timestamp.isoformat(),
                "message": notification.message,
                "user_id": notification.user_id,
                "sender_id": notification.sender_id,
                "is_read": notification.is_read
            }
            for notification in notifications
        ]

        # Devolver datos en formato JSON
        logger.info("Notificaciones cargadas y enviadas exitosamente.")
        return jsonify({"notifications": notifications_data}), 200

    except Exception as e:
        logger.exception("Error al recuperar notificaciones.")
        return jsonify({"error": "No se pudieron cargar las notificaciones."}), 500
