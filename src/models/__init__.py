from .notification import Notification
from .servicio import Servicio
from .message import Message
from .usuarios import Usuario
from .etapa import Etapa  # Nuevo modelo
from .foto import Foto  # Nuevo modelo
from .audio import Audio  # Nuevo modelo
from .video import Video  # Nuevo modelo
from .plantilla_personalizada import PlantillaPersonalizada  # ✅ Nuevo modelo agregado
from .colombia_data.sesion_usuario import SesionUsuario  # ✅ Nueva tabla de sesiones agregada

from src.models.colombia_data.ratings import ServiceRatings
from src.models.colombia_data.ratings import ServiceOverallScores
from src.models.colombia_data.ratings import ServiceQualifiers
from src.models.colombia_data import Feedback, MonetizationManagement, Colombia
from src.models.database import db, init_app, create_database, DATABASE_URL

# 📌 Crear la base de datos al cargar el módulo
create_database()

# 📌 Exportar funciones clave para otros módulos
__all__ = [
    "db",
    "init_app",
    "DATABASE_URL",
    "Notification",
    "Servicio",
    "Message",
    "Usuario",
    "SesionUsuario",  # ✅ Nueva tabla de sesiones agregada
    "Etapa",
    "Foto",
    "Audio",
    "Video",
    "PlantillaPersonalizada",
    "ServiceRatings",
    "ServiceOverallScores",
    "ServiceQualifiers",
    "Feedback",
    "MonetizationManagement"
]
