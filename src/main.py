import os

from dotenv import dotenv_values

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from jose import JWTError, jwt
from sql import models
from sql.database import engine
from sqlalchemy.orm import Session

from sql import crud, schemas
from sql.database import SessionLocal

from security import utils

from datetime import timedelta, datetime
from fastapi.middleware.cors import CORSMiddleware

# models.Base.metadata.create_all(bind=engine)

description = """
Esta API es un Wrapper desarrollado por **Frontini & Asoc.** para la API de
MercadoPago

## Clientes

Los Clientes tienen las siguientes funcionalidades:

* **Crear un Cliente**.
* **Obtener todos los Clientes**.
* **Obtener las Preferencias de un Cliente**.
* **Obtener un Cliente en base a su ID** (_No implementado aún_).
* **Modificar a un Cliente** (_No implementado aún_).

## Preferencias

* **Crear una o varias preferencias en Batch**.

## Pagos

_Documentación en Desarrollo_

"""

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

BASEDIR = os.path.abspath(os.path.dirname("../"))

config = dotenv_values(os.path.join(BASEDIR, ".env"))

# Conexion con DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Funciones necesarias de Seguridad
models.Base.metadata.create_all(bind=engine)

async def get_usuario_actual(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    excepcion_credenciales = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, config["SECRET_KEY"], algorithms=[config["ALGORITHM"]]
        )
        username: str = payload.get("sub")
        if username is None:
            raise excepcion_credenciales
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise excepcion_credenciales
    user = crud.get_usuario_by_username(db, username=token_data.username)
    if user is None:
        raise excepcion_credenciales
    return user


async def get_usuario_actual_activo(
    usuario_actual: schemas.Usuario = Depends(get_usuario_actual),
):
    if not usuario_actual.activo:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return usuario_actual


# Endpoints de Seguridad


@app.post(
    "/login",
    tags=["Seguridad"],
)
async def Login(
    payload: schemas.PayloadLogin,
    db: Session = Depends(get_db), 
):


    usuario = crud.crear_o_logear_usuario(db, payload.google_jwt)
    return {"access_token": payload.google_jwt, "token_type": usuario}

    # user = utils.autentificar_usuario(db, username, password)
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Usuario o contraseña incorrecta",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    # access_token_expires = timedelta(minutes=int(config["ACCESS_TOKEN_EXPIRE_MINUTES"]))
    # access_token = utils.crear_token_acceso(
    #     data={"sub": user.username}, expires_delta=access_token_expires
    # )
    # return {"access_token": access_token, "token_type": "bearer"}

@app.post(
    "/usuarios/crear",
    status_code=201,
    description="Crea un nuevo Usuario",
    response_model=schemas.CrearUsuario,
    responses={
        500: {"model": schemas.MensajeError500},
        409: {"model": schemas.MensajeErrorGenerico},
    },
    tags=["Seguridad"],
)
def Registrar_Nuevo_Usuario(
    usuario: schemas.UsuarioCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    try:
        if crud.get_usuario_by_username(db, usuario.username) == None:
            crud.crear_usuario(db, usuario)
            return {
                "code": 201,
                "mensaje": "Usuario creado exitosamente",
            }
        else:
            return JSONResponse(
                status_code=409,
                content={
                    "code": 409,
                    "error": "Duplicate - Ese Username ya corresponde a un Usuario registrado",
                },
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "error": "Internal Server Error - Detalle: {0}".format(str(e)),
            },
        )


# Endpoints de Clientes


@app.get(
    "/clientes/",
    response_model=schemas.GetClientes,
    description="Retorna todos los clientes registrados hasta el momento",
    responses={500: {"model": schemas.MensajeError500}},
    tags=["Clientes"],
)
def Get_Clientes_Registrados(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    try:
        clientes = crud.get_clientes(db)
        return {"code": 200, "clientes": clientes}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "error": "Internal Server Error - Detalle: {0}".format(str(e)),
            },
        )


@app.get(
    "/clientes/{id_cliente}",
    response_model=schemas.GetPreferenciasCliente,
    description="Retorna la información del cliente junto con sus preferencias",
    responses={
        500: {"model": schemas.MensajeError500},
        404: {"model": schemas.MensajeError404},
    },
    tags=["Clientes"],
)
def Get_Preferencias_Clientes(
    id_cliente: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    try:
        cliente = crud.get_cliente_by_id(db, id_cliente)
        if cliente == None:
            return JSONResponse(
                status_code=404,
                content={
                    "code": 404,
                    "error": "Not Found - Ese ID no corresponde a un Cliente registrado",
                },
            )
        else:
            return {
                "code": 200,
                "cliente": cliente,
                "preferencias": cliente.preferencias,
            }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "error": "Internal Server Error - Detalle: {0}".format(str(e)),
            },
        )


@app.post(
    "/clientes/crear",
    status_code=201,
    description="Crea un nuevo cliente",
    response_model=schemas.CrearCliente,
    responses={
        500: {"model": schemas.MensajeError500},
        409: {"model": schemas.MensajeErrorGenerico},
    },
    tags=["Clientes"],
)
def Crear_Nuevo_Cliente(
    cliente: schemas.ClienteCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    try:
        if crud.get_cliente_by_nombre(db, cliente.nombre) == None:
            import mercadopago
            sdk = mercadopago.SDK(cliente.access_token)
            userInfo = sdk.user().get()
            nuevo_cliente = crud.crear_cliente(db, cliente, userInfo["response"]["id"])
            return {
                "code": 201,
                "mensaje": "Cliente creado exitosamente",
                "cliente": nuevo_cliente,
            }
        else:
            return JSONResponse(
                status_code=409,
                content={
                    "code": 409,
                    "error": "Duplicate - Ese nombre ya corresponde a un Cliente registrado",
                },
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "error": "Internal Server Error - Detalle: {0}".format(str(e)),
            },
        )


# Endpoints de Preferencias


@app.get(
    "/preferencias/{id_preferencia_mp}",
    status_code=200,
    description="Obtiene el detalle de una Preferencia en base a su ID en Mercado Pago",
    response_model=schemas.GetPreferenciaResponse,
    responses={
        404: {"model": schemas.MensajeError404},
        500: {"model": schemas.MensajeError500}
    },
    tags=["Preferencias"]
)
def Get_Preferencia(
    id_preferencia_mp: str,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):

    try:
        preferencia = crud.get_preferencia_by_mp_id(db, id_preferencia_mp)
        if preferencia == None:
            return JSONResponse(
                status_code=404,
                content={
                    "code": 404,
                    "error": "Not Found - Ese ID no corresponde a una Preferencia existente",
                },
            )  
        return {
                "code":200,
                "preferencia":preferencia,
                "pago_preferencia":preferencia.pago
            }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "error": "Internal Server Error - Detalle: {0}".format(str(e)),
            },
        )



@app.post(
    "/preferencias/crear/{id_cliente}",
    status_code=201,
    description="Crea nuevas preferencias en base a datos básicos que se envían en el body",
    response_model=schemas.CrearPreferenciaResponse,
    responses={
        404: {"model": schemas.MensajeError404},
        500: {"model": schemas.MensajeError500},
    },
    tags=["Preferencias"],
)
def Crear_Preferencias_De_Cliente(
    id_cliente: int,
    payload: schemas.PayloadPreferenciaCrear,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    import mercadopago

    try:
        cliente = crud.get_cliente_by_id(db, id_cliente)
        if cliente == None:
            return JSONResponse(
                status_code=404,
                content={
                    "code": 404,
                    "error": "Not Found - Ese ID no corresponde a un Cliente registrado",
                },
            )
        sdk = mercadopago.SDK(cliente.access_token)
        items_parsed = []
        for item in payload.items:
            items_parsed.append(
                {
                    "title": item.titulo,
                    "description": item.descripcion,
                    "quantity": item.cantidad,
                    "unit_price": item.precio_unitario,
                }
            )
        preference_data = {
            "additional_info": payload.info_adicional,
            "statement_descriptor": cliente.nombre,
            "items": items_parsed,
            "back_urls":{
                "success":cliente.url_exito,
                "pending":cliente.url_pendiente,
                "failure":cliente.url_error,
            }
        }
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]
        nueva_preferencia = {}
        nueva_preferencia["estado"] = "PENDIENTE"
        nueva_preferencia["additional_info"] = preference["additional_info"]
        nueva_preferencia["id_preferencia_mp"] = preference["id"]
        nueva_preferencia["init_point"] = preference["init_point"]
        nueva_preferencia["id_cliente"] = id_cliente
        nueva_preferencia["created_at"] = preference["date_created"]
        nueva_preferencia = crud.crear_preferencia(db, nueva_preferencia)
        preference_response = sdk.preference().update(
            preference["id"], {"external_reference": nueva_preferencia.id}
        )
        for item in payload.items:
            crud.crear_item_preferencia(db, nueva_preferencia.id, item)
        nueva_preferencia = crud.get_preferencia_by_id(db, nueva_preferencia.id)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "error": "Internal Server Error - Detalle: {0}".format(str(e)),
            },
        )

    return {
        "code": 201,
        "mensaje": "Preferencia creada exitosamente",
        "cliente": cliente,
        "preferencia": nueva_preferencia,
    }


# Endpoints de Pagos

@app.get(
    "/pagos/{id_pago_mp}",
    status_code=200,
    description="Obtiene el detalle del Pago en base a su ID en Mercado Pago",
    response_model=schemas.GetPagoResponse,
    responses={
        404: {"model": schemas.MensajeError404},
        500: {"model": schemas.MensajeError500},
    },
    tags=["Pagos"]
)
def Get_Pago(
    id_pago_mp: str,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):

    try:
        pago = crud.get_pago_by_id_mercadopago(db, id_pago_mp)
        if pago == None:
            return JSONResponse(
                status_code=404,
                content={
                    "code": 404,
                    "error": "Not Found - Ese ID no corresponde a un Pago existente",
                },
            )
        return {
            "code": 200,
            "pago": pago
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "error": "Internal Server Error - Detalle: {0}".format(str(e)),
            },
        )


@app.post(
    "/pagos/notificar",
    status_code=200,
    description="URL para procesar las notificaciones de pago de Mercado Pago",
    response_model=schemas.ResponseNotificacionMP,
    tags=["Pagos"],
)
def Notificar_Pagos_Mercado_Pago(
    payload: schemas.PayloadNotificacionMP, db: Session = Depends(get_db)
):
    if payload.action == "payment.created":
        import mercadopago
        cliente = crud.get_cliente_by_id_mp(db, str(payload.user_id))
        sdk = mercadopago.SDK(cliente.access_token)
        pago = sdk.payment().get(payload.data["id"])
        response = pago["response"]
        if crud.get_pago_by_id_mercadopago(db, response["id"]) == None:
            if (
                pago["response"]["status"] == "approved"
                and pago["response"]["status_detail"] == "accredited"
            ):
                payload_pago = {
                    "fecha_hora": response["date_approved"],
                    "monto_abonado": response["transaction_amount"],
                    "metodo_pago": response["payment_method_id"]
                    + "-"
                    + response["payment_type_id"],
                    "pagador_nombre": response["payer"]["first_name"]
                    + " "
                    + response["payer"]["last_name"]
                    if response["payer"]["first_name"] != None
                    else None,
                    "pagador_email": response["payer"]["email"],
                    "pagador_telefono": response["payer"]["phone"]["area_code"]
                    + response["payer"]["phone"]["number"]
                    if response["payer"]["phone"]["number"] != None
                    else None,
                    "pagador_tipo_identificacion": response["payer"]["identification"][
                        "type"
                    ],
                    "pagador_nro_identificacion": response["payer"]["identification"][
                        "number"
                    ],
                    "id_preferencia": response["external_reference"],
                    "id_pago_mp": response["id"],
                }
                crud.crear_pago(db, payload_pago)
                crud.update_preferencia(db, payload_pago["id_preferencia"], "PAGADO")

    return {"code": 200, "response_payload": payload}
