import logging
from flask import Blueprint, jsonify
from flask_login import current_user
from sqlalchemy import or_, and_
from src.models.servicio import Servicio
from src.models.colombia_data.ratings import ServiceRatings

# Configurar logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Crear Blueprint para la funcionalidad de calificaciones recibidas por contratante
calificaciones_recibidas_bp = Blueprint('calificaciones_recibidas_bp', __name__)

@calificaciones_recibidas_bp.route('/calificaciones_recibidas/contratante', methods=['GET'])
def calificaciones_recibidas_contratante():
    """
    API para obtener las calificaciones recibidas por el contratante en sus servicios.
    Devuelve una lista en formato JSON con las calificaciones relacionadas.
    """
    logger.info("Procesando solicitud GET para obtener calificaciones recibidas como contratante.")

    try:
        # Consultar las calificaciones relacionadas al contratante actual
        calificaciones = ServiceRatings.query.join(Servicio).filter(
            and_(
                Servicio.id_contratante == current_user.id_usuario,
                or_(
                    ServiceRatings.calificacion_recived_contratante1.isnot(None),
                    ServiceRatings.calificacion_recived_contratante2.isnot(None),
                    ServiceRatings.calificacion_recived_contratante3.isnot(None)
                )
            )
        ).all()

        logger.debug(f"Calificaciones recibidas como contratante: {[c.id_rating for c in calificaciones]}")

        # Crear una lista con los datos a devolver
        calificaciones_data = [
            {
                "id_rating": calificacion.id_rating,
                "calificacion1": calificacion.calificacion_recived_contratante1,
                "calificacion2": calificacion.calificacion_recived_contratante2,
                "calificacion3": calificacion.calificacion_recived_contratante3,
                "comentario": calificacion.comentary_employer_hired
            }
            for calificacion in calificaciones
        ]

        # Devolver datos en formato JSON
        return jsonify({
            "calificaciones": calificaciones_data,
            "rol": "contratante"
        }), 200

    except Exception as e:
        logger.exception("Error al obtener calificaciones recibidas como contratante.")
        return jsonify({"error": "Hubo un error al cargar las calificaciones."}), 500