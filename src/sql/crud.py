from sqlalchemy.orm import Session

from . import models, schemas

from security import utils as secu
import jwt
""" <--- CRUD DE CLIENTES ---> """


def get_clientes(db: Session):
    return db.query(models.Cliente).all()


def get_cliente_by_id(db: Session, id_cliente: int):
    return db.query(models.Cliente).filter(models.Cliente.id == id_cliente).first()

def get_cliente_by_id_mp(db: Session, id_usuario_mp: str):
    return db.query(models.Cliente).filter(models.Cliente.id_mp == id_usuario_mp).first()


def get_cliente_by_nombre(db: Session, nombre_cliente: str):
    return (
        db.query(models.Cliente).filter(models.Cliente.nombre == nombre_cliente).first()
    )


def crear_cliente(db: Session, cliente: schemas.ClienteCreate, id_usuario_mp: str):
    nuevo_cliente = models.Cliente(
        id_mp=id_usuario_mp,
        nombre=cliente.nombre,
        public_key=cliente.public_key,
        access_token=cliente.access_token,
        url_exito=cliente.url_exito,
        url_pendiente=cliente.url_pendiente,
        url_error=cliente.url_error,
    )
    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)
    return nuevo_cliente


""" <--- CRUD DE PREFERENCIAS ---> """


def get_preferencia_by_id(db: Session, id_preferencia: int):
    return (
        db.query(models.Preferencia)
        .filter(models.Preferencia.id == id_preferencia)
        .first()
    )

def get_preferencia_by_mp_id(db: Session, id_preferencia_mp: str):
    return(
        db.query(models.Preferencia)
        .filter(models.Preferencia.id_preferencia_mp == id_preferencia_mp)
        .first()
    )


def crear_preferencia(db: Session, preferencia: schemas.PreferenciaCreate):
    nueva_preferencia = models.Preferencia(
        id_preferencia_mp=preferencia["id_preferencia_mp"],
        init_point=preferencia["init_point"],
        info_adicional=preferencia["additional_info"],
        id_cliente=preferencia["id_cliente"],
        created_at=preferencia["created_at"],
        estado="PENDIENTE",
    )
    db.add(nueva_preferencia)
    db.commit()
    db.refresh(nueva_preferencia)
    return nueva_preferencia


def crear_item_preferencia(
    db: Session, id_preferencia: int, item: schemas.ItemPreferenciaCreate
):
    nuevo_item_preferencia = models.ItemPreferencia(
        titulo=item.titulo,
        descripcion=item.descripcion,
        cantidad=item.cantidad,
        precio_unitario=item.precio_unitario,
        id_preferencia=id_preferencia,
    )
    db.add(nuevo_item_preferencia)
    db.commit()
    db.refresh(nuevo_item_preferencia)
    return nuevo_item_preferencia


def update_preferencia(db: Session, id_preferencia: int, estado: str):
    preferencia_a_actualizar = get_preferencia_by_id(db, id_preferencia)
    preferencia_a_actualizar.estado = estado
    db.commit()
    db.refresh(preferencia_a_actualizar)
    return preferencia_a_actualizar


""" <--- CRUD DE PAGOS ---> """


def crear_pago(db: Session, pago: schemas.PagoCreate):
    nuevo_pago = models.Pago(
        fecha_hora=pago["fecha_hora"],
        monto_abonado=pago["monto_abonado"],
        metodo_pago=pago["metodo_pago"],
        pagador_nombre=pago["pagador_nombre"],
        pagador_email=pago["pagador_email"],
        pagador_telefono=pago["pagador_telefono"],
        pagador_tipo_identificacion=pago["pagador_tipo_identificacion"],
        pagador_nro_identificacion=pago["pagador_nro_identificacion"],
        id_preferencia=pago["id_preferencia"],
        id_pago_mp=pago["id_pago_mp"],
    )
    db.add(nuevo_pago)
    db.commit()
    db.refresh(nuevo_pago)
    return nuevo_pago


def get_pago_by_id_mercadopago(db: Session, id_pago_mp: str):
    return db.query(models.Pago).filter(models.Pago.id_pago_mp == id_pago_mp).first()


""" <--- CRUD DE USUARIOS ---> """

def crear_usuario(db, usuario):
    nuevo_usuario = models.Usuario(
        username=usuario.username,
        foto=usuario.picture,
        nombre=usuario.name,
        activo=True
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario
    
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
            username=usuario.username, hashed_password=usuario.password, activo=usuario.activo
        )
