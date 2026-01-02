import logging
from flask import Blueprint, request, jsonify
from src.models.database import db
from src.models.plantilla_personalizada import PlantillaPersonalizada

logger = logging.getLogger(__name__)

plantillas_bp = Blueprint("plantillas_api", __name__, url_prefix="/plantillas")

@plantillas_bp.route("/crear", methods=["POST"])
def crear_plantilla():
    """
    Crea una nueva plantilla personalizada a partir de los datos enviados por el usuario.
    """
    data = request.json
    if not data or "nombre_plantilla" not in data or "id_usuario" not in data or "datos" not in data:
        return jsonify({"error": "Datos insuficientes"}), 400

    nueva_plantilla = PlantillaPersonalizada(
        id_usuario=data["id_usuario"],
        nombre_plantilla=data["nombre_plantilla"],
        datos_json=data["datos"],
        imagenes=data.get("imagenes", []),  # 📌 Lista de imágenes (si se envían)
        videos=data.get("videos", []),  # 📌 Lista de videos (si se envían)
        url_preview=f"https://mitrayectoria.web.app/previews/{data['id_usuario']}/{data['nombre_plantilla']}.png",
        url_final=f"https://mitrayectoria.web.app/{data['id_usuario']}/{data['nombre_plantilla']}"
    )

    try:
        db.session.add(nueva_plantilla)
        db.session.commit()
        return jsonify({"mensaje": "Plantilla creada exitosamente", "id": nueva_plantilla.id}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear la plantilla: {e}", exc_info=True)
        return jsonify({"error": "Error al guardar la plantilla en la base de datos"}), 500

@plantillas_bp.route("/editar/<int:plantilla_id>", methods=["PUT"])
def editar_plantilla(plantilla_id):
    """
    Edita los datos de una plantilla personalizada existente.
    """
    plantilla = PlantillaPersonalizada.query.get_or_404(plantilla_id)
    data = request.json
    if not data or "datos" not in data:
        return jsonify({"error": "Faltan los datos para editar la plantilla"}), 400

    try:
        plantilla.datos_json = data["datos"]
        plantilla.imagenes = data.get("imagenes", plantilla.imagenes)
        plantilla.videos = data.get("videos", plantilla.videos)
        db.session.commit()
        return jsonify({"mensaje": "Plantilla editada exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al editar la plantilla {plantilla_id}: {e}", exc_info=True)
        return jsonify({"error": "Error al actualizar la plantilla en la base de datos"}), 500

@plantillas_bp.route("/buscar", methods=["GET"])
def buscar_plantillas():
    """
    Devuelve una lista de plantillas disponibles con sus vistas previas.
    """
    id_usuario = request.args.get("id_usuario")
    if not id_usuario:
        return jsonify({"error": "Falta id_usuario"}), 400

    plantillas = PlantillaPersonalizada.query.filter_by(id_usuario=id_usuario).all()
    resultado = [
        {
            "id": p.id,  # Necesitamos el ID para el enlace de edición
            "nombre": p.nombre_plantilla,
            "url_preview": p.url_preview,
            "url_final": p.url_final,
            "imagenes": p.imagenes,
            "videos": p.videos
        }
        for p in plantillas
    ]

    return jsonify(resultado), 200