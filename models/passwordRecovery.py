from typing import List, Optional
from pydantic import BaseModel, validator
from datetime import datetime
from bson import ObjectId

class Temperature(BaseModel):
    temperature: float
    valid: bool

class TemperatureData(BaseModel):
    _id: Optional[str]
    dateCreated: datetime = datetime(1, 1, 1)
    temperatures: List[Temperature]

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
                "_id": "661333808c6994004ae4dc70",
                "dateCreated": "2024-04-08T00:00:00Z",
                "temperatures": [
                    {"temperature": 14.46, "valid": True},
                    {"temperature": 14.46, "valid": True}
                ]
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
