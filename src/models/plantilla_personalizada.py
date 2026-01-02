from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from src.models.database import db

from src.models.colombia_data.ratings.service_ratings import ServiceRatings  # Assuming ServiceRatings is in this path
class PlantillaPersonalizada(db.Model):
    __tablename__ = "plantilla_personalizada"

    id = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)

    # Template seleccionado
    nombre_plantilla = Column(String(100), nullable=False)

    # Meta datos
    keywords = Column(String(255), default="")
    description = Column(Text, default="")
    title = Column(String(100), default="")

    # Datos generales
    company_name = Column(String(100), default="")
    home_url = Column(String(255), default="")
    about_url = Column(String(255), default="")
    product_url = Column(String(255), default="")
    client_url = Column(String(255), default="")
    contact_url = Column(String(255), default="")

    # Información Personal
    full_name = Column(String(100), default="")
    birthday_day = Column(String(2), default="")
    birthday_month = Column(String(2), default="")
    birthday_year = Column(String(4), default="")
    address = Column(String(255), default="")
    courses = Column(String(255), default="")
    business_description = Column(Text, default="") # Candidato para IA content_editado

    # Redes Sociales
    facebook_link = Column(String(255), default="")
    instagram_link = Column(String(255), default="")
    other_social_media = Column(String(255), default="")

    # Hero section
    hero_title = Column(String(150), default="")
    hero_subtitle = Column(String(255), default="")

    # Products Section
    products_heading = Column(String(150), default="")
    products_see_more_text = Column(String(50), default="")
    contact_us_text = Column(String(100), default="")

    # About Us
    about_heading = Column(String(150), default="")
    about_description_1 = Column(Text, default="")
    about_description_2 = Column(Text, default="")
    read_more_text = Column(String(50), default="")
    about_you_description = Column(Text, default="") # Added based on form field aboutYouDescription

    # Portfolio Services
    portfolio_service_1_name = Column(String(150), default="")
    portfolio_service_1_short_phrase = Column(String(255), default="")
    portfolio_service_1_description = Column(Text, default="")
    portfolio_service_2_name = Column(String(150), default="")
    portfolio_service_2_short_phrase = Column(String(255), default="")
    portfolio_service_2_description = Column(Text, default="")
    portfolio_service_3_name = Column(String(150), default="")
    portfolio_service_3_short_phrase = Column(String(255), default="")
    portfolio_service_3_description = Column(Text, default="")
    additional_portfolio_service = Column(Text, default="") # Text for additional requests

    # Contact Information
    email = Column(String(100), default="")
    phone = Column(String(50), default="")
    # Preferencias de color y feedback
    have_color_palette = Column(Boolean, default=False)
    suggest_color_palette = Column(Boolean, default=False)
    color_palette_choice = Column(String(50), default="")
    feedback = Column(Text, default="")
    domain_agreement = Column(String(50), default="")
    referrals = Column(Integer, default=0)

    # Multimedia
    imagenes = Column(JSON, default={})  # 📌 Evita valores `None`
    videos = Column(JSON, default={})  # 📌 Evita valores `None`

    # URLs de la página personalizada
    url_preview = Column(String(255), unique=True, nullable=False)
    url_final = Column(String(255), unique=True, nullable=False)

    # 🔗 **Datos normalizados de `ServiceRatings`**
    puntaje_promedio = Column(Integer, nullable=True)
    comentarios_general = Column(JSON, default={})  # 📌 Evita valores `None`

    # Contenido procesado por IA
    contenido_editado = Column(Text, nullable=True)  
    html_generado = Column(Text, nullable=True)

    # Relación con `Usuario`
    usuario = relationship("Usuario", back_populates="plantillas", lazy="joined")

    # Relación con `ServiceRatings`
    calificaciones = relationship("ServiceRatings", back_populates="plantilla", lazy="joined", foreign_keys=[ServiceRatings.plantilla_id])
