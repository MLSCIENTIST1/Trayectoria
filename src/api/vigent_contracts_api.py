import logging
from flask import Blueprint, jsonify
from flask_login import current_user, login_required
from src.models.servicio import Servicio

# Configurar logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Crear Blueprint para la funcionalidad de contratos vigentes
vigent_contracts_bp = Blueprint('vigent_contracts_bp', __name__)

@vigent_contracts_bp.route('/vigent_contracts/<string:role>', methods=['GET'])
@login_required
def vigent_contracts(role):
    """
    API para obtener contratos vigentes según el rol (contratante o contratado).
    Devuelve los datos en formato JSON.
    """
    logger.info(f"Procesando solicitud GET para contratos vigentes con rol: {role} del usuario {current_user.id_usuario}.")

    try:
        # Verificar si el rol es válido
        if role not in ['contratante', 'contratado']:
            logger.warning("Rol inválido seleccionado.")
            return jsonify({"error": "Rol inválido seleccionado."}), 400

        # Obtener contratos según el rol seleccionado
        if role == 'contratante':
            contracts = Servicio.query.filter_by(id_contratante=current_user.id_usuario).all()
        else:  # role == 'contratado'
            contracts = Servicio.query.filter_by(id_contratado=current_user.id_usuario).all()

        logger.debug(f"Contratos obtenidos para el rol {role}: {len(contracts)} encontrados.")

        # Añadir el nombre de la persona a calificar
        contracts_with_names = []
        for contract in contracts:
            if role == 'contratante':
                # Si el usuario es contratante, califica al contratado
                person_to_rate = contract.contratado.nombre if contract.contratado else "No definido"
            elif role == 'contratado':
                # Si el usuario es contratado, califica al contratante
                person_to_rate = contract.contratante.nombre if contract.contratante else "No definido"

            contracts_with_names.append({
                'id_servicio': contract.id_servicio,
                'nombre_servicio': contract.nombre_servicio,
                'fecha_inicio': str(contract.fecha_inicio),
                'fecha_fin': str(contract.fecha_fin),
                'person_to_rate': person_to_rate  # Nombre dinámico para el botón
            })

        logger.debug(f"Contratos procesados para el rol {role}: {contracts_with_names}")

        # Devolver los datos en formato JSON
        return jsonify({
            "contracts": contracts_with_names,
            "role": role
        }), 200

    except Exception as e:
        logger.exception("Error al obtener los contratos vigentes.")
        return jsonify({"error": "Hubo un error al cargar los contratos vigentes."}), 500
