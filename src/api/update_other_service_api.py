import logging
from flask import Blueprint, jsonify, request
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

# Crear Blueprint para la funcionalidad de actualización de servicios
update_service_bp = Blueprint('update_service_bp', __name__)

@update_service_bp.route('/update_other_service/<int:service_id>', methods=['POST'])
@login_required
def update_other_service(service_id):
    """
    API para actualizar un servicio específico asociado al usuario actual.
    Permite la actualización de campos específicos enviados desde el frontend.
    """
    logger.info(f"Procesando solicitud POST para actualizar el servicio con ID: {service_id}")

    try:
        # Obtener datos enviados desde el frontend
        data = request.get_json()
        logger.debug(f"Datos recibidos para actualizar el servicio {service_id}: {data}")

        # Buscar el servicio asociado al usuario actual
        service = Servicio.query.filter_by(id_servicio=service_id, id_usuario=current_user.id_usuario).first()

        if service:
            # Actualizar solo los campos presentes en `data`
            if 'service_name' in data and data['service_name']:
                service.nombre_servicio = data['service_name']
                logger.debug(f"Nombre del servicio actualizado: {service.nombre_servicio}")
            if 'description' in data and data['description']:
                service.descripcion = data['description']
                logger.debug(f"Descripción del servicio actualizada: {service.descripcion}")
            if 'category' in data and data['category']:
                service.categoria = data['category']
                logger.debug(f"Categoría del servicio actualizada: {service.categoria}")
            if 'price' in data and data['price'] is not None:
                service.precio = float(data['price'])
                logger.debug(f"Precio del servicio actualizado: {service.precio}")

            # Guardar los cambios
            db.session.commit()
            logger.info(f"Servicio con ID {service_id} actualizado con éxito.")
            return jsonify({"message": "Servicio actualizado con éxito."}), 200
        else:
            logger.warning(f"El servicio con ID {service_id} no existe o no pertenece al usuario.")
            return jsonify({"error": "El servicio no existe o no pertenece al usuario."}), 400
    except Exception as e:
        logger.exception("Error al actualizar el servicio adicional.")
        return jsonify({"error": "Hubo un problema al actualizar el servicio adicional."}), 500
