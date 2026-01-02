import logging
from flask import Blueprint, jsonify, request
from datetime import datetime
from src.models.database import db
from src.models.colombia_data.sesion_usuario import SesionUsuario
from flask_cors import CORS  # ✅ Importar CORS
from src.models.usuarios import Usuario  # ✅ Importar Usuario para acceder a los datos

# 📌 Configuración del Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

status_sesion_bp = Blueprint("status_sesion_bp", __name__)  # ✅ Se asegura que coincide con el registro en `__init__.py`
CORS(status_sesion_bp, origins=["https://mitrayectoria.web.app"], supports_credentials=True)  # ✅ Aplicar CORS

@status_sesion_bp.route("/session_status", methods=["GET", "OPTIONS"])  # ✅ Se mantiene sin prefijo adicional
def session_status():
    """
    API para verificar el estado de la sesión en la BD.
    Maneja solicitudes GET para el estado y OPTIONS para el pre-vuelo CORS.
    """
    if request.method == "OPTIONS":
        logger.info("📌 Solicitud OPTIONS recibida para /session_status.")
        return "", 200

    logger.info("📌 Solicitud GET para verificar el estado de la sesión recibida.")

    token_sesion = request.headers.get("Authorization", "").strip()
    if not token_sesion:
        logger.warning("🚫 No se proporcionó un token de sesión.")
        return jsonify({"isAuthenticated": False, "message": "No hay sesión activa."}), 401

    # ✅ Optimización de la consulta y uso de 'join' para acceder a datos del usuario
    sesion = SesionUsuario.query.filter(
        SesionUsuario.token_sesion == token_sesion,
        SesionUsuario.fecha_expiracion > datetime.utcnow()
    ).join(Usuario).first()

    if sesion:
        logger.info(f"✅ Sesión activa para usuario {sesion.usuario.nombre}.")
        return jsonify({
            "isAuthenticated": True,
            "userId": sesion.usuario.id_usuario,
            "userName": sesion.usuario.nombre,
            "userEmail": sesion.usuario.correo
        }), 200

    logger.warning("⚠️ Sesión inválida o expirada.")
    return jsonify({"isAuthenticated": False, "message": "Sesión expirada o inválida."}), 401
