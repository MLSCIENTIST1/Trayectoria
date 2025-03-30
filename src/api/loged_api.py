import logging
from flask import Blueprint, jsonify
from flask_login import login_required, current_user

# Configurar logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Crear Blueprint para la funcionalidad de usuario logueado
loged_bp = Blueprint('loged', __name__)

@loged_bp.route('/loged', methods=['GET'])
@login_required
def principal_usuario_logueado():
    """
    API para manejar la información básica del usuario logueado.
    Devuelve un mensaje de bienvenida junto con el ID del usuario autenticado.
    """
    logger.info(f"El usuario {current_user.id_usuario} ha accedido a la API de usuario logueado.")

    try:
        # Devolver datos básicos sobre el usuario logueado
        return jsonify({
            "message": "Bienvenido al área principal del usuario logueado.",
            "user_id": current_user.id_usuario
        }), 200

    except Exception as e:
        logger.exception("Error al procesar la solicitud en la API del usuario logueado.")
        return jsonify({"error": "Hubo un problema al cargar los datos del usuario logueado."}), 500
