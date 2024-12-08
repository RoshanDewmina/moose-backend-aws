from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId
from enum import Enum

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class User(BaseModel):
    username: str
    role: str

class Token(BaseModel):
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None

class UserRole(str, Enum):
    OWNER = 'OWNER'
    SUPEROPERATOR = 'SUPEROPERATOR'
    USER = 'USER'

class Dates(BaseModel):
    dateCreated: datetime = datetime(1, 1, 1)
    dateUpdated: datetime = datetime(1, 1, 1)

class UserModel(BaseModel):
    userID: Optional[str] = None
    firstName: str
    lastName: str
    email: str
    telephone: Optional[int] = None
    password: str
    verified: Optional[bool] = None
    type: Optional[UserRole] = None
    language: Optional[str] = None
    dates: Optional[Dates] = None
    apiKey: Optional[str] = None
    HEMSCID: Optional[str] = None

    @classmethod
    def validate_objectid_shape(cls, v):
        if v:
            try:
                ObjectId(v)
            except Exception as e:
                raise ValueError(f'Invalid ObjectId format: {e}')
        return v

    @classmethod
    def validate_id(cls, v):
        return cls.validate_objectid_shape(v)

    class Config:
        json_schema_extra = {
            "example": {
                "firstName": "Javad",
                "lastName": "Fattahi",
                "email": "CoVue@uottawa.ca",
                "telephone": 6135625800,
                "password": "password",
                "type": "OWNER",
                "apiKey": "123456789"
            }
        }

class UserCredentials(BaseModel):
    email: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "CoVue@uottawa.ca",
                "password": "password"
            }
        }

class UserModelUpdate(BaseModel):
    firstName:  Optional[str] = None
    lastName:  Optional[str] = None
    telephone: Optional[int] = None
    type: Optional[UserRole] = None
    language: Optional[str] = None
    apiKey: Optional[str] = None

    @classmethod
    def validate_objectid_shape(cls, v):
        if v:
            try:
                ObjectId(v)
            except Exception as e:
                raise ValueError(f'Invalid ObjectId format: {e}')
        return v

    @classmethod
    def validate_id(cls, v):
        return cls.validate_objectid_shape(v)

    class Config:
        json_schema_extra = {
            "example": {
                "firstName": "Javad",
                "lastName": "Fattahi",
                "telephone": 6135625800,
                "type": "USER",
                "language": "EN",
                "apiKey": "123456789"
            }
        }

def ResponseModel(data,code, message):
    return {
        "data": [
            data
        ],
        "code": code,
        "message": message,
    }

def ErrorResponseModel(error, code, message):
    return {
        "error": error,
        "code": code,
        "message": message
    }
