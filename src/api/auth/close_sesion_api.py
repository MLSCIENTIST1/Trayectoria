# src/api/auth/close_sesion_api.py
import logging
from flask import Blueprint, request, jsonify
from datetime import datetime
from src.models.database import db
from src.models.colombia_data.sesion_usuario import SesionUsuario
from flask_cors import CORS # ✅ Importar CORS

# Configuración del Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

close_sesion_bp = Blueprint('close_sesion_bp', __name__)
# ✅ Aplicar CORS al Blueprint con el origen permitido y credenciales
CORS(close_sesion_bp, origins=["https://mitrayectoria.web.app"], supports_credentials=True)


@close_sesion_bp.route('/logout', methods=['POST', 'OPTIONS']) # ✅ Permitir OPTIONS
def logout():
    """
    API para cerrar sesión eliminando la entrada en la BD.
    Maneja solicitudes POST para el cierre de sesión y OPTIONS para el pre-vuelo CORS.
    """
    # 📌 Manejar la solicitud OPTIONS para CORS pre-vuelo
    if request.method == "OPTIONS":
        logger.info("📌 Solicitud OPTIONS recibida para /logout.")
        return '', 200

    logger.info("📌 Procesando solicitud POST de cierre de sesión.")

    token_sesion = request.headers.get("Authorization", "").strip()
    if not token_sesion:
        logger.warning("🚫 No se proporcionó un token de sesión.")
        return jsonify({"error": "No hay sesión activa para cerrar."}), 400

    sesion = SesionUsuario.query.filter_by(token_sesion=token_sesion).first()

    if sesion:
        if sesion.fecha_expiracion < datetime.utcnow():
            logger.info(f"⚠️ La sesión asociada al token ya había expirado.")
            # Aunque ya expiró, podemos eliminarla para limpiar
            try:
                db.session.delete(sesion)
                db.session.commit()
                logger.info("✅ Sesión expirada eliminada.")
            except Exception as e:
                 db.session.rollback()
                 logger.error(f"❌ Error al eliminar sesión expirada: {e}", exc_info=True)

            return jsonify({"message": "Sesión ya expirada."}), 200


        logger.info(f"✅ Eliminando sesión activa para usuario {sesion.usuario.nombre}.") # ✅ Acceder al nombre del usuario si es posible
        try:
            db.session.delete(sesion)
            db.session.commit()
            return jsonify({"message": "Sesión cerrada correctamente."}), 200
        except Exception as e:
             db.session.rollback()
             logger.error(f"❌ Error al eliminar sesión activa: {e}", exc_info=True)
             return jsonify({"error": "Error interno al cerrar la sesión."}), 500


    logger.warning("⚠️ Intento de cierre de sesión con un token inválido o ya cerrado.")
    return jsonify({"error": "Sesión inválida o ya cerrada."}), 400
