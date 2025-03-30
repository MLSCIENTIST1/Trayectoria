from flask import Blueprint, jsonify, request
from src.models.database import db
import logging
from flask_login import login_required
from src.models.colombia_data.colombia_data import Colombia

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Definir el Blueprint
obtener_nombre_ciudades_bp = Blueprint('obtener_nombre_ciudades', __name__)

@obtener_nombre_ciudades_bp.route('/get_name_cities', methods=['GET'])

def obtener_nombre_ciudades():
    termino = request.args.get('q', '').strip()
    id_ciudad = request.args.get('id', '').strip()

    try:
        # Búsqueda por ID
        if id_ciudad:
            if not id_ciudad.isdigit():
                return jsonify({"error": "El ID debe ser un número"}), 400
            ciudad = Colombia.query.filter_by(id=id_ciudad).first()
            if ciudad:
                return jsonify({"id": ciudad.id, "ciudad_nombre": ciudad.ciudad_nombre})
            else:
                return jsonify({"error": "Ciudad no encontrada"}), 404

        # Búsqueda por nombre
        if termino:
            ciudades = Colombia.query.filter(
                Colombia.ciudad_nombre.ilike(f"%{termino}%")
            ).limit(10).all()
            resultados = [ciudad.ciudad_nombre for ciudad in ciudades]
            return jsonify(resultados)

        # Sin parámetros válidos
        return jsonify({"error": "Se requiere un término o ID"}), 400

    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500