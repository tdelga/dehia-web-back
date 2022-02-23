from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.expression import null

from .database import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True)
    nombre = Column(String(255))
    foto = Column(String(255))
    activo = Column(Boolean, nullable=False)


class Cliente(Base):
    __tablename__ = "cliente"

    id = Column(Integer, primary_key=True, index=True)
    id_mp = Column(String(255), unique=True)
    nombre = Column(String(255), unique=True, nullable=False)
    public_key = Column(String(255), nullable=False)
    access_token = Column(String(255), nullable=False)
    url_exito = Column(String(255), nullable=False)
    url_pendiente = Column(String(255))
    url_error = Column(String(255), nullable=False)
    preferencias = relationship("Preferencia", back_populates="cliente")


class Preferencia(Base):
    __tablename__ = "preferencia"

    id = Column(Integer, primary_key=True, index=True)
    id_preferencia_mp = Column(String(255), unique=True)
    init_point = Column(String(255), nullable=False)
    info_adicional = Column(String(255))
    id_cliente = Column(Integer, ForeignKey("cliente.id"))
    created_at = Column(DateTime, nullable=False)
    estado = Column(String(255), nullable=False)
    cliente = relationship("Cliente", back_populates="preferencias")
    items = relationship("ItemPreferencia", back_populates="preferencia")
    pago = relationship("Pago", back_populates="preferencia", uselist=False)


class ItemPreferencia(Base):
    __tablename__ = "item_preferencia"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255))
    descripcion = Column(String(255))
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    id_preferencia = Column(Integer, ForeignKey("preferencia.id"))
    preferencia = relationship("Preferencia", back_populates="items")


class Pago(Base):
    __tablename__ = "Pago"

    id = Column(Integer, primary_key=True, index=True)
    fecha_hora = Column(DateTime, nullable=False)
    monto_abonado = Column(Float, nullable=False)
    metodo_pago = Column(String(255))
    pagador_nombre = Column(String(255))
    pagador_email = Column(String(255))
    pagador_telefono = Column(String(255))
    pagador_tipo_identificacion = Column(String(255))
    pagador_nro_identificacion = Column(String(255))
    id_pago_mp = Column(String(255), nullable=False)
    id_preferencia = Column(Integer, ForeignKey("preferencia.id"))
    preferencia = relationship("Preferencia", back_populates="pago")
