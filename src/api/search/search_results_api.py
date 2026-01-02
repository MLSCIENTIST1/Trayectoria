from src.models.database import db
from src.models.usuarios import Usuario
from src.models.servicio import Servicio
import logging
from flask import Blueprint, jsonify, request
from sqlalchemy import or_

# Configuración del Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Blueprint para realizar búsquedas filtradas
search_results_bp = Blueprint('search_results_bp', __name__)

@search_results_bp.route('/search_results', methods=['POST'])
def resultado_filtro_primera_busqueda():
    """
    API para realizar una búsqueda filtrada de servicios y usuarios por ciudad, labor o nombre.
    Devuelve los resultados en formato JSON, con logs detallados para depuración.
    """
    logger.info("🚀 Procesando solicitud POST para búsqueda filtrada.")

    try:
        # 🔍 Verificar si hay registros en la base de datos
        total_servicios = Servicio.query.count()
        total_usuarios = Usuario.query.count()
        logger.debug(f"📊 Total Servicios en la BD: {total_servicios}")
        logger.debug(f"📊 Total Usuarios en la BD: {total_usuarios}")

        if total_servicios == 0 and total_usuarios == 0:
            logger.warning("⚠️ No hay datos en la base de datos. Retornando lista vacía.")
            return jsonify({"resultados": [], "message": "No se encontraron registros disponibles."}), 200

        # 📝 Obtener parámetros de la solicitud
        data = request.get_json()
        ciudad = data.get('ciudad', '').strip() if data else ''
        labor = data.get('labor', '').strip() if data else ''
        nombre_usuario = data.get('nombre_usuario', '').strip() if data else ''
        logger.debug(f"🎯 Parámetros de búsqueda - Ciudad: {ciudad}, Labor: {labor}, Usuario: {nombre_usuario}")

        # 🔍 Construir la consulta con filtros
        condiciones_servicios = []
        condiciones_usuarios = []

        if ciudad:
            condiciones_servicios.append(Servicio.categoria.ilike(f"%{ciudad}%"))
        if labor:
            condiciones_servicios.append(Servicio.nombre_servicio.ilike(f"%{labor}%"))
        if nombre_usuario:
            condiciones_usuarios.append(Usuario.nombre.ilike(f"%{nombre_usuario}%"))
            condiciones_usuarios.append(Usuario.correo.ilike(f"%{nombre_usuario}%"))

        # 🔎 Consultar servicios
        if condiciones_servicios:
            servicios = Servicio.query.filter(or_(*condiciones_servicios)).limit(20).all()
            logger.debug(f"🔹 Servicios encontrados con filtros: {len(servicios)}")
        else:
            servicios = Servicio.query.limit(20).all()
            logger.debug("🔹 No se aplicaron filtros, trayendo primeros 20 servicios.")

        # 🔎 Consultar usuarios
        if condiciones_usuarios:
            usuarios = Usuario.query.filter(or_(*condiciones_usuarios)).limit(20).all()
            logger.debug(f"🔹 Usuarios encontrados con filtros: {len(usuarios)}")
        else:
            usuarios = Usuario.query.limit(20).all()
            logger.debug("🔹 No se aplicaron filtros, trayendo primeros 20 usuarios.")

        # ⚠️ Validación si todo sigue vacío
        if not servicios and not usuarios:
            logger.warning("🚨 No se encontraron coincidencias, devolviendo primeros 20 registros generales.")
            servicios = Servicio.query.limit(20).all()
            usuarios = Usuario.query.limit(20).all()

        logger.debug(f"✅ Final - Servicios: {len(servicios)}, Usuarios: {len(usuarios)}")

        # 📌 Preparar datos en JSON
        resultados = {
            "servicios": [
                {
                    "id_servicio": servicio.id_servicio,
                    "nombre_servicio": servicio.nombre_servicio,
                    "categoria": servicio.categoria,
                    "id_usuario": servicio.id_usuario
                }
                for servicio in servicios
            ],
            "usuarios": [
                {
                    "id_usuario": usuario.id_usuario,
                    "nombre": usuario.nombre,
                    "correo": usuario.correo,
                }
                for usuario in usuarios
            ]
        }

        logger.info("✅ Resultados de búsqueda preparados exitosamente.")
        return jsonify(resultados), 200

    except Exception as e:
        logger.error("🔥 Error al realizar la búsqueda.", exc_info=True)
        return jsonify({"error": "Hubo un problema al realizar la búsqueda."}), 500
