import logging
import os
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from src.models.servicio import Servicio
from src.models.database import db

# Configurar logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Configuración de carga de archivos (ajusta según tu proyecto)
UPLOAD_FOLDER_TEMP = 'static/uploads/temp/'
UPLOAD_FOLDER_FINAL = 'static/uploads/final/'
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi'}

# Crear Blueprint para la funcionalidad de nuevo servicio
new_service_bp = Blueprint('new_service_bp', __name__)

# Función para validar archivos permitidos
def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@new_service_bp.route('/new_service_page', methods=['POST'])
@login_required
def new_service_page():
    """
    API para gestionar la creación de nuevos servicios y guardar archivos asociados.
    Permite la subida temporal de archivos y el registro de servicios.
    """
    logger.info("Procesando solicitud POST para nuevo servicio.")

    # Identificar si es un clic en "Guardar Archivos" o "Agregar Servicio"
    if 'guardar_archivos' in request.form:
        try:
            logger.debug("Intentando guardar archivos temporalmente...")
            archivos = request.files.getlist('files')
            if not archivos:
                logger.warning("No se cargaron archivos.")
                return jsonify({"error": "No se cargaron archivos."}), 400

            saved_files = []
            for archivo in archivos:
                if archivo.filename and allowed_file(archivo.filename, ALLOWED_IMAGE_EXTENSIONS.union(ALLOWED_AUDIO_EXTENSIONS, ALLOWED_VIDEO_EXTENSIONS)):
                    filename = secure_filename(archivo.filename)
                    file_path = os.path.join(UPLOAD_FOLDER_TEMP, filename)
                    archivo.save(file_path)
                    saved_files.append(file_path)

            logger.debug(f"Archivos guardados temporalmente: {saved_files}")
            return jsonify({"message": f"Archivos guardados temporalmente: {len(saved_files)}"}), 200

        except Exception as e:
            logger.exception("Error al guardar archivos temporalmente.")
            return jsonify({"error": "Ocurrió un error al guardar los archivos."}), 500

    elif 'agregar_servicio' in request.form:
        try:
            logger.debug("Intentando agregar un nuevo servicio...")

            # Obtener los datos del formulario
            nombre_servicio = request.form.get('nombre_servicio')
            descripcion = request.form.get('descripcion')
            categoria = request.form.get('categoria')
            precio_hora = request.form.get('precio_hora')
            etapas_calificacion = request.form.get('etapas_calificacion')
            viajar_dentro_pais = request.form.get('viajar_dentro_pais')
            viajar_fuera_pais = request.form.get('viajar_fuera_pais')
            domicilios = request.form.get('domicilios')
            incluye_asesoria = request.form.get('incluye_asesoria')
            requiere_presencia_cliente = request.form.get('requiere_presencia_cliente')
            experiencia_previa = request.form.get('experiencia_previa')
            facturacion_formal = request.form.get('facturacion_formal')
            modelos_negocio = ",".join(filter(None, [
                request.form.get('modelo_negocio1'),
                request.form.get('modelo_negocio2'),
                request.form.get('modelo_negocio3'),
                request.form.get('modelo_negocio4')
            ]))

            logger.debug(f"Datos recibidos para el nuevo servicio: {locals()}")

            # Validar los datos obligatorios
            if not nombre_servicio or not descripcion or not precio_hora or not etapas_calificacion:
                logger.warning("Faltan datos obligatorios en el formulario.")
                return jsonify({"error": "Por favor, completa todos los campos obligatorios."}), 400

            # Crear el nuevo servicio
            nuevo_servicio = Servicio(
                id_usuario=current_user.id_usuario,
                nombre_servicio=nombre_servicio,
                descripcion=descripcion,
                categoria=categoria,
                precio=float(precio_hora) if precio_hora else None,
                etapas_calificacion=int(etapas_calificacion),
                viajar_dentro_pais=True if viajar_dentro_pais == "sí" else False,
                viajar_fuera_pais=True if viajar_fuera_pais == "sí" else False,
                domicilios=True if domicilios == "sí" else False,
                incluye_asesoria=True if incluye_asesoria == "sí" else False,
                requiere_presencia_cliente=True if requiere_presencia_cliente == "sí" else False,
                experiencia_previa=True if experiencia_previa == "sí" else False,
                facturacion_formal=True if facturacion_formal == "sí" else False,
                modelos_negocio=modelos_negocio
            )
            db.session.add(nuevo_servicio)
            db.session.commit()

            logger.debug(f"Servicio creado exitosamente: {nuevo_servicio}")

            # Mover archivos de la carpeta temporal a la carpeta final
            temp_files = os.listdir(UPLOAD_FOLDER_TEMP)
            for file in temp_files:
                temp_file_path = os.path.join(UPLOAD_FOLDER_TEMP, file)
                final_file_path = os.path.join(UPLOAD_FOLDER_FINAL, file)
                os.rename(temp_file_path, final_file_path)

            logger.debug(f"Archivos movidos a la carpeta final: {temp_files}")
            return jsonify({"message": "Servicio agregado exitosamente con los archivos asociados."}), 200

        except Exception as e:
            db.session.rollback()
            logger.exception("Error al agregar servicio.")
            return jsonify({"error": "Hubo un error al agregar el servicio."}), 500

    return jsonify({"error": "Método no permitido."}), 405
