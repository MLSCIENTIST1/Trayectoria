import logging
from flask import Blueprint, jsonify
from flask_login import login_required, current_user

# Importar función auxiliar (debes asegurarte de definirla/importarla)
from src.utils.calculos import calcular_total_servicios

# Configurar logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Crear Blueprint para la funcionalidad de servicios ofrecidos
offered_service_page_bp = Blueprint('offered_service_page_bp', __name__)

@offered_service_page_bp.route('/offered_service_page', methods=['GET'])
@login_required
def offered_service_page():
    """
    API para obtener el total de servicios ofrecidos y devolverlos en formato JSON.
    """
    logger.info(f"Procesando solicitud GET para la página de servicios ofrecidos del usuario {current_user.id_usuario}.")

    try:
        # Calcular el total de servicios ofrecidos
        total_services = calcular_total_servicios()
        logger.debug(f"Total de servicios ofrecidos calculados: {total_services}")

        # Devolver los datos en formato JSON
        return jsonify({"services_offered": total_services}), 200

    except Exception as e:
        logger.exception("Error al procesar la solicitud para la página de servicios ofrecidos.")
        return jsonify({"error": "Hubo un problema al cargar los servicios ofrecidos."}), 500
