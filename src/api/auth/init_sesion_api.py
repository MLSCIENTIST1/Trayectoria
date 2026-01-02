# src/api/auth/init_sesion_api.py
import logging
import secrets
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from src.models.database import db
from src.models.usuarios import Usuario
from src.models.colombia_data.sesion_usuario import SesionUsuario
from flask_cors import CORS # ✅ Importar CORS

# 📌 Configuración del Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

init_sesion_bp = Blueprint("init_sesion_bp", __name__) # ✅ Asegurar que coincide con el registro en __init__.py
# ✅ Aplicar CORS al Blueprint de autenticación con el origen permitido y credenciales
CORS(init_sesion_bp, origins=["https://mitrayectoria.web.app"], supports_credentials=True)


@init_sesion_bp.route("/login", methods=["POST", "OPTIONS"]) # ✅ Permitir OPTIONS
def ingreso():
    """
    API para manejar inicio de sesión con sesión en la base de datos.
    Maneja solicitudes POST para el login y OPTIONS para el pre-vuelo CORS.
    """
    # 📌 Manejar la solicitud OPTIONS para CORS pre-vuelo
    if request.method == "OPTIONS":
        logger.info("📌 Solicitud OPTIONS recibida para /login.")
        # flask-cors se encarga de agregar las cabeceras Access-Control-*
        return '', 200

    logger.info("📌 Solicitud POST de inicio de sesión recibida.")

    # 📌 Obtener datos de la solicitud
    data = request.get_json()
    if not data:
        logger.error("❌ No se proporcionaron datos en la solicitud.")
        return jsonify({"error": "Datos no proporcionados"}), 400

    correo = data.get("correo", "").strip()
    contrasenia_input = data.get("contrasenia", "").strip()

    if not correo or not contrasenia_input:
        logger.warning("⚠️ Correo y contraseña son obligatorios.")
        return jsonify({"error": "Debes proporcionar correo y contraseña."}), 400

    # 📌 Verificar si el usuario existe y validar credenciales
    usuario = Usuario.query.filter_by(correo=correo).first()
    if not usuario:
        logger.warning(f"🚫 No existe un usuario con el correo: {correo}")
        return jsonify({"error": "Correo o contraseña incorrectos."}), 401

    if not usuario.check_password(contrasenia_input):
        logger.warning(f"🚫 Contraseña incorrecta para el usuario: {correo}")
        return jsonify({"error": "Correo o contraseña incorrectos."}), 401

    logger.info(f"✅ Usuario {usuario.nombre} autenticado correctamente.")

    # 📌 Verificar si ya tiene una sesión activa
    sesion_existente = SesionUsuario.query.filter_by(usuario_id=usuario.id_usuario).first()
    if sesion_existente and sesion_existente.fecha_expiracion > datetime.utcnow():
        logger.info(f"🔄 Usuario {usuario.nombre} ya tiene sesión activa con token: {sesion_existente.token_sesion}.")
        return jsonify({"message": "Ya tienes una sesión activa.", "token_sesion": sesion_existente.token_sesion, "success": True}), 200

    # 📌 Crear una nueva sesión en la BD
    try:
        nueva_sesion = SesionUsuario(
            usuario_id=usuario.id_usuario,
            token_sesion=secrets.token_hex(32),
            fecha_inicio=datetime.utcnow(),
            fecha_expiracion=datetime.utcnow() + timedelta(days=7)
        )

        db.session.add(nueva_sesion)
        db.session.commit()

        logger.info(f"✅ Sesión iniciada correctamente para usuario {usuario.nombre}. Token: {nueva_sesion.token_sesion}")
        return jsonify({"message": "Inicio de sesión exitoso", "token_sesion": nueva_sesion.token_sesion, "success": True}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error al registrar la sesión en la base de datos: {e}", exc_info=True)
        return jsonify({"error": "Error interno. Inténtalo nuevamente más tarde."}), 500
