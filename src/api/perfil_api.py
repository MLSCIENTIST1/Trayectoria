import logging
import os
import requests
import json
from flask import Blueprint, request, jsonify, current_app
from src.models.plantilla_personalizada import PlantillaPersonalizada
from src.utils.ia_processor import generar_html_con_gemini  
from src.models.database import db

logger = logging.getLogger(__name__)

perfil_bp = Blueprint("perfil_api", __name__, url_prefix="/api/perfil")

@perfil_bp.route("/<int:id_usuario>", methods=["GET"])
def obtener_perfil(id_usuario):
    """
    Obtiene los datos del perfil/plantilla para un usuario específico.
    """
    logger.info(f"Attempting to fetch profile data for user {id_usuario}")

    plantilla = PlantillaPersonalizada.query.filter_by(id_usuario=id_usuario).first()

    if not plantilla:
        logger.warning(f"No template found for user {id_usuario}.")
        return jsonify({"error": "Plantilla not found for this user"}), 404

    # Prepare the data to be returned. Include fields needed by the frontend or render API.
    # Add more fields here if necessary.
    perfil_data = {
        "id_usuario": plantilla.id_usuario,
        "nombre_plantilla": plantilla.nombre_plantilla,
        "contenido_editado": plantilla.contenido_editado, # Include this to check if IA processing is pending
        "html_generado": plantilla.html_generado,
        "keywords": plantilla.keywords,
        "description": plantilla.description,
        "title": plantilla.title,
        "company_name": plantilla.company_name,
        "full_name": plantilla.full_name, # Mapped from 'author' by IA
        "email": plantilla.email,         # Mapped from 'contact_email' by IA
        # Add other relevant fields here, e.g., hero_title, about_heading, etc.
        # Based on the model, consider including:
        "phone": plantilla.phone,
        "hero_title": plantilla.hero_title,
        "hero_subtitle": plantilla.hero_subtitle,
        "contact_us_text": plantilla.contact_us_text,
        "about_heading": plantilla.about_heading,
        "about_description_1": plantilla.about_description_1,
        "about_description_2": plantilla.about_description_2,
        "read_more_text": plantilla.read_more_text,
        "about_you_description": plantilla.about_you_description,
        "imagenes": plantilla.imagenes, # JSON field
        "videos": plantilla.videos,   # JSON field
        "testimonials": plantilla.testimonials, # JSON field (mapped from testimonials_data)
        # Add other fields as needed for rendering the full template or UI
    }

    logger.info(f"Successfully fetched profile data for user {id_usuario}.")
    return jsonify(perfil_data), 200
