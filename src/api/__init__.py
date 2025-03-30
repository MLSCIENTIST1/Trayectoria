
from flask import Blueprint , jsonify
from src.api.get_name_services_api import obtener_nombre_servicios_bp  # Importar los Blueprints
from src.api.get_resultado_filtro_servicio_api import obtener_servicios_bp
from src.api.get_name_cities_api import obtener_nombre_ciudades_bp
from src.api.post_register_api import post_register_api_bp
from src.api.auth_api import auth_api_bp
from src.api.calificar_api import calificar_bp
from src.api.rate_contratante_api import rate_contratante_bp
from src.api.rate_contratado_api import rate_contratado_bp
from src.api.calificaciones_recibidas_contratante_api import calificaciones_recibidas_bp
from src.api.calificaciones_recibidas_contratado_api import calificaciones_contratado_bp
from src.api.contratos_vigentes_roles_api import contratos_vigentes_roles_bp
from src.api.new_service_page_api import new_service_bp
from src.api.delete_other_service_api import delete_service_bp
from src.api.delete_principal_service_api import delete_principal_service_bp
from src.api.delete_principal_service_api import delete_principal_service_bp
from src.api.edit_service_page_api import edit_service_page_bp
from src.api.offered_service_page_api import offered_service_page_bp
from src.api.service_count_offered_api import service_count_offered_bp
from src.api.vigent_contracts_api import vigent_contracts_bp
from src.api.total_services_api import total_services_bp
from src.api.loged_api import loged_bp
from src.api.index_api import index_bp
from src.api.logout_api import logout_bp
from src.api.editando_api import editando_bp
from src.api.edit_profile_api import edit_profile_bp
from src.api.logic_delete_user_api import logic_delete_user_bp
from src.api.chat_api import chat_bp
from src.api.more_details_api import more_details_bp
from src.api.reject_notification_api import reject_notification_bp
from src.api.create_service_from_notification_api import create_service_bp
from src.api.accept_notification_api import accept_notification_bp
from src.api.show_notifications_api import show_notifications_bp
from src.api.detalle_candidato_api import detalle_candidato_bp
from src.api.search_results_api import search_results_bp
from src.api.notifications_api import notifications_bp



# Crear el Blueprint principal
api_bp = Blueprint('api', __name__)




#despues del test calificar
api_bp.register_blueprint(calificar_bp, url_prefix='/calificar')
#GET http://localhost:5000/api/calificar/<servicio_id>

api_bp.register_blueprint(rate_contratante_bp, url_prefix='/rate_contratante')
#POST http://localhost:5000/api/rate_contratante/<servicio_id>

api_bp.register_blueprint(rate_contratado_bp, url_prefix='/rate_contratado')
#POST http://localhost:5000/api/rate_contratado/<servicio_id>

api_bp.register_blueprint(calificaciones_recibidas_bp, url_prefix='/calificaciones_recibidas')
#GET http://localhost:5000/api/calificaciones_recibidas/contratante

api_bp.register_blueprint(calificaciones_contratado_bp, url_prefix='/calificaciones_recibidas')
#GET http://localhost:5000/api/calificaciones_recibidas/contratado

api_bp.register_blueprint(contratos_vigentes_roles_bp, url_prefix='/contratos')
#GET http://localhost:5000/api/contratos/contratos_vigentes_roles

api_bp.register_blueprint(new_service_bp, url_prefix='/services')
#POST http://localhost:5000/api/services/new_service_page

api_bp.register_blueprint(delete_service_bp, url_prefix='/services')
#DELETE http://localhost:5000/api/services/delete_other_service/<service_id>

api_bp.register_blueprint(delete_principal_service_bp, url_prefix='/services')
#DELETE http://localhost:5000/api/services/delete_principal_service

api_bp.register_blueprint(delete_principal_service_bp, url_prefix='/services')
#DELETE http://localhost:5000/api/services/delete_principal_service

api_bp.register_blueprint(edit_service_page_bp, url_prefix='/services')
#GET http://localhost:5000/api/services/edit_service_page

api_bp.register_blueprint(offered_service_page_bp, url_prefix='/services')
#api_bp.register_blueprint(offered_service_page_bp, url_prefix='/services')

api_bp.register_blueprint(service_count_offered_bp, url_prefix='/services')
#GET http://localhost:5000/api/services/offered_service

api_bp.register_blueprint(vigent_contracts_bp, url_prefix='/contracts')
#GET http://localhost:5000/api/contracts/vigent_contracts/<role>

api_bp.register_blueprint(dashboard_bp, url_prefix='/dashboard')
#GET http://localhost:5000/api/dashboard

api_bp.register_blueprint(total_services_bp, url_prefix='/services')
#GET http://localhost:5000/api/services/total_services

api_bp.register_blueprint(loged_bp, url_prefix='/user')
#GET http://localhost:5000/api/user/loged

api_bp.register_blueprint(index_bp, url_prefix='/')
#http://localhost:5000/api/

api_bp.register_blueprint(logout_bp, url_prefix='/auth')
#POST http://localhost:5000/api/auth/logout

api_bp.register_blueprint(password_bp, url_prefix='/password')
#POST http://localhost:5000/api/password/hash_password

api_bp.register_blueprint(editando_bp, url_prefix='/profile')
#GET http://localhost:5000/api/profile/loged

api_bp.register_blueprint(edit_profile_bp, url_prefix='/profile')
#GET http://localhost:5000/api/profile/edit

api_bp.register_blueprint(logic_delete_user_bp, url_prefix='/profile')
#POST http://localhost:5000/api/profile/logic_delete_user

api_bp.register_blueprint(chat_bp, url_prefix='/notifications')
#GET http://localhost:5000/api/notifications/notification/<notification_id>/chat

api_bp.register_blueprint(more_details_bp, url_prefix='/notifications')
#api_bp.register_blueprint(more_details_bp, url_prefix='/notifications')

api_bp.register_blueprint(reject_notification_bp, url_prefix='/notifications')
#POST http://localhost:5000/api/notifications/notification/<notification_id>/reject

api_bp.register_blueprint(create_service_bp, url_prefix='/notifications')
#POST http://localhost:5000/api/notifications/notification/<notification_id>/create_service

api_bp.register_blueprint(accept_notification_bp, url_prefix='/notifications')
#POST http://localhost:5000/api/notifications/notification/<notification_id>/accept

api_bp.register_blueprint(show_notifications_bp, url_prefix='/notifications')
#GET http://localhost:5000/api/notifications

api_bp.register_blueprint(search_results_bp, url_prefix='/api')
#GET http://localhost:5000/api/search/resultado_filtro_primera_busqueda?ciudad=Bogotá&labor=Electricista

api_bp.register_blueprint(detalle_candidato_bp, url_prefix='/candidatos')
#GET http://localhost:5000/api/candidatos/detalle_candidato/<id_usuario>

api_bp.register_blueprint(notifications_bp, url_prefix='/api')
#POST http://localhost:5000/api/notifications/<candidato_id>
































# Aquí se agregarán los controladores convertidos a APIs según los listados en la imagen

from src.api.chat_api import chat_bp
from src.api.dashboard_api import dashboard_bp
from src.api.loged_api import loged_bp
from src.api.password_api import password_bp
from src.api.profile_api import profile_bp
from src.api.recive_notifications_api import recive_notifications_bp
from src.api.search_api import search_bp
from src.api.send_api import notifications_bp
from src.api.prueba_api import prueba_bp





# Registrar los Blueprints de los controladores convertidos a APIs
api_bp.register_blueprint(obtener_nombre_servicios_bp)
api_bp.register_blueprint(obtener_servicios_bp)
api_bp.register_blueprint(obtener_nombre_ciudades_bp)
api_bp.register_blueprint(post_register_api_bp)
api_bp.register_blueprint(auth_api_bp)

# Registrar los Blueprints según la imagen
api_bp.register_blueprint(calificar_bp)
api_bp.register_blueprint(chat_bp)
api_bp.register_blueprint(dashboard_bp)
api_bp.register_blueprint(loged_bp)
api_bp.register_blueprint(password_bp)
api_bp.register_blueprint(profile_bp)
api_bp.register_blueprint(recive_notifications_bp)
api_bp.register_blueprint(search_bp)
api_bp.register_blueprint(notifications_bp)
api_bp.register_blueprint(prueba_bp)