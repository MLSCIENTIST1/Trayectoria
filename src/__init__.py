import os
import sys
import logging
from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restful import Api

from src.models.database import db, init_app
from src.api import api_bp  # ✅ Se importa el Blueprint principal de las APIs
from src.models.usuarios import Usuario
from src.models.colombia_data.sesion_usuario import SesionUsuario  # ✅ Tabla de sesiones en BD

# Importación individual de los Blueprints de autenticación para registro directo
from src.api.auth.close_sesion_api import close_sesion_bp
from src.api.auth.init_sesion_api import init_sesion_bp
from src.api.auth.password_api import password_bp
from src.api.auth.status_sesion_api import status_sesion_bp


# Inicializar la variable global de Flask-Migrate
migrate = None

# 📌 Configuración de logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app_startup.log", mode="a", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "clave_secreta_predeterminada")

def create_app():
    logger.info("🚀 Inicializando la aplicación Flask")
    flask_env = os.environ.get("FLASK_ENV", "development")
    logger.info(f"🔧 Entorno Flask: {flask_env}")

    app = Flask(__name__)
    app.config.from_object(Config)
    logger.info("✅ Flask app creada y configuración cargada")

    app.config["SECRET_KEY"] = Config.SECRET_KEY
    logger.info("🔑 Clave secreta configurada")

    app.config["ENV"] = "development"
    app.config["DEBUG"] = True

    try:
        logger.info("🔄 Intentando inicializar la base de datos...")
        init_app(app)
        global migrate
        migrate = Migrate(app, db)
        logger.info("✅ Base de datos y migración inicializadas correctamente")
    except Exception as e:
        logger.error(f"❌ Error inicializando la base de datos: {e}", exc_info=True)
        raise

    # 🌍 Inicializar CORS con configuración específica
    CORS(app, origins=["https://mitrayectoria.web.app"], supports_credentials=True)
    app.config["CORS_HEADERS"] = "Content-Type"
    logger.info("🌐 CORS configurado para aceptar solicitudes de `https://mitrayectoria.web.app`")

    # 📌 Verificación de sesión de usuario en la base de datos
    def verificar_sesion(usuario_id):
        logger.info(f"🔍 Verificando sesión de usuario ID: {usuario_id}")
        sesion = SesionUsuario.query.filter_by(usuario_id=usuario_id).first()
        if sesion and sesion.fecha_expiracion > datetime.utcnow():
            logger.info(f"✅ Sesión activa encontrada para usuario {usuario_id}. Token: {sesion.token_sesion}")
            return sesion.token_sesion
        else:
            logger.warning(f"⚠️ No hay sesión activa para usuario {usuario_id}")
            return None

    logger.info("🔗 Registrando Blueprints...")

    # ✅ Registrar el Blueprint principal de APIs sin prefijo
    app.register_blueprint(api_bp)

    # ✅ Registrar individualmente los Blueprints de autenticación con prefijo /api/auth
    app.register_blueprint(close_sesion_bp, url_prefix='/api/auth')
    app.register_blueprint(init_sesion_bp, url_prefix='/api/auth')
    app.register_blueprint(password_bp, url_prefix='/api/auth')
    app.register_blueprint(status_sesion_bp, url_prefix='/api/auth')


    logger.info("✅ Blueprints registrados correctamente")

    # 📜 Mostrar las rutas registradas con log
    with app.app_context(): # Acceder a url_map dentro del contexto de la aplicación
        for rule in app.url_map.iter_rules():
            logger.info(f"📌 Endpoint: {rule.endpoint}, Ruta: {rule.rule}, Métodos: {rule.methods}")


    # 🚀 Inicializar Flask-RESTful
    api = Api(app)
    logger.info("✅ API RESTful inicializada") # Recurso registrado se maneja dentro de los Blueprints o en otro lado

    app.config["UPLOAD_FOLDER"] = "static/uploads/"

    return app

if __name__ == "__main__":
    app = create_app()
    logger.info("🚀 Servidor Flask corriendo en http://0.0.0.0:5000/")
    app.run(host="0.0.0.0", port=5000, debug=True)