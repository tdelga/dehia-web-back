import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

""" <--- SCHEMAS DE MENSAJES DE ERROR ---> """

class MensajeError500(BaseModel):
    code: int = Field(500, const=True, title="Código de respuesta", example=500)
    error: str = Field(
        None,
        title="Mensaje descriptivo del error",
        example="Internal Server Error - Detalle: [Detalle_Del_Error]",
    )


class MensajeError404(BaseModel):
    code: int = Field(404, const=True, title="Código de respuesta", example=404)
    error: str = Field(
        None,
        title="Mensaje descriptivo del error",
        example="Not Found - [Detalle del Error]",
    )


class MensajeErrorGenerico(BaseModel):
    code: int = Field(
        None, ge=400, le=409, title="Código de respuesta", example="[400 .. 409]"
    )
    error: str = Field(
        None,
        title="Mensaje descriptivo del error",
        example="Error: [Detalle del Error]",
    )

class CrearUsuario(BaseModel):
    code: int = Field(201, const=True, title="Código de respuesta", example=201)
    mensaje: str = "Usuario creado exitosamente"

class CrearResolucion(BaseModel):
    code: int = Field(201, const=True, title="Código de respuesta", example=201)
    mensaje: str = "Resolucion registrada exitosamente"
    

""" <--- SCHEMAS DE USUARIO Y SEGURIDAD ---> """


class Token(BaseModel):
    access_token: str = Field(
        ...,
        title="JWT Token válido",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9[...]",
    )
    token_type: str = Field(..., title="El tipo de Token", example="Bearer")

class Resolucion(BaseModel):
    id_actividad: str = Field(..., title="ID de la actividad", example="1")
    resolucion: str = Field(..., title="Resolucion de la actividad", example="1")

class ResolucionGet(Resolucion):
    fecha: datetime.datetime  = Field(..., title="Fecha resolucion de la actividad", example="2021-08-19")

    class Config:
        orm_mode = True

class GetResoluciones(BaseModel):
    code: int = Field(200, const=True, title="Código de respuesta", example=200)
    resoluciones: List[ResolucionGet]

    class Config:
        orm_mode = True


class TokenData(BaseModel):
    username: Optional[str] = None


class Usuario(BaseModel):
    id: str = Field(
        ...,
        title="ID de Usuario",
        example="1"
    )
    username: str = Field(
        ...,
        title="Nombre de Usuario",
        example="Usuario_Test"
    )
    activo: bool = Field(
        ...,
        title="Booleando que indica si el usuario está activo o no",
        example=True
    )

class UsuarioCreate(Usuario):
    password: str = Field(
        ...,
        title="Password en texto plano que luego será hasheada",
        example="La_mejor_password_del_mund0!!"
    )

class ResolucionCreate(Resolucion):
    pass


class UsuarioEnDB(Usuario):
    hashed_password: str

# Make a Schema named PayloadLogin that has 3 parameters: username, password and google_jwt. All of the parameters are strings
class PayloadLogin(BaseModel):

    google_jwt: str = Field(
        ...,
        title="JWT Token de Google",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9[...]"
    )