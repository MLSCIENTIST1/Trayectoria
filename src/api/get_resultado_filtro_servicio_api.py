from flask import Blueprint, jsonify, request
from src.models.database import db
from src.models.servicio import Servicio
from src.models.usuarios import Usuario
from src.models.colombia_data.ratings import ServiceRatings  # Reemplazo de Calificacion
from src.models.colombia_data.colombia_data import Colombia
import logging
from flask_login import login_required
from sqlalchemy import or_

# Configurar logger para depuración
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

obtener_servicios_bp = Blueprint('resultado_filtro_servicio', __name__)

@obtener_servicios_bp.route('/get_resultado_filtro_servicio_api', methods=['POST', 'GET'])
@login_required
def resultado_filtro_servicio():
    try:
        ciudad = request.args.get('city')
        labor = request.args.get('job')

        query_servicios = Servicio.query
        condiciones = []

        if ciudad:
            condiciones.append(Servicio.categoria.ilike(f"%{ciudad}%"))
        if labor:
            condiciones.append(Servicio.nombre_servicio.ilike(f"%{labor}%"))

        if condiciones:
            query_servicios = query_servicios.filter(or_(*condiciones))

        servicios = query_servicios.all()

        if not servicios:  # Sin resultados
            return jsonify({"mensaje": "No se encontraron servicios para los criterios proporcionados"}), 404

        resultados = [
            {
                "servicio_id": servicio.id_servicio,
                "nombre_servicio": servicio.nombre_servicio,
                "descripcion": servicio.descripcion,
                "categoria": servicio.categoria,
                "precio": servicio.precio,
                "service_active": servicio.service_active,
                "datos_usuario": {
                    "usuario_id": servicio.id_usuario,
                    "nombre": Usuario.query.get(servicio.id_usuario).nombre,
                    "apellidos": Usuario.query.get(servicio.id_usuario).apellidos,
                    "correo": Usuario.query.get(servicio.id_usuario).correo,
                    "celular": Usuario.query.get(servicio.id_usuario).celular,
                    "ciudad": Usuario.query.get(servicio.id_usuario).ciudad,
                    "labor": Usuario.query.get(servicio.id_usuario).labor,
                    "calificaciones": [
                        {
                            "calificacion1": c.calificacion_recived_contratado1,
                            "calificacion2": c.calificacion_recived_contratado2,
                            "calificacion3": c.calificacion_recived_contratado3
                        }
                        for c in ServiceRatings.query.filter_by(servicio_id=servicio.id_servicio).all()
                    ]
                }
            }
            for servicio in servicios
        ]

        return jsonify({"resultados": resultados})

    except Exception as e:
        logger.error(f"Error al realizar la consulta: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500