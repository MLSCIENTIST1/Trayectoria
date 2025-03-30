import logging
from flask import Blueprint, jsonify
from flask_login import login_required
from src.models.usuario import Usuario
from src.models.servicio import Servicio
from src.models.calificacion import Calificacion
from src.models.database import db

# Configurar logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Crear Blueprint para el detalle del candidato
detalle_candidato_bp = Blueprint('detalle_candidato_bp', __name__)

@detalle_candidato_bp.route('/detalle_candidato/<int:id_usuario>', methods=['GET'])
@login_required
def detalle_candidato_api(id_usuario):
    """
    API para obtener información detallada de un candidato.
    Devuelve los datos del usuario, los servicios ofrecidos y el puntaje promedio de la última labor.
    """
    logger.info(f"Procesando solicitud GET para el detalle del candidato con ID {id_usuario}.")

    try:
        # Buscar al usuario por su ID
        usuario = Usuario.query.get_or_404(id_usuario)
        logger.debug(f"Usuario encontrado: ID: {usuario.id_usuario}, Nombre: {usuario.nombre}")

        # Obtener todos los servicios ofrecidos por el usuario
        servicios = Servicio.query.filter_by(id_usuario=id_usuario).all()
        logger.debug(f"Servicios encontrados para el usuario {id_usuario}: {len(servicios)}")

        # Calcular el puntaje promedio en la última labor como contratado
        calificacion = Calificacion.query.filter_by(usuario_id=id_usuario).first()
        puntaje_ultima_labor = None
        if calificacion:
            # Calcular promedio de las calificaciones válidas
            calificaciones_contratado = [
                calificacion.calificacion_recived_contratado1,
                calificacion.calificacion_recived_contratado2,
                calificacion.calificacion_recived_contratado3
            ]
            validas = [c for c in calificaciones_contratado if c is not None]
            if len(validas) == 3:  # Solo calcular si hay 3 calificaciones válidas
                puntaje_ultima_labor = sum(validas) / 3
                calificacion.puntaje_por_labor = puntaje_ultima_labor
                db.session.commit()  # Guardar el puntaje promedio
                logger.debug(f"Puntaje promedio de la última labor calculado: {puntaje_ultima_labor}")
        
        # Preparar datos para el JSON
        servicios_data = [
            {
                "id_servicio": servicio.id_servicio,
                "nombre_servicio": servicio.nombre_servicio,
                "categoria": servicio.categoria,
                "id_usuario": servicio.id_usuario
            }
            for servicio in servicios
        ]
        usuario_data = {
            "id_usuario": usuario.id_usuario,
            "nombre": usuario.nombre,
            "email": usuario.email
        }

        logger.info(f"Datos preparados para el candidato {id_usuario}.")
        return jsonify({
            "usuario": usuario_data,
            "servicios": servicios_data,
            "puntaje_ultima_labor": puntaje_ultima_labor
        }), 200

    except Exception as e:
        logger.exception(f"Error al obtener el detalle del candidato con ID {id_usuario}.")
        return jsonify({"error": "Hubo un problema al obtener el detalle del candidato."}), 500
