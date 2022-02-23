from typing import List, Optional, Dict
from datetime import datetime
from fastapi import applications

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


""" <--- SCHEMAS DE CLIENTE ---> """


class ClienteBase(BaseModel):
    nombre: str = Field(
        ..., title="Nombre descriptivo del Cliente", example="C.A.E.R", max_length=50
    )
    url_exito: str = Field(
        ...,
        title="URL de Feedback para pagos exitosos",
        example="https://notificaciones.frontiniyasoc.com.ar/exito",
        max_length=300,
    )
    url_pendiente: Optional[str] = Field(
        None,
        title="URL de Feedback para pagos pendientes",
        example="https://notificaciones.frontiniyasoc.com.ar/pendiente",
        max_length=300,
    )
    url_error: str = Field(
        ...,
        title="URL de Feedback para pagos erróneos",
        example="https://notificaciones.frontiniyasoc.com.ar/error",
        max_length=300,
    )


class ClienteCreate(ClienteBase):
    public_key: str = Field(
        ...,
        title="Public Key de las Credenciales de Mercado Pago",
        example="TEST-XXXXXXXXXXXX-XXXXXXXX",
    )
    access_token: str = Field(
        ...,
        title="Access Token de las Credenciales de Mercado Pago",
        example="TEST-XXXXXXXXXXXX-XXXXXXXX",
    )


class Cliente(ClienteBase):
    id: int = Field(..., title="ID de la Base de Datos", example=1)
    # preferencias: List[Preferencia] = []

    class Config:
        orm_mode = True


""" <--- SCHEMAS DE ITEM PREFERENCIA ---> """


class ItemPreferenciaBase(BaseModel):
    titulo: str = Field(
        None,
        title="Título del Item de la Preferencia",
        example="CUOTA SOCIAL 2021-01",
        max_length=100,
    )
    descripcion: str = Field(
        None,
        title="Descripción del Item de la Preferencia",
        example="Cuota Social correspondiente al mes de Enero de 2021",
        max_length=100,
    )
    cantidad: int = Field(..., title="Cantidad del Item de la Preferencia", example=1)
    precio_unitario: float = Field(
        ..., title="Precio unitario del Item de la Preferencia", example=500.00
    )


class ItemPreferenciaCreate(ItemPreferenciaBase):
    pass


class ItemPreferencia(ItemPreferenciaBase):
    id: int = Field(..., title="ID de la Base de Datos", example=1)
    id_preferencia: int = Field(
        ..., title="ID de la Preferencia a la que corresponde el Item", example=1
    )

    class Config:
        orm_mode = True


""" <--- SCHEMAS DE PAGOS ---> """


class PagoBase(BaseModel):
    fecha_hora: datetime
    monto_abonado: float
    id_preferencia: int
    id_pago_mp: str


class PagoCreate(PagoBase):
    metodo_pago: Optional[str] = None
    pagador_nombre: Optional[str] = None
    pagador_email: Optional[str] = None
    pagador_telefono: Optional[str] = None
    pagador_tipo_identificacion: Optional[str] = None
    pagador_nro_identifiacion: Optional[str] = None


class Pago(PagoBase):
    id: int

    class Config:
        orm_mode = True


class PayloadNotificacionMP(BaseModel):
    id: int = Field(..., title="ID de la notificación de Mercado Pago", example=1)
    live_mode: bool = Field(
        ...,
        title="Booleano que indica si la notificación es del modo producción o no",
        example=True,
    )
    type: str = Field(
        ..., title="El tipo de notificación de Mercado Pago", example="payment"
    )
    date_created: str = Field(
        ...,
        title="La fecha de creación de la notificación de Mercado Pago",
        example="2021-09-15T14:55:50Z",
    )
    application_id: int = Field(
        None,
        title="La ID de aplicación < ? > (No especificado por Mercado Pago)",
        example=181672,
    )
    user_id: int = Field(
        ...,
        title="El ID de Usuario de Mercado Pago de donde se generó la notificación",
        example=168065984,
    )
    version: int = Field(
        None, title="Versión < ? > (No especificado por Mercado Pago)", example=1
    )
    api_version: str = Field(
        ..., title="Versión de la API de Mercado Pago", example="v1"
    )
    action: str = Field(
        ...,
        title="Tipo de acción relacionada al tipo de notificación",
        example="payment.created",
    )
    data: Dict = Field(
        None,
        title="Datos adicionales para identificar la acción de la notificación",
        example={"id": "1241104080"},
    )


class ResponseNotificacionMP(BaseModel):
    code: int = Field(
        ...,
        title="Código de respuesta",
        example=200
    )
    response_payload: PayloadNotificacionMP

class GetPagoResponse(BaseModel):
    code: int = Field(200, const=True, title="Código de respuesta", example=200)
    pago: Pago

class GetPagosClienteResponse(BaseModel):
    code: int = Field(200, const=True, title="Código de respuesta", example=200)
    cliente: Cliente
    pagos: List[Pago] = []

    class Config:
        orm_mode = True




""" <--- SCHEMAS DE PREFERENCIA ---> """


class PreferenciaBase(BaseModel):
    init_point: str = Field(
        ...,
        title="URL brindada por la API de Mercado Pago para pagar la Preferencia",
        example="https://www.mercadopago.com.ar/checkout/v1/redirect?pref_id=[pref_id]",
    )
    id_preferencia_mp: str = Field(
        ...,
        title="El ID de la Preferencia generado por la API de Mercado Pago",
        example="XXXXXXXX-XXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXX",
    )
    id_cliente: int = Field(
        ..., title="ID del Cliente al que corresponde la Preferencia", example=1
    )
    created_at: datetime = Field(
        ...,
        title="Fecha y hora de creación de la Preferencia",
        example="2021-09-14T00:00:00Z",
    )
    info_adicional: str = Field(
        None,
        title="Información adicional útil para la Preferencia",
        example="Algo útil sobre la Preferencia",
        max_length=200,
    )


class PreferenciaCreate(PreferenciaBase):
    estado: str = Field(
        ...,
        title="El estado inicial de la Preferencia",
        example="PENDIENTE",
        max_length=50,
    )


class Preferencia(PreferenciaCreate):
    id: int = Field(..., title="ID de la Base de Datos", example=1)
    items: List[ItemPreferencia] = Field(
        ..., title="Los Items asociados a la Preferencia"
    )
    pago: Pago = Field(None, title="El Pago de la Preferencia")
    # cliente: Cliente

    class Config:
        orm_mode = True


class PayloadPreferenciaCrear(BaseModel):
    items: List[ItemPreferenciaBase] = Field(
        ..., title="Conjunto de datos necesarios para crear la Preferencia"
    )
    info_adicional: str = Field(
        None,
        title="Información adicional útil para la Preferencia",
        example="Algo útil sobre la Preferencia",
        max_length=200,
    )

class GetPreferenciaResponse(BaseModel):
    code: int = Field(200, const=True, title="Código de respuesta", example=200)
    preferencia: Preferencia = Field(
        None, title="La Preferencia en detalle"
    )
    pago_preferencia: Pago = Field(None, title="El Pago de la Preferencia")

class CrearPreferenciaResponse(BaseModel):
    code: int = Field(201, const=True, title="Código de respuesta", example=201)
    mensaje: str = Field(
        None, title="Mensaje de éxito", example="Preferencia creada exitosamente"
    )
    cliente: Cliente = Field(None)
    preferencia: Preferencia = Field(
        None, title="La Preferencia creada junto con sus Items"
    )


""" <--- SCHEMAS DE RESPUESTA ---> """


class GetClientes(BaseModel):
    code: int = Field(200, const=True, title="Código de respuesta", example=200)
    clientes: List[Cliente]

    class Config:
        orm_mode = True


class GetPreferenciasCliente(BaseModel):
    code: int = Field(200, const=True, title="Código de respuesta", example=200)
    cliente: Cliente
    preferencias: List[Preferencia] = []

    class Config:
        orm_mode = True


class CrearCliente(BaseModel):
    code: int = Field(201, const=True, title="Código de respuesta", example=201)
    mensaje: str = "Cliente creado exitosamente"
    cliente: Cliente

class CrearUsuario(BaseModel):
    code: int = Field(201, const=True, title="Código de respuesta", example=201)
    mensaje: str = "Usuario creado exitosamente"
    


""" <--- SCHEMAS DE USUARIO Y SEGURIDAD ---> """


class Token(BaseModel):
    access_token: str = Field(
        ...,
        title="JWT Token válido",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9[...]",
    )
    token_type: str = Field(..., title="El tipo de Token", example="Bearer")


class TokenData(BaseModel):
    username: Optional[str] = None


class Usuario(BaseModel):
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


class UsuarioEnDB(Usuario):
    hashed_password: str

# Make a Schema named PayloadLogin that has 3 parameters: username, password and google_jwt. All of the parameters are strings
class PayloadLogin(BaseModel):

    google_jwt: str = Field(
        ...,
        title="JWT Token de Google",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9[...]"
    )