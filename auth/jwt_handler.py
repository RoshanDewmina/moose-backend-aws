import time
from typing import Dict, Union
from datetime import datetime, timedelta, timezone
import jwt
from decouple import config

# def token_response(token: str):
#     return {
#         "access_token": token
#     }

JWT_SECRET = config('secret')

def signJWT(data: dict, expires_delta: Union[int, None] = None, refresh_expires_delta: Union[int, None] = 7 * 24 * 60 * 60) -> Dict[str, str]:
    # Set the expiry time.
    payload = data.copy()
    # expireTime = datetime.now(timezone.utc) + timedelta(seconds=expires_delta) if expires_delta else datetime.now(timezone.utc) + timedelta(seconds=30)
    # payload['exp'] = expireTime.timestamp()
    # access_token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    # payload.update({'expires': expireTime.timestamp()})
    #

    refresh_expire_time = datetime.now(timezone.utc) + timedelta(seconds=refresh_expires_delta)  # Longer expiry time for refresh token
    payload['exp'] = refresh_expire_time.timestamp()
    access_token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return {
        "access_token": access_token,

    }

def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token.encode(), JWT_SECRET, algorithms=["HS256"])
        return decoded_token if decoded_token['exp'] >= time.time() else None
    except jwt.ExpiredSignatureError:
        return None
    except jwt.PyJWTError:
        return None

def is_token_expired(token: str) -> bool:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"], options={"verify_exp": False})
        expiration_time = payload.get('exp')
        if expiration_time is None:
            return True
        return time.time() > expiration_time
    except jwt.ExpiredSignatureError:
        return True
    except jwt.InvalidTokenError:
        return True

