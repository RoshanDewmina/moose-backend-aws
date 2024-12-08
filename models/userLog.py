from typing import Optional
from pydantic import BaseModel, Field,validator
from datetime import datetime
from bson import ObjectId
from models.users import *


class UserLog(BaseModel):
    _id: str
    userID: Optional[str] = None
    firstName: str
    lastName: str
    email: str    
    type: Optional[UserRole] = None    
    loginDates: datetime = datetime(1, 1, 1)    


    @validator('_id', check_fields=False)
    def check_objectid_shape(cls, value):
        try:
            ObjectId(value)
        except Exception as e:
            raise ValueError(f'Invalid ObjectId format: {e}')
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "5a9e3449b572e101fe470d7f",
                "userID": "5a9e3449b572e101fe470d7f",
                "firstName": "Javad",
                "lastName": "Fattahi",
                "email": "CoVue@uottawa.ca",
                "type": "OWNER",                
                "loginDates": "2024-06-12T10:14:19.968Z"                
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


    
    