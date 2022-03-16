from datetime import datetime
from sqlalchemy.orm import Session

from . import models, schemas

from security import utils as secu
import jwt

def crear_o_logear_usuario(db, google_jwt):
    usuario = jwt.decode(google_jwt, options={"verify_signature": False})
    has_usuario = (
        db.query(models.Usuario).filter(models.Usuario.username == usuario["email"]).first()
    )
    if has_usuario == None:
        nuevo_usuario = models.Usuario(
            username=usuario["email"],
            foto=usuario["picture"],
            nombre=usuario["name"],
            activo=True
        )
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        return nuevo_usuario
    else:
        return has_usuario


def get_usuario_by_username(db, username: str):
    usuario = (
        db.query(models.Usuario).filter(models.Usuario.username == username).first()
    )
    if usuario != None:
        return schemas.UsuarioEnDB(
            id= usuario.id ,username=usuario.username, hashed_password=usuario.password, activo=usuario.activo
        )


def cargar_resolucion(db : Session, resolucion: schemas.ResolucionCreate, id_usuario: str):
    
    nueva_resolucion = models.Resolucion(
            id_actividad= resolucion.id_actividad,
            resolucion= resolucion.resolucion,
            nombre_actividad= resolucion.nombre_actividad,
            fecha= datetime.now(),
            usuario_id= id_usuario
        )
    db.add(nueva_resolucion)
    db.commit()
    db.refresh(nueva_resolucion)
    return nueva_resolucion

def get_resoluciones(db: Session,params, usuario_id : int):
    
    query = db.query(models.Resolucion).filter(models.Resolucion.usuario_id == usuario_id)
    
    resoluciones = query.order_by(models.Resolucion.fecha.desc()).all()

    return resoluciones
