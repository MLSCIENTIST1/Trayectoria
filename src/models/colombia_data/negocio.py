import sqlalchemy as sa
from sqlalchemy.orm import relationship
from src.models.database import db
from datetime import datetime

class Negocio(db.Model):
    __tablename__ = 'negocios'

    id = sa.Column(sa.Integer, primary_key=True)
    nombre_negocio = sa.Column(sa.String(150), nullable=False)
    descripcion = sa.Column(sa.Text, nullable=True)
    direccion = sa.Column(sa.String(255), nullable=True)
    telefono = sa.Column(sa.String(20), nullable=True)
    categoria = sa.Column(sa.String(100), nullable=True) 
    
    # CLAVES FORÁNEAS (Deben apuntar a tablas existentes)
    ciudad_id = sa.Column(sa.Integer, sa.ForeignKey('colombia.ciudad_id'), nullable=False)
    usuario_id = sa.Column(sa.Integer, sa.ForeignKey('usuarios.id_usuario'), nullable=False)
    
    fecha_registro = sa.Column(sa.DateTime, default=datetime.utcnow)

    # RELACIONES CON MAPEO EXPLÍCITO (Solución al error del Mapeador)
    ciudad = relationship(
        "Colombia", 
        foreign_keys=[ciudad_id],
        backref="negocios_asociados"
    )
    
    # Aquí es donde fallaba: especificamos exactamente qué columnas unir
    dueno = relationship(
        "Usuario", 
        primaryjoin="Negocio.usuario_id == Usuario.id_usuario",
        backref="mis_negocios"
    )

    def serialize(self):
        return {
            "id": self.id,
            "nombre_negocio": self.nombre_negocio,
            "nombre_ciudad": self.ciudad.ciudad_nombre if self.ciudad else "No asignada",
            "fecha_registro": self.fecha_registro.strftime('%Y-%m-%d')
        }