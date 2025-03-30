import logging
from flask import Blueprint, jsonify
from flask_login import login_required, current_user

# Importar la función auxiliar para calcular servicios
from src.utils.calculos import calcular_total_servicios

# Configurar logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Crear Blueprint para la funcionalidad de conteo de servicios ofrecidos
service_count_offered_bp = Blueprint('service_count_offered_bp', __name__)

@service_count_offered_bp.route('/offered_service', methods=['GET'])
@login_required
def service_count_offered():
    """
    API para obtener el total de servicios ofrecidos por el usuario actual.
    Devuelve los datos en formato JSON.
    """
    logger.info(f"Procesando solicitud GET para el conteo de servicios ofertados del usuario {current_user.id_usuario}.")

    try:
        # Calcular el total de servicios ofrecidos
        total_services = calcular_total_servicios()
        logger.debug(f"✅ Total de servicios calculados: {total_services}")

        # Devolver los datos en formato JSON
        return jsonify({"services_offered": total_services}), 200

    except Exception as e:
        logger.exception("Error al contar los servicios ofertados.")
        return jsonify({"error": "Ocurrió un error al procesar la solicitud."}), 500
