import logging
from flask import Blueprint, jsonify
from flask_login import current_user, login_required
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

# Crear Blueprint para la funcionalidad de eliminación de servicios
delete_service_bp = Blueprint('delete_service_bp', __name__)

@delete_service_bp.route('/delete_other_service/<int:service_id>', methods=['DELETE'])
@login_required
def delete_other_service(service_id):
    """
    API para eliminar un servicio específico asociado al usuario actual.
    Verifica que el servicio exista y que pertenezca al usuario antes de eliminarlo.
    """
    logger.info(f"Procesando solicitud DELETE para eliminar el servicio con ID: {service_id}")

    try:
        # Buscar el servicio en el modelo Servicio en lugar de AditionalService
        service = Servicio.query.filter_by(id_servicio=service_id, id_usuario=current_user.id_usuario).first()

        if service:
            logger.debug(f"Servicio encontrado: {service.nombre_servicio}. Procediendo a eliminar.")
            db.session.delete(service)
            db.session.commit()
            logger.info(f"Servicio con ID {service_id} eliminado exitosamente.")
            return jsonify({"message": "Servicio eliminado con éxito."}), 200
        else:
            logger.warning(f"Servicio con ID {service_id} no encontrado o no pertenece al usuario.")
            return jsonify({"error": "El servicio no existe o no pertenece al usuario."}), 400

    except Exception as e:
        logger.exception("Error al eliminar el servicio.")
        return jsonify({"error": "Hubo un problema al eliminar el servicio."}), 500