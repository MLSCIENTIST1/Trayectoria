import logging
from flask import Blueprint, jsonify

# Configurar logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Crear Blueprint para el índice
index_bp = Blueprint('index_bp', __name__)

@index_bp.route('/', methods=['GET'])
def index_api():
    """
    API para manejar la solicitud GET de la página principal.
    Devuelve un mensaje de bienvenida en formato JSON.
    """
    logger.info("Procesando solicitud GET para la página principal.")
    try:
        # Devolver un mensaje básico en formato JSON
        return jsonify({"message": "Bienvenido a la página principal de la API."}), 200
    except Exception as e:
        logger.exception("Error al procesar la solicitud para la página principal.")
        return jsonify({"error": "Hubo un problema al cargar la página principal."}), 500
