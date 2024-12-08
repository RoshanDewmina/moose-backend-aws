from typing import List, Optional
from pydantic import BaseModel, validator
from datetime import datetime
from bson import ObjectId

class Energy(BaseModel):
    energy: float
    valid: bool

class DeviceEnergy(BaseModel):
    Timestamp: datetime
    Energy: float

class DeviceEnergyHour(BaseModel):
    _id: str
    deviceID: str
    dateCreated: datetime = datetime(1, 1, 1)
    energy: List[Optional[Energy]]

    @validator('_id', check_fields=False)
    def check_objectid_shape(cls, value):
        try:
            ObjectId(value)
        except Exception as e:
            raise ValueError(f'Invalid ObjectId format: {e}')
        return value

    @validator('deviceID', check_fields=False)
    def check_deviceid_shape(cls, value):
        try:
            ObjectId(value)
        except Exception as e:
            raise ValueError(f'Invalid ObjectId format: {e}')
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "659837818c69940043999d71",
                "deviceID": "6569492c8c69940043998944",
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
