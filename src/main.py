import os

from dotenv import dotenv_values

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse

from jose import JWTError, jwt
from sql import models
from sql.database import engine
from sqlalchemy.orm import Session

from sql import crud, schemas
from sql.database import SessionLocal

from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

description = """
API correspondiente al cliente web de dehia

"""

app = FastAPI()

origins = [
    "*",
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
    "/resolucion",
    status_code=201,
    description="Carga la resolucion de una actividad",
    response_model=schemas.CrearResolucion,
    responses={
        500: {"model": schemas.MensajeError500},
        409: {"model": schemas.MensajeErrorGenerico},
    },
    tags=["Resolucion"],
)
def Cargar_Resolucion(
    resolucion: schemas.ResolucionCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):

    try:
        usuario = crud.crear_o_logear_usuario(db, token)
    except:
        return JSONResponse(
            status_code=401,
            content={
                "code": 401,
                "error": "Acceso no autorizado",
            },
        )

    try:
        # REQUEST A DEHIA
        
        # SE CARGO EXITOSAMENTE LO GUARDO LOCAL
        crud.cargar_resolucion(db, resolucion,usuario.id)
        
        return {
                "code": 201,
                "mensaje": "Resolucion registrada exitosamente"
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
    "/resolucion_anonima",
    status_code=201,
    description="Carga la resolucion de una actividad de usuario anonimo",
    response_model=schemas.CrearResolucion,
    responses={
        500: {"model": schemas.MensajeError500},
        409: {"model": schemas.MensajeErrorGenerico},
    },
    tags=["Resolucion"],
)
def Cargar_Resolucion_Anonima(
    resolucion: schemas.ResolucionCreate,
    db: Session = Depends(get_db)
):

    try:
        # REQUEST A DEHIA
        
        return {
                "code": 201,
                "mensaje": "Resolucion registrada exitosamente"
            }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "error": "Internal Server Error - Detalle: {0}".format(str(e)),
            },
        )

@app.get(
    "/resoluciones",
    response_model=schemas.GetResoluciones,
    description="Retorna todos las resoluciones del usuario",
    responses={500: {"model": schemas.MensajeError500}},
    tags=["Resolucion"],
)
async def Get_Resoluciones(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):

    try:
        usuario = crud.crear_o_logear_usuario(db, token)
    except:
        return JSONResponse(
            status_code=401,
            content={
                "code": 401,
                "error": "Acceso no autorizado",
            },
        )

    try:

        resoluciones = crud.get_resoluciones(db,request.query_params,usuario.id)

        return {
            "code": 200,
            "resoluciones": resoluciones
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "error": "Internal Server Error - Detalle: {0}".format(str(e)),
            },
        )

@app.get(
    "/resoluciones/{id_resolucion}",
    response_model=schemas.GetResolucion,
    description="Retorna una resolucion por id",
    responses={500: {"model": schemas.MensajeError500}},
    tags=["Resolucion"],
)
async def Get_Resolucion_By_ID(
    id_resolucion: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):

    try:
        crud.crear_o_logear_usuario(db, token)
    except:
        return JSONResponse(
            status_code=401,
            content={
                "code": 401,
                "error": "Acceso no autorizado",
            },
        )

    try:

        resolucion = crud.get_resolucion(db,id_resolucion)

        return {
            "code": 200,
            "resolucion": resolucion
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "error": "Internal Server Error - Detalle: {0}".format(str(e)),
            },
        )

