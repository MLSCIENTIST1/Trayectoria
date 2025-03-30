from flask import Blueprint, jsonify, request
from src.models.database import db
from src.models.usuarios import Servicio
import logging
from flask_login import login_required

# Configurar logger para depuración
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Definir el Blueprint
obtener_nombre_servicios_bp = Blueprint('obtener_nombre_servicios', __name__)

@obtener_nombre_servicios_bp.route('/get_name_services_api', methods=['GET'])
@login_required
def obtener_nombre_servicios():
    """
    Endpoint para buscar servicios de forma dinámica (autocompletado).

    """
    logger.debug('bp cargado exitosamente')
    termino = request.args.get('q', '').strip()  # Término ingresado por el usuario

    # Validar si el término está vacío
    if not termino:
        return jsonify([])

    try:
        # Realizar la consulta filtrando servicios cuyo nombre coincida parcialmente
        servicios = Servicio.query.filter(
            Servicio.nombre_servicio.ilike(f"%{termino}%")
        ).limit(10).all()  # Limitar a 10 resultados

        # Extraer solo los nombres de los servicios para el autocompletado
        resultados = [servicio.nombre_servicio for servicio in servicios]

        # Registrar los resultados en los logs para depuración
        logger.debug(f"Término buscado: {termino}")
        logger.debug(f"Servicios encontrados: {resultados}")

        return jsonify(resultados)

    except Exception as e:
        # Manejar errores y registrar en los logs
        logger.error(f"Error al buscar servicios: {e}")
        return jsonify({"error": "Error al buscar servicios"}), 500