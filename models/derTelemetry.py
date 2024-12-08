from typing import List, Optional
from pydantic import BaseModel, validator, ValidationError
from datetime import datetime
from bson import ObjectId

class DERTelemetry(BaseModel):
    timestamp : datetime
    phaseAVoltage: float
    phaseBVoltage: float
    unitACWatts: float
    unitACWhr: float
    frequency: float
    dcVoltage: float
    dcWatts: float
    soc: float
    availableStorage: float
    batteryVoltage: int
    pvVoltage: int
    status: Optional[dict]={}
    valid: bool

class DeviceTelemetryHour(BaseModel):
    _id: str
    deviceID: str
    telemetry: List[Optional[DERTelemetry]]
    dateCreated: datetime = datetime(1, 1, 1)

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
                "_id": "659837818c69940043999d70",
                "deviceID": "6569492c8c69940043998944",
                "telemetry": [
                    {
                        "phaseAVoltage": 0,
                        "phaseBVoltage": 0,
                        "unitACWatts": 0,
                        "unitACWhr": 0,
                        "frequency": 0,
                        "dcVoltage": 0,
                        "dcWatts": 0,
                        "soc": 0,
                        "availableStorage": 0,
                        "batteryVoltage": 0,
                        "pvVoltage": 0,
                        "valid": False
                    },
                    {
                        "phaseAVoltage": 0,
                        "phaseBVoltage": 0,
                        "unitACWatts": 0,
                        "unitACWhr": 0,
                        "frequency": 0,
                        "dcVoltage": 0,
                        "dcWatts": 0,
                        "soc": 0,
                        "availableStorage": 0,
                        "batteryVoltage": 0,
                        "pvVoltage": 0,
                        "valid": False
                    }
                ],
                "dateCreated": "2024-01-05T17:00:00Z"
            }
        }

class telemetryScheduler(BaseModel):
    site_id: str
    asset_id: str
    interval: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "site_id": "10018",
                "asset_id": "42169497-44a6-4b5c-9c4b-5fe81fa54da4"
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
