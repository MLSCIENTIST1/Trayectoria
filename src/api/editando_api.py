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

# Crear Blueprint para la funcionalidad de edición de perfil
editando_bp = Blueprint('editando_bp', __name__)

@editando_bp.route('/loged', methods=['GET'])
@login_required
def editando_api():
    """
    API para obtener los datos del usuario logueado.
    Devuelve información básica del usuario en formato JSON.
    """
    logger.info(f"Procesando solicitud GET para editar datos del usuario {current_user.id_usuario}.")

    try:
        # Obtener datos básicos del usuario actual
        usuario_data = {
            "id_usuario": current_user.id_usuario,
            "nombre": current_user.nombre,
            "email": current_user.email
        }
        logger.debug(f"Datos del usuario obtenidos: {usuario_data}")

        # Devolver datos en formato JSON
        return jsonify({"usuario": usuario_data}), 200

    except Exception as e:
        logger.exception("Error al procesar los datos del usuario.")
        return jsonify({"error": "Hubo un problema al obtener los datos del usuario."}), 500

