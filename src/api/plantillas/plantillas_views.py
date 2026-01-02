import logging
from flask import Blueprint, render_template, jsonify, request
from src.models.database import db
from src.models.plantilla_personalizada import PlantillaPersonalizada

logger = logging.getLogger(__name__)

plantillas_views_bp = Blueprint("plantillas_views", __name__, url_prefix="/plantilla")

@plantillas_views_bp.route("/<int:plantilla_id>")
def ver_plantilla(plantilla_id):
    """
    Renderiza una plantilla personalizada basada en los datos almacenados en la BD,
    cargando el archivo correcto según el nombre de la plantilla.
    """
    plantilla = PlantillaPersonalizada.query.get_or_404(plantilla_id)

    return render_template(
        f'plantilla/{plantilla.nombre_plantilla}/index.html',  # 📌 Ajuste de la ruta
        datos=plantilla.datos_json,  # 📌 Datos completos del usuario
        imagenes=plantilla.imagenes,  # 📌 Lista de imágenes
        videos=plantilla.videos,  # 📌 Lista de videos
        nombre_plantilla=plantilla.nombre_plantilla,  # 📌 Nombre de la plantilla
        url_final=plantilla.url_final,  # 📌 URL final donde se alojará la plantilla
        url_preview=plantilla.url_preview  # 📌 Vista previa de la plantilla
    )
