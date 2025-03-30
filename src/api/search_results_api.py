import logging
from flask import Blueprint, jsonify, request
from flask_login import login_required
from sqlalchemy import or_
from src.models.servicio import Servicio
from src.models.usuario import Usuario

# Configurar logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Crear Blueprint para la funcionalidad de búsqueda
search_results_bp = Blueprint('search_results_bp', __name__)

@search_results_bp.route('/search/resultado_filtro_primera_busqueda', methods=['GET'])
@login_required
def resultado_filtro_primera_busqueda_api():
    """
    API para realizar una búsqueda filtrada de servicios por ciudad o labor.
    Devuelve los servicios y sus usuarios asociados en formato JSON.
    """
    logger.info("Procesando solicitud GET para búsqueda filtrada de servicios.")

    try:
        # Obtener parámetros de la solicitud
        ciudad = request.args.get('ciudad')
        labor = request.args.get('labor')
        logger.debug(f"Parámetros de búsqueda - Ciudad: {ciudad}, Labor: {labor}")

        # Construir la consulta con filtros dinámicos
        query_servicios = Servicio.query
        condiciones = []

        if ciudad:
            condiciones.append(Servicio.categoria.ilike(f"%{ciudad}%"))
        if labor:
            condiciones.append(Servicio.nombre_servicio.ilike(f"%{labor}%"))

        if condiciones:
            query_servicios = query_servicios.filter(or_(*condiciones))
        servicios = query_servicios.all()
        logger.debug(f"Servicios encontrados: {len(servicios)}")

        # Combinar cada servicio con su usuario correspondiente
        resultados = [
            {
                "servicio": {
                    "id_servicio": servicio.id_servicio,
                    "nombre_servicio": servicio.nombre_servicio,
                    "categoria": servicio.categoria,
                    "id_usuario": servicio.id_usuario
                },
                "usuario": {
                    "id_usuario": usuario.id_usuario,
                    "nombre": usuario.nombre,
                    "email": usuario.email
                } if (usuario := Usuario.query.get(servicio.id_usuario)) else None
            }
            for servicio in servicios
        ]

        logger.info("Resultados de búsqueda preparados exitosamente.")
        return jsonify({"resultados": resultados}), 200

    except Exception as e:
        logger.exception("Error al realizar la búsqueda de servicios.")
        return jsonify({"error": "Hubo un problema al realizar la búsqueda."}), 500
