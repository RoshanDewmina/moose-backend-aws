from typing import List
from pydantic import BaseModel, validator
from datetime import datetime
from bson import ObjectId

class Energy(BaseModel):
    energy: int
    valid: bool

class HomeEnergy(BaseModel):
    Timestamp: datetime
    Energy: float

class HomeEnergyHour(BaseModel):
    _id: str
    homeID: str
    dateCreated: datetime = datetime(1, 1, 1)
    energy: List[Energy]

    @validator('_id', check_fields=False)
    def check_objectid_shape(cls, value):
        try:
            ObjectId(value)
        except Exception as e:
            raise ValueError(f'Invalid ObjectId format: {e}')
        return value

    @validator('homeID', check_fields=False)
    def check_deviceid_shape(cls, value):
        try:
            ObjectId(value)
        except Exception as e:
            raise ValueError(f'Invalid ObjectId format: {e}')
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "659837818c69940043999d6c",
                "homeID": "5a9e3449b572e101fe470d7f",
                "dateCreated": "2024-01-05T17:00:00Z",
                "energy": [
                    {"energy": 0, "valid": False},
                    {"energy": 0, "valid": False}
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
