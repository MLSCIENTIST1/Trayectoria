import bcrypt
from sqlalchemy import Column, Integer, String, BigInteger, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from src.models.database import db
from src.models.servicio import Servicio
from src.models.usuario_servicio import usuario_servicio
from src.models.colombia_data.sesion_usuario import SesionUsuario  # ✅ Ajustada la importación desde `colombia_data`

class Usuario(db.Model):
    __tablename__ = "usuario"

    # Definición de columnas
    id_usuario = Column(Integer, primary_key=True)
    ciudad_id = Column(Integer, ForeignKey("colombia.ciudad_id"), nullable=False)
    ciudad = Column(String, nullable=False)
    nombre = Column(String, nullable=False)
    apellidos = Column(String, nullable=False)
    correo = Column(String, nullable=False, unique=True)
    contrasenia = Column(String, nullable=False)
    profesion = Column(String, nullable=False)
    cedula = Column(BigInteger, nullable=False, unique=True)
    celular = Column(BigInteger, nullable=False)

    active = Column(Boolean, default=True)
    pais_id = Column(Integer, nullable=True)
    validate = Column(Boolean, nullable=True, default=False)
    black_list = Column(Boolean, nullable=True, default=False)

    # ✅ Relación con `SesionUsuario`, ajustando la referencia al módulo correcto
    sesiones = relationship("SesionUsuario", back_populates="usuario", cascade="all, delete-orphan")

    # Relaciones existentes
    sent_notifications = relationship("Notification", foreign_keys="[Notification.sender_id]", back_populates="sender")
    received_notifications = relationship("Notification", foreign_keys="[Notification.user_id]", back_populates="receiver")
    received_feedbacks = relationship("Feedback", back_populates="usuario", cascade="all, delete-orphan", lazy="dynamic")
    monetizaciones = relationship("MonetizationManagement", back_populates="usuario", cascade="all, delete-orphan")
    calificaciones = relationship("ServiceRatings", back_populates="usuario", cascade="all, delete-orphan")
    plantillas = relationship("PlantillaPersonalizada", back_populates="usuario", cascade="all, delete-orphan")

    servicios = relationship("Servicio", secondary=usuario_servicio, back_populates="usuarios", lazy="select")
    servicios_como_contratante = relationship("Servicio", foreign_keys="[Servicio.id_contratante]", back_populates="contratante")
    servicios_como_contratado = relationship("Servicio", foreign_keys="[Servicio.id_contratado]", back_populates="contratado")

    def __init__(self, nombre, apellidos, correo, profesion, cedula, celular, ciudad_id, ciudad):
        self.nombre = nombre
        self.apellidos = apellidos
        self.correo = correo
        self.profesion = profesion
        self.cedula = cedula
        self.celular = celular
        self.ciudad_id = ciudad_id
        self.ciudad = ciudad

    # Métodos para manejar contraseñas
    def set_password(self, password):
        salt = bcrypt.gensalt()
        self.contrasenia = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def check_password(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.contrasenia.encode("utf-8"))

    def get_id(self):
        return str(self.id_usuario)

    def __repr__(self):
        return f"<Usuario {self.correo}>"
