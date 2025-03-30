from flask import Blueprint, request, jsonify
from src.models.usuarios import Usuario
from src.models.database import db
from src.models.colombia_data.colombia_data import Colombia
import logging
import bcrypt  # Importamos bcrypt para el hashing de contraseñas

# Configuración del logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Crear el Blueprint
post_register_api_bp = Blueprint('post_register_api', __name__)

# Ruta de registro
@post_register_api_bp.route('/post_register_api', methods=['POST'])
def register_user():
    print("Solicitud recibida en /post_register_api")
    logger.debug("Inicio de la función 'register_user': Solicitud POST recibida en /post_register_api")

    try:
        # Obtener los datos enviados en la solicitud
        data = request.get_json()
        logger.debug(f"Datos recibidos del cliente: {data}")

        # Validación de datos requeridos
        required_keys = ('nombre', 'apellidos', 'correo', 'profesion', 'cedula', 'celular', 'ciudad_id', 'ciudad', 'contrasenia', 'confirmar_contrasenia')
        if not all(key in data for key in required_keys):
            logger.warning(f"Faltan datos requeridos. Claves esperadas: {required_keys}, Claves recibidas: {data.keys()}")
            return jsonify({'error': 'Faltan datos requeridos en la solicitud.'}), 400

        # Validación de contraseñas
        if data['contrasenia'].strip() != data['confirmar_contrasenia'].strip():
            logger.warning(f"Contraseñas no coinciden. Contraseña: {data['contrasenia']}, Confirmación: {data['confirmar_contrasenia']}")
            return jsonify({'error': 'Las contraseñas no coinciden. Por favor, verifica.'}), 400

        # Validar si el correo ya está registrado
        logger.debug("Verificando si el correo ya está registrado.")
        existing_user = Usuario.query.filter_by(correo=data['correo']).first()
        if existing_user:
            logger.info(f"Correo ya registrado en la base de datos: {data['correo']}")
            return jsonify({'error': 'El correo ya está registrado.'}), 409

        # Validar si la cédula ya está registrada
        logger.debug("Verificando si la cédula ya está registrada.")
        existing_cedula = Usuario.query.filter_by(cedula=data['cedula']).first()
        if existing_cedula:
            logger.info(f"Cédula ya registrada en la base de datos: {data['cedula']}")
            return jsonify({'error': 'La cédula ya está registrada.'}), 409

        # Validación del ID de ciudad y el nombre
        logger.debug("Verificando ciudad_id y nombre de ciudad.")
        ciudad = Colombia.query.filter_by(ciudad_id=data['ciudad_id']).first()
        if not ciudad:
            logger.warning(f"El ciudad_id no es válido: {data['ciudad_id']}")
            return jsonify({'error': 'El ciudad_id no es válido.'}), 400
        
        logger.debug(f"Ciudad encontrada: ciudad_id={ciudad.ciudad_id}, Nombre={ciudad.ciudad_nombre}")
        if ciudad.ciudad_nombre.strip() != data['ciudad'].strip():
            logger.warning(f"Nombre de ciudad no coincide. Esperado: '{ciudad.ciudad_nombre}', Recibido: '{data['ciudad']}'")
            return jsonify({'error': 'El nombre de ciudad no coincide con el ciudad_id proporcionado.'}), 400

        # Hashear la contraseña
        logger.debug("Realizando el hash de la contraseña.")
        hashed_password = bcrypt.hashpw(data['contrasenia'].strip().encode('utf-8'), bcrypt.gensalt())
        logger.debug(f"Contraseña hasheada: {hashed_password}")

        # Crear un nuevo usuario
        logger.debug("Creando el nuevo usuario.")
        new_user = Usuario(
            nombre=data['nombre'],
            apellidos=data['apellidos'],
            correo=data['correo'],
            profesion=data['profesion'],
            cedula=data['cedula'],
            celular=data['celular'],
            ciudad_id=data['ciudad_id'],  # Almacena el ID de la ciudad
            ciudad=data['ciudad'],        # Almacena el nombre de la ciudad
            contrasenia=hashed_password.decode('utf-8')  # Almacena la contraseña hasheada
        )
        logger.debug(f"Nuevo usuario creado: {new_user}")

        # Guardar el usuario en la base de datos
        logger.debug("Guardando el nuevo usuario en la base de datos.")
        db.session.add(new_user)
        db.session.commit()
        logger.info(f"Usuario registrado exitosamente: {data['correo']}")

        return jsonify({'message': '¡Te has registrado exitosamente!'}), 201

    except Exception as e:
        logger.error(f"Error inesperado durante el registro: {e}")
        db.session.rollback()
        return jsonify({'error': 'Ocurrió un error durante el registro. Inténtalo de nuevo.'}), 500