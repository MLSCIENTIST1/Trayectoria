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
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

# Blueprint para la API de registro de usuarios
register_user_bp = Blueprint("register_user_bp", __name__)

@register_user_bp.route("/register_user", methods=["POST"])
def register_user():
    """
    API para registrar nuevos usuarios.
    Obtiene el nombre de la ciudad desde los datos enviados y asigna automáticamente su ID basado en la tabla `Colombia`.
    """
    logger.info("Procesando solicitud POST para registrar usuario.")

    try:
        # Obtener los datos enviados en la solicitud
        data = request.get_json()
        logger.debug(f"Datos recibidos: {data}")

        # Normalizar el nombre de la ciudad
        ciudad_nombre_usuario = data["ciudad"].strip().lower()

        # Validación de datos obligatorios
        required_fields = [
            "nombre", "apellidos", "correo", "profesion",
            "cedula", "celular", "ciudad", "contrasenia", "confirmar_contrasenia"
        ]
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            logger.warning(f"Faltan los siguientes datos: {missing_fields}")
            return jsonify({"error": f"Faltan datos requeridos: {', '.join(missing_fields)}"}), 400

        # Validación de contraseñas
        if data["contrasenia"].strip() != data["confirmar_contrasenia"].strip():
            logger.warning("Las contraseñas no coinciden.")
            return jsonify({"error": "Las contraseñas no coinciden. Por favor, verifica."}), 400

        # Validar si el correo ya está registrado
        if Usuario.query.filter_by(correo=data["correo"]).first():
            logger.info(f"Correo ya registrado: {data['correo']}")
            return jsonify({"error": "El correo ya está registrado."}), 409

        # Validar si la cédula ya está registrada
        if Usuario.query.filter_by(cedula=data["cedula"]).first():
            logger.info(f"Cédula ya registrada: {data['cedula']}")
            return jsonify({"error": "La cédula ya está registrada."}), 409

        # 🔥 Buscar el ID de la ciudad basado en el nombre proporcionado
        ciudad = Colombia.query.filter(Colombia.ciudad_nombre.ilike(ciudad_nombre_usuario)).first()
        if not ciudad:
            ciudades_disponibles = [c.ciudad_nombre for c in Colombia.query.all()]
            logger.warning(f"El nombre de la ciudad no es válido: {data['ciudad']}")
            return jsonify({
                "error": "El nombre de la ciudad no es válido.",
                "sugerencias": ciudades_disponibles
            }), 400

        # Obtener el ID de la ciudad
        ciudad_id = ciudad.ciudad_id  

        # Hashear la contraseña
        hashed_password = bcrypt.hashpw(data["contrasenia"].strip().encode("utf-8"), bcrypt.gensalt())
        logger.debug("Contraseña hasheada correctamente.")

        # 🔥 Crear el usuario con el ID de ciudad obtenido automáticamente
        new_user = Usuario(
            nombre=data["nombre"],
            apellidos=data["apellidos"],
            correo=data["correo"],
            profesion=data["profesion"],
            cedula=data["cedula"],
            celular=data["celular"],
            ciudad_id=ciudad_id,  # ✅ Asignamos el ID de la ciudad correctamente
            ciudad=ciudad.ciudad_nombre,  # ✅ Pasamos el nombre de la ciudad correctamente
        )
        new_user.set_password(data["contrasenia"].strip())  # ✅ Usa `set_password()` para almacenar el hash

        db.session.add(new_user)
        db.session.commit()

        logger.info(f"Usuario registrado exitosamente: {new_user.nombre}")
        return jsonify({"message": "¡Te has registrado exitosamente!"}), 201

    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos durante el registro: {e}")
        db.session.rollback()
        return jsonify({"error": "Error al registrar usuario en la base de datos."}), 500

    except Exception as e:
        logger.exception("Error inesperado durante el registro de usuario.")
        return jsonify({"error": "Ocurrió un error durante el registro. Inténtalo de nuevo."}), 500
