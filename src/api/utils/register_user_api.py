from src.models.database import db
from src.models.usuarios import Usuario
from src.models.colombia_data.colombia_data import Colombia
import logging
import bcrypt
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

# Configuración del Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Blueprint para la API de registro de usuarios
register_user_bp = Blueprint('register_user_bp', __name__)

@register_user_bp.route('/register_user', methods=['POST'])
def register_user():
    """
    API para registrar nuevos usuarios.
    Realiza validaciones de los campos obligatorios y procesa el registro en la base de datos,
    asignando automáticamente el ID de la ciudad basado en el nombre ingresado.
    """
    logger.info("Procesando solicitud POST para registrar usuario.")

    try:
        # Obtener los datos enviados en la solicitud
        data = request.get_json()
        logger.debug(f"Datos recibidos: {data}")

        # Validación de datos obligatorios
        required_fields = [
            'nombre', 'apellidos', 'correo', 'profesion',
            'cedula', 'celular', 'ciudad', 'contrasenia', 'confirmar_contrasenia'
        ]
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            logger.warning(f"Faltan los siguientes datos: {missing_fields}")
            return jsonify({'error': f"Faltan datos requeridos: {', '.join(missing_fields)}"}), 400

        # Validación de contraseñas
        if data['contrasenia'].strip() != data['confirmar_contrasenia'].strip():
            logger.warning("Las contraseñas no coinciden.")
            return jsonify({'error': 'Las contraseñas no coinciden. Por favor, verifica.'}), 400

        # Validar si el correo ya está registrado
        existing_user = Usuario.query.filter_by(correo=data['correo']).first()
        if existing_user:
            logger.info(f"Correo ya registrado: {data['correo']}")
            return jsonify({'error': 'El correo ya está registrado.'}), 409

        # Validar si la cédula ya está registrada
        existing_cedula = Usuario.query.filter_by(cedula=data['cedula']).first()
        if existing_cedula:
            logger.info(f"Cédula ya registrada: {data['cedula']}")
            return jsonify({'error': 'La cédula ya está registrada.'}), 409

        # Buscar el id de la ciudad basado en el nombre proporcionado
        ciudad = Colombia.query.filter_by(ciudad_nombre=data['ciudad'].strip()).first()
        if not ciudad:
            logger.warning(f"El nombre de la ciudad no es válido: {data['ciudad']}")
            return jsonify({'error': 'El nombre de la ciudad no es válido.'}), 400

        # Hashear la contraseña
        hashed_password = bcrypt.hashpw(data['contrasenia'].strip().encode('utf-8'), bcrypt.gensalt())
        logger.debug("Contraseña hasheada correctamente.")

        # Crear un nuevo usuario
        new_user = Usuario(
            nombre=data['nombre'],
            apellidos=data['apellidos'],
            correo=data['correo'],
            profesion=data['profesion'],
            cedula=data['cedula'],
            celular=data['celular'],
            ciudad_id=ciudad.ciudad_id,  # Asignar el ID de la ciudad automáticamente
            ciudad=data['ciudad'],  # Guardar también el nombre para validación
            contrasenia=hashed_password.decode('utf-8')  # Convertir el hash a string
        )
        db.session.add(new_user)
        db.session.commit()

        logger.info(f"Usuario registrado exitosamente: {new_user.nombre}")
        return jsonify({'message': '¡Te has registrado exitosamente!'}), 201

    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos durante el registro: {e}")
        db.session.rollback()
        return jsonify({'error': 'Error al registrar usuario en la base de datos.'}), 500

    except Exception as e:
        logger.exception("Error inesperado durante el registro de usuario.")
        return jsonify({'error': 'Ocurrió un error durante el registro. Inténtalo de nuevo.'}), 500
