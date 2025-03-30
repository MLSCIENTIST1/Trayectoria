import logging
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from src.models.database import db
from src.forms.forms import EditProfileForm

# Configurar logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Crear Blueprint para la funcionalidad de edición de perfil
edit_profile_bp = Blueprint('edit_profile_bp', __name__)

@edit_profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile_api():
    """
    API para editar el perfil del usuario logueado.
    En el método GET, devuelve los datos del usuario actual en formato JSON.
    En el método POST, actualiza los datos del usuario y devuelve una confirmación.
    """
    if request.method == 'GET':
        logger.info(f"Procesando solicitud GET para obtener datos de perfil del usuario {current_user.id_usuario}.")

        try:
            # Obtener datos básicos del usuario actual
            usuario_data = {
                "nombre": current_user.nombre,
                "apellidos": current_user.apellidos,
                "celular": current_user.celular,
                "ciudad": current_user.ciudad
            }
            logger.debug(f"Datos del usuario obtenidos: {usuario_data}")

            return jsonify({"usuario": usuario_data}), 200

        except Exception as e:
            logger.exception("Error al obtener los datos del usuario.")
            return jsonify({"error": "Hubo un problema al obtener los datos del usuario."}), 500

    elif request.method == 'POST':
        logger.info(f"Procesando solicitud POST para actualizar datos del usuario {current_user.id_usuario}.")

        try:
            # Crear formulario con los datos recibidos
            data = request.get_json()
            logger.debug(f"Datos recibidos: {data}")
            form = EditProfileForm(data=data, obj=current_user)

            # Validar el formulario
            if form.validate():
                # Actualizar los datos del usuario
                current_user.nombre = form.nombre.data
                current_user.apellidos = form.apellidos.data
                current_user.celular = form.celular.data
                current_user.ciudad = form.ciudad.data
                db.session.commit()
                logger.info("Perfil actualizado correctamente.")
                return jsonify({"message": "Perfil actualizado correctamente."}), 200
            else:
                logger.warning(f"Errores de validación en el formulario: {form.errors}")
                return jsonify({"error": "Errores en los datos proporcionados.", "form_errors": form.errors}), 400

        except Exception as e:
            logger.exception("Error al actualizar los datos del usuario.")
            return jsonify({"error": "Hubo un problema al actualizar el perfil."}), 500
