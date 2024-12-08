from fastapi import Request, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List
from .jwt_handler import decodeJWT
from models.users import User
import jwt
from decouple import config

JWT_SECRET = config('secret')

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):

        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials = await super().__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication token")

            return await self.verify_jwt(credentials.credentials)
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization token")

    async def verify_jwt(self, jwtoken: str):
        try:
            payload = decodeJWT(jwtoken)
            username: str = payload.get("user_id")
            role: str = payload.get("type")

            if username is None:
                raise HTTPException(status_code=401, detail="Invalid token formats")
            else:
                user_data = {"username": username, "role": role}

                return User(**user_data)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid JWT token")

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, user: User = Depends(JWTBearer())):
        # print(user, self.allowed_roles)
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=403, detail="You don't have enough permissions"
            )
        return True