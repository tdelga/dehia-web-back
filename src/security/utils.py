import os

from dotenv import dotenv_values

from passlib.context import CryptContext

from datetime import datetime, timedelta

import time

from sql import crud

from jose import jwt

from typing import Optional

import sys

sys.path.append("..")  # Adds higher directory to python modules path.

from sql import crud

BASEDIR = os.path.abspath(os.path.dirname("../"))

config = dotenv_values(os.path.join(BASEDIR, ".env"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verificar_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_hash_password(password):
    return pwd_context.hash(password)


def autentificar_usuario(db, username: str, password: str):
    user = crud.get_usuario_by_username(db, username)
    if not user:
        return False
    if not verificar_password(password, user.hashed_password):
        return False
    return user


def crear_token_acceso(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, config["SECRET_KEY"], algorithm=config["ALGORITHM"]
    )
    return encoded_jwt
