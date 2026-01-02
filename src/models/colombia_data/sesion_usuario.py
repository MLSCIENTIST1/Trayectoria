import secrets
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from src.models.database import db

class SesionUsuario(db.Model):
    __tablename__ = "sesion_usuario"

    id_sesion = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)  # 🔗 Relación con Usuario sin importar el módulo
    token_sesion = Column(String(255), unique=True, nullable=False, default=lambda: secrets.token_hex(32))  
    fecha_inicio = Column(DateTime, default=datetime.utcnow)  
    fecha_expiracion = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=7))  

    usuario = relationship("Usuario", back_populates="sesiones")  # ✅ Referencia con un string para evitar importaciones circulares

    def __repr__(self):
        return f"<SesionUsuario {self.token_sesion}>"
