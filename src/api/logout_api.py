import logging
from flask import Blueprint, jsonify
from flask_login import logout_user

# Configurar logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Crear Blueprint para la funcionalidad de cierre de sesión
logout_bp = Blueprint('logout_bp', __name__)

@logout_bp.route('/logout', methods=['POST'])
def logout_api():
    """
    API para cerrar la sesión del usuario autenticado.
    Devuelve una confirmación en formato JSON.
    """
    logger.info("Procesando solicitud POST para cerrar sesión.")

    try:
        # Cerrar la sesión del usuario
        logout_user()
        logger.info("La sesión se ha cerrado exitosamente.")
        return jsonify({"message": "La sesión se ha cerrado exitosamente."}), 200

    except Exception as e:
        logger.exception("Error al cerrar la sesión.")
        return jsonify({"error": "Hubo un problema al cerrar la sesión."}), 500
