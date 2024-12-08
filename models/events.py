from typing import Optional
from pydantic import BaseModel, validator
from datetime import datetime
from bson import ObjectId

class Event(BaseModel):
    _id: str
    homeID: str
    message: str
    active: bool
    cancelled: bool
    startTime: datetime = datetime(1, 1, 1)
    endTime: datetime = datetime(1, 2, 1)
    dates: dict

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
                "_id": "5adcbfac963fbc009b000001",
                "homeID": "5adcbfac963fbc009b000001",
                "message": "message",
                "active": True,
                "cancelled": False,
                "startTime": "2023-12-01T02:40:37.321Z",
                "endTime": "2023-12-01T02:40:37.321Z",
                "dates": {
                    "dateCreated": "2023-12-01T02:40:37.321Z",
                    "dateUpdated": "2023-12-01T02:40:37.321Z"
                }
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
