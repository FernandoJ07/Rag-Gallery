from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from app.core.models import User
from typing import Union, Dict, cast


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bool(pwd_context.verify(plain_password, hashed_password))


def get_password_hash(password: str) -> str:
    return str(pwd_context.hash(password))


def create_access_token_for_user(user: User) -> str:

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.uid}, expires_delta=access_token_expires
    )
    return access_token


def create_access_token(
    data: dict, expires_delta: Union[timedelta, None] = None
) -> str:
    to_encode = data.copy()
    expire = (
        datetime.utcnow() + expires_delta
        if expires_delta
        else datetime.utcnow() + timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = str(
        jwt.encode(
            to_encode,
            "TAs5sfX8hqHbdYz6JnSnpfWkHhNV44swZ0YaLoghooGUvPvWwmMvlAjBqShW2TO",
            algorithm=["HS256"],
        )
    )
    return encoded_jwt


def decode_access_token(token: str) -> Union[Dict[str, Union[str, int]], None]:
    try:
        payload = jwt.decode(
            token,
            "TAs5sfX8hqHbdYz6JnSnpfWkHhNV44swZ0YaLoghooGUvPvWwmMvlAjBqShW2TO",
            algorithms=["HS256"],
        )
        # Aseguramos que el payload sea del tipo especificado
        if isinstance(payload, dict):
            return cast(Dict[str, Union[str, int]], payload)
        else:
            return None
    except JWTError:
        return None
