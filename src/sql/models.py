
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship, backref

from .database import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True)
    nombre = Column(String(255))
    foto = Column(String(255))
    activo = Column(Boolean, nullable=False)
    resoluciones = relationship( "Resolucion", back_populates="usuario")


class Resolucion(Base):
    __tablename__ = "resolucion"

    id = Column(Integer, primary_key=True, index=True)
    id_actividad = Column(Integer)
    resolucion = Column(String(8000))
    fecha = Column(DateTime)
    usuario_id = Column(Integer, ForeignKey('usuario.id'))
    usuario = relationship("Usuario", back_populates="resoluciones")





